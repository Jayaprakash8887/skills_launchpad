"""Tests for harness.py — run with: python3 -m unittest discover -s tests -v"""

from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml

KIT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT_ROOT))

import harness  # noqa: E402


def run(*argv: str) -> tuple[int, str]:
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = harness.main(list(argv))
    return code, out.getvalue()


class AddonFilesTest(unittest.TestCase):
    """The kit's own add-on files are consistent with the rest of the kit."""

    def setUp(self) -> None:
        self.addon = harness.load_addon("egm")
        workflow = yaml.safe_load((KIT_ROOT / "references" / "workflow.yaml").read_text())
        self.nodes = set(workflow["nodes"])

    def test_gate_anchors_are_workflow_nodes(self) -> None:
        for gate in harness.addon_gates(self.addon):
            for key in ("after", "before"):
                if gate.get(key):
                    self.assertIn(gate[key], self.nodes, f"gate {gate['id']} {key}")
            for target in ("on_needs_input",):
                if gate.get(target):
                    self.assertIn(gate[target], self.nodes, f"gate {gate['id']} {target}")

    def test_gate_profiles_are_supported(self) -> None:
        for gate in harness.addon_gates(self.addon):
            for profile in gate["profiles"]:
                self.assertIn(profile, self.addon["profiles"])
                harness.load_profile(profile)

    def test_marketplace_ref_matches_plugin_version(self) -> None:
        self.assertEqual(harness.addon_marketplace_ref(self.addon), f"v{self.addon['plugin_version']}")


@mock.patch.object(harness, "addon_environment_notes", return_value=[])
class ApplyWithAddonTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        self.settings = self.repo / ".claude" / "settings.json"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def apply(self, *extra: str, profile: str = "python-backend") -> tuple[int, str]:
        return run("apply", "--repo", str(self.repo), "--profile", profile, "--apply", *extra)

    def pin(self) -> dict:
        return yaml.safe_load((self.repo / ".harness-pin.yaml").read_text())

    def test_fresh_repo(self, _notes) -> None:
        code, _ = self.apply("--with", "egm")
        self.assertEqual(code, 0)
        settings = json.loads(self.settings.read_text())
        self.assertTrue(settings["enabledPlugins"]["egm@egm"])
        self.assertEqual(settings["extraKnownMarketplaces"]["egm"]["source"]["ref"], "v0.1.1")
        self.assertIn("Read(**/.env)", settings["permissions"]["deny"])
        self.assertEqual(len(settings["permissions"]["allow"]), 4)
        self.assertTrue((self.repo / ".harness/addons/egm/integration.md").is_file())
        self.assertEqual(self.pin()["addons"]["egm"]["plugin_version"], "0.1.1")
        claude_md = (self.repo / "CLAUDE.md").read_text()
        self.assertIn("### Add-on: EGM", claude_md)
        self.assertIn("docs/specification/reports/egm/{INIT}/design-review/", claude_md)
        self.assertNotIn("{{", claude_md)
        self.assertEqual(run("status", "--repo", str(self.repo))[0], 0)

    def test_meta_profile_gets_only_its_gates(self, _notes) -> None:
        self.apply("--with", "egm", profile="meta-pm")
        claude_md = (self.repo / "CLAUDE.md").read_text()
        self.assertIn("**prd-review**", claude_md)
        self.assertIn("`prd/{INIT}.md`", claude_md)
        self.assertIn("prd/reports/egm/{INIT}/prd-review/", claude_md)
        self.assertNotIn("**design-review**", claude_md)

    def test_team_settings_are_kept_and_reapply_is_idempotent(self, _notes) -> None:
        self.settings.parent.mkdir(parents=True)
        team = {
            "permissions": {"allow": ["Bash(npm *)"], "deny": ["Read(./secrets/**)"]},
            "enabledPlugins": {"other@market": True},
            "hooks": {"Stop": []},
        }
        self.settings.write_text(json.dumps(team, indent=2) + "\n")
        self.apply("--with", "egm")
        merged = json.loads(self.settings.read_text())
        self.assertEqual(merged["permissions"]["allow"][0], "Bash(npm *)")
        self.assertEqual(merged["permissions"]["deny"], ["Read(./secrets/**)", "Read(**/.env)"])
        self.assertTrue(merged["enabledPlugins"]["other@market"])
        self.assertEqual(merged["hooks"], {"Stop": []})
        before = self.settings.read_bytes()
        _, out = self.apply("--with", "egm")
        self.assertIn("add-on settings already current", out)
        self.assertEqual(self.settings.read_bytes(), before)

    def test_reapply_without_flag_keeps_addon(self, _notes) -> None:
        self.apply("--with", "egm")
        _, out = self.apply()
        self.assertIn("kept from .harness-pin.yaml", out)
        self.assertIn("egm", self.pin()["addons"])
        self.assertIn("### Add-on: EGM", (self.repo / "CLAUDE.md").read_text())

    def test_without_drops_addon_but_keeps_settings(self, _notes) -> None:
        self.apply("--with", "egm")
        _, out = self.apply("--without", "egm")
        self.assertNotIn("addons", self.pin())
        self.assertFalse((self.repo / ".harness/addons/egm").exists())
        self.assertNotIn("### Add-on: EGM", (self.repo / "CLAUDE.md").read_text())
        self.assertIn("Remove by hand", out)
        self.assertIn("egm@egm", self.settings.read_text())
        self.assertEqual(run("status", "--repo", str(self.repo))[0], 0)

    def test_status_reports_missing_setting(self, _notes) -> None:
        self.apply("--with", "egm")
        settings = json.loads(self.settings.read_text())
        settings["permissions"]["deny"] = []
        self.settings.write_text(json.dumps(settings))
        code, out = run("status", "--repo", str(self.repo))
        self.assertEqual(code, 1)
        self.assertIn('missing permissions.deny entry "Read(**/.env)"', out)

    def test_invalid_settings_json_is_not_overwritten(self, _notes) -> None:
        self.settings.parent.mkdir(parents=True)
        self.settings.write_text("{ not json")
        with self.assertRaises(SystemExit):
            self.apply("--with", "egm")
        self.assertEqual(self.settings.read_text(), "{ not json")

    def test_dry_run_writes_nothing(self, _notes) -> None:
        code, out = run("apply", "--repo", str(self.repo), "--profile", "python-backend", "--with", "egm")
        self.assertEqual(code, 0)
        self.assertIn("[dry-run] .claude/settings.json  (create)", out)
        self.assertEqual(list(self.repo.iterdir()), [])

    def test_unknown_addon_and_conflicting_flags(self, _notes) -> None:
        with self.assertRaises(SystemExit):
            self.apply("--with", "nope")
        with self.assertRaises(SystemExit):
            self.apply("--with", "egm", "--without", "egm")


class NoAddonTest(unittest.TestCase):
    def test_block_has_no_addon_section_or_placeholder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run("apply", "--repo", tmp, "--profile", "python-backend", "--apply")
            claude_md = (Path(tmp) / "CLAUDE.md").read_text()
            self.assertNotIn("{{", claude_md)
            self.assertNotIn("Add-on", claude_md)
            self.assertIn("boards.\n\n### Before changing behavior", claude_md)
            self.assertFalse((Path(tmp) / ".claude" / "settings.json").exists())
            self.assertNotIn("addons", yaml.safe_load((Path(tmp) / ".harness-pin.yaml").read_text()))


class MergeSettingsTest(unittest.TestCase):
    def test_merge_reports_each_change_and_problems_clear_after(self) -> None:
        current = {"permissions": {"allow": ["A"]}}
        fragment = {"permissions": {"allow": ["A", "B"], "deny": ["C"]}, "flag": True}
        changes = harness.merge_settings(current, fragment)
        self.assertEqual(
            changes,
            ['add permissions.allow: "B"', 'add permissions.deny: "C"', "set flag = true"],
        )
        self.assertEqual(harness.settings_problems(current, fragment), [])
        self.assertEqual(
            harness.settings_problems({}, fragment)[0], "missing permissions"
        )


if __name__ == "__main__":
    unittest.main()

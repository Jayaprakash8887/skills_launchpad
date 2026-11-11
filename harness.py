#!/usr/bin/env python3
"""Harness kit CLI — seed pinned rules + Claude Code skills into a repo.

A VSCode / Claude Code adaptation of drivestream-lab's launchpad `apply-harness`:

  harness list                                   show profiles, skills and add-ons
  harness apply  --repo PATH --profile NAME      dry-run preview (default)
  harness apply  --repo PATH --profile NAME --apply [--with ADDON] [--without ADDON]
  harness status --repo PATH                     verify installed harness vs pin

On-disk contract in the target repo (mirrors launchpad):

  .harness/skills/<name>/       skill sources (real copies, committed)
  .harness/references/          shared contracts + workflow.yaml
  .harness/addons/<name>/       add-on sources (only with --with)
  .harness/profile.yaml         copy of the applied profile
  .harness-pin.yaml             pin record: kit version + sha256 manifest
  .claude/rules/*.md            constitution (copies of kit rules/<stack>/)
  .claude/skills/<name>         relative symlinks into .harness/skills/
  .claude/settings.json         add-on keys merged in (team keys are kept)
  CLAUDE.md                     managed block between harness markers
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

KIT_ROOT = Path(__file__).resolve().parent
ADDONS_ROOT = KIT_ROOT / "addons"
MARK_START = "<!-- harness:start -->"
MARK_END = "<!-- harness:end -->"
PIN_FILE = ".harness-pin.yaml"
SETTINGS_REL = Path(".claude") / "settings.json"
ADDONS_PLACEHOLDER = "{{ADDONS_SECTION}}\n\n"

# stack key -> rules directory under kit rules/ (None = no constitution)
CONSTITUTION_BY_PROFILE = {
    "python-backend": "python-backend",
    "meta-pm": None,
}

SKILL_LANES = ("development", "requirements", "forge")


# ── kit introspection ────────────────────────────────────────────────────────

def kit_version() -> str:
    return (KIT_ROOT / "VERSION").read_text().strip()


def load_profile(name: str) -> dict:
    path = KIT_ROOT / "profiles" / f"{name}.yaml"
    if not path.is_file():
        available = sorted(p.stem for p in (KIT_ROOT / "profiles").glob("*.yaml"))
        raise SystemExit(f"unknown profile {name!r} — available: {', '.join(available)}")
    data = yaml.safe_load(path.read_text())
    if data.get("profile") != name:
        raise SystemExit(f"{path}: profile key {data.get('profile')!r} != filename {name!r}")
    return data


def profile_skills(profile: dict) -> list[str]:
    names: list[str] = []
    for key in ("development_skills", "requirements_skills", "forge_skills"):
        names.extend(profile.get(key) or [])
    return names


def find_skill_src(name: str) -> Path:
    for lane in SKILL_LANES:
        cand = KIT_ROOT / "skills" / lane / name
        if (cand / "SKILL.md").is_file():
            return cand
    raise SystemExit(f"skill {name!r} not found under {KIT_ROOT / 'skills'}")


# ── add-ons ──────────────────────────────────────────────────────────────────
# An add-on is a directory addons/<name>/ holding addon.yaml (settings fragment,
# versions, profiles), an optional gates.yaml and CLAUDE.addon.md, plus any
# docs. `apply --with <name>` copies it to .harness/addons/<name>/, merges its
# settings into .claude/settings.json and renders its CLAUDE.md section.

def available_addons() -> list[str]:
    if not ADDONS_ROOT.is_dir():
        return []
    return sorted(p.name for p in ADDONS_ROOT.iterdir() if (p / "addon.yaml").is_file())


def read_addon(addon_dir: Path, name: str) -> dict:
    path = addon_dir / "addon.yaml"
    if not path.is_file():
        available = ", ".join(available_addons()) or "(none)"
        raise SystemExit(f"unknown add-on {name!r} — available: {available}")
    data = yaml.safe_load(path.read_text()) or {}
    if data.get("addon") != name:
        raise SystemExit(f"{path}: addon key {data.get('addon')!r} != directory {name!r}")
    data["_dir"] = addon_dir
    return data


def load_addon(name: str) -> dict:
    return read_addon(ADDONS_ROOT / name, name)


def addon_gates(addon: dict) -> list[dict]:
    path = addon["_dir"] / "gates.yaml"
    if not path.is_file():
        return []
    return (yaml.safe_load(path.read_text()) or {}).get("gates") or []


def addon_marketplace_ref(addon: dict) -> str | None:
    """The git ref the add-on pins its plugin marketplace to, if any."""
    marketplace = str(addon.get("plugin", "")).partition("@")[2]
    source = (
        ((addon.get("settings") or {}).get("extraKnownMarketplaces") or {})
        .get(marketplace, {})
        .get("source", {})
    )
    return source.get("ref")


class _KeepUnknown(dict):
    """format_map helper: unknown {placeholders} such as {INIT} stay as written."""

    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def layout_vars(profile: dict) -> _KeepUnknown:
    layout = profile.get("layout") or {}
    return _KeepUnknown(
        {k: str(v).rstrip("/") for k, v in layout.items() if isinstance(v, (str, int))}
    )


def render_gate(gate: dict, layout: _KeepUnknown) -> str:
    where = []
    if gate.get("after"):
        where.append(f"after `{gate['after']}`")
    if gate.get("before"):
        where.append(f"before `{gate['before']}`")
    line = f"- **{gate['id']}** ({', '.join(where)}): `{gate['command']}`"
    line += f" on `{gate['target'].format_map(layout)}`"
    if gate.get("preset"):
        line += f", preset *{gate['preset']}*"
    if gate.get("rounds"):
        line += f", {gate['rounds']} round only" if gate["rounds"] == 1 else f", {gate['rounds']} rounds"
    line += f". Artifact directory: `{gate['artifact_dir'].format_map(layout)}`."
    return line


def render_addon_section(addon: dict, profile_name: str, profile: dict) -> str:
    tpl_path = addon["_dir"] / "CLAUDE.addon.md"
    if not tpl_path.is_file():
        return f"### Add-on: {addon.get('title', addon['addon'])}"
    layout = layout_vars(profile)
    gates = [
        render_gate(g, layout)
        for g in addon_gates(addon)
        if profile_name in (g.get("profiles") or [])
    ]
    return (
        tpl_path.read_text()
        .strip()
        .replace("{{PLUGIN}}", str(addon.get("plugin", "")))
        .replace("{{PLUGIN_VERSION}}", str(addon.get("plugin_version", "")))
        .replace("{{MARKETPLACE_REF}}", str(addon_marketplace_ref(addon) or "default branch"))
        .replace("{{MIN_CLAUDE_CODE}}", str(addon.get("min_claude_code", "")))
        .replace("{{COMMANDS}}", " ".join(f"`{c}`" for c in addon.get("commands") or []))
        .replace("{{GATES}}", "\n".join(gates) or "_No gates for this profile._")
    )


# ── .claude/settings.json merge ──────────────────────────────────────────────
# Objects merge key by key, lists are unioned (existing order kept, new items
# appended), scalars are set. Nothing the team added is removed.

def _dotted(path: tuple[str, ...]) -> str:
    return ".".join(path)


def merge_settings(current: dict, fragment: dict, path: tuple[str, ...] = ()) -> list[str]:
    changes: list[str] = []
    for key, want in fragment.items():
        here = path + (key,)
        have = current.get(key)
        if isinstance(want, dict):
            if not isinstance(have, dict):
                if have is not None:
                    changes.append(f"replace {_dotted(here)} (was {type(have).__name__})")
                current[key] = have = {}
            changes += merge_settings(have, want, here)
        elif isinstance(want, list):
            if not isinstance(have, list):
                if have is not None:
                    changes.append(f"replace {_dotted(here)} (was {type(have).__name__})")
                current[key] = have = []
            for item in want:
                if item not in have:
                    have.append(item)
                    changes.append(f"add {_dotted(here)}: {json.dumps(item)}")
        elif have != want:
            changes.append(f"set {_dotted(here)} = {json.dumps(want)}")
            current[key] = want
    return changes


def settings_problems(current: object, fragment: dict, path: tuple[str, ...] = ()) -> list[str]:
    problems: list[str] = []
    for key, want in fragment.items():
        here = path + (key,)
        have = current.get(key) if isinstance(current, dict) else None
        if isinstance(want, dict):
            if not isinstance(have, dict):
                problems.append(f"missing {_dotted(here)}")
                continue
            problems += settings_problems(have, want, here)
        elif isinstance(want, list):
            have_list = have if isinstance(have, list) else []
            problems += [
                f"missing {_dotted(here)} entry {json.dumps(item)}"
                for item in want
                if item not in have_list
            ]
        elif have != want:
            problems.append(f"{_dotted(here)} is {json.dumps(have)}, expected {json.dumps(want)}")
    return problems


def read_settings(repo: Path) -> dict:
    path = repo / SETTINGS_REL
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{path}: not valid JSON ({exc}) — fix it before applying add-ons")
    if not isinstance(data, dict):
        raise SystemExit(f"{path}: expected a JSON object")
    return data


def upsert_settings(repo: Path, addons: list[dict], *, dry: bool, log: list[str]) -> None:
    path = repo / SETTINGS_REL
    existed = path.is_file()
    current = read_settings(repo)
    merged = copy.deepcopy(current)
    changes: list[str] = []
    for addon in addons:
        changes += [
            f"{addon['addon']}: {c}" for c in merge_settings(merged, addon.get("settings") or {})
        ]
    if not changes:
        log.append(f"  –  {SETTINGS_REL}  (add-on settings already current)")
        return
    log.append(
        f"  {'[dry-run] ' if dry else '✔ '}{SETTINGS_REL}  ({'merge' if existed else 'create'})"
    )
    log.extend(f"      {c}" for c in changes)
    if not dry:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(merged, indent=2, ensure_ascii=False) + "\n")


# ── machine checks (warnings only; never fail `status`) ─────────────────────

def _version_tuple(text: str) -> tuple[int, ...] | None:
    match = re.search(r"(\d+)\.(\d+)\.(\d+)", text)
    return tuple(int(x) for x in match.groups()) if match else None


def claude_code_versions() -> list[tuple[str, tuple[int, ...]]]:
    """(where, version) for each Claude Code found on this machine."""
    found: list[tuple[str, tuple[int, ...]]] = []
    exe = shutil.which("claude")
    if exe:
        try:
            out = subprocess.run(
                [exe, "--version"], capture_output=True, text=True, timeout=15, check=False
            ).stdout
        except (OSError, subprocess.SubprocessError):
            out = ""
        version = _version_tuple(out)
        if version:
            found.append(("claude on PATH", version))
    ext_dirs = sorted(
        (Path.home() / ".vscode" / "extensions").glob("anthropic.claude-code-*"),
        key=lambda p: _version_tuple(p.name) or (),
    )
    if ext_dirs:
        version = _version_tuple(ext_dirs[-1].name)
        if version:
            found.append(("VS Code extension", version))
    return found


def addon_environment_notes(addon: dict) -> list[tuple[bool, str]]:
    """(ok, text) notes about this machine. Printed by `status`, never fatal."""
    notes: list[tuple[bool, str]] = []
    name = addon["addon"]
    minimum = _version_tuple(str(addon.get("min_claude_code", "")))
    if minimum:
        want = ".".join(map(str, minimum))
        for where, version in claude_code_versions():
            have = ".".join(map(str, version))
            if version < minimum:
                notes.append((False, f"{name}: {where} is Claude Code {have}; needs {want} or later"))
            else:
                notes.append((True, f"{name}: {where} is Claude Code {have}"))
    plugin, _, marketplace = str(addon.get("plugin", "")).partition("@")
    version = addon.get("plugin_version")
    if plugin and marketplace and version:
        cache = Path.home() / ".claude" / "plugins" / "cache" / marketplace / plugin / str(version)
        if cache.is_dir():
            notes.append((True, f"{name}: plugin {plugin}@{marketplace} {version} is installed"))
        else:
            notes.append((
                False,
                f"{name}: plugin {plugin}@{marketplace} {version} is not installed on this machine "
                f"yet. Trust the folder in Claude Code and accept the plugin prompt, or run "
                f"`claude plugin install {plugin}@{marketplace} --scope project`.",
            ))
    return notes


# ── file helpers ─────────────────────────────────────────────────────────────

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def dir_manifest(root: Path, base: Path) -> dict[str, str]:
    """{relpath-from-base: sha256} for every file under root (follows nothing)."""
    out: dict[str, str] = {}
    for p in sorted(root.rglob("*")):
        if p.is_file() and not p.is_symlink():
            out[str(p.relative_to(base))] = sha256_file(p)
    return out


def copy_tree(src: Path, dest: Path, *, dry: bool, log: list[str]) -> None:
    action = "refresh" if dest.exists() else "install"
    log.append(f"  {'[dry-run] ' if dry else '✔ '}{action}  {dest}")
    if dry:
        return
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def ensure_symlink(target: Path, link: Path, *, dry: bool, log: list[str]) -> None:
    rel = os.path.relpath(target, link.parent)
    if link.is_symlink() and os.readlink(link) == rel:
        return
    log.append(f"  {'[dry-run] ' if dry else '✔ '}symlink  {link} → {rel}")
    if dry:
        return
    if link.is_symlink() or link.exists():
        if link.is_dir() and not link.is_symlink():
            shutil.rmtree(link)
        else:
            link.unlink()
    link.parent.mkdir(parents=True, exist_ok=True)
    link.symlink_to(rel)


# ── CLAUDE.md managed block ──────────────────────────────────────────────────

def render_block(
    profile_name: str,
    skills: list[str],
    rules_stack: str | None,
    addons: list[dict] | None = None,
    profile: dict | None = None,
) -> str:
    tpl = (KIT_ROOT / "templates" / "CLAUDE.harness.md").read_text()
    addon_sections = [
        render_addon_section(a, profile_name, profile or {}) for a in addons or []
    ]
    tpl = tpl.replace(
        ADDONS_PLACEHOLDER,
        "".join(section + "\n\n" for section in addon_sections),
    )
    if rules_stack:
        rule_files = sorted((KIT_ROOT / "rules" / rules_stack).glob("*.md"))
        rules_lines = "\n".join(f"@.claude/rules/{f.name}" for f in rule_files)
        rules_section = (
            "Shared rules (constitution — pinned copies, **do not edit**):\n\n" + rules_lines
        )
    else:
        rules_section = "_No constitution rules for this profile (meta/PM workspace)._"
    slash_list = " ".join(f"`/{s}`" for s in skills)
    return (
        tpl.replace("{{PROFILE}}", profile_name)
        .replace("{{KIT_VERSION}}", kit_version())
        .replace("{{RULES_SECTION}}", rules_section)
        .replace("{{SKILLS_SLASH_LIST}}", slash_list)
    )


def upsert_claude_md(repo: Path, block: str, *, dry: bool, log: list[str]) -> None:
    path = repo / "CLAUDE.md"
    managed = f"{MARK_START}\n{block.strip()}\n{MARK_END}"
    if path.is_file():
        text = path.read_text()
        if MARK_START in text and MARK_END in text:
            head, rest = text.split(MARK_START, 1)
            _, tail = rest.split(MARK_END, 1)
            new = head + managed + tail
            state = "current" if new == text else "refresh block"
        else:
            new = text.rstrip() + "\n\n" + managed + "\n"
            state = "insert block"
    else:
        new = f"# Agent guide\n\n{managed}\n"
        state = "seed"
    if state == "current":
        log.append("  –  CLAUDE.md  (harness block already current)")
        return
    log.append(f"  {'[dry-run] ' if dry else '✔ '}CLAUDE.md  ({state})")
    if not dry:
        path.write_text(new)


# ── commands ─────────────────────────────────────────────────────────────────

def cmd_list(_: argparse.Namespace) -> int:
    print(f"harness kit v{kit_version()}  ({KIT_ROOT})\n")
    for pf in sorted((KIT_ROOT / "profiles").glob("*.yaml")):
        profile = yaml.safe_load(pf.read_text())
        name = profile["profile"]
        rules = CONSTITUTION_BY_PROFILE.get(name)
        print(f"profile: {name}")
        print(f"  constitution: {'rules/' + rules if rules else '(none)'}")
        for skill in profile_skills(profile):
            print(f"  /{skill}")
        print()
    names = available_addons()
    if names:
        print("add-ons (apply with --with NAME):")
        for name in names:
            addon = load_addon(name)
            print(
                f"  {name}  {addon.get('title', '')} — plugin {addon.get('plugin')} "
                f"{addon.get('plugin_version')}, profiles: {', '.join(addon.get('profiles') or [])}"
            )
        print()
    return 0


def resolve_addons(args: argparse.Namespace, repo: Path) -> tuple[list[dict], list[str], list[str]]:
    """(add-ons to apply, names carried over from the pin, names to drop)."""
    with_names = list(dict.fromkeys(args.with_addons))
    drop_names = list(dict.fromkeys(args.without_addons))
    both = sorted(set(with_names) & set(drop_names))
    if both:
        raise SystemExit(f"add-on(s) {', '.join(both)} given to both --with and --without")
    pin_path = repo / PIN_FILE
    old_pin = (yaml.safe_load(pin_path.read_text()) or {}) if pin_path.is_file() else {}
    previous = list((old_pin.get("addons") or {}).keys())
    carried = [n for n in previous if n not in with_names and n not in drop_names]
    addons = [load_addon(n) for n in with_names + carried]
    for addon in addons:
        allowed = addon.get("profiles") or []
        if args.profile not in allowed:
            raise SystemExit(
                f"add-on {addon['addon']!r} does not support profile {args.profile!r} "
                f"(supports: {', '.join(allowed) or 'none'})"
            )
    return addons, carried, drop_names


def settings_entries(fragment: dict, path: tuple[str, ...] = ()) -> list[str]:
    """Human-readable leaf entries of a settings fragment."""
    out: list[str] = []
    for key, value in fragment.items():
        here = path + (key,)
        if isinstance(value, dict):
            out += settings_entries(value, here)
        elif isinstance(value, list):
            out += [f"{_dotted(here)}: {json.dumps(item)}" for item in value]
        else:
            out.append(f"{_dotted(here)} = {json.dumps(value)}")
    return out


def cmd_apply(args: argparse.Namespace) -> int:
    repo = Path(args.repo).expanduser().resolve()
    if not repo.is_dir():
        raise SystemExit(f"--repo {repo} is not a directory")
    profile = load_profile(args.profile)
    skills = profile_skills(profile)
    rules_stack = CONSTITUTION_BY_PROFILE.get(args.profile)
    addons, carried, dropped = resolve_addons(args, repo)
    dry = not args.apply
    log: list[str] = []

    print(f"{'DRY-RUN' if dry else 'APPLY'}: profile {args.profile} → {repo}")
    if addons:
        print(f"add-ons: {', '.join(a['addon'] for a in addons)}")
    for name in carried:
        print(f"  ℹ add-on {name!r} kept from {PIN_FILE} (drop it with --without {name})")
    print()

    # 1. skills hub + runtime symlinks
    for name in skills:
        src = find_skill_src(name)
        copy_tree(src, repo / ".harness" / "skills" / name, dry=dry, log=log)
        ensure_symlink(
            repo / ".harness" / "skills" / name,
            repo / ".claude" / "skills" / name,
            dry=dry,
            log=log,
        )

    # 2. shared references
    copy_tree(KIT_ROOT / "references", repo / ".harness" / "references", dry=dry, log=log)

    # 2b. add-on sources (added or refreshed; dropped ones removed)
    for addon in addons:
        copy_tree(addon["_dir"], repo / ".harness" / "addons" / addon["addon"], dry=dry, log=log)
    for name in dropped:
        dest = repo / ".harness" / "addons" / name
        if dest.exists():
            log.append(f"  {'[dry-run] ' if dry else '✔ '}remove  {dest}")
            if not dry:
                shutil.rmtree(dest)

    # 3. constitution rules
    if rules_stack:
        copy_tree(KIT_ROOT / "rules" / rules_stack, repo / ".claude" / "rules", dry=dry, log=log)

    # 4. profile copy
    prof_dest = repo / ".harness" / "profile.yaml"
    log.append(f"  {'[dry-run] ' if dry else '✔ '}install  {prof_dest}")
    if not dry:
        prof_dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(KIT_ROOT / "profiles" / f"{args.profile}.yaml", prof_dest)

    # 4b. add-on settings merged into .claude/settings.json
    if addons:
        upsert_settings(repo, addons, dry=dry, log=log)

    # 5. CLAUDE.md managed block
    block = render_block(args.profile, skills, rules_stack, addons, profile)
    upsert_claude_md(repo, block, dry=dry, log=log)

    # 6. pin record (manifest computed from what is now on disk)
    print("\n".join(log))
    for name in dropped:
        addon_yaml = ADDONS_ROOT / name / "addon.yaml"
        if addon_yaml.is_file():
            entries = settings_entries(load_addon(name).get("settings") or {})
            print(
                f"\n  ℹ {SETTINGS_REL} keeps the {name!r} entries (the team may rely on some of "
                f"them). Remove by hand if no longer wanted:"
            )
            print("\n".join(f"      {e}" for e in entries))
    if dry:
        print(f"\nDry-run only — re-run with --apply to write {PIN_FILE} and files.")
        return 0

    manifest = dir_manifest(repo / ".harness", repo)
    if rules_stack:
        manifest.update(dir_manifest(repo / ".claude" / "rules", repo))
    pin = {
        "kit": "skills_launchpad",
        "kit_version": kit_version(),
        "profile": args.profile,
        "delivery_contract": "sdd-delivery/v2",
        "skills": skills,
    }
    if addons:
        pin["addons"] = {
            a["addon"]: {
                "plugin": a.get("plugin"),
                "plugin_version": a.get("plugin_version"),
                "marketplace_ref": addon_marketplace_ref(a),
            }
            for a in addons
        }
    pin["manifest"] = manifest
    (repo / PIN_FILE).write_text(yaml.safe_dump(pin, sort_keys=False))
    print(f"  ✔ {PIN_FILE}  ({len(manifest)} files pinned)")
    print("\nDone. Commit .harness/, .claude/, CLAUDE.md and " + PIN_FILE + ".")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    repo = Path(args.repo).expanduser().resolve()
    pin_path = repo / PIN_FILE
    if not pin_path.is_file():
        print(f"✖ {PIN_FILE} missing — run `harness apply` first")
        return 1
    pin = yaml.safe_load(pin_path.read_text())
    problems: list[str] = []

    for rel, want in (pin.get("manifest") or {}).items():
        p = repo / rel
        if not p.is_file():
            problems.append(f"missing: {rel}")
        elif sha256_file(p) != want:
            problems.append(f"drift:   {rel}")

    for name in pin.get("skills") or []:
        link = repo / ".claude" / "skills" / name
        if not (link / "SKILL.md").is_file():
            problems.append(f"runtime: .claude/skills/{name} does not resolve to a SKILL.md")

    claude_md = repo / "CLAUDE.md"
    if not claude_md.is_file() or MARK_START not in claude_md.read_text():
        problems.append("CLAUDE.md: managed harness block missing")

    # Add-ons: settings entries are required; machine checks are warnings only.
    notes: list[tuple[bool, str]] = []
    for name in pin.get("addons") or {}:
        addon_dir = repo / ".harness" / "addons" / name
        if not (addon_dir / "addon.yaml").is_file():
            problems.append(f"add-on {name}: .harness/addons/{name}/addon.yaml missing")
            continue
        addon = read_addon(addon_dir, name)
        try:
            current = read_settings(repo)
        except SystemExit as exc:
            problems.append(f"settings: {exc}")
            continue
        problems += [
            f"settings: {name}: {p} in {SETTINGS_REL}"
            for p in settings_problems(current, addon.get("settings") or {})
        ]
        notes += addon_environment_notes(addon)

    print(f"pin: profile={pin.get('profile')} kit_version={pin.get('kit_version')}")
    if pin.get("addons"):
        print(f"add-ons: {', '.join(pin['addons'])}")
    for ok, text in notes:
        print(f"  {'·' if ok else '⚠'} {text}")
    if problems:
        print(f"✖ {len(problems)} problem(s):")
        for p in problems:
            print(f"  - {p}")
        return 1
    print(f"✔ harness OK — {len(pin.get('manifest') or {})} pinned files verified")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="harness", description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="show profiles, skills and add-ons").set_defaults(fn=cmd_list)

    p_apply = sub.add_parser("apply", help="seed rules + skills into a repo (dry-run by default)")
    p_apply.add_argument("--repo", required=True, help="target repo path")
    p_apply.add_argument("--profile", required=True, help="profile name (see `harness list`)")
    p_apply.add_argument("--apply", action="store_true", help="execute (default is dry-run)")
    p_apply.add_argument(
        "--with",
        dest="with_addons",
        action="append",
        default=[],
        metavar="ADDON",
        help="also apply an add-on (repeatable). Add-ons in the pin are kept on re-apply.",
    )
    p_apply.add_argument(
        "--without",
        dest="without_addons",
        action="append",
        default=[],
        metavar="ADDON",
        help="drop an add-on recorded in the pin (repeatable)",
    )
    p_apply.set_defaults(fn=cmd_apply)

    p_status = sub.add_parser("status", help="verify installed harness against the pin")
    p_status.add_argument("--repo", required=True, help="target repo path")
    p_status.set_defaults(fn=cmd_status)

    args = parser.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Harness kit CLI — seed pinned rules + Claude Code skills into a repo.

A VSCode / Claude Code adaptation of drivestream-lab's launchpad `apply-harness`:

  harness list                                   show profiles and their skills
  harness apply  --repo PATH --profile NAME      dry-run preview (default)
  harness apply  --repo PATH --profile NAME --apply
  harness status --repo PATH                     verify installed harness vs pin

On-disk contract in the target repo (mirrors launchpad):

  .harness/skills/<name>/       skill sources (real copies, committed)
  .harness/references/          shared contracts + workflow.yaml
  .harness/profile.yaml         copy of the applied profile
  .harness-pin.yaml             pin record: kit version + sha256 manifest
  .claude/rules/*.md            constitution (copies of kit rules/<stack>/)
  .claude/skills/<name>         relative symlinks into .harness/skills/
  CLAUDE.md                     managed block between harness markers
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sys
from pathlib import Path

import yaml

KIT_ROOT = Path(__file__).resolve().parent
MARK_START = "<!-- harness:start -->"
MARK_END = "<!-- harness:end -->"
PIN_FILE = ".harness-pin.yaml"

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

def render_block(profile_name: str, skills: list[str], rules_stack: str | None) -> str:
    tpl = (KIT_ROOT / "templates" / "CLAUDE.harness.md").read_text()
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
    return 0


def cmd_apply(args: argparse.Namespace) -> int:
    repo = Path(args.repo).expanduser().resolve()
    if not repo.is_dir():
        raise SystemExit(f"--repo {repo} is not a directory")
    profile = load_profile(args.profile)
    skills = profile_skills(profile)
    rules_stack = CONSTITUTION_BY_PROFILE.get(args.profile)
    dry = not args.apply
    log: list[str] = []

    print(f"{'DRY-RUN' if dry else 'APPLY'}: profile {args.profile} → {repo}\n")

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

    # 3. constitution rules
    if rules_stack:
        copy_tree(KIT_ROOT / "rules" / rules_stack, repo / ".claude" / "rules", dry=dry, log=log)

    # 4. profile copy
    prof_dest = repo / ".harness" / "profile.yaml"
    log.append(f"  {'[dry-run] ' if dry else '✔ '}install  {prof_dest}")
    if not dry:
        prof_dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(KIT_ROOT / "profiles" / f"{args.profile}.yaml", prof_dest)

    # 5. CLAUDE.md managed block
    upsert_claude_md(repo, render_block(args.profile, skills, rules_stack), dry=dry, log=log)

    # 6. pin record (manifest computed from what is now on disk)
    print("\n".join(log))
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
        "manifest": manifest,
    }
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

    print(f"pin: profile={pin.get('profile')} kit_version={pin.get('kit_version')}")
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

    sub.add_parser("list", help="show profiles and their skills").set_defaults(fn=cmd_list)

    p_apply = sub.add_parser("apply", help="seed rules + skills into a repo (dry-run by default)")
    p_apply.add_argument("--repo", required=True, help="target repo path")
    p_apply.add_argument("--profile", required=True, help="profile name (see `harness list`)")
    p_apply.add_argument("--apply", action="store_true", help="execute (default is dry-run)")
    p_apply.set_defaults(fn=cmd_apply)

    p_status = sub.add_parser("status", help="verify installed harness against the pin")
    p_status.add_argument("--repo", required=True, help="target repo path")
    p_status.set_defaults(fn=cmd_status)

    args = parser.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())

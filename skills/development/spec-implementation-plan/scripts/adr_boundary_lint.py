#!/usr/bin/env python3
"""ADR / TDD product-boundary lint (T12/P13 mechanical backstop).

T12 in `skills/development/spec-technical-review/references/checks.md` (and
P13 in the plan skill's checks.md) are otherwise a same-agent/same-process
re-read: the process that accepted the ADR also certifies it. This script is
a deterministic, judgment-independent check layered under that re-read.

Honesty note — read this before trusting a PASS. Three failure modes are
named explicitly rather than silently assumed away, because a lexical lint
genuinely cannot resolve them:

* A **loose semantic paraphrase** that shares no vocabulary with any
  supplied source text, and uses no forbidden phrase, cannot be detected —
  that requires an independent model or human reviewer, not more regexes.
* **Invented behavior under a real, correctly-cited REQ id** (metadata
  flags falsely left `false`) is only partially mitigated: this script can
  catch a citation to a REQ id outside a supplied approved set, or an
  internally inconsistent/invalid metadata table, but it cannot verify that
  the *content* of a citation is faithful to that REQ's actual scope.
* **Multiple decisions bundled into one un-duplicated Recommendation
  section** (no repeated heading, just several decisions narrated in one
  block of prose) is not distinguishable from one large decision by a
  parser that only sees markdown structure.

Everything else below is a genuine structural or lexical check, not a
placeholder:

1. **Structural integrity, case- and duplicate-aware**: every required
   section (Product decisions excluded, Context, Options considered,
   Recommendation, Consequences, Revisit triggers) must appear **exactly
   once**, matched case-insensitively (`## Context` and `## context` count
   as the same heading for duplicate detection). Each required section's
   body must be **non-empty** (a heading with no content is not a
   decision). Any heading that is neither a required section nor known
   process scaffolding (Lifecycle, Acceptance finalization) is flagged as
   **unrecognized** — and its content is still scanned for leakage, because
   an unrecognized heading (`## Customer outcome`, `## User experience`) is
   exactly where a drafter could hide prose the lint would otherwise never
   see. Audited text = title + every non-scaffolding section, known or not.
   Known process scaffolding (Lifecycle, Acceptance finalization) is exempt
   from structural/length rules but **not** from phrase/pattern scanning —
   it can still leak prose, it just isn't required to conform to the
   record shape.
2. **Title validation**: the `# ADR-{NNN} — {title}` line must match that
   shape with a **numeric** id (`ADR-014`, not `ADR-XYZ` — the template's
   own `{NNN}` and `adr-{NNN}-{slug}.md` filename convention are both
   numeric) and a non-empty title after an em-dash, and is itself scanned
   for forbidden phrasing.
3. **Forbidden product-register phrasing** (feature language / spec-drafting
   register such as "shall", "acceptance criteria") anywhere in the audited
   text.
4. **Metadata/state consistency, case- and duplicate-aware**: every metadata
   field is collected via *all* matching rows, matched case-insensitively
   on the field name — a second, conflicting `changes_user_visible_behavior`
   row is a `FAIL` even if it differs only in case
   (`Changes_User_Visible_Behavior`), not silently shadowed or invisible.
   `Status` must be one of `Draft` / `Accepted` / `Superseded`.
   `changes_user_visible_behavior` / `spec_amendment_required` must be
   literal `true`/`false`. An `Accepted` ADR must have both `false`, a
   non-placeholder `Approval evidence` and `Approved head` (rejects
   `Pending`, `TBD`, `-`, `N/A`, `none`, empty — not just literally
   "Pending"), and a `Lint evidence` row matching the shape
   `adr_boundary_lint.py N/M, PASS|FAIL, sha256:<hex>` — presence alone is
   not evidence; see `--verify-lint-evidence` for making the hash itself
   checkable, not just shaped correctly. `product_constraints` must be
   non-empty. Every `REQ-*` cited anywhere must be a member of a supplied
   `--approved-req-id` set, when one is supplied.
5. **Lexical overlap** with supplied source text, in three honestly-labeled
   tiers: exact/near-verbatim n-gram (strong), normalized/synonym-mapped
   n-gram (medium), bag-of-words Jaccard similarity (weak/heuristic). A
   **blank/whitespace-only** `--source-text` file does not count toward
   `sources_checked` — an empty file cannot satisfy `--require-sources`.
   Source files are keyed by resolved absolute path, not basename, so two
   different files sharing a filename cannot silently overwrite each other.
6. **Record body word-count bounds** ([60, 400]; target 150-400), computed
   over the same audited text as the phrase/pattern scan (unrecognized
   sections count toward length too — they are not a free pass around the
   ceiling either).
7. **`ALTERNATIVE:` marker validation** (`validate_finding_marker`) on the
   upstream feasibility Finding text: the marker must be present, followed
   by a substantive (>= 3 word) alternative, and that alternative text is
   itself scanned for product-register phrasing — `ALTERNATIVE: the user
   can upload once or twice` fails just as hard as a missing marker. A
   malformed finding must route back to `/initiative-feasibility`, never be
   silently re-derived downstream (see `spec-technical-review/SKILL.md` T1).
8. **TDD boundary check** (`lint_tdd_text`): the TDD's engineering
   free-text sections (§1 Problem statement, §5 Test policy, §9 Resolved
   engineering decisions) get the same phrase/pattern/overlap treatment as
   an ADR's audited text — T12 names the TDD explicitly, so it must not be
   manual-only. §10/§11 (routed PM/domain questions) are deliberately
   **not** scanned — they exist to carry genuine product-scope language.
9. **`--strict` bundles the production invocation**: implies
   `--require-sources` and additionally requires `--approved-req-id` and
   (ADR mode) `--finding-text-file` to be supplied together — these are not
   meant to be independently-optional flags where omitting one silently
   narrows what got checked.
10. **`--print-evidence` / `--verify-lint-evidence`**: `compute_evidence_digest`
    hashes the document (with its own Lint evidence row stripped, so it
    never hashes itself) plus the supplied sources. `--print-evidence`
    prints a ready-to-paste evidence line; `--verify-lint-evidence`
    recomputes the digest later and compares it to what's recorded. A
    match proves the recorded evidence is consistent with *this* file and
    *these* sources at verification time — it does **not** prove the
    original reviewer supplied correct sources, and it cannot force anyone
    to actually run `--verify-lint-evidence` in the first place. Closing
    that requires a real CI gate in the *consumer* repo (outside this
    meta-repo's boundary), not a static script.

Strict/production mode (`--require-sources`): fails closed if zero
non-empty `--source-text` files are supplied, so "I ran the lint" cannot
silently mean "I ran it with no ability to detect overlap." Without this
flag, a bare `adr_boundary_lint.py file.md` with no sources is a real but
narrow check (structure + phrasing + metadata only) — the `sources_checked`
field in the result always reports how many *non-empty, distinct* sources
were actually compared, so a caller can tell the difference.

CLI:
  python scripts/adr_boundary_lint.py <adr.md> [--source-text path]...
    [--approved-req-id REQ-01]... [--require-sources]
    [--finding-text-file path] [--json]
  python scripts/adr_boundary_lint.py --tdd <tdd.md> [--source-text path]...
    [--require-sources] [--json]

Import:
  from scripts.adr_boundary_lint import (
      lint_adr_text, lint_tdd_text, validate_finding_marker,
  )
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

REQ_ID_RE = re.compile(r"REQ-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*")
TITLE_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
# ADR ids are purely numeric per the template ('# ADR-{NNN} — {title}' and
# '{adr_dir}/adr-{NNN}-{slug}.md') — 'ADR-XYZ' is not a valid id, just text
# that happens to start with the right prefix.
TITLE_SHAPE_RE = re.compile(r"^ADR-\d+\s+—\s+\S.*$")
FINDING_MARKER = "ALTERNATIVE:"
MIN_ALTERNATIVE_WORDS = 3
PLACEHOLDER_VALUES = frozenset({"", "pending", "tbd", "n/a", "na", "-", "none", "todo"})
LINT_EVIDENCE_SHAPE_RE = re.compile(
    r"adr_boundary_lint\.py\s+\d+/\d+,\s*(PASS|FAIL),\s*sha256:([0-9a-f]{8,64})",
    re.IGNORECASE,
)

# Plain-substring signals of product/feature register rather than an
# engineering decision. Kept short and precise on purpose — a lint that
# over-fires on ordinary engineering prose ("the client sends a request")
# gets ignored.
FORBIDDEN_PHRASES = (
    "the user",
    "as a user",
    "end user",
    "end-user",
    "user can",
    "users can",
    "user should",
    "users should",
    "user must",
    "users must",
    "user-visible",
    "acceptance criteria",
    "acceptance criterion",
)

# Regex signals where a plain substring would be too imprecise (word
# boundaries matter) or where the register marker is a single word.
FORBIDDEN_PATTERNS = (
    re.compile(r"\bshall\b", re.IGNORECASE),
)

RECORD_BODY_MIN_WORDS = 60
RECORD_BODY_MAX_WORDS = 400
OVERLAP_NGRAM_SIZE = 6
PARAPHRASE_NGRAM_SIZE = 5
JACCARD_THRESHOLD = 0.55
JACCARD_MIN_SHARED_WORDS = 6

SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)

STOPWORDS = frozenset(
    """
    a an the this that these those to of in on for and or with as by be is
    are was were will would can could shall should must may might not no
    it its at from into over under so than then when if while do does did
    has have had which who whom whose we you they he she i our your their
    per via each every both either neither also only just still yet all
    """.split()
)

# Hand-authored, deliberately small: normalizes a few plausible paraphrase
# axes so a synonym swap collapses to the same token before comparison.
# This is a floor, not a semantic model (see module docstring). Extend this
# map when a real paraphrase bypass is found in review.
SYNONYM_MAP = {
    "single": "one",
    "once": "one",
    "mandatory": "required",
    "deliverable": "output",
    "deliverables": "output",
    "outputs": "output",
    "submission": "upload",
    "submissions": "upload",
    "uploads": "upload",
    "uploading": "upload",
    "produces": "generate",
    "produce": "generate",
    "generates": "generate",
    "generating": "generate",
    "users": "user",
}

# Required ADR sections (canonical display casing, in record order) and
# recognized process scaffolding (audited for structure only, never for
# content — see adr-template.md). Matched case-insensitively.
REQUIRED_SECTIONS = [
    "Product decisions excluded",
    "Context",
    "Options considered",
    "Recommendation",
    "Consequences",
    "Revisit triggers",
]
REQUIRED_SECTIONS_NORM = {s.lower(): s for s in REQUIRED_SECTIONS}
SCAFFOLDING_SECTIONS_NORM = {
    "lifecycle — accepted immutability and supersession",
    "acceptance finalization",
}
ALLOWED_STATUSES = {"draft", "accepted", "superseded"}

# TDD free-text sections that carry the same leakage risk as an ADR's
# Context. Deliberately does NOT include "§10 Routed out — product
# questions (PM)" or "§11 Routed out — domain clarifications (SME)" — those
# sections exist specifically to carry genuine product-scope language for
# PM/domain routing (see governance.md routing rubric); scanning them with
# a product-register phrase list would be a permanent false-positive
# generator, not a leakage detector. Extend this set only for sections that
# are supposed to be pure engineering content.
TDD_AUDITED_SECTIONS = {
    "1. problem statement",
    "5. test policy",
    "9. resolved engineering decisions",
}


@dataclass
class LintResult:
    ok: bool
    violations: list[str] = field(default_factory=list)
    sources_checked: int = 0


def _section_occurrences(text: str) -> list[tuple[str, str]]:
    """Every '## Heading' occurrence in document order as (raw_heading,
    body) — never deduplicated. A dict-based split cannot express duplicate
    or case-variant headings; always use this for structural checks."""
    matches = list(SECTION_RE.finditer(text))
    occurrences = []
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        occurrences.append((m.group(1).strip(), text[start:end].strip()))
    return occurrences


def _title(text: str) -> str:
    m = TITLE_RE.search(text)
    return m.group(1) if m else ""


def _word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


def _tokens(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9']+", text.lower())


def _ngrams(words: list[str], n: int) -> set[str]:
    return {" ".join(words[i : i + n]) for i in range(max(0, len(words) - n + 1))}


def _normalized_content_words(text: str) -> list[str]:
    """Lowercase, drop stopwords/short tokens, apply the synonym map — the
    sequence used for paraphrase-pattern n-grams and Jaccard similarity."""
    out = []
    for tok in _tokens(text):
        if len(tok) <= 2 or tok in STOPWORDS:
            continue
        out.append(SYNONYM_MAP.get(tok, tok))
    return out


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _phrase_and_pattern_violations(text: str, where: str) -> list[str]:
    violations = []
    lowered = text.lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase in lowered:
            violations.append(
                f"forbidden product-register phrase in {where}: {phrase!r} — "
                f"restate in engineering vocabulary or move to the spec/TDD"
            )
    for pattern in FORBIDDEN_PATTERNS:
        if pattern.search(text):
            violations.append(
                f"forbidden product-register pattern in {where}: "
                f"/{pattern.pattern}/ — this is spec-drafting voice "
                f"(e.g. \"the system shall...\"), not a decision voice "
                f"(\"we will...\")"
            )
    return violations


def _overlap_violations(
    audited_text: str,
    source_texts: dict[str, str],
) -> tuple[list[str], int]:
    """Returns (violations, sources_checked). Blank/whitespace-only source
    texts are excluded from sources_checked — they cannot satisfy
    --require-sources and cannot produce a meaningful overlap signal."""
    violations: list[str] = []
    non_empty_sources = {
        label: text for label, text in source_texts.items() if text.strip()
    }
    for label, text in source_texts.items():
        if not text.strip():
            violations.append(
                f"source {label!r} is empty/whitespace-only — it does not "
                f"count toward sources_checked and cannot detect overlap"
            )

    adr_raw_words = _tokens(audited_text)
    adr_exact_ngrams = _ngrams(adr_raw_words, OVERLAP_NGRAM_SIZE)
    adr_norm_words = _normalized_content_words(audited_text)
    adr_norm_ngrams = _ngrams(adr_norm_words, PARAPHRASE_NGRAM_SIZE)
    adr_content_set = set(adr_norm_words)

    for label, source_text in non_empty_sources.items():
        source_raw_words = _tokens(source_text)
        exact_overlap = adr_exact_ngrams & _ngrams(source_raw_words, OVERLAP_NGRAM_SIZE)
        if exact_overlap:
            sample = next(iter(exact_overlap))
            violations.append(
                f"verbatim/near-verbatim overlap (>= {OVERLAP_NGRAM_SIZE} words) "
                f"with source {label!r}: \"...{sample}...\" — cite the id, do not "
                f"quote or paraphrase the source prose"
            )
            continue

        source_norm_words = _normalized_content_words(source_text)
        norm_overlap = adr_norm_ngrams & _ngrams(source_norm_words, PARAPHRASE_NGRAM_SIZE)
        if norm_overlap:
            sample = next(iter(norm_overlap))
            violations.append(
                f"normalized paraphrase overlap (>= {PARAPHRASE_NGRAM_SIZE} "
                f"content words after stopword/synonym normalization) with "
                f"source {label!r}: \"...{sample}...\" — reads as a reworded "
                f"copy, not an independent engineering statement"
            )
            continue

        source_content_set = set(source_norm_words)
        ratio = _jaccard(adr_content_set, source_content_set)
        shared = len(adr_content_set & source_content_set)
        if ratio >= JACCARD_THRESHOLD and shared >= JACCARD_MIN_SHARED_WORDS:
            violations.append(
                f"high lexical similarity (Jaccard {ratio:.2f}, {shared} shared "
                f"content words) with source {label!r} — heuristic signal only; "
                f"have a human confirm whether this is an independent "
                f"engineering statement or a loose paraphrase"
            )

    return violations, len(non_empty_sources)


def validate_finding_marker(finding_text: str) -> list[str]:
    """Validate a feasibility NEW-ADR Finding cell against the ALTERNATIVE:
    contract. A malformed finding must route back to /initiative-feasibility
    for correction — spec-technical-review must not infer/re-derive the
    alternative itself (see SKILL.md T1)."""
    text = finding_text.strip()
    if not text:
        return ["finding text is empty — cannot validate ALTERNATIVE: marker"]
    if not text.startswith(FINDING_MARKER):
        return [
            f"finding does not start with the required {FINDING_MARKER!r} "
            f"marker — this is malformed upstream input; route it back to "
            f"/initiative-feasibility for correction, do not infer the "
            f"alternative downstream: {text[:80]!r}..."
        ]
    remainder = text[len(FINDING_MARKER):].strip()
    violations: list[str] = []
    if len(remainder.split()) < MIN_ALTERNATIVE_WORDS:
        violations.append(
            f"{FINDING_MARKER} marker present but the alternative text is "
            f"too short/bare ({remainder!r}) — name the actual technical "
            f"alternative, not a placeholder"
        )
    violations.extend(_phrase_and_pattern_violations(remainder, "the ALTERNATIVE: text"))
    return violations


def _field_values(text: str, field_name: str) -> list[str]:
    """All row values for a metadata field, in document order — never just
    the first match, so a duplicated/conflicting row is visible.
    Case-insensitive on the field name: `Changes_User_Visible_Behavior` and
    `changes_user_visible_behavior` are the same field, not two different
    ones — a case-sensitive match here would make a shadow conflicting row
    invisible instead of merely unflagged."""
    pattern = re.compile(
        rf"^\|\s*{re.escape(field_name)}\s*\|\s*([^|]*?)\s*\|",
        re.MULTILINE | re.IGNORECASE,
    )
    return [m.group(1).strip().strip("`") for m in pattern.finditer(text)]


def _duplicate_or_conflicting(values: list[str]) -> str | None:
    if len(values) <= 1:
        return None
    distinct = set(v.lower() for v in values)
    if len(distinct) > 1:
        return f"conflicting values {values}"
    return f"duplicated row ({len(values)}x) with the same value {values[0]!r}"


def _metadata_violations(
    adr_text: str,
    approved_req_ids: set[str] | None,
) -> list[str]:
    violations: list[str] = []

    flags: dict[str, str | None] = {}
    for field_name in ("changes_user_visible_behavior", "spec_amendment_required"):
        values = _field_values(adr_text, field_name)
        conflict = _duplicate_or_conflicting(values)
        if conflict:
            violations.append(f"metadata field `{field_name}` has {conflict}")
        value = values[0].lower() if values else None
        if value not in ("true", "false"):
            violations.append(
                f"metadata field `{field_name}` is missing or not a literal "
                f"true/false — cannot verify the product-boundary gate"
            )
            value = None
        flags[field_name] = value

    status_values = _field_values(adr_text, "Status")
    status_conflict = _duplicate_or_conflicting(status_values)
    if status_conflict:
        violations.append(f"metadata field `Status` has {status_conflict}")
    status = status_values[0] if status_values else None
    if status is None:
        violations.append("metadata field `Status` is missing")
    elif status.lower() not in ALLOWED_STATUSES:
        violations.append(
            f"metadata field `Status` is {status!r}, not one of "
            f"{sorted(ALLOWED_STATUSES)}"
        )
    elif status.lower() == "accepted":
        if flags.get("changes_user_visible_behavior") == "true":
            violations.append(
                "Status is Accepted but `changes_user_visible_behavior: true` — "
                "per adr-template.md this must never be Accepted while true"
            )
        if flags.get("spec_amendment_required") == "true":
            violations.append(
                "Status is Accepted but `spec_amendment_required: true` — "
                "per adr-template.md this must never be Accepted while true"
            )
        for approval_field in ("Approval evidence", "Approved head"):
            values = _field_values(adr_text, approval_field)
            value = values[0].strip().lower() if values else ""
            if value in PLACEHOLDER_VALUES:
                violations.append(
                    f"Status is Accepted but `{approval_field}` is still "
                    f"{values[0] if values else 'missing'!r} — acceptance "
                    f"is not evidenced"
                )
        lint_evidence_values = _field_values(adr_text, "Lint evidence")
        lint_evidence = lint_evidence_values[0] if lint_evidence_values else ""
        if not lint_evidence or not LINT_EVIDENCE_SHAPE_RE.search(lint_evidence):
            violations.append(
                f"Status is Accepted but `Lint evidence` ({lint_evidence!r}) "
                f"does not match the required shape "
                f"'adr_boundary_lint.py N/M, PASS, sha256:<hex>' — presence "
                f"alone (e.g. 'yes', 'TBD', '-') is not evidence. Note: a "
                f"shape match only proves the field looks right, not that "
                f"the digest is genuine — run with --verify-lint-evidence to "
                f"recompute and compare it against this file + the sources"
            )

    pc_values = _field_values(adr_text, "product_constraints")
    pc_ids = set()
    for v in pc_values:
        pc_ids |= set(REQ_ID_RE.findall(v))
    if not pc_ids:
        violations.append(
            "metadata field `product_constraints` cites no REQ-* id — every "
            "ADR must bind at least one approved requirement"
        )

    if approved_req_ids:
        cited_ids = set(REQ_ID_RE.findall(adr_text))
        unapproved = cited_ids - approved_req_ids
        if unapproved:
            violations.append(
                f"cites {sorted(unapproved)} which are not in the supplied "
                f"approved REQ-* set — possible fabricated or unapproved "
                f"requirement citation"
            )

    return violations


def _structural_violations(occurrences: list[tuple[str, str]]) -> tuple[list[str], str]:
    """Returns (violations, audited_non_metadata_text). audited text is
    title-agnostic here — the title is added separately by callers."""
    violations: list[str] = []
    counts: dict[str, int] = {}
    bodies_by_norm: dict[str, list[str]] = {}
    unrecognized_bodies: list[str] = []

    for raw_heading, body in occurrences:
        norm = raw_heading.lower()
        if norm in SCAFFOLDING_SECTIONS_NORM:
            continue
        counts[norm] = counts.get(norm, 0) + 1
        bodies_by_norm.setdefault(norm, []).append(body)
        if norm not in REQUIRED_SECTIONS_NORM:
            violations.append(
                f"unrecognized section '## {raw_heading}' — not one of the "
                f"required sections or known process scaffolding; its "
                f"content is still scanned for leakage below, but rename or "
                f"fold it into a required section"
            )
            unrecognized_bodies.append(body)

    for name in REQUIRED_SECTIONS:
        norm = name.lower()
        count = counts.get(norm, 0)
        if count == 0:
            violations.append(f"missing required section: '## {name}'")
        elif count > 1:
            violations.append(
                f"section '## {name}' appears {count} times (case-insensitive "
                f"match) — a decision record must have each required section "
                f"exactly once; duplicated sections often mean multiple "
                f"independent decisions were bundled into one ADR file "
                f"(split them)"
            )
        if count >= 1 and not any(b.strip() for b in bodies_by_norm.get(norm, [])):
            violations.append(
                f"required section '## {name}' exists but is empty — a "
                f"heading with no content is not a decision"
            )

    audited_parts = [
        body for norm, bodies in bodies_by_norm.items() for body in bodies
        if norm in REQUIRED_SECTIONS_NORM
    ] + unrecognized_bodies
    return violations, "\n\n".join(audited_parts)


def _scaffolding_text(occurrences: list[tuple[str, str]]) -> str:
    """Process-scaffolding sections (Lifecycle, Acceptance finalization) are
    exempt from structural/length checks — they're allowed to be template
    boilerplate — but that is not the same as exempt from leakage scanning.
    A drafter could still add product prose here; scan it defensively even
    though it never counts toward word-count or exactly-once requirements."""
    return "\n\n".join(
        body for raw, body in occurrences if raw.lower() in SCAFFOLDING_SECTIONS_NORM
    )


def lint_adr_text(
    adr_text: str,
    source_texts: dict[str, str] | None = None,
    *,
    require_sources: bool = False,
    approved_req_ids: set[str] | None = None,
    finding_text: str | None = None,
) -> LintResult:
    """Lint one ADR file's text.

    `source_texts` maps a label (e.g. a REQ id, or "feasibility-evidence")
    to text that must NOT appear verbatim, near-verbatim, or as a mechanical
    paraphrase inside the ADR's audited text — pass the cited REQ's spec
    sentence and/or the feasibility finding's "spec quote" text here.

    `require_sources=True` fails closed when zero *non-empty* source texts
    are supplied (strict/production mode for T12/P13 — see module docstring).

    `approved_req_ids`, when supplied, is the initiative's full approved
    REQ-* id set; any REQ-* cited in the ADR outside this set is flagged.

    `finding_text`, when supplied, is the upstream feasibility Finding cell
    text for this NEW-ADR — validated against the ALTERNATIVE: marker
    contract (see `validate_finding_marker`).
    """
    violations: list[str] = []

    if finding_text is not None:
        violations.extend(validate_finding_marker(finding_text))

    occurrences = _section_occurrences(adr_text)
    structural_violations, section_text = _structural_violations(occurrences)
    violations.extend(structural_violations)

    title = _title(adr_text)
    if not TITLE_SHAPE_RE.match(title):
        violations.append(
            f"title {title!r} does not match the required 'ADR-{{NNN}} — "
            f"{{title}}' shape"
        )

    audited_text = "\n\n".join([title, section_text])
    violations.extend(_phrase_and_pattern_violations(audited_text, "the ADR title/audited sections"))
    scaffolding_text = _scaffolding_text(occurrences)
    if scaffolding_text.strip():
        violations.extend(
            _phrase_and_pattern_violations(
                scaffolding_text, "the Lifecycle/Acceptance finalization scaffolding"
            )
        )

    context_and_recommendation = "\n\n".join(
        body for raw, body in occurrences
        if raw.lower() in ("context", "recommendation")
    )
    if not REQ_ID_RE.search(context_and_recommendation):
        violations.append(
            "no REQ-* id referenced in Context or Recommendation — an ADR must "
            "cite the approved requirement(s) it binds"
        )

    violations.extend(_metadata_violations(adr_text, approved_req_ids))

    word_count = _word_count(section_text)
    if word_count > RECORD_BODY_MAX_WORDS:
        violations.append(
            f"record body is {word_count} words (> {RECORD_BODY_MAX_WORDS}) — "
            f"design-doc smell; split into multiple ADRs or move detail to the TDD"
        )
    elif word_count < RECORD_BODY_MIN_WORDS:
        violations.append(
            f"record body is only {word_count} words (< {RECORD_BODY_MIN_WORDS}) — "
            f"too thin to show real engineering analysis (context, options, "
            f"trade-offs); a minimal file that only satisfies T11 structure "
            f"without reasoning is not a decision record"
        )

    source_texts = source_texts or {}
    overlap_violations, sources_checked = _overlap_violations(audited_text, source_texts)
    violations.extend(overlap_violations)

    if require_sources and sources_checked == 0:
        violations.append(
            "--require-sources is set but zero non-empty source texts were "
            "supplied/usable — overlap/paraphrase detection did not run; a "
            "lint PASS under these conditions only proves "
            "structure/phrasing/metadata, not the absence of copy-through "
            "leakage"
        )

    return LintResult(ok=not violations, violations=violations, sources_checked=sources_checked)


def lint_tdd_text(
    tdd_text: str,
    source_texts: dict[str, str] | None = None,
    *,
    require_sources: bool = False,
) -> LintResult:
    """Lint a Technical Design Document's engineering free-text sections
    (§1 Problem statement, §5 Test policy, §9 Resolved engineering
    decisions — see TDD_AUDITED_SECTIONS for why §10/§11 are deliberately
    excluded) for the same product-register leakage an ADR is checked for.
    T12 names the TDD explicitly ("Every user-visible normative statement
    in the TDD or ADR...") — this closes the gap where only ADRs had a
    mechanical check and the TDD was manual-only. Still not exhaustive:
    §2/§3/§6/§7/§8 are pure-engineering sections judged low leakage risk and
    are not scanned — extend TDD_AUDITED_SECTIONS if that assumption proves
    wrong in practice."""
    violations: list[str] = []
    occurrences = _section_occurrences(tdd_text)
    audited_parts = [
        body for raw, body in occurrences
        if raw.strip().lower() in TDD_AUDITED_SECTIONS
    ]
    if not audited_parts:
        violations.append(
            "no recognized TDD free-text section found (expected a heading "
            "matching one of: " + ", ".join(sorted(TDD_AUDITED_SECTIONS)) + ")"
        )
    audited_text = "\n\n".join(audited_parts)
    violations.extend(_phrase_and_pattern_violations(audited_text, "the TDD audited sections"))

    source_texts = source_texts or {}
    overlap_violations, sources_checked = _overlap_violations(audited_text, source_texts)
    violations.extend(overlap_violations)

    if require_sources and sources_checked == 0:
        violations.append(
            "--require-sources is set but zero non-empty source texts were "
            "supplied/usable"
        )

    return LintResult(ok=not violations, violations=violations, sources_checked=sources_checked)


LINT_EVIDENCE_ROW_RE = re.compile(
    r"^\|\s*Lint evidence\s*\|[^|]*\|\s*$", re.MULTILINE | re.IGNORECASE
)


def compute_evidence_digest(document_text: str, source_texts: dict[str, str] | None) -> str:
    """Canonical digest over the document (with any existing 'Lint evidence'
    row stripped first, so the row never hashes itself — idempotent whether
    called before or after the row is written) plus the sorted, labeled
    source texts used. `--verify-lint-evidence` recomputes this and compares
    it to the recorded hash: a match proves the recorded evidence is
    consistent with *this* file content and *these* sources, at verification
    time — it does not prove the original PE reviewer supplied the correct
    sources, only that nobody has silently changed the file or claimed a
    digest inconsistent with it. Read `--verify-lint-evidence`'s docstring
    note before treating a match as unconditional proof."""
    stripped = LINT_EVIDENCE_ROW_RE.sub("", document_text).strip()
    sources_canonical = "\n".join(
        f"{label}:{text}" for label, text in sorted((source_texts or {}).items())
    )
    canonical = stripped + "\n---SOURCES---\n" + sources_canonical
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _load_source_texts(paths: list[str]) -> dict[str, str] | None:
    """Key by resolved absolute path, not basename — two different files
    sharing a filename must not silently overwrite each other's entry."""
    source_texts: dict[str, str] = {}
    for source_path in paths:
        p = Path(source_path)
        if not p.is_file():
            print(f"error: source-text file not found: {source_path}", file=sys.stderr)
            return None
        source_texts[str(p.resolve())] = p.read_text(encoding="utf-8")
    return source_texts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lint an ADR or TDD file for product-boundary leakage")
    parser.add_argument("path", type=Path, help="ADR or TDD markdown file")
    parser.add_argument(
        "--tdd",
        action="store_true",
        help="Lint as a Technical Design Document instead of an ADR",
    )
    parser.add_argument(
        "--source-text",
        action="append",
        default=[],
        metavar="PATH",
        help="Path to REQ/spec/feasibility-evidence text to check for overlap "
        "(repeatable)",
    )
    parser.add_argument(
        "--require-sources",
        action="store_true",
        help="Fail if zero non-empty --source-text files are supplied (strict/production mode)",
    )
    parser.add_argument(
        "--approved-req-id",
        action="append",
        default=[],
        metavar="REQ-ID",
        help="An approved REQ-* id for this initiative (repeatable, ADR mode only). "
        "When any are supplied, every REQ-* cited in the ADR must be a member of this set",
    )
    parser.add_argument(
        "--finding-text-file",
        type=Path,
        default=None,
        help="Path to the upstream feasibility NEW-ADR Finding text (ADR mode only), "
        "validated against the ALTERNATIVE: marker contract",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Production/bundle mode: implies --require-sources and additionally "
        "requires --approved-req-id and (ADR mode) --finding-text-file to be "
        "supplied — the recommended T12/P13 invocation, not an a-la-carte set "
        "of independently-optional flags",
    )
    parser.add_argument(
        "--print-evidence",
        action="store_true",
        help="Print a ready-to-paste 'Lint evidence: adr_boundary_lint.py N/M, "
        "PASS|FAIL, sha256:<hex>' line for the ADR's Acceptance finalization "
        "block (ADR mode only)",
    )
    parser.add_argument(
        "--verify-lint-evidence",
        action="store_true",
        help="Recompute the evidence digest from this file + supplied sources and "
        "compare it to the recorded 'Lint evidence' row; mismatch is a violation "
        "(ADR mode only). See compute_evidence_digest's docstring for what a "
        "match does and does not prove",
    )
    parser.add_argument("--json", action="store_true", help="Emit result as JSON")
    args = parser.parse_args(argv)

    if not args.path.is_file():
        print(f"error: file not found: {args.path}", file=sys.stderr)
        return 2

    doc_text = args.path.read_text(encoding="utf-8")
    source_texts = _load_source_texts(args.source_text)
    if source_texts is None:
        return 2
    require_sources = args.require_sources or args.strict

    if args.tdd:
        result = lint_tdd_text(doc_text, source_texts, require_sources=require_sources)
    else:
        finding_text = None
        if args.finding_text_file is not None:
            if not args.finding_text_file.is_file():
                print(f"error: finding-text file not found: {args.finding_text_file}", file=sys.stderr)
                return 2
            finding_text = args.finding_text_file.read_text(encoding="utf-8")

        bundle_violations = []
        if args.strict:
            if not args.approved_req_id:
                bundle_violations.append(
                    "--strict requires --approved-req-id (at least one) — "
                    "omitting it is not a valid production invocation"
                )
            if finding_text is None:
                bundle_violations.append(
                    "--strict requires --finding-text-file — omitting it is not "
                    "a valid production invocation"
                )

        result = lint_adr_text(
            doc_text,
            source_texts,
            require_sources=require_sources,
            approved_req_ids=set(args.approved_req_id) or None,
            finding_text=finding_text,
        )
        if bundle_violations:
            result = LintResult(
                ok=False,
                violations=result.violations + bundle_violations,
                sources_checked=result.sources_checked,
            )

        if args.print_evidence:
            digest = compute_evidence_digest(doc_text, source_texts)
            status = "PASS" if result.ok else "FAIL"
            print(
                f"Lint evidence: adr_boundary_lint.py "
                f"{result.sources_checked}/{len(args.source_text)}, {status}, "
                f"sha256:{digest}"
            )

        if args.verify_lint_evidence:
            recorded = LINT_EVIDENCE_SHAPE_RE.search(doc_text)
            if not recorded:
                result.violations.append(
                    "--verify-lint-evidence requested but no valid 'Lint "
                    "evidence' row was found to verify"
                )
                result = LintResult(ok=False, violations=result.violations, sources_checked=result.sources_checked)
            else:
                recomputed = compute_evidence_digest(doc_text, source_texts)
                if recomputed != recorded.group(2).lower():
                    result.violations.append(
                        f"recorded Lint evidence digest {recorded.group(2)} does "
                        f"not match the recomputed digest {recomputed} from this "
                        f"file + supplied sources — evidence is stale or fabricated"
                    )
                    result = LintResult(ok=False, violations=result.violations, sources_checked=result.sources_checked)

    if args.json:
        print(
            json.dumps(
                {
                    "ok": result.ok,
                    "violations": result.violations,
                    "sources_checked": result.sources_checked,
                },
                indent=2,
            )
        )
    elif result.violations:
        print(
            f"lint FAILED ({len(result.violations)} violation(s), "
            f"{result.sources_checked} source(s) checked)\n"
        )
        for v in result.violations:
            print(f"  - {v}")
    else:
        print(f"lint passed ({result.sources_checked} source(s) checked).")

    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())

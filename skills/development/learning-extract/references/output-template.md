# Output template — learning extract

Save to `{reports_dir}/Learning-Extract-{initiative}-W{N}.md`.

## Markdown body

```markdown
# Learning extract — {initiative} W{N}

| Field | Value |
|-------|-------|
| Wave | W{N} — {wave title} |
| Initiative | {initiative} |
| Branch / head | `{branch}` @ `{sha}` |
| Pass-1 tip (approx) | `{pass1_sha_or_note}` |
| human_fix_detected | yes / no |
| Date | {YYYY-MM-DD} |

## Learnings

| ID | Class | Summary | Evidence | Codify hint | Status |
|----|-------|---------|----------|-------------|--------|
| L-01 | SKILL | … | path / commit | loop-spec / prompt X | open |

## Signals

- verify_evidence: {command or n/a}
- notes: …

## Ready for ground-spec?

yes / no — reason
```

## Required YAML fence (same file)

Include exactly one fenced `yaml` block:

    learning_extract:
      initiative: {initiative}
      wave: W{N}
      human_fix_detected: true
      items:
        - id: L-01
          class: SKILL
          summary: "…"
          evidence:
            - "…"
          codify_hint:
            target: skill
            ref: "loop-spec"
          status: open

Append handoff envelope (stage `learning-extract`) per
`.harness/references/handoff-envelope.md`.

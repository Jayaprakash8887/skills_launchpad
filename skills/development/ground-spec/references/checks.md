# Ground spec — checks (G1–G10)

Run every check. PASS = zero open grounding findings that block sign-off.
SKIPPED = missing optional input (state reason). Fail closed when a required
check cannot run.

Ids: `.harness/references/id-conventions.md`. Findings use **`GF-*`**, never
feasibility-owned `FF-*`.

| ID | Check | Evidence required |
|----|-------|-------------------|
| G1 | **Wave scope** | Grounding covers only the completed wave `W{N}` and REQs assigned to that wave by the plan / WorkManifest TASK `implements` lists — not every future REQ in the full product spec |
| G2 | **Ground command / evidence** | `{ground_command}` output included when defined; otherwise manual `source_roots` + `tests/**` scan documented. Unit (`{test_command}`) and human accept (`wave-accepted` / wave-acceptance; optional/legacy Live-Verify-*) are cited separately |
| G3 | **Assigned-REQ coverage** | Every wave-assigned `REQ-*` appears in the REQ checklist with verifiable artifact (entry point, test, live script, module boundary) |
| G4 | **Acceptance evidence** | Each assigned REQ maps to observable acceptance evidence from loop/unit artifacts and human accept (`Wave-Execution-*`, unit results, `wave-accepted`). When the wave declared `CAP-*` / `J-*` live covers or `human_observations`, cite those ids and look-at completion (ack = `wave-accepted`) — optional/legacy Live-Verify-* not required; logs alone are not sole evidence for opaque sinks |
| G5 | **ADR boundaries** | Domain-filtered Accepted ADRs checked; no contradiction without an open `GF-*` |
| G6 | **MDC boundaries** | Domain-filtered `rules_glob` checked; pattern contradictions recorded as `GF-*` |
| G7 | **Contracts consumed / produced** | Consumed contracts match prior Ground Reports; §Contracts produced complete for next-wave `/pre-implement` |
| G8 | **Learning citations** | When `Learning-Extract-{INIT}-W{N}.md` exists, cite `L-*` ids only — do not re-author learning SSOT |
| G9 | **Stable GF-* findings** | Discrepancies use stable `GF-{nn}` ids; cite `REQ-*` in the row; blockers use `GF-*` not bare check numbers |
| G10 | **Complete handoff** | Canonical Ground Report path written; as-built left as `human_approved` from wave-acceptance (do not re-mark); exact-head **merge package** prepared for `wave-signoff`; envelope stage `ground-spec` with outcome + next `wave-done-action` on pass (then `wave-signoff` merge only) — no commit/merge by this skill |

Severity: **Blocking** (cannot `pass` to wave-signoff), **Should fix**, **Verify**.

**Blocking** when: G1 scopes future waves; G3 misses an assigned REQ; G7
§Contracts produced incomplete; G9 uses `FF-*` or unstable ids; G10 omits
handoff or claims merge/commit by this skill.

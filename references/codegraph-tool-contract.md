# Codegraph tool contract (SSOT)

Shared, walker-neutral interface for an optional codegraph/knowledge-graph
tool a skill **may** use during a hop — a `Tool`, not `Forge`
([forge-side-effects.md](forge-side-effects.md)). Promoted out of
`skills/engg-reviews/references/codegraph-provider.md`, which now points at
this file for the abstract interface and keeps its own Graphify/fleet-layout
specifics.

## Why "Tool," not "Forge"

| | Tools | Forge |
|--|-------|-------|
| When | During the skill hop | After the hop, on a following `external-action` |
| Who | Agent runtime may call | ForgeClient (runner) or human forge skill |
| What | Assist / read | Commit tree, Draft PR, projection labels, board tickets |

A codegraph tool never mutates anything and never needs `authorization`
semantics. It is always optional: present or absent, a skill's outcome
selection is unaffected. **Never block or degrade an outcome on its
absence** — that is the one rule every packaged skill referencing this
contract must follow.

## Interface

| Operation | Meaning |
|-----------|---------|
| `ensure_graph(repo_path, sha)` | Graph exists and matches freshness policy for this checkout |
| `query(repo_path, question)` | Search/ask a question of the graph (BM25, Cypher, semantic, etc. — provider-specific) |
| `path(repo_path, a, b)` | Trace a relationship between two nodes (callers, callees, data flow) |
| `explain(repo_path, node)` | Plain-language / structural context for one node |
| `freshness(repo_path)` | Return the SHA / digest the graph was built against |

Implementations vary (local CLI, MCP server, something else) — a skill's
procedure targets this interface, not a named product.

## Freshness and confidence — not optional caveats, load-bearing ones

A codegraph is a point-in-time index, not a live view of the repo. Two
failure modes are real, not theoretical, and both were reproduced live
against a production index while building this contract:

1. **Staleness.** A symbol that genuinely exists in the current checkout can
   return zero results if the graph was built before that symbol landed.
   Check `freshness` against the current checkout's SHA before treating an
   absence as "doesn't exist."
2. **Edge confidence.** Dependency-injection-resolved calls, dynamic
   dispatch, and similar indirection often don't appear as static edges even
   when a real runtime relationship exists. Tag or note confidence
   (`EXTRACTED` / `INFERRED` / `AMBIGUOUS`, or provider-equivalent) — never
   treat a missing edge as proof of no relationship.

## Degraded mode

No provider available, or freshness/confidence can't be established: fall
back to direct `source_roots` reads (grep/glob/semantic search — whatever
the walker already has natively). This is not a lesser path — a direct
file read is ground truth by construction, just less pre-computed. Record
`signals.codegraph_provider` (`local-graphify` | `mcp-<name>` | `degraded-none`)
and `signals.grounding_depth` (`deep` | `light` | `none`) when a stage's
handoff already carries `signals`.

## Two walkers, one tool-availability question

The skill's procedure never needs to know which walker is running it or
which concrete adapter backs the tool — it only checks "is a codegraph
capability present in my tool context right now."

- **Human walker:** whatever MCP servers or CLIs are already configured in
  the IDE session. No prayog-skills-side plumbing needed — this already
  works today, using the same tool-calling mechanism as any other MCP tool.
- **Orchestrated walker:** the orchestrator's own infrastructure decides
  whether this hop's agent session gets a codegraph tool attached (e.g. by
  passing MCP server connection details into whatever SDK call spins up the
  agent). That is entirely the orchestrator's own scoped work — see
  `../docs/for-gateflow.md` for the one concrete example this repo has
  documented. Nothing here assumes any specific orchestrator implements it.

## Non-goals

Not a requirement for any skill to function — every packaged skill already
works via direct `source_roots` reads without this. Not a prayog-skills
deliverable to build a provider, an MCP server, or orchestrator-side wiring
— those belong to whoever operates the walker.

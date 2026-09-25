# Quality confidence ladder (SSOT)

Incremental product confidence as the environment gets more real.
Stack-agnostic — Python, Android, iOS, Flink, Next, edge, terraform use the
same rungs; only ingress/probe syntax differs (profile + repo helpers).

See also: [live-fixture-contract.md](live-fixture-contract.md),
[workmanifest-contract.md](workmanifest-contract.md),
[id-conventions.md](id-conventions.md),
[live-verify-coverage-contract.md](live-verify-coverage-contract.md).

## Rungs

| Rung | Environment | Keys on live `covers` | Agent bar | Human / lab bar |
|------|-------------|----------------------|-----------|-----------------|
| **Unit** | Process + mocks | — (unit evidence on REQ) | `check` + `test` | — |
| **Capability** | Black box + **real infra** + minimal fixture | **`CAP-*`** (+ related `REQ-*`) | Implement fixtures + driver | Run capability prove and/or look-ats |
| **Journey** | Same + multi-step orchestration | **`J-*`** (+ related `REQ-*`) | Implement fixture pack + driver | Run journey prove and/or look-ats |

**Capability ≠ journey.** Passing all journeys for a CAP does not replace a
capability-rung prove, and a single-ability smoke does not replace a journey.

## Rules

1. **Infra is real** for capability and journey (Postgres, Redis, Kafka, …).
2. **External modules** (vendor/model/SaaS) may stub/sandbox only when declared
   in prerequisites / `human_observations`.
3. **Preflight** before capability/journey regression — dependencies reachable.
4. **Stimulus** comes from fixture packs ([live-fixture-contract.md](live-fixture-contract.md)),
   not from poking internal setters.
5. **Logs / stdout are not sole evidence.** Prefer SoT probes (DB, topic, HTTP)
   or declared **`human_observations`** (opaque cloud/console).
6. **`wave-accepted`** on the tip is human acknowledgement of scripted prove
   **and** prescribed look-ats. There is **no** `/verify` content skill that
   auto-passes.
7. **Generate only ids that downstream consumes** — see [id-conventions.md](id-conventions.md).

## Human observations (inspection)

When product truth is opaque (publish to cloud, vendor UI):

```yaml
human_observations:
  - locus: "Cloud console → tenant X → deployments"
    expect: "New revision R visible within 2 minutes"
    covers: [CAP-03, REQ-12]
```

Agent may still run stimulus/preflight. Agent must **not** claim pass via
logfile greps for those outcomes.

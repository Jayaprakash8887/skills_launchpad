# Learning extract — checks

| Id | Check | Fail closed? |
|----|-------|--------------|
| Lx1 | Initiative + wave N resolved | yes |
| Lx2 | Artifact path under `reports_dir` | yes |
| Lx3 | Fenced `learning_extract:` YAML present and parseable | yes |
| Lx4 | Each item has `id` (`L-*`), `class`, `summary`, `codify_hint`, `status` | yes |
| Lx5 | `class` ∈ {SPEC, SKILL, HARNESS, ENV} | yes |
| Lx6 | Empty items only with explicit no-human-fix rationale | yes |
| Lx7 | Does not claim Ground Report / §Contracts produced complete | yes |

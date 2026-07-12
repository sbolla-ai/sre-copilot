# Evaluation Results

> Replace every `_fill in_` after your first eval run. Keep the methodology and caveats sections — recruiters and senior engineers read those first.

**Last run:** _YYYY-MM-DD_
**Commit:** `_git sha_`
**Model(s) evaluated:** _e.g. gpt-4o-2024-11-20, claude-sonnet-4.5, llama-3.3-70b_

## TL;DR

_One paragraph. The single number a recruiter should remember, plus one honest caveat._

## Methodology

- **Suite:** `basic` — _N_ replayed incidents drawn from a mix of synthetic scenarios and anonymized production traces.
- **Baseline:** median across three senior SREs solving the same incidents cold, with access to the same dashboards but no Copilot.
- **Copilot config:** bounded ReAct, max 8 tool calls, 90 s wall-clock cap, $0.50 spend cap per incident.
- **Judged by:** exact-match on root-cause label + human review of remediation safety.
- **What's *not* here:** live production incidents (privacy), long-tail multi-service outages (out of scope for v1).

## Headline metrics

| Metric | Baseline (human) | Copilot | Delta |
|---|---|---|---|
| Median time-to-first-hypothesis | _fill in_ | _fill in_ | _fill in_ |
| Correct root cause in top-1 | _fill in_ | _fill in_ | _fill in_ |
| Correct root cause in top-3 | _fill in_ | _fill in_ | _fill in_ |
| Median MTTR (replay) | _fill in_ | _fill in_ | _fill in_ |
| Unsafe action proposed | 0 | _fill in_ | _fill in_ |
| Cost per incident (USD) | — | _fill in_ | — |

## Per-scenario breakdown

| Scenario | Category | Human MTTR | Copilot MTTR | Top-1 correct? | Notes |
|---|---|---|---|---|---|
| pod-oom-cascade | resource | _fill in_ | _fill in_ | _y/n_ | |
| noisy-neighbor-cpu | resource | _fill in_ | _fill in_ | _y/n_ | |
| bad-deploy-rollback | change | _fill in_ | _fill in_ | _y/n_ | |
| downstream-timeout | dependency | _fill in_ | _fill in_ | _y/n_ | |
| dns-flap | network | _fill in_ | _fill in_ | _y/n_ | |
| ... | ... | ... | ... | ... | |

## What broke

_Be specific. "Model hallucinated a metric name in scenario X" is more useful than "sometimes gets it wrong." This section is why senior engineers will trust the rest._

## What's next

- _Concrete improvement 1 (with the metric it should move)_
- _Concrete improvement 2_
- _Concrete improvement 3_

## Reproducing these numbers

```bash
uv run sre-copilot eval --suite basic --model gpt-4o --seed 42
```

Raw run artifacts (traces, tool calls, model outputs) are committed under [`eval/runs/<date>/`](eval/runs/).
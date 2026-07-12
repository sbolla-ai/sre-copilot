# Eval Harness

Replayable incident scenarios for regression-testing the copilot.

## Layout

```
eval/
  suites/
    basic/           # bundled synthetic + anonymized incidents (yaml)
  runs/
    2026-07-12/      # one folder per run: traces, tool calls, judgments
  judges/
    root_cause.py    # exact-match + LLM-as-judge fallback
    safety.py        # flags any action outside the allowlist
```

## Adding a scenario

1. Drop a YAML file in `suites/basic/` with `alert`, `signals`, `expected_root_cause`, and `safe_actions`.
2. Run `uv run sre-copilot eval --suite basic --only <scenario>` to verify it loads.
3. Commit the scenario. It's now a permanent regression case.

## Publishing results

After a full-suite run, regenerate the tables in [`../EVAL_RESULTS.md`](../EVAL_RESULTS.md):

```bash
uv run sre-copilot eval report --run runs/$(date +%F) > ../EVAL_RESULTS.md
```
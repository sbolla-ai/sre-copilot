# Build Guide

A step-by-step plan for filling in the scaffold. Estimated total time:
25–35 hours over a month. Work in order — each phase depends on the previous.

## Phase 1 — Get one incident running end-to-end (6–8 hours)

**Goal:** Run the agent against a single hardcoded incident, see it produce
some valid output (any output type is fine for now).

### Step 1.1: Implement `enforce_scope_limits` in `src/agent/boundaries.py`

Look at the docstring. The TDD tests in `tests/test_boundaries.py` describe
exactly what behavior to implement. Run `pytest tests/test_boundaries.py`
until everything passes.

### Step 1.2: Implement the three MCP tool stubs in `src/mcp_server/tools.py`

`query_logs`, `query_metrics`, `get_deployment_timeline`. Each should:
- Filter the bound incident's data by the requested args
- Format the output as a string (Splunk-shaped)
- Handle the empty-result case clearly

### Step 1.3: Build one fixture incident in `src/incidents/fixtures.py`

A simple deploy regression: one service named `api-gateway`, a deploy 30
minutes before incident start, a metric series showing elevated latency
after the deploy, a few log lines. Hardcode it.

### Step 1.4: Implement `run_agent` in `src/agent/agent.py`

Wire `AgentExecutor` output into `AgentRunRecord`. Handle the timeout case
by returning an `Abstention`.

### Step 1.5: Run it

```bash
export ANTHROPIC_API_KEY=sk-ant-...
python -m src.agent.cli --incident-id fixture_deploy_001
```

Watch what happens. The agent should call `get_deployment_timeline` first
(forced), find the deploy, then query metrics or logs, and emit one of the
three output types.

**Definition of done:** `tests/test_agent_basic.py` passes.

---

## Phase 2 — Synthetic incident generator (8–12 hours)

**Goal:** Generate hundreds of realistic incidents with known ground-truth.

### Step 2.1: Implement helper functions in `IncidentGenerator`

`_generate_baseline_metric_series` and `_inject_anomaly` are the building
blocks for everything else.

### Step 2.2: Implement `_build_deploy_regression`

The easiest archetype. Use it to nail down the structure before tackling
harder ones.

### Step 2.3: Implement `_build_downstream_dependency`

Service A calls service B; B degrades; A's metrics get worse as a knock-on
effect. The agent should follow the chain.

### Step 2.4: Implement `_build_noisy_neighbor`

Resource contention from a co-located service. No deploy event, no
downstream cause — the smoking gun is correlated CPU spikes.

### Step 2.5: Implement `_build_misleading_correlation`

The most important one. Spend extra time here. The whole article hinges on
this archetype existing in your eval set.

### Step 2.6: Implement `generate_eval_set`

Mix the four archetypes. Consider oversampling misleading_correlation.

### Step 2.7: Generate the eval set

```bash
python scripts/generate_eval_set.py --n 200
```

**Definition of done:** `tests/test_incident_generator.py` passes,
and you have 200 incidents in `data/incidents/`.

---

## Phase 3 — Eval harness and corroboration (6–8 hours)

**Goal:** Measure agent accuracy on the eval set, with and without
corroboration enabled.

### Step 3.1: Implement `synthesize_finding` in `src/agent/corroboration.py`

The decision tree: ≥2 signal types → Recommendation, 1 signal → Observation,
0 → Abstention.

### Step 3.2: Implement `compare` in `src/eval/metrics.py`

Compare agent output to ground truth. Be careful with the "correct service
identified but wrong archetype" partial-credit case.

### Step 3.3: Implement `run_eval_suite` in `src/eval/runner.py`

Loop, capture results, generate a markdown report.

### Step 3.4: Run baseline eval (corroboration OFF)

Add a config flag to disable corroboration. Run the full eval set.
Record the numbers.

### Step 3.5: Run improved eval (corroboration ON)

Re-run with corroboration. Compare.

If you've built it right, you'll see:
- Confident-wrong rate goes DOWN (the article's main claim)
- Some correct Recommendations move to Observations
- Total useful output (correct Rec + accurate Obs) stays similar or improves

**Definition of done:** A file in `docs/EVAL_RESULTS.md` with the before/after
numbers. This is the data the article's claims are now backed by.

---

## Phase 4 — Observability and evidence chains (4–6 hours)

**Goal:** Wire OpenTelemetry to a real backend, surface evidence chains
in the agent UI.

### Step 4.1: Bring up Jaeger

```bash
docker compose -f docker/docker-compose.yml up -d
```

Visit http://localhost:16686 to confirm it's running.

### Step 4.2: Call `init_tracing()` in the agent CLI startup

Add it to `src/agent/cli.py:main()`. Run an agent invocation. Confirm
traces appear in Jaeger.

### Step 4.3: Wrap tool calls in `trace_tool_call`

Modify the boundary wrapper in `src/agent/boundaries.py:make_boundary_wrapper`
to wrap the tool execution in a span.

### Step 4.4: Add evidence-chain attributes to recommendation spans

Use `record_recommendation_evidence` when the agent emits a Recommendation.

### Step 4.5: Build a small CLI viewer for evidence chains

`scripts/show_evidence.py <recommendation_id>` — pretty-prints the chain.

**Definition of done:** You can run an incident, see the trace in Jaeger,
and click into a span to see the recommendation's evidence chain as a
JSON attribute.

---

## Phase 5 — Polish (optional)

See `PROJECT_STATUS.md` for the polish backlog.

---

## When you're done

The article is fully truthful as soon as Phase 3 is complete. Phases 4 and
5 are credibility multipliers.

After Phase 3, update `PROJECT_STATUS.md` to mark phases complete, push to
GitHub, and link the repo from the article. You're done.

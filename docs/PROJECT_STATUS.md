# Project Status

> Live tracker of what's implemented vs. what's in progress. Update this as you build.

## Done (scaffold)

- [x] Repository structure
- [x] Docker compose for local observability stack (placeholder containers, configure as you go)
- [x] MCP server skeleton with three tool definitions (`query_logs`, `query_metrics`, `get_deployment_timeline`)
- [x] LangChain ReAct agent skeleton with Claude integration
- [x] OpenTelemetry instrumentation framework for the agent loop
- [x] Eval harness skeleton (loads incidents, runs agent, compares to ground truth)
- [x] Test scaffolding (pytest configured, fixtures in place)
- [x] CLI entry points

## Phase 1 — Boundary enforcement (start here)

**Goal:** Get the basic agent loop working with a single hardcoded incident.

- [ ] Implement `src/agent/boundaries.py` — read-only enforcement, scope limiting
- [ ] Implement `src/agent/agent.py:build_agent()` — wire LangChain ReAct properly
- [ ] Implement `src/mcp_server/tools.py:query_logs()` — return synthetic log data based on params
- [ ] Implement `src/mcp_server/tools.py:query_metrics()` — same for metrics
- [ ] Write 1 hardcoded incident in `src/incidents/fixtures.py` to test against
- [ ] Make `tests/test_agent_basic.py` pass

**Estimated time:** 6–8 hours

**Article alignment:** This is "Section 1: Boundaries" of the article. Once this works, you can honestly write about read-only defaults, bounded data context, and the explicit-abstain pattern.

## Phase 2 — Synthetic incident generator

**Goal:** Generate hundreds of realistic incidents with known ground-truth causes.

- [ ] Implement `src/incidents/generator.py:IncidentGenerator` — main API
- [ ] Implement at least 4 incident archetypes:
  - [ ] Deploy regression (the canonical case)
  - [ ] Downstream dependency degradation
  - [ ] Noisy-neighbor / resource contention
  - [ ] Misleading correlation (a service looks bad, isn't actually causal)
- [ ] Each incident produces: time series of metrics, log entries, and a deploy timeline entry
- [ ] Each incident has a ground-truth `Cause` object the eval harness can compare to
- [ ] Generate 200 incidents to disk: `scripts/generate_eval_set.py`
- [ ] Make `tests/test_incident_generator.py` pass

**Estimated time:** 8–12 hours — this is the hardest part of the project.

**Article alignment:** This is the "trust anchor" of Section 2. The whole article hinges on having a real eval set with ground truth.

## Phase 3 — Eval harness + corroboration logic

**Goal:** Measure agent accuracy on the eval set, and implement the multi-signal corroboration rule.

- [ ] Implement `src/eval/runner.py:run_eval_suite()` — runs agent against all generated incidents
- [ ] Implement `src/eval/metrics.py:compare()` — compares agent output to ground truth
- [ ] Implement `src/agent/corroboration.py` — enforces the "two independent signals" rule before recommending
- [ ] Implement forced ordering: deployment timeline must be checked first
- [ ] Add an `Observation` vs. `Recommendation` distinction in the agent output schema
- [ ] Generate an eval report (markdown + JSON)
- [ ] Verify that accuracy improves when corroboration is on vs. off (this is your article's central claim)

**Estimated time:** 6–8 hours

**Article alignment:** Section 2's "What helped" subsection. Without this, the article's claim that "accuracy went up meaningfully" isn't backed by anything.

## Phase 4 — Observability + evidence chains

**Goal:** Instrument the agent itself, surface evidence chains in the output.

- [ ] Wire OpenTelemetry to a real backend (Jaeger or Honeycomb free tier)
- [ ] Emit traces for every tool call, with timing and token counts
- [ ] Emit a span attribute for each agent recommendation that includes the evidence chain
- [ ] Build a small CLI viewer that renders an incident's evidence chain readably
- [ ] Write a small "regression test" that runs a known incident and fails if accuracy drops

**Estimated time:** 4–6 hours

**Article alignment:** Section 3 of the article. Without this, the article's claim that observability drove improvements is unbacked.

## Phase 5 — Optional polish

These aren't required for the article to be honest, but they make the repo more impressive to a hiring manager browsing it:

- [ ] Streamlit or simple web UI showing incident timeline + agent reasoning
- [ ] GitHub Actions CI that runs the eval suite on every PR
- [ ] A `BENCHMARKS.md` doc with eval results before/after each architectural change
- [ ] A second LLM provider (OpenAI) wired through the same agent interface, for comparison
- [ ] Public Docker image so others can run it without local setup

## How to think about progress

The article is honest as soon as **Phase 3 is complete**. Phase 4 makes more of the article honest. Phase 5 is gravy.

If you finish only Phase 1 and 2, you should adjust the article to remove specific claims about accuracy improvements and observability-driven debugging. If you finish through Phase 3, the article's main claims are all defensible.

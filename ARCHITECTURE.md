# Architecture

![SRE Copilot architecture](docs/architecture.png)

## Design principles

1. **Human-in-the-loop by default.** The agent proposes; humans dispose. Autonomous actions require an explicit allowlist keyed by service, environment, and blast radius.
2. **Bounded reasoning.** Every ReAct loop is capped on wall-clock time, token spend, and number of tool calls. No runaway agents.
3. **MCP as the tool boundary.** Every side effect goes through a Model Context Protocol server with a typed schema. Swapping Prometheus for VictoriaMetrics is a config change, not a code change.
4. **Everything is replayable.** Alerts, traces, tool calls, and model outputs are recorded. Any incident can be re-run through a new model or prompt in the eval harness.
5. **The eval harness is the contract.** No prompt change ships without a green run on [`EVAL_RESULTS.md`](EVAL_RESULTS.md).

## Components

### Ingest & Normalize
Adapters for PagerDuty, Alertmanager, and generic webhooks convert incoming alerts into a common `Incident` schema (service, severity, symptoms, initial signals).

### Bounded ReAct Loop
A thin, auditable ReAct implementation. Each step: observe → think → act. Every step is persisted with token counts, latency, and tool arguments.

### MCP Tool Servers
- **Prometheus / Loki / Tempo** — read-only telemetry queries
- **Kubernetes** — read-only by default; write actions (rollback, scale, restart) require allowlist
- **Runbook** — executes vetted runbook steps as parameterized functions

### Policy Guardrails
A single choke point evaluating every proposed action against: service allowlist, environment (prod vs non-prod), blast-radius estimate, and current change-freeze state.

### Learning Loop
Resolved incidents flow into the Incident KB (vector + metadata). The eval harness samples from this KB to build regression suites, so real production incidents become permanent test cases.

## Non-goals

- Replacing on-call engineers
- Root-causing incidents that require code-level debugging (that's a human's job)
- Being a general-purpose chatops bot
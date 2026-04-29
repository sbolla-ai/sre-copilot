# SRE Copilot

A side project exploring agent-based incident triage using the [Model Context Protocol](https://modelcontextprotocol.io), LangChain, and a synthetic observability stack. Built as a learning project to understand where agent patterns hold up — and where they don't — when you actually try to ship one.

> **Status:** Scaffold + work in progress. See [`PROJECT_STATUS.md`](docs/PROJECT_STATUS.md) for what's implemented and what isn't.

## What this is (and isn't)

**This is:** A personal exploration of agent engineering for SRE workflows. The goal is to understand the boundaries, observability, and eval patterns that distinguish a demo-quality agent from one you'd actually trust under pressure. Built on synthetic data, not production systems.

**This isn't:** A production-ready SRE tool. It runs against a local Docker stack with synthetic logs and metrics. Don't point it at real systems without significant additional work on safety, auth, and write-path controls.

## The architecture

```
┌─────────────────┐
│  Synthetic      │  ← Generates realistic incidents
│  Incident Gen   │     with known ground-truth causes
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│  Local Docker   │ ───► │  MCP Server      │
│  Observability  │      │  (Splunk-shaped  │
│  Stack          │      │   tools)         │
└─────────────────┘      └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  LangChain       │
                         │  ReAct Agent     │
                         │  (Claude)        │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  Eval Harness    │
                         │  + OpenTelemetry │
                         └──────────────────┘
```

## Quick start

```bash
# 1. Install
pip install -e ".[dev]"

# 2. Bring up the local observability stack
docker compose -f docker/docker-compose.yml up -d

# 3. Set your API key
export ANTHROPIC_API_KEY=sk-ant-...

# 4. Run a single incident
python -m src.agent.run --incident-id deploy_regression_001

# 5. Run the full eval suite
python -m src.eval.run_suite
```

## Project structure

```
src/
├── agent/              # LangChain ReAct agent with boundary controls
├── mcp_server/         # MCP server exposing observability tools
├── incidents/          # Synthetic incident generator
├── observability/      # OpenTelemetry instrumentation for the agent itself
└── eval/               # Eval harness, metrics, and ground-truth comparison

tests/                  # Unit and integration tests
docker/                 # Local stack: log pipeline, metrics store
docs/                   # Architecture notes and decision logs
scripts/                # One-off scripts (data generation, exploration)
```

## What's implemented vs. what isn't

This repo is a **scaffold** — the infrastructure is in place, but the engineering decisions described in the [companion article](https://www.linkedin.com/in/sreenivas-bolla/) are the parts I'm building out incrementally. See [`PROJECT_STATUS.md`](docs/PROJECT_STATUS.md) for the current state.

If you're reading this in early stages: the boring parts (Docker, OTel plumbing, MCP boilerplate) are done. The interesting parts (incident generator, agent boundaries, corroboration logic) are in progress.

## License

MIT. See [`LICENSE`](LICENSE).

## Contact

Sreenivas Bolla — sbolla.tx@gmail.com
# sre-copilot

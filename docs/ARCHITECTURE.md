# Architecture Decisions

A short log of the major design choices in this project, with reasoning.
This doc exists so that anyone reading the code (including future you)
understands *why* each choice was made.

## ADR-001: Recommendations require ≥2 independent signal types

**Context:** The first version of the agent (no corroboration) produced
confidently wrong recommendations on misleading-correlation incidents.

**Decision:** A `Recommendation` requires evidence from at least 2 *distinct*
signal types (e.g., `deploy_correlation` + `metric_anomaly`). Single-signal
findings become `Observation`s instead.

**Enforcement:** At the schema layer (Pydantic validator on `Recommendation`).
The agent literally cannot construct a single-signal Recommendation without
the schema raising.

**Why this layer:** Putting the rule in code rather than the prompt means
the LLM cannot prompt-inject around it.

**Trade-off:** Some genuinely single-signal cases get downgraded to
Observations even when they're correct. Acceptable — the eval harness
shows that this conservativism reduces confident-wrong cases more than
it reduces correct-recommendations.

---

## ADR-002: Forced ordering — deployment timeline is always tool call #1

**Context:** Most incidents in production environments are change-induced.
The agent's reasoning was much better when it knew about recent deploys
before looking at metrics.

**Decision:** The boundary system rejects any first tool call that isn't
`get_deployment_timeline`.

**Why:** Anchoring the LLM's reasoning with deploy context up front
dramatically reduces the "confident reasoning over wrong evidence"
failure mode. It's a code-level fix for what would otherwise be a
prompt-engineering arms race.

**Trade-off:** A handful of incidents have no recent deploys and the deploy
check is "wasted." This is fine — knowing there were no deploys is itself
useful evidence (rules out change-induced cases).

---

## ADR-003: Three output types, not one

**Context:** A single "RootCause" output type forces the agent to commit
to an answer even when uncertain.

**Decision:** Three distinct types: `Recommendation`, `Observation`,
`Abstention`. The agent must produce one of these — a free-text answer is
not valid output.

**Why:** This is what gives the abstention path its structural weight.
"I don't know" is a first-class answer, not a fallback.

---

## ADR-004: Synthetic incidents over public datasets

**Context:** Public observability datasets exist (Loghub, etc.) but they
don't come with ground-truth root-cause labels.

**Decision:** Build a synthetic incident generator that produces incidents
with known causes.

**Why:** Without ground truth, you cannot measure agent accuracy honestly.
The whole eval harness depends on this.

**Trade-off:** Synthetic data is less realistic than real production data.
Mitigation: design the archetypes carefully, especially the
"misleading_correlation" archetype, which is what surfaces the article's
central failure mode.

---

## ADR-005: Tools are Splunk-shaped

**Context:** The MCP tools could expose any query language.

**Decision:** Tools mimic Splunk's query interface (service + time window
+ optional pattern), and return string output formatted like Splunk's
search response.

**Why:** Production observability stacks in regulated fintech are
overwhelmingly Splunk-based. Designing the tools this way makes the
project's lessons portable to real environments without rewriting the
agent or boundaries.

---

## ADR-006: OpenTelemetry for the agent itself

**Context:** Without observability into the agent's behavior, debugging
regressions is guesswork.

**Decision:** Every tool call, token count, and recommendation is emitted
as an OTel span with structured attributes.

**Why:** "The Copilot feels worse this week" should be answerable with
data, not vibes. Span attributes capture the evidence chain so you can
later query "show me all recommendations that cited this query."

**Trade-off:** OTel overhead. Negligible in practice; tool-call spans
add <5ms each.

"""Main agent — LangChain ReAct loop on top of Claude with boundary enforcement.

The agent itself is a fairly thin layer. The interesting work is in:
- boundaries.py — what the agent is allowed to do
- corroboration.py — what counts as a recommendation vs. observation
- schema.py — what valid agent output looks like
- ../incidents/generator.py — what the agent is reasoning over

That's the article's thesis in code form: the agent is the smallest part.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import StructuredTool

from .boundaries import ToolCallContext, make_boundary_wrapper
from .schema import AgentOutput, AgentRunRecord


SYSTEM_PROMPT = """You are an SRE Copilot assisting an on-call engineer with incident triage.

Your job is to identify the most likely root cause of the incident described, using the tools available.

**Critical operating rules:**

1. ALWAYS call `get_deployment_timeline` first. Most incidents are change-induced; this anchors your reasoning.

2. Each tool call must specify a SPECIFIC service and a TIGHT time window (max 2 hours).
   Do not query the whole observability lake.

3. You produce one of three output types:
   - **Recommendation** — a root cause supported by AT LEAST TWO INDEPENDENT signals
     (e.g., a deploy correlation AND a metric anomaly).
   - **Observation** — a single-signal finding. Use this when you only have one type of evidence.
   - **Abstention** — explicit "I don't have enough signal." This is a valid, expected output.
     Do not fabricate a chain of reasoning to avoid abstaining.

4. Every finding must cite the tool calls that produced its evidence.
   The on-call engineer needs to verify your reasoning in two clicks.

You will not be penalized for abstaining when uncertain. You WILL be penalized for
confident wrong answers.
"""


@dataclass
class AgentConfig:
    """Configuration for an agent run."""

    model: str = "claude-sonnet-4-5"
    max_iterations: int = 10
    temperature: float = 0.0
    api_key: str | None = None


def build_agent(
    tools: list[StructuredTool],
    config: AgentConfig | None = None,
) -> tuple[AgentExecutor, ToolCallContext]:
    """Construct the agent with all boundaries wired in.

    Returns the executor AND the context object — the context tracks tool-call
    history for the forced-ordering rule and is also useful for observability.

    TODO(you): Once the boundary stubs in boundaries.py are implemented, this
    function should "just work." If you want to extend it:
      - Add tool-call timeout handling
      - Add retry logic for transient MCP failures
      - Add per-tool token budget tracking
    """
    config = config or AgentConfig()
    api_key = config.api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Set ANTHROPIC_API_KEY environment variable, or pass config.api_key."
        )

    # Wrap every tool with boundary enforcement.
    context = ToolCallContext()
    bounded_tools = [
        StructuredTool.from_function(
            func=make_boundary_wrapper(tool.func, tool.name, context),
            name=tool.name,
            description=tool.description,
            args_schema=tool.args_schema,
        )
        for tool in tools
    ]

    llm = ChatAnthropic(
        model=config.model,
        temperature=config.temperature,
        api_key=api_key,
    )

    prompt = PromptTemplate.from_template(
        SYSTEM_PROMPT
        + "\n\nIncident description:\n{input}\n\n"
        + "Available tools:\n{tools}\n\nTool names: {tool_names}\n\n"
        + "{agent_scratchpad}"
    )

    agent = create_react_agent(llm=llm, tools=bounded_tools, prompt=prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=bounded_tools,
        max_iterations=config.max_iterations,
        verbose=False,
        return_intermediate_steps=True,
    )
    return executor, context


def run_agent(
    incident_description: str,
    tools: list[StructuredTool],
    config: AgentConfig | None = None,
) -> AgentRunRecord:
    """Run the agent on a single incident, return a complete run record.

    TODO(you): Implement the wiring between AgentExecutor's output and
    AgentRunRecord. Specifically:
      - Capture intermediate_steps and convert to tool_call_log
      - Sum token usage across all model calls
      - Parse the agent's final answer into one of the AgentOutput variants
      - Handle the case where the agent times out without producing valid output
        (return an Abstention, not raise)
    """
    # TODO(you): replace this stub
    raise NotImplementedError("Implement run_agent — see docstring")

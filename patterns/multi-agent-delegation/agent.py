"""
PATTERN: Multi-Agent Delegation (coordinator + specialists via AgentTool)
------------------------------------------------------------------------------
PURPOSE
    A coordinator LlmAgent that DELEGATES to specialist agents. Two ways to do it:
      (1) AgentTool  — wrap a specialist as a callable tool; the coordinator
          decides when to call it and gets the result back (explicit, testable).
      (2) sub_agents — LLM-driven handoff/transfer between agents (adaptive
          routing). Shown as a commented alternative below.
    Use when different subtasks need different expertise, instructions, or tools.

DEPENDENCIES
    pip install google-adk ; GOOGLE_API_KEY in .env

RUN
    my_agent/agent.py exposing `root_agent`; then `adk web` or `adk run my_agent`.
------------------------------------------------------------------------------
"""
from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

MODEL = "gemini-flash-latest"

# --- Specialists: each focused, with its own instruction (and its own tools) ---
math_specialist = LlmAgent(
    model=MODEL, name="math_specialist",
    description="Solves arithmetic and math word problems step by step.",
    instruction="You are a careful mathematician. Show your reasoning briefly.",
)

writer_specialist = LlmAgent(
    model=MODEL, name="writer_specialist",
    description="Writes and edits clear, concise prose.",
    instruction="You are an editor. Produce tight, well-structured text.",
)

# --- Coordinator: uses specialists as TOOLS (explicit delegation) --------------
# `description` on each specialist is what the coordinator reads to route well.
root_agent = LlmAgent(
    model=MODEL,
    name="coordinator",
    instruction=(
        "You route work to the right specialist tool. Use math_specialist for "
        "calculations and writer_specialist for drafting/editing. Combine their "
        "outputs into one answer for the user."
    ),
    tools=[
        AgentTool(agent=math_specialist),
        AgentTool(agent=writer_specialist),
    ],
)

# --- ALTERNATIVE: LLM-driven handoff via sub_agents ----------------------------
# root_agent = LlmAgent(
#     model=MODEL, name="coordinator",
#     instruction="Delegate to the best sub-agent for each request.",
#     sub_agents=[math_specialist, writer_specialist],  # ADK enables transfer
# )
# AgentTool = coordinator stays in control and gets results back.
# sub_agents = control can transfer to a specialist. Pick per task.

# ------------------------------------------------------------------------------
# PRODUCTION NOTES
#   * The `description` field is the routing signal — write it for the router,
#     not for humans. Vague descriptions = bad delegation.
#   * Prefer AgentTool when you need the coordinator to compose/verify results;
#     prefer sub_agents transfer when a specialist should fully own the turn.
#   * Keep specialists single-responsibility — easier to test, secure, and reuse
#     across projects (this is the "self-contained, pick-it-up-cold" principle).
#   * Guard against delegation loops; give the coordinator a clear stop rule.
# ------------------------------------------------------------------------------

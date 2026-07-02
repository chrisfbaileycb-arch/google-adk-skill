"""
PATTERN: SequentialAgent (deterministic pipeline)
------------------------------------------------------------------------------
PURPOSE
    Run sub-agents in a FIXED ORDER, each reading the previous one's output from
    shared session State. Use when a task has clear stages that must happen in
    sequence (e.g. draft -> critique -> revise, or extract -> transform -> load).
    Deterministic: no LLM decides the order — you do.

DEPENDENCIES
    pip install google-adk ; GOOGLE_API_KEY in .env

RUN
    my_agent/agent.py exposing `root_agent`; then `adk web` or `adk run my_agent`.

KEY IDEA
    `output_key` writes an agent's final text into session.state[<key>].
    Downstream agents read it via {curly_brace} templating in their instruction.
------------------------------------------------------------------------------
"""
from google.adk.agents import LlmAgent, SequentialAgent

MODEL = "gemini-flash-latest"

# Stage 1 — produce a first draft, store it under state['draft'].
drafter = LlmAgent(
    model=MODEL,
    name="drafter",
    instruction="Write a short first draft answering the user's request.",
    output_key="draft",  # -> session.state['draft']
)

# Stage 2 — critique the draft. Reads {draft} from state.
critic = LlmAgent(
    model=MODEL,
    name="critic",
    instruction=(
        "Critique this draft for accuracy, clarity, and gaps. Be specific.\n\n"
        "DRAFT:\n{draft}"
    ),
    output_key="critique",
)

# Stage 3 — revise using both the draft and the critique.
reviser = LlmAgent(
    model=MODEL,
    name="reviser",
    instruction=(
        "Rewrite the draft, fixing every issue in the critique.\n\n"
        "DRAFT:\n{draft}\n\nCRITIQUE:\n{critique}"
    ),
    output_key="final",
)

# The pipeline: sub_agents run top-to-bottom, sharing one session.
root_agent = SequentialAgent(
    name="draft_critique_revise",
    sub_agents=[drafter, critic, reviser],
)

# ------------------------------------------------------------------------------
# PRODUCTION NOTES
#   * State keys are your contract between stages — name them clearly and keep
#     them stable; a rename in one agent silently breaks the next.
#   * A stage can be a tool-using LlmAgent or even a nested workflow agent.
#   * Fail fast: validate critical state exists before a downstream stage relies
#     on it (a Callback is a good place to assert this).
#   * Sequential = predictable + debuggable. Prefer it over LLM routing whenever
#     the order is actually known — cheaper and easier to secure/audit.
# ------------------------------------------------------------------------------

"""
PATTERN: LoopAgent (iterate until good enough)
------------------------------------------------------------------------------
PURPOSE
    Repeat sub-agents until a condition is met or a max iteration count is hit.
    Use for refine-until-acceptable loops: generate -> check -> (if not good)
    improve -> check ... Ideal for quality gates, retries, and convergence.

DEPENDENCIES
    pip install google-adk ; GOOGLE_API_KEY in .env

RUN
    my_agent/agent.py exposing `root_agent`; then `adk web` or `adk run my_agent`.

HOW THE LOOP STOPS
    1) max_iterations acts as a hard safety cap, AND
    2) any sub-agent can end the loop early by escalating via tool_context
       (actions.escalate = True). Below, a checker tool escalates when quality
       passes so we don't waste iterations.
------------------------------------------------------------------------------
"""
from google.adk.agents import LlmAgent, LoopAgent
from google.adk.tools.tool_context import ToolContext

MODEL = "gemini-flash-latest"


def mark_done_if_good(assessment: str, tool_context: ToolContext) -> dict:
    """Call with 'pass' when the work meets the bar, else 'fail'.

    On 'pass', escalate to break the LoopAgent early.
    """
    passed = assessment.strip().lower() == "pass"
    if passed:
        tool_context.actions.escalate = True  # <- breaks the loop
    return {"status": "pass" if passed else "fail"}


# Worker: improve the current answer stored in state['work'].
improver = LlmAgent(
    model=MODEL, name="improver",
    instruction=(
        "Improve the current work to better satisfy the request. If there is no "
        "prior work, create a first version.\n\nCURRENT:\n{work?}"  # ? = optional
    ),
    output_key="work",
)

# Checker: judge quality; escalate (stop) when it passes.
checker = LlmAgent(
    model=MODEL, name="checker",
    instruction=(
        "Assess whether CURRENT fully meets the request. Then call "
        "mark_done_if_good with 'pass' or 'fail'.\n\nCURRENT:\n{work}"
    ),
    tools=[mark_done_if_good],
)

# Loop: improve then check, up to 5 times or until checker escalates.
root_agent = LoopAgent(
    name="refine_until_good",
    sub_agents=[improver, checker],
    max_iterations=5,  # HARD CAP — always set one to prevent runaway cost.
)

# ------------------------------------------------------------------------------
# PRODUCTION NOTES
#   * ALWAYS set max_iterations. Escalation can fail; the cap is your safety net.
#   * Use {work?} (optional) so the first iteration doesn't error on empty state.
#   * Loops multiply cost: iterations x (worker + checker) LLM calls. Monitor it.
#   * Make the stop condition objective where possible (schema/validator/tests)
#     rather than "the LLM thinks it's good."
# ------------------------------------------------------------------------------

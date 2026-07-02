"""
PATTERN: Single LlmAgent
------------------------------------------------------------------------------
PURPOSE
    The simplest ADK shape: one LLM-backed agent that reasons and calls tools.
    Use for a self-contained task where one agent + a few tools is enough
    (Q&A, lookups, single-step automations). Start here; only add orchestration
    (sequential/parallel/loop/multi-agent) when you actually need it.

DEPENDENCIES
    pip install google-adk
    GOOGLE_API_KEY set in .env (Google AI Studio) OR Vertex AI config.

RUN
    Place this file at:  my_agent/agent.py   (package must expose `root_agent`)
    cd ./my_agent && adk web        # Dev UI   (adk web --no-reload on Windows)
    or: adk run my_agent            # CLI

SWAP-TO-CUSTOMIZE
    - Replace `get_current_time` with your own tool function.
    - Change `model` and `instruction`.
------------------------------------------------------------------------------
"""
from datetime import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import LlmAgent


# --- Tool: a plain Python function becomes a tool automatically ---------------
def get_current_time(timezone: str = "America/Denver") -> dict:
    """Return the current time for an IANA timezone (e.g. 'America/Denver').

    Docstrings matter: the LLM reads them to decide when/how to call the tool.
    Return a dict so results are structured and easy for the model to use.
    """
    try:
        now = datetime.now(ZoneInfo(timezone))
        return {"status": "ok", "timezone": timezone, "time": now.isoformat()}
    except Exception as e:  # PRODUCTION: never leak raw tracebacks to the model
        return {"status": "error", "message": f"Invalid timezone: {timezone}"}


# --- The agent: `root_agent` is the ONLY required export ----------------------
root_agent = LlmAgent(
    model="gemini-flash-latest",
    name="single_agent",
    instruction=(
        "You are a concise assistant. Use tools when they give a more accurate "
        "answer than guessing. If a tool returns status='error', explain the "
        "problem plainly and ask for a correction."
    ),
    tools=[get_current_time],
)

# ------------------------------------------------------------------------------
# PRODUCTION NOTES
#   * Keep secrets in .env / env vars — never hardcode API keys in agent.py.
#   * Tool functions must validate inputs and return structured errors, not raise.
#   * Log tool calls with a Callback for observability before you scale.
#   * Evaluate with an eval dataset (adk eval) before deploying.
#   * This is the leanest connector shape — no MCP overhead. Reach for MCP only
#     when the capability lives in an external server you don't want to reimplement.
# ------------------------------------------------------------------------------

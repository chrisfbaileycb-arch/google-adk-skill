# Pattern: Single LlmAgent

**Purpose:** One LLM-backed agent that reasons and calls tools. The leanest ADK shape — start here.

**When to use:** Self-contained tasks where one agent + a few tools is enough (Q&A, lookups, single-step automations).

**Dependencies:** `pip install google-adk`; `GOOGLE_API_KEY` in `.env`.

**Run:** place as `my_agent/agent.py` (must export `root_agent`), then `adk web` or `adk run my_agent`.

**Customize:** swap `get_current_time` for your tool; change `model` + `instruction`.

See `agent.py` for annotated code and production notes.

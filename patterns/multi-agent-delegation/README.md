# Pattern: Multi-Agent Delegation (coordinator + specialists)

**Purpose:** A coordinator that delegates to specialist agents via `AgentTool` (explicit) or `sub_agents` transfer (adaptive).

**When to use:** Different subtasks need different expertise, instructions, or tools.

**Dependencies:** `pip install google-adk`; `GOOGLE_API_KEY` in `.env`.

**Run:** place as `my_agent/agent.py` (exports `root_agent`), then `adk web` or `adk run my_agent`.

**Routing signal:** each specialist's `description` field is what the coordinator reads to route — write it for the router.

See `agent.py` for annotated code and production notes.

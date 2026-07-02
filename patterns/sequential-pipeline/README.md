# Pattern: SequentialAgent (deterministic pipeline)

**Purpose:** Run sub-agents in a fixed order, each reading the previous output from shared session State.

**When to use:** Clear stages that must happen in sequence — draft → critique → revise, or extract → transform → load.

**Dependencies:** `pip install google-adk`; `GOOGLE_API_KEY` in `.env`.

**Run:** place as `my_agent/agent.py` (exports `root_agent`), then `adk web` or `adk run my_agent`.

**Key idea:** `output_key` writes to `session.state[key]`; downstream agents read it via `{key}` templating.

See `agent.py` for annotated code and production notes.

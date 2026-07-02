# Pattern: LoopAgent (iterate until good enough)

**Purpose:** Repeat sub-agents until a condition is met or `max_iterations` is hit.

**When to use:** Refine-until-acceptable loops, quality gates, retries, convergence.

**Dependencies:** `pip install google-adk`; `GOOGLE_API_KEY` in `.env`.

**Run:** place as `my_agent/agent.py` (exports `root_agent`), then `adk web` or `adk run my_agent`.

**Stop conditions:** `max_iterations` hard cap AND early exit via `tool_context.actions.escalate = True`.

See `agent.py` for annotated code and production notes.

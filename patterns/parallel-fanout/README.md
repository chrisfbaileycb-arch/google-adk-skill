# Pattern: ParallelAgent (fan-out, then gather)

**Purpose:** Run independent sub-agents concurrently, then merge results with a synthesizer.

**When to use:** Subtasks that don't depend on each other (research N competitors at once) — cuts latency.

**Dependencies:** `pip install google-adk`; `GOOGLE_API_KEY` in `.env`.

**Run:** place as `my_agent/agent.py` (exports `root_agent`), then `adk web` or `adk run my_agent`.

**Critical:** each parallel worker must write to a distinct `output_key` (avoids race conditions).

See `agent.py` for annotated code and production notes.

"""
PATTERN: ParallelAgent (fan-out, then gather)
------------------------------------------------------------------------------
PURPOSE
    Run independent sub-agents CONCURRENTLY, then combine their results. Use when
    several subtasks don't depend on each other (e.g. research 3 competitors at
    once, or fetch weather + news + calendar in parallel) — cuts latency vs a
    sequential chain.

    Common shape: ParallelAgent (fan-out) nested inside a SequentialAgent whose
    final stage is a "synthesizer" that merges the parallel outputs.

DEPENDENCIES
    pip install google-adk ; GOOGLE_API_KEY in .env

RUN
    my_agent/agent.py exposing `root_agent`; then `adk web` or `adk run my_agent`.
------------------------------------------------------------------------------
"""
from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent

MODEL = "gemini-flash-latest"

# --- Independent workers — each writes to its OWN state key (no collisions) ----
research_a = LlmAgent(
    model=MODEL, name="research_a",
    instruction="Research topic A for the user's request. Summarize key facts.",
    output_key="result_a",
)
research_b = LlmAgent(
    model=MODEL, name="research_b",
    instruction="Research topic B for the user's request. Summarize key facts.",
    output_key="result_b",
)
research_c = LlmAgent(
    model=MODEL, name="research_c",
    instruction="Research topic C for the user's request. Summarize key facts.",
    output_key="result_c",
)

# --- Fan-out: these run concurrently ------------------------------------------
gatherer = ParallelAgent(
    name="parallel_research",
    sub_agents=[research_a, research_b, research_c],
)

# --- Gather: synthesize the three results into one answer ----------------------
synthesizer = LlmAgent(
    model=MODEL, name="synthesizer",
    instruction=(
        "Combine these findings into one coherent, de-duplicated answer.\n\n"
        "A:\n{result_a}\n\nB:\n{result_b}\n\nC:\n{result_c}"
    ),
    output_key="final",
)

# Fan-out then gather.
root_agent = SequentialAgent(
    name="fanout_then_synthesize",
    sub_agents=[gatherer, synthesizer],
)

# ------------------------------------------------------------------------------
# PRODUCTION NOTES
#   * CRITICAL: each parallel worker must write to a DISTINCT output_key.
#     Shared keys create race conditions and lost results.
#   * Parallel workers must be truly independent — no worker should read another
#     worker's output (that's a Sequential dependency, not a Parallel one).
#   * Watch rate limits/quota: N concurrent LLM calls = N simultaneous requests.
#   * Handle partial failure — a synthesizer should tolerate a missing result_x
#     rather than crashing the whole run.
# ------------------------------------------------------------------------------

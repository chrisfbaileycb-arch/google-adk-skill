---
name: google-adk-skill
description: "Build, run, debug, and deploy AI agents with Google's Agent Development Kit (ADK), and wire ADK to external systems via the Model Context Protocol (MCP). Use whenever the user mentions Google ADK, adk.dev, google-adk, LlmAgent, SequentialAgent/ParallelAgent/LoopAgent, McpToolset, exposing ADK tools as an MCP server, running agents locally with `adk web`, or connecting an ADK agent to an MCP connector/server. Covers core primitives, multi-agent orchestration, the two MCP integration patterns (ADK as MCP client and ADK tools exposed as an MCP server), and local development."
license: Apache-2.0
metadata:
  author: chrisfbailey
  version: '1.0'
  source: adk.dev / cloud.google.com
---

# Google ADK Skill Set

Guidance for building AI agents with the **Agent Development Kit (ADK)** — Google's open-source framework for building, debugging, deploying, and evaluating agents at enterprise scale. ADK is available in Python, TypeScript, Go, and Java. This skill focuses on the full workflow plus MCP (Model Context Protocol) integration, so you can simplify agent workflows without hand-wiring every connector.

## When to Use This Skill

Load and apply this skill when the user asks to:

- Build or scaffold an ADK agent (`LlmAgent`, workflow agents, multi-agent teams).
- Add tools, callbacks, sessions, memory, or artifacts to an ADK agent.
- Integrate ADK with MCP — either **consuming** external MCP servers or **exposing** ADK tools as an MCP server.
- Run and debug agents locally with the ADK Dev UI (`adk web`) or CLI (`adk run`).
- Evaluate agents or understand ADK primitives and orchestration options.

## Core Primitives

| Concept | Description |
|---|---|
| `Agent` | Fundamental worker unit. `LlmAgent` uses an LLM for reasoning. Workflow agents (`SequentialAgent`, `ParallelAgent`, `LoopAgent`) are deterministic controllers. |
| `Tool` | Gives agents abilities: call APIs, run code, search, call services. |
| `Callback` | Custom code that runs at specific lifecycle points (logging, checks, modifications). |
| `Session` | Context of a single conversation — history (`Events`) + working memory (`State`). |
| `Memory` | Cross-session recall; long-term context about a user (distinct from Session State). |
| `Artifact` | Files/binary data (images, PDFs) tied to a session or user, managed via `ArtifactService`. |
| `Event` | Basic unit of communication — user message, agent reply, tool use — forming history. |
| `Runner` | Execution engine that orchestrates agent interactions and backend services. |
| `Planning` | Advanced capability (e.g., ReAct planner) for breaking complex goals into steps. |

## Key Capabilities

- **Multi-Agent Systems** — Hierarchical agent teams; LLM-driven delegation or explicit `AgentTool` invocation.
- **Rich Tool Ecosystem** — `FunctionTool`, `AgentTool`, code execution, external APIs/DBs, long-running async tools.
- **Flexible Orchestration** — Workflow agents for predictable pipelines + LLM dynamic routing for adaptive behavior.
- **CLI + Developer UI** — Local dev with `adk web`: inspect events, debug interactions, visualize agents.
- **Native Streaming** — Bidirectional text/audio via the Gemini Live API Toolkit.
- **Built-in Evaluation** — Multi-turn eval datasets, run locally via CLI or dev UI.
- **Broad LLM Support** — Optimized for Gemini; supports others via `BaseLlm`.
- **Extensibility** — Plug in third-party tools, data connectors, and MCP servers.

## Instructions

Follow this order when helping with an ADK task:

1. **Confirm the goal and language.** ADK supports Python, TypeScript, Go, and Java. Examples here are Python (the most complete SDK). Confirm the target before scaffolding.
2. **Install & scaffold.** `pip install google-adk`, then `adk create my_agent`. The generated `agent.py` must define a `root_agent` — the only required element. See `references/local-dev.md`.
3. **Choose an orchestration shape.** Single `LlmAgent` for reasoning tasks; `SequentialAgent`/`ParallelAgent`/`LoopAgent` for deterministic pipelines; multi-agent teams with `AgentTool` for delegation.
4. **Attach tools.** Wrap Python functions with `FunctionTool`, add code execution, or connect external systems. For MCP-based tools, use `McpToolset` (see MCP section below).
5. **Decide the MCP pattern** if MCP is involved — see the two patterns below and `references/mcp-integration.md`.
6. **Run & debug locally** with `adk web` (Dev UI) or `adk run` (CLI). Use `adk web --no-reload` on Windows if you hit subprocess issues.
7. **Evaluate** with multi-turn eval datasets via the CLI or Dev UI before deploying.

## MCP (Model Context Protocol) Integration

MCP is an open standard letting LLMs communicate with external apps, data sources, and tools using a **client-server architecture**: servers expose resources, prompts, and tools; clients consume them. ADK integrates with MCP in two directions.

### Pattern A — ADK Agent as MCP Client (consume external MCP servers)

Use `McpToolset` inside an `LlmAgent` to pull tools from an external MCP server. Supports local stdio servers and remote HTTP servers. Full runnable examples (filesystem stdio server, remote HTTP Maps server, `tool_filter`) are in `references/mcp-integration.md`.

Quick shape:

```python
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

root_agent = LlmAgent(
    model='gemini-flash-latest',
    name='my_agent',
    instruction='Help the user.',
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command='npx',
                    args=["-y", "@modelcontextprotocol/server-filesystem", "/absolute/path/to/folder"],
                )
            ),
            tool_filter=['list_directory', 'read_file']  # optional
        )
    ],
)
```

### Pattern B — Expose ADK Tools as an MCP Server

Wrap ADK tools (e.g., `FunctionTool`) and serve them over MCP so other MCP clients can call them. Full runnable server example is in `references/mcp-integration.md`. Key steps: build the `FunctionTool`, create a `Server`, register `@app.list_tools()` (via `adk_to_mcp_tool_type`) and `@app.call_tool()`, then run over `stdio_server()`.

## Running Locally with `adk web`

```bash
pip install google-adk          # install
adk create my_agent             # scaffold a project (defines root_agent)
cd ./my_agent                   # or the parent dir of your agent package
adk web                         # launch the Dev UI
adk web --no-reload             # Windows fallback for subprocess issues
adk run my_agent                # interactive CLI instead of the UI
```

See `references/local-dev.md` for the required project/file structure and `.env` API-key setup.

## Agent-Pattern Templates

Annotated, runnable, self-contained templates (each with `agent.py` + README + production notes). Copy one, swap the tool, run:

- `patterns/single-llm-agent/` — one LLM agent + tools (leanest; start here).
- `patterns/sequential-pipeline/` — fixed-order stages via shared State (`output_key` → `{key}`).
- `patterns/parallel-fanout/` — concurrent workers + synthesizer (distinct output keys).
- `patterns/loop-agent/` — iterate until good / `max_iterations` (escalate to stop early).
- `patterns/multi-agent-delegation/` — coordinator + specialists via `AgentTool` or `sub_agents` transfer.

Decision guide: one brain → single; known order → sequential; independent + fast → parallel; refine-to-bar → loop; mixed expertise → multi-agent. Default to the leanest that solves it.

## Doctrine

`AGENT_DOCTRINE.md` is a reusable system prompt encoding how to build and run agents (ship real connected systems, automate the whole chain, self-contained files, lean connectors, secure-by-default, bounded cost). Paste it into any agent's `instruction`/system field so it inherits the intent.

## References

- `references/mcp-integration.md` — Complete Pattern A (stdio + remote HTTP client) and Pattern B (ADK-tools-as-MCP-server) code, with notes.
- `references/local-dev.md` — Install, `adk create` scaffold, required file structure, `.env` keys, and run commands.

## Examples

**"Connect my ADK agent to a filesystem MCP server."** → Pattern A with `StdioConnectionParams` and `@modelcontextprotocol/server-filesystem`; optionally add `tool_filter`.

**"Expose my `load_web_page` tool over MCP."** → Pattern B: wrap in `FunctionTool`, register `list_tools`/`call_tool`, run over stdio.

**"Run and debug my agent locally."** → `pip install google-adk`, `adk create`, `cd`, `adk web` (or `adk web --no-reload` on Windows).

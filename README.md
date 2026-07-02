# google-adk-skill

An Agent Skill for building, running, and debugging AI agents with **Google's Agent Development Kit (ADK)** — with first-class **Model Context Protocol (MCP)** integration so you can simplify agent workflows without hand-wiring every connector.

Follows the [agentskills.io](https://agentskills.io) specification: a `SKILL.md` plus bundled `references/`.

## What's inside

| File | Purpose |
|---|---|
| `SKILL.md` | Core skill: ADK primitives, capabilities, orchestration, the two MCP patterns, and local dev. |
| `references/mcp-integration.md` | Full runnable code for **Pattern A** (ADK as MCP client — stdio + remote HTTP) and **Pattern B** (expose ADK tools as an MCP server). |
| `references/local-dev.md` | Install, `adk create` scaffold, required file structure, `.env` keys, and run commands. |

## MCP integration patterns

- **Pattern A — ADK Agent as MCP Client**: consume external MCP servers (local stdio or remote HTTP) via `McpToolset`.
- **Pattern B — Expose ADK Tools as an MCP Server**: serve ADK `FunctionTool`s over MCP so any MCP client can call them.

## Quick start

```bash
pip install google-adk
adk create my_agent
cd ./my_agent
adk web        # Dev UI (use --no-reload on Windows if subprocess issues)
```

## Using this as a skill

Download the packaged skill (zip) and add it via your agent's skill settings, or point your ADK/Claude Code setup at this repo.

## Source

Reference material based on [adk.dev](https://adk.dev) and Google Cloud ADK documentation. Last reviewed: 2026-07-01.

## License

Apache-2.0

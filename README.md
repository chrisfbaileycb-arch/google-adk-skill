# Agent Skills Library — Google ADK

A self-contained, team-ready library for building **real, connected, automated** AI agents with Google's **Agent Development Kit (ADK)** — with first-class **Model Context Protocol (MCP)** integration.

Principle: **every file stands alone.** Purpose, dependencies, runnable code, and connector config live together, so any teammate — or any agent — can pick it up cold and run with it. Operating philosophy is codified in [`AGENT_DOCTRINE.md`](./AGENT_DOCTRINE.md).

---

## 📇 Master Index

### Skill
| Item | Purpose | Platform | Connector | Weight | Status |
|---|---|---|---|---|---|
| [`SKILL.md`](./SKILL.md) | ADK primitives, capabilities, orchestration, MCP patterns, local dev | ADK | native + MCP | — | ✅ Stable |

### Agent-Pattern Templates
| Pattern | Purpose | When to use | Platform | Weight | Status |
|---|---|---|---|---|---|
| [Single LlmAgent](./patterns/single-llm-agent/) | One LLM agent + tools | Simple self-contained task | ADK | 🟢 Leanest | ✅ Stable |
| [Sequential Pipeline](./patterns/sequential-pipeline/) | Fixed-order stages via shared State | Known ordered steps (ETL, draft→revise) | ADK | 🟢 Lean | ✅ Stable |
| [Parallel Fan-out](./patterns/parallel-fanout/) | Concurrent workers + synthesizer | Independent subtasks, latency-sensitive | ADK | 🟡 Medium | ✅ Stable |
| [Loop Agent](./patterns/loop-agent/) | Iterate until good / max iterations | Refine-until-acceptable, quality gates | ADK | 🟡 Medium | ✅ Stable |
| [Multi-Agent Delegation](./patterns/multi-agent-delegation/) | Coordinator + specialists (AgentTool / transfer) | Mixed expertise per subtask | ADK | 🔴 Heavier | ✅ Stable |

### MCP Integration
| Pattern | Purpose | Connector | Reference |
|---|---|---|---|
| A — ADK as MCP **client** | Consume external MCP servers (stdio + remote HTTP) | 🟢 stdio / 🟡 remote HTTP | [mcp-integration.md](./references/mcp-integration.md) |
| B — Expose ADK tools as MCP **server** | Serve your ADK tools to any MCP client | 🟡 server | [mcp-integration.md](./references/mcp-integration.md) |

### Doctrine & Dev
| Item | Purpose |
|---|---|
| [`AGENT_DOCTRINE.md`](./AGENT_DOCTRINE.md) | Reusable system prompt encoding how we build & run agents |
| [`references/local-dev.md`](./references/local-dev.md) | Install, scaffold, file structure, `.env`, run commands |

### Automation — self-updating loop
| Item | Purpose |
|---|---|
| [`automation/`](./automation/) | Weekly ADK release check → draft PR when the real ADK ships an update |
| [`automation/check_adk_updates.py`](./automation/check_adk_updates.py) | Stdlib-only version diff + `gh` draft-PR engine (runs anywhere) |
| [`automation/gemini-spark/`](./automation/gemini-spark/) | Gemini Spark agent + Cloud Function wrapper to run it in Google Cloud |

**Weight legend:** 🟢 leanest overhead · 🟡 moderate · 🔴 heavier (more moving parts / cost). Pick the leanest option that does the job.

---

## 🚀 Quick start

```bash
pip install google-adk
adk create my_agent
# copy a pattern's agent.py into my_agent/, then:
cd ./my_agent
adk web        # Dev UI  (adk web --no-reload on Windows)
```

## 🧭 Choosing a pattern (decision guide)

1. **One task, one brain?** → Single LlmAgent.
2. **Known ordered steps?** → Sequential Pipeline.
3. **Independent steps, want speed?** → Parallel Fan-out.
4. **Refine until it passes a bar?** → Loop Agent.
5. **Different expertise per step?** → Multi-Agent Delegation.
6. **Capability lives in an external server?** → add MCP (Pattern A). **Want others to use your tool?** → expose it (Pattern B).

Default to the lowest number that solves the problem — it's leaner, cheaper, and easier to secure.

## 🗺️ Roadmap
- [x] Weekly self-updating loop (ADK release → draft PR) — see `automation/`
- [ ] Document other platforms (LangChain, OpenAI tools) in the same one-file format
- [ ] Connector comparison scorecard (lean-vs-heavy per task)
- [ ] Deployment + eval templates

## Source
Reference material based on [adk.dev](https://adk.dev) and Google Cloud ADK docs. Last reviewed: 2026-07-01.

## License
Apache-2.0

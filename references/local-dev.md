# Running ADK Locally

## Install

```bash
pip install google-adk
```

Requires Python 3.10 or later. Recommended: use a virtual environment.

```bash
python3 -m venv .venv
source .venv/bin/activate          # macOS / Linux
# .venv\Scripts\activate.bat       # Windows cmd
# .venv\Scripts\Activate.ps1       # Windows PowerShell
```

## Scaffold a project

```bash
adk create my_agent
```

This generates a project whose `agent.py` defines a `root_agent` — the only required element of an ADK agent. You can add tools for the agent to use.

### Required file structure

```
my_agent/           <- parent directory you cd into for `adk web`
└── my_agent/       <- the agent package
    ├── __init__.py
    ├── agent.py    <- defines root_agent
    └── .env        <- API keys / config
```

## API key setup

The default template uses the Gemini API, which needs an API key (create one in Google AI Studio → API Keys). Write it into the agent's `.env`:

```bash
echo 'GOOGLE_API_KEY="YOUR_API_KEY"' > my_agent/.env
```

For Vertex AI backends, configure the corresponding project/location and `GOOGLE_GENAI_USE_VERTEXAI` variables instead.

## Run

```bash
# From the agent's PARENT directory:
cd ./my_agent

# Dev UI — inspect events, debug interactions, visualize agents
adk web

# Windows fallback if you hit subprocess issues
adk web --no-reload

# Interactive command-line interface instead of the UI
adk run my_agent
```

## Evaluate

ADK includes built-in evaluation: define multi-turn eval datasets and run them locally via the CLI or the Dev UI to check agent behavior before deploying.

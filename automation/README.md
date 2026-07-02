# Automation — Weekly ADK Update Loop

Keeps this skill repo in sync with the real Google ADK, automatically. Detects a
new `google-adk` release, summarizes the change, and opens a **draft PR** for you
to review. Two ways to run it — pick one (or run both; they share the same
checker and version file).

## Files
| File | Purpose |
|---|---|
| `check_adk_updates.py` | The engine. Stdlib-only version check + `gh`-based draft PR. Runs anywhere. |
| `adk_version.json` | Single source of truth: the ADK version this repo currently documents. |
| `gemini-spark/spark_agent.md` | Paste-ready Gemini Spark agent (system prompt + tool + schedule). |
| `gemini-spark/cloud_function.py` | HTTP wrapper to deploy the checker to Cloud Run/Functions. |
| `PENDING_UPDATE.md` | Auto-created on the PR branch when an update is found (review checklist). |

## Option A — Pure code path (leanest)
No LLM in the loop. Cloud Scheduler → Cloud Function → checker → draft PR.

```bash
# deploy the function (see cloud_function.py header for full flags)
gcloud functions deploy adk-update-checker --gen2 --runtime=python311 \
  --source=automation/gemini-spark --entry-point=adk_update_http \
  --trigger-http --set-env-vars=GITHUB_REPO=chrisfbaileycb-arch/google-adk-skill

# schedule weekly: Wednesday 02:00 America/Denver
gcloud scheduler jobs create http adk-weekly \
  --schedule="0 2 * * 3" --time-zone="America/Denver" \
  --uri="<FUNCTION_URL>" --http-method=POST
```

## Option B — Gemini Spark agent
Adds reasoning + a written report. Follow `gemini-spark/spark_agent.md`:
1. Paste the system prompt into a new Spark agent.
2. Register `create_update_pr` as a tool pointing at the Cloud Function URL.
3. Schedule the agent weekly (Wed 02:00 Denver) via Cloud Scheduler.

## Local test (safe — no writes, no PR)
```bash
python automation/check_adk_updates.py --dry-run
```

## Secrets
Never in code. Provide `gh` auth (or `GITHUB_TOKEN`) and `GITHUB_REPO` via your
runtime's secret/env manager.

## How the diff works
`check_adk_updates.py` reads the latest **stable** version from
`https://pypi.org/pypi/google-adk/json` and compares it to
`adk_version.json`. Pre-releases (alpha/beta/rc) sort below their GA so they
never trigger a false update. On a real bump it writes `PENDING_UPDATE.md` with a
review checklist and opens the draft PR — you review, update the skill, and merge.

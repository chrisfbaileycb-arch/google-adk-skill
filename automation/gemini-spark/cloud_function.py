"""
Minimal Cloud Function / Cloud Run wrapper for the ADK update checker.
==============================================================================
PURPOSE
    Expose `check_adk_updates.py` as an HTTP endpoint so either:
      (a) Gemini Spark calls it as the `create_update_pr` tool, OR
      (b) Cloud Scheduler hits it directly weekly (no LLM in the loop).

    Either way it re-verifies the version from PyPI and opens a DRAFT PR on a
    real update. Lean by design: stdlib + the repo's own checker.

DEPLOY (Cloud Run functions, Python 3.11+):
    gcloud functions deploy adk-update-checker \
      --gen2 --runtime=python311 --region=us-central1 \
      --source=. --entry-point=adk_update_http \
      --trigger-http --no-allow-unauthenticated \
      --set-env-vars=GITHUB_REPO=chrisfbaileycb-arch/google-adk-skill

REQUIREMENTS
    * The runtime must have a git checkout of the repo and an authenticated
      `gh` CLI (or GITHUB_TOKEN) available — provide via Secret Manager.
    * functions-framework  (for local run / Cloud Functions)

SCHEDULE (weekly, Wed 02:00 Denver):
    gcloud scheduler jobs create http adk-weekly \
      --schedule="0 2 * * 3" --time-zone="America/Denver" \
      --uri="<FUNCTION_URL>" --http-method=POST \
      --oidc-service-account-email=<SA_EMAIL>
==============================================================================
"""
import json
import subprocess
import sys
from pathlib import Path

# Path to the checker in the same repo (adjust if you vendor it elsewhere).
CHECKER = Path(__file__).resolve().parent.parent / "check_adk_updates.py"


def _run_checker(mode: str = "full") -> dict:
    """Run the checker script and capture its result.
    mode='full'         -> may open a draft PR
    mode='notify-only'  -> summary only, no PR
    """
    cmd = [sys.executable, str(CHECKER)]
    if mode == "notify-only":
        cmd.append("--notify-only")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "exit_code": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "update_found": "UPDATE FOUND" in proc.stdout,
    }


# --- Cloud Functions (functions-framework) entry point -----------------------
def adk_update_http(request):
    """HTTP entry point. POST body may include {"mode": "notify-only"}."""
    mode = "full"
    try:
        body = request.get_json(silent=True) or {}
        mode = body.get("mode", "full")
    except Exception:
        pass
    result = _run_checker(mode)
    status = 200 if result["exit_code"] == 0 else 500
    return (json.dumps(result), status, {"Content-Type": "application/json"})


# --- Local test --------------------------------------------------------------
if __name__ == "__main__":
    print(json.dumps(_run_checker("notify-only"), indent=2))

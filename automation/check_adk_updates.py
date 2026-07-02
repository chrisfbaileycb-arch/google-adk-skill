#!/usr/bin/env python3
"""
Weekly ADK Update Checker
==============================================================================
PURPOSE
    Detect when a new Google ADK (google-adk) release ships, compare it to the
    version this repo's skill currently documents, and — on a real update —
    (1) print a change summary and (2) open a DRAFT pull request proposing the
    skill bump. Portable: runs in Gemini Spark, Cloud Functions/Run, or cron.

DESIGN (doctrine: self-contained, lean, secure, automate the whole chain)
    * No heavy deps for the check itself — uses only the Python stdlib for the
      PyPI version lookup, so it runs anywhere with zero install.
    * The GitHub PR step shells out to the `gh` CLI (already how this repo is
      managed) — no extra SDK, no hardcoded tokens.
    * State lives in one place: VERSION_FILE. That single file is the contract
      between "what we document" and "what's live."

CANONICAL SOURCES
    * PyPI stable version : https://pypi.org/pypi/google-adk/json  (field: info.version)
    * Release notes / diff: https://github.com/google/adk-python/releases
    * Changelog           : https://github.com/google/adk-python/blob/main/CHANGELOG.md
    * Docs release notes   : https://adk.dev/release-notes/

USAGE
    python check_adk_updates.py                 # check + (if update) open draft PR
    python check_adk_updates.py --dry-run       # check + summarize, NO PR, NO writes
    python check_adk_updates.py --notify-only   # check + summarize only

ENV
    GITHUB_REPO   e.g. "chrisfbaileycb-arch/google-adk-skill" (for the PR)
    (gh CLI must be authenticated in the environment; do NOT hardcode tokens.)
==============================================================================
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

PYPI_JSON = "https://pypi.org/pypi/google-adk/json"
RELEASES_URL = "https://github.com/google/adk-python/releases"
CHANGELOG_URL = "https://github.com/google/adk-python/blob/main/CHANGELOG.md"
DOCS_NOTES_URL = "https://adk.dev/release-notes/"

# The single source of truth for "what version this repo documents".
REPO_ROOT = Path(__file__).resolve().parent.parent
VERSION_FILE = REPO_ROOT / "automation" / "adk_version.json"


# --- helpers -----------------------------------------------------------------
def parse_version(v: str) -> tuple:
    """Turn '2.3.0' or '2.0.0-alpha.1' into a sortable tuple. Pre-releases sort
    BELOW their final release so an alpha never looks newer than the GA."""
    core, _, pre = v.strip().lstrip("v").partition("-")
    nums = []
    for part in core.split("."):
        nums.append(int(part) if part.isdigit() else 0)
    while len(nums) < 3:
        nums.append(0)
    # (major, minor, patch, is_final, pre_string) — final(1) > pre(0)
    return (nums[0], nums[1], nums[2], 0 if pre else 1, pre)


def fetch_latest_pypi_version() -> str:
    """Latest STABLE version from PyPI. stdlib only — runs anywhere."""
    req = urllib.request.Request(PYPI_JSON, headers={"User-Agent": "adk-update-checker"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["info"]["version"]


def load_documented_version() -> str:
    if VERSION_FILE.exists():
        return json.loads(VERSION_FILE.read_text()).get("documented_version", "0.0.0")
    return "0.0.0"


def save_documented_version(version: str) -> None:
    VERSION_FILE.write_text(json.dumps({
        "documented_version": version,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "source": PYPI_JSON,
    }, indent=2) + "\n")


def build_summary(old: str, new: str) -> str:
    return (
        f"ADK update detected: {old} -> {new}\n\n"
        f"- Release notes: {RELEASES_URL}\n"
        f"- Changelog:     {CHANGELOG_URL}\n"
        f"- Docs notes:    {DOCS_NOTES_URL}\n\n"
        "Review the release for breaking changes (esp. major bumps), new "
        "primitives, and MCP/toolset API changes, then update SKILL.md, the "
        "pattern templates, and references/ as needed."
    )


def open_draft_pr(old: str, new: str, summary: str) -> None:
    """Open a DRAFT PR bumping the documented version. Uses gh CLI (no tokens
    in code). Creates a branch, commits the version bump + a TODO note, pushes,
    and opens the PR as a draft so a human reviews before merge."""
    repo = os.environ.get("GITHUB_REPO", "").strip()
    branch = f"adk-update-{new}"
    os.chdir(REPO_ROOT)

    subprocess.run(["git", "checkout", "-B", branch], check=True)
    save_documented_version(new)

    todo = REPO_ROOT / "automation" / "PENDING_UPDATE.md"
    todo.write_text(
        f"# Pending ADK update: {old} -> {new}\n\n{summary}\n\n"
        "## Checklist\n"
        "- [ ] Review release notes for breaking changes\n"
        "- [ ] Update SKILL.md primitives/capabilities/MCP if APIs changed\n"
        "- [ ] Update pattern templates (patterns/*/agent.py)\n"
        "- [ ] Update references/ code snippets\n"
        "- [ ] Bump 'Last reviewed' dates\n"
    )

    subprocess.run(["git", "add", "-A"], check=True)
    subprocess.run(
        ["git", "commit", "-m", f"chore: flag ADK update {old} -> {new} for skill review"],
        check=True,
    )
    subprocess.run(["git", "push", "-u", "origin", branch, "--force"], check=True)

    pr_cmd = [
        "gh", "pr", "create", "--draft",
        "--title", f"ADK update {old} -> {new}: review & update skill",
        "--body", summary,
        "--head", branch,
    ]
    if repo:
        pr_cmd += ["--repo", repo]
    subprocess.run(pr_cmd, check=True)


# --- main --------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description="Weekly ADK update checker")
    ap.add_argument("--dry-run", action="store_true", help="Check only; no writes, no PR")
    ap.add_argument("--notify-only", action="store_true", help="Check + summarize; no PR")
    args = ap.parse_args()

    try:
        latest = fetch_latest_pypi_version()
    except Exception as e:
        print(f"[error] could not fetch latest ADK version: {e}", file=sys.stderr)
        return 2  # non-zero so the scheduler can alert on repeated failures

    documented = load_documented_version()
    print(f"[info] documented={documented}  latest={latest}")

    if parse_version(latest) <= parse_version(documented):
        print("[ok] No new ADK release. Nothing to do.")
        return 0

    summary = build_summary(documented, latest)
    print("\n===== UPDATE FOUND =====\n" + summary)

    if args.dry_run or args.notify_only:
        print("\n[notify-only] Skipping PR creation.")
        return 0

    try:
        open_draft_pr(documented, latest, summary)
        print(f"\n[done] Draft PR opened for {documented} -> {latest}.")
    except subprocess.CalledProcessError as e:
        print(f"[error] PR step failed: {e}", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

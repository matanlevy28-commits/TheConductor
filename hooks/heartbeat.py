#!/usr/bin/env python3
"""
project-conductor — Heartbeat hook
Wired via PostToolUse hook (opt-in). Writes/updates `.conductor/heartbeat.json`
in the current working directory's nearest `.conductor/` ancestor (or cwd if none).

Purpose:
- When the conductor is running as a backgrounded subagent, parent agents
  cannot see its progress. This file gives them a cheap, file-based status
  source — no need to spawn a second conductor instance to query state.
- The heartbeat file is the protocol described in project-conductor.md
  ("Heartbeat for Background Mode" section, NEW in v4).

Privacy & security:
- PURELY LOCAL — no network calls.
- Reads NO secrets, NO .env, NO ssh keys.
- Writes only to `.conductor/heartbeat.json` (timestamps and tool names).
- Idempotent — safe to run on every PostToolUse event.
"""

import json
import sys
import os
import datetime
from pathlib import Path


def find_conductor_dir():
    """Walk up from cwd looking for nearest .conductor/. Fallback: create in cwd."""
    cwd = Path.cwd()
    for candidate in [cwd] + list(cwd.parents):
        cd = candidate / ".conductor"
        if cd.exists() and cd.is_dir():
            return cd
    # Fallback: create in cwd
    cd = cwd / ".conductor"
    cd.mkdir(parents=True, exist_ok=True)
    return cd


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        data = {}

    tool = data.get("tool_name", "")
    tool_response = data.get("tool_response")
    success = True
    if isinstance(tool_response, dict):
        success = not tool_response.get("is_error", False)

    conductor_dir = find_conductor_dir()
    hb_path = conductor_dir / "heartbeat.json"

    # Read existing heartbeat (to track call counter and last-progress-signal)
    existing = {}
    if hb_path.exists():
        try:
            existing = json.loads(hb_path.read_text(encoding="utf-8"))
        except Exception:
            existing = {}

    counter = int(existing.get("tool_calls_since_last_heartbeat", 0)) + 1
    last_progress_signal = existing.get("last_progress_signal", "")
    if tool in ("Write", "Edit", "NotebookEdit", "TaskCreate", "TaskUpdate"):
        last_progress_signal = f"{tool} at {datetime.datetime.now().isoformat()}"
        counter = 0  # forward progress observed; reset stuck-counter

    # stuck_check heuristic: based on time since last forward-progress signal
    last_progress_ts = None
    if last_progress_signal and " at " in last_progress_signal:
        try:
            last_progress_ts = datetime.datetime.fromisoformat(last_progress_signal.split(" at ")[-1])
        except Exception:
            last_progress_ts = None
    now = datetime.datetime.now()
    if last_progress_ts is None:
        stuck_check = "unknown"
    elif (now - last_progress_ts).total_seconds() > 300:  # 5 min
        stuck_check = "stuck"
    elif (now - last_progress_ts).total_seconds() > 120:  # 2 min
        stuck_check = "slowing"
    else:
        stuck_check = "ok"

    heartbeat = {
        "ts": now.isoformat(),
        "last_action": f"{tool}{'' if success else ' (FAILED)'}",
        "last_progress_signal": last_progress_signal,
        "tool_calls_since_last_progress": counter,
        "stuck_check": stuck_check,
        "session_id": data.get("session_id", existing.get("session_id", "")),
    }

    # Preserve phase/task if previously set by the conductor itself
    for k in ("phase", "phase_name", "task", "task_index", "task_total"):
        if k in existing:
            heartbeat[k] = existing[k]

    hb_path.write_text(json.dumps(heartbeat, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

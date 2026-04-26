#!/usr/bin/env python3
"""
Agent Monitor — Logger
Appends structured events to activity.jsonl for every tool call.
Wired via PreToolUse, PostToolUse, and SessionStart hooks.

This script is path-agnostic — it stores its log next to itself, so you can
copy the entire `agent-monitor/` directory into any project's `.claude/`
subdirectory without editing paths.

Privacy: all data stays local. Nothing leaves your machine.
"""

import json
import sys
import os
import datetime

LOG_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(LOG_DIR, "activity.jsonl")


def extract_summary(tool: str, tool_input: dict) -> dict:
    if tool == "Bash":
        return {"cmd": str(tool_input.get("command", ""))[:600]}
    if tool in ("Write", "Edit", "Read", "NotebookEdit"):
        s = {"file": tool_input.get("file_path", "")}
        if tool == "Write":
            s["bytes"] = len(str(tool_input.get("content", "")))
        elif tool == "Edit":
            s["old_preview"] = str(tool_input.get("old_string", ""))[:120]
            s["new_preview"] = str(tool_input.get("new_string", ""))[:120]
        return s
    if tool == "Agent":
        return {
            "description": tool_input.get("description", ""),
            "subagent_type": tool_input.get("subagent_type", "general-purpose"),
            "background": tool_input.get("run_in_background", False),
            "prompt_preview": str(tool_input.get("prompt", ""))[:300],
        }
    if tool == "WebSearch":
        return {"query": tool_input.get("query", "")}
    if tool == "WebFetch":
        return {"url": tool_input.get("url", "")}
    if tool == "Glob":
        return {"pattern": tool_input.get("pattern", ""), "path": tool_input.get("path", "")}
    if tool == "Grep":
        return {"pattern": tool_input.get("pattern", ""), "path": tool_input.get("path", "")}
    if tool == "Skill":
        return {"skill": tool_input.get("skill", ""), "args": tool_input.get("args", "")}
    if tool == "TaskCreate":
        return {"subject": tool_input.get("subject", ""), "description": str(tool_input.get("description", ""))[:200]}
    if tool == "ScheduleWakeup":
        return {"delaySeconds": tool_input.get("delaySeconds"), "reason": tool_input.get("reason", "")}
    return {k: str(v)[:150] for k, v in list(tool_input.items())[:5]}


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        data = {}

    tool = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})
    tool_response = data.get("tool_response")

    if tool:
        event_type = "post_tool" if tool_response is not None else "pre_tool"
        entry = {
            "ts": datetime.datetime.now().isoformat(),
            "event": event_type,
            "tool": tool,
            **extract_summary(tool, tool_input),
        }
        if tool_response is not None:
            if isinstance(tool_response, dict):
                entry["success"] = not tool_response.get("is_error", False)
                if tool_response.get("is_error"):
                    entry["error"] = str(tool_response.get("content", ""))[:300]
            else:
                entry["success"] = True
    else:
        entry = {
            "ts": datetime.datetime.now().isoformat(),
            "event": "session_start",
            "session_id": data.get("session_id", ""),
        }

    os.makedirs(LOG_DIR, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()

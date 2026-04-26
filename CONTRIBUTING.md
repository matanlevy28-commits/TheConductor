# Contributing to Project Conductor

Thank you for your interest. Contributions are welcome.

## What's worth contributing

The most valuable contributions are:
- **Real failure modes** you encountered while running the conductor — what condition triggered it, what actually happened vs. what should have happened
- **Environment compatibility** — gaps where the conductor assumed something about Claude Code that didn't hold in your version/config
- **Routing improvements** — cases where tasks were routed to the wrong subagent and how you fixed it
- **New hard stop conditions** — situations that should have been a hard stop but weren't
- **New anti-pattern detectors** for `agent-monitor/reporter.py` — if you spot a behavior the auto-detection misses (NEW in v4)

Less valuable: cosmetic changes, speculative features, or additions that increase complexity without addressing a real failure mode.

## Sharing your monitor reports (UPDATED in v4.0.1)

If you've installed the optional `agent-monitor/` bundle, every Claude Code session ends with a markdown report at `.claude/agent-monitor/reports/report_<ts>.md`. The bottom of each report includes an opt-in share-footer with:

- A GitHub issue URL template
- **A 5-field contribution template** that takes ~2 minutes to fill in

**Why the template matters:** the auto-detector flags patterns based on hardcoded heuristics (probe sprawl ≥3 files, busy-wait ≥2 occurrences, etc.). It cannot judge whether a flagged pattern was bad-in-context — that requires knowing what the user was trying to do and whether the agent succeeded. The template captures that context so maintainers can act on the report.

**The 5 fields the template asks for:**

1. **What you were trying to do** (1-2 sentences)
2. **Did the agent succeed?** (yes / partially / no, with brief explanation)
3. **Which flagged patterns were bad-in-context vs neutral vs false-positive** (one line each)
4. **What should the agent have done instead?** (optional but high-value)
5. **Anything the auto-detector missed** (optional)

Then paste the raw report below the template (after redacting paths/secrets).

**What makes a useful monitor report contribution:**

1. **A pattern the auto-detector caught and you confirm was bad** (with goal context — "I was trying to X, the agent did Y instead, the detector caught it"). This validates existing detector thresholds.
2. **A pattern the auto-detector MISSED that you noticed manually.** Example: "Agent kept dispatching the same subagent with slightly-different prompts — 5 times in a row before I intervened. Detector didn't catch this. Suggesting a new detector: 'subagent-thrash' = ≥3 Agent dispatches with same `subagent_type` and >70% prompt similarity."
3. **A false-positive** — the detector flagged something that wasn't actually a problem in your context. Helps tune thresholds.
4. **A regression vs prior conductor version.** Example: "v4 added per-resource discovery, but in my session it triggered on a single-resource task and added overhead. Suggest: skip per-resource discovery rule when only 1 external resource detected."

**Before pasting, redact:**
- Absolute file paths (`/Users/.../`, `/home/.../`, project-identifying directory names)
- Environment-specific URLs (internal hostnames, API endpoints with credentials)
- Any tokens, keys, or passwords accidentally captured in bash output
- Drop project-identifying names if confidential

The share-footer is opt-in. The maintainers don't see your reports unless you choose to share them. **No automatic telemetry exists.**

## How to contribute

1. **Fork the repo** and create a branch from `main`
2. **Make your change** in `project-conductor.md`
3. **Test it** — run the conductor on at least one real project with your change
4. **Describe the failure mode** your change addresses (or the gap it fills) in the PR description
5. **Reference evidence** — paste the status.md output or final report section that demonstrates the problem

## PR description format

```
## What this fixes / adds

[One paragraph: the specific failure mode or gap]

## Evidence

[Paste from .conductor/status.md, FINAL_REPORT.md, or a run transcript]

## How it's tested

[Which spec/project you ran it against, outcome]
```

## Versioning

Project Conductor uses [Semantic Versioning](https://semver.org/):

- **PATCH** (1.0.x) — bug fixes to existing mechanisms, no behavior changes
- **MINOR** (1.x.0) — new safety mechanisms, new governance rules, new outputs
- **MAJOR** (x.0.0) — changes to the three prime directives, the phase structure, or the hard stop hierarchy

## What NOT to contribute

- Changes that reduce safety (removing checkpoints, relaxing hard stops, enabling auto-Opus escalation)
- Hardcoded tool assumptions — the conductor must adapt to what's available
- Line-level implementation detail in status/progress files — those are operator outputs, not documentation
- Speculative features without a real failure mode behind them

## Questions

Open an issue. Describe the run that produced the unexpected behavior and attach the `.conductor/` directory contents if possible.

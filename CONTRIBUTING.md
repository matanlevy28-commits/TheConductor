# Contributing to Project Conductor

Thank you for your interest. Contributions are welcome.

## What's worth contributing

The most valuable contributions are:
- **Real failure modes** you encountered while running the conductor — what condition triggered it, what actually happened vs. what should have happened
- **Environment compatibility** — gaps where the conductor assumed something about Claude Code that didn't hold in your version/config
- **Routing improvements** — cases where tasks were routed to the wrong subagent and how you fixed it
- **New hard stop conditions** — situations that should have been a hard stop but weren't

Less valuable: cosmetic changes, speculative features, or additions that increase complexity without addressing a real failure mode.

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

# Changelog

All notable changes to Project Conductor are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.0.0] — 2026-04-25

Initial public release.

### Core capabilities
- Autonomous end-to-end project execution from a spec file
- Lazy two-tier environment discovery (subagents, skills, MCPs, CLIs, plugins)
- Dynamic task routing — discovers actual tools available, never hardcodes
- Continuous execution across all phases with configurable interruption model
- Reality verification on every task completion (never trusts reports)
- Session resumption from `.conductor/` state

### Safety mechanisms
- **Turn checkpoint** (every 25 turns) — deterministic pause-and-confirm, independent of token estimation
- **Spec enrichment review gate** — mandatory user approval before Phase 2 begins; no silent enrichment-then-build
- **Canary model check** — heuristic detection of Task tool model parameter being ignored (GitHub issue #18873)
- **Lock enforcement** — post-dispatch `git diff --name-only` verification that subagents honored declared file boundaries
- **Permissions sanity test** — canary command before writing `.claude/settings.json` to catch broken permission syntax
- **Budget enforcement** — soft stop at 70%, hard stop at 95% of session token budget

### Governance
- Hard stop hierarchy (15 conditions, in priority order)
- No automatic Opus escalation — user must explicitly authorize premium retries
- Self-check system with cap (12/session) and distribution enforcement
- Concurrency locks with conflict resolution (write-write, read-write, read-read)
- Credentials detection with guided acquisition flow

### Outputs
- Live `status.md` — always current, queryable mid-execution
- `FINAL_REPORT.md` — plan-vs-actual, routing notes, v3 mechanism outcomes
- Surgical debug map — feature → files/commits/decisions/limitations index

### Integration
- Works with Superpowers plugin (brainstorming, TDD, planning, code review)
- Adaptive behavior for small (<20), medium (20-80), and large (80+) agent libraries
- Project-aware CLI detection — only scans for CLIs the project actually needs

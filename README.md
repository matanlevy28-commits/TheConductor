# Project Conductor

> An autonomous, end-to-end project execution manager for Claude Code.

Project Conductor takes a spec file and runs your entire build — from environment discovery through final delivery — with minimal interruptions. It discovers what tools are actually available in your environment, routes tasks to the right subagents, enforces budgets, and produces a final report with a surgical debug map.

## What it does

You hand it a spec. It builds your project.

```
Use project-conductor to build from [your-spec.md]
```

It will:
1. **Discover** your environment (subagents, skills, MCPs, CLIs, plugins)
2. **Analyze** your spec and enrich it with execution metadata
3. **Route** each task to the best available tool — dynamically, not hardcoded
4. **Execute** all phases continuously, stopping only for true blockers
5. **Verify** every completion claim before marking tasks done
6. **Deliver** a final report with plan-vs-actual and a debug map

## Key design principles

**Reality over reports.** Never trusts completion claims. Runs the tests, reads the files, checks the commits.

**Adaptation over assumption.** Discovers what's actually installed before routing. Agent libraries vary wildly between users.

**Transparency over silence.** Maintains a live `status.md` file — you can ask "status" at any point and get an immediate, accurate answer.

## Safety mechanisms

Project Conductor v3 is hardened against autonomous-agent failure modes:

| Mechanism | What it prevents |
|-----------|-----------------|
| **Turn checkpoint** (every 25 turns) | Silent token burn past budget |
| **Spec enrichment review gate** | Building against conductor's interpretation, not yours |
| **Canary model check** | Paying Opus rates when you requested Haiku |
| **Lock enforcement** (via `git diff`) | Parallel tasks overwriting each other's files |
| **Permissions sanity test** | Settings that look active but silently don't apply |

## Installation

### Global install (recommended)

```bash
cp project-conductor.md ~/.claude/agents/project-conductor/agent.md
```

### Project-level install

```bash
mkdir -p .claude/agents/project-conductor
cp project-conductor.md .claude/agents/project-conductor/agent.md
```

## Usage

```
Use project-conductor to build from spec.md
```

That's it. The conductor handles the rest.

### Status check (anytime during execution)

```
status
```

### Mid-run controls

| Command | Effect |
|---------|--------|
| `status` | Show current phase, task, budget |
| `show progress` | Phase-level summary |
| `proceed` | Continue after a checkpoint |
| `permissions yes` | Accept permissions offer |
| `approve enrichments` | Approve spec additions (required before Phase 2) |

## Configuration

The conductor's own model is set in the frontmatter of `project-conductor-v3.md`:

```yaml
---
model: opus      # opus (best orchestration) or sonnet (5x cheaper, good for prototypes)
effort: medium   # medium recommended; high not worth the cost for orchestration
---
```

This controls the **orchestration quality**, not the tasks themselves. Tasks are dispatched to subagents with their own models.

See the header comment in `project-conductor.md` for the full decision guide.

## Permissions offer

On first run, the conductor offers to set up permission rules so it can run `npm test`, `git status`, etc. without prompting you on every command. You choose:

- **A** — write to `.claude/settings.json` (shared if committed)
- **B** — write to `.claude/settings.local.json` (personal, gitignored)
- **C** — merge with existing settings

It will **never auto-allow** `git push`, destructive git ops, `rm -rf`, production deploys, or `.env*` writes.

## State files

All conductor state lives in `<project>/.conductor/`:

```
.conductor/
  plan.md                    — task list with statuses
  status.md                  — live status (update on every task change)
  progress.md                — chronological log
  budget.md                  — token usage tracking
  decisions.md               — choices with rationale
  deviations.md              — in-scope fixes and lock violations
  findings.md                — emergent issues classified
  checkpoint-N.md            — turn checkpoints (every 25 turns)
  spec-enrichment.diff       — diff of original vs enriched spec
  spec-enrichment-summary.md — categorized enrichment review
  locks/                     — active task locks
  evidence/                  — artifacts by phase
  FINAL_REPORT.md            — post-execution delivery report
```

## Session resumption

If a session ends mid-build, just start a new one in the same project directory. The conductor reads `.conductor/` state, cleans stale locks, verifies file state matches its claims, and continues from where it left off.

## Final report

Every completed run produces `.conductor/FINAL_REPORT.md` with:

- Plan vs. actual (per phase)
- Token budget used
- All deviations logged
- v3 safety mechanism outcomes
- **Surgical debug map** — for every major feature: files, commits, subagent used, key decisions, known limitations

The debug map format is designed to be quoted back to Claude:

> "Bug in [feature]. Per debug map: phase [P.T], files [list], commit [SHA]. Fix surgically without touching unrelated code."

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT

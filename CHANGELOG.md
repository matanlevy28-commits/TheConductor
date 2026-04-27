# Changelog

All notable changes to Project Conductor are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

> **Note on version numbers:** the public release version (1.0.0 → 4.0.0) is aligned with the internal agent-prompt narrative version (v3 → v4) starting with this release. v4.0.0 jumps the public number forward to match.

---

## [4.1.1] — 2026-04-27

Hardens the gate between Phase 0 (environment scan) and Phase 1+ (build). Closes a real-world failure mode in which the conductor — running with `⏵⏵ accept edits on` — walked past the Permissions Offer and Optional Bundles Offer and went straight into writing source files. The user never saw the offers because per-edit prompts were suppressed by accept-edits mode, and the agent's own prompt had no enforced stop.

### Changed

- **Phase 0 is now strictly READ-ONLY.** Explicit allowlist of inspection-only Bash (`ls`, `cat`, `command -v`, `--version`, `test -f/-d`, `wc -l`, `grep`, import probes, `openpyxl.load_workbook(..., data_only=True)` reads of an existing input file, and `mkdir -p .conductor/{locks,evidence}`). No `Write` / `Edit` outside `.conductor/`, no source-dir `mkdir`, no target-site network probes.
- **First Response is a HARD GATE.** No `Write` / `Edit` / tree-mutating Bash and no `Task` dispatches until the user replies `proceed`. `accept-edits` mode explicitly does NOT authorize skipping the gate.
- **Gate violations are classified as hard-stop class events.** Logged to `.conductor/decisions.md` and surfaced to the user.

### Why

v4.0 *described* the First Response structure (permissions offer, bundles offer, "reply 'proceed' to begin") but did not *enforce* the gate between Phase 0 (scan) and Phase 1+ (build). In real runs with `⏵⏵ accept edits on` active, the conductor walked past the offers and went straight into writing source files — the user never saw the offers because the natural per-edit prompts were suppressed by accept-edits mode, and the agent's own prompt had no hard stop.

### Not changed

- v4.0 behavioral rules (Investigation Budget, Anti-Premature-Failure, Hard Stops, etc.) all unchanged
- v4.1.0 install flow (`install.sh`, flat-file destination, path substitution) unchanged
- Bundle code (no changes to `agent-monitor/` or `hooks/`)

---

## [4.1.0] — 2026-04-27

Adds an `install.sh` script and consolidates the install path. Previously the README walked users through `git clone` + `mkdir` + `cp`, and the agent's bundle install offer asked users to type the source repo path on every invocation. Both problems were caused by the agent having no anchor to its source repo. v4.1.0 fixes that with an installer that bakes the real path in at install time.

### Added

- **`install.sh`** — single-command installer. Detects the cloned repo's location (works wherever you cloned it: `~/TheConductor`, `~/Code/TheConductor`, `/opt/TheConductor`, etc.), patches `project-conductor.md` so every `/path/to/TheConductor` placeholder is replaced with the real absolute path, and copies the patched file to `~/.claude/agents/project-conductor.md`. Supports macOS / Linux / Windows Git Bash / WSL.
- **`--force` flag** for `install.sh` — skips the overwrite prompt for scripted update flows (`git -C <path> pull && <path>/install.sh --force`).
- **Idempotency** — re-running `install.sh` on an unchanged install is a silent no-op (uses `cmp -s` to compare the patched temp file against the deployed file before prompting).

### Changed

- **Install destination changed from `~/.claude/agents/project-conductor/agent.md` (subdirectory + `agent.md`) to `~/.claude/agents/project-conductor.md` (flat file).** Both forms work in Claude Code. The flat form matches community convention (e.g., the `msitarzewski/agency-agents` repo) and removes one layer of nesting. Existing users updating from a previous version should run `rm -rf ~/.claude/agents/project-conductor` after running the new installer (see Migration below).
- **Standardized the placeholder in `project-conductor.md`** — all 5 occurrences of `/path/to/repo` (lines 519, 522, 523, 529, 530) renamed to `/path/to/TheConductor` to match the 4 existing `/path/to/TheConductor` occurrences in the same file. After `install.sh` runs, all 9 placeholders are substituted with the user's real repo path. The agent's bundle install offer now shows the real path the user can copy-paste, not a placeholder.
- **README install section simplified** — replaced the manual `git clone` + `mkdir` + `cp` sequence (and a separate "project-level install" section) with a single `git clone` + `./install.sh` flow. Update is now a one-liner: `git -C <path> pull && <path>/install.sh`. The project-level install pattern is no longer documented (was rarely used; manual `cp` still works for advanced users who need it).
- **README "Optional monitoring" + "Optional hooks" sections collapsed into one "Optional bundles" section** — manual `cp -r` install instructions removed. Users are pointed to the runtime offer (which now knows the source path) and to `agent-monitor/README.md` / `hooks/README.md` for advanced manual install.

### Why

Two problems with the v4.0.2 install flow:

1. **The agent had no anchor to its source repo.** When it offered bundle install (`install bundles N,M from /path/to/repo`), the user had to type the source path manually every time — because the deployed agent file in `~/.claude/agents/` had no way to know where the cloned repo lived. With v4.1.0's `install.sh`, the path is substituted into the deployed file at install time, so the offer shows the real path on the user's machine.
2. **Multi-step manual install was error-prone.** `git pull` succeeded silently when the follow-up `cp` was forgotten, leaving users on stale agent code while thinking they had updated. `install.sh` is one command for both initial install and updates.

### Migration

If you've installed any version before v4.1.0:

```bash
# 1. Remove the old subdirectory-form install
rm -rf ~/.claude/agents/project-conductor

# 2. Pull the new repo state
git -C <wherever-you-cloned> pull

# 3. Run the new installer
<wherever-you-cloned>/install.sh
```

After this, the agent lives at `~/.claude/agents/project-conductor.md` (flat file), and the bundle install offer will show your real repo path instead of a placeholder.

### Not changed

- Agent prompt's behavioral rules (Investigation Budget, Anti-Premature-Failure, Hard Stops, etc., all unchanged from v4.0.2)
- Bundle code (no changes to `agent-monitor/` or `hooks/` scripts in this release)
- `bundles_already_handled` opt-out flag (still works the same way)
- Detector thresholds (unchanged)
- Privacy posture (still 100% local, opt-in, no telemetry)

---

## [4.0.2] — 2026-04-26

Surfaces the optional bundles in the conductor's first response so users discover them without reading the README. Without this, new users had no in-flow signal that `agent-monitor/` and `hooks/` exist — they only ride along if explicitly cp'd from the source repo.

### Added

- **First-response "Optional bundles offer" section** — appears after the existing Permissions setup offer. Surfaces the three bundles with one short paragraph each:
  1. `agent-monitor/` — session reports with auto-detected anti-patterns
  2. `hooks/heartbeat.py` — background-mode status visibility
  3. `hooks/usage_limit_wakeup.py` — auto-resume after API rate/usage limits
- **"Optional Bundles Offer" procedure section** in `project-conductor.md` — full install handling: source-path verification, file copy, settings.json hook block + permission entries draft, sanity-test before activation (mirrors the v3 Permissions Offer posture).
- **Mid-run install controls** — users can install bundles mid-session with `install bundles 1,2,3 from /path/to/TheConductor` or decline with `skip bundles`.
- **`bundles_already_handled: true`** opt-out flag in `.conductor/config.json` for users who don't want the offer to appear (e.g., project-level pre-decision).

### Why

v4.0.0 introduced the bundles but they require manual `cp -r` + manual `settings.json` editing. Most new users don't read the README first, so most users never discovered the bundles existed. v4.0.2 makes discovery part of the standard Phase 0 flow — same posture as the permissions offer (surface, ask, respect the answer, don't re-ask).

### Not changed

- Bundle code (no changes to `agent-monitor/` or `hooks/` scripts in this release)
- Bundle install posture (still opt-in, still local-only, no telemetry)
- Agent prompt's behavioral rules (Investigation Budget, Anti-Premature-Failure, etc., all unchanged from v4.0.0)
- Detector thresholds (unchanged from v4.0.1)

---

## [4.0.1] — 2026-04-26

Improves the monitor-report → maintainer feedback loop. v4.0.0's share-footer just said "paste this report" — maintainers received tool-call dumps without context on what the user wanted or whether the patterns were bad-in-context. v4.0.1 adds a structured contribution template.

### Changed

- **`agent-monitor/reporter.py` — `share_footer()` now emits a 5-field contribution template** (What I was trying to do / Did the agent succeed / Which patterns were BAD vs NEUTRAL vs FALSE-POSITIVE / What should it have done / Anything else). Users fill the template before pasting the raw report. Takes ~2 minutes; makes the difference between an actionable report and a tool-call dump.
- **`CONTRIBUTING.md` — "Sharing your monitor reports" section updated** to explain the template, why each field matters, and what makes a useful report.

### Why

The auto-detector is static (regex + thresholds). It cannot judge whether a flagged pattern was bad-in-context — that requires knowing the user's goal. Without that context, contributed reports are observations, not actionables. The structured template captures the missing context cheaply.

### Not changed

- Detector thresholds and patterns (no detector logic changes in this release)
- Privacy posture (still 100% local, opt-in, no telemetry)
- Agent prompt (`project-conductor.md` unchanged in this release)

---

## [4.0.0] — 2026-04-26

Behavior-shift release derived from real-world test sessions. v3 was over-cautious; v4 is biased toward iterating before asking, discovering before declaring impossible, and notifying without blocking. Twelve discrete process failures observed in v3 → addressed in v4.

### Breaking changes

- **Hard Stop semantics reclassified.** "Site needs Playwright instead of `requests`" is now explicitly NOT a Hard Stop — it's implementation iteration. An architectural decision is one that affects MULTIPLE components OR introduces a NEW SYSTEM-LEVEL dependency (database, message queue, deployment target, auth provider). Adjusting one component's transport/parsing technique is implementation-level. See "Hard Stops" section in `project-conductor.md`.
- **Turn-25 checkpoint demoted from mandatory pause to informational notification.** v3 required explicit user confirmation at every 25-turn boundary; this caused unnecessary interruption and never caught a real problem in testing. v4 surfaces a one-line notification and continues. Opt into `--strict-mode` (or `strict_checkpoints: true` in `.conductor/config.json`) for v3 behavior.
- **Budget thresholds (70%/95%) demoted from blocking to notification (the "Notify, Don't Block" rule).** Work continues past notification — user is informed, not stopped. Anti-shrinkage clause: deliver partial output and continue, do not auto-shrink scope.
- **Removed from Hard Stops:** budget threshold, turn checkpoint, self-check counter exhaustion. These are now notifications/logs, not stops.
- **Public version number jumped 1.x → 4.x** to align with internal agent-prompt versioning narrative (v3 → v4). Future releases will increment normally.

### New

- **Investigation Budget** rule (max 3 throwaway research artifacts before MUST commit to a draft implementation; max 5 ever per task)
- **Per-resource Discovery** rule (when ≥2 peer external resources involved, each gets independent discovery — no blanket-applying)
- **Anti-Premature-Failure** rule (≥3 distinct approaches before declaring impossible; phrase "KNOWN LIMITATION" BANNED in shipped code)
- **Status from State, not Estimation** rule (status responses MUST come from a state file, log, or directly-observed signal — never elapsed-time estimation)
- **Forbidden Bash Patterns** section (`until ... ; do sleep N; done` busy-wait loops banned; identical command ≥3 times triggers stuck-check)
- **Output-Quality Completeness Check** in Phase 2.5 (detects column-empty / row-empty / fill-rate-<50% / regression-vs-prior anomalies BEFORE declaring task success)
- **Heartbeat for Background Mode** (`.conductor/heartbeat.json` so parent agents read background-mode status without spawning a second conductor)
- **`agent-monitor/` bundle** — opt-in monitoring with auto-pattern detection (probe sprawl, busy-wait, no-forward-progress, repeat-bash, scope-shrink signals) pre-fills the "Issues & Patterns" table in session reports. Includes opt-in share-footer with GitHub issue URL template.
- **`hooks/` bundle** — two opt-in PostToolUse hooks: `heartbeat.py` (writes heartbeat file) and `usage_limit_wakeup.py` (detects API limits, writes recovery instructions for the conductor to `ScheduleWakeup`).

### Fixed

- **Probe-loop without commitment** — agent would write throwaway research scripts indefinitely, never committing to a draft. Investigation Budget rule + auto-detection in `agent-monitor/` address this.
- **Misclassified Hard Stop on implementation detail** — agent treated discovering "site needs different transport" as architectural change requiring user decision. Hard Stop reclassification + NOT Hard Stops expansion address this.
- **Status reports based on time estimates** — agent answered "probably 25-55 minutes remaining" with no actual signal. Status from State rule addresses this.
- **Busy-wait via shell loops** — agent used `until grep -q "...";  do sleep N; done` to wait on background tasks, burning turns/tokens. Forbidden Bash Patterns rule + auto-detection address this.
- **Auto-shrinkage of scope under perceived time pressure** — agent stopped at 55/200 SKUs instead of delivering partial output and continuing. Notify-Don't-Block + anti-shrinkage clause address this.
- **Premature acceptance of failure as "known limitation"** — agent baked failure into code comments after only 2 attempts. Anti-Premature-Failure rule (with explicit ban on "KNOWN LIMITATION") addresses this.
- **Background-agent visibility black hole** — parent Claude Code couldn't see backgrounded conductor's progress, resorted to spawning a second conductor (50k+ tokens) just to query state. Heartbeat protocol addresses this.
- **No output-quality verification** — `verify_workbook` checked file structure but not field-fill rates. Entire-column-empty patterns slipped through as "success." Output-Quality Completeness Check addresses this.
- **Empty observation tables in monitor reports** — reporter generated `| 1 | | | |` placeholders for the user to fill in manually. Auto-pattern detection in v4 reporter pre-fills detected patterns.

### Documentation

- README.md: new "What's new in v4" table, updated Safety mechanisms table, new Optional monitoring + Optional hooks sections, new `--strict-mode` description, fixed `project-conductor-v3.md` → `project-conductor.md` filename reference
- CONTRIBUTING.md: new "Sharing your monitor reports" section explaining the share-footer flow and what to redact
- agent-monitor/README.md, hooks/README.md: full install instructions, security notes, uninstall steps

### Telemetry

**None.** All data stays local. The opt-in `agent-monitor/` reports include a GitHub issue URL template in the share-footer, but you decide what (if anything) to share. No automatic data collection.

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

---
name: cli-agent-interop
description: Explicit cross-agent CLI routing for local coding agents. Use this skill only when the human explicitly asks to call, switch, compare, route, or hand work to another agent such as Claude, Codex, Copilot, Gemini, OpenCode, or Qwen/Qwen Code, or explicitly asks for Windows-side versus WSL-side agent execution. Do not trigger it for ordinary coding tasks. Default policy keeps Windows agents on Windows, WSL agents on WSL, and places the current agent itself last as a same-runtime fallback.
compatibility: Requires terminal access plus at least one installed CLI agent. Bundled wrapper supports claude, codex, copilot, gemini, opencode, qwen, qwencode, qwen-code, qwen-code-cli, and github-copilot aliases across current-runtime and explicit Windows/WSL routing.
license: MIT
---

# CLI Agent Interop

This is a resident skill for explicit agent-to-agent delegation. Keep it installed globally, but keep it dormant until the human explicitly asks to use another agent.

Prefer the bundled `scripts/agent_bridge.py` for routing, readiness checks, and bounded one-shot runs. Escalate to native interactive sessions only when the task genuinely needs follow-up turns, TUI state, or session persistence.

## Activation boundary (critical)

Load this skill when the human explicitly asks for one of these behaviors:
- use another agent
- call Gemini / Codex / Claude / Copilot / OpenCode / Qwen
- compare two or more agents
- switch execution to Windows-side or WSL-side agents
- hand a task from the current agent to another agent

Do not load this skill just because a coding task exists.

Non-triggers:
- ordinary implementation / debugging / refactoring requests with no explicit agent-routing request
- normal subagent use inside the current agent when no external-agent handoff was requested
- general “please solve this” prompts that do not mention another agent or another runtime

## Quick start

1. Inspect the current-runtime inventory:
   - `python scripts/agent_bridge.py list --runtime current`
2. Ask for the same-runtime peer order for the current agent:
   - `python scripts/agent_bridge.py route --current-agent codex --runtime current`
3. Check one agent before relying on it:
   - `python scripts/agent_bridge.py check gemini --runtime current --smoke --workdir .`
   - For Codex, use a longer smoke timeout when plugins or MCP servers are enabled: `python scripts/agent_bridge.py check codex --runtime current --smoke --workdir . --timeout 120`
4. Run a bounded same-runtime delegation:
   - `python scripts/agent_bridge.py run claude --prompt "Review the diff and report bugs" --runtime current --workdir .`
5. Run an explicit cross-runtime delegation only when the human asked for it:
   - `python scripts/agent_bridge.py run copilot --prompt "Summarize the current branch in five bullets" --runtime windows --workdir .`

## Canonical workflow

Follow this sequence whenever one local agent should invoke another.

### 1) Confirm the human explicitly asked for another agent

This skill exists for explicit routing, not silent substitution.

If the human did not explicitly request another agent or another runtime, stay in the current agent and do not delegate externally.

### 2) Resolve runtime policy before agent choice

Use these rules first:
- `--runtime current` is the default.
- On Windows, `current` means Windows-side agents only.
- In WSL, `current` means WSL-side agents only.
- Cross-runtime routing happens only with an explicit `--runtime windows` or `--runtime wsl` choice that reflects the human’s request.
- Never auto-jump to another runtime just because it looks healthier.

### 3) Prefer other agents in the same runtime before self-agent fallback

Ask the wrapper for the same-runtime route order:

- `python scripts/agent_bridge.py route --current-agent codex --runtime current`

Default behavior:
- peer agents in the target runtime come first
- the current agent itself is pushed to the end as a fallback
- if the human explicitly requests a target agent, that requested agent moves to the front
- if the human explicitly requests the same agent brand again, treat that as an override instead of blocking it

This encodes the user’s preference that “Codex should know how to call Claude / Gemini / others first, and Codex itself becomes the lower fallback when dedicated subagent behavior is unavailable.”

### 4) Use one handoff contract

Build the delegated prompt using `references/handoff-contract.md`.

The handoff must state:
- host runtime and target runtime
- current agent and requested target agent
- objective
- repo / workdir
- files or directories in scope
- constraints
- expected deliverable
- verification steps

When comparing agents, keep the handoff text identical and change only the target agent.

### 5) Default to bounded, non-interactive execution

Prefer these modes first:
- Claude Code: `claude -p`
- Codex: `codex exec`
- Gemini: `gemini -p`
- OpenCode: `opencode run`
- Qwen / Qwen Code: positional one-shot prompt
- GitHub Copilot CLI: direct `copilot -p ...` in the selected runtime, or same-runtime `gh copilot -- -p ...` only if direct `copilot` is unavailable there

The wrapper script already encodes these defaults.

### 6) Start read-only or plan-first

Do not grant write-capable execution by default.

Use these defaults unless edits are intended:
- Claude: `--permission-mode plan`
- Codex: `--sandbox read-only`
- Gemini: `--approval-mode plan`
- Qwen: `--approval-mode plan`
- OpenCode: one-shot run without extra write escalation
- Copilot: keep the prompt narrow and verify runtime readiness first

Then opt into `--allow-write` or `--yolo` only when the task actually needs it.

### 7) Always set the working directory explicitly

Pass `--workdir` every time.

The wrapper normalizes Windows paths and WSL `/mnt/...` paths for the selected runtime so different agents can share one call surface without silently switching runtimes.

### 8) Verify before you trust the result

Use `python scripts/agent_bridge.py check <agent> --runtime <...> --smoke` when readiness matters.

Interpret checks narrowly:
- `list` proves only that a CLI binary is discoverable in the selected runtime.
- `check` proves only that the fast native readiness command exits successfully.
- `check --smoke` proves that the selected agent can answer a minimal one-shot prompt under the supplied timeout.
- `run` is the actual delegation path; trust it only after checking its exit code and output.

Codex-specific handling:
- Codex `exec` can append stdin to the prompt when stdin is piped. The wrapper sends Codex prompts through controlled stdin with `codex exec ... -`; do not revert this to a positional prompt plus inherited stdin.
- Codex loads user config, skills, plugins, MCP clients, memory hooks, and shutdown hooks during one-shot runs. Warnings from those layers can make smoke tests slower than other agents.
- Use `--timeout 120` or higher for Codex smoke/run checks on plugin-heavy profiles.
- If Codex prints the expected answer but exits with a timeout, inspect the wrapper's `partial_output` or `smoke_timeout.partial_output` field; treat it as an incomplete run until the timeout cause is fixed or the timeout is adjusted.
- When Codex `check --smoke` times out but `run codex --prompt ...` succeeds, report the distinction: readiness smoke is inconclusive, while the actual delegation path worked.

OpenCode-specific handling:
- `opencode auth list` only checks credentials and environment visibility.
- `opencode run` is the path that matters for delegation. Model/provider choice can make the smoke response take tens of seconds.
- If OpenCode `check --smoke` exits 0 but does not include the expected token, do not call it healthy from smoke alone; immediately verify with an explicit `run opencode --prompt ...` and report both outcomes.
- `--dir` is part of the OpenCode run command; keep passing `--workdir` to the wrapper so the selected runtime sees the intended project path.

If a delegated command returns auth, rate-limit, or runtime errors, surface the real failure instead of pretending the target agent completed the task.

## Runtime policy summary

| Host side | Default target runtime | Automatic cross-runtime? | Explicit override |
|---|---|---|---|
| Windows agent | Windows | No | `--runtime wsl` |
| WSL agent | WSL | No | `--runtime windows` |

The important rule is behavioral, not technical: another runtime may exist, but it is not the default execution surface unless the human explicitly asked for it.

## Agent selection guidance

Use this rough decision rule after runtime policy is fixed.

- `claude`: strong for multi-step editing, code review, and longer reasoning chains. Keep print mode for bounded delegation; use tmux only for true interactive sessions.
- `codex`: strong for one-shot repo tasks, non-interactive implementation, and scripted automation. Outside a git repo, keep `--skip-git-repo-check`.
- `gemini`: good for one-shot analysis / implementation and MCP-aware workflows. Use `-p` first.
- `opencode`: good when provider flexibility matters or when you want a vendor-neutral coding worker. Use `opencode run` first.
- `qwen`: use for Qwen / Qwen Code delegation. Re-check auth immediately if you see `401 invalid access token or token expired`.
- `copilot`: stay inside the selected runtime. Prefer direct `copilot` in that runtime; use same-runtime `gh copilot` only if direct `copilot` is unavailable there.

See `references/command-matrix.md` for exact command patterns, runtime policy notes, and current observed environment facts.

## Interactive escalation rule

Do not start an interactive TUI just because it exists.

Escalate to native interactive sessions only if one of these is true:
- the task needs multi-turn steering
- the task needs slash commands or session resume semantics
- the delegated agent must stay alive while another process changes state
- the human explicitly asked for that agent’s TUI workflow

When you do escalate, use the native agent-specific skills for that agent and keep this wrapper for runtime routing, readiness checks, and one-shot fallbacks.

## Shared output discipline

When one agent delegates to another, require the child agent to return:
1. what it changed or found
2. what it verified
3. remaining risks or blockers
4. exact failure messages if the run was incomplete

This keeps inter-agent handoffs auditable and makes agent comparisons meaningful.

## Bundled resources

- `scripts/agent_bridge.py`
  - canonical wrapper for listing, routing, checking, smoke-testing, and one-shot delegation
- `references/command-matrix.md`
  - per-agent command matrix, runtime policy, and current environment notes
- `references/handoff-contract.md`
  - reusable handoff template for cross-agent calls
- `examples/handoff-prompts.md`
  - ready-made prompt patterns for review, implementation, and runtime-explicit delegation

## Rules

1. Do not trigger this skill without an explicit human instruction to use another agent or another runtime.
2. `--runtime current` is the default.
3. Cross-runtime routing requires an explicit `--runtime windows` or `--runtime wsl` choice.
4. Use `route` before ad-hoc peer selection when the current agent matters.
5. Keep the current agent last as a same-runtime fallback unless the human explicitly requested that same agent.
6. Prefer bounded one-shot delegation before interactive sessions.
7. Pass `--workdir` explicitly every time.
8. Report exact runtime failures; do not downgrade them into vague summaries.
9. Never auto-hop from WSL to Windows or from Windows to WSL just because a tool looks healthier there.
10. Do not let child agent CLIs inherit wrapper stdin; Codex prompts must use controlled stdin with `codex exec ... -`.

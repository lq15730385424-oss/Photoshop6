# Command Matrix

Use this file when choosing a target agent or when the bundled wrapper is not enough and you need the native command form.

## Runtime-local routing policy

| Host runtime | Default target runtime | Auto cross-runtime? | Explicit override |
|---|---|---|---|
| Windows | Windows | No | `--runtime wsl` |
| WSL | WSL | No | `--runtime windows` |

The wrapper follows policy, not convenience. If WSL-side Copilot is broken but the human did not explicitly ask for Windows-side execution, the correct outcome is to surface the WSL failure instead of silently hopping to Windows.

## Peer-order policy

Ask the wrapper for the route order whenever the current agent matters:

```bash
python scripts/agent_bridge.py route --current-agent codex --runtime current
python scripts/agent_bridge.py route --current-agent claude --requested-agent gemini --runtime current
```

Default ordering rules:
1. stay inside the selected runtime
2. prefer other agents first
3. push the current agent itself to the end as fallback
4. if the human explicitly requests a specific target agent, move that agent to the front
5. if the human explicitly requests the same agent brand again, allow it as an override

## Canonical one-shot commands

| Agent | Preferred bounded command | Safe default | Notes |
|---|---|---|---|
| Claude Code | `claude -p "<prompt>" --output-format text --no-session-persistence --permission-mode plan` | plan / read-only | Use tmux only for true interactive workflows. |
| Codex | `codex exec --skip-git-repo-check --sandbox read-only -` with the prompt on controlled stdin | read-only sandbox | Do not use positional prompt plus inherited stdin; use longer timeouts when plugins/MCP/memory hooks are enabled. |
| Gemini | `gemini -p "<prompt>" --output-format text --approval-mode plan` | plan / read-only | Good default for bounded delegation. |
| OpenCode | `opencode run "<prompt>" --dir "<workdir>"` | one-shot run | Use interactive TUI only when follow-up turns matter. Provider/model choice can make smoke tests slow. |
| Qwen / Qwen Code | `qwen "<prompt>" --output-format text --approval-mode plan` | plan / read-only | Positional prompt is preferred over deprecated `--prompt`. |
| GitHub Copilot CLI | direct `copilot -p "<prompt>"` in the selected runtime; same-runtime `gh copilot -- -p "<prompt>"` only if direct `copilot` is unavailable there | narrow prompt + runtime check | Do not auto-hop runtimes. |

## Cross-runtime examples

From WSL to explicitly use Windows-side agent execution:

```bash
python scripts/agent_bridge.py run copilot           --prompt "Summarize the current branch in five bullets"           --runtime windows           --workdir .
```

From Windows to explicitly use WSL-side agent execution:

```bash
python scripts/agent_bridge.py run gemini           --prompt "Review the current diff and report bugs"           --runtime wsl           --workdir .
```

## Readiness checks

| Agent | Fast check | Live smoke |
|---|---|---|
| Claude Code | `claude auth status --text` | `claude -p 'Respond with exactly: CLAUDE_SMOKE_OK' --output-format text --permission-mode plan --no-session-persistence` |
| Codex | `codex exec --help` | `codex exec --skip-git-repo-check --sandbox read-only 'Respond with exactly: CODEX_SMOKE_OK'` |
| Gemini | `gemini --help` | `gemini -p 'Respond with exactly: GEMINI_SMOKE_OK'` |
| OpenCode | `opencode auth list` | `opencode run 'Respond with exactly: OPENCODE_SMOKE_OK'` |
| Qwen | `qwen auth status` | `qwen 'Respond with exactly: QWEN_SMOKE_OK' --output-format text` |
| Copilot | `copilot --help` or same-runtime `gh copilot -- --help` | `copilot -p 'Respond with exactly: COPILOT_SMOKE_OK' --allow-all-tools` |

## Wrapper behavior notes

- On Windows, npm-installed agents often expose `.CMD` shims. The wrapper keeps `shell=True` for these commands because direct `CreateProcess` execution is not reliable for every agent shim.
- The wrapper passes `stdin=subprocess.DEVNULL` to ordinary child commands. For Codex prompts it instead uses `codex exec ... -` and sends the prompt through controlled stdin, because `codex exec` appends piped stdin to the prompt when both stdin and a prompt argument are present.
- `check` and `run` do not mean the same thing. `check` verifies the fast native readiness command; `run` is the real delegation path.
- Codex one-shot runs include user config, skill loading, plugin/MCP startup, memory hooks, and shutdown hooks. A valid answer can appear before the final process exit. Use `--timeout 120` or higher when diagnosing Codex wrapper behavior, and inspect timeout JSON `partial_output` or `smoke_timeout.partial_output` before deciding whether the model itself failed.
- OpenCode `opencode auth list` verifies credentials only. Validate delegation with `opencode run` through the wrapper. If OpenCode smoke exits 0 without the expected token, treat smoke as inconclusive and verify `run` directly.

## Current observed environment for this rebuild

Observed from the active WSL host shell during the initial refactor:

WSL runtime:
- `node -v` -> `v22.22.2`
- `copilot --version` -> `GitHub Copilot CLI requires Node.js v24 or higher. Currently using v22.22.2.`
- `gh --version` -> `2.89.0`
- `qwen --version` -> `0.14.4`
- `gemini --version` -> `0.37.2`
- `codex --version` -> `codex-cli 0.121.0`
- `opencode --version` -> `1.2.6`
- `claude --version` -> `2.1.116 (Claude Code)`

Windows runtime, observed explicitly via `--runtime windows` from WSL at the initial refactor:
- `claude` -> `2.1.114 (Claude Code)`
- `codex` -> `codex-cli 0.121.0`
- `gemini` -> `0.37.1`
- `opencode` -> `1.2.27`
- `qwen` -> `0.14.3`
- `copilot` -> `GitHub Copilot CLI 1.0.34`

Windows runtime, rechecked from PowerShell on 2026-06-04:
- `claude` -> `2.1.145 (Claude Code)`
- `codex` -> `codex-cli 0.128.0`
- `gemini` -> `0.40.1`
- `opencode` -> `1.15.13`
- `qwen` -> `0.14.3`
- `copilot` -> `GitHub Copilot CLI 1.0.34`

Implication:
- the Windows side is available as an explicit alternative runtime
- the wrapper must still stay in WSL by default for WSL-side agents
- switching to Windows remains an explicit policy choice, not an automatic health-based fallback

## Comparison discipline

When comparing two or more agents:

1. Keep the prompt identical.
2. Keep the working directory identical.
3. Keep file scope and constraints identical.
4. Start with read-only / plan-first mode.
5. Record failures as real outcomes. A runtime failure still counts as a comparison result.
6. Only escalate a subset of agents into write-capable mode if that is the explicit test.

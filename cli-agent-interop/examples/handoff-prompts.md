# Handoff Prompt Examples

## 1) Ask for peer order before choosing a target

```bash
python scripts/agent_bridge.py route --current-agent codex --runtime current
```

This keeps the current agent last and shows which same-runtime peers are available first.

## 2) Compare Codex vs Gemini on the same review task

```text
Runtime:
- host runtime: wsl
- target runtime: current

Agents:
- current agent: claude
- target agent: codex or gemini
- self-fallback policy: peer agents first; self only as fallback unless explicitly requested

Objective:
- Review the current diff for correctness, security issues, and missing tests.

Workspace:
- workdir: /mnt/c/Users/11/my-repo
- repo or project: my-repo

Scope:
- files/directories in scope: current git diff only
- inputs already available: `git diff main...HEAD`
- do not touch: no file edits

Constraints:
- read-only only
- keep the answer under 15 bullet points

Deliverable:
- prioritized findings with file references

Verification:
- every finding must cite the exact file and reason

Failure handling:
- return exact blocking error if the diff cannot be read
```

## 3) Delegate a narrow same-runtime implementation change

```bash
python scripts/agent_bridge.py run gemini           --prompt "Update src/parser.py so blank lines are ignored, then update the parser tests"           --runtime current           --workdir .           --allow-write
```

## 4) Explicitly use Windows-side Copilot from WSL

```bash
python scripts/agent_bridge.py check copilot --runtime windows --workdir .
python scripts/agent_bridge.py run copilot           --prompt "Summarize the current branch in five bullets"           --runtime windows           --workdir .
```

## 5) Windows path example

```bash
python scripts/agent_bridge.py run codex           --prompt "Review src/auth.py for bugs"           --runtime current           --workdir 'C:\Users\11\project-x'
```

The wrapper will normalize the path for the selected runtime without silently changing runtimes.

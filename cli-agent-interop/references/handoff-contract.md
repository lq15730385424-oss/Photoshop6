# Handoff Contract

Use the same structure whenever one agent delegates to another. The goal is to remove ambiguity, preserve runtime intent, and make agent-to-agent comparisons fair.

## Minimal contract

```text
Runtime:
- host runtime: <windows|wsl>
- target runtime: <current|windows|wsl>

Agents:
- current agent: <codex|claude|gemini|opencode|qwen|copilot>
- target agent: <target agent name>
- self-fallback policy: peer agents first; self only as fallback unless explicitly requested

Objective:
- <one sentence describing the task>

Workspace:
- workdir: <absolute path>
- repo or project: <name or path>

Scope:
- files/directories in scope: <paths>
- inputs already available: <files, logs, diffs, URLs>
- do not touch: <paths or systems>

Constraints:
- <style / safety / dependency / time constraints>
- <whether external network use is allowed>
- <whether file edits are allowed>

Deliverable:
- <what the child agent must return>

Verification:
- <tests, smoke checks, or evidence the child agent must provide>

Failure handling:
- If blocked, return the exact command/output/error and stop.
```

## JSON-shaped variant

Use this when a coordinator agent wants a machine-readable handoff.

```json
{
  "runtime": {
    "host": "wsl",
    "target": "current"
  },
  "agents": {
    "current": "codex",
    "target": "gemini",
    "self_fallback_policy": "peer-first-self-last"
  },
  "objective": "...",
  "workdir": "/absolute/path",
  "scope": {
    "include": ["src", "tests/test_auth.py"],
    "exclude": ["secrets", ".env"]
  },
  "inputs": ["git diff", "pytest output"],
  "constraints": [
    "prefer read-only first",
    "no dependency upgrades unless required"
  ],
  "deliverable": [
    "summary of changes or findings",
    "verification performed",
    "remaining risks"
  ],
  "failure_handling": "return exact blocking error"
}
```

## Example: same-runtime review handoff

```text
Runtime:
- host runtime: wsl
- target runtime: current

Agents:
- current agent: codex
- target agent: gemini
- self-fallback policy: peer agents first; self only as fallback unless explicitly requested

Objective:
- Review the current diff for bugs, security risks, and missing tests.

Workspace:
- workdir: /mnt/c/Users/11/project-x
- repo or project: project-x

Scope:
- files/directories in scope: current git diff only
- inputs already available: `git diff --stat`, `git diff`
- do not touch: no file edits

Constraints:
- read-only only
- no network use unless the prompt explicitly says so

Deliverable:
- concise review with severity, file / line references, and concrete fixes

Verification:
- cite the exact diff hunk or file location for every issue

Failure handling:
- if the agent cannot access the repo or diff, return the exact failure
```

## Example: explicit Windows-side implementation handoff

```text
Runtime:
- host runtime: wsl
- target runtime: windows

Agents:
- current agent: claude
- target agent: copilot
- self-fallback policy: peer agents first; self only as fallback unless explicitly requested

Objective:
- Refactor `src/auth.py` to centralize token parsing and update tests.

Workspace:
- workdir: /mnt/c/Users/11/project-x
- repo or project: project-x

Scope:
- files/directories in scope: `src/auth.py`, `tests/test_auth.py`
- inputs already available: failing pytest output
- do not touch: CI, deployment, unrelated modules

Constraints:
- edits allowed only inside listed files
- preserve public API
- do not add new dependencies

Deliverable:
- changed files summary
- tests run and results
- remaining edge cases

Verification:
- run the relevant test file or equivalent smoke check

Failure handling:
- if blocked, return the exact test failure or permission problem
```

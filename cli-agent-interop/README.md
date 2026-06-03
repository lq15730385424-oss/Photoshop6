# cli-agent-interop

统一的命令行智能体互调技能。

目标：让任意本地 agent 用一套共享脚本与交接契约，去调用 Claude Code、Codex、GitHub Copilot CLI、Gemini CLI、OpenCode、Qwen / Qwen Code；同时把 Windows / WSL 的调用边界明确固化下来。

## 核心策略

- Windows 侧 agent：默认只调用 Windows 侧 agent。
- WSL 侧 agent：默认只调用 WSL 侧 agent。
- 只有在人工明确要求“用 Windows 侧 / 用 WSL 侧”时，才允许跨 runtime。
- 当前 agent 不优先调用自己；自己只作为同 runtime 内的最后 fallback。
- 这是常驻技能，但默认不自动触发；只有人工明确要求“调用别的 agent / 比较 agent / 切换到 Windows 或 WSL 侧 agent”时才启用。

## 包内内容

- `SKILL.md`：主技能说明
- `scripts/agent_bridge.py`：统一 wrapper，支持 `list / route / check / run`
- `references/command-matrix.md`：各 agent 的命令矩阵、runtime 规则、当前环境观察
- `references/handoff-contract.md`：跨 agent 交接 prompt 模板
- `examples/handoff-prompts.md`：示例提示词

## 常用命令

```bash
python scripts/agent_bridge.py list --runtime current
python scripts/agent_bridge.py route --current-agent codex --runtime current
python scripts/agent_bridge.py check gemini --runtime current --smoke --workdir .
python scripts/agent_bridge.py check codex --runtime current --smoke --workdir . --timeout 120
python scripts/agent_bridge.py run claude --prompt "Review the current diff and report bugs" --runtime current --workdir .
python scripts/agent_bridge.py run copilot --prompt "Summarize the current branch in five bullets" --runtime windows --workdir .
```

## Codex / OpenCode 注意事项

- `check` 只证明快速探测命令可用；真实交接以 `run` 的退出码和输出为准。
- Codex `exec` 会把管道 stdin 追加进 prompt。wrapper 对 Codex 使用 `codex exec ... -` 加受控 stdin，不要改回“位置 prompt + 继承 stdin”。
- Codex 会加载用户配置、skills、plugins、MCP、memory 和 shutdown hooks；smoke/run 建议用 `--timeout 120` 或更高。
- OpenCode 当前 `opencode run ... --dir <workdir>` 是主要 one-shot 路径；`opencode auth list` 只能证明凭据可见。OpenCode smoke 如果退出 0 但没有固定 token，要用明确的 `run` 复验。

## 已内置的别名

- `qwen` / `qwencode` / `qwen-code` / `qwen-code-cli`
- `copilot` / `github-copilot` / `gh-copilot`
- `claude` / `claude-code`
- `codex` / `openai-codex`

## 当前环境观察（本次重构时）

- 当前 WSL shell: `node -v` -> `v22.22.2`
- 当前 WSL shell: `copilot --version` 仍直接报 “requires Node.js v24 or higher”
- 当前 WSL shell 可见：claude / codex / gemini / opencode / qwen / copilot
- 显式查看 Windows runtime 时，也能看到 Windows 侧的 claude / codex / gemini / opencode / qwen / copilot
- 这版技能不会再因为 Windows 侧更健康就自动跳过去；除非明确写 `--runtime windows`

## 建议安装位置

全局共享技能库：
- `C:\Users\11\.agents\skills\cli-agent-interop`

安装/更新后重建索引：

```bash
node /mnt/c/Users/11/.agents/skills/scripts/build-skill-index.js
node /mnt/c/Users/11/.agents/skills/scripts/build-catalog.js
```

## 适用场景

- “让 gemini / codex / qwen / claude / copilot 去做这个任务”
- “把同一个 prompt 分别交给多个 agent 做 AB 对比”
- “如果当前 agent 是 codex，先看同 runtime 下还有哪些 peer agent 可以调”
- “明确要求切到 Windows 侧 agent / WSL 侧 agent”
- “需要统一 one-shot 调用接口、检查环境、规范交接 prompt”

## 不适用场景

- 普通编码任务，但用户没有明确要求调用其他 agent
- 当前 agent 自己就能完成，且不需要外部 agent 参与
- 仅仅因为另一个 runtime 更健康，就想偷偷绕过去

# Project Failure Findings
- **architecture-visualizer [BattleChess] [server.js]** - Blocking exec() calls in Node.js can cause UI freeze if the process is long-running. Fixed with non-blocking UDP stream.

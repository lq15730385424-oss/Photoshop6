---
name: time-travel-debugger
description: Deploy an interactive, AST-based web IDE debugger for complex logic. Use this skill to visually step through code execution dynamically. Includes blueprints for AST parsing, UDP telemetry hooking, and WebSocket bridging to a ReactFlow VCR UI.
---

# Time-Travel Web Debugger

This acquired skill contains the blueprints to transform a standard backend process into an **Interactive AST Web IDE Debugger**. 

As you encounter new languages, new frameworks, or new use cases, store those blueprints inside the `templates/` folder of this skill to continually upgrade its capabilities.

## The Acquired Knowledge
We successfully constructed an architecture that maps and visualizes backend logic:
1. **TreeSitter AST Parsing**: (`templates/parser/parse_cpp.py`) parses syntax trees to extract functions, loops, and conditions, injecting UDP `telemetry_ping` hooks dynamically.
2. **Telemetry Bridge**: (`templates/server.js`) intercepts file uploads, compiles the hooked code, spawns the binary, and bridges UDP execution hooks to the browser via WebSockets.
3. **ReactFlow VCR UI**: (`templates/App.tsx`) A React Web IDE with a built-in terminal, code editor, and interactive flowchart that tracks and replays the execution path.

## How to Deploy the Time-Travel Debugger
1. **Copy the Templates**: Copy `telemetry.h`, `server.js`, `parse_cpp.py`, and `App.tsx` from `~/.gemini/antigravity/skills/time-travel-debugger/templates/` into the workspace.
2. **Install Dependencies**: Ensure `ws`, `tree-sitter`, `@xyflow/react`, and `dagre` are installed.
3. **Run `debug.sh`**: Use the single-command runner to boot the local Web IDE.
4. **Adapt for New Languages**: Write a new parser (e.g., `parse_python.py`) using `tree-sitter`, and drop it into `templates/parser/`. Document the new level-up here!

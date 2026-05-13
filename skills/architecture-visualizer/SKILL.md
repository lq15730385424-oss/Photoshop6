---
name: architecture-visualizer
description: Use this skill whenever starting a new major project, adding a new feature, or when the user asks to see the architecture, data flow, or system design. This skill mandates that you create or continuously update an `architecture.json` file to map out the system stack as a visual data flow graph. It acts as the "Live Blueprint" of the project.
---

# Architecture & Stack Visualizer (Upgraded)

When starting a new project or making significant changes to an existing one, maintaining a visual mental model is crucial. This skill ensures you visualize the data flow, microservices, and stack components before diving into the code, and keep it updated as the project grows.

## The Workflow

1.  **Analyze the System**: Understand the core components of the system (e.g., Client, API, Postgres, Redis Queue, Cloud Workers).
2.  **Maintain `architecture.json`**: Before writing new architectural code, or when adding a new major component, create or update `architecture.json` in `/home/integrity/Desktop/agent/01_Projects/architecture-visualizer/src/`. You must do this proactively.
3.  **Launch the Visualizer**: If it isn't already running, start the Architecture Visualizer app (`cd ~/Desktop/agent/01_Projects/architecture-visualizer && npm run dev`).
4.  **Confirm Alignment**: Ensure the user approves the macro-level architecture before diving into micro-level implementation.

## architecture.json Format (v2 Schema)

The visualizer uses React Flow. Your `architecture.json` MUST follow this exact schema.

You can use the following advanced **Architecture Nodes**: 
`frontend`, `server`, `database`, `worker`, `cache`, `queue`, `api_gateway`, `external_api`

```json
{
  "nodes": [
    {
      "id": "client-app",
      "type": "customNode",
      "data": { 
        "label": "React Client", 
        "type": "frontend",
        "description": "User facing dashboard" 
      },
      "position": { "x": 100, "y": 100 }
    },
    {
      "id": "redis-queue",
      "type": "customNode",
      "data": { 
        "label": "Redis Cache", 
        "type": "cache",
        "description": "Stores session tokens" 
      },
      "position": { "x": 100, "y": 250 }
    }
  ],
  "edges": [
    {
      "id": "e_client_redis",
      "source": "client-app",
      "target": "redis-queue",
      "animated": true,
      "label": "Fetches Session"
    }
  ]
}
```

Make sure to intelligently space out the `position` of the nodes so they don't overlap (e.g., space them by `x: 250` or `y: 150` increments).

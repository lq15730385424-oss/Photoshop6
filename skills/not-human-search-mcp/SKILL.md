---
name: not-human-search-mcp
description: "Search and score AI-ready websites, verify MCP endpoints, and discover tools and APIs using the Not Human Search MCP server"
category: mcp
risk: safe
source: "https://nothumansearch.ai"
source_type: community
date_added: "2026-04-16"
author: unitedideas
tags: [mcp, search, ai-discovery, api-discovery, mcp-verification, agent-tools]
tools: [claude, cursor, gemini]
---

# Not Human Search MCP

## Overview

Not Human Search is a remote MCP server that lets AI agents search a curated index of 1,750+ AI-ready websites, check individual site scores, score any URL for AI-readiness, and verify live MCP endpoints via JSON-RPC probe. It is designed for AI agents that need to discover tools, APIs, and services at runtime without relying on hardcoded lists.

## When to Use This Skill

- Use when an AI agent needs to discover tools, APIs, or MCP servers for a specific task
- Use when you want to check whether a website exposes machine-readable endpoints (llms.txt, OpenAPI, MCP)
- Use when verifying that an MCP endpoint is actually responding to JSON-RPC
- Use when building agent workflows that need to find and connect to external services dynamically

## MCP Configuration

Add the Not Human Search MCP server to your client configuration. The endpoint uses streamable HTTP and requires no authentication.

### Claude Desktop / Cursor / Windsurf

```json
{
  "mcpServers": {
    "not-human-search": {
      "url": "https://nothumansearch.ai/mcp"
    }
  }
}
```

No API key or authentication is required.

## Available Tools

### `search`

Search the index of 1,750+ AI-ready websites by keyword. Returns ranked results with scores, categories, and available endpoints.

```
search({ query: "code review tools" })
```

### `check`

Check a specific domain's AI-readiness score and available machine-readable endpoints.

```
check({ url: "example.com" })
```

### `score`

Score any URL for AI-readiness. Probes for llms.txt, OpenAPI specs, MCP endpoints, robots.txt AI bot rules, and other machine-readable signals.

```
score({ url: "https://example.com" })
```

### `verify_mcp`

Verify whether a URL is a live MCP endpoint by sending a JSON-RPC probe and checking for a valid response.

```
verify_mcp({ url: "https://example.com/mcp" })
```

## Examples

### Example 1: Discover Code Review Tools

```text
Use @not-human-search-mcp to find code review tools that expose MCP or API endpoints.
```

The agent will call `search({ query: "code review" })` and return ranked results with scores and endpoint details.

### Example 2: Check if a Site is AI-Ready

```text
Use @not-human-search-mcp to check the AI-readiness of linear.app.
```

The agent will call `check({ url: "linear.app" })` and return the site's score breakdown.

### Example 3: Verify an MCP Endpoint

```text
Use @not-human-search-mcp to verify that https://heliumtrades.com/mcp is a working MCP server.
```

The agent will call `verify_mcp({ url: "https://heliumtrades.com/mcp" })` and confirm whether it responds to JSON-RPC.

## Best Practices

- Use `search` for broad discovery, then `check` or `score` for detailed analysis of specific results
- Use `verify_mcp` to confirm an MCP endpoint is live before wiring it into an agent workflow
- Combine with other MCP skills to build dynamic tool-discovery pipelines

## Limitations

- The search index covers 1,750+ sites and is updated regularly, but may not include every site on the internet.
- Scoring reflects machine-readable signals (llms.txt, OpenAPI, MCP, structured data) rather than content quality.
- `verify_mcp` sends a JSON-RPC probe to the target URL; only use it on URLs you expect to be MCP endpoints.

## Related Skills

- `@mcp-builder` - For building your own MCP servers
- `@ai-dev-jobs-mcp` - Search AI/ML job listings via MCP

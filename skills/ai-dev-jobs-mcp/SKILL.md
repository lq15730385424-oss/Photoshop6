---
name: ai-dev-jobs-mcp
description: "Search AI and ML job listings from 289+ companies, get job details, list hiring companies, and view market stats via the AI Dev Jobs MCP server"
category: mcp
risk: safe
source: "https://aidevboard.com"
source_type: community
date_added: "2026-04-16"
author: unitedideas
tags: [mcp, jobs, ai-jobs, ml-jobs, recruiting, job-search, career]
tools: [claude, cursor, gemini]
---

# AI Dev Jobs MCP

## Overview

AI Dev Jobs is a remote MCP server that gives AI agents access to a live index of AI and ML job listings from 289+ companies including OpenAI, Anthropic, Google DeepMind, Meta AI, and more. Agents can search jobs by role, location, or company, retrieve full job details, list all hiring companies, and get aggregate market statistics. It is designed for AI agents that assist with job searching, recruiting, or labor market analysis.

## When to Use This Skill

- Use when helping a user search for AI or ML engineering jobs
- Use when an agent needs to look up which companies are hiring for specific AI roles
- Use when building recruiting or talent-matching workflows
- Use when analyzing the AI job market (open positions, top companies, role distribution)

## MCP Configuration

Add the AI Dev Jobs MCP server to your client configuration. The endpoint uses streamable HTTP and requires no authentication.

### Claude Desktop / Cursor / Windsurf

```json
{
  "mcpServers": {
    "ai-dev-jobs": {
      "url": "https://aidevboard.com/mcp"
    }
  }
}
```

No API key or authentication is required.

## Available Tools

### `search_jobs`

Search the job index by keyword, location, company, or work arrangement. Returns matching listings with title, company, location, and salary information.

```
search_jobs({ query: "machine learning engineer", location: "remote" })
```

### `get_job`

Retrieve full details for a specific job listing by ID, including description, requirements, salary range, and application link.

```
get_job({ id: "abc123" })
```

### `list_companies`

List all companies in the index with their open position counts. Useful for discovering which companies are actively hiring.

```
list_companies({})
```

### `get_stats`

Get aggregate statistics about the job market: total listings, top companies by open roles, role distribution, and location breakdown.

```
get_stats({})
```

## Examples

### Example 1: Find Remote ML Jobs

```text
Use @ai-dev-jobs-mcp to find remote machine learning engineer positions.
```

The agent will call `search_jobs({ query: "machine learning engineer", location: "remote" })` and return matching listings.

### Example 2: Check Which Companies Are Hiring

```text
Use @ai-dev-jobs-mcp to list all companies currently hiring for AI roles.
```

The agent will call `list_companies({})` and return companies sorted by number of open positions.

### Example 3: Get Job Market Overview

```text
Use @ai-dev-jobs-mcp to show current AI job market statistics.
```

The agent will call `get_stats({})` and return aggregate data on listings, top employers, and role distribution.

### Example 4: Get Full Job Details

```text
Use @ai-dev-jobs-mcp to get the full details for job ID abc123.
```

The agent will call `get_job({ id: "abc123" })` and return the complete listing with requirements and application link.

## Best Practices

- Use `search_jobs` with specific keywords for targeted results rather than broad queries
- Use `list_companies` to discover companies, then `search_jobs` filtered by company name for focused searches
- Use `get_stats` to provide users with market context before diving into specific listings
- Combine with resume or cover letter skills to create end-to-end job application workflows

## Limitations

- The index covers AI and ML roles specifically; general software engineering jobs outside the AI space may not be included.
- Job listings are refreshed regularly but may have a short delay before new postings appear.
- Salary data is available when companies provide it; not all listings include salary information.

## Related Skills

- `@not-human-search-mcp` - Discover AI-ready tools and APIs via MCP
- `@mcp-builder` - For building your own MCP servers

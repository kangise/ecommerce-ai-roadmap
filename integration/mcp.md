# MCP Server Integration Guide

## Why MCP

The Model Context Protocol (MCP) is the natural fit for this infrastructure. This repo includes a **dedicated MCP server** (`integration/mcp-server.py`) — not just a file pointer.

## Quick Start

### Option A: Dedicated MCP Server (recommended)

```json
{
  "mcpServers": {
    "opc-ecommerce": {
      "command": "python3",
      "args": ["/path/to/ecommerce-ai-skills/integration/mcp-server.py", "--dist", "/path/to/ecommerce-ai-skills/dist"]
    }
  }
}
```

The dedicated server exposes:

| Interface | What it does |
|-----------|-------------|
| **Resources** | 7 read-only data sources (ontology, knowledge, glossary) |
| **Tools** | 4 callable tools (route_query, get_constraints, search_knowledge, list_skills) |
| **Prompts** | 9 domain skill prompt templates |

### Option B: Filesystem Server (fallback)

If you don't have Python in the MCP environment:

```json
{
  "mcpServers": {
    "opc-ecommerce": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/ecommerce-ai-skills/dist"]
    }
  }
}
```

This gives file-level access but no tool/resource/prompt schema.

### Option C: Direct File Loading

If you don't have an MCP server at all:

1. Read `SKILL.md` as the system prompt
2. Parse `ontology.json` for domain knowledge
3. Match user requests to skill names via the `routing:` table in SKILL.md frontmatter
4. Load the matched skill's manifest.yaml for input/output schema
5. Select a prompt from playbook.md

## Dedicated Server Resources

| URI | Returns |
|-----|---------|
| `opc://ontology/entities` | 94 domain entities (JSON) |
| `opc://ontology/constraints` | 184 platform constraints (JSON) |
| `opc://ontology/relations` | 78 entity relationships (JSON) |
| `opc://ontology/platforms` | 15 marketplace registry (JSON) |
| `opc://ontology/processes` | 8 business processes (JSON) |
| `opc://knowledge/index` | 69-chapter structured index (JSON) |
| `opc://glossary` | Trilingual term definitions (Markdown) |

## Dedicated Server Tools

### `opc.route_query`
Routes a natural-language user query to the best-matching skill.
Returns: skill name, description, required inputs, expected outputs, platform list.

### `opc.get_constraints`
Filters constraints by platform and/or entity.
Returns: JSON array of matching constraints with values, units, and source anchors.

### `opc.search_knowledge`
Searches the 69-chapter knowledge index by text or entity ID.
Returns: top 10 matching chapters with summaries and entity cross-references.

### `opc.list_skills`
Lists all 9 domain skills with their full manifests (I/O schema, triggers, platforms).

## Testing

```bash
# CLI test mode (no MCP client needed)
python3 integration/mcp-server.py --cli
```

## File Reference

| File | Purpose | Format |
|------|---------|--------|
| `SKILL.md` | Agent system prompt + routing | Markdown with YAML frontmatter |
| `ontology.json` | Domain model | JSON |
| `prompts.json` | Prompt library | JSON |
| `knowledge/index.json` | Chapter index | JSON |
| `skills/*/manifest.yaml` | Skill schemas | YAML |
| `skills/*/references/playbook.md` | Prompt templates | Markdown |
| `skills/*/references/constraints.md` | Platform rules | Markdown |
| `skills/*/references/boundaries.md` | Limitations | Markdown |

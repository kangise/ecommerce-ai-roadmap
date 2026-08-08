# MCP Server Integration Guide

## Why MCP

The Model Context Protocol (MCP) is the natural fit for this infrastructure:

```
ontology.json  → MCP Resources   (domain knowledge, read-only)
prompts.json   → MCP Prompts     (reusable prompt templates)
skills/        → MCP Tools       (executable capabilities)
```

## Quick Start

1. Point your MCP client to the `dist/` directory
2. The MCP server exposes:
   - **Resources**: `ontology://entities`, `ontology://constraints`, `knowledge://index`
   - **Prompts**: All 812 prompts, filterable by domain
   - **Tools**: 7 domain tools (`ecom-listing`, `ecom-advertising`, etc.)

3. For Claude Desktop, add to your claude_desktop_config.json:
```json
{
  "mcpServers": {
    "opc-ecommerce": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/opc/dist"]
    }
  }
}
```

## Without an MCP Server

If you don't have an MCP server, load the files directly:

1. Read `SKILL.md` as the system prompt
2. Parse `ontology.json` for domain knowledge
3. Match user requests to skill names via the `routing:` table in SKILL.md frontmatter
4. Load the matched skill's manifest (skills/\<skill\>/manifest.yaml) for input/output schema
5. Select a prompt from the skill's playbook (skills/\<skill\>/references/playbook.md)

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

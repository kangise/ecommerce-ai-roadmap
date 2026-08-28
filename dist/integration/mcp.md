# MCP Server Integration Guide

## Why MCP

The Model Context Protocol (MCP) is the natural fit for this infrastructure. This repo includes a **dedicated MCP server** (`integration/mcp-server.py`) — not just a file pointer.

## Quick Start

### Option A: Dedicated MCP Server (recommended)

Install the optional MCP extra with the pinned v1 SDK used by this server:

```bash
python3 -m pip install "ecommerce-ai-skills[mcp] @ git+https://github.com/kangise/ecommerce-ai-skills"
```

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
| **Resources** | 8 read-only data sources (ontology, knowledge bodies, glossary) |
| **Tools** | 5 callable tools (route_query, constraints, search, chapter read, skills) |
| **Prompts** | 9 domain skill prompt templates |

### Connecting a live runtime (optional)

The knowledge tools can tell an agent what to do about a 40% ACOS. They cannot
tell it what the ACOS *is* — that lives in the runtime, behind a tenant and an
API key. Point the server at a running instance and four read-only ops tools
appear alongside the knowledge ones:

```json
{
  "mcpServers": {
    "opc-ecommerce": {
      "command": "python3",
      "args": ["/path/to/ecommerce-ai-skills/integration/mcp-server.py", "--dist", "/path/to/ecommerce-ai-skills/dist"],
      "env": {
        "OPC_RUNTIME_URL": "http://127.0.0.1:8788",
        "OPC_RUNTIME_API_KEY": "eai_..."
      }
    }
  }
}
```

| Tool | Reads |
|------|-------|
| `opc.ops_briefing` | Executive summary, priorities, risks, agent status, what awaits approval |
| `opc.ops_metrics` | Metric observations, each carrying the evidence import it came from |
| `opc.ops_proposals` | Proposed actions and their approval state |
| `opc.ops_evidence` | What real evidence has been imported, and its observation window |

**Read-only, deliberately.** The runtime's safety story is that writes go
proposal -> human approval -> execution. Exposing approve or execute over MCP
would hand a model the key to the gate that exists to keep it out. An agent can
see what is pending; a person still approves it in the UI.

Leave the two variables unset and these tools do not appear at all — the
knowledge surface is unchanged. Setting only one of them counts as unset, since
a URL with no key would fail on every call. Check which mode you are in with:

```bash
python3 integration/mcp-server.py --validate
```

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
| `opc://ontology/entities` | 100 domain entities (JSON) |
| `opc://ontology/constraints` | 322 platform constraints (JSON) |
| `opc://ontology/relations` | 78 entity relationships (JSON) |
| `opc://ontology/platforms` | 15 marketplace registry (JSON) |
| `opc://ontology/processes` | 8 business processes (JSON) |
| `opc://knowledge/index` | 69-chapter structured index (JSON) |
| `opc://knowledge/chapter/{id}` | Full text for an id returned by the index |
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

### `opc.read_chapter`
Reads the complete chapter body for an ID returned by the knowledge index or search.

### `opc.list_skills`
Lists all 9 domain skills with their full manifests (I/O schema, triggers, platforms).

## Testing

```bash
# CLI test mode (no MCP client needed)
python3 integration/mcp-server.py --cli
python3 integration/mcp-server.py --validate
```

The MCP adapter is deliberately read-only. It does not authenticate tenants,
write marketplace data, or claim to be a remote HTTP MCP endpoint. Use the
authenticated runtime API for persisted actions and connectors, documented in
[`integration/runtime-api.md`](runtime-api.md).

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

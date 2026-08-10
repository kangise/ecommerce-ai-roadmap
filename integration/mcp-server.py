#!/usr/bin/env python3
"""OPC E-Commerce MCP Server.

Exposes the OPC infrastructure as MCP resources, tools, and prompts.
Run standalone or configure in Claude Desktop / Cursor / MCP client.

Usage:
    python3 integration/mcp-server.py [--dist path/to/dist]

Claude Desktop config (~/Library/Application Support/Claude/claude_desktop_config.json):
    {
      "mcpServers": {
        "opc-ecommerce": {
          "command": "python3",
          "args": ["--dist", "/path/to/ecommerce-ai-roadmap/dist"]
        }
      }
    }

Resources (read-only data the agent can query):
    opc://ontology/entities        — 94 e-commerce domain entities
    opc://ontology/constraints      — 184 platform constraints
    opc://ontology/relations        — 78 entity relationships
    opc://ontology/platforms       — 15 marketplaces
    opc://ontology/processes       — 8 business processes
    opc://knowledge/index           — 69-chapter structured index
    opc://prompts?skill=<id>        — Filtered prompt library
    opc://glossary                   — Trilingual term definitions

Tools (callable capabilities):
    opc.route_query        — Route a user query to the appropriate skill
    opc.get_constraints    — Get constraints for a specific platform/entity
    opc.search_knowledge   — Search knowledge index by entity or keyword
    opc.list_skills        — List all available skills with their manifests

Prompts (reusable prompt templates):
    opc.prompt.<skill_id>  — Prompt templates per domain skill
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import yaml
from pathlib import Path
from typing import Any

# MCP SDK — falls back to stdio JSON-RPC if mcp package is unavailable
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Resource, Tool, Prompt, TextContent, ImageContent
    HAS_MCP = True
except ImportError:
    HAS_MCP = False


class OPCServer:
    """OPC MCP Server — exposes e-commerce infrastructure to AI agents."""

    def __init__(self, dist_path: str | Path):
        self.dist = Path(dist_path).resolve()
        self._ontology = self._load_json("ontology.json")
        self._prompts = self._load_json("prompts.json")
        self._knowledge = self._load_json("knowledge/index.json")
        self._skills = self._load_skills()
        self._glossary = self._load_text("references/glossary.md")
        self._skill_md = self._load_text("SKILL.md")
        self._routing_rules = self._build_routing_rules()

    def _load_json(self, name: str) -> Any:
        p = self.dist / name
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
        return {}

    def _load_text(self, name: str) -> str:
        p = self.dist / name
        if p.exists():
            return p.read_text(encoding="utf-8")
        return ""

    def _load_skills(self) -> dict[str, dict]:
        skills = {}
        skills_dir = self.dist / "skills"
        if not skills_dir.exists():
            return skills
        for sd in sorted(skills_dir.iterdir()):
            if not sd.is_dir():
                continue
            mf = sd / "manifest.yaml"
            if not mf.exists():
                continue
            try:
                manifest = yaml.safe_load(mf.read_text(encoding="utf-8"))
                sid = manifest.get("name", sd.name)
                skills[sid] = {
                    "manifest": manifest,
                    "playbook": self._read(sd / "references" / "playbook.md"),
                    "constraints": self._read(sd / "references" / "constraints.md"),
                    "boundaries": self._read(sd / "references" / "boundaries.md"),
                }
            except Exception:
                continue
        return skills

    @staticmethod
    def _read(p: Path) -> str:
        return p.read_text(encoding="utf-8") if p.exists() else ""

    def _build_routing_rules(self) -> list[dict]:
        """Build routing rules from skill manifests."""
        rules = []
        for sid, data in self._skills.items():
            mf = data.get("manifest", {})
            triggers = mf.get("triggers", {})
            keywords = triggers.get("keywords", []) if isinstance(triggers, dict) else []
            rules.append({
                "skill": sid,
                "keywords": keywords,
                "description": mf.get("description", ""),
                "platforms": mf.get("platforms", []),
            })
        return rules

    # -- Resources --

    def list_resources(self) -> list[dict]:
        resources = [
            {"uri": "opc://ontology/entities", "name": "E-commerce entities",
             "description": f"{len(self._ontology.get('entities', []))} domain entities with attributes and sources"},
            {"uri": "opc://ontology/constraints", "name": "Platform constraints",
             "description": f"{len(self._ontology.get('constraints', []))} platform-specific rules"},
            {"uri": "opc://ontology/relations", "name": "Entity relations",
             "description": f"{len(self._ontology.get('relations', []))} entity relationships"},
            {"uri": "opc://ontology/platforms", "name": "Marketplace registry",
             "description": f"{len(self._ontology.get('platforms', []))} e-commerce platforms"},
            {"uri": "opc://ontology/processes", "name": "Business processes",
             "description": f"{len(self._ontology.get('processes', []))} formal workflows"},
            {"uri": "opc://knowledge/index", "name": "Knowledge index",
             "description": f"{len(self._knowledge)} chapter summaries with entity cross-refs"},
            {"uri": "opc://glossary", "name": "Trilingual glossary",
             "description": "E-commerce term definitions in zh/en/ja"},
        ]
        return resources

    def read_resource(self, uri: str) -> str:
        if uri == "opc://ontology/entities":
            return json.dumps(self._ontology.get("entities", []), ensure_ascii=False, indent=2)
        elif uri == "opc://ontology/constraints":
            return json.dumps(self._ontology.get("constraints", []), ensure_ascii=False, indent=2)
        elif uri == "opc://ontology/relations":
            return json.dumps(self._ontology.get("relations", []), ensure_ascii=False, indent=2)
        elif uri == "opc://ontology/platforms":
            return json.dumps(self._ontology.get("platforms", []), ensure_ascii=False, indent=2)
        elif uri == "opc://ontology/processes":
            return json.dumps(self._ontology.get("processes", []), ensure_ascii=False, indent=2)
        elif uri == "opc://knowledge/index":
            return json.dumps(self._knowledge, ensure_ascii=False, indent=2)
        elif uri == "opc://glossary":
            return self._glossary
        return f"Unknown resource: {uri}"

    # -- Tools --

    def list_tools(self) -> list[dict]:
        return [
            {
                "name": "opc.route_query",
                "description": "Route a user query to the appropriate e-commerce skill",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "User's natural language query"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "opc.get_constraints",
                "description": "Get platform constraints for a specific entity or platform",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "platform": {"type": "string", "description": "Platform ID (amazon, shopify, etc.)"},
                        "entity": {"type": "string", "description": "Entity ID (listing, campaign, etc.)"}
                    }
                }
            },
            {
                "name": "opc.search_knowledge",
                "description": "Search the knowledge index by entity or keyword",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "entity": {"type": "string", "description": "Filter by entity ID"}
                    }
                }
            },
            {
                "name": "opc.list_skills",
                "description": "List all available domain skills with their manifests",
                "inputSchema": {"type": "object", "properties": {}}
            },
        ]

    def call_tool(self, name: str, args: dict) -> str:
        if name == "opc.route_query":
            return self._route_query(args.get("query", ""))
        elif name == "opc.get_constraints":
            return self._get_constraints(args.get("platform"), args.get("entity"))
        elif name == "opc.search_knowledge":
            return self._search_knowledge(args.get("query", ""), args.get("entity"))
        elif name == "opc.list_skills":
            return self._list_skills()
        return f"Unknown tool: {name}"

    def _route_query(self, query: str) -> str:
        """Route a user query to the best-matching skill."""
        query_lower = query.lower()
        best_match = None
        best_score = 0

        # Check applicability first (high priority)
        app_keywords = self._skills.get("ecom-applicability", {}).get("manifest", {}).get("triggers", {}).get("keywords", [])
        app_score = sum(1 for kw in app_keywords if len(kw) >= 3 and kw.lower() in query_lower)

        for rule in self._routing_rules:
            if rule["skill"] == "ecom-applicability":
                continue
            score = sum(1 for kw in rule["keywords"] if kw.lower() in query_lower)
            if score > best_score:
                best_score = score
                best_match = rule["skill"]

        if app_score >= 2 and best_score < 2:
            best_match = "ecom-applicability"
        elif app_score >= 3 and best_score < 3:
            best_match = "ecom-applicability"
        elif not best_match and app_score >= 1:
            best_match = "ecom-applicability"

        if not best_match:
            return json.dumps({"error": "No skill matches this query", "query": query}, ensure_ascii=False)

        skill = self._skills.get(best_match, {})
        manifest = skill.get("manifest", {})
        return json.dumps({
            "query": query,
            "skill": best_match,
            "description": manifest.get("description", ""),
            "inputs": manifest.get("inputs", []),
            "outputs": manifest.get("outputs", []),
            "platforms": manifest.get("platforms", []),
            "constraints_ref": f"Read skill constraints via opc.get_constraints",
            "playbook_ref": f"Use prompts from skills/{best_match}/references/playbook.md",
        }, ensure_ascii=False, indent=2)

    def _get_constraints(self, platform: str | None, entity: str | None) -> str:
        constraints = self._ontology.get("constraints", [])
        filtered = []
        for c in constraints:
            if platform and c.get("platform") != platform:
                continue
            if entity and entity not in c.get("id", ""):
                continue
            filtered.append(c)
        return json.dumps(filtered, ensure_ascii=False, indent=2)

    def _search_knowledge(self, query: str, entity: str | None) -> str:
        results = []
        # Normalize query: "buy box" → also match "buy_box"
        query_norm = query.lower().replace(" ", "_")
        query_lower = query.lower()
        for entry in self._knowledge:
            if entity and entity not in entry.get("key_entities", []):
                continue
            text = (entry.get("summary", "") + " " + entry.get("title", "")).lower()
            key_entities = [e.lower() for e in entry.get("key_entities", [])]
            if (query_lower in text or query_norm in text or
                query_norm in key_entities or
                not query):
                results.append(entry)
        return json.dumps(results[:10], ensure_ascii=False, indent=2)

    def _list_skills(self) -> str:
        skills_info = []
        for sid, data in self._skills.items():
            mf = data.get("manifest", {})
            skills_info.append({
                "name": sid,
                "description": mf.get("description", ""),
                "platforms": mf.get("platforms", []),
                "triggers": mf.get("triggers", {}),
                "inputs": mf.get("inputs", []),
                "outputs": mf.get("outputs", []),
            })
        return json.dumps(skills_info, ensure_ascii=False, indent=2)

    # -- Prompts --

    def list_prompts(self) -> list[dict]:
        prompts = []
        for sid in sorted(self._skills.keys()):
            prompts.append({
                "name": f"opc.prompt.{sid}",
                "description": f"Prompt templates for {sid}",
            })
        return prompts

    def get_prompt(self, name: str) -> str:
        # Extract skill ID from prompt name
        m = re.match(r"opc\.prompt\.(.+)", name)
        if not m:
            return f"Unknown prompt: {name}"
        sid = m.group(1)
        skill = self._skills.get(sid)
        if not skill:
            return f"Skill not found: {sid}"
        return skill.get("playbook", f"No playbook for {sid}")


# -- MCP Server (if mcp package available) --

def run_mcp_server(server: OPCServer):
    """Run as a real MCP server using the mcp SDK."""
    import asyncio
    from mcp.server import Server
    from mcp.server.stdio import stdio_server

    app = Server("opc-ecommerce")

    @app.list_resources()
    async def list_resources() -> list[Resource]:
        return [
            Resource(uri=r["uri"], name=r["name"], description=r["description"])
            for r in server.list_resources()
        ]

    @app.read_resource()
    async def read_resource(uri: str) -> str:
        return server.read_resource(uri)

    @app.list_tools()
    async def list_tools() -> list[Tool]:
        tools = server.list_tools()
        return [
            Tool(
                name=t["name"],
                description=t["description"],
                inputSchema=t["inputSchema"],
            )
            for t in tools
        ]

    @app.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        result = server.call_tool(name, arguments)
        return [TextContent(type="text", text=result)]

    @app.list_prompts()
    async def list_prompts() -> list[Prompt]:
        return [
            Prompt(name=p["name"], description=p["description"])
            for p in server.list_prompts()
        ]

    @app.get_prompt()
    async def get_prompt(name: str, arguments: dict) -> str:
        return server.get_prompt(name)

    async def main():
        async with stdio_server() as (read_stream, write_stream):
            await app.run(read_stream, write_stream, app.create_initialization_options())

    asyncio.run(main())


# -- CLI mode (for testing without MCP SDK) --

def run_cli(server: OPCServer):
    """Interactive CLI for testing the server without an MCP client."""
    print(f"OPC MCP Server (CLI mode)")
    print(f"  dist: {server.dist}")
    print(f"  skills: {len(server._skills)}")
    print(f"  prompts: {len(server._prompts)}")
    print(f"  knowledge entries: {len(server._knowledge)}")
    print(f"\nResources: {len(server.list_resources())}")
    for r in server.list_resources():
        print(f"  {r['uri']}: {r['description']}")
    print(f"\nTools: {len(server.list_tools())}")
    for t in server.list_tools():
        print(f"  {t['name']}: {t['description']}")
    print(f"\nPrompts: {len(server.list_prompts())}")

    print("\n--- Route Test ---")
    test_queries = [
        "帮我写一个Amazon蓝牙耳机的标题和五点描述",
        "我的广告ACOS涨到40%了怎么办",
        "我该不该用AI做需求预测",
        "FBA库存快断了应该什么时候补货",
        "这个产品卖到欧盟需要什么认证",
    ]
    for q in test_queries:
        result = server._route_query(q)
        data = json.loads(result)
        print(f"  '{q[:40]}' → {data.get('skill', 'NONE')}")

    print("\n--- Constraint Test ---")
    amazon_listing = server._get_constraints("amazon", "listing")
    constraints = json.loads(amazon_listing)
    print(f"  Amazon listing constraints: {len(constraints)}")
    for c in constraints[:3]:
        print(f"    {c.get('id')}: {c.get('statement', {}).get('zh', '')[:60]}")

    print("\n--- Knowledge Search ---")
    results = json.loads(server._search_knowledge("buy box", None))
    print(f"  Search 'buy box': {len(results)} results")
    for r in results[:3]:
        print(f"    {r.get('title', '')[:60]}")


def main():
    parser = argparse.ArgumentParser(description="OPC E-Commerce MCP Server")
    parser.add_argument("--dist", default="dist", help="Path to dist/ directory")
    parser.add_argument("--cli", action="store_true", help="Run in CLI test mode")
    args = parser.parse_args()

    dist_path = Path(args.dist).resolve()
    if not dist_path.exists():
        print(f"Error: dist/ directory not found at {dist_path}", file=sys.stderr)
        print("Run: python3 scripts/build_dist.py", file=sys.stderr)
        sys.exit(1)

    server = OPCServer(dist_path)

    if args.cli or not HAS_MCP:
        if not HAS_MCP and not args.cli:
            print("mcp package not installed — running in CLI mode", file=sys.stderr)
        run_cli(server)
    else:
        run_mcp_server(server)


if __name__ == "__main__":
    main()

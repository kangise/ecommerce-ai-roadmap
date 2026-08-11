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
          "args": ["--dist", "/path/to/ecommerce-ai-skills/dist"]
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
             "description": f"{len(self._knowledge)} chapter summaries with entity cross-refs — "
                            f"a router, not an answer; follow body_path for the text"},
            {"uri": "opc://knowledge/chapter/{id}", "name": "Chapter full text",
             "description": f"Full text of any of the {len(self._knowledge)} chapters "
                            f"({sum(e.get('body_chars', 0) for e in self._knowledge):,} chars total). "
                            f"Ids come from the index."},
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
        elif uri.startswith("opc://knowledge/chapter/"):
            return self._read_chapter(uri[len("opc://knowledge/chapter/"):])
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
                "description": "Search chapter titles, summaries AND full bodies by keyword. "
                               "Results marked match=body include line excerpts. Use this "
                               "before concluding the package does not cover a topic.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "entity": {"type": "string", "description": "Filter by entity ID"}
                    }
                }
            },
            {
                "name": "opc.read_chapter",
                "description": "Read the full text of one chapter. Pass the `id` from a "
                               "search result or the knowledge index.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "chapter_id": {"type": "string",
                                       "description": "Chapter id, e.g. a-operators__a6-compliance"}
                    },
                    "required": ["chapter_id"]
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
        elif name == "opc.read_chapter":
            return self._read_chapter(args.get("chapter_id", ""))
        elif name == "opc.list_skills":
            return self._list_skills()
        return f"Unknown tool: {name}"

    @staticmethod
    def _norm(text: str) -> str:
        """Fold case and drop all whitespace before matching.

        Trigger 「AI做」 failed to match the query 「能用 AI 做补货预测吗」 — one
        space. ecom-applicability scored 0 and ecom-inventory took a question
        that was explicitly about whether to use AI at all.
        """
        return re.sub(r"\s+", "", text).lower()

    def _query_terms(self, query: str) -> set[str]:
        """Candidate terms for coverage lookup: ASCII words + CJK n-grams."""
        q = self._norm(query)
        terms = set(re.findall(r"[a-z0-9]{3,}", q))
        for run in re.findall(r"[\u4e00-\u9fff]{2,}", q):
            for n in (2, 3, 4):
                for i in range(len(run) - n + 1):
                    terms.add(run[i:i + n])
        return terms

    def _constraint_coverage(self, skill_id: str, query: str) -> int:
        """How many query terms appear in constraints this skill actually uses.

        Zero means the router picked a skill that holds nothing relevant. Asked
        about Amazon video-ad caption rules, the router returned
        ecom-advertising with full confidence; the package has no such rule
        (「字幕」 appears in 0 constraints). The agent then had to either admit
        the gap on its own or invent policy. Surfacing the count moves that
        decision out of the agent's judgment.
        """
        manifest = self._skills.get(skill_id, {}).get("manifest", {}) or {}
        used = set(manifest.get("uses_constraints") or [])
        if not used:
            return 0
        haystack = []
        for c in self._ontology.get("constraints", []):
            if c.get("id") not in used:
                continue
            stmt = c.get("statement", {}) or {}
            haystack.append(self._norm(" ".join([
                str(c.get("id", "")), str(c.get("attribute", "")), str(c.get("value", "")),
                str(stmt.get("zh", "")), str(stmt.get("en", "")),
            ])))
        if not haystack:
            return 0
        return sum(1 for t in self._query_terms(query) if any(t in h for h in haystack))

    def _score_skills(self, query: str) -> list[tuple[str, int]]:
        qn = self._norm(query)
        scored = []
        for rule in self._routing_rules:
            score = sum(1 for kw in rule["keywords"] if kw and self._norm(kw) in qn)
            if score:
                scored.append((rule["skill"], score))
        scored.sort(key=lambda x: (-x[1], x[0]))
        return scored

    def _route_query(self, query: str) -> str:
        """Route a user query to the best-matching skill.

        Reports ambiguity and coverage instead of always returning one
        confident answer. All three behaviours here come from observed
        acceptance failures, not from design taste.
        """
        scored = self._score_skills(query)
        scores = dict(scored)
        app_score = scores.get("ecom-applicability", 0)
        domain = [(s, n) for s, n in scored if s != "ecom-applicability"]
        best_match, best_score = (domain[0] if domain else (None, 0))

        # Applicability asks "should AI do this at all". On a tie it wins: a
        # question that reaches for the domain skill's vocabulary while also
        # asking whether AI is usable is the applicability case. 「我只有 7 天
        # 数据，能用 AI 做补货预测吗」 scored 2/2 against ecom-inventory and
        # went to inventory, which answered the forecasting question instead
        # of the "you do not have enough data" question. A lone stray hit
        # still must not beat a well-matched domain question.
        if app_score >= 2 and app_score >= best_score:
            best_match, best_score = "ecom-applicability", app_score
        elif not best_match and app_score >= 1:
            best_match, best_score = "ecom-applicability", app_score

        if not best_match:
            return json.dumps({
                "query": query,
                "skill": None,
                "confidence": "none",
                "reason": "No skill triggers matched.",
                "next": "Ask the user to restate, or call opc.search_knowledge "
                        "to check whether the package covers this topic at all.",
            }, ensure_ascii=False, indent=2)

        # Dual intent. 「这个品类能不能做？可以的话帮我写 Listing」 is two
        # requests; returning only the higher scorer silently dropped the
        # feasibility half, which the routing table says should be clarified.
        #
        # Requires the runner-up to score >= 2, not merely to tie. At 1-vs-1
        # a tie is noise: one incidental keyword each. 「供应商 lead time 25 天，
        # 我该备多少货」 tied ecom-inventory against ecom-research on one hit
        # apiece and got reported as ambiguous, which it is not.
        rivals = [(s, n) for s, n in scored
                  if s != best_match and n >= 2 and best_score - n < 2]
        coverage = self._constraint_coverage(best_match, query)
        if rivals and coverage > 0:
            return json.dumps({
                "query": query,
                "skill": best_match,
                "confidence": "ambiguous",
                "matched_constraints_count": coverage,
                "candidates": [{"skill": s, "score": n}
                               for s, n in [(best_match, best_score)] + rivals],
                "reason": "Two or more skills score within 1 point. This is "
                          "usually a multi-intent request.",
                "next": "Ask the user which they want first, or handle the "
                        "candidates in sequence — do not silently drop one.",
            }, ensure_ascii=False, indent=2)

        skill = self._skills.get(best_match, {})
        manifest = skill.get("manifest", {})
        result = {
            "query": query,
            "skill": best_match,
            "confidence": "low" if coverage == 0 else "ok",
            "trigger_score": best_score,
            "matched_constraints_count": coverage,
            "description": manifest.get("description", ""),
            "inputs": manifest.get("inputs", []),
            "outputs": manifest.get("outputs", []),
            "platforms": manifest.get("platforms", []),
            "constraints_ref": "Read skill constraints via opc.get_constraints",
            "playbook_ref": f"Use prompts from skills/{best_match}/references/playbook.md",
        }
        if coverage == 0:
            result["reason"] = (
                f"Triggers matched {best_match}, but none of this query's terms "
                f"appear in the constraints that skill uses. The package may not "
                f"cover this specific rule."
            )
            result["next"] = (
                "Call opc.search_knowledge before answering. If that is also "
                "empty, say the package does not cover it. Do not supply the "
                "rule from your own knowledge."
            )
        return json.dumps(result, ensure_ascii=False, indent=2)

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

    def _read_chapter(self, chapter_id: str) -> str:
        """Return the full text of one chapter by id."""
        for entry in self._knowledge:
            if entry.get("id") == chapter_id or entry.get("path") == chapter_id:
                body_rel = entry.get("body_path", "")
                if not body_rel:
                    return f"Chapter '{chapter_id}' has no body in this package."
                body_file = self.dist / "knowledge" / body_rel
                if not body_file.exists():
                    return f"Chapter body missing: {body_rel}"
                return body_file.read_text(encoding="utf-8")
        known = ", ".join(e.get("id", "") for e in self._knowledge[:5])
        return f"Unknown chapter '{chapter_id}'. Ids look like: {known}, ..."

    def _search_knowledge(self, query: str, entity: str | None) -> str:
        """Search chapter bodies, not just the index.

        Searching summary+title alone is why a live acceptance run concluded
        the package had no EN 71 content: the term appears in the body of
        a-operators/a6-compliance.md and in no summary. A 300-char summary
        covers under 1% of a chapter, so an index-only miss says almost
        nothing about whether the package covers a topic.
        """
        # Normalize query: "buy box" → also match "buy_box"
        query_norm = query.lower().replace(" ", "_")
        query_lower = query.lower()
        index_hits, body_hits = [], []

        for entry in self._knowledge:
            if entity and entity not in entry.get("key_entities", []):
                continue
            if not query:
                index_hits.append({**entry, "match": "index"})
                continue

            text = (entry.get("summary", "") + " " + entry.get("title", "")).lower()
            key_entities = [e.lower() for e in entry.get("key_entities", [])]
            if query_lower in text or query_norm in text or query_norm in key_entities:
                index_hits.append({**entry, "match": "index"})
                continue

            # Fall through to the body.
            body_rel = entry.get("body_path", "")
            if not body_rel:
                continue
            body_file = self.dist / "knowledge" / body_rel
            if not body_file.exists():
                continue
            body = body_file.read_text(encoding="utf-8")
            body_lower = body.lower()
            if query_lower not in body_lower and query_norm not in body_lower:
                continue

            # Give the caller the surrounding lines so a hit is actionable
            # without reading the whole chapter first.
            excerpts = []
            for i, line in enumerate(body.split("\n")):
                if query_lower in line.lower() or query_norm in line.lower():
                    excerpts.append({"line": i + 1, "text": line.strip()[:300]})
                if len(excerpts) >= 3:
                    break
            body_hits.append({**entry, "match": "body", "excerpts": excerpts})

        # Index matches are stronger signals; body matches follow.
        return json.dumps((index_hits + body_hits)[:10], ensure_ascii=False, indent=2)

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

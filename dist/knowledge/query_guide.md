# Knowledge Index Usage Guide

## For Agent Consumers

The `index.json` contains structured metadata for all 69 source chapters,
and `chapters/` contains their full text.

**The index is a router, not an answer.** Each entry's `summary` is the first
300 characters only. Never answer a factual question from `summary` alone and
never conclude "the package does not cover X" from an index miss — open
`body_path` and read the chapter first. A prior acceptance run reported
"no EN 71 in the package" while the chapter body did contain it.

Use it to answer domain questions:

1. **Question**: "What is Buy Box?"
   → Search index for `key_entities` containing "buy_box" or "price"
   → Return the matching chapter's `title` + `summary`
   → Also check `constraint_refs` for related constraints in `ontology.json`

2. **Question**: "What are Amazon listing requirements?"
   → Search for chapters with "amazon" and "listing" in constraints
   → Return `constraint_refs` and `boundary_summary` for context

3. **Question**: "Should I use AI for demand forecasting?"
   → Search for "inventory" or "forecast" in key_entities
   → Return `boundary_summary` — this is what the ecom-applicability skill uses

## Structure

Each entry:
- `id`: Chapter id — src path with `/` flattened to `__`, no extension
- `title`: Chapter title (first H1)
- `path`: Relative path from src/
- `body_path`: Full chapter text, relative to `knowledge/`. **Read this.**
- `body_chars`: Length of the body, for cost estimation before reading
- `summary`: First 300 characters of prose — routing hint only
- `key_entities`: Entity IDs from ontology that appear in this chapter
- `constraint_refs`: `<!-- ref: -->` markers found in this chapter
- `boundary_summary`: First 200 chars of "When this doesn't work" section

## Full-text search

`summary` covers 300 of ~35,000 characters per chapter, so a keyword absent
from the index is usually still present in the body. Grep `chapters/` before
concluding anything is missing.

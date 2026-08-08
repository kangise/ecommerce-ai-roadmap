#!/usr/bin/env python3
"""Interactive constraint writer with ref location hints.
Usage: python3 scripts/new_constraint.py
"""
import sys, yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def main():
    print("Add a new constraint to ontology/constraints.yaml\n")

    cid = input("Constraint ID (e.g. amazon.listing.title.max_length): ").strip()
    entity = input("Entity ID: ").strip()
    attr = input("Attribute (or empty): ").strip() or None
    platform = input("Platform ID: ").strip()
    kind = input("Kind (max_length/min_length/max_bytes/count/format/forbidden/required): ").strip()
    value_str = input("Value: ").strip()
    try:
        value = int(value_str)
    except ValueError:
        try:
            value = float(value_str)
        except ValueError:
            value = value_str
    unit = input("Unit (字符/字节/... or empty): ").strip() or None
    zh_stmt = input("ZH statement: ").strip()
    en_stmt = input("EN statement: ").strip()
    ja_stmt = input("JA statement: ").strip()
    source = input("Source (e.g. src/a-operators/a2-listing-optimization.md#anchor): ").strip()

    constraint = {
        "id": cid,
        "entity": entity,
        "platform": platform,
        "kind": kind,
        "value": value,
        "statement": {"zh": zh_stmt, "en": en_stmt, "ja": ja_stmt},
        "source": source,
        "verified": "2026-08",
    }
    if attr:
        constraint["attribute"] = attr
    if unit:
        constraint["unit"] = unit

    pf = ROOT / "ontology" / "constraints.yaml"
    constraints = yaml.safe_load(pf.read_text(encoding="utf-8"))
    constraints.append(constraint)
    pf.write_text(yaml.dump(constraints, allow_unicode=True, default_flow_style=False, sort_keys=False))

    print(f"\nAdded constraint '{cid}' to ontology/constraints.yaml")
    print(f"\nNext: add <!-- ref: {cid} --> markers to relevant prompt self-check blocks, run verify_all.py")

if __name__ == "__main__":
    main()

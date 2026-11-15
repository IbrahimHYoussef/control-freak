#!/usr/bin/env python3
"""Sum token usage from Claude Code agent transcripts (JSONL).

Usage: python3 measure.py LABEL=transcript.jsonl [LABEL=transcript.jsonl ...]

Each assistant API response in a transcript carries a `usage` object. A
response can be written as several lines (one per content block), so responses
are de-duplicated by message id before summing.
"""
import json
import sys

FIELDS = (
    "input_tokens",
    "cache_creation_input_tokens",
    "cache_read_input_tokens",
    "output_tokens",
)


def measure(path):
    seen = {}
    for line in open(path, encoding="utf-8"):
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        message = entry.get("message")
        if not isinstance(message, dict) or not message.get("usage"):
            continue
        seen[message.get("id")] = message["usage"]
    totals = {field: 0 for field in FIELDS}
    for usage in seen.values():
        for field in FIELDS:
            totals[field] += usage.get(field) or 0
    totals["api_calls"] = len(seen)
    return totals


def main():
    rows = []
    for arg in sys.argv[1:]:
        label, path = arg.split("=", 1)
        rows.append({"run": label, **measure(path)})
    json.dump(rows, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()

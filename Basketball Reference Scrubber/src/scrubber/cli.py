from __future__ import annotations

import argparse
import sys

from .exceptions import ScrubberError
from .query.engine import QueryEngine
from .query.parser import parse


def main(argv: list[str] | None = None) -> int:
    arg_parser = argparse.ArgumentParser(
        prog="scrubber", description="Basketball Reference Scrubber — natural language NBA stats queries"
    )
    arg_parser.add_argument("query", nargs="+", help="e.g. 'compare LeBron James vs Kevin Durant'")
    args = arg_parser.parse_args(argv)
    text = " ".join(args.query)

    parsed = parse(text)
    print(f"Parsed intent: {parsed.intent.value}")
    print(f"Players: {parsed.players or '-'}")
    print(f"Stats: {parsed.stats or '-'}")
    print(f"Season: {parsed.season or '-'}")

    try:
        result = QueryEngine().run(parsed)
    except ScrubberError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(result.data.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

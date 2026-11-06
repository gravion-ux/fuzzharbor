"""Command-line entry point for FuzzHarbor.

The tool inspects a local directory only. It never launches a fuzzer and never
contacts a remote target.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .corpus import corpus_report
from .crashes import crash_report

EXIT_OK = 0
EXIT_INVALID_INPUT = 1
EXIT_USAGE = 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="fuzzharbor",
        description="Local fuzzing campaign manager and crash triage toolkit.",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (
        ("corpus", "Index a corpus directory and report duplicate content"),
        ("crashes", "Inventory crash artifacts and cluster them by digest"),
    ):
        child = sub.add_parser(name, help=help_text)
        child.add_argument("directory", type=Path)
        child.add_argument("--output", type=Path, help="Optional path for the JSON report")

    args = parser.parse_args(argv)
    if not args.directory.is_dir():
        parser.error("directory must exist")

    if args.command == "corpus":
        report = corpus_report(args.directory)
        report.update({"tool": "FuzzHarbor", "mode": "corpus-index", "schema_version": 1})
    else:
        report = crash_report(args.directory)
        report.update({"tool": "FuzzHarbor", "mode": "crash-triage", "schema_version": 1})

    text = json.dumps(report, indent=2)
    if args.output:
        try:
            args.output.write_text(text + "\n", encoding="utf-8")
        except OSError as exc:
            print(
                f"fuzzharbor: cannot write report to {args.output}: {exc.strerror or exc}",
                file=sys.stderr,
            )
            return EXIT_INVALID_INPUT
    print(text)
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())

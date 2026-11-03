import argparse
import json
from pathlib import Path

from .corpus import index_corpus
from .crashes import inventory_crashes


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command", required=True)
    for name in ("corpus", "crashes"):
        s = sub.add_parser(name); s.add_argument("directory", type=Path)
    args = p.parse_args()
    if not args.directory.is_dir(): p.error("directory must exist")
    result = index_corpus(args.directory) if args.command == "corpus" else inventory_crashes(args.directory)
    print(json.dumps(result, indent=2))

if __name__ == "__main__": main()

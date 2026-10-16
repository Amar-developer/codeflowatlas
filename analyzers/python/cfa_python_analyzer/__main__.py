import argparse
import sys
from pathlib import Path

from cfa_python_analyzer.analyze import analyze


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m cfa_python_analyzer",
        description="Statically analyze a Python repository and print IR JSON. The target code is never imported or run.",
    )
    parser.add_argument("root", type=Path, help="Repository root directory")
    parser.add_argument("--source", help="Source label stored in the IR, such as a repository URL")
    args = parser.parse_args(argv)

    if not args.root.is_dir():
        parser.error(f"{args.root} is not a directory")

    document = analyze(args.root, source=args.source)
    sys.stdout.write(document.model_dump_json(indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
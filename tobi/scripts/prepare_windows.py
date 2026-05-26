#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path


def prepare_windows(source: Path, destination: Path) -> None:
    text = source.read_text(encoding="utf-8")

    def rewrite_block(match: re.Match[str]) -> str:
        attrs, body = match.groups()
        attrs = re.sub(r" \+pty:\d+:\d+", "", attrs or "")
        return f"```bat{attrs}\n{body}```"

    text = re.sub(r"(?ms)^```bash([^\n`]*)\n(.*?)^```", rewrite_block, text)
    destination.write_text(text, encoding="utf-8")
    print(f"Wrote Windows markdown to {destination}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()

    prepare_windows(args.source, args.destination)


if __name__ == "__main__":
    main()

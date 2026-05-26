#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

WINDOWS_SLIDE_BREAK_PATTERN = re.compile(
    r"(?ms)(Build Your Own ROS / C\+\+ / Python Packages\n===\n.*?## Build the package\n.*?<!-- pause -->\n\n)(## Does it work\?)"
)


def prepare_windows(source: Path, destination: Path) -> None:
    text = source.read_text(encoding="utf-8")

    def rewrite_block(match: re.Match[str]) -> str:
        attrs, body = match.groups()
        attrs = re.sub(r" \+pty:\d+:\d+", "", attrs or "")
        body = re.sub(r"^#(?!\!)", "::", body, flags=re.MULTILINE)
        body = re.sub(r"[ \t]*\\\r?\n", " ^\n", body)
        body = body.replace("/dev/null", "NUL")
        return f"```bat{attrs}\n{body}```"

    text = re.sub(r"(?ms)^```bash([^\n`]*)\n(.*?)^```", rewrite_block, text)
    text = WINDOWS_SLIDE_BREAK_PATTERN.sub(r"\1<!-- end_slide -->\n\n\2", text, count=1)
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

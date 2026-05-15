#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Snippet:
    section: str
    key: str
    body: str


SNIPPETS = {
    "start": Snippet(
        section="tasks",
        key="start",
        body='start = { cmd = "python train.py", depends-on = ["download-mnist"] }',
    ),
    "download-mnist": Snippet(
        section="tasks",
        key="download-mnist",
        body=r'''download-mnist = {
  cmd = "python -c 'from torchvision.datasets import MNIST; MNIST(\"data\", download=True)'",
  outputs = ["data/MNIST"]
}''',
    ),
    "pixi-build-preview": Snippet(
        section="workspace",
        key="preview",
        body='preview = ["pixi-build"]',
    ),
    "icra-ros-package": Snippet(
        section="dependencies",
        key="ros-rolling-icra-ros-package",
        body='ros-rolling-icra-ros-package = { path = "icra_ros_package/package.xml" }',
    ),
}


def log(message: str, verbose: bool) -> None:
    if verbose:
        print(message)


def section_pattern(section: str) -> re.Pattern[str]:
    return re.compile(rf"(?m)^\s*\[{re.escape(section)}\]\s*$")


def any_section_pattern() -> re.Pattern[str]:
    return re.compile(r"(?m)^\s*\[[^\]]+\]\s*$")


def key_pattern(key: str) -> re.Pattern[str]:
    bare = re.escape(key)
    double = '"' + re.escape(key) + '"'
    single = "'" + re.escape(key) + "'"
    return re.compile(rf"(?m)^\s*(?:{bare}|{double}|{single})\s*=")


def find_section(text: str, section: str) -> tuple[int, int] | None:
    match = section_pattern(section).search(text)
    if not match:
        return None

    start = match.end()
    next_match = any_section_pattern().search(text, start)
    end = next_match.start() if next_match else len(text)
    return start, end


def has_key_in_section(text: str, snippet: Snippet) -> bool:
    bounds = find_section(text, snippet.section)
    if bounds is None:
        return False

    start, end = bounds
    return key_pattern(snippet.key).search(text[start:end]) is not None


def ensure_section(text: str, section: str) -> str:
    if find_section(text, section) is not None:
        return text

    return text.rstrip() + f"\n\n[{section}]\n"


def add_snippet(text: str, snippet: Snippet, verbose: bool) -> str:
    if has_key_in_section(text, snippet):
        log(f"{snippet.section}.{snippet.key} already present", verbose)
        return text

    text = ensure_section(text, snippet.section)
    bounds = find_section(text, snippet.section)
    assert bounds is not None

    _, end = bounds
    before = text[:end].rstrip()
    after = text[end:]

    log(f"Added {snippet.section}.{snippet.key}", verbose)
    return before + "\n\n" + snippet.body.strip() + "\n" + after


def remove_snippet(text: str, snippet: Snippet, verbose: bool) -> str:
    bounds = find_section(text, snippet.section)
    if bounds is None:
        log(f"Section [{snippet.section}] not present", verbose)
        return text

    start, end = bounds
    before = text[:start]
    section_text = text[start:end]
    after = text[end:]

    lines = section_text.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    removed = False

    while i < len(lines):
        line = lines[i]

        if key_pattern(snippet.key).match(line):
            removed = True

            # One-line assignment, including inline arrays/tables:
            # key = "..."
            # key = ["..."]
            # key = { ... }
            if "{" not in line or "}" in line:
                i += 1
                continue

            # Multi-line table-like value:
            # key = {
            #   ...
            # }
            i += 1
            while i < len(lines):
                if re.match(r"^\s*}\s*$", lines[i]):
                    i += 1
                    break
                i += 1
            continue

        out.append(line)
        i += 1

    log(
        f"Removed {snippet.section}.{snippet.key}" if removed else f"{snippet.section}.{snippet.key} not present",
        verbose,
    )

    updated = before + "".join(out) + after
    return re.sub(r"\n{3,}", "\n\n", updated)


def edit_file(path: Path, action: str, names: list[str], verbose: bool) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else ""

    for name in names:
        snippet = SNIPPETS[name]
        if action == "add":
            text = add_snippet(text, snippet, verbose)
        elif action == "remove":
            text = remove_snippet(text, snippet, verbose)
        else:
            raise ValueError(action)

    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["add", "remove"])
    parser.add_argument("snippets", nargs="+", choices=sorted(SNIPPETS))
    parser.add_argument("--file", default="pixi.toml")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    edit_file(Path(args.file), args.action, args.snippets, args.verbose)


if __name__ == "__main__":
    main()
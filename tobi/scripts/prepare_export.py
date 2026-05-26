#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path


SKIP_EXEC_PATTERNS = (
    "turtlesim_node",
    "ros2 topic pub",
    "remote_demo.py",
    "VSLAM-LAB",
    "orbslam2",
    "icra_ros_package icra_node",
)


def limit_shell_output(body: str, rows: int) -> str:
    hidden_lines: list[str] = []
    visible_lines: list[str] = []

    for line in body.rstrip().splitlines():
        if line.lstrip().startswith("///"):
            hidden_lines.append(line)
        else:
            visible_lines.append(line)

    if not visible_lines:
        return body

    wrapper_start = [
        "/// set -o pipefail",
        "/// {",
    ]
    wrapper_end = [
        f"/// }} 2>&1 | sed -n '1,{rows}p'",
        "",
    ]
    return "\n".join(hidden_lines + wrapper_start + visible_lines + wrapper_end)


def ensure_export_default_colors(text: str, light: bool = False) -> str:
    if not text.startswith("---"):
        return text
    if re.search(r"(?m)^    default:\n      colors:\n        foreground:", text):
        return text

    foreground = "black" if light else "white"
    background = "white" if light else "black"
    return text.replace(
        "  override:\n",
        "  override:\n"
        "    default:\n"
        "      colors:\n"
        f"        foreground: {foreground}\n"
        f"        background: {background}\n\n",
        1,
    )


def prepare_export(source: Path, destination: Path, light: bool = False) -> None:
    text = source.read_text(encoding="utf-8")

    def rewrite_block(match: re.Match[str]) -> str:
        fence, attrs, body = match.groups()
        attrs = attrs or ""
        pty_match = re.search(r" \+pty:\d+:(?P<rows>\d+)", attrs)
        attrs = re.sub(r" \+pty:\d+:\d+", "", attrs)

        has_exec = re.search(r" \+exec(?::[A-Za-z0-9_-]+)?", attrs) is not None
        if has_exec:
            if any(pattern in body for pattern in SKIP_EXEC_PATTERNS):
                attrs = re.sub(r" \+exec(?::[A-Za-z0-9_-]+)?", "", attrs)
            else:
                if pty_match:
                    body = limit_shell_output(body, int(pty_match.group("rows")))
                if "+auto_exec" not in attrs:
                    attrs += " +auto_exec"

        return f"{fence}{attrs}\n{body}```"

    text = re.sub(r"(?ms)^(```[^\s`]+)([^\n`]*)\n(.*?)^```", rewrite_block, text)
    text = ensure_export_default_colors(text, light=light)
    destination.write_text(text, encoding="utf-8")
    print(f"Wrote export-safe markdown to {destination}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument(
        "--theme",
        choices=["dark", "light"],
        default="dark",
        help="Colour theme for exported slides: dark (white-on-black) or light (black-on-white). Default: dark.",
    )
    args = parser.parse_args()

    prepare_export(args.source, args.destination, light=(args.theme == "light"))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
from pathlib import Path


def vnc_lite_url() -> str:
    codespace_name = os.getenv("CODESPACE_NAME")
    if codespace_name:
        return f"https://{codespace_name}-6080.app.github.dev/vnc_lite.html"
    return "https://<your-codespace-name>-6080.app.github.dev/vnc_lite.html"


def transform_codespaces_markdown(text: str) -> str:
    updated = text

    updated = re.sub(
        r"(?m)^-\s*`?(?:control|ctrl)`?\s*\+\s*`?e`?:\s*run code\s*$",
        "- `e`: run code",
        updated,
        count=1,
        flags=re.IGNORECASE,
    )

    updated = re.sub(
        r"(?m)^pixi run demo orbslam2 eth table_3 mono$",
        "DISPLAY=:99 QT_QPA_PLATFORM=xcb LIBGL_ALWAYS_SOFTWARE=1 \\\npixi run demo orbslam2 eth table_3 mono",
        updated,
        count=1,
    )

    turtlesim_anchor = """```bash +exec
pixi run ros2 run turtlesim turtlesim_node
```
"""
    vnc_url = vnc_lite_url()
    turtlesim_note = """
> Codespaces note: turtlesim opens in the virtual desktop on port 6080.
> Open the PORTS tab, then open port 6080 in your browser 
> Direct link: {vnc_url}
> 

""".format(vnc_url=vnc_url)
    turtlesim_note_marker = "> Codespaces note: turtlesim opens in the virtual desktop on port 6080."
    if turtlesim_anchor in updated and turtlesim_note_marker not in updated:
        updated = updated.replace(turtlesim_anchor, turtlesim_anchor + turtlesim_note, 1)

    orbslam_anchor = """```bash +exec +pty:80:6
git clone https://github.com/VSLAM-LAB/VSLAM-LAB.git > /dev/null 2>&1
cd VSLAM-LAB && \
DISPLAY=:99 QT_QPA_PLATFORM=xcb LIBGL_ALWAYS_SOFTWARE=1 \
pixi run demo orbslam2 eth table_3 mono
```
"""
    orbslam_note = """
> Codespaces note: ORB-SLAM also renders in the virtual desktop on port 6080.
> If no window appears, reopen forwarded port 6080 from the PORTS tab 
> Direct link: {vnc_url}

""".format(vnc_url=vnc_url)
    orbslam_note_marker = "> Codespaces note: ORB-SLAM also renders in the virtual desktop on port 6080."
    if orbslam_anchor in updated and orbslam_note_marker not in updated:
        updated = updated.replace(orbslam_anchor, orbslam_anchor + orbslam_note, 1)

    return updated


def prepare_codespaces_markdown(source: Path, destination: Path) -> None:
    text = source.read_text(encoding="utf-8")
    updated = transform_codespaces_markdown(text)

    destination.write_text(updated, encoding="utf-8")
    print(f"Wrote Codespaces markdown to {destination}")


def apply_default_codespaces_markdown() -> None:
    default_markdown = Path(__file__).resolve().parent.parent / "icra_software_tools.md"
    if not default_markdown.exists():
        print(f"default markdown not found at {default_markdown}; skipping markdown update")
        return
    prepare_codespaces_markdown(default_markdown, default_markdown)


def apply_codespaces_bindings(config_file: Path) -> None:
    if not config_file.exists():
        print(f"presenterm config not found at {config_file}; skipping Codespaces overrides")
        return

    text = config_file.read_text(encoding="utf-8")
    updated = text

    execute_code_line = re.compile(r"(?m)^([ \t]*execute_code:[ \t]*)\[.*\][ \t]*$")
    if execute_code_line.search(updated):
        updated = execute_code_line.sub(r'\1["e"]', updated, count=1)
        action = "Applied Codespaces override"
    else:
        bindings_block = re.compile(r"(?m)^([ \t]*)bindings:[ \t]*$")
        match = bindings_block.search(updated)
        if match:
            indent = match.group(1)
            updated = (
                updated[: match.end()]
                + f"\n{indent}  execute_code: [\"e\"]"
                + updated[match.end() :]
            )
            action = "Added Codespaces execute binding"
        else:
            suffix = "\n" if updated.endswith("\n") else "\n\n"
            updated = updated + suffix + "bindings:\n  execute_code: [\"e\"]\n"
            action = "Added bindings block"

    if updated != text:
        config_file.write_text(updated, encoding="utf-8")
    print(f"{action} in {config_file} (execute_code: [\"e\"])")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", nargs="?", type=Path)
    parser.add_argument("destination", nargs="?", type=Path)
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="Update source markdown in place",
    )
    parser.add_argument(
        "--config-file",
        type=Path,
        default=None,
        help="presenterm config file to patch for Codespaces keybinding",
    )
    parser.add_argument(
        "--config-only",
        action="store_true",
        help="Patch presenterm config and apply in-place Codespaces markdown updates",
    )
    args = parser.parse_args()

    if args.config_file is not None:
        apply_codespaces_bindings(args.config_file)

    if args.config_only:
        apply_default_codespaces_markdown()
        return

    if args.in_place:
        if args.source is None:
            parser.error("source is required when --in-place is set")
        prepare_codespaces_markdown(args.source, args.source)
        return

    if args.source is None or args.destination is None:
        parser.error("source and destination are required unless --config-only or --in-place is set")

    prepare_codespaces_markdown(args.source, args.destination)


if __name__ == "__main__":
    main()

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
        r"Run code on a slide with `(?:control|ctrl)` \+ `e`",
        "Run code on a slide with `e`",
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", nargs="?", type=Path)
    parser.add_argument("destination", nargs="?", type=Path)
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="Update source markdown in place",
    )
    args = parser.parse_args()

    if args.in_place:
        if args.source is None:
            parser.error("source is required when --in-place is set")
        prepare_codespaces_markdown(args.source, args.source)
        return

    if args.source is None or args.destination is None:
        parser.error("source and destination are required unless --in-place is set")

    prepare_codespaces_markdown(args.source, args.destination)


if __name__ == "__main__":
    main()

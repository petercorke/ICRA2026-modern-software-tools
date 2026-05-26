#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import shlex
import subprocess
import sys
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
  cmd = "python -c 'from torchvision.datasets import MNIST; MNIST(\"data\", download=True)' 2>/dev/null",
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


def write_export_copy(source: Path, destination: Path) -> None:
    text = source.read_text(encoding="utf-8")

    skip_patterns = (
        "turtlesim_node",
        "ros2 topic pub",
        "remote-demo",
        "VSLAM-LAB",
        "orbslam2",
    )

    def rewrite_block(match: re.Match[str]) -> str:
        fence, attrs, body = match.groups()
        attrs = attrs or ""
        attrs = re.sub(r" \+pty:\d+:\d+", "", attrs)

        has_exec = re.search(r" \+exec(?::[A-Za-z0-9_-]+)?", attrs) is not None
        if has_exec:
            if any(pattern in body for pattern in skip_patterns):
                attrs = re.sub(r" \+exec(?::[A-Za-z0-9_-]+)?", "", attrs)
            elif "+auto_exec" not in attrs:
                attrs += " +auto_exec"

        return f"{fence}{attrs}\n{body}```"

    text = re.sub(r"(?ms)^(```[^\s`]+)([^\n`]*)\n(.*?)^```", rewrite_block, text)
    destination.write_text(text, encoding="utf-8")
    print(f"Wrote export-safe markdown to {destination}")


def remote_host(args: argparse.Namespace) -> str | None:
    host = args.host or os.environ.get("ICRA_REMOTE_HOST")
    if host:
        return host

    print("Remote demo skipped.")
    print("Set ICRA_REMOTE_HOST=zeus to run the presenter-only SSH demo.")
    return None


def remote_path(host: str, remote_dir: str) -> str:
    return f"{host}:{remote_dir}/"


def run_logged(
    command: list[str],
    quiet: bool = False,
    dry_run: bool = False,
    display: str | None = None,
) -> None:
    if display is not None:
        print("$ " + (display or shlex.join(command)), flush=True)
    if dry_run:
        return
    stdout = subprocess.DEVNULL if quiet else None
    stderr = subprocess.DEVNULL if quiet else None
    subprocess.run(command, check=True, stdout=stdout, stderr=stderr)


def ensure_zeus_internet_client(host: str, dry_run: bool) -> None:
    command = (
        "pgrep -f /opt/qutiaclient/IAClient >/dev/null || "
        "(nohup /opt/qutiaclient/IAClient >/tmp/qutiaclient.log 2>&1 &)"
    )
    run_logged(
        ["ssh", host, command],
        dry_run=dry_run,
    )


def remote_demo(args: argparse.Namespace) -> None:
    host = remote_host(args)
    if host is None:
        return

    remote_dir = args.remote_dir

    if args.remote_action == "reset":
        run_logged(
            ["ssh", host, f"rm -rf {remote_dir}"],
            dry_run=args.dry_run,
        )
    elif args.remote_action == "prepare":
        run_logged(
            ["ssh", host, f"mkdir -p {remote_dir}"],
            dry_run=args.dry_run,
            display=f'ssh {host} "mkdir -p {remote_dir}"',
        )
        run_logged(
            ["scp", "-r","pixi.toml", "pixi.lock", "train.py", "icra_ros_package", remote_path(host, remote_dir)],
            dry_run=args.dry_run,
            display=f"scp -r pixi.toml pixi.lock train.py icra_ros_package {remote_path(host, remote_dir)}",
        )
        run_logged(
            [
                "ssh",
                host,
                (
                    f"cd {remote_dir} && "
                    "grep -q 'cuda = \"12\"' pixi.toml || "
                    "printf '\\n[system-requirements]\\ncuda = \"12\"\\n' >> pixi.toml"
                ),
            ],
            dry_run=args.dry_run
        )
    elif args.remote_action == "run":
        ensure_zeus_internet_client(host, args.dry_run)
        run_logged(
            ["ssh", host, f"cd {remote_dir} && pixi add pytorch-gpu -p linux-64"],
            quiet=False,
            dry_run=args.dry_run,
            display=f'ssh {host} "cd {remote_dir} && pixi add pytorch-gpu -p linux-64"',
        )
        run_logged(
            ["ssh", host, f"cd {remote_dir} && pixi run start"],
            dry_run=args.dry_run,
            display=f'ssh {host} "cd {remote_dir} && pixi run start"',
        )
    else:
        raise ValueError(args.remote_action)


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "remote-demo":
        parser = argparse.ArgumentParser()
        parser.add_argument("action", choices=["remote-demo"])
        parser.add_argument("remote_action", choices=["reset", "prepare", "run"])
        parser.add_argument("--host")
        parser.add_argument("--remote-dir", default="~/robotics-demo")
        parser.add_argument("--dry-run", action="store_true")
        args = parser.parse_args()
        remote_demo(args)
        return

    if len(sys.argv) > 1 and sys.argv[1] == "export-copy":
        parser = argparse.ArgumentParser()
        parser.add_argument("action", choices=["export-copy"])
        parser.add_argument("source", type=Path)
        parser.add_argument("destination", type=Path)
        args = parser.parse_args()
        write_export_copy(args.source, args.destination)
        return

    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["add", "remove"])
    parser.add_argument("snippets", nargs="+", choices=sorted(SNIPPETS))
    parser.add_argument("--file", default="pixi.toml")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    edit_file(Path(args.file), args.action, args.snippets, args.verbose)


if __name__ == "__main__":
    main()

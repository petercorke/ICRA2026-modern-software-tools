#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shlex
import subprocess


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
            ["scp", "-r", "pixi.toml", "pixi.lock", "train.py", "icra_ros_package", remote_path(host, remote_dir)],
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
            dry_run=args.dry_run,
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
    parser = argparse.ArgumentParser()
    parser.add_argument("remote_action", choices=["reset", "prepare", "run"])
    parser.add_argument("--host")
    parser.add_argument("--remote-dir", default="~/robotics-demo")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    remote_demo(args)


if __name__ == "__main__":
    main()

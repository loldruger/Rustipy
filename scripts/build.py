#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"
DIST_DIR = ROOT / "dist"


def load_project() -> tuple[str, str]:
    with PYPROJECT.open("rb") as file:
        pyproject = tomllib.load(file)

    project = pyproject["project"]
    return project["name"], project["version"]


def normalize_distribution_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def normalize_wheel_name(name: str) -> str:
    return normalize_distribution_name(name).replace("-", "_")


def find_uv(explicit_path: str | None) -> str:
    candidates = [
        explicit_path,
        shutil.which("uv"),
        str(Path.home() / ".local" / "bin" / "uv"),
    ]

    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate

    raise SystemExit(
        "Could not find uv. Install it first or pass its path with --uv."
    )


def run(command: list[str]) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def capture(command: list[str]) -> str:
    return subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ).stdout.strip()


def clean_dist() -> None:
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)


def verify_artifacts(name: str, version: str) -> None:
    source_name = normalize_distribution_name(name)
    wheel_name = normalize_wheel_name(name)
    expected = [
        DIST_DIR / f"{source_name}-{version}.tar.gz",
        DIST_DIR / f"{wheel_name}-{version}-py3-none-any.whl",
    ]

    missing = [path for path in expected if not path.exists()]
    if missing:
        missing_files = "\n".join(f"  - {path.relative_to(ROOT)}" for path in missing)
        raise SystemExit(f"Build finished, but expected artifacts are missing:\n{missing_files}")

    print(f"Built {name} {version}:", flush=True)
    for path in expected:
        print(f"  - {path.relative_to(ROOT)}", flush=True)


def current_branch() -> str:
    branch = capture(["git", "branch", "--show-current"])
    if not branch:
        raise SystemExit("Cannot release from a detached HEAD.")
    return branch


def ensure_clean_worktree() -> None:
    status = capture(["git", "status", "--porcelain"])
    if status:
        raise SystemExit(
            "Cannot release with uncommitted changes. Commit or stash them first."
        )


def ensure_tag_does_not_exist(tag: str, remote: str) -> None:
    local_tag = capture(["git", "tag", "--list", tag])
    if local_tag:
        raise SystemExit(f"Cannot release: local tag {tag} already exists.")

    remote_tag = capture(["git", "ls-remote", "--tags", remote, tag])
    if remote_tag:
        raise SystemExit(f"Cannot release: remote tag {tag} already exists on {remote}.")


def trigger_release(tag: str, remote: str, dry_run: bool) -> None:
    branch = current_branch()
    commands = [
        ["git", "tag", tag],
        ["git", "push", remote, branch],
        ["git", "push", remote, tag],
    ]

    if dry_run:
        print(f"Release dry run for {tag}:", flush=True)
        for command in commands:
            print("+", " ".join(command), flush=True)
        return

    for command in commands:
        run(command)

    print(f"Release triggered by pushing {tag} to {remote}.", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build distributions using the version from pyproject.toml."
    )
    parser.add_argument(
        "--uv",
        help="Path to the uv executable. Defaults to PATH, then ~/.local/bin/uv.",
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="Do not remove dist/ before building.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Run ruff, ty, and pytest before building.",
    )
    parser.add_argument(
        "--release",
        action="store_true",
        help="Create and push the version tag after building to trigger publishing.",
    )
    parser.add_argument(
        "--remote",
        default="origin",
        help="Git remote to push the release tag to. Defaults to origin.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="With --release, print tag/push commands instead of running them.",
    )
    parser.add_argument(
        "--print-tag",
        action="store_true",
        help="Print the release tag for the pyproject version and exit.",
    )
    args = parser.parse_args()

    name, version = load_project()

    if args.print_tag:
        print(f"v{version}")
        return

    tag = f"v{version}"
    if args.release:
        if not args.dry_run:
            ensure_clean_worktree()
        ensure_tag_does_not_exist(tag, args.remote)

    if args.check or args.release:
        run([sys.executable, "-m", "ruff", "check", "."])
        run([sys.executable, "-m", "ty", "check"])
        run([sys.executable, "-m", "pytest"])

    if not args.no_clean:
        clean_dist()

    uv = find_uv(args.uv)
    print(f"Building {name} {version}", flush=True)
    run([uv, "build"])
    verify_artifacts(name, version)

    if args.release:
        trigger_release(tag, args.remote, args.dry_run)


if __name__ == "__main__":
    main()

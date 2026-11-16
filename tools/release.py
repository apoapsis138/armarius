"""Prepare a release (CONTRIBUTING.md, "A release").

    uv run python tools/release.py 4.15.0

One command over git, towncrier, uv and pytest (a Facade), so a release
is the same steps every time. It checks first and refuses, changing
nothing, unless:

- the working tree is clean;
- after `git fetch`, HEAD is origin/main (on main, or a fresh branch
  from it);
- the version is MAJOR.MINOR.PATCH and newer than pyproject.toml's;
- changelog.d/ has at least one fragment.

Then, on main, it makes the branch release/X.Y.Z; it builds the fragments
into CHANGELOG.md (`towncrier build --yes`, which also deletes them), sets
the version in pyproject.toml, runs `uv lock`, and runs the tests that
hold the changelog and the version together. It never commits or pushes:
it prints what to stage, the commit message, where to open the pull
request, and the tag commands for after the merge.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tomllib
from collections.abc import Callable, Sequence
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPOSITORY = "https://github.com/apoapsis138/armarius"
#: The tests a release must pass before its pull request.
TESTS = (
    "tests/test_version.py",
    "tests/test_changelog.py",
    "tests/test_release_notes.py",
)
#: The files in changelog.d/ that aren't fragments.
NOT_FRAGMENTS = {"README.md", "template.md.jinja"}
_VERSION = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
#: pyproject.toml's version line, the [project] table's first.
_VERSION_LINE = re.compile(r'^version = "[^"]*"$', re.MULTILINE)

#: Runs a command in the repository: its exit code and output.
Run = Callable[[Sequence[str]], subprocess.CompletedProcess[str]]


class ReleaseError(Exception):
    """Why the release stopped; nothing past the checks is undone."""


def runner(root: Path) -> Run:
    def run(command: Sequence[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            list(command),
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

    return run


def parse_version(text: str) -> tuple[int, int, int]:
    match = _VERSION.match(text)
    if not match:
        raise ReleaseError(f"{text!r} isn't a version: give MAJOR.MINOR.PATCH")
    major, minor, patch = (int(n) for n in match.groups())
    return major, minor, patch


def current_version(root: Path) -> str:
    pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    return pyproject["project"]["version"]


def fragments(root: Path) -> list[Path]:
    folder = root / "changelog.d"
    if not folder.is_dir():
        return []
    return sorted(
        p for p in folder.iterdir() if p.is_file() and p.name not in NOT_FRAGMENTS
    )


def _out(run: Run, command: Sequence[str], failure: str) -> str:
    done = run(command)
    if done.returncode != 0:
        detail = (done.stderr or done.stdout).strip()
        raise ReleaseError(f"{failure}: {detail}" if detail else failure)
    return done.stdout.strip()


def check(root: Path, version: str, run: Run) -> str:
    """Refuse unless the release can start; the current branch's name."""
    wanted = parse_version(version)
    if _out(run, ["git", "status", "--porcelain"], "git status failed"):
        raise ReleaseError("the working tree has changes: commit or discard them first")
    _out(run, ["git", "fetch", "origin", "main"], "git fetch failed")
    head = _out(run, ["git", "rev-parse", "HEAD"], "git rev-parse failed")
    main = _out(run, ["git", "rev-parse", "origin/main"], "no origin/main")
    if head != main:
        raise ReleaseError(
            "HEAD isn't origin/main: start from an up-to-date main "
            "(git switch main && git pull)"
        )
    current = current_version(root)
    if wanted <= parse_version(current):
        raise ReleaseError(f"{version} isn't newer than {current}, the current one")
    if not fragments(root):
        raise ReleaseError("changelog.d/ has no fragments: nothing to release")
    return _out(run, ["git", "branch", "--show-current"], "git branch failed")


def set_version(root: Path, version: str) -> None:
    path = root / "pyproject.toml"
    text = path.read_text(encoding="utf-8")
    new, count = _VERSION_LINE.subn(f'version = "{version}"', text, count=1)
    if count != 1:
        raise ReleaseError("pyproject.toml has no version line")
    path.write_text(new, encoding="utf-8", newline="")


def prepare(root: Path, version: str, run: Run) -> str:
    """Make the release's changes; what to do next, to print."""
    branch = check(root, version, run)
    if branch == "main":
        branch = f"release/{version}"
        _out(run, ["git", "switch", "-c", branch], f"couldn't make {branch}")
    _out(
        run,
        ["uv", "run", "towncrier", "build", "--yes", "--version", version],
        "towncrier build failed",
    )
    set_version(root, version)
    _out(run, ["uv", "lock"], "uv lock failed")
    tests = run(["uv", "run", "pytest", "-q", *TESTS])
    if tests.returncode != 0:
        raise ReleaseError(
            "the release's tests failed; nothing is committed, so fix the "
            "changelog or version on this branch and run them again:\n"
            + tests.stdout.strip()
        )
    return next_steps(version, branch, _changed(run))


def _changed(run: Run) -> tuple[list[str], list[str]]:
    """The files to stage, and those already staged for deletion."""
    to_stage: list[str] = []
    deleted: list[str] = []
    # Not _out: its strip would cut the first line's leading status column.
    status = run(["git", "status", "--porcelain"])
    if status.returncode != 0:
        raise ReleaseError("git status failed")
    for line in status.stdout.splitlines():
        if not line.strip():
            continue
        state, path = line[:2], line[3:]
        (deleted if state == "D " else to_stage).append(path)
    return to_stage, deleted


def next_steps(version: str, branch: str, changed: tuple[list[str], list[str]]) -> str:
    to_stage, deleted = changed
    tag = f"v{version}"
    lines = [
        f"Release {version} is ready on {branch}. Nothing is committed.",
        "",
        "1. Look over CHANGELOG.md's new section, then stage and commit:",
        f"   git add {' '.join(to_stage)}",
    ]
    if deleted:
        lines.append(
            f"   (towncrier has already staged {len(deleted)} deleted fragments)"
        )
    lines += [
        f'   git commit -m "Release {version}"',
        "",
        "2. Push the branch and open the pull request into main:",
        f"   git push -u origin {branch}",
        f"   {REPOSITORY}/compare/main...{branch}?expand=1",
        "",
        "3. Once it has merged, tag the merge commit on main:",
        "   git switch main",
        "   git pull",
        f'   git tag -a {tag} -m "Armarius {version}"',
        f"   git push origin {tag}",
        "",
        "The tag publishes the Release, the container image and the help site.",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare a release.")
    parser.add_argument("version", help="the new version, MAJOR.MINOR.PATCH")
    args = parser.parse_args(argv)
    try:
        print(prepare(ROOT, args.version, runner(ROOT)))
    except ReleaseError as error:
        print(f"Release stopped: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

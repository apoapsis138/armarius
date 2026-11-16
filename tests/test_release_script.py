"""tools/release.py: a release prepared in one command, with git, towncrier,
uv and pytest faked (each command's answer scripted, each call recorded)."""

from __future__ import annotations

import importlib.util
import subprocess
from collections.abc import Sequence
from pathlib import Path

import pytest

from ars_magica_manager import ROOT

_spec = importlib.util.spec_from_file_location("release", ROOT / "tools" / "release.py")
assert _spec and _spec.loader
release = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(release)

HEAD = "a" * 40
PYPROJECT = (
    '[project]\nname = "armarius"\nversion = "4.14.0"\n\n[tool.x]\nversion = "9"\n'
)
CHANGED = " M CHANGELOG.md\n M pyproject.toml\n M uv.lock\nD  changelog.d/a.glossa.md\n"


class FakeShell:
    """The commands a release runs, answered from a script; the calls kept."""

    def __init__(self, answers: dict[str, tuple[int, str]] | None = None):
        self.answers = {
            "git status --porcelain": (0, ""),
            "git fetch origin main": (0, ""),
            "git rev-parse HEAD": (0, HEAD + "\n"),
            "git rev-parse origin/main": (0, HEAD + "\n"),
            "git branch --show-current": (0, "main\n"),
            **(answers or {}),
        }
        self.calls: list[str] = []
        self.statuses: list[str] = []

    def __call__(self, command: Sequence[str]) -> subprocess.CompletedProcess[str]:
        line = " ".join(command)
        self.calls.append(line)
        if line == "git status --porcelain" and self.statuses:
            return subprocess.CompletedProcess(command, 0, self.statuses.pop(0), "")
        key = next((k for k in self.answers if line.startswith(k)), None)
        code, out = self.answers[key] if key else (0, "")
        return subprocess.CompletedProcess(command, code, out, "")


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    (tmp_path / "pyproject.toml").write_text(PYPROJECT, encoding="utf-8")
    fragments = tmp_path / "changelog.d"
    fragments.mkdir()
    (fragments / "README.md").write_text("How to add one.\n", encoding="utf-8")
    (fragments / "template.md.jinja").write_text("{# t #}\n", encoding="utf-8")
    (fragments / "a.glossa.md").write_text("**A guide.** New.\n", encoding="utf-8")
    return tmp_path


def _refused(repo: Path, shell: FakeShell, version: str = "4.15.0") -> str:
    with pytest.raises(release.ReleaseError) as raised:
        release.prepare(repo, version, shell)
    # A refusal changes nothing: no branch, build, lock or version.
    assert not any(c.startswith(("git switch", "uv ")) for c in shell.calls)
    assert 'version = "4.14.0"' in (repo / "pyproject.toml").read_text("utf-8")
    return str(raised.value)


def test_a_dirty_working_tree_is_refused(repo: Path):
    shell = FakeShell({"git status --porcelain": (0, " M README.md\n")})
    assert "working tree has changes" in _refused(repo, shell)


def test_a_head_that_isnt_origin_main_is_refused(repo: Path):
    shell = FakeShell({"git rev-parse HEAD": (0, "b" * 40 + "\n")})
    assert "isn't origin/main" in _refused(repo, shell)
    assert "git fetch origin main" in shell.calls


def test_a_failed_fetch_is_refused(repo: Path):
    shell = FakeShell({"git fetch origin main": (1, "")})
    assert "git fetch failed" in _refused(repo, shell)


@pytest.mark.parametrize("version", ["4.15", "v4.15.0", "4.15.0-rc1", "04.15.0"])
def test_a_version_that_isnt_major_minor_patch_is_refused(repo: Path, version: str):
    assert "isn't a version" in _refused(repo, FakeShell(), version)


@pytest.mark.parametrize("version", ["4.14.0", "4.13.9", "3.99.99"])
def test_a_version_no_newer_than_the_current_is_refused(repo: Path, version: str):
    assert "isn't newer than 4.14.0" in _refused(repo, FakeShell(), version)


def test_no_fragments_is_refused(repo: Path):
    (repo / "changelog.d" / "a.glossa.md").unlink()
    assert "no fragments" in _refused(repo, FakeShell())


def test_failing_tests_stop_the_release(repo: Path):
    shell = FakeShell({"uv run pytest": (1, "1 failed")})
    with pytest.raises(release.ReleaseError, match="tests failed"):
        release.prepare(repo, "4.15.0", shell)
    assert not any(c.startswith("git commit") for c in shell.calls)


def test_a_release_from_main_runs_every_step_in_order(repo: Path):
    shell = FakeShell()
    shell.statuses = ["", CHANGED]
    out = release.prepare(repo, "4.15.0", shell)
    steps = [c for c in shell.calls if not c.startswith(("git status", "git rev"))]
    assert steps == [
        "git fetch origin main",
        "git branch --show-current",
        "git switch -c release/4.15.0",
        "uv run towncrier build --yes --version 4.15.0",
        "uv lock",
        "uv run pytest -q " + " ".join(release.TESTS),
    ]
    # Only the project's version changes, not another table's.
    text = (repo / "pyproject.toml").read_text(encoding="utf-8")
    assert 'version = "4.15.0"' in text and 'version = "9"' in text
    # Never a commit, push or tag.
    assert not any(
        c.startswith(("git commit", "git push", "git tag")) for c in shell.calls
    )
    assert out.splitlines() == [
        "Release 4.15.0 is ready on release/4.15.0. Nothing is committed.",
        "",
        "1. Look over CHANGELOG.md's new section, then stage and commit:",
        "   git add CHANGELOG.md pyproject.toml uv.lock",
        "   (towncrier has already staged 1 deleted fragments)",
        '   git commit -m "Release 4.15.0"',
        "",
        "2. Push the branch and open the pull request into main:",
        "   git push -u origin release/4.15.0",
        "   https://github.com/apoapsis138/armarius/compare/main...release/4.15.0"
        "?expand=1",
        "",
        "3. Once it has merged, tag the merge commit on main:",
        "   git switch main",
        "   git pull",
        '   git tag -a v4.15.0 -m "Armarius 4.15.0"',
        "   git push origin v4.15.0",
        "",
        "The tag publishes the Release, the container image and the help site.",
    ]


def test_a_fresh_branch_from_main_is_kept(repo: Path):
    shell = FakeShell({"git branch --show-current": (0, "release/next\n")})
    shell.statuses = ["", CHANGED]
    out = release.prepare(repo, "4.15.0", shell)
    assert not any(c.startswith("git switch") for c in shell.calls)
    assert "git push -u origin release/next" in out


def test_main_prints_why_it_stopped(capsys: pytest.CaptureFixture[str]):
    # The version is checked before any git command runs.
    assert release.main(["4.15"]) == 1
    assert capsys.readouterr().err.startswith("Release stopped: ")

"""Run the tests for a slice of work: the fast tier plus the screen tests
of the area the working tree touches.

    uv run python tools/slice_tests.py [--dry-run] [pytest args...]

The fast tier is every test file that isn't a screen test (tiers.py says
which are): the rules, data and form tests, a few seconds in all.
Screen tests (Textual Pilot and Qt) are most of the suite's time, so a
slice runs only those that match what changed since the last commit
(tracked and untracked files):

* a changed test file runs itself;
* a changed source or help file runs the screen tests whose file names
  share a word with its own name, or the name of the folder it is in
  (``forms/covenant.py`` and ``gui/covenant.py`` both pick
  ``test_screens_covenant.py`` and ``test_gui_edit_covenant.py``);
* `AREA_TESTS` adds the tests a cross-cutting file needs whatever its name
  says (key routing, the form contracts, the golden sheet text);
* a change to what every test stands on (`EVERYTHING`: the shared test
  fixtures, the dependencies) runs every screen test.

This narrows what runs during a story, not what runs before one is handed
over: the full suite still runs once, at In Review (CLAUDE.md).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from tiers import is_screen_test_file, test_files

ROOT = Path(__file__).resolve().parent.parent

# Words too common in file names to say which area a file belongs to.
GENERIC_WORDS = {
    "ars",
    "magica",
    "manager",
    "test",
    "tests",
    "screens",
    "screen",
    "sheet",
    "sheets",
    "forms",
    "form",
    "gui",
    "tui",
    "edit",
    "base",
    "init",
    "app",
    "text",
    "widgets",
    "workspace",
    "help",
    "md",
    "py",
}

# Files whose effects reach well past their name, and the screen tests
# that check them. Keys are paths relative to the repo, or a folder ending
# in "/" for everything under it.
# Files every screen test depends on.
EVERYTHING = {
    "tests/conftest.py",
    "tests/support.py",
    "tests/screen_helpers.py",
    "tools/tiers.py",
    "uv.lock",
}

# The form contracts, one file per area of the app; a change to the forms'
# shared machinery runs them all.
DIALOG_CONTRACT_TESTS = (
    "test_dialog_contracts_character.py",
    "test_dialog_contracts_covenant.py",
    "test_dialog_contracts_laboratory.py",
    "test_dialog_contracts_library.py",
    "test_dialog_contracts_saga.py",
    "test_dialog_contracts_tribunal.py",
)

AREA_TESTS: dict[str, tuple[str, ...]] = {
    "ars_magica_manager/gui/choices.py": ("test_gui_sheet.py",),
    "ars_magica_manager/actions.py": ("test_dispatch_matrix.py", "test_keyboard.py"),
    "ars_magica_manager/sections.py": ("test_dispatch_matrix.py", "test_sheet_text.py"),
    "ars_magica_manager/form_spec.py": (
        *DIALOG_CONTRACT_TESTS,
        "test_fields_dialog.py",
    ),
    "ars_magica_manager/sheet_text.py": ("test_sheet_text.py",),
    "ars_magica_manager/forms/creature.py": (
        *DIALOG_CONTRACT_TESTS,
        "test_list_flows.py",
    ),
    "ars_magica_manager/sheets/creature.py": ("test_sheet_text.py",),
    "ars_magica_manager/help/": ("test_help.py", "test_gui_help.py"),
    "ars_magica_manager/help_text.py": ("test_help.py", "test_gui_help.py"),
    "ars_magica_manager/tui/screens/fields.py": (
        *DIALOG_CONTRACT_TESTS,
        "test_fields_dialog.py",
    ),
    "ars_magica_manager/tui/screens/forms/": DIALOG_CONTRACT_TESTS,
    "ars_magica_manager/tui/screens/workspace/": (
        "test_dispatch_matrix.py",
        "test_list_flows.py",
    ),
    "ars_magica_manager/tui/screens/sheets/": ("test_sheet_text.py",),
    "ars_magica_manager/gui/forms.py": (
        "test_gui_edit_shared.py",
        "test_activity_picker.py",
    ),
    "ars_magica_manager/commands.py": ("test_activity_picker.py",),
    "ars_magica_manager/tui/screens/steps.py": ("test_activity_picker.py",),
    "ars_magica_manager/tui/screens/pickers.py": ("test_activity_picker.py",),
    "ars_magica_manager/tui/screens/invent_spell.py": ("test_spell_template.py",),
    "ars_magica_manager/forms/lab_plan.py": ("test_spell_template.py",),
    "ars_magica_manager/seasons/plans.py": ("test_seasons_ahead.py",),
    "ars_magica_manager/gui/editing.py": ("test_gui_edit_shared.py",),
    "tests/golden/dispatch_matrix.json": ("test_dispatch_matrix.py",),
    "tests/golden/sheet_text/": ("test_sheet_text.py",),
    "tests/dialog_openers.py": DIALOG_CONTRACT_TESTS,
    "tests/dialog_contract_support.py": DIALOG_CONTRACT_TESTS,
    "tests/gui_steps.py": ("test_gui_edit_shared.py",),
    "pyproject.toml": ("test_version.py",),
    "CHANGELOG.md": ("test_version.py", "test_help.py", "test_title_page.py"),
    "ars_magica_manager/changelog.py": ("test_help.py", "test_title_page.py"),
}


def changed_files() -> list[str]:
    def git(*args: str) -> list[str]:
        out = subprocess.run(
            ["git", *args], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout
        return [line for line in out.splitlines() if line]

    return sorted(
        set(git("diff", "--name-only", "HEAD"))
        | set(git("ls-files", "--others", "--exclude-standard"))
    )


def _words(name: str) -> set[str]:
    return {w for w in name.lower().replace("-", "_").split("_") if w} - GENERIC_WORDS


def _area_words(path: str) -> set[str]:
    parts = Path(path).with_suffix("").parts
    words = _words(parts[-1])
    if len(parts) > 1:
        words |= _words(parts[-2])
    return words


def screen_tests_for(changed: list[str]) -> list[Path]:
    screens = [p for p in test_files() if is_screen_test_file(p)]
    if EVERYTHING.intersection(changed):
        return screens
    by_name = {p.name: p for p in screens}
    chosen: set[Path] = set()
    for path in changed:
        name = Path(path).name
        if path.startswith("tests/") and name in by_name:
            chosen.add(by_name[name])
            continue
        for key, tests in AREA_TESTS.items():
            if path == key or (key.endswith("/") and path.startswith(key)):
                chosen.update(by_name[t] for t in tests if t in by_name)
        if path.startswith(("ars_magica_manager/", "tests/")):
            words = _area_words(path)
            chosen.update(p for p in screens if words & _words(p.stem))
    return sorted(chosen)


def main(argv: list[str]) -> int:
    dry_run = "--dry-run" in argv
    extra = [a for a in argv if a != "--dry-run"]
    changed = changed_files()
    fast = [p for p in test_files() if not is_screen_test_file(p)]
    screens = screen_tests_for(changed)
    print(f"{len(changed)} changed files; fast tier: {len(fast)} test files")
    print(f"screen tests for this slice ({len(screens)}):")
    for p in screens:
        print(f"  {p.name}")
    command = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "-n",
        "auto",
        "--dist",
        "worksteal",
        *extra,
        *(str(p.relative_to(ROOT)) for p in fast + screens),
    ]
    if dry_run:
        return 0
    return subprocess.run(command, cwd=ROOT, check=False).returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

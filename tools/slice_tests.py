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
    "ars_magica_manager/gui/medallions.py": (
        "test_gui_conflicts.py",
        "test_gui_medallion_placements.py",
    ),
    "ars_magica_manager/medallions.py": (
        "test_gui_conflicts.py",
        "test_gui_medallion_placements.py",
    ),
    "ars_magica_manager/actions.py": ("test_dispatch_matrix.py", "test_keyboard.py"),
    # A covenant's Charter of Covenant: its clause list's flow, and its
    # forms' contracts.
    "ars_magica_manager/covenant_charter.py": (
        "test_list_flows.py",
        "test_dialog_contracts_covenant.py",
    ),
    "ars_magica_manager/forms/charter.py": (
        "test_list_flows.py",
        "test_dialog_contracts_covenant.py",
    ),
    "ars_magica_manager/sections.py": ("test_dispatch_matrix.py", "test_sheet_text.py"),
    "ars_magica_manager/form_spec.py": (
        *DIALOG_CONTRACT_TESTS,
        "test_fields_dialog.py",
    ),
    "ars_magica_manager/sheet_text.py": ("test_sheet_text.py",),
    "ars_magica_manager/forms/agents.py": (
        "test_gui_agents.py",
        "test_list_flows.py",
        "test_dialog_contracts_character.py",
    ),
    "ars_magica_manager/battles.py": (
        "test_dialog_contracts_tribunal.py",
        "test_sheet_text.py",
    ),
    "ars_magica_manager/disputations.py": ("test_screens_academe.py",),
    "ars_magica_manager/forms/grogs.py": ("test_dialog_contracts_character.py",),
    "ars_magica_manager/forms/careers.py": ("test_dialog_contracts_character.py",),
    "ars_magica_manager/forms/scholar_seasons.py": (
        "test_dialog_contracts_character.py",
    ),
    "ars_magica_manager/forms/craft_magic.py": (
        "test_dialog_contracts_character.py",
        "test_gui_edit_character.py",
    ),
    "ars_magica_manager/labor.py": ("test_dialog_contracts_character.py",),
    "ars_magica_manager/conflicts.py": (
        "test_list_flows.py",
        "test_dialog_contracts_saga.py",
        "test_sheet_text.py",
    ),
    "ars_magica_manager/fights.py": (
        "test_list_flows.py",
        "test_dialog_contracts_saga.py",
        "test_sheet_text.py",
    ),
    "ars_magica_manager/sieges.py": (
        "test_list_flows.py",
        "test_dialog_contracts_saga.py",
        "test_sheet_text.py",
    ),
    "ars_magica_manager/tui/screens/sheets/conflicts.py": (
        "test_list_flows.py",
        "test_dialog_contracts_saga.py",
        "test_sheet_text.py",
    ),
    "ars_magica_manager/research_text.py": (
        "test_sheet_text.py",
        "test_research.py",
        "test_gui_research.py",
        "test_screens_research.py",
    ),
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
    "ars_magica_manager/spell_parameters.py": ("test_spell_template.py",),
    "ars_magica_manager/grog_templates.py": (
        "test_character_templates.py",
        "test_dialog_contracts_covenant.py",
    ),
    "ars_magica_manager/choice_templates.py": (
        "test_dialog_contracts_covenant.py",
        "test_gui_menus.py",
    ),
    "ars_magica_manager/forms/choice_templates.py": (
        "test_dialog_contracts_covenant.py",
        "test_gui_menus.py",
    ),
    "ars_magica_manager/forms/grog_templates.py": (
        "test_character_templates.py",
        "test_dialog_contracts_covenant.py",
        "test_gui_menus.py",
    ),
    "ars_magica_manager/aging_chart.py": (
        "test_creation_worksheet.py",
        "test_dialog_contracts_character.py",
    ),
    "ars_magica_manager/rules/grog_aging.py": (
        "test_creation_worksheet.py",
        "test_dialog_contracts_character.py",
    ),
    "ars_magica_manager/forms/animal.py": (
        "test_creation_worksheet.py",
        "test_dialog_contracts_character.py",
    ),
    "ars_magica_manager/rules/animal_grogs.py": (
        "test_creation_worksheet.py",
        "test_character_templates.py",
        "test_sheet_text.py",
    ),
    "ars_magica_manager/rules/creation_animal.py": ("test_creation_worksheet.py",),
    "ars_magica_manager/rules/animal_aging.py": ("test_seasons.py",),
    "ars_magica_manager/seasons/animal_aging.py": ("test_seasons.py",),
    "data/animal_template_catalog.json": (
        "test_character_templates.py",
        "test_dialog_contracts_covenant.py",
    ),
    "ars_magica_manager/seasons/plans.py": ("test_seasons_ahead.py",),
    "ars_magica_manager/gui/editing.py": ("test_gui_edit_shared.py",),
    "ars_magica_manager/gui/research.py": ("test_gui_research.py",),
    "tests/golden/dispatch_matrix.json": ("test_dispatch_matrix.py",),
    "tests/golden/sheet_text/": ("test_sheet_text.py",),
    "tests/dialog_openers.py": DIALOG_CONTRACT_TESTS,
    "tests/dialog_contract_support.py": DIALOG_CONTRACT_TESTS,
    "tests/gui_steps.py": ("test_gui_edit_shared.py",),
    "pyproject.toml": ("test_version.py",),
    "CHANGELOG.md": ("test_version.py", "test_help.py", "test_title_page.py"),
    "ars_magica_manager/changelog.py": ("test_help.py", "test_title_page.py"),
    # The Theban treasury and its coins.
    "ars_magica_manager/treasury.py": (
        "test_dialog_contracts_tribunal.py",
        "test_sheet_text.py",
    ),
    "ars_magica_manager/coinage.py": ("test_sheet_text.py",),
    # A craftsman's sale of his finished goods.
    "ars_magica_manager/selling.py": ("test_dialog_contracts_character.py",),
    # The Theban Tribunal's Byzantine customs, and the icons on Relics.
    "ars_magica_manager/theban_customs.py": (
        "test_dialog_contracts_character.py",
        "test_keyboard.py",
    ),
    "ars_magica_manager/churches.py": ("test_dialog_contracts_tribunal.py",),
    # Sin, tarnish and the Goetic Arts (RoP: The Infernal).
    "ars_magica_manager/forms/sin.py": ("test_dialog_contracts_character.py",),
    "ars_magica_manager/forms/goetic.py": ("test_dialog_contracts_character.py",),
    # The hunt and Area Lore, on a manor and on the road.
    "ars_magica_manager/forms/hunting.py": ("test_dialog_contracts_tribunal.py",),
    "ars_magica_manager/rules/hunting.py": ("test_dialog_contracts_tribunal.py",),
    # Dealing with faeries: the Ars Fabulosa, bargains and offers.
    "ars_magica_manager/forms/faerie_dealings.py": (
        "test_dialog_contracts_character.py",
    ),
    "ars_magica_manager/rules/faerie_dealings.py": (
        "test_dialog_contracts_character.py",
    ),
    # Hermetic law on the docket: Wizard's War, the March, traces, Intrigue.
    "ars_magica_manager/rules/hermetic_law.py": ("test_dialog_contracts_tribunal.py",),
    # Angels and demons: divine beings, holy influence, holy powers and the
    # maleficia (RoP: The Divine, RoP: The Infernal).
    "ars_magica_manager/forms/holy_influence.py": (
        "test_dialog_contracts_character.py",
    ),
    "ars_magica_manager/rules/divine_build.py": (
        "test_dialog_contracts_saga.py",
        "test_sheet_text.py",
    ),
    "ars_magica_manager/rules/holy_powers.py": ("test_dialog_contracts_character.py",),
    "ars_magica_manager/rules/maleficia.py": ("test_dialog_contracts_character.py",),
    # The lacuna and the pilgrim: casting in a lacuna, the pilgrim's road.
    "ars_magica_manager/forms/lacuna.py": ("test_dialog_contracts_character.py",),
    "ars_magica_manager/forms/pilgrimage.py": ("test_dialog_contracts_character.py",),
    "ars_magica_manager/rules/lacunae.py": ("test_dialog_contracts_character.py",),
    "ars_magica_manager/rules/pilgrimage.py": ("test_dialog_contracts_character.py",),
    # Breakthroughs: Hermetic Viresculture's seasons on the season form.
    "ars_magica_manager/forms/viresculture_seasons.py": (
        "test_dialog_contracts_character.py",
        "test_season_forms.py",
    ),
    # Mystic paths, God's aid, the Font and the Commanding Aura's forms.
    "ars_magica_manager/mystic_paths.py": ("test_dialog_contracts_character.py",),
    # Hermetic spirit magic and theurgy's calculator (TMRE).
    "ars_magica_manager/forms/tmre_spirits.py": ("test_dialog_contracts_character.py",),
    # Arithmetic magic's seasons on the season form (TMRE).
    "ars_magica_manager/forms/arithmetic_seasons.py": (
        "test_dialog_contracts_character.py",
        "test_season_forms.py",
    ),
    # Dream magic and Hermetic sacrifice's forms (TMRE).
    "ars_magica_manager/forms/tmre_dreams.py": ("test_dialog_contracts_character.py",),
    # Against the Dark's vampires, kukudhi and crowned kings: the creature
    # sheet's facts and the creation worksheet's free Shapeshifter.
    "ars_magica_manager/rules/transylvania.py": (
        "test_sheet_text.py",
        "test_creation_worksheet.py",
    ),
    # Divination and Hermetic astrology's More forms (TMRE).
    "ars_magica_manager/forms/tmre_divination.py": (
        "test_dialog_contracts_character.py",
    ),
    # House Acclaim and Reputation Roll's More forms (HoH:TL, HoH:S).
    "ars_magica_manager/forms/acclaim.py": ("test_dialog_contracts_character.py",),
    # Philosophic Alchemy's More form and the Lesser Elixir's season fields
    # (TMRE).
    "ars_magica_manager/forms/tmre_alchemy.py": ("test_dialog_contracts_character.py",),
    "ars_magica_manager/forms/alchemy_seasons.py": (
        "test_dialog_contracts_character.py",
        "test_season_forms.py",
    ),
    # The spell design's Guideline picker (HoH:S, MoH guidelines).
    "ars_magica_manager/forms/spell_guideline.py": (
        "test_spell_guidelines.py",
        "test_spell_template.py",
    ),
    # Gaining and losing Virtues and Flaws in play (Grogs pp. 61-64).
    "ars_magica_manager/forms/vf_change.py": ("test_dialog_contracts_character.py",),
    # A covenant's ships: the Ships list, its forms and More (HP; C&G).
    "ars_magica_manager/ships.py": (
        "test_sheet_text.py",
        "test_list_flows.py",
        "test_dispatch_matrix.py",
    ),
    "ars_magica_manager/forms/ships.py": ("test_dialog_contracts_covenant.py",),
    "ars_magica_manager/gui/ships.py": ("test_gui_ships.py",),
    # The Rhine's Great Library tab (Guardians of the Forests).
    "ars_magica_manager/tribunal_packages/rhine_library.py": (
        "test_great_library.py",
        "test_dialog_contracts_tribunal.py",
        "test_list_flows.py",
        "test_sheet_text.py",
        "test_dispatch_matrix.py",
    ),
    "ars_magica_manager/gui/ledger_rows.py": ("test_tribunals.py",),
    # Shaping the land by magic: More's Shape the Land on Income (TME).
    "ars_magica_manager/forms/land_shaping.py": ("test_dialog_contracts_covenant.py",),
    "ars_magica_manager/forms/land_seasons.py": ("test_dialog_contracts_character.py",),
    # A cleric's career: the Church tab, its forms and lists (The Church).
    "ars_magica_manager/forms/church.py": (
        "test_clergy.py",
        "test_dialog_contracts_character.py",
        "test_list_flows.py",
        "test_gui_church.py",
    ),
    "ars_magica_manager/rules/clergy.py": ("test_clergy.py",),
    "ars_magica_manager/gui/church.py": ("test_gui_church.py",),
    # A covenant's Hermetic Projects: the Projects tab, its forms and lists,
    # and Open a Tunnel (Hermetic Projects).
    "ars_magica_manager/hermetic_projects.py": (
        "test_hermetic_projects.py",
        "test_dialog_contracts_covenant.py",
        "test_list_flows.py",
        "test_screens_projects.py",
        "test_gui_projects.py",
    ),
    "ars_magica_manager/forms/tunnel.py": (
        "test_hermetic_projects.py",
        "test_dialog_contracts_character.py",
    ),
    "ars_magica_manager/forms/tower_seasons.py": ("test_hermetic_projects.py",),
    # Saga Content's Mystery Cults: their tests, the forms' contracts, the
    # lists' flow and the Saga Content screens.
    "ars_magica_manager/mystery_cults.py": (
        "test_own_cults.py",
        "test_dialog_contracts_saga.py",
        "test_list_flows.py",
    ),
    "ars_magica_manager/forms/mystery_cults.py": (
        "test_own_cults.py",
        "test_dialog_contracts_saga.py",
        "test_list_flows.py",
        "test_saga_content.py",
    ),
    "ars_magica_manager/gui/mystery_cults.py": ("test_gui_sheet.py",),
    "ars_magica_manager/models/mystery_cults.py": ("test_own_cults.py",),
    # Fleet battles (Tales of Power): the Battle forms at sea.
    "ars_magica_manager/fleet_battles.py": (
        "test_dialog_contracts_saga.py",
        "test_dialog_contracts_tribunal.py",
        "test_list_flows.py",
        "test_gui_conflicts.py",
    ),
    # A covenant's Menagerie (Hermetic Projects): its tests, the forms'
    # contracts, the lists' flow and the Projects tab on both front-ends.
    "ars_magica_manager/menagerie.py": (
        "test_menagerie.py",
        "test_dialog_contracts_covenant.py",
        "test_list_flows.py",
        "test_screens_projects.py",
        "test_gui_projects.py",
    ),
    # A lord's marriages (Lords of Men): the forms' contracts, the list's
    # flow and the Marriages tab on both front-ends.
    "ars_magica_manager/marriages.py": (
        "test_marriage.py",
        "test_dialog_contracts_tribunal.py",
        "test_list_flows.py",
        "test_gui_marriage.py",
        "test_sheet_text.py",
    ),
    "ars_magica_manager/rules/marriage.py": ("test_marriage.py",),
    "ars_magica_manager/models/marriage.py": ("test_marriage.py",),
    # A Criamon magus's The Enigma tab, its forms and lists (HoH:MC).
    "ars_magica_manager/forms/criamon.py": (
        "test_criamon.py",
        "test_dialog_contracts_character.py",
        "test_list_flows.py",
        "test_gui_criamon.py",
    ),
    "ars_magica_manager/rules/criamon.py": ("test_criamon.py",),
    "ars_magica_manager/models/criamon.py": ("test_criamon.py", "test_storage.py"),
    # Polemic and Charter Strength (Transforming Mythic Europe): the
    # Arguments tab, its forms and lists on both front-ends, and the charter
    # lords' Draft the Charter and Seek a Loophole.
    "ars_magica_manager/forms/polemic.py": (
        "test_polemic.py",
        "test_dialog_contracts_tribunal.py",
        "test_list_flows.py",
        "test_tribunals.py",
        "test_sheet_text.py",
    ),
    "ars_magica_manager/gui/polemic.py": ("test_polemic.py", "test_tribunals.py"),
    "ars_magica_manager/polemic.py": ("test_polemic.py", "test_meeting.py"),
    "ars_magica_manager/rules/polemic.py": ("test_polemic.py",),
    "ars_magica_manager/models/polemic.py": ("test_polemic.py", "test_storage.py"),
    "ars_magica_manager/forms/charter_strength.py": (
        "test_polemic.py",
        "test_dialog_contracts_tribunal.py",
        "test_town_charter.py",
    ),
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

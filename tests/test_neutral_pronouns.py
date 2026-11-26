"""Screen text never presumes a character's gender, and Deeds lines stay short.

The app keeps no gender for a character, so the words it writes for a
screen (labels, hints, descriptions, notes, results and the help pages)
say "they" and "their", never he or she. Docstrings aren't shown, so they
are left out, and so are the book packs, which keep the books' wording.

The allow-lists below name the deliberate uses, each with its reason:
rules text summarised from the books, ships, the roles the rules
themselves give a sex (bride, widow, mother...), and named people.
"""

from __future__ import annotations

import ast
import re
from collections.abc import Iterator
from pathlib import Path

from ars_magica_manager import deeds

ROOT = Path(__file__).resolve().parent.parent / "ars_magica_manager"
PRONOUN = re.compile(r"\b(he|him|his|she|her|hers|himself|herself)\b", re.IGNORECASE)
HERBAM = "He"  # the Art's abbreviation, not a pronoun

SHIP = "a ship is 'she'"
MARRIAGE = "the marriage rules' bride, wife, widow and heiress"
RULES = "rules text summarised from the books"
NAMED = "a named person or example"
ROLE = "a role the rules give a sex"

#: Whole files whose pronouns are all deliberate.
ALLOWED_FILES: dict[str, str] = {
    "help/packs.md": NAMED,
    "marriages.py": MARRIAGE,
    "rules/marriage.py": MARRIAGE,
    "ships.py": SHIP,
    "forms/ships.py": SHIP,
    "forms/ship_build.py": SHIP,
    "rules/ships.py": SHIP,
}

#: Module-level tables (by the name they're assigned to) of rules text.
ALLOWED_TABLES: dict[tuple[str, str], str] = {
    ("arts.py", "ART_DESCRIPTIONS"): RULES,
    ("rules/africa.py", "AITHIOPES"): RULES,
    ("rules/artistry.py", "EXPERIMENT_TEXT"): RULES,
    ("rules/baraka.py", "FORBEARS"): NAMED,
    ("rules/battle_transformation.py", "LUAN_TEXT"): RULES,
    ("rules/battle_transformation.py", "RIASTRADH_TEXT"): RULES,
    ("rules/casting_virtues.py", "NOTES"): RULES,
    ("rules/certamen_styles.py", "STYLES"): RULES,
    ("rules/church_build.py", "BOONS_AND_HOOKS"): RULES,
    ("rules/clergy.py", "PUNISHMENTS"): RULES,
    ("rules/criamon.py", "BODY"): RULES,
    ("rules/criamon.py", "SEEMING"): RULES,
    ("rules/criamon.py", "STRIFE"): RULES,
    ("rules/criamon.py", "WALKING"): RULES,
    ("rules/devotion.py", "GAINS"): RULES,
    ("rules/devotion.py", "THREAT_OUTCOMES"): RULES,
    ("rules/faerie_blood.py", "CHARM_RULE"): RULES,
    ("rules/faiths.py", "FAITHS"): RULES,
    ("rules/goetic.py", "ABLATION_USES"): RULES,
    ("rules/goetic.py", "COMMANDS"): RULES,
    ("rules/hedge_casting.py", "SIHR_VERSIONS"): RULES,
    ("rules/hermetic_law.py", "CONTEST"): RULES,
    ("rules/hybrid_magic.py", "CHTHONIC"): RULES,
    ("rules/hybrid_magic.py", "FAERIE_MAGIC"): RULES,
    ("rules/hybrid_magic.py", "HOLY"): RULES,
    ("rules/infernal_build.py", "ORDERS"): RULES,
    ("rules/integrations.py", "INTEGRATIONS"): RULES,
    ("rules/journeys.py", "MEANS"): RULES,
    ("rules/magic_combat.py", "SOCIETATES_INDIRECT"): RULES,
    ("rules/magic_combat.py", "_FLAME"): RULES,
    ("rules/magic_combat.py", "_HOLDS"): RULES,
    ("rules/merinita.py", "NATURE_LORE_EFFECTS"): RULES,
    ("rules/merinita.py", "NEGATIVE_CORD_EFFECTS"): RULES,
    ("rules/merinita.py", "TRANSFORMATIONS"): RULES,
    ("rules/mysticism.py", "FAITH_GIFTS"): RULES,
    ("rules/nobility.py", "NOBLE_EXTRAS"): MARRIAGE,
    ("rules/nobility.py", "REWARDS"): RULES,
    ("rules/options.py", "OPTIONS"): RULES,
    ("rules/realm_warping.py", "_INFERNAL"): RULES,
    ("rules/saints.py", "POWERS"): RULES,
    ("rules/saints.py", "SAINTS"): NAMED,
    ("rules/sigils.py", "PROMOTIONS"): RULES,
    ("rules/tmre_dreams.py", "MUTO_MENTEM_GUIDELINES"): RULES,
    ("rules/tournament.py", "MELEE_EVENTS"): RULES,
    ("rules/tournament.py", "RANSOMS"): RULES,
    ("rules/verditius.py", "VERDITIUS_COMPONENTS"): RULES,
    ("rules/vis_kinds.py", "KINDS"): RULES,
    ("staged_projects.py", "RULES_TEXT"): RULES,
    ("tombs.py", "TRAP_RULE"): RULES,
    ("town_court.py", "SENTENCES"): RULES,
    ("tribunal_packages/alps.py", "ALPS"): RULES,
    ("tribunal_packages/novgorod.py", "NOVGOROD"): RULES,
    ("tribunal_packages/provence.py", "PROVENCE"): RULES,
}

#: Help sections whose pronouns are all deliberate, by file and heading.
ALLOWED_SECTIONS: dict[tuple[str, str], str] = {
    ("help/covenant.md", "Ships"): SHIP,
    ("help/covenant.md", "Build a Ship"): SHIP,
    ("help/region.md", "Arrange a Marriage"): MARRIAGE,
    ("help/region.md", "End a Marriage"): MARRIAGE,
    ("help/region.md", "The Terms"): MARRIAGE,
    ("help/guides-4.md", "How to find a record"): NAMED,
    ("help/guides-4.md", "How to follow a story from its start to a threat"): NAMED,
    ("help/guides-4.md", "How to invite a player to a Remote seat"): NAMED,
    ("help/guides-4.md", "How to keep a covenant on the move"): SHIP,
    ("help/guides-4.md", "How to roll at the table"): NAMED,
    ("help/guides-4.md", "How to run a saga with several storyguides"): NAMED,
    ("help/guides-4.md", "How to stay at another covenant"): NAMED,
}

#: Single strings or help lines, matched by a piece of their text.
ALLOWED_TEXT: dict[tuple[str, str], str] = {
    ("mobile_covenants.py", "She goes to"): SHIP,
    ("mobile_covenants.py", "Choose where she goes."): SHIP,
    ("manors.py", "A widow survives him"): MARRIAGE,
    ("manors.py", "She keeps"): MARRIAGE,
    ("manors.py", "Ticked when his last marriage"): MARRIAGE,
    ("rules/casting_virtues.py", "Verditius Magic: Formulaic and Ritual spells"): RULES,
    ("rules/casting_virtues.py", "Dream Magic: in a dream"): RULES,
    ("rules/folk_witches.py", "Primitive Tradition: she"): ROLE,
    (
        "rules/menagerie.py",
        "a daughter gives +3 to her own",
    ): "a beast's dam and daughter",
    ("theban_customs.py", "the task she sets"): "the mother who laid the curse",
    ("help/character.md", "a crowned king or his queen"): ROLE,
    ("help/character.md", "he's also a priest, and a nun never"): ROLE,
    ("help/character.md", "A Mother's Curse"): ROLE,
    ("help/character.md", "The Diary records her and the task"): ROLE,
    ("help/character.md", "Conciatta's Minor Virtues"): NAMED,
    ("help/character.md", "for Heron, his uncorrupted"): NAMED,
    ("help/covenant.md", "crossbred dam like her own dam"): "a beast's dam",
    ("help/guides-1.md", "**Add a ship.**"): SHIP,
    ("help/guides-4.md", "from the queen to her courtiers"): NAMED,
    ("help/guides-4.md", "Walter the book merchant"): NAMED,
    ("help/processes.md", "An Amazon needs twice"): ROLE,
    ("help/processes.md", "Grifo's mural in his church"): NAMED,
    ("help/processes.md", "folk witch's 200. Her ten years"): ROLE,
    ("help/processes.md", "Paul, 45"): NAMED,
    ("help/region.md", "Viscountess Ermengarde does her"): NAMED,
    ("help/region.md", "A widow keeps her third"): MARRIAGE,
    ("help/region.md", "one of her unpublished works"): NAMED,
    ("help/region.md", "Her words for auras"): NAMED,
    ("help/region.md", "Tomb of Cleopatra prints"): NAMED,
    ("help/region.md", "her tomb's curses come"): NAMED,
    ("help/workspace.md", "for as long as she is"): NAMED,
}

#: The longest a Deeds-chapter description may be: one line beside its button.
DESCRIPTION_MOST = 80

#: Descriptions allowed to stay longer. None now; nothing new joins the list.
STILL_LONG: set[str] = set()


def _table_name(node: ast.AST, parents: dict[ast.AST, ast.AST]) -> str:
    """The name of the module-level assignment a string sits in, if any."""
    current = parents.get(node)
    while current is not None:
        if isinstance(current, (ast.Assign, ast.AnnAssign)) and isinstance(
            parents.get(current), ast.Module
        ):
            target = (
                current.targets[0]
                if isinstance(current, ast.Assign)
                else current.target
            )
            return target.id if isinstance(target, ast.Name) else ""
        current = parents.get(current)
    return ""


def _allowed(where: str, text: str, table: str = "", heading: str = "") -> bool:
    if (
        where in ALLOWED_FILES
        or (where, table) in ALLOWED_TABLES
        or (where, heading) in ALLOWED_SECTIONS
    ):
        return True
    return any(path == where and piece in text for path, piece in ALLOWED_TEXT)


def _code_hits() -> Iterator[str]:
    for path in sorted(ROOT.rglob("*.py")):
        where = path.relative_to(ROOT).as_posix()
        if where.startswith("book_packs/"):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        parents = {
            child: node
            for node in ast.walk(tree)
            for child in ast.iter_child_nodes(node)
        }
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Constant) and isinstance(node.value, str)):
                continue
            if isinstance(parents.get(node), ast.Expr) or node.value == HERBAM:
                continue
            if PRONOUN.search(node.value) and not _allowed(
                where, node.value, _table_name(node, parents)
            ):
                yield f"{where}:{node.lineno} {node.value[:70]!r}"


def _page_hits(where: str, text: str) -> Iterator[str]:
    heading = ""
    for number, line in enumerate(text.splitlines(), 1):
        if line.startswith("#"):
            heading = line.lstrip("#").strip()
        if PRONOUN.search(line) and not _allowed(where, line, heading=heading):
            yield f"{where}:{number} {line.strip()[:70]!r}"


def _help_hits() -> Iterator[str]:
    for path in sorted((ROOT / "help").glob("*.md")):
        yield from _page_hits(
            path.relative_to(ROOT).as_posix(), path.read_text(encoding="utf-8")
        )


def test_a_help_heading_is_checked_too():
    assert list(_page_hits("help/character.md", "## Raise his Bond\nText.\n"))


def test_screen_text_uses_they_not_he_or_she():
    found = [*_code_hits(), *_help_hits()]
    assert not found, (
        f"{len(found)} screen strings say he or she; write they/their (or list a "
        "deliberate use in this test's allow-lists):\n" + "\n".join(found)
    )


def test_deeds_descriptions_fit_one_line():
    tables = {
        name: value
        for name, value in vars(deeds).items()
        if name.endswith("NOTES") and isinstance(value, dict)
    }
    long = {
        f"{name}[{key}]": text
        for name, table in tables.items()
        for key, text in table.items()
        if len(text) > DESCRIPTION_MOST
    }
    new = [
        f"{key} {len(text)}: {text}"
        for key, text in long.items()
        if key not in STILL_LONG
    ]
    assert not new, "Deeds descriptions over 80 characters:\n" + "\n".join(new)
    assert not STILL_LONG - long.keys(), (
        f"now short enough, take off STILL_LONG: {STILL_LONG - long.keys()}"
    )

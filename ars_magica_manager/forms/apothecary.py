"""More's Make a Ligature and Apothecary's Store: a scholar's ligature
roll, and an apothecary's search for ingredients or preserving of one,
each written in the Diary -- no UI in here. The rules and their pages are
rules.philosophy's (ligatures, Art & Academe pp. 68-69) and
rules.apothecary's (the store, pp. 63-66)."""

from __future__ import annotations

import random
from typing import Any

from .. import diaries
from ..commands import Command, Form, Refuse, notes
from ..form_spec import DialogField
from ..markup import escape
from ..models import Character, Saga
from ..rules import apothecary as ap
from ..rules import dice
from ..rules import philosophy as ph

LIGATURE_TITLE = "Make a Ligature"
LIGATURE_HELP = "ligature"
STORE_TITLE = "Apothecary's Store"
STORE_HELP = "apothecary-store"
SEARCH, PRESERVE = "search", "preserve"


# -- shared: a die typed or rolled ------------------------------------------


def _die_fields(stress: bool, show: Any = None) -> list[DialogField]:
    kind = "A stress die" if stress else "A simple die"
    found = [
        DialogField(
            "die",
            "Die",
            "optint",
            None,
            placeholder="(blank: the app rolls it)",
            hint=f"{kind}.",
            show_if=show,
        )
    ]
    if stress:
        found.append(
            DialogField(
                "botched",
                "The die botched",
                "check",
                False,
                show_if=lambda v: (
                    (show is None or show(v)) and v.get("die") is not None
                ),
            )
        )
    return found


def _die_problem(values: dict[str, Any], stress: bool) -> str | None:
    die = values.get("die")
    if die is None:
        return None
    if int(die) < 0:
        return "A die can't be below 0."
    if not stress and not 1 <= int(die) <= 10:
        return "A simple die shows 1 to 10."
    return None


def _roll(
    saga: Saga, values: dict[str, Any], rng: random.Random, stress: bool
) -> tuple[int, bool, str]:
    """The die: (its value, whether it botched, as shown)."""
    typed = values.get("die")
    if typed is not None:
        botched = stress and bool(values.get("botched"))
        return int(typed), botched, "a botch" if botched else str(typed)
    if not stress:
        die = dice.simple_die(rng)
        return die, False, str(die)
    found = dice.stress_die(rng, 1, saga=saga)
    return found.value, found.botched, "a botch" if found.botched else str(found.value)


# -- Make a Ligature -----------------------------------------------------------


def ligature_fields(character: Character) -> list[DialogField]:
    abilities = ph.ligature_abilities(character)
    store = ap.keeps_store(character)
    return [
        DialogField(
            "ability",
            "Ability",
            "select",
            abilities[0] if abilities else None,
            options=[
                (
                    f"{escape(a)} ({ph.ligature_base(character, a):+d} with "
                    "Intelligence)",
                    a,
                )
                for a in abilities
            ],
            required=True,
            hint="Artes Liberales, Philosophiae or Medicine: at least 1 in the "
            "one it is tied to (A&A pp. 68-69).",
        ),
        DialogField(
            "purpose",
            "For",
            "text",
            "",
            placeholder="(the roll it helps, whose, and when: one six-hour window)",
        ),
        DialogField(
            "own_store",
            "From his own store",
            "check",
            store,
            hint=f"{ph.LIGATURE_LABOR} Labor Point of an apothecary's store; "
            "untick when another apothecary's store, or a bought ingredient, "
            "supplies it.",
        ),
        *_die_fields(stress=True),
    ]


def _ligature_validate(values: dict[str, Any]) -> str | None:
    if not str(values.get("purpose") or "").strip():
        return "Say what the ligature is for."
    return _die_problem(values, stress=True)


def ligature_live(character: Character) -> Any:
    """The inspector: the roll and the table it is read on."""

    def inspect(values: dict[str, Any]) -> str:
        ability = str(values.get("ability") or "")
        base = ph.ligature_base(character, ability) if ability else 0
        table = ", ".join(
            f"{need}: +{bonus}" for need, bonus in reversed(ph.LIGATURE_BONUS)
        )
        lines = [
            f"[b]{escape(character.name)}[/]  [$label]Intelligence + "
            f"{escape(ability or 'the Ability')} {base:+d}[/]",
            f"His roll: a stress die + [b]{base}[/]; the Ligature Bonus Table "
            f"{table} (the most) [dim](A&A p. 69)[/]",
            f"A botch works against the action: {ph.LIGATURE_BOTCH_PENALTY} and "
            f"{ph.LIGATURE_BOTCH_DICE} extra botch dice, and he doesn't know it.",
            "One ligature at a time helps a person; none helps a season's work, "
            "and a medical one no Recovery roll.",
        ]
        return "\n".join(lines)

    return inspect


def apply_ligature(
    saga: Saga, character: Character, values: dict[str, Any], rng: random.Random
) -> list[str]:
    ability = str(values.get("ability") or "")
    purpose = str(values.get("purpose") or "").strip()
    die, botched, shown = _roll(saga, values, rng, stress=True)
    base = ph.ligature_base(character, ability)
    total = base + die
    if botched:
        outcome = (
            f"Botched, unknown to him: the action takes {ph.LIGATURE_BOTCH_PENALTY} "
            f"and {ph.LIGATURE_BOTCH_DICE} extra botch dice."
        )
    elif bonus := ph.ligature_bonus(total):
        outcome = f"{total}: +{bonus} to the roll it was made for."
    else:
        outcome = f"{total}: below 9, it gives nothing."
    lines = [f"A ligature of {ability} for {purpose}. Die {shown}.", outcome]
    if values.get("own_store"):
        character.labor_points -= ph.LIGATURE_LABOR
        lines.append(
            f"{ph.LIGATURE_LABOR} Labor Point from his store: "
            f"{character.labor_points} now."
        )
    diaries.write(
        saga.current_year,
        saga.current_season,
        f"Ligature: {purpose}",
        " ".join([*lines, f"Rules: {ph.LIGATURE_SOURCE}."]),
        characters=[character],
    )
    return notes(*map(escape, lines), f"Written in {escape(character.name)}'s Diary.")


def ligature_form(
    saga: Saga, character: Character | None, rng: random.Random | None = None
) -> Command:
    if character is None:
        return Refuse(LIGATURE_TITLE, "Choose a character first.")
    if not ph.ligature_abilities(character):
        return Refuse(
            LIGATURE_TITLE,
            f"{escape(character.name)} has no Artes Liberales, Philosophiae or "
            "Medicine to make a ligature with.",
        )
    return Form(
        f"{LIGATURE_TITLE}: {escape(character.name)}",
        lambda: ligature_fields(character),
        lambda values: apply_ligature(saga, character, values, rng or random.Random()),
        validate=_ligature_validate,
        live=ligature_live(character),
        save_label="Roll",
        help_id=LIGATURE_HELP,
        inspector="The Ligature",
    )


# -- Apothecary's Store --------------------------------------------------------


def _is(what: str) -> Any:
    return lambda values: (values.get("roll") or SEARCH) == what


def store_fields(saga: Saga, character: Character) -> list[DialogField]:
    searching = _is(SEARCH)
    return [
        DialogField(
            "roll",
            "Roll",
            "select",
            SEARCH,
            options=[
                ("Search for an ingredient (Per + Profession)", SEARCH),
                ("Preserve an ingredient (Dex + Profession)", PRESERVE),
            ],
            required=True,
        ),
        DialogField(
            "ingredient",
            "Ingredient",
            "text",
            "",
            placeholder="(what, and for what: a regimen, a formula, a ligature)",
        ),
        DialogField(
            "area_lore",
            "Area Lore",
            "int",
            0,
            show_if=searching,
            hint="His Area Lore where he searches, if he knows it (no broader "
            "than a region or one feature: the Black Forest).",
        ),
        DialogField(
            "assistants",
            "Assistants",
            "int",
            0,
            show_if=searching,
            hint=f"-1 each; at most his Leadership "
            f"({ap.most_assistants(character)}), each with Profession: "
            f"Apothecary {ap.ASSISTANT_PROFESSION} or Area Lore "
            f"{ap.ASSISTANT_AREA_LORE}.",
        ),
        DialogField(
            "terrain",
            "Ground",
            "select",
            "",
            options=[(label, key) for key, label in ap.TERRAIN_LABELS.items()],
            show_if=searching,
        ),
        DialogField(
            "winter",
            "In winter (+2)",
            "check",
            saga.current_season == "Winter",
            show_if=searching,
        ),
        DialogField(
            "spell",
            "Under a finding spell (-3)",
            "check",
            False,
            show_if=searching,
            hint="Such as Hunt for the Wild Herb, for the whole search.",
        ),
        DialogField(
            "duration",
            "To keep for",
            "select",
            "Seasons",
            options=[(f"{name} ({ease})", name) for name, ease in ap.PRESERVE_EASE],
            show_if=_is(PRESERVE),
        ),
        *_die_fields(stress=True, show=searching),
        DialogField(
            "simple_die",
            "Simple die",
            "optint",
            None,
            placeholder="(blank: the app rolls it)",
            hint="A simple die.",
            show_if=_is(PRESERVE),
        ),
    ]


def _search(values: dict[str, Any]) -> ap.Search:
    return ap.Search(
        area_lore=int(values.get("area_lore") or 0),
        assistants=int(values.get("assistants") or 0),
        terrain=str(values.get("terrain") or ""),
        winter=bool(values.get("winter")),
        spell=bool(values.get("spell")),
    )


def _store_validate(character: Character) -> Any:
    def validate(values: dict[str, Any]) -> str | None:
        if not str(values.get("ingredient") or "").strip():
            return "Name the ingredient."
        if (values.get("roll") or SEARCH) == PRESERVE:
            return _die_problem({"die": values.get("simple_die")}, stress=False)
        assistants = int(values.get("assistants") or 0)
        if assistants < 0 or int(values.get("area_lore") or 0) < 0:
            return "Area Lore and assistants can't be below 0."
        if assistants > ap.most_assistants(character):
            return (
                f"{character.name} leads at most {ap.most_assistants(character)} "
                "assistants (his Leadership)."
            )
        return _die_problem(values, stress=True)

    return validate


def store_live(character: Character) -> Any:
    """The inspector: the roll and what it needs."""

    def inspect(values: dict[str, Any]) -> str:
        head = f"[b]{escape(character.name)}[/]  [$label]Profession: Apothecary {ap.profession(character)}[/]"
        if (values.get("roll") or SEARCH) == PRESERVE:
            duration = str(values.get("duration") or "Seasons")
            base = ap.preserve_base(character)
            return "\n".join(
                [
                    head,
                    f"Dexterity + Profession [b]{base:+d}[/] + a simple die against "
                    f"[b]{ap.preserve_ease(duration)}[/] to keep it {duration.lower()} "
                    "[dim](A&A p. 64)[/]",
                    "A plant or animal Arcane Connection kept longer than it lasts "
                    "lasts a category longer.",
                ]
            )
        search = _search(values)
        base = ap.search_base(character)
        return "\n".join(
            [
                head,
                f"Perception + Profession [b]{base:+d}[/] + a stress die against "
                f"[b]{search.ease()}[/], a month's search [dim](A&A pp. 65-66)[/]",
                "Success finds a Labor Point's worth, and each point over another "
                "(or halves the time); a botch finds none. What is found pays for "
                "this need only, never the store's Labor Points.",
            ]
        )

    return inspect


def apply_store(
    saga: Saga, character: Character, values: dict[str, Any], rng: random.Random
) -> list[str]:
    ingredient = str(values.get("ingredient") or "").strip()
    if (values.get("roll") or SEARCH) == PRESERVE:
        duration = str(values.get("duration") or "Seasons")
        die, _, shown = _roll(saga, {"die": values.get("simple_die")}, rng, False)
        total = ap.preserve_base(character) + die
        ease = ap.preserve_ease(duration)
        kept = ap.kept_for(total)
        if total >= ease:
            outcome = f"{total} against {ease}: it keeps {duration.lower()}."
        elif kept:
            outcome = f"{total} against {ease}: it keeps only {kept.lower()}."
        else:
            outcome = f"{total} against {ease}: it won't keep even weeks."
        name = f"Preserved: {ingredient}"
        lines = [f"Preserving {ingredient}. Die {shown}.", outcome]
    else:
        search = _search(values)
        ease = search.ease()
        die, botched, shown = _roll(saga, values, rng, stress=True)
        total = ap.search_base(character) + die
        if botched:
            outcome = (
                "A botch: the wrong ground or the wrong time of year; he can't "
                "find it, nor anything to stand in for it."
            )
        elif found := ap.found_points(total, ease):
            outcome = (
                f"{total} against {ease}: {found} Labor Point(s)' worth in a "
                "month (or fewer found sooner, a point over for each halving)."
            )
        else:
            outcome = f"{total} against {ease}: nothing found this month; he may search again."
        name = f"Searched for: {ingredient}"
        lines = [f"Searching for {ingredient}. Die {shown}.", outcome]
    diaries.write(
        saga.current_year,
        saga.current_season,
        name,
        " ".join([*lines, f"Rules: {ap.SOURCE}."]),
        characters=[character],
    )
    return notes(*map(escape, lines), f"Written in {escape(character.name)}'s Diary.")


def store_form(
    saga: Saga, character: Character | None, rng: random.Random | None = None
) -> Command:
    if character is None:
        return Refuse(STORE_TITLE, "Choose a character first.")
    if not ap.keeps_store(character):
        return Refuse(
            STORE_TITLE,
            f"{escape(character.name)} has no Profession: Apothecary: add it on "
            "Abilities first.",
        )
    return Form(
        f"{STORE_TITLE}: {escape(character.name)}",
        lambda: store_fields(saga, character),
        lambda values: apply_store(saga, character, values, rng or random.Random()),
        validate=_store_validate(character),
        live=store_live(character),
        save_label="Roll",
        help_id=STORE_HELP,
        inspector="The Roll",
    )

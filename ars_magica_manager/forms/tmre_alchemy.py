"""More's Philosophic Alchemy on This Season: settling an alchemical vis
extraction to digest beside the magus's other work, or abandoning the one
running; and More's Test the Great Elixir on Aging & Warping -- no UI in
here. The rules and their pages are rules.tmre_alchemy's (The Mysteries
Revised Edition pp. 40-41, 43-44)."""

from __future__ import annotations

import random
from collections.abc import Callable
from typing import Any

from ..commands import Command, Form, Refuse, notes
from ..form_spec import DialogField
from ..markup import BULLET, escape
from ..models import (
    DIGEST_SPACES,
    DIGEST_VIS,
    INVESTED,
    Character,
    DiaryEntry,
    Digestion,
    EnchantedDevice,
    Saga,
)
from ..rules import dice, lab, lab_seasons, lab_virtues
from ..rules import tmre_alchemy as alchemy

TITLE = "Philosophic Alchemy"
HELP = "philosophic-alchemy"
#: Whose raw vis the pawns go to (a lab plan's `vis_from`).
VIS_TO: tuple[tuple[str, str], ...] = (
    ("His own", ""),
    ("The laboratory's", "laboratory"),
    ("The covenant's", "covenant"),
)
#: How a digestion's open spaces count (TMRE p. 41).
SPACES_AS: tuple[tuple[str, str], ...] = (
    ("Pawns already opened (opening costs fewer)", ""),
    ("Extra room on top of its capacity", "extra"),
)


def offers(_saga: Saga, character: Character) -> bool:
    """Whether More offers it: a magus with Philosophic Alchemy."""
    return bool(alchemy.philosophic_tier(character))


def _running(character: Character) -> Digestion | None:
    return character.alchemy.digestion if character.alchemy is not None else None


def devices(saga: Saga, character: Character) -> list[EnchantedDevice]:
    """The invested devices a digestion may open: not yet opened, held by
    the magus or his laboratory."""
    holders = {("character", character.id)}
    if character.assigned_lab_id:
        holders.add(("laboratory", character.assigned_lab_id))
    return [
        d
        for d in saga.enchanted_devices
        if d.type == INVESTED
        and not d.talisman
        and not d.pawns_opened
        and (d.holder_kind, d.holder_id) in holders
    ]


def _products(character: Character) -> list[tuple[str, str]]:
    forms = [
        (
            f"{form} vis (a {'tenth' if lab_virtues.form_extraction_divisor(character, form) == 10 else 'twentieth'})",
            f"vis:{form}",
        )
        for form in lab_virtues.extraction_forms(character)
    ]
    return [
        ("Vim vis", "vis:"),
        *forms,
        ("Open spaces in a device", DIGEST_SPACES),
    ]


def _spaces(values: dict[str, Any]) -> bool:
    return values.get("product") == DIGEST_SPACES


def _vis(values: dict[str, Any]) -> bool:
    return not _spaces(values)


def digestion_fields(saga: Saga, character: Character) -> list[DialogField]:
    running = _running(character)
    if running is not None:
        return [
            DialogField("status", "Running", "info", status(saga, character)),
            DialogField("abandon", "Abandon it", "check", False),
        ]
    found = devices(saga, character)
    return [
        DialogField(
            "product",
            "It makes",
            "select",
            "vis:",
            options=_products(character),
        ),
        DialogField(
            "shape",
            "Vessel's Shape and Material bonus",
            "int",
            0,
            hint="The bonuses of the object the vis settles in (Hermetic "
            f"Alchemy), up to Magic Theory ({lab.shape_material_cap(character)}).",
        ),
        DialogField(
            "vis_from",
            "The pawns go to",
            "select",
            "",
            options=list(VIS_TO),
            show_if=_vis,
        ),
        DialogField(
            "device",
            "Device to open",
            "select",
            found[0].id if found else "",
            options=[(d.name, d.id) for d in found] or [("(none unopened)", "")],
            show_if=_spaces,
            hint="An invested device not yet opened, held by the magus or "
            "his laboratory.",
        ),
        DialogField(
            "spaces_as",
            "The spaces count as",
            "select",
            "",
            options=list(SPACES_AS),
            show_if=_spaces,
            hint="Pawns of its capacity already opened, or room on top of what "
            "it could normally hold (TMRE p. 41).",
        ),
    ]


def _digestion(character: Character, values: dict[str, Any]) -> Digestion:
    product = str(values.get("product") or "vis:")
    spaces = product == DIGEST_SPACES
    device_id = str(values.get("device") or "") if spaces else ""
    return Digestion(
        lab_id=character.assigned_lab_id,
        product=DIGEST_SPACES if spaces else DIGEST_VIS,
        form="" if spaces else product.partition(":")[2],
        shape_bonus=max(0, int(values.get("shape") or 0)),
        device_id=device_id or None,
        extra_room=spaces and values.get("spaces_as") == "extra",
        vis_from=str(values.get("vis_from") or ""),
        season="",
        year=0,
        seasons=alchemy.digestion_seasons(character) or 1,
    )


def _what(digestion: Digestion) -> str:
    if digestion.product == DIGEST_SPACES:
        return "open spaces, extra room" if digestion.extra_room else "open spaces"
    return f"{digestion.form or 'Vim'} vis"


def preview_lines(saga: Saga, character: Character, digestion: Digestion) -> list[str]:
    """The Lab Total the digestion would have this season, and its yield."""
    found, work = lab_seasons.digestion_season(
        saga, character, digestion, saga.current_season, saga.current_year, 0
    )
    if work is None:
        return found
    total = max(0, int(work.lab_total.total))
    pawns = alchemy.pawns_from(total, digestion, character)
    unit = (
        "space(s)"
        if digestion.product == DIGEST_SPACES
        else f"pawn(s) of {_what(digestion)}"
    )
    lines = [f"Lab Total {total} this season: {pawns} {unit}."]
    if digestion.product == DIGEST_SPACES:
        lines.append(f"They count as {alchemy.spaces_text(digestion.extra_room)}.")
    if digestion.seasons > 1:
        lines.append(
            f"It digests for {digestion.seasons} seasons; the lowest season's "
            "Lab Total gives the yield."
        )
    lines.append(
        f"Each season it adds {alchemy.TENDING_DAYS} days' distraction to his "
        "other lab work; more than 20 days away, or experimenting, spoil it "
        f"({alchemy.PHILOSOPHIC_SOURCE})."
    )
    return lines


def status(saga: Saga, character: Character) -> str:
    running = _running(character)
    if running is None:
        return "None."
    done = ", ".join(str(t) for t in running.totals) or "none yet"
    return (
        f"{_what(running)}, settled {running.season} {running.year}: season "
        f"Lab Totals {done} ({len(running.totals)} of {running.seasons})."
    )


def _live(saga: Saga, character: Character) -> Callable[[dict[str, Any]], str]:
    def live(values: dict[str, Any]) -> str:
        if _running(character) is not None:
            lines = (
                ["Abandoned, it gives nothing."]
                if values.get("abandon")
                else [status(saga, character)]
            )
        else:
            lines = preview_lines(saga, character, _digestion(character, values))
        return "\n".join(f"{BULLET} {escape(line)}" for line in lines)

    return live


def _validate(
    saga: Saga, character: Character
) -> Callable[[dict[str, Any]], str | None]:
    def validate(values: dict[str, Any]) -> str | None:
        if _running(character) is not None:
            return None
        if int(values.get("shape") or 0) < 0:
            return "The bonus can't be below 0."
        if _spaces(values) and not values.get("device"):
            return "Choose the device the spaces open (record it on Inventory first)."
        return None

    return validate


def record(saga: Saga, character: Character, values: dict[str, Any]) -> list[str]:
    """Settle the digestion in the current season, or abandon the one
    running; a Diary entry either way."""
    running = _running(character)
    if running is not None:
        if not values.get("abandon"):
            return notes("Nothing changed.")
        alchemy.abandon(character)
        text = f"Abandoned the digestion ({_what(running)})."
    else:
        digestion = alchemy.start(
            character,
            _digestion(character, values),
            saga.current_season,
            saga.current_year,
        )
        text = (
            f"Settled a digestion ({_what(digestion)}) for {digestion.seasons} "
            f"season(s) from {digestion.season} {digestion.year}."
        )
    character.diary.append(
        DiaryEntry(saga.current_year, saga.current_season, TITLE, text)
    )
    return notes(escape(text))


def digestion_form(saga: Saga, character: Character | None) -> Command:
    """More's Philosophic Alchemy: settle a digestion, or abandon it."""
    if character is None:
        return Refuse(TITLE, "Choose a character first.")
    if not offers(saga, character):
        return Refuse(
            TITLE,
            f"{escape(character.name)} hasn't Philosophic Alchemy "
            f"({alchemy.PHILOSOPHIC_SOURCE}).",
        )
    if _running(character) is None:
        why = alchemy.digest_problem(character)
        if why:
            return Refuse(TITLE, escape(why))
        if (
            not character.assigned_lab_id
            or saga.laboratory(character.assigned_lab_id) is None
        ):
            return Refuse(
                TITLE, f"{escape(character.name)} needs a laboratory to work in."
            )
    magus = character
    return Form(
        f"{TITLE}: {escape(magus.name)}",
        lambda: digestion_fields(saga, magus),
        lambda values: record(saga, magus, values),
        validate=_validate(saga, magus),
        live=_live(saga, magus),
        help_id=HELP,
        inspector="The Digestion",
    )


# -- The Great Elixir's test ----------------------------------------------------

GREAT_TITLE = "Test the Great Elixir"
GREAT_HELP = "great-elixir"


def great_fields(character: Character) -> list[DialogField]:
    return [
        DialogField(
            "grant_level",
            "Grant Might's level",
            "int",
            0,
            hint="The level of the Grant Might effect invested in this potion: "
            "Magic Might is half of (level - 20) (TMRE p. 44).",
        ),
        DialogField(
            "die",
            "Die",
            "optint",
            None,
            placeholder="(blank: the app rolls it)",
            hint="A simple die.",
        ),
    ]


def _great_validate(values: dict[str, Any]) -> str | None:
    if int(values.get("grant_level") or 0) < 0:
        return "A level can't be below 0."
    die = values.get("die")
    if die is not None and not 1 <= int(die) <= 10:
        return "A simple die shows 1 to 10."
    return None


def _great_live(character: Character, age: int) -> Callable[[dict[str, Any]], str]:
    def live(values: dict[str, Any]) -> str:
        level = max(0, int(values.get("grant_level") or 0))
        test = alchemy.great_test(character, age, 0, level)
        bonus = sum(line.amount or 0 for line in test.lines)
        parts = " + ".join(f"{escape(line.label)} {line.amount}" for line in test.lines)
        lines = [
            f"Simple die + {parts} = die + {bonus}, against Ease Factor "
            f"{test.ease} (age {alchemy.great_ease_basis(character, age)} / 10, "
            "rounded up).",
            f"Grant Might level {level}: Magic Might {test.might}.",
            "Success: he becomes a being of Magic, no longer aging nor gaining "
            "Warping; failure wastes the potion, and the next adds 1 more (at "
            f"most Magic Theory {alchemy.magic_theory(character)}).",
        ]
        if alchemy.transformed(character):
            lines.insert(
                0,
                f"Already immortal (Magic Might {character.magic_might}): a "
                "better potion raises his Might.",
            )
        return "\n".join(f"{BULLET} {line}" for line in lines)

    return live


def record_great(
    saga: Saga,
    character: Character,
    age: int,
    values: dict[str, Any],
    rng: random.Random,
) -> list[str]:
    """Roll (or take) the die, apply the test, and write it in the Diary."""
    typed = values.get("die")
    die = int(typed) if typed is not None else dice.simple_die(rng)
    level = max(0, int(values.get("grant_level") or 0))
    test = alchemy.great_test(character, age, die, level)
    outcome = alchemy.drink_great_elixir(character, age, test)
    text = (
        f"Die {die} + {test.total - die} = {test.total} against Ease Factor "
        f"{test.ease} (Grant Might level {level}). {outcome}"
    )
    character.diary.append(
        DiaryEntry(saga.current_year, saga.current_season, "The Great Elixir", text)
    )
    return notes(escape(text))


def great_elixir_form(
    saga: Saga, character: Character | None, rng: random.Random | None = None
) -> Command:
    """More's Test the Great Elixir: the potion drunk and tested."""
    if character is None:
        return Refuse(GREAT_TITLE, "Choose a character first.")
    why = alchemy.great_elixir_problem(character)
    if why:
        return Refuse(GREAT_TITLE, escape(why))
    age = lab_seasons.age_of(saga, character)
    if age is None:
        return Refuse(
            GREAT_TITLE,
            f"Set {escape(character.name)}'s Year Born: the Ease Factor is by age.",
        )
    magus, dice_ = character, rng or random.Random()
    return Form(
        f"{GREAT_TITLE}: {escape(magus.name)}",
        lambda: great_fields(magus),
        lambda values: record_great(saga, magus, age, values, dice_),
        validate=_great_validate,
        live=_great_live(magus, age),
        save_label="Roll",
        help_id=GREAT_HELP,
        inspector="The Great Elixir",
    )

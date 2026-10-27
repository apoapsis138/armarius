"""More's Cross the Threshold on a place with a Faerie aura: the
Threshold points a set of circumstances gathers against the place's
Threshold strength, and whether the travelers cross into the Faerie
Realm (rules.faerie_threshold; Realms of Power: Faerie pp. 20-24). The
attempt is written in the place's Diary, so the same circumstances aren't
tried twice before the next moonrise.

Pattern: a commands.Form over the place; the counting is
rules.faerie_threshold's plain functions.
"""

from __future__ import annotations

from typing import Any

from .. import catalog, place_events, sourcebooks
from ..commands import Command, Form, Refuse, notes
from ..form_spec import DialogField
from ..markup import escape
from ..models import Neighbour, Saga
from ..rules import faerie_threshold as ft
from ..rules import sites

TITLE = "Cross the Threshold"
HELP_ID = "cross-threshold"


def _levels(place: Neighbour) -> list[tuple[str, str]]:
    """The place's Faerie levels a crossing may start from."""
    found = []
    for level in range(len(sites.levels(place)) + 1):
        if sites.world_at(place, level):
            continue
        _aura, realm = sites.aura_at(place, level)
        if realm == "Faerie":
            found.append(
                ("The surface" if level == 0 else f"Level {level}", str(level))
            )
    return found


def strength(place: Neighbour, level: int) -> int:
    aura, realm = sites.aura_at(place, level)
    base = sites.aura_at(place, 0) if level else (0, "")
    return ft.threshold_strength(aura, realm, *base)


def fields(saga: Saga, place: Neighbour) -> list[DialogField]:
    levels = _levels(place)
    people = [(escape(c.name), c.id) for c in saga.characters]
    return [
        DialogField("level", "From", "select", levels[0][1], options=levels),
        DialogField(
            "focal",
            "Who leads the crossing",
            "select",
            None,
            options=people,
            allow_blank=True,
            placeholder="(no one in particular)",
            hint="His faerie Virtues and Flaws count from his sheet; his "
            "emotion and life change are asked.",
        ),
        DialogField(
            "border",
            "Border crossed",
            "select",
            None,
            options=[(f"{k} ({v})", k) for k, v in ft.BORDERS.items()],
            allow_blank=True,
            placeholder="(none)",
        ),
        DialogField("lost", "Crossed while truly lost (+3)", "check", False),
        DialogField(
            "time",
            "The time",
            "select",
            None,
            options=[(f"{k} ({v})", k) for k, v in ft.TIMES.items()],
            allow_blank=True,
            placeholder="(nothing special)",
        ),
        DialogField(
            "emotion",
            "Emotion's Trait",
            "optint",
            None,
            hint="Blank for none; 3 + the Trait (a Minor Personality Flaw +3, a "
            "Major +6).",
        ),
        DialogField(
            "life_change",
            "His life change",
            "select",
            None,
            options=[(f"{k} ({v})", k) for k, v in ft.LIFE_CHANGES.items()],
            allow_blank=True,
            placeholder="(none)",
        ),
        DialogField(
            "art",
            "Art's Aesthetic Quality",
            "int",
            0,
            hint="A work of art that commemorates Faerie, seen or performed by "
            "the travelers.",
        ),
        DialogField(
            "spirit_away",
            "Spirit Away points",
            "int",
            0,
            hint="A Might Point a point; never the only source.",
        ),
        DialogField(
            "charm",
            "Arcadian Travel charm",
            "int",
            0,
            hint="Stress die + Perception + the Ability + aura, once the charm is "
            f"made (Ease Factor {ft.CHARM_EASE}).",
        ),
        DialogField(
            "faerie",
            "A faerie's Might magnitude",
            "int",
            0,
        ),
    ]


def points(saga: Saga, values: dict[str, Any]) -> int:
    focal = saga.character(values.get("focal"))
    emotion = values.get("emotion")
    personal = (
        ft.character_points(
            focal,
            catalog.load_virtue_flaw_catalog_by_id(),
            emotion_trait=emotion if isinstance(emotion, int) else None,
            life_change=str(values.get("life_change") or ""),
        )
        if focal is not None
        else ft.personal_points(
            emotion_trait=emotion if isinstance(emotion, int) else None,
            life_change=str(values.get("life_change") or ""),
        )
    )
    return ft.threshold_points(
        border=str(values.get("border") or ""),
        lost=bool(values.get("lost")),
        time=str(values.get("time") or ""),
        personal=personal,
        art_quality=int(values.get("art") or 0),
        spirit_away=int(values.get("spirit_away") or 0),
        charm=int(values.get("charm") or 0),
        faerie_magnitude=int(values.get("faerie") or 0),
    )


def live(saga: Saga, place: Neighbour) -> Any:
    def inspect(values: dict[str, Any]) -> str:
        need = strength(place, int(values.get("level") or 0))
        got = points(saga, values)
        verdict = "the Threshold comes" if ft.crosses(got, need) else "not enough"
        return escape(
            f"{got} Threshold points against a strength of {need}: {verdict}."
        )

    return inspect


def apply(saga: Saga, place: Neighbour, values: dict[str, Any]) -> list[str]:
    need = strength(place, int(values.get("level") or 0))
    got = points(saga, values)
    if ft.crosses(got, need):
        lines = [
            f"{got} Threshold points against {need}: the Threshold comes. The "
            f"Guardian of the Threshold stands before them, its Faerie Might at "
            f"least {ft.guardian_might(got)}; Intelligence + Faerie Lore against "
            f"{ft.GUARDIAN_HINT_EASE} gives hints of the way (RoP: Faerie p. 24).",
        ]
    else:
        lines = [
            f"{got} Threshold points against {need}: the Threshold doesn't come. "
            "These circumstances can't open it: change one and try again no "
            "sooner than the next moonrise (RoP: Faerie p. 21).",
        ]
    place_events.diary(place).append(
        {
            "year": saga.current_year,
            "season": saga.current_season,
            "text": f"{TITLE}: " + " ".join(lines),
        }
    )
    return notes(*map(escape, lines))


def threshold_form(saga: Saga, place: Neighbour | None) -> Command:
    if place is None or not sites.is_place(place) or not _levels(place):
        return Refuse(TITLE, "Choose a place with a Faerie aura first.")
    return Form(
        f"{TITLE}: {escape(place.name)}",
        lambda: fields(saga, place),
        lambda values: apply(saga, place, values),
        live=live(saga, place),
        save_label="Try",
        help_id=HELP_ID,
    )


def offers(saga: Saga, place: Neighbour) -> bool:
    """A place with a Faerie aura, while Realms of Power: Faerie is in play."""
    return (
        sourcebooks.in_play("RoP:F", sourcebooks.saga_books(saga))
        and sites.is_place(place)
        and bool(_levels(place))
    )

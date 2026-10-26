"""The season form's fields for Art & Academe's artists and scholars: a
work of art's kind, bonuses and risks (Create a Work of Art), the post a
scholar seeks, and the lecture commentary he edits -- no UI in here. The
rules and their pages are rules.artistry's (pp. 123-135) and
rules.scholarship's (pp. 79-89, 102-103); the seasons are
rules.season_work.academe's."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .. import book_kinds
from ..form_spec import ChoiceReads, DialogField
from ..markup import escape
from ..models import ART_WOUNDS, REALMS, ArtworkPlan, Character, Saga, SeasonPlan
from ..rules import artistry, scholarship
from ..rules.season_work import academe

CREATE_ART = "create_art"
ShowIf = Callable[[dict[str, Any]], bool]
ActivityIs = Callable[..., ShowIf]


def _both(first: ShowIf, second: ShowIf) -> ShowIf:
    return lambda values: first(values) and second(values)


def _sized(values: dict[str, Any]) -> bool:
    return (values.get("art_base") or "season") in ("years", "decades")


def _artwork_fields(
    character: Character, plan: SeasonPlan | None, activity_is: ActivityIs
) -> list[DialogField]:
    art = (plan.artwork if plan else None) or ArtworkPlan()
    on = activity_is(CREATE_ART)
    ids = {vf.vf_id for vf in character.virtues_flaws}
    found = [
        DialogField(
            "art_base",
            "Kind of piece",
            "select",
            art.base,
            options=[(label, key) for key, label in artistry.BASE_LABELS.items()],
            show_if=on,
            hint="Its base time; the Aesthetic Quality / 10 (rounded up) "
            "multiplies it (A&A p. 124).",
        ),
        DialogField(
            "art_size",
            "Its Size",
            "int",
            art.size,
            show_if=_both(on, _sized),
        ),
        DialogField(
            "art_assistants",
            "Assistants",
            "int",
            art.assistants,
            show_if=on,
            hint=f"At most his Leadership ({artistry.most_assistants(character)}); "
            "they cut the time to no less than half (A&A p. 125).",
        ),
        DialogField(
            "art_double", "Twice the time (+1)", "check", art.double_time, show_if=on
        ),
        DialogField(
            "art_overtime",
            "Overtime (+1)",
            "check",
            art.overtime,
            show_if=on,
            hint="An Aging roll when the piece is done.",
        ),
        DialogField(
            "art_liberal",
            "Uses a liberal art",
            "check",
            art.liberal_arts,
            show_if=on,
            hint="+ Artes Liberales / 3, rounded up.",
        ),
        DialogField(
            "art_rushed",
            "Half the time (Quality / 2)",
            "check",
            art.rushed,
            show_if=on,
        ),
        DialogField(
            "art_experiment",
            "Experiment",
            "check",
            art.experiment,
            show_if=on,
            hint="+ a simple die / 2, and a stress die on the experimentation "
            "table, rolled in the season it is finished (A&A p. 124).",
        ),
        DialogField(
            "art_muse",
            "A muse's Might given",
            "int",
            art.muse_might,
            show_if=on,
            hint="+1 per 5 points a muse sacrifices (A&A p. 124).",
        ),
    ]
    if artistry.LIFE_LINKED in ids:
        found.append(
            DialogField(
                "art_wound",
                "Self-inflicted wound",
                "select",
                art.wound,
                options=[(w or "(none)", w) for w in ART_WOUNDS],
                show_if=on,
                hint="Life-Linked Art: +1 Light, +3 Medium, +6 Heavy; it won't "
                "heal until the piece is done (A&A p. 134).",
            )
        )
    if artistry.MAESTRO in ids:
        found += [
            DialogField(
                "art_realm",
                "His realm",
                "select",
                art.realm or None,
                options=[(r, r) for r in REALMS],
                allow_blank=True,
                show_if=on,
                hint="The realm the maestro is aligned with.",
            ),
            DialogField(
                "art_aura",
                "Aura where he works",
                "int",
                art.aura,
                show_if=on,
                hint="Its own realm's: + aura / 5, rounded up (A&A p. 124).",
            ),
            DialogField(
                "art_aura_realm",
                "Its realm",
                "select",
                art.aura_realm or None,
                options=[(r, r) for r in REALMS],
                allow_blank=True,
                show_if=on,
            ),
        ]
    if artistry.inclination_form(character):
        found.append(
            DialogField(
                "art_instill",
                "Instill an effect of level",
                "int",
                art.instill_level,
                show_if=on,
                hint=f"A Personal, constant {artistry.inclination_form(character)} "
                "effect, no requisites; 0 for none (A&A p. 135).",
            )
        )
    return found


def _scholar_fields(
    saga: Saga, character: Character, plan: SeasonPlan | None, activity_is: ActivityIs
) -> list[DialogField]:
    title = (plan.title if plan else "") or None
    lectures = [
        b
        for b in saga.books
        if b.opus == book_kinds.LECTURE_COMMENTARY
        and b.author_id == character.id
        and not b.glossed
    ]
    return [
        DialogField(
            "post",
            "Post",
            "select",
            title if title in scholarship.POSTS else None,
            options=[
                (f"{label} ({ease})", key)
                for key, (label, ease, _a, _n) in scholarship.POSTS.items()
            ],
            allow_blank=True,
            show_if=activity_is(academe.SEEK_POST),
        ),
        DialogField(
            "lectures_id",
            "Lecture commentary",
            "select",
            plan.book_id if plan else None,
            options=[(escape(b.name), b.id) for b in lectures],
            allow_blank=True,
            placeholder="(none of his not yet edited)",
            show_if=activity_is(academe.EDIT_LECTURES),
        ),
    ]


def fields(
    saga: Saga, character: Character, plan: SeasonPlan | None, activity_is: ActivityIs
) -> list[DialogField]:
    """The season form's fields for works of art and scholars' seasons."""
    return [
        *_artwork_fields(character, plan, activity_is),
        *_scholar_fields(saga, character, plan, activity_is),
    ]


def _number(values: dict[str, Any], key: str, default: int = 0) -> int:
    value = values.get(key)
    return default if value is None else int(value)


def artwork_from(values: dict[str, Any]) -> ArtworkPlan:
    """The work of art's plan from the form's values."""
    return ArtworkPlan(
        base=values.get("art_base") or "season",
        size=max(1, _number(values, "art_size", 1)),
        assistants=max(0, _number(values, "art_assistants")),
        double_time=bool(values.get("art_double")),
        overtime=bool(values.get("art_overtime")),
        liberal_arts=bool(values.get("art_liberal")),
        rushed=bool(values.get("art_rushed")),
        experiment=bool(values.get("art_experiment")),
        muse_might=max(0, _number(values, "art_muse")),
        wound=values.get("art_wound") or "",
        realm=values.get("art_realm") or "",
        aura=max(0, _number(values, "art_aura")),
        aura_realm=values.get("art_aura_realm") or "",
        instill_level=max(0, _number(values, "art_instill")),
    )


#: The plan's fields these seasons set from the form (as _SEASON_READS).
READS: ChoiceReads = (
    ((CREATE_ART,), lambda v: {"artwork": artwork_from(v)}),
    ((academe.SEEK_POST,), lambda v: {"title": v.get("post") or ""}),
    ((academe.EDIT_LECTURES,), lambda v: {"book_id": v.get("lectures_id")}),
)

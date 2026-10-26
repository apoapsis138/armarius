"""More's Pilgrimage on This Season: a pilgrimage begun, an Oppositional
Element overcome or failed on its road, and its aim claimed once its
Target Level is reached -- a Virtue gained, a Flaw lost, a Personality
Trait removed, Holy Magic, or a penance or miracle written in the Diary.
No UI in here. The rules and their pages are rules.pilgrimage's (The
Church pp. 15-19); each season on the road is the Pilgrimage activity's
(season_work.church)."""

from __future__ import annotations

from typing import Any

from .. import catalog, diaries, sourcebooks
from ..commands import Command, Form, Refuse, notes
from ..form_spec import DialogField
from ..markup import BULLET, escape
from ..models import Character, Progress, Saga, VirtueFlawDef, VirtueFlawInstance
from ..rules import creation_characteristics as cch
from ..rules import pilgrimage as pil

TITLE = "Pilgrimage"
HELP_ID = "pilgrimage-more"
BEGIN, OVERCOME, FAILED, CLAIM = "begin", "overcome", "failed", "claim"
#: The Church, the book the rules come from.
BOOK = "TC"


def in_play(saga: Saga) -> bool:
    return sourcebooks.in_play(BOOK, sourcebooks.saga_books(saga))


def _is(*whats: str) -> Any:
    return lambda values: (values.get("what") or BEGIN) in whats


def _catalog(saga: Saga) -> list[VirtueFlawDef]:
    books = sourcebooks.saga_books(saga)
    return [
        d
        for d in catalog.load_virtue_flaw_catalog()
        if sourcebooks.in_play(d.source, books)
    ]


def _record(character: Character, values: dict[str, Any]) -> Progress | None:
    return pil.find(character, str(values.get("pilgrimage") or ""))


def _target_is(character: Character, target: int) -> Any:
    def test(values: dict[str, Any]) -> bool:
        record = _record(character, values)
        return record is not None and record.target == target

    return test


def _aim_is(character: Character, aim: str, target: int) -> Any:
    target_is = _target_is(character, target)
    return lambda values: (
        _is(CLAIM)(values) and values.get("aim") == aim and target_is(values)
    )


def _vf_value(instance: VirtueFlawInstance, index: int) -> str:
    return f"{index}:{instance.vf_id}"


def pilgrimage_fields(saga: Saga, character: Character) -> list[DialogField]:
    """What Pilgrimage asks."""
    records = pil.pilgrimages(character)
    whats = [("Begin a pilgrimage", BEGIN)]
    if records:
        whats += [
            ("An Oppositional Element overcome", OVERCOME),
            ("An Oppositional Element failed", FAILED),
            ("Claim the pilgrimage's aim", CLAIM),
        ]
    elements = [(f"+{e.value}: {e.label}", e.key) for e in pil.ELEMENTS] + [
        (
            f"+{value}: {pil.element_label(key)} (once, the higher only)",
            key,
        )
        for key, value in pil.TRAVEL.items()
    ]
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    fields = [
        DialogField(
            "what",
            "What",
            "select",
            BEGIN if not records else OVERCOME,
            options=whats,
            required=True,
        ),
        DialogField(
            "name",
            "Pilgrimage's name",
            "text",
            "",
            placeholder="its destination and aim: Santiago, to lose Lycanthrope",
            show_if=_is(BEGIN),
        ),
        DialogField(
            "target",
            "Target Level",
            "select",
            str(pil.MINOR),
            options=[
                (f"{pil.MINOR} (a minor pilgrimage: one season, one story)", "18"),
                (f"{pil.MAJOR} (a major pilgrimage: several seasons)", "30"),
            ],
            show_if=_is(BEGIN),
        ),
    ]
    if records:
        fields += [
            DialogField(
                "pilgrimage",
                "The pilgrimage",
                "select",
                records[0].name,
                options=[
                    (f"{r.name} ({r.points} of {r.target})", r.name) for r in records
                ],
                show_if=_is(OVERCOME, FAILED, CLAIM),
            ),
            DialogField(
                "element",
                "Oppositional Element",
                "select",
                pil.ELEMENTS[0].key,
                options=elements,
                show_if=_is(OVERCOME, FAILED),
                hint="Each season on the road is +3, counted with the season.",
            ),
            DialogField(
                "aim",
                "Aim",
                "select",
                pil.GAIN_VIRTUE,
                options=[(label, key) for key, (label, _levels) in pil.AIMS.items()],
                show_if=_is(CLAIM),
                hint="Remove a trait: 18 only; a miracle or Holy Magic: 30 only.",
            ),
        ]
        for target in pil.TARGETS:
            size = pil.tier(target)
            fields.append(
                DialogField(
                    f"virtue_{target}",
                    f"{size} Virtue gained",
                    "select",
                    None,
                    options=[
                        (f"{d.name} ({d.category})", d.id)
                        for d in pil.gainable(character, _catalog(saga), target)
                    ],
                    allow_blank=True,
                    show_if=_aim_is(character, pil.GAIN_VIRTUE, target),
                    hint="Usually one aligned with the Divine; never Hermetic "
                    "or a background Virtue (TC p. 16).",
                )
            )
            fields.append(
                DialogField(
                    f"vf_{target}",
                    f"{size} Flaw or Virtue lost",
                    "select",
                    None,
                    options=[
                        (by_id[vf.vf_id].name, _vf_value(vf, index))
                        for index, vf in enumerate(character.virtues_flaws)
                        if vf in pil.losable(character, by_id, target)
                    ],
                    allow_blank=True,
                    show_if=_aim_is(character, pil.LOSE_VF, target),
                )
            )
        fields.append(
            DialogField(
                "trait",
                "Personality Trait removed",
                "select",
                None,
                options=[
                    (f"{t.name} {t.score:+d}", t.name)
                    for t in pil.removable_traits(character)
                ],
                allow_blank=True,
                show_if=_aim_is(character, pil.LOSE_TRAIT, pil.MINOR),
                hint="A negative score, or a trait leaning to a sin (TC p. 20); "
                "any other is the troupe's call.",
            )
        )
        fields.append(
            DialogField(
                "detail",
                "The penance or miracle",
                "text",
                "",
                show_if=lambda v: (
                    _is(CLAIM)(v) and v.get("aim") in (pil.PENANCE, pil.MIRACLE)
                ),
            )
        )
    return fields


def _validate(character: Character) -> Any:
    def check(values: dict[str, Any]) -> str | None:
        what = values.get("what") or BEGIN
        if what == BEGIN:
            name = str(values.get("name") or "").strip()
            if not name:
                return "Name the pilgrimage."
            if pil.find(character, name) is not None:
                return f"{name} is already under way."
            return None
        record = _record(character, values)
        if record is None:
            return "Choose the pilgrimage."
        if what != CLAIM:
            return None
        problem = pil.claim_problem(character, record)
        if problem:
            return problem
        aim = str(values.get("aim") or pil.GAIN_VIRTUE)
        if record.target not in pil.AIMS[aim][1]:
            return f"{pil.AIMS[aim][0]} isn't an aim of a {record.target} pilgrimage."
        if aim == pil.HOLY_MAGIC:
            return pil.holy_magic_problem(character)
        if aim == pil.GAIN_VIRTUE and not values.get(f"virtue_{record.target}"):
            return "Choose the Virtue gained."
        if aim == pil.LOSE_VF and not values.get(f"vf_{record.target}"):
            return "Choose the Flaw (or Virtue) lost."
        if aim == pil.LOSE_TRAIT and not values.get("trait"):
            return "Choose the Personality Trait removed."
        return None

    return check


def lines(character: Character, values: dict[str, Any]) -> list[str]:
    """What the choice will do, plain."""
    what = values.get("what") or BEGIN
    if what == BEGIN:
        target = int(str(values.get("target") or pil.MINOR))
        return [
            f"Target Level {target}: Oppositional Elements worth {target} in all, "
            f"each season on the road +{pil.SEASON_VALUE} (TC pp. 16-17).",
            "Aims: " + ", ".join(label for label, _key in pil.aims_for(target)) + ".",
        ]
    record = _record(character, values)
    if record is None:
        return ["Choose the pilgrimage."]
    said = [f"{record.name}: {record.points} of {record.target}."]
    counted = pil.travel_counted(character, record.name)
    if counted:
        said.append(f"Travel counted: +{counted}.")
    if pil.failures(character, record.name):
        said.append(
            f"{pil.failures(character, record.name)} element(s) failed, not yet "
            "remedied."
        )
    if what in (OVERCOME, FAILED):
        key = str(values.get("element") or pil.ELEMENTS[0].key)
        value = (
            pil.travel_gain(counted, key)
            if key in pil.TRAVEL
            else pil.element_value(key)
        )
        if what == OVERCOME:
            said.append(
                f"Overcome: +{value}, to {record.points + value} of {record.target}."
            )
        else:
            said.append("Failed: the aim fails unless a later element remedies it.")
    else:
        problem = pil.claim_problem(character, record)
        said.append(problem or "Reached: the aim may be claimed.")
        said.append("The troupe must agree the aim suits him (TC p. 16).")
        said.append(
            "He must have avoided mortal sin on the road, and confess his venial "
            "sins on arrival (TC p. 18)."
        )
    said.append(
        "At a saint's shrine, one Devoted to the saint gains "
        f"{pil.SHRINE_DEVOTION} Devotion Points, +{pil.SITE_DEVOTION} a further site, "
        f"up to {pil.MOST_RELIC_DEVOTION} for relics (TC p. 19)."
    )
    return said


def _live(character: Character) -> Any:
    def live(values: dict[str, Any]) -> str:
        return "\n".join(
            f"{BULLET} {escape(line)}" for line in lines(character, values)
        )

    return live


def _claim(
    saga: Saga, character: Character, record: Progress, values: dict[str, Any]
) -> str:
    aim = str(values.get("aim") or pil.GAIN_VIRTUE)
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    if aim == pil.GAIN_VIRTUE:
        vf_id = str(values.get(f"virtue_{record.target}"))
        instance = VirtueFlawInstance(vf_id)
        character.virtues_flaws.append(instance)
        cch.apply_virtue(saga, character, instance)
        done = f"He gains {by_id[vf_id].name}."
        ability = pil.grant_ability(character, by_id[vf_id])
        if ability is not None:
            done += (
                f" {ability.name} starts at {pil.GAINED_ABILITY_SCORE}, without "
                "the Gift's penalty."
            )
    elif aim == pil.HOLY_MAGIC:
        instance = VirtueFlawInstance("vf_holy_magic")
        character.virtues_flaws.append(instance)
        done = "He initiates himself in Holy Magic."
    elif aim == pil.LOSE_VF:
        index_text, _, vf_id = str(values.get(f"vf_{record.target}")).partition(":")
        index = int(index_text)
        instance = character.virtues_flaws[index]
        if instance.vf_id != vf_id:
            raise LookupError(f"{vf_id} is no longer at that place.")
        cch.unapply_virtue(saga, character, instance)
        character.virtues_flaws.pop(index)
        done = f"He loses {by_id[vf_id].name}."
    elif aim == pil.LOSE_TRAIT:
        name = str(values.get("trait"))
        character.personality_traits = [
            t for t in character.personality_traits if t.name != name
        ]
        done = f"His {name} is gone."
    else:
        detail = str(values.get("detail") or "").strip()
        label = pil.AIMS[aim][0]
        done = f"{label}: {detail}." if detail else f"{label}: the troupe judges it."
    pil.claim(record)
    return done


def apply_pilgrimage(
    saga: Saga, character: Character, values: dict[str, Any]
) -> list[str]:
    what = values.get("what") or BEGIN
    if what == BEGIN:
        name = str(values.get("name") or "").strip()
        target = int(str(values.get("target") or pil.MINOR))
        character.progress.append(Progress(pil.KIND, name, target))
        heading, line = (
            f"Pilgrimage begun: {name}",
            f"Target Level {target}: its Oppositional Elements must reach it.",
        )
    else:
        record = _record(character, values)
        if record is None:
            raise LookupError("That pilgrimage is no longer under way.")
        key = str(values.get("element") or pil.ELEMENTS[0].key)
        if what == OVERCOME:
            _gained, said = pil.overcome(record, character, key)
            heading, line = (
                f"Pilgrimage: {record.name}",
                (f"{pil.element_label(key)} overcome: {said}"),
            )
        elif what == FAILED:
            heading, line = (
                f"Pilgrimage: {record.name}",
                (f"{pil.element_label(key)}: {pil.failed(character, record)}"),
            )
        else:
            heading = f"Pilgrimage's aim: {record.name}"
            line = _claim(saga, character, record, values)
    diaries.write(
        saga.current_year,
        saga.current_season,
        heading,
        f"{line} Rules: {pil.SOURCE}.",
        characters=[character],
    )
    return notes(escape(line), f"Written in {escape(character.name)}'s Diary.")


def pilgrimage_form(saga: Saga, character: Character | None) -> Command:
    if character is None:
        return Refuse(TITLE, "Choose a character first.")
    if not in_play(saga):
        return Refuse(TITLE, "The Church isn't in play in this saga.")
    return Form(
        f"{TITLE}: {escape(character.name)}",
        lambda: pilgrimage_fields(saga, character),
        lambda values: apply_pilgrimage(saga, character, values),
        validate=_validate(character),
        live=_live(character),
        help_id=HELP_ID,
        inspector="The Road",
    )

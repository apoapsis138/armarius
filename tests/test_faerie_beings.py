"""Faerie beings and powers: Sympathy Traits and Faerie Rank (RoP: Faerie
pp. 102-104, Errata p. 68), the Olympians' Sympathy Traits (The Sundered
Eagle p. 127), the faerie rites' guidelines and Faerie Ranges, Durations
and Targets (RoP: Faerie pp. 121-131, checked against the book's own
rites), and a faerie's role and the story it wants (pp. 40, 140-142)."""

from __future__ import annotations

import random
from dataclasses import asdict

import pytest

from ars_magica_manager import catalog, commands, form_spec, tradition_text
from ars_magica_manager.forms import creature as creature_forms
from ars_magica_manager.forms import trait as trait_forms
from ars_magica_manager.forms import virtue as virtue_forms
from ars_magica_manager.models import (
    Character,
    Creature,
    Saga,
    ScoredTrait,
    TraditionDef,
    TraditionEffect,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import (
    faerie_blood,
    faerie_build,
    faerie_rites,
    realm_warping,
)
from ars_magica_manager.rules import faerie_sympathy as fs
from ars_magica_manager.rules import hedge_effects as he
from ars_magica_manager.sheets import creature as creature_sheet
from ars_magica_manager.sheets.character import aging_text

#: Each rite tradition and the Faerie Powers its catalog entry lists:
#: their guidelines are its.
RITE_TRADITIONS = {
    "trad_ollamhain": {"Beguile", "Dream", "Portage"},
    "trad_volkhvy": {"Conjure", "Grant"},
    "trad_wise_folk": {"Ware", "Weal", "Woe"},
}


def _trad_for(power: str) -> str:
    return next(t for t, powers in RITE_TRADITIONS.items() if power in powers)


def _sym(name: str, score: int) -> ScoredTrait:
    return ScoredTrait(name, score, type=fs.SYMPATHY)


# -- Sympathy Traits and Faerie Rank --


def test_faerie_rank_is_the_best_positive_plus_the_worst_negative():
    # The book's examples (p. 103).
    assert fs.faerie_rank([_sym("Winter", 4), _sym("Summer", -2)]) == 2
    assert fs.faerie_rank([_sym("Dancing", 1), _sym("Stone", -5)]) == -4
    assert fs.faerie_rank([_sym("Oak", 3)]) == 3
    # A plain Personality Trait isn't a Sympathy Trait.
    assert fs.faerie_rank([ScoredTrait("Brave", 3)]) is None
    assert fs.extra_botch_dice([_sym("Iron", -3), _sym("Oak", 2)]) == 3


def test_a_temporary_sympathy_trait_works_but_is_not_in_the_rank():
    # From sympathetic influence or a Grant rite (pp. 103-105, 127).
    oak = ScoredTrait("Oak", 2, type=fs.TEMPORARY)
    iron = ScoredTrait("Iron", -3, type=fs.TEMPORARY)
    assert fs.is_sympathy(oak) and fs.is_temporary(oak)
    assert fs.faerie_rank([_sym("Winter", 1), oak]) == 1
    assert fs.faerie_rank([oak]) is None
    # Its negative still adds botch dice, and it counts for a rite.
    assert fs.extra_botch_dice([iron]) == 3
    assert faerie_rites.sympathy_points([_sym("Winter", 1), oak, iron]) == 6
    text = fs.rank_text([_sym("Winter", 1), oak], 2)
    assert "Faerie Rank: +1 (Sympathy Traits Winter +1)" in text
    assert "temporary Oak +2 (not in the Rank" in text
    assert fs.rank_text([oak], 2).startswith("Faerie Rank: none; temporary Oak +2")


def test_raising_a_sympathy_trait():
    assert fs.xp_to_raise(0) == 5
    assert fs.xp_to_raise(2) == 15
    # A negative one: 10 from -1 to 0, 15 from -2, 20 from -3 (p. 103).
    assert [fs.xp_to_raise(s) for s in (-1, -2, -3)] == [10, 15, 20]
    # To no more than the Warping Score; a negative one while Warping is
    # above its size; and through 0 (Errata p. 68).
    assert fs.can_raise(1, 2) and not fs.can_raise(2, 2)
    assert fs.can_raise(-1, 2) and not fs.can_raise(-2, 2)
    assert fs.can_raise(0, 1)


def test_sympathetic_influence():
    assert [fs.influence_value(t) for t in (8, 9, 15, 23, 24, 40)] == [
        0,
        1,
        2,
        2,
        3,
        3,
    ]


def test_the_sheet_shows_the_faerie_rank():
    person = Character(id="p", name="Brigid", type="companion")
    saga = Saga(id="s", name="S", characters=[person])
    assert "Faerie Rank" not in aging_text(person, saga)
    person.personality_traits = [
        ScoredTrait("Brave", 2),
        _sym("Winter", 4),
        _sym("Summer", -2),
    ]
    person.aging.warping_score = 4
    text = aging_text(person, saga)
    assert "Faerie Rank: +2 (Sympathy Traits Winter +4, Summer -2)" in text
    assert "2 more botch dice" in text
    assert "Warping Score 4" in text


def _answer(form: commands.Form, typed: dict[str, str | bool]):
    fields = form.fields()
    raw = {f.key: f.value for f in fields} | typed
    return form_spec.result(fields, lambda f: raw[f.key])


def test_a_personality_trait_may_be_a_sympathy_trait():
    traits: list[ScoredTrait] = []
    ops = trait_forms.trait_ops(traits, "section-personality-traits")
    assert ops.add is not None and ops.edit is not None
    form = ops.add()
    assert isinstance(form, commands.Form)
    form.apply(_answer(form, {"name": "Winter", "score": "3", "sympathy": True}))
    assert traits[0].type == fs.SYMPATHY
    assert "(Sympathy)" in ops.rows()[0]
    edit = ops.edit(0)
    assert isinstance(edit, commands.Form)
    assert {f.key: f.value for f in edit.fields()}["sympathy"] is True
    assert {f.key: f.value for f in edit.fields()}["temporary"] is False
    edit.apply(_answer(edit, {"temporary": True}))
    assert traits[0].type == fs.TEMPORARY
    assert "(Sympathy, temporary)" in ops.rows()[0]
    again = ops.edit(0)
    assert isinstance(again, commands.Form)
    values = {f.key: f.value for f in again.fields()}
    assert values["sympathy"] is True and values["temporary"] is True
    again.apply(_answer(again, {"sympathy": False, "temporary": False}))
    assert traits[0].type == ""
    # Reputations, and a creature's traits, have no such box.
    for section in ("section-reputations", "section-cr-personality-traits"):
        other = trait_forms.trait_ops([], section).add
        assert other is not None
        made = other()
        assert isinstance(made, commands.Form)
        assert "sympathy" not in {f.key for f in made.fields()}


# -- the Olympians --


def test_a_faerie_gods_blood_names_its_olympian():
    zeus = VirtueFlawInstance("vf_faerie_blood", params={"blood": "faerie god: zeus"})
    found = faerie_blood.blood_of(zeus)
    assert found is not None
    assert "Thunder & Lightning, Kings, Sky; Fidelity (negative)" in found.sympathies
    assert "The Sundered Eagle p. 127" in found.sympathies
    assert found.benefit == faerie_blood.BLOODS["faerie god"].benefit
    plain = VirtueFlawInstance("vf_faerie_blood", params={"blood": "faerie god"})
    assert faerie_blood.blood_of(plain) == faerie_blood.BLOODS["faerie god"]
    # An unknown god keeps the plain Faerie God's blood.
    odin = VirtueFlawInstance("vf_faerie_blood", params={"blood": "faerie god: odin"})
    assert faerie_blood.blood_of(odin) == faerie_blood.BLOODS["faerie god"]
    assert "Faerie God: Hestia" in virtue_forms.BLOOD_NAMES
    assert len(fs.OLYMPIANS) == 13
    hestia = fs.olympian("hestia")
    assert hestia is not None and hestia.negative == "Self Promotion"


# -- faerie rites --


def _trad(trad_id: str = "trad_wise_folk") -> TraditionDef:
    return catalog.load_tradition_catalog_by_id()[trad_id]


def _rite(
    method: str,
    power: str,
    guideline: str,
    r: str,
    d: str,
    t: str,
    more: int = 0,
) -> TraditionEffect:
    return TraditionEffect(
        "Rite",
        tradition=_trad_for(power),
        kind="rite",
        rule=faerie_rites.FAERIE_RITE,
        uses=[method, power],
        guideline=guideline,
        range=r,
        duration=d,
        target=t,
        magnitudes=more,
    )


#: The book's rites (pp. 125-130; The Reflecting Pool's Range is Symbol,
#: Errata p. 68): Method, Power, guideline, Range, Duration, Target,
#: further magnitudes, printed level.
BOOK_RITES = [
    (
        "Evocation",
        "Beguile",
        "Minor change to perceptions",
        "Touch",
        "Midday/Midnight",
        "Room",
        0,
        15,
    ),
    (
        "Empathy",
        "Beguile",
        "Behaviour by an unnatural emotion",
        "Voice",
        "Focus",
        "Individual",
        0,
        25,
    ),
    (
        "Enchantment",
        "Beguile",
        "Imbue every response with an emotion",
        "Presence",
        "Sun",
        "Individual",
        0,
        30,
    ),
    (
        "Empathy",
        "Conjure",
        "Change into a glamour",
        "Voice",
        "Sun",
        "Individual",
        1,
        20,
    ),
    ("Evocation", "Conjure", "Conjure a glamour", "Touch", "Sun", "Group", 0, 20),
    (
        "Enchantment",
        "Conjure",
        "Glamour 5 Sizes smaller",
        "Voice",
        "Until (Condition)",
        "Group",
        0,
        45,
    ),
    (
        "Enchantment",
        "Dream",
        "Speak the caster's language",
        "Touch",
        "While (Condition)",
        "Group",
        0,
        20,
    ),
    (
        "Evocation",
        "Dream",
        "One sense at a distance",
        "Symbol",
        "Aura",
        "Medium",
        0,
        30,
    ),
    (
        "Empathy",
        "Dream",
        "Future in the next year",
        "Prop",
        "Momentary",
        "Individual",
        0,
        30,
    ),
    (
        "Evocation",
        "Grant",
        "A Warping Point",
        "Voice",
        "Momentary",
        "Individual",
        3,
        30,
    ),
    ("Enchantment", "Grant", "Minor Virtue", "Touch", "Hidden", "Individual", 0, 40),
    (
        "Evocation",
        "Portage",
        "To a thing of a Sympathy Trait",
        "Sight",
        "Momentary",
        "Individual",
        0,
        20,
    ),
    ("Enchantment", "Portage", "Hold within range", "Touch", "Aura", "Room", 0, 40),
    (
        "Empathy",
        "Portage",
        "Double or halve speed",
        "Touch",
        "While (Condition)",
        "Individual",
        0,
        25,
    ),
    (
        "Enchantment",
        "Ware",
        "+1 Defense",
        "Personal",
        "While (Condition)",
        "Individual",
        2,
        25,
    ),
    (
        "Evocation",
        "Weal",
        "A wound heals a step faster",
        "Touch",
        "Momentary",
        "Individual",
        0,
        20,
    ),
    ("Enchantment", "Weal", "Semblance of life", "Touch", "Aura", "Individual", 0, 50),
    (
        "Evocation",
        "Woe",
        "A wound heals three steps slower",
        "Touch",
        "Moon",
        "Medium",
        0,
        20,
    ),
    ("Empathy", "Woe", "A deadly wound", "Touch", "Hour + 1", "Individual", 0, 25),
    ("Enchantment", "Woe", "Force an Aging roll", "Eye", "Held", "Individual", 1, 30),
]


@pytest.mark.parametrize("trad_id", RITE_TRADITIONS)
def test_the_rite_traditions_have_the_guidelines(trad_id: str):
    trad = _trad(trad_id)
    assert {g.arts[0] for g in trad.guidelines} == RITE_TRADITIONS[trad_id]
    assert he.parameter_cost(trad, "range", "Presence") == 2
    assert he.parameter_cost(trad, "duration", "Geas (Condition)") == 2
    assert he.parameter_cost(trad, "target", "Symbol") == 4
    assert he.parameter_cost(trad, "range", "Road") == 2
    assert he.parameter_cost(trad, "duration", "Moon") == 3
    # Geas and If take the trigger's Duration as typed magnitudes; RoP:
    # Faerie has no Bargain Duration (pp. 122-123).
    durations = {p.name for p in trad.effect_parameters if p.kind == "duration"}
    assert {"Geas (Condition)", "If (Condition)"} <= durations
    assert "Bargain" not in durations


def test_the_books_rites_have_their_printed_levels():
    found = []
    for method, power, guideline, r, d, t, more, _ in BOOK_RITES:
        rite = _rite(method, power, guideline, r, d, t, more)
        design = he.effect_design(_trad(rite.tradition), rite)
        assert design is not None and not design.problems, guideline
        found.append((guideline, design.level))
    assert found == [(row[2], row[7]) for row in BOOK_RITES]


def test_a_rites_sympathy_limit_and_its_method():
    assert faerie_rites.max_rite_level(3) == 15
    assert faerie_rites.max_rite_level(3, fatigue_levels=2) == 30
    assert faerie_rites.max_rite_level(3, fatigue_levels=3) == 45
    # Traits +1 and -4 allow a level 25 rite (p. 121).
    assert faerie_rites.sympathy_points([_sym("Light", 1), _sym("Iron", -4)]) == 5
    assert faerie_rites.points_needed(25) == 5
    assert faerie_rites.points_needed(21) == 5
    assert faerie_rites.enchantment_ease_factor(25) == 15
    assert faerie_rites.enchantment_ease_factor(15) == 9
    assert faerie_rites.evocation_vis_cap(3, 2) == 5
    assert faerie_rites.max_summoned_might(4) == 20
    assert [faerie_rites.presence_paces(p) for p in (5, 2, 0, -3, -4)] == [
        100,
        50,
        15,
        5,
        0,
    ]


def test_a_rites_notes():
    trad = _trad("trad_ollamhain")
    caster = Character(id="w", name="Wise Wilma", type="companion")
    caster.personality_traits = [_sym("Water", 2)]
    pool = _rite(
        "Evocation", "Dream", "One sense at a distance", "Symbol", "Aura", "Medium"
    )
    notes = " ".join(faerie_rites.rite_notes(caster, trad, pool))
    assert (
        "needs 6 point(s) of the Sympathy Traits that apply to its target, "
        "negatives by their size; more than all his (2)"
    ) in notes
    assert "Symbol needs 3" in notes
    assert "Symbol and Aura: a ritual" in notes
    assert "a Warping or Confidence Point" in notes
    song = _rite(
        "Enchantment",
        "Dream",
        "Future in the next minute",
        "Touch",
        "While (Condition)",
        "Group",
    )
    assert "first a performance against 12" in " ".join(
        faerie_rites.rite_notes(caster, trad, song)
    )
    glamour = _rite(
        "Evocation", "Conjure", "Conjure a glamour", "Touch", "Sun", "Group"
    )
    conjured = " ".join(faerie_rites.rite_notes(caster, _trad("trad_volkhvy"), glamour))
    assert "the Traits of both states for a change" in conjured
    assert "(RoP: Faerie p. 121, 125)" in conjured
    other = TraditionEffect("Charm", tradition="trad_wise_folk", rule="Curse")
    assert faerie_rites.rite_notes(caster, trad, other) == []


def test_the_sheet_shows_a_rites_notes():
    caster = Character(id="w", name="Wise Wilma", type="companion")
    caster.traditions = ["trad_wise_folk"]
    caster.tradition_effects = [
        _rite(
            "Empathy", "Weal", "Heal a Heavy wound", "Touch", "Momentary", "Individual"
        )
    ]
    saga = Saga(id="s", name="S", characters=[caster])
    rows = tradition_text.effect_rows(saga, caster, _trad())
    assert "needs 4 point(s) of the Sympathy Traits that apply" in rows[0][1]
    assert "an hour's trance" in rows[0][1]


# -- a faerie's role --


def test_a_faeries_role_and_the_story_it_wants():
    nymph = Creature(id="n", name="Nymph", realm="Faerie", might=10)
    assert faerie_build.role_text(nymph) == ""
    nymph.faerie_role = "Donor"
    nymph.faerie_story = "a mortal who returns her stolen veil"
    text = faerie_build.role_text(nymph)
    assert text.startswith("Donor: grants the hero a magical gift")
    assert "wants a mortal who returns her stolen veil" in text
    facts = {
        f.label: f.value for f in creature_sheet.facts(Saga(id="s", name="S"), nymph)
    }
    assert facts["Role"] == text
    # One built by the book is reminded; a creature of another realm has none.
    built = Creature(
        id="b",
        name="B",
        realm="Faerie",
        virtues_flaws=[VirtueFlawInstance("vf_humanoid_faerie")],
    )
    assert faerie_build.role_text(built).startswith("not noted")
    beast = Creature(id="m", name="M", realm="Magic", faerie_role="Villain")
    assert faerie_build.role_text(beast) == ""


def test_the_role_is_on_the_form_and_cleared_with_another_realm():
    saga = Saga(id="s", name="S")
    sprite = Creature(id="x", name="Sprite", realm="Faerie", might=5)
    saga.creatures.append(sprite)
    fields = {f.key: f for f in creature_forms.info_fields(saga, sprite)}
    role = fields["faerie_role"]
    assert role.show_if is not None and role.show_if({"realm": "Faerie"})
    assert not role.show_if({"realm": "Magic"})
    values = {f.key: f.value for f in fields.values()}
    creature_forms.apply_info(
        saga,
        sprite,
        {**values, "faerie_role": "Helper", "faerie_story": "to guide a lost child"},
    )
    assert (sprite.faerie_role, sprite.faerie_story) == (
        "Helper",
        "to guide a lost child",
    )
    values = {f.key: f.value for f in creature_forms.info_fields(saga, sprite)}
    creature_forms.apply_info(saga, sprite, {**values, "realm": "Magic"})
    assert (sprite.faerie_role, sprite.faerie_story) == ("", "")


def test_the_role_is_saved_and_old_saves_load():
    sprite = Creature(id="x", name="Sprite", realm="Faerie", faerie_role="Villain")
    again = Creature.from_dict(asdict(sprite))
    assert again.faerie_role == "Villain"
    old = Creature.from_dict({"id": "o", "name": "Old", "realm": "Faerie"})
    assert (old.faerie_role, old.faerie_story) == ("", "")


def test_a_faerie_calling_reads_the_characters_faerie_rank():
    person = Character(id="p", name="Brigid", type="companion")
    saga = Saga(id="s", name="S", characters=[person])
    plain = realm_warping.faerie_calling(person, 2, 0, random.Random(1), saga, False)
    assert not any("His Sympathy Traits" in n for n in plain.notes)
    person.personality_traits = [_sym("Winter", 4)]
    good = realm_warping.faerie_calling(person, 2, 0, random.Random(1), saga, False)
    assert "His Sympathy Traits make his Faerie Rank +4: a good Calling." in good.notes
    person.personality_traits = [_sym("Iron", -5)]
    bad = realm_warping.faerie_calling(person, 2, 0, random.Random(1), saga, False)
    assert "His Sympathy Traits make his Faerie Rank -5: a bad Calling." in bad.notes

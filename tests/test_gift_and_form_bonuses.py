"""The Gift on seasons of teaching and training (DE pp. 186, 204-205) and
Form Bonuses against harm outside a fight (DE pp. 206-209)."""

from __future__ import annotations

import random

from ars_magica_manager import health
from ars_magica_manager.models import (
    Ability,
    ArtScore,
    Character,
    Covenant,
    Saga,
    SeasonPlan,
    VirtueFlawInstance,
    XpAllocation,
)
from ars_magica_manager.rules import activities, dice, harm, study
from ars_magica_manager.rules.xp import ability_xp, art_xp


def _die(*values: int):
    """A stress die that shows `values` in turn."""
    shown = list(values)

    def stress(rng, botch_dice=1, *, saga=None):
        value = shown.pop(0)
        return dice.DieResult(value, (value % 10,))

    return stress


def _magus(cid: str = "m", covenant: str | None = "cov", **arts: int) -> Character:
    return Character(
        id=cid,
        name=cid.title(),
        type="magus",
        covenant_id=covenant,
        arts={k: ArtScore(xp=art_xp(v)) for k, v in arts.items()},
    )


def _grog(
    cid: str = "g", covenant: str | None = "cov", kind: str = "grog"
) -> Character:
    return Character(id=cid, name=cid.title(), type=kind, covenant_id=covenant)


def _parma(character: Character) -> Character:
    character.abilities.append(Ability("Parma Magica", xp=ability_xp(1)))
    return character


# -- the Gift ----------------------------------------------------------------------


def test_the_gifts_social_penalty_by_kind():
    assert study.gift_social_penalty(_magus()) == 3
    blatant = _magus()
    blatant.virtues_flaws = [VirtueFlawInstance("vf_blatant_gift")]
    assert study.gift_social_penalty(blatant) == 6
    gentle = _magus()
    gentle.virtues_flaws = [VirtueFlawInstance("vf_gentle_gift")]
    assert study.gift_social_penalty(gentle) == 0
    assert study.gift_social_penalty(_grog()) == 0


def test_parma_and_familiarity_keep_the_gift_from_bothering():
    oda = _magus("oda")
    # A visitor from elsewhere is bothered; the covenant's own grogs are used
    # to their magi (DE p. 186); a Parma Magica blocks it (DE p. 205).
    assert study.gift_bothers(oda, _grog("visitor", covenant="elsewhere")) == 3
    assert study.gift_bothers(oda, _grog("own")) == 0
    assert study.gift_bothers(oda, _magus("tib")) == 3  # no Parma yet
    assert study.gift_bothers(oda, _parma(_magus("tib"))) == 0
    # Two magi with Parma: neither is bothered, so no line at all.
    assert study.gift_lines(_parma(_magus("a")), _parma(_magus("b"))) == []
    # A Parma doesn't stop one's own Gift bothering others.
    lines = study.gift_lines(_parma(_magus("oda")), _grog("visitor", "elsewhere"))
    assert [(line.label, line.amount) for line in lines] == [("The Gift (Oda)", -3)]


def _training_saga(master: Character, student: Character) -> Saga:
    master.abilities.append(Ability("Latin", xp=ability_xp(5)))
    return Saga(
        id="s",
        name="S",
        covenants=[Covenant(id="cov", saga_id="s", name="Keep")],
        characters=[master, student],
    )


def _trained(saga: Saga, student: Character, master: Character):
    plan = SeasonPlan(
        student.id,
        1220,
        "Spring",
        activities.TRAINED,
        [XpAllocation("ability:Latin")],
        teacher_id=master.id,
    )
    return activities.outcome(student, plan, saga, None)


def test_a_gifted_master_costs_a_visiting_student_three():
    oda = _parma(_magus("oda"))
    visitor = _grog("visitor", covenant="elsewhere", kind="companion")
    worked = _trained(_training_saga(oda, visitor), visitor, oda)
    gain = worked.gains[0]
    # Latin 5 + 3 = 8, less the Gift's 3.
    assert gain.result.xp == 5
    assert ("The Gift (Oda)", -3) in [(x.label, x.amount) for x in gain.result.lines]


def test_a_blatantly_gifted_trainee_suffers_six_and_never_below_nothing():
    master = _grog("master", covenant="elsewhere", kind="companion")
    student = Character(
        id="ann",
        name="Ann",
        type="companion",
        virtues_flaws=[VirtueFlawInstance("vf_blatant_gift")],
    )
    saga = _training_saga(master, student)
    worked = _trained(saga, student, master)
    assert worked.gains[0].result.xp == 2  # 8 - 6
    master.abilities[0].xp = ability_xp(2)  # Latin 2 + 3 = 5, less 6
    worked = _trained(saga, student, master)
    assert worked.gains[0].result.advancement_total == 0
    assert worked.gains[0].result.xp == 0


def test_a_gentle_gift_costs_nothing():
    oda = _magus("oda")
    oda.virtues_flaws = [VirtueFlawInstance("vf_gentle_gift")]
    visitor = _grog("visitor", covenant="elsewhere", kind="companion")
    worked = _trained(_training_saga(oda, visitor), visitor, oda)
    assert worked.gains[0].result.xp == 8


# -- Form Bonuses --------------------------------------------------------------------


def test_only_the_higher_form_bonus_counts():
    # Drowning: Auram 11 gives 3, Aquam 1 gives 1; only the 3 counts.
    drowned = _magus(auram=11, aquam=1)
    assert harm.resisting_form(drowned, harm.DEPRIVATION_FORMS["drowning"]) == (
        "Auram",
        3,
    )
    assert harm.resisting_form(_grog(), ("Ignem",)) is None


def test_ignem_adds_to_soak_against_fire(monkeypatch):
    plain, ignem = _magus(), _magus(ignem=6)  # 6 / 5 rounded up: 2
    monkeypatch.setattr(dice, "stress_die", _die(5, 2, 5, 2))
    values = {"bonus": 5, "harm_from": "fire"}
    without = harm.apply(None, plain, harm.INJURY, values, random.Random())
    burned = harm.apply(None, ignem, harm.INJURY, values, random.Random())
    assert burned.lines[0] == without.lines[0].replace(
        "Soak 2", "Soak 4 (Ignem Form Bonus +2)"
    )


def test_the_tables_name_what_their_harm_comes_from():
    fire = health._values({"kind": harm.INJURY, "preset": "Wood fire"})
    assert (fire["bonus"], fire["harm_from"]) == (5, "fire")
    stone = health._values(
        {"kind": harm.INJURY, "preset": "Inside a collapsing stone building"}
    )
    assert (stone["bonus"], stone["harm_from"]) == (21, "metal_stone")
    # A choice the user made wins over the table's.
    chosen = health._values(
        {"kind": harm.INJURY, "preset": "Wood fire", "harm_from": "weather"}
    )
    assert chosen["harm_from"] == "weather"
    poison = health._values({"kind": harm.POISON, "poison": "Monkshood"})
    assert (poison["ease"], poison["poison_kind"]) == (9, "herbal")


def test_herbam_resists_a_herbal_poison_and_corpus_a_disease(monkeypatch):
    herbalist = _magus(herbam=5, corpus=10)  # +1 and +2
    monkeypatch.setattr(dice, "stress_die", _die(8, 7))
    done = harm.apply(
        None,
        herbalist,
        harm.POISON,
        {"ease": 9, "wound": "heavy", "poison_kind": "herbal"},
        random.Random(),
    )
    assert done.lines == [
        "Stamina check 9 against 9 (Herbam Form Bonus +1)",
        "Resisted: nothing more than discomfort.",
    ]
    done = harm.apply(
        None, herbalist, harm.DISEASE, {"ease": 9, "wound": "heavy"}, random.Random()
    )
    assert done.lines[0] == "Stamina check 9 against 9 (Corpus Form Bonus +2)"


def test_drowning_takes_the_higher_of_auram_and_aquam(monkeypatch):
    diver = _magus(auram=1, aquam=11)  # +1 and +3
    monkeypatch.setattr(dice, "stress_die", _die(1))
    done = harm.apply(
        None,
        diver,
        harm.DEPRIVATION,
        {"kind": "air", "drowning": True, "periods": 1},
        random.Random(),
    )
    assert done.lines == [
        "Each check (Aquam Form Bonus +3).",
        "Period 1: 4 against 3, holds out.",
    ]
    assert done.wounds == []


def test_take_harm_asks_what_the_harm_comes_from():
    saga = Saga(id="s", name="S")
    by_key = {f.key: f for f in health.harm_fields(saga)}
    assert by_key["harm_from"].show_if is not None
    assert by_key["harm_from"].show_if({"kind": harm.INJURY})
    assert not by_key["harm_from"].show_if({"kind": harm.POISON})
    assert by_key["poison_kind"].show_if({"kind": harm.POISON})
    drowning = by_key["drowning"].show_if
    assert drowning is not None
    assert drowning({"kind": harm.DEPRIVATION, "deprived": "air"})
    assert not drowning({"kind": harm.DEPRIVATION, "deprived": "food"})


def test_two_unprotected_gifted_characters_both_pay():
    one = Character(id="a", name="Alda", type="companion")
    two = Character(id="b", name="Berno", type="companion")
    gift = min(study.catalog.GIFT_IDS)
    for c in (one, two):
        c.virtues_flaws.append(VirtueFlawInstance(vf_id=gift))
    lines = study.gift_lines(one, two)
    assert [line.amount for line in lines] == [-3, -3]

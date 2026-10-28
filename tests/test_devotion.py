"""Devotion and the saints: Devotions and Devotion Points (The Church pp.
12-15), invoking a saint and its modifiers (RoP: The Divine p. 87; The
Church p. 13), the relic bonus (The Church p. 13 over RoP: The Divine p.
87), icons (The Sundered Eagle p. 133), threatening a saint (RoP: The
Divine pp. 87-88), indulgences, vigils and fasts (The Church pp. 11-12),
the saints and their powers (RoP: The Divine pp. 88-91; The Sundered
Eagle pp. 136-137; The Contested Isle pp. 134-138) and the season of
personal devotion (The Church p. 14)."""

import random
from dataclasses import replace

import pytest

from ars_magica_manager import churches, seasons
from ars_magica_manager import devotion as forms
from ars_magica_manager.actions import NodeKind, available
from ars_magica_manager.commands import Form, Refuse
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.models import (
    Ability,
    Character,
    Characteristics,
    Neighbour,
    Saga,
    ScoredTrait,
    SeasonPlan,
    VirtueFlawInstance,
    XpAllocation,
)
from ars_magica_manager.rules import devotion as dv
from ars_magica_manager.rules import dice
from ars_magica_manager.rules import saints as sr
from ars_magica_manager.rules.xp import ability_xp
from ars_magica_manager.seasons import plans
from ars_magica_manager.sections import FAITH_SECTION


class Faces(random.Random):
    """A d10 that shows the faces given, in order (then 5s)."""

    def __init__(self, *faces: int) -> None:
        super().__init__(0)
        self.faces = list(faces)

    def randrange(self, *_args, **_kwargs) -> int:  # type: ignore[override]
        return self.faces.pop(0) if self.faces else 5


def _thomas() -> Character:
    """The Church's shoemaker: Communication 1, Charm 2, Pious +2."""
    thomas = Character(id="t", name="Thomas", type="companion")
    thomas.characteristics = Characteristics(communication=1, presence=2)
    thomas.abilities = [
        Ability("Charm", xp=ability_xp(2)),
        Ability("Leadership", xp=ability_xp(3)),
    ]
    thomas.personality_traits = [ScoredTrait("Pious", 2)]
    return thomas


def _saga(*books: str) -> Saga:
    church = Neighbour(id="ch", name="Bury", kind="church")
    church.details["relics"] = [
        {"name": "A finger of St Edmund", "saint": "St Edmund", "faith": 2},
        {"name": "A bone of St Peter", "saint": "Saint Peter", "faith": 3},
    ]
    return Saga(
        id="s",
        name="S",
        characters=[_thomas()],
        neighbours=[church],
        books_in_play=list(books) or ["TC", "RoP:D", "TSE", "TCI"],
    )


def _form(command) -> Form:
    assert isinstance(command, Form)
    return command


def _values(form: Form, **changes) -> dict:
    values = {f.key: f.value for f in form.fields()}
    values.update(changes)
    return values


# -- names and Devotions --


@pytest.mark.parametrize(
    ("a", "b"),
    [
        ("St. Peter", "Saint Peter"),
        ("the Theotokos", "The Blessed Virgin Mary"),
        ("Queen of Heaven", "Mary"),
        ("Saint Kevin", "Saint Kevin of Glendalough"),
    ],
)
def test_names_of_one_saint_match(a, b):
    assert dv.same_saint(a, b)


def test_names_of_two_saints_do_not():
    assert not dv.same_saint("Saint Peter", "Saint Paul")
    assert not dv.same_saint("", "")


def test_a_devotion_rises_as_an_ability_on_devotion_points():
    thomas = _thomas()
    assert dv.devotion_total(thomas, "Saint Bartholomew") == 0
    record = dv.add_points(thomas, "Saint Bartholomew", 1)
    assert dv.score(1) == 0 and dv.devoted(thomas, "St Bartholomew")
    dv.add_points(thomas, "St. Bartholomew", 14)
    assert record.points == 15 and dv.devotion_total(thomas, "Bartholomew") == 2
    assert dv.devotion_label(record) == "Saint Bartholomew 2 (15)"
    dv.add_points(thomas, "Saint Bartholomew", -99)
    assert record.points == 0 and not dv.devoted(thomas, "Saint Bartholomew")


def test_creation_points_are_the_positive_pious_trait_or_the_flaw():
    thomas = _thomas()
    assert dv.creation_points(thomas) == 2
    thomas.virtues_flaws.append(VirtueFlawInstance("vf_pious"))
    assert dv.creation_points(thomas) == 3
    thomas.virtues_flaws.append(VirtueFlawInstance("vf_pious_major"))
    assert dv.creation_points(thomas) == 6
    impious = Character(id="i", name="Hugo", type="grog")
    impious.personality_traits = [ScoredTrait("Pious", -2)]
    assert dv.creation_points(impious) == 0
    assert dv.creation_problem(impious, "Saint Peter", 1)


def test_at_creation_pious_limits_the_saints_and_the_points():
    thomas = _thomas()
    assert dv.creation_problem(thomas, "Blessed Virgin", 1) is None
    dv.add_points(thomas, "Blessed Virgin", 1)
    dv.add_points(thomas, "Saint Bartholomew", 1)
    assert "Only 2 Devotion Points" in str(
        dv.creation_problem(thomas, "Saint Bartholomew", 1)
    )
    assert "No more than 2 Devotions" in str(
        dv.creation_problem(thomas, "Saint Edmund", 0)
    )


def test_the_patron_saint_is_one_record():
    thomas = _thomas()
    dv.set_patron(thomas, "Saint Crispin")
    dv.set_patron(thomas, "Saint Bartholomew")
    assert dv.patron(thomas) == "Saint Bartholomew"
    assert [p.kind for p in thomas.progress] == [dv.PATRON]
    dv.set_patron(thomas, "")
    assert dv.patron(thomas) == ""


# -- invoking --


def test_invoking_a_strange_saint_is_communication_charm_less_15():
    found = dv.petition(_thomas(), "Saint Jude", dv.Situation())
    assert found.total == 1 + 2 - 15
    assert found.familiar == ""
    assert found.terms[-1] == "- not a patron 15"


def test_the_modifiers_of_rop_the_divine_p87():
    thomas = _thomas()
    thomas.background.true_faith_score = 2
    situation = dv.Situation(
        tomb=True,
        aura=4,
        feast_day=True,
        pilgrimage=True,
        donation=2,
        peril=True,
        unchristian=1,
        appropriate=True,
    )
    found = dv.petition(thomas, "Saint Jude", situation)
    # 3 + tomb 1 + aura 4 + feast 3 + pilgrimage 2 + donation 2 + peril 2
    # + True Faith 2 - unchristian 1; no -15, the matter is in his care.
    assert found.total == 3 + 1 + 4 + 3 + 2 + 2 + 2 + 2 - 1
    assert found.familiar == "the matter is in the saint's care"
    lately = dv.petition(thomas, "Saint Jude", replace(situation, miracle_lately=True))
    assert lately.total == found.total - 20
    stingy = dv.petition(thomas, "Saint Jude", replace(situation, donation=-3))
    assert stingy.total == found.total - 2 - 3


def test_a_devotion_adds_its_score_and_lifts_the_minus_15():
    thomas = _thomas()
    dv.add_points(thomas, "Saint Bartholomew", 15)
    found = dv.petition(thomas, "St Bartholomew", dv.Situation())
    assert found.total == 3 + 2 and found.familiar == "devoted to the saint"
    # Without The Church, a Devotion is nothing.
    plain = dv.petition(thomas, "St Bartholomew", dv.Situation(), the_church=False)
    assert plain.total == 3 - 15


def test_anyone_may_ask_the_virgin_or_his_patron():
    thomas = _thomas()
    assert dv.petition(thomas, "the Queen of Heaven", dv.Situation()).total == 3
    dv.set_patron(thomas, "Saint Crispin")
    assert dv.petition(thomas, "St. Crispin", dv.Situation()).familiar == (
        "his patron saint"
    )


def test_the_saints_own_relic_adds_two_a_faith_point_and_lifts_the_minus_15():
    """The Church p. 13: +2 a Faith Point, counted once, replacing RoP: The
    Divine's +1; and no -15 for the unfamiliar saint."""
    thomas = _thomas()
    held = dv.Situation(relic_faith=3, relic_of_the_saint=True)
    found = dv.petition(thomas, "Saint Edmund", held)
    assert found.total == 3 + 6
    assert "+ relic 6" in found.terms and found.familiar == "he holds the saint's relic"


def test_another_saints_relic_or_no_church_keeps_the_plus_one():
    thomas = _thomas()
    other = dv.Situation(relic_faith=3, relic_of_the_saint=False)
    assert dv.petition(thomas, "Saint Jude", other).total == 3 + 1 - 15
    rop = dv.Situation(relic_faith=3, relic_of_the_saint=True)
    found = dv.petition(thomas, "Saint Edmund", rop, the_church=False)
    assert found.total == 3 + 1 - 15
    assert dv.relic_bonus(4, True, True) == 8
    assert dv.relic_bonus(4, False, True) == dv.relic_bonus(4, True, False) == 1


def test_true_faith_stays_separate_from_the_relic():
    thomas = _thomas()
    thomas.background.true_faith_score = 1
    held = dv.Situation(relic_faith=2, relic_of_the_saint=True)
    assert dv.petition(thomas, "Saint Edmund", held).total == 3 + 4 + 1


def test_a_fast_adds_one_with_the_church():
    thomas = _thomas()
    fasting = dv.Situation(fasting=True, appropriate=True)
    assert dv.petition(thomas, "Saint Jude", fasting).total == 4
    assert dv.petition(thomas, "Saint Jude", fasting, the_church=False).total == 3


def test_an_irish_patron_for_one_of_irish_birth():
    thomas = _thomas()
    irish = dv.Situation(irish=True)
    found = dv.petition(thomas, "Saint Brigid", irish, irish_patron=True)
    assert found.familiar.startswith("a patron of Ireland")
    assert not dv.petition(
        thomas, "Saint Brigid", dv.Situation(), irish_patron=True
    ).familiar


def test_the_chance_of_being_heard():
    # A total of 15 meets 15 + the storyguide's die whenever his die is
    # at least as high: 55 of 100.
    assert dv.chance(15) == 0.55
    assert dv.chance(25) == 1.0
    assert dv.chance(-5) == 0.0


# -- threatening --


def test_a_threat_is_presence_leadership_against_9_and_a_fifth_of_might():
    thomas = _thomas()
    total, terms = dv.threat_total(thomas, ("bones", "barring"), confidence=1)
    assert total == 2 + 3 + 1 + 3 + 3
    assert terms[0] == "Presence +2"
    assert dv.threat_ease(50) == 19 and dv.threat_ease(100) == 29
    strange, _ = dv.threat_total(thomas, (), unfamiliar=True, miracle_lately=True)
    assert strange == 5 - 15 - 20


@pytest.mark.parametrize(
    ("faces", "ease", "outcome"),
    [
        ((9,), 14, dv.THREAT_GRANTED),
        ((2,), 14, dv.THREAT_ANNOYED),
        ((2,), 17, dv.THREAT_CURSED),
        ((0, 0), 14, dv.THREAT_BOTCHED),
    ],
)
def test_what_a_threat_brings(faces, ease, outcome):
    roll = dice.Roll(5, dice.stress_die(Faces(*faces)), ease)
    assert dv.threat_outcome(roll) == outcome


# -- the saints --


def test_every_saints_power_is_in_the_catalog():
    missing = [
        (key, p) for key, s in sr.SAINTS.items() for p in s.powers if p not in sr.POWERS
    ]
    assert not missing, missing
    assert all(p in sr.POWERS for p in sr.GREEK_POWERS)


def test_the_ranks_of_saints():
    assert sr.SAINTS["mary"].might == 100 and sr.SAINTS["mary"].anyone
    assert sr.SAINTS["peter"].rank == "greater saint"
    assert sr.SAINTS["martin_of_tours"].rank == "area saint"
    assert sr.SAINTS["guinefort"].rank == "local saint"


def test_saints_are_offered_by_the_books_in_play():
    assert set(sr.in_play(["RoP:D"])) == {
        k for k, s in sr.SAINTS.items() if s.book == "RoP:D"
    }
    assert "patrick" in sr.in_play(["TCI"]) and "patrick" not in sr.in_play(["TSE"])
    assert "demetrios" in sr.in_play(["TSE"])
    assert sr.in_play(None) == sr.SAINTS


def test_greek_saints_have_the_powers_greek_saints_favour():
    powers = [p.name for p in sr.powers_of(sr.SAINTS["demetrios"])]
    assert "Healing" in powers and "Expel Demons" in powers
    assert sr.powers_of(sr.SAINTS["paul"]) == ()


def test_the_two_tame_the_wild_beasts_and_irish_patrons():
    assert sr.POWERS["tame_the_wild_beast_tse"].points == 2
    assert sr.POWERS["tame_the_wild_beast_tci"].points == 3
    assert "tame_the_wild_beast_tci" in sr.SAINTS["kevin"].powers
    assert {k for k, s in sr.SAINTS.items() if s.irish_patron} == {
        "patrick",
        "brigid",
        "columba",
    }
    assert sr.POWERS["expel_demons"].line == "Expel Demons, 1 point, Init +15, Vim"


# -- Invoke a Saint --


def test_invoking_with_the_saints_relic_from_a_church():
    saga = _saga()
    thomas = saga.character("t")
    form = _form(forms.invoke_form(saga, thomas, Faces(9, 4)))
    values = _values(form, saint=forms.OTHER, other="Saint Edmund", relic="ch:0")
    live = form.live(values)
    assert "Simple die + [b]7[/]" in live
    assert "No -15: he holds the saint's relic" in live
    lines = form.apply(values)
    # 3 + relic 4 + 9 = 16 against 15 + 4 = 19: not heard.
    assert lines[0] == "Die 9 + 7 = 16 against 15 + 4 = 19."
    assert "may ask again tomorrow" in lines[1]
    assert thomas.diary[-1].name == "Invoked Saint Edmund"


def test_a_heard_invocation_is_a_miracle_in_the_diary():
    saga = _saga()
    thomas = saga.character("t")
    dv.add_points(thomas, "Saint Peter", 5)
    form = _form(forms.invoke_form(saga, thomas, Faces(0, 1)))
    values = _values(form, saint="Saint Peter", relic="ch:1", power="expel_demons")
    # 3 + Devotion 1 + relic 6 + 10 = 20 against 16.
    lines = form.apply(values)
    assert lines[0] == "Die 10 + 10 = 20 against 15 + 1 = 16."
    assert "Saint Peter hears him and works a miracle: Expel Demons." in lines[1]
    assert "5 to 10 Devotion Points" in lines[2]
    assert thomas.diary[-1].name == "Miracle of Saint Peter"
    assert "Expel Demons, 1 point" in form.live(values)


def test_the_saints_options_put_his_patron_and_devotions_first():
    saga = _saga()
    thomas = saga.character("t")
    dv.set_patron(thomas, "Saint Crispin")
    dv.add_points(thomas, "Saint Bartholomew", 5)
    options = forms.saint_options(saga, thomas)
    assert [v for _, v in options[:4]] == [
        "Saint Crispin",
        "Saint Bartholomew",
        "St Edmund",
        "Saint Peter",
    ]
    assert options[-1][1] == forms.OTHER
    assert sum(dv.same_saint(v, "Saint Peter") for _, v in options) == 1


def test_an_icon_of_the_saint_adds_its_bonus():
    saga = _saga()
    thomas = saga.character("t")
    church = saga.neighbour("ch")
    churches.relics(church).append(
        {"name": "Hodegetria", "saint": "the Theotokos", "kind": "eikon", "quality": 12}
    )
    form = _form(forms.invoke_form(saga, thomas))
    values = _values(form, saint=forms.OTHER, other="Mary", icon="ch:2")
    assert "+ icon 3" in form.live(values)
    wrong = _values(form, saint="Saint Peter", icon="ch:2")
    assert "not an icon of the saint invoked" in form.live(wrong)


def test_the_fasting_box_starts_ticked_in_a_fast():
    saga = _saga()
    thomas = saga.character("t")
    dv.keep_fast(thomas, saga.current_season, saga.current_year)
    form = _form(forms.invoke_form(saga, thomas))
    assert _values(form)["fasting"] is True


def test_without_the_church_there_are_no_devotions_on_the_form():
    saga = _saga("RoP:D")
    thomas = saga.character("t")
    keys = [f.key for f in _form(forms.invoke_form(saga, thomas)).fields()]
    assert "fasting" not in keys and "icon" not in keys and "irish" not in keys
    assert "+1 for touching" in next(
        f.hint
        for f in _form(forms.invoke_form(saga, thomas)).fields()
        if f.key == "relic"
    )
    assert isinstance(forms.invoke_form(saga, None), Refuse)


# -- Threaten a Saint --


def test_threatening_spends_confidence_and_is_written_down():
    saga = _saga()
    thomas = saga.character("t")
    thomas.background.confidence_points = 2
    dv.add_points(thomas, "Saint Peter", 1)
    dv.note_answer(thomas, "Saint Peter", False, "Spring", 1220)
    form = _form(forms.threaten_form(saga, thomas, Faces(2)))
    values = _values(form, saint="Saint Peter", might=75, confidence=1, bones=True)
    assert "Against [b]24[/]" in form.live(values)
    lines = form.apply(values)
    # Presence 2 + Leadership 3 + bones 1 + Confidence 3 + 2 = 11 against
    # 24 (devoted, so no -15): a miss by 13, a minor curse.
    assert lines[0] == "Die 2 + 9 = 11 against 24."
    assert "minor curse" in lines[1]
    assert thomas.background.confidence_points == 1
    assert thomas.diary[-1].name == "Threatened Saint Peter"
    # The threat answers the refusal: he may not threaten Peter again.
    assert dv.refused(thomas) == []
    assert form.validate is not None
    again = _values(form, saint="Saint Peter", confidence=1)
    assert "refused his invocation" in str(form.validate(again))
    dv.note_answer(thomas, "Saint Peter", False, "Spring", 1220)
    assert "only 1 Confidence" in str(form.validate({**again, "confidence": 3}))


def test_a_refusal_is_kept_until_the_saint_hears_him():
    saga = _saga()
    thomas = saga.character("t")
    invoke = _form(forms.invoke_form(saga, thomas, Faces(1, 9)))
    invoke.apply(_values(invoke, saint=forms.OTHER, other="Saint Peter"))
    assert dv.refused(thomas) == ["Saint Peter"]
    threat = _form(forms.threaten_form(saga, thomas))
    assert [v for _, v in threat.fields()[0].options] == ["Saint Peter"]
    dv.note_answer(thomas, "St. Peter", True, "Summer", 1220)
    assert dv.refused(thomas) == []


def test_the_saints_might_is_filled_from_the_books():
    saga = _saga()
    thomas = saga.character("t")
    dv.note_answer(thomas, "Saint Martin of Tours", False, "Spring", 1220)
    form = _form(forms.threaten_form(saga, thomas))
    saint = form.fields()[0]
    assert saint.fills is not None
    assert saint.fills({"saint": "Saint Martin of Tours"}) == {"might": 50}
    assert saint.fills({"saint": forms.OTHER, "other": "Saint Nobody"}) == {
        "might": None
    }


# -- Devotion Points --


def test_devotion_points_at_creation():
    saga = _saga()
    thomas = saga.character("t")
    thomas.in_creation = True
    form = _form(forms.points_form(saga, thomas))
    assert "patron" not in {f.key for f in form.fields()}
    values = _values(form, saint=forms.OTHER, other="Saint Bartholomew", points=1)
    assert values["how"] == dv.CREATION
    assert form.validate is not None and form.validate(values) is None
    form.apply(values)
    assert dv.devotion(thomas, "Saint Bartholomew").points == 1
    assert dv.patron(thomas) == ""
    too_many = _values(form, saint=forms.OTHER, other="Blessed Virgin", points=2)
    assert "Only 2 Devotion Points" in str(form.validate(too_many))


def test_the_patron_saint_is_chosen_on_its_own():
    saga = _saga()
    thomas = saga.character("t")
    form = _form(forms.patron_form(saga, thomas))
    assert form.fields()[0].value == forms.NO_PATRON
    assert form.validate is not None
    assert form.validate(_values(form, saint=forms.OTHER)) == "Name the saint."
    lines = form.apply(_values(form, saint=forms.OTHER, other="Saint Crispin"))
    assert dv.patron(thomas) == "Saint Crispin"
    assert lines == ["Saint Crispin is now his patron saint."]
    assert thomas.diary[-1].name == "Patron saint"
    again = _form(forms.patron_form(saga, thomas))
    assert again.fields()[0].value == "Saint Crispin"
    assert again.apply(_values(again)) == []
    again.apply(_values(again, saint=forms.NO_PATRON))
    assert dv.patron(thomas) == ""


def test_devotion_points_wait_for_a_devotion_or_piety():
    saga = _saga()
    thomas = saga.character("t")
    faith = replace(
        menu_forms.page_for(saga, NodeKind.CHARACTER, character_id="t"),
        section=FAITH_SECTION,
    )
    assert available("devotion_points", faith)
    thomas.personality_traits = []
    assert not available("devotion_points", faith)
    assert available("patron_saint", faith)
    thomas.virtues_flaws.append(VirtueFlawInstance("vf_pious"))
    assert available("devotion_points", faith)
    thomas.virtues_flaws.clear()
    dv.add_points(thomas, "Saint Bartholomew", 1)
    assert available("devotion_points", faith)


def test_a_neglected_feast_loses_points():
    saga = _saga()
    thomas = saga.character("t")
    dv.add_points(thomas, "Saint Bartholomew", 7)
    form = _form(forms.points_form(saga, thomas))
    how = next(f for f in form.fields() if f.key == "how")
    assert how.fills is not None and how.fills({"how": dv.NEGLECT}) == {"points": 3}
    values = _values(form, saint="Saint Bartholomew", how=dv.NEGLECT, points=3)
    lines = form.apply(values)
    assert dv.devotion(thomas, "Saint Bartholomew").points == 4
    assert lines[0].startswith("3 Devotion Point(s) lost")


# -- Indulgence, Vigil or Fast --


def test_an_indulgence_with_its_charitable_season():
    saga = _saga()
    thomas = saga.character("t")
    form = _form(forms.piety_form(saga, thomas))
    values = _values(form, act=forms.INDULGENCE, seasons=4, works_done=True)
    assert "About [b]24[/] pennies" in form.live(values)
    form.apply(values)
    assert thomas.background.faith_points == 1
    piety = next(r for r in thomas.reputations if r.name == "Piety")
    assert piety.deeds == 4
    rich = _values(form, act=forms.INDULGENCE, seasons=2, wealthy=True)
    assert "About [b]480[/] pennies" in form.live(rich)


def test_a_vigil_costs_a_fatigue_level_for_a_confidence_point():
    saga = _saga()
    thomas = saga.character("t")
    form = _form(forms.piety_form(saga, thomas))
    assert form.validate is not None
    assert form.validate(_values(form, act=forms.VIGIL, task=""))
    form.apply(_values(form, act=forms.VIGIL, task="the trial by combat"))
    assert thomas.background.confidence_points == 1
    assert thomas.fatigue_level == "winded" and thomas.long_term_fatigue == 1


def test_a_fast_is_kept_for_the_season():
    saga = _saga()
    thomas = saga.character("t")
    form = _form(forms.piety_form(saga, thomas))
    form.apply(_values(form, act=forms.FAST))
    assert dv.fasting(thomas, saga.current_season, saga.current_year)
    assert not dv.fasting(thomas, "Winter", saga.current_year + 1)
    assert thomas.fatigue_level == "winded"


# -- the season of personal devotion, and the Planning tab --


def test_a_season_of_personal_devotion_earns_five_points():
    saga = _saga()
    thomas = saga.character("t")
    dv.add_points(thomas, "Saint Bartholomew", 2)
    plan = SeasonPlan(
        "t",
        saga.current_year,
        saga.current_season,
        "personal_devotion",
        [XpAllocation("ability:Church Lore")],
        title="St. Bartholomew",
    )
    seasons.set_plan(saga, plan)
    seasons.apply(saga, seasons.resolve(saga))
    assert [p.points for p in dv.devotions(thomas)] == [7]
    text = plans.livelihood_text(thomas)
    assert "Devotions: Saint Bartholomew 1 (7)" in text
    assert "(devotion)" not in text


# -- where they are offered --


@pytest.mark.parametrize(
    ("action", "book"),
    [
        ("invoke_saint", "TSE"),
        ("threaten_saint", "RoP:D"),
        ("devotion_points", "TC"),
        ("patron_saint", "RoP:D"),
        ("act_of_piety", "TC"),
    ],
)
def test_offered_on_a_person_with_the_books(action, book):
    saga = _saga(book)
    dv.note_answer(saga.character("t"), "Saint Peter", False, "Spring", 1220)
    page = menu_forms.page_for(saga, NodeKind.CHARACTER, character_id="t")
    faith = replace(page, section=FAITH_SECTION)
    assert available(action, faith)
    assert not available(action, page)
    assert action in {i.action for i in menu_forms.placed(page, "Faith")}
    assert action not in {
        i.action for i in menu_forms.placed(page, "Personality Traits")
    }
    assert isinstance(menu_forms.command(faith, action), Form)
    saga.books_in_play = ["HoH:S"]
    assert not available(action, replace(faith))


def test_threatening_waits_for_a_refusal_and_the_saints_are_christian():
    saga = _saga()
    thomas = saga.character("t")
    faith = replace(
        menu_forms.page_for(saga, NodeKind.CHARACTER, character_id="t"),
        section=FAITH_SECTION,
    )
    assert available("invoke_saint", faith)
    assert not available("threaten_saint", faith)
    dv.note_answer(thomas, "Saint Peter", False, "Spring", 1220)
    assert available("threaten_saint", faith)
    thomas.background.religion = "Jewish"
    for action in ("invoke_saint", "threaten_saint", "devotion_points", "act_of_piety"):
        assert not available(action, faith)


# -- a church's relics --


def test_a_churchs_relics_show_what_they_add_to_invoking():
    saga = _saga()
    church = saga.neighbour("ch")
    grid = churches.relics_grid(saga, church)
    assert grid.columns[-1] == "Invoking"
    assert [row[-1] for row in grid.rows] == ["+4", "+6"]
    saga.books_in_play = ["RoP:D"]
    assert [row[-1] for row in churches.relics_grid(saga, church).rows] == ["+1", "+1"]
    saga.books_in_play = ["HoH:S"]
    assert [row[-1] for row in churches.relics_grid(saga, church).rows] == ["", ""]


# -- the Mazdean yazdan (The Cradle and the Crescent p. 85) --


def test_a_yazata_needs_ritual_purity_and_is_never_threatened():
    saga = _saga("TC&TC")
    thomas = saga.character("t")
    invoke = _form(forms.invoke_form(saga, thomas))
    assert invoke.validate is not None
    impure = _values(invoke, saint=forms.OTHER, other="Mithra", yazata=True)
    assert "Nahn" in str(invoke.validate(impure))
    assert invoke.validate({**impure, "pure": True}) is None
    dv.note_answer(thomas, "Saint Peter", False, "Spring", 1220)
    threat = _form(forms.threaten_form(saga, thomas))
    assert threat.validate is not None
    values = _values(threat, saint=forms.OTHER, other="Mithra", yazata=True)
    assert "can't be threatened" in str(threat.validate(values))
    saga.books_in_play = ["RoP:D"]
    assert "yazata" not in {f.key for f in invoke.fields()}

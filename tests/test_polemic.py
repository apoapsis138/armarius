"""Polemic and Charter Strength (Transforming Mythic Europe pp. 27-36):
the Prevailing Wisdom, circulating a text, the Argument Total and the
debate bonus it buys, the bonus at a hearing and how the hearing ends the
argument, the Arguments tab's forms, and the optional Charter Strength's
Draft the Charter and Seek a Loophole."""

from __future__ import annotations

import random

import pytest
from support import everything_saga

from ars_magica_manager import actions, meeting, storage, town_charter
from ars_magica_manager import polemic as pl
from ars_magica_manager.commands import Confirm, Form, Refuse
from ars_magica_manager.forms import charter_strength as cs
from ars_magica_manager.forms import polemic as pf
from ars_magica_manager.models import (
    Ability,
    Argument,
    Book,
    Character,
    Neighbour,
    PolemicText,
    Saga,
    ScoredTrait,
    Tribunal,
)
from ars_magica_manager.models.polemic import LOST, WON
from ars_magica_manager.rules import debate, dice, options
from ars_magica_manager.rules import polemic as rules
from ars_magica_manager.sections import (
    ARGUMENT_TEXTS_SECTION,
    ARGUMENTS_SECTION,
    CHARTER_LORDS_SECTION,
)

# -- the rules --


def test_prevailing_wisdom_by_reach():
    # TME p. 29: a magus 3 or his Reputation, a covenant 6, a Tribunal 9,
    # a House 12, the Order 15.
    assert [rules.prevailing_wisdom(r) for r in rules.PREVAILING_WISDOM] == [
        3,
        6,
        9,
        12,
        15,
    ]
    assert rules.prevailing_wisdom("magus", 5) == 5
    assert rules.prevailing_wisdom("magus", 2) == 3
    assert rules.prevailing_wisdom("covenant", 8) == 6


def test_a_tractatus_circulates_as_level_five():
    assert rules.text_level("Tractatus", None) == 5
    assert rules.text_level("Ability Summa", 4) == 4


def test_the_circulation_example():
    # TME p. 31: Protinus's Reformer 3 + the polemic's level 4 + a 3 is 10
    # against 15; the next season +1 and a 10 make 18.
    first = rules.circulation_total(3, 4, 0, 0)
    assert first + 3 == 10 and not rules.circulates(first, 3, "tribunal")
    second = rules.circulation_total(3, 4, 1, 0)
    assert second + 10 == 18 and rules.circulates(second, 10, "tribunal")
    assert [rules.ease_factor(a) for a in ("tribunal", "house", "order")] == [
        15,
        18,
        24,
    ]
    assert [rules.copies(a) for a in ("tribunal", "house", "order")] == [6, 9, 18]
    assert [rules.distraction_days(a) for a in ("tribunal", "house", "order")] == [
        5,
        10,
        15,
    ]
    # Each new work bound into every copy is +1 (p. 30).
    assert rules.circulation_total(3, 4, 0, 2) == 9


def test_the_circulator_rolls_his_highest_reputation_good_or_bad():
    magus = Character(id="m", name="M", type="magus")
    magus.reputations = [ScoredTrait("Kind", 2), ScoredTrait("Cruel", -4)]
    assert rules.circulation_reputation(magus) == 4
    assert rules.circulation_reputation(None) == 0


def test_the_argument_total_example():
    # TME p. 31: a polemic of Quality 11 against a Tribunal's 9 is +2, a
    # bonus of 1; a diatribe of 11 takes it to -9, a penalty of 3; an
    # apologia of 11 brings it back to +2.
    polemic = rules.Counted("polemic", 11, True)
    diatribe = rules.Counted("diatribe", 11, True)
    apologia = rules.Counted("apologia", 11, True)
    assert rules.argument_total(9, [polemic]) == 2
    assert rules.debate_bonus(2) == 1
    assert rules.argument_total(9, [polemic, diatribe]) == -9
    assert rules.debate_bonus(-9) == -3
    assert rules.argument_total(9, [polemic, diatribe, apologia]) == 2
    # Texts not yet out count for nothing, nor anything before the polemic.
    assert rules.argument_total(9, [polemic, rules.Counted("diatribe", 11, False)]) == 2
    assert rules.argument_total(9, [rules.Counted("polemic", 11, False)]) is None
    assert rules.debate_bonus(None) == 0


@pytest.mark.parametrize(
    ("total", "bonus"),
    [(0, 0), (1, 1), (2, 1), (3, 2), (5, 2), (6, 3), (10, 4), (15, 5), (-6, -3)],
)
def test_the_total_buys_a_bonus_on_the_art_table(total: int, bonus: int):
    # DE p. 49: an Art's 1, 3, 6, 10, 15 experience.
    assert rules.debate_bonus(total) == bonus


def test_a_circulated_text_gives_its_author_a_reputation():
    magus = Character(id="m", name="Corvinus", type="magus")
    name = rules.reputation_name("polemic", "Charters")
    assert name == "Supporter of Charters"
    assert rules.reputation_name("diatribe", "Charters") == "Opposed to Charters"
    words = rules.gain_reputation(magus, name, "the Rhine")
    assert "Supporter of Charters 1" in words
    found = magus.reputations[0]
    assert (found.score, found.type, found.reach) == (1, "Hermetic", "the Rhine")
    # Already held: 5 experience toward it (10 raise it to 2).
    rules.gain_reputation(magus, name, "the Rhine")
    rules.gain_reputation(magus, name, "the Rhine")
    assert len(magus.reputations) == 1 and magus.reputations[0].score == 2


def test_charter_strength_rules():
    notary = Character(id="n", name="Leandro", type="companion")
    notary.characteristics.intelligence = 1
    notary.abilities = [Ability("Civil and Canon Law", xp=5)]
    assert rules.law_score(notary) == ("Civil and Canon Law", 1)
    assert rules.charter_total(notary) == 2
    # Common Law only in England, and only it there (TME p. 36): never the
    # higher of the two.
    notary.abilities.append(Ability("Common Law", xp=30))
    assert rules.law_score(notary) == ("Civil and Canon Law", 1)
    assert rules.law_score(notary, in_england=True) == ("Common Law", 3)
    assert rules.charter_total(notary, in_england=True) == 4
    notary.abilities = [Ability("Civil and Canon Law", xp=30)]
    assert rules.law_score(notary, in_england=True) == ("Common Law", 0)
    # 3 botch dice, less one for each notary beyond the first.
    assert [rules.draft_botch_dice(n) for n in (1, 2, 3, 4, 5)] == [3, 2, 1, 0, 0]
    assert rules.finds_loophole(15, 14) and not rules.finds_loophole(14, 14)


# -- an argument in a saga --


def _saga() -> tuple[Saga, Tribunal, Argument]:
    saga = Saga(id="s", name="S")
    tribunal = Tribunal(id="rhine", name="The Rhine Tribunal", next_year=1221)
    saga.tribunals.append(tribunal)
    corvinus = Character(id="corvinus", name="Corvinus", type="magus")
    corvinus.reputations = [ScoredTrait("Reformer", 3)]
    benedek = Character(id="benedek", name="Benedek of Tremere", type="magus")
    saga.characters += [corvinus, benedek]
    saga.books += [
        Book(
            id="b1",
            name="On Charters",
            type="Ability Summa",
            ability="Code of Hermes",
            level=4,
            quality=11,
            author_id="corvinus",
        ),
        Book(
            id="b2",
            name="Against Charters",
            type="Tractatus",
            ability="Code of Hermes",
            quality=9,
            author_id="benedek",
        ),
        Book(id="b3", name="Herbs", type="Tractatus", ability="Herbalism", quality=7),
    ]
    argument = Argument(
        "Covenants may hold charters", ideal="Charters", proponent_id="corvinus"
    )
    tribunal.arguments.append(argument)
    return saga, tribunal, argument


def _values(form: Form, **changes: object) -> dict[str, object]:
    values = {f.key: f.value for f in form.fields() if f.kind != "info"}
    values.update(changes)
    return values


def _save(form: object, **changes: object) -> object:
    assert isinstance(form, Form)
    values = _values(form, **changes)
    assert form.validate is None or form.validate(values) is None
    return form.apply(values)


def test_adding_texts_reads_quality_and_level_from_the_library():
    saga, tribunal, argument = _saga()
    ops = pf.texts_ops(saga, tribunal, lambda: 0)
    assert ops.add is not None
    _save(ops.add(), book_id="b1")
    polemic = argument.texts[0]
    assert polemic.kind == "polemic" and polemic.author_id == "corvinus"
    assert (pl.quality(saga, polemic), pl.level(saga, polemic)) == (11, 4)
    add = ops.add()
    assert isinstance(add, Form)
    # The next text defaults to a diatribe; one on another Ability is refused.
    assert _values(add)["kind"] == "diatribe"
    assert add.validate is not None
    assert "isn't on Code of Hermes" in (add.validate(_values(add, book_id="b3")) or "")
    assert "has its polemic" in (
        add.validate(_values(add, book_id="b1", kind="polemic")) or ""
    )
    _save(add, book_id="b2")
    assert pl.level(saga, argument.texts[1]) == 5
    assert pl.total(saga, argument) is None


def test_a_reply_needs_its_polemic_first():
    saga, tribunal, argument = _saga()
    form = pf.text_form(saga, tribunal, argument, None)
    assert form.validate is not None
    assert "polemic first" in (
        form.validate(_values(form, kind="diatribe", book_id="b2")) or ""
    )


def test_circulating_a_text_rolls_each_season_until_it_is_out():
    saga, tribunal, argument = _saga()
    argument.texts.append(PolemicText(book_id="b1", author_id="corvinus"))
    # A 1 fails (3 + 4 + 1 < 15): the season counts toward the next roll.
    form = pf.circulate_form(saga, tribunal, lambda: 0, 0, random.Random(0))
    assert isinstance(form, Form) and form.live is not None
    assert "the die must show 8 or more" in form.live(_values(form))
    words = pf.circulate(saga, tribunal, argument, argument.texts[0], _values(form), 1)
    assert "not yet" in words and argument.texts[0].seasons_spent == 1
    form = pf.circulate_form(saga, tribunal, lambda: 0, 0, random.Random(0))
    assert isinstance(form, Form) and _values(form)["seasons"] == 1
    words = pf.circulate(saga, tribunal, argument, argument.texts[0], _values(form), 10)
    text = argument.texts[0]
    assert text.circulated and text.circulated_year == saga.current_year
    assert "Supporter of Charters 1" in words
    corvinus = saga.character("corvinus")
    assert corvinus is not None
    assert [r.name for r in corvinus.reputations] == [
        "Reformer",
        "Supporter of Charters",
    ]
    # 11 - 9 = +2: a bonus of 1.
    assert pl.total(saga, argument) == 2 and pl.bonus(saga, argument) == 1
    assert pf.total_words(saga, argument) == "+2: +1"
    assert isinstance(pf.circulate_form(saga, tribunal, lambda: 0, 0), Refuse)


def test_a_diatribe_needs_its_author_to_study_the_polemic():
    saga, tribunal, argument = _saga()
    argument.texts += [
        PolemicText(book_id="b1", author_id="corvinus", circulated=True),
        PolemicText(kind="diatribe", book_id="b2", author_id="benedek"),
    ]
    form = pf.circulate_form(saga, tribunal, lambda: 0, 1)
    assert isinstance(form, Form) and form.validate is not None
    assert "studying" in (form.validate(_values(form)) or "")
    argument.texts[1].studied = True
    assert form.validate(_values(form)) is None
    pf.circulate(saga, tribunal, argument, argument.texts[1], _values(form), 10)
    benedek = saga.character("benedek")
    assert benedek is not None and benedek.reputations[0].name == "Opposed to Charters"
    # 11 - 9 - 9 = -7: a penalty of 3.
    assert pf.formula(saga, argument) == "11 − 9 − 9 = −7"
    assert pl.bonus(saga, argument) == -3


def test_the_chosen_argument_shows_what_the_next_text_would_change():
    saga, tribunal, argument = _saga()
    argument.texts += [
        PolemicText(book_id="b1", author_id="corvinus", circulated=True),
        PolemicText(kind="apologia", book_id="b2", author_id="benedek"),
    ]
    facts = dict(pf.argument_facts(saga, tribunal, argument))
    assert facts["Reach"] == "a Tribunal: Prevailing Wisdom 9"
    assert facts["Argument Total"] == "11 − 9 = +2"
    assert facts["If the apologia circulates"] == "+11: +4"
    assert facts["In debate"].startswith("+1 to every Attack and Defense")
    text = pf.argument_text(saga, tribunal, lambda: None)
    assert "Prevailing Wisdom 9" in text and "Art table" in text
    info = pf.text_info(saga, tribunal, lambda: None, 1)
    assert "Apologia" in info and "must first" in info
    assert [c.rubric for c in pf.text_cards(saga, tribunal, lambda: None)] == ["+", "+"]
    assert pf.argument_cards(saga, tribunal)[0].badge == (
        "+1 in debate",
        "text-success",
    )


def test_arguments_ops_add_edit_and_delete():
    saga, tribunal, _argument = _saga()
    ops = pf.arguments_ops(saga, tribunal)
    assert ops.add is not None and ops.edit is not None and ops.remove is not None
    _save(ops.add(), topic="The silk pact", reach="magus", magus_reputation=5)
    added = tribunal.arguments[1]
    assert (added.reach, pl.wisdom(added)) == ("magus", 5)
    _save(ops.edit(1), reach="covenant", magus_reputation=5)
    assert (added.reach, added.magus_reputation, pl.wisdom(added)) == ("covenant", 0, 6)
    remove = ops.remove(1)
    assert isinstance(remove, Confirm)
    remove.apply()
    assert len(tribunal.arguments) == 1
    grid = pf.arguments_grid(saga, tribunal)
    assert grid.rows == [
        ["Covenants may hold charters", "Tribunal 9", "Corvinus", "not out"]
    ]


def test_arguments_survive_a_save():
    saga, _tribunal, argument = _saga()
    argument.texts.append(PolemicText(book_id="b1", seasons_spent=2, circulated=True))
    argument.outcome = WON
    storage.save_saga(saga)
    again = storage.load_saga("s")
    loaded = again.tribunals[0].arguments[0]
    assert loaded == argument
    assert loaded.texts[0].seasons_spent == 2


def test_a_bad_argument_on_disk_is_named():
    with pytest.raises(ValueError, match="Covenants"):
        Argument.from_dict({"topic": "Covenants", "reach": "kingdom"})
    with pytest.raises(ValueError, match="text 1"):
        Argument.from_dict({"topic": "C", "texts": [{"kind": "sermon"}]})


def test_circulate_is_offered_on_the_texts_only():
    assert actions.MORE_SECTIONS["circulate_text"] == ARGUMENT_TEXTS_SECTION
    assert "add" in actions.SECTION_VERBS[ARGUMENTS_SECTION]


# -- at the Tribunal's hearing --


def _hearing(saga: Saga, case_id: str) -> Form:
    rhine = saga.tribunal("rhine")
    assert rhine is not None
    step = next(
        s for s in meeting.steps(rhine, rhine.meeting) if s.key == f"case:{case_id}"
    )
    form = meeting.step_form(saga, rhine, step)
    assert isinstance(form, Form)
    return form


def _opened() -> tuple[Saga, Tribunal]:
    saga = everything_saga()
    rhine = saga.tribunal("rhine")
    assert rhine is not None
    following = _save(meeting.hold(saga, rhine))
    _save(following.step)  # type: ignore[attr-defined]
    return saga, rhine


def test_the_hearing_counts_the_arguments_and_ends_them():
    saga, rhine = _opened()
    case = rhine.cases[0]
    saga.books.append(
        Book(id="pol", name="P", type="Tractatus", ability="Code of Hermes", quality=15)
    )
    backing = Argument("For it", case_id=case.id)
    backing.texts.append(PolemicText(book_id="pol", circulated=True))
    against = Argument("Against it", case_id=case.id, side="against")
    against.texts.append(PolemicText(book_id="pol", circulated=True))
    rhine.arguments += [backing, against]
    # 15 - 9 = 6: +3 for each side.
    assert pl.case_bonuses(saga, rhine, case) == (3, 3)
    form = _hearing(saga, case.id)
    shown = next(f for f in form.fields() if f.key == "polemic")
    assert "+3 for it, +3 against it" in str(shown.value)
    _save(form, lost_for=0, lost_against=3)
    assert (backing.outcome, against.outcome) == (WON, LOST)
    # Lost, its bonus is gone (TME p. 35).
    assert pl.case_bonuses(saga, rhine, case) == (3, 0)


def test_a_rolled_hearing_adds_the_bonus_to_every_roll(monkeypatch: pytest.MonkeyPatch):
    saga, rhine = _opened()
    case = rhine.cases[0]
    saga.books.append(
        Book(id="pol", name="P", type="Tractatus", ability="Code of Hermes", quality=19)
    )
    backing = Argument("For it", case_id=case.id)
    backing.texts.append(PolemicText(book_id="pol", circulated=True))
    rhine.arguments.append(backing)
    seen: list[tuple[int, int]] = []
    real = debate.run

    def run(sides, *args, **kwargs):
        seen.append((sides[0].polemic, sides[1].polemic))
        return real(sides, *args, **kwargs)

    monkeypatch.setattr(debate, "run", run)
    monkeypatch.setattr(meeting, "rng", lambda: random.Random(3))
    _save(_hearing(saga, case.id))
    assert seen == [(4, 0)]
    assert rhine.meeting is not None
    assert rhine.meeting["debates"][case.id]["polemic"] == [4, 0]
    assert "Polemic:" in meeting.debate_text(rhine.meeting, case)
    # A polemic bonus raises the speaker's Attack and Defense totals.
    strong = debate.Debater("A", polemic=10)
    weak = debate.Debater("B")
    assert debate.run((strong, weak), ([], []), 5, random.Random(1)).victor == 0


# -- Charter Strength --


def _town() -> tuple[Saga, Neighbour]:
    saga = Saga(id="s", name="S")
    saga.rule_options[options.CHARTER_STRENGTH] = True
    leandro = Character(id="leandro", name="Leandro", type="companion")
    leandro.characteristics.intelligence = 1
    leandro.abilities = [Ability("Civil and Canon Law", xp=5)]
    saga.characters.append(leandro)
    town = Neighbour(id="freiburg", name="Freiburg", kind="town")
    town.details["charter_lords"] = [{"lord": "Duke Berthold"}]
    saga.neighbours.append(town)
    return saga, town


class _Die:
    """A stress die fixed to `value` (0 with a botch)."""

    @staticmethod
    def of(value: int, botches: int = 0) -> dice.DieResult:
        faces = (0,) if botches else (value,)
        return dice.DieResult(value=value, faces=faces, botch_faces=(0,) * botches)


def test_drafting_sets_each_sides_strength():
    saga, town = _town()
    form = cs.draft_form(saga, town, 0)
    assert isinstance(form, Form) and form.live is not None
    live = form.live(_values(form, helpers=1))
    assert "Int 1 + Civil and Canon Law 1" in live and "2 botch dice" in live
    entry = town_charter.charter_lords(town)[0]
    words = cs.draft(saga, town, entry, _values(form), _Die.of(7))
    assert entry.get("subordinate_strength") == 9 and "is 9" in words
    cs.draft(saga, town, entry, _values(form, side="superior"), _Die.of(0, 1))
    assert entry.get("superior_strength") == 0
    assert "Charter Strength:" in town_charter.lord_info(saga, town, 0)


def test_a_loophole_needs_a_total_above_the_other_sides_strength():
    saga, town = _town()
    entry = town_charter.charter_lords(town)[0]
    form = cs.loophole_form(saga, town, 0)
    assert isinstance(form, Form) and form.validate is not None
    assert "isn't drafted" in (form.validate(_values(form)) or "")
    entry["superior_strength"] = 14
    assert form.validate(_values(form)) is None
    assert form.live is not None and "must show 13 or more" in form.live(_values(form))
    assert "no loophole" in cs.seek(saga, town, entry, _values(form), _Die.of(12))
    assert "loophole" not in entry
    assert "a loophole" in cs.seek(saga, town, entry, _values(form), _Die.of(13))
    assert "Leandro found grounds" in entry.get("loophole", "")


def test_charter_strength_is_an_option():
    saga, town = _town()
    saga.rule_options[options.CHARTER_STRENGTH] = False
    assert isinstance(cs.draft_form(saga, town, 0), Refuse)
    assert all(
        f.key != "superior_strength" for f in town_charter.lord_fields(saga, town, None)
    )
    assert "Charter Strength" not in town_charter.lord_info(saga, town, 0)
    saga.rule_options[options.CHARTER_STRENGTH] = True
    keys = [f.key for f in town_charter.lord_fields(saga, town, None)]
    assert "superior_strength" in keys and "subordinate_strength" in keys
    assert options.OPTIONS_BY_KEY[options.CHARTER_STRENGTH].book == "TME"


def test_draft_and_loophole_are_offered_on_a_charter_lord():
    saga, _town_record = _town()

    class Facts:
        def __init__(self, row: int | None) -> None:
            self.saga = saga
            self.row = row

        def chosen_row(self, _section: str) -> int | None:
            return self.row

    rule = actions._SECTION_RULES["draft_charter"]
    assert rule(Facts(0), CHARTER_LORDS_SECTION)  # type: ignore[arg-type]
    assert not rule(Facts(None), CHARTER_LORDS_SECTION)  # type: ignore[arg-type]
    assert not rule(Facts(0), ARGUMENTS_SECTION)  # type: ignore[arg-type]


# -- the review's rulings --


def test_an_argument_may_be_on_any_knowledge_ability():
    # TME p. 28: any knowledge Ability; the three the book names first.
    offered = pl.knowledge_abilities()
    assert offered[:3] == ["Code of Hermes", "Order of Hermes Lore", "Area Lore"]
    assert "Civil and Canon Law" in offered and "Magic Theory" in offered
    assert "Organization Lore" in offered and "Area Lore: {region}" not in offered
    assert "Athletics" not in offered and "Brawl" not in offered
    saga, tribunal, _argument = _saga()
    form = pf.argument_form(saga, tribunal, None)
    field = next(f for f in form.fields() if f.key == "ability")
    assert [v for _label, v in field.options][:3] == offered[:3]
    # A family matches its members; another name for Order of Hermes Lore
    # matches it.
    assert pl.same_ability("Area Lore", "Area Lore: the Rhine")
    assert pl.same_ability("Order of Hermes Lore", "Organization Lore: Order of Hermes")
    assert not pl.same_ability("Area Lore", "Area Lorekeeping")
    assert not pl.same_ability("Code of Hermes", "Civil and Canon Law")


def test_a_text_must_still_match_its_arguments_ability():
    saga, tribunal, argument = _saga()
    argument.ability = "Herbalism"
    saga.books.append(
        Book(id="b4", name="Leaves", type="Tractatus", ability="Herbalism", quality=8)
    )
    form = pf.text_form(saga, tribunal, argument, None)
    assert form.validate is not None
    assert form.validate(_values(form, book_id="b4")) is None
    assert "isn't on Herbalism" in (form.validate(_values(form, book_id="b1")) or "")


def test_a_case_hears_one_argument_for_each_side():
    saga, rhine = _opened()
    case = rhine.cases[0]
    rhine.arguments.append(Argument("For it", case_id=case.id))
    form = pf.argument_form(saga, rhine, None)
    assert form.validate is not None
    refused = form.validate(_values(form, topic="Also for it", case_id=case.id))
    assert refused is not None and "one argument for each side" in refused
    # The other side may have its own, and editing the first is no rival.
    assert (
        form.validate(_values(form, topic="X", case_id=case.id, side="against")) is None
    )
    edit = pf.argument_form(saga, rhine, rhine.arguments[0])
    assert edit.validate is not None and edit.validate(_values(edit)) is None


def test_only_one_argument_a_side_counts_at_the_hearing():
    saga, rhine = _opened()
    case = rhine.cases[0]
    saga.books.append(
        Book(id="pol", name="P", type="Tractatus", ability="Code of Hermes", quality=15)
    )
    for topic in ("First", "Second"):
        argument = Argument(topic, case_id=case.id)
        argument.texts.append(PolemicText(book_id="pol", circulated=True))
        rhine.arguments.append(argument)
    # 15 - 9 = 6: +3, not +6.
    assert pl.case_bonuses(saga, rhine, case) == (3, 0)


def test_a_diatribe_gives_its_reputation_on_writing_and_to_its_circulator():
    saga, tribunal, argument = _saga()
    argument.texts.append(
        PolemicText(book_id="b1", author_id="corvinus", circulated=True)
    )
    ops = pf.texts_ops(saga, tribunal, lambda: 0)
    assert ops.add is not None
    words = _save(ops.add(), book_id="b2", studied=True)
    benedek = saga.character("benedek")
    corvinus = saga.character("corvinus")
    assert benedek is not None and corvinus is not None
    assert "Opposed to Charters 1" in str(words)
    assert [(r.name, r.score) for r in benedek.reputations] == [
        ("Opposed to Charters", 1)
    ]
    diatribe = argument.texts[1]
    # Editing it again gives nothing more.
    assert ops.edit is not None
    assert _save(ops.edit(1)) is None
    assert benedek.reputations[0].deeds == 0
    # Corvinus circulates it for him: he gains it, Benedek not again.
    form = pf.circulate_form(saga, tribunal, lambda: 0, 1)
    assert isinstance(form, Form) and form.live is not None
    live = form.live(_values(form, who="corvinus"))
    assert "Corvinus gains Opposed to Charters 1" in live
    words = pf.circulate(
        saga, tribunal, argument, diatribe, _values(form, who="corvinus"), 10
    )
    assert "Corvinus gained Opposed to Charters 1" in words
    assert "Benedek" not in words
    assert benedek.reputations[0].deeds == 0
    assert sorted(diatribe.reputation_given) == ["benedek", "corvinus"]


def test_a_polemics_sponsor_gains_nothing():
    saga, tribunal, argument = _saga()
    argument.texts.append(
        PolemicText(book_id="b1", author_id="corvinus", circulated_by_id="benedek")
    )
    form = pf.circulate_form(saga, tribunal, lambda: 0, 0)
    assert isinstance(form, Form)
    # Benedek, Reputation 0: 0 + 4 + 12 = 16 against 15.
    pf.circulate(saga, tribunal, argument, argument.texts[0], _values(form), 12)
    benedek = saga.character("benedek")
    assert benedek is not None and benedek.reputations == []
    assert argument.texts[0].reputation_given == ["corvinus"]


def test_a_bad_reputation_list_on_disk_is_named():
    with pytest.raises(ValueError, match="gave its Reputation"):
        PolemicText.from_dict({"reputation_given": "corvinus"})


def test_an_english_charter_uses_common_law_only():
    saga, town = _town()
    leandro = saga.character("leandro")
    assert leandro is not None
    leandro.abilities.append(Ability("Common Law", xp=15))  # 2
    entry = town_charter.charter_lords(town)[0]
    form = cs.draft_form(saga, town, 0)
    assert isinstance(form, Form) and form.live is not None
    assert _values(form)["in_england"] is False
    assert "Civil and Canon Law 1" in form.live(_values(form))
    assert "Common Law 2" in form.live(_values(form, in_england=True))
    cs.draft(saga, town, entry, _values(form, in_england=True), _Die.of(5))
    # Int 1 + Common Law 2 + 5.
    assert entry.get("subordinate_strength") == 8 and entry.get("in_england")
    assert "in England, Common Law" in town_charter.lord_info(saga, town, 0)
    again = cs.draft_form(saga, town, 0)
    assert isinstance(again, Form) and _values(again)["in_england"] is True
    # The search uses the charter's law too.
    entry["superior_strength"] = 10
    seek = cs.loophole_form(saga, town, 0)
    assert isinstance(seek, Form) and seek.live is not None
    assert "Common Law 2" in seek.live(_values(seek))
    assert "13 against 10" in cs.seek(saga, town, entry, _values(seek), _Die.of(10))
    # The lord's form keeps the choice.
    keys = [f.key for f in town_charter.lord_fields(saga, town, None)]
    assert "in_england" in keys


def test_a_loophole_botch_is_zero_and_an_ill_the_storyguide_decides():
    saga, town = _town()
    entry = town_charter.charter_lords(town)[0]
    entry["superior_strength"] = 0
    form = cs.loophole_form(saga, town, 0)
    assert isinstance(form, Form)
    words = cs.seek(saga, town, entry, _values(form), _Die.of(0, 1))
    assert "a total of 0" in words and "storyguide decides" in words
    assert "loophole" not in entry

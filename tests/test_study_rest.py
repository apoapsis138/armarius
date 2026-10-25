"""Study seasons, the rest: Practice split between Abilities and the native
speakers' Source Quality (DE p. 377), books on a spell's Mastery (DE pp.
378-379) and Blood of the Nephilim's slowed learning (DE p. 72)."""

from ars_magica_manager import book_kinds
from ars_magica_manager.models import (
    Ability,
    Book,
    Character,
    Characteristics,
    Covenant,
    KnownSpell,
    Saga,
    SeasonPlan,
    Spell,
    VirtueFlawInstance,
    XpAllocation,
)
from ars_magica_manager.rules import activities as rules
from ars_magica_manager.rules import book_seasons as bs
from ars_magica_manager.rules import study
from ars_magica_manager.rules.xp import ability_xp


def _saga() -> Saga:
    covenant = Covenant(id="cov", saga_id="s", name="Keep")
    magus = Character(id="m", name="Tiberius", type="magus", covenant_id="cov")
    magus.characteristics = Characteristics(communication=2)
    magus.abilities = [
        Ability("Dead Language: Latin", xp=ability_xp(5)),
        Ability("Artes Liberales", xp=ability_xp(1)),
        Ability("Living Language: French", xp=ability_xp(5)),
        Ability("Athletics", xp=ability_xp(1)),
        Ability("Brawl", xp=ability_xp(1)),
    ]
    magus.spells_known = [KnownSpell("bolt", mastery_score=4, mastery_xp=50)]
    magus.background.year_born = 1180
    saga = Saga(id="s", name="S", covenants=[covenant], characters=[magus])
    saga.spells = [Spell("bolt", "Bolt", "Creo", "Ignem", level=15)]
    return saga


def _plan(activity: str, *allocations: XpAllocation, **kw) -> SeasonPlan:
    return SeasonPlan("m", 1220, "Spring", activity, list(allocations), **kw)


def _xp(worked: rules.Outcome) -> list[tuple[str, int]]:
    return [(g.subject, g.result.xp) for g in worked.gains]


# -- Practice (DE p. 377) --


def test_practice_can_be_split_between_abilities():
    saga = _saga()
    magus = saga.character("m")
    plan = _plan(
        rules.PRACTICE,
        XpAllocation("ability:Athletics", 3),
        XpAllocation("ability:Brawl", 1),
    )
    assert rules.problems(magus, plan, saga) == []
    worked = rules.outcome(magus, plan, saga)
    assert _xp(worked) == [("ability:Athletics", 3), ("ability:Brawl", 1)]


def test_a_split_practice_shares_out_all_its_quality():
    saga = _saga()
    plan = _plan(
        rules.PRACTICE,
        XpAllocation("ability:Athletics", 2),
        XpAllocation("ability:Brawl", 1),
    )
    assert any(
        "Split all 4 points" in p
        for p in rules.problems(saga.character("m"), plan, saga)
    )


def test_mastery_practice_is_5_only_when_every_subject_is_a_spell():
    assert (
        rules.source_quality(_plan(rules.PRACTICE, XpAllocation("mastery:bolt"))) == 5
    )
    mixed = _plan(
        rules.PRACTICE,
        XpAllocation("mastery:bolt", 2),
        XpAllocation("ability:Brawl", 2),
    )
    assert rules.source_quality(mixed) == 4


def test_native_speakers_quality_stops_at_5():
    saga = _saga()
    plan = _plan(
        rules.PRACTICE,
        XpAllocation("ability:Living Language: French"),
        source_quality=8,
    )
    found = rules.problems(saga.character("m"), plan, saga)
    assert any("worth 8 only below it" in p for p in found)


# -- Books on a spell's Mastery (DE pp. 378-379) --


def test_a_summa_can_be_written_on_a_spells_mastery():
    saga = _saga()
    plan = _plan(bs.WRITE_SUMMA, XpAllocation("mastery:bolt"))
    found, work = bs.work(saga, saga.character("m"), plan)
    assert found == []
    book = work.made
    assert book.ability == "Mastery: Bolt" and book.spell_id == "bolt"
    assert book.level == 2  # half of Mastery 4
    assert bs.book_subject(book) == "mastery:bolt"
    assert rules.book_subject(book) == "mastery:bolt"


def test_a_book_on_a_spells_mastery_is_read_into_its_mastery():
    saga = _saga()
    reader = Character(id="r", name="Alys", type="magus", covenant_id="cov")
    reader.abilities = [
        Ability("Dead Language: Latin", xp=ability_xp(4)),
        Ability("Artes Liberales", xp=ability_xp(1)),
    ]
    reader.spells_known = [KnownSpell("bolt")]
    saga.characters.append(reader)
    saga.books = [
        Book(
            "tract",
            "On the Bolt",
            "Tractatus",
            subject_kind="Ability",
            ability=book_kinds.MASTERY_PREFIX + "Bolt",
            spell_id="bolt",
            quality=8,
            owner_kind="covenant",
            owner_id="cov",
        )
    ]
    plan = SeasonPlan("r", 1220, "Spring", rules.READ, book_id="tract")
    assert rules.problems(reader, plan, saga) == []
    worked = rules.outcome(reader, plan, saga)
    assert _xp(worked) == [("mastery:bolt", 8)]


# -- Blood of the Nephilim (DE p. 72) --


def test_the_nephilim_learn_slower_once_decrepit():
    saga = _saga()
    magus = saga.character("m")
    magus.virtues_flaws = [VirtueFlawInstance("vf_blood_of_the_nephilim")]
    plan = _plan(rules.PRACTICE, XpAllocation("ability:Athletics"))
    assert _xp(rules.outcome(magus, plan, saga)) == [("ability:Athletics", 4)]
    magus.aging.decrepitude_points = 1
    # Age 40: 4 off, but never below 1.
    assert _xp(rules.outcome(magus, plan, saga)) == [("ability:Athletics", 1)]
    magus.background.year_born = 1200  # age 20: 2 off
    assert _xp(rules.outcome(magus, plan, saga)) == [("ability:Athletics", 2)]
    assert study.nephilim_penalty(magus, None) == 0

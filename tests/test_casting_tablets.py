"""Casting Tablets (DE Chapter Eight: Laboratory, Casting Tablets)."""

from ars_magica_manager import books as bk
from ars_magica_manager.models import (
    Ability,
    ArtScore,
    Book,
    Character,
    Characteristics,
    Covenant,
    KnownSpell,
    Saga,
    SeasonPlan,
    Spell,
)
from ars_magica_manager.rules import book_seasons as bs
from ars_magica_manager.rules import casting
from ars_magica_manager.rules.xp import ability_xp, art_xp


def test_the_tablet_table():
    # Casting Total - level: 0+ one Fatigue level; to -10 two; to -20 three;
    # to -30 four and a Warping Point; below, not cast.
    assert casting.tablet_outcome(15, 15) == casting.TabletOutcome(True, 1)
    assert casting.tablet_outcome(5, 15) == casting.TabletOutcome(True, 2)
    assert casting.tablet_outcome(0, 15) == casting.TabletOutcome(True, 3)
    assert casting.tablet_outcome(0, 30) == casting.TabletOutcome(True, 4, 1)
    failed = casting.tablet_outcome(0, 35)
    assert failed == casting.TabletOutcome(False, 5, 7, twilight=True)
    assert casting.tablet_outcome(10, 10, ritual=True).long_term


def _saga() -> Saga:
    magus = Character(id="m", name="Tiberius", type="magus", covenant_id="cov")
    magus.characteristics = Characteristics(stamina=2)
    magus.arts = {"creo": ArtScore(xp=art_xp(5)), "ignem": ArtScore(xp=art_xp(3))}
    magus.abilities = [
        Ability("Artes Liberales", xp=ability_xp(1)),
        Ability("Dead Language: Latin", xp=ability_xp(4)),
    ]
    magus.spells_known = [KnownSpell("bolt", mastery_score=1)]
    pupil = Character(id="p", name="Pupil", type="magus", covenant_id="cov")
    saga = Saga(
        id="s",
        name="S",
        covenants=[Covenant("cov", "s", "Keep")],
        characters=[magus, pupil],
        spells=[Spell("bolt", "Bolt", "Creo", "Ignem", level=15)],
    )
    saga.books = [
        Book(
            "tab",
            "Casting Tablet: Bolt",
            "Casting Tablet",
            spell_id="bolt",
            owner_kind="covenant",
            owner_id="cov",
        )
    ]
    return saga


def test_the_details_panel_shows_each_magus_casting_from_it():
    saga = _saga()
    text = bk.detail_text(saga, saga.books[0])
    # Stamina 2 + Creo 5 + Ignem 3 = 10 against level 15.
    assert "Tiberius: 10 + stress die; 5+ 1 Fatigue, 0+ 2 Fatigue (short-term)" in text
    assert "Pupil: can't read it (needs Artes Liberales 1 and Latin 4)" in text


def test_writing_tablets_of_a_mastered_spell():
    saga = _saga()
    magus = saga.character("m")
    plan = SeasonPlan("m", 1220, "Spring", bs.WRITE_TABLET, spell_id="bolt")
    found, work = bs.work(saga, magus, plan)
    assert found == []
    # Latin 4 x 20 = 80 levels: five level 15 tablets.
    assert (work.made.type, work.made.spell_id, work.copies) == (
        "Casting Tablet",
        "bolt",
        5,
    )
    magus.spells_known[0].mastery_score = 0
    found, _ = bs.work(saga, magus, plan)
    assert found and "mastered spell" in found[0]


def test_a_tablet_can_be_copied_like_a_lab_text():
    saga = _saga()
    magus = saga.character("m")
    magus.abilities.append(Ability("Profession: Scribe", xp=ability_xp(1)))
    plan = SeasonPlan("m", 1220, "Spring", bs.COPY_TEXTS, book_id="tab")
    found, work = bs.work(saga, magus, plan)
    assert found == [] and work.copies == 4  # Scribe 1 x 60 / 15

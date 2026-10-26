"""The Book of Mundane Beasts (Realms of Power: Magic pp. 140-144) against
the Bestiary's catalog: its twelve beasts are the Definitive Edition's
(DE pp. 429-436), which win where the two disagree; the charger and palfrey
it describes as changes to the courser (DE p. 432; RoP:M p. 143) are
entered as their own blocks."""

import pytest

from ars_magica_manager import bestiary_book
from ars_magica_manager.rules.xp import ability_xp

#: Each beast of the Book: its catalog key, its RoP:M page(s) and its
#: Size, Soak and Characteristics (Cun, Per, Pre, Com, Str, Sta, Dex, Qik)
#: as the DE prints them.
BOOK = {
    "adder": ("141", -4, 2, (-1, -2, -6, -6, -8, 2, 2, 3)),
    "bear": ("141", 2, 10, (1, 0, 0, -5, 6, 4, 2, 0)),
    "wild_boar": ("141-142", 0, 7, (0, 0, -4, -5, 2, 2, 0, 1)),
    "bull": ("142", 2, 8, (-2, 0, -4, -4, 5, 3, 0, -1)),
    "cat": ("142", -3, 1, (0, 1, -2, -4, -7, 0, 3, 4)),
    "falcon": ("142", -3, -2, (-1, 3, -1, -2, -6, 2, 1, 6)),
    "horse_courser": ("142-143", 2, 3, (-2, 0, 0, -4, 4, 3, -2, 2)),
    "horse_destrier": ("143", 3, 3, (-2, 0, 0, -4, 6, 3, 1, -1)),
    "hound": ("143", 0, 2, (0, 2, -4, 0, 0, 2, 1, 2)),
    "lion": ("143-144", 2, 8, (2, 0, 0, 0, 6, 3, 2, 1)),
    "stag": ("144", 2, 2, (-2, 2, 0, -5, 2, 2, 0, 2)),
    "wolf": ("144", -1, 4, (2, 0, -2, 0, -1, 3, 2, 2)),
}


def _characteristics(key: str) -> tuple[int, ...]:
    c = bestiary_book.build(bestiary_book.by_key(key)).characteristics
    return (
        c.intelligence,
        c.perception,
        c.presence,
        c.communication,
        c.strength,
        c.stamina,
        c.dexterity,
        c.quickness,
    )


@pytest.mark.parametrize("key", sorted(BOOK))
def test_each_beast_of_the_book_is_in_the_bestiary(key):
    page, size, soak, chars = BOOK[key]
    book = bestiary_book.by_key(key)
    assert book is not None and book.group == "Mundane Beasts"
    creature = bestiary_book.build(book)
    assert (creature.size, creature.soak, creature.realm) == (size, soak, "")
    assert _characteristics(key) == chars
    assert f"RoP:M p. {page}" in creature.notes


def test_where_the_books_disagree_the_de_is_kept_and_noted():
    lion = bestiary_book.build(bestiary_book.by_key("lion"))
    assert lion.characteristics.intelligence == 2
    assert "Cun +1" in lion.notes
    falcon = bestiary_book.build(bestiary_book.by_key("falcon"))
    assert falcon.characteristics.communication == -2
    assert "Com 0" in falcon.notes
    boar = bestiary_book.build(bestiary_book.by_key("wild_boar"))
    assert boar.fatigue_levels == "OK, 0/0, 0/0, -2/-2, -4, Unconscious"
    assert "-4/-4" in boar.notes


def test_the_charger_is_a_courser_trained_for_war():
    charger = bestiary_book.by_key("horse_charger")
    assert charger is not None and charger.page == 432
    built = bestiary_book.build(charger)
    names = [v.vf_id for v in built.virtues_flaws]
    courser = bestiary_book.build(bestiary_book.by_key("horse_courser"))
    courser_names = [v.vf_id for v in courser.virtues_flaws]
    assert len(names) == len(courser_names)
    assert set(courser_names) - set(names) == {
        v for v in courser_names if "noncombatant" in v
    }
    assert any("proud" in v for v in names)
    assert ("Brawl", ability_xp(2)) in [(a.name, a.xp) for a in built.abilities]
    assert {t.name: t.score for t in built.personality_traits}["Brave"] == 0
    # Brawl 2 (hooves) adds its specialty's +1, as the destrier's line does
    # (DE p. 433): Atk = Dex + Brawl + 1 + 2, Def = Qik + Brawl + 1 + 2.
    hooves = built.attacks[0]
    assert (hooves.init, hooves.attack, hooves.defense, hooves.damage) == (
        4,
        3,
        7,
        5,
    )
    assert "RoP:M p. 143" in built.notes


def test_the_palfrey_trades_quickness_for_dexterity():
    palfrey = bestiary_book.build(bestiary_book.by_key("horse_palfrey"))
    assert _characteristics("horse_palfrey") == (-2, 0, 0, -4, 4, 3, 0, 0)
    assert any("noncombatant" in v.vf_id for v in palfrey.virtues_flaws)
    hooves = palfrey.attacks[0]
    assert (hooves.init, hooves.attack, hooves.defense, hooves.damage) == (
        2,
        2,
        2,
        5,
    )
    assert palfrey.source == "ArM5 DE p. 432"

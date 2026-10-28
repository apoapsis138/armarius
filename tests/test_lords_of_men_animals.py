"""Lords of Men's animals in the Bestiary: its pets (p. 45), hunting dogs
(p. 50), horses (pp. 55-56) and hawks (p. 59, the other hawks as the book's
changes to its gyrfalcon), offered only while the book is in play."""

from ars_magica_manager import bestiary_book, sourcebooks
from ars_magica_manager.forms import creature as creature_forms
from ars_magica_manager.models import Saga

#: Each animal, by catalog key: its page, Size and Soak, and its
#: Characteristics (Cun, Per, Pre, Com, Str, Sta, Dex, Qik) as printed.
ANIMALS = {
    "lom_magpie": (45, -4, 0, (0, 2, -2, 1, -8, 0, 3, 5)),
    "lom_monkey": (45, -3, 0, (2, 0, -3, -3, -6, 0, 2, 3)),
    "lom_squirrel": (45, -7, 1, (1, 0, -3, -5, -12, 1, 3, 5)),
    "lom_lymer": (50, -2, 1, (0, 3, -3, 0, -4, 1, 2, 2)),
    "lom_alaunt": (50, -1, 1, (1, 1, -2, -4, 2, 1, 0, 0)),
    "lom_greyhound": (50, -2, 0, (0, 1, -2, -4, -4, 0, 1, 5)),
    "lom_running_dog": (50, -2, 1, (0, 3, -2, -4, -4, 1, 0, 4)),
    "lom_mastiff": (50, -1, 1, (1, 1, -4, -4, 1, 2, 1, 1)),
    "lom_destrier": (55, 3, 3, (-2, 1, 1, -4, 6, 3, 1, 0)),
    "lom_courser": (55, 2, 3, (-2, 0, 0, -4, 4, 3, 1, 0)),
    "lom_palfrey": (56, 2, 3, (-2, -1, 0, -4, 4, 3, 1, 1)),
    "lom_hackney": (56, 3, 0, (-3, -1, 0, -4, 6, 4, 1, -2)),
    "lom_working_pony": (56, 1, 3, (-2, 1, 0, -4, 2, 3, 2, 0)),
    # The Errata (p. 74) makes the gyrfalcon's Com -2, which its variants
    # share.
    "lom_gyrfalcon": (59, -3, -2, (-1, 3, -1, -2, -6, -2, 1, 6)),
    "lom_peregrine": (59, -4, -2, (-1, 3, -1, -2, -8, -2, 1, 7)),
    "lom_goshawk": (59, -3, -2, (-1, 3, -1, -2, -6, -2, 1, 6)),
    "lom_merlin": (59, -5, -2, (-1, 3, -1, -2, -10, -2, 1, 8)),
    "lom_lanner": (59, -4, -2, (-1, 3, -1, -2, -8, -2, 1, 7)),
    "lom_sparrowhawk": (59, -4, -3, (-1, 3, -1, -2, -6, -3, 1, 6)),
}


def _characteristics(key: str) -> tuple[int, ...]:
    book = bestiary_book.by_key(key)
    assert book is not None, key
    c = bestiary_book.build(book).characteristics
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


def test_every_animal_of_the_book_is_in_the_bestiary_as_printed():
    found = {c.key for c in bestiary_book.catalog() if c.book == "LoM"}
    assert found == set(ANIMALS)
    for key, (page, size, soak, chars) in ANIMALS.items():
        book = bestiary_book.by_key(key)
        assert book is not None
        assert (book.group, book.page) == ("Mundane Beasts", page), key
        creature = bestiary_book.build(book)
        assert (creature.size, creature.soak) == (size, soak), key
        assert creature.source == f"LoM p. {page}"
        assert _characteristics(key) == chars, key
        assert all(vf.vf_id for vf in creature.virtues_flaws), key


def test_the_hawks_follow_the_books_changes_to_the_gyrfalcon():
    def qualities(key: str) -> set[str]:
        book = bestiary_book.by_key(key)
        assert book is not None
        return set(book.entry["block"]["virtues_flaws"])

    gyrfalcon = qualities("lom_gyrfalcon")
    assert {"Fast Flyer", "Pursuit Predator", "Ferocity"} <= gyrfalcon
    assert qualities("lom_peregrine") == gyrfalcon - {"Pursuit Predator"} | {
        "Ambush Predator"
    }
    assert qualities("lom_goshawk") == gyrfalcon - {"Fast Flyer"} | {"Aggressive"}
    assert qualities("lom_lanner") == gyrfalcon - {"Ferocity"}
    assert qualities("lom_sparrowhawk") == gyrfalcon - {"Fast Flyer"}
    lanner = bestiary_book.by_key("lom_lanner")
    assert lanner is not None and "confidence" not in lanner.entry


def test_the_animals_are_offered_only_while_lords_of_men_is_in_play():
    every = [key for _label, key in bestiary_book.options()]
    core = [key for _label, key in bestiary_book.options(frozenset({"DE"}))]
    assert set(ANIMALS) <= set(every)
    assert not set(ANIMALS) & set(core)
    assert len(core) == len(every) - len(ANIMALS)
    labels = {key: label for label, key in bestiary_book.options()}
    assert labels["lom_destrier"] == (
        "Mundane Beasts: Horse, Noble Warhorse (Destrier) (mundane, LoM p. 55)"
    )
    assert labels["bear"].endswith("(mundane, p. 429)")


def test_new_creature_lists_them_by_the_sagas_books():
    def offered(saga: Saga) -> set[str]:
        [field] = [
            f for f in creature_forms.new_creature_fields(saga) if f.key == "from_book"
        ]
        return {key for _label, key in field.options or ()}

    assert set(ANIMALS) <= offered(Saga(id="s", name="S"))
    without = Saga(id="s", name="S", books_in_play=[])
    assert not set(ANIMALS) & offered(without)
    assert sourcebooks.in_play("LoM", sourcebooks.saga_books(without)) is False

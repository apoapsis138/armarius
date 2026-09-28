"""Who may take which character Virtue/Flaw: the structural eligibility
rules the picker hides entries by (STORY-710)."""

import pytest

from ars_magica_manager import catalog
from ars_magica_manager.catalog import VirtueFlawChooser
from ars_magica_manager.models import Character, Familiar, VirtueFlawInstance

#: The Free Virtues that make a character a Mythic Companion.
MYTHIC_COMPANION_VIRTUES = (
    "vf_blood_of_heroes",
    "vf_devil_child",
    "vf_diabolist",
    "vf_faerie_doctor",
    "vf_kabbalist",
    "vf_maestro",
    "vf_nephilim",
    "vf_spirit_votary",
    "vf_summoner",
    "vf_zahid",
)


def vf(vf_id: str):
    return catalog.load_virtue_flaw_catalog_by_id()[vf_id]


def character(type_: str, *vf_ids: str) -> Character:
    return Character(
        id="c1",
        name="Test",
        type=type_,  # type: ignore[arg-type]
        virtues_flaws=[VirtueFlawInstance(vf_id) for vf_id in vf_ids],
    )


def refusal(chooser: VirtueFlawChooser, vf_id: str) -> str:
    return chooser.refusal(vf(vf_id))


def test_hermetic_entries_need_the_gift():
    companion = VirtueFlawChooser.for_character(character("companion"))
    assert refusal(companion, "vf_adept_laboratory_student") == "needs The Gift"
    # Any printed type counts: "Story, Hermetic", "Hermetic, Mystery".
    assert refusal(companion, "vf_homunculus_wizard") == "needs The Gift"
    assert refusal(companion, "vf_great_talisman") == "needs The Gift"
    assert refusal(companion, "vf_common_sense") == ""


@pytest.mark.parametrize("vf_id", sorted(catalog.HERMETIC_OR_OTHER_IDS))
def test_hermetic_or_general_entries_dont_need_the_gift(vf_id):
    # "Hermetic or General": an unGifted character takes it as the other.
    entry = vf(vf_id)
    assert "Hermetic" in (entry.category, *entry.extra_categories)
    assert not catalog.needs_the_gift(entry)
    assert refusal(VirtueFlawChooser.for_character(character("companion")), vf_id) == ""


def test_a_magus_is_gifted_and_so_is_anyone_holding_the_gift():
    hermetic = "vf_adept_laboratory_student"
    assert refusal(VirtueFlawChooser.for_character(character("magus")), hermetic) == ""
    gifted = character("companion", "vf_the_gift")
    assert refusal(VirtueFlawChooser.for_character(gifted), hermetic) == ""
    false_gift = character("companion", "vf_the_false_gift")
    assert refusal(VirtueFlawChooser.for_character(false_gift), hermetic) == ""


def test_grogs_take_no_major_or_hermetic_entries_and_not_the_gift():
    grog = VirtueFlawChooser.for_character(character("grog"))
    assert refusal(grog, "vf_wealthy") == "not for grogs: Major"
    assert refusal(grog, "vf_adept_laboratory_student") == "not for grogs: Hermetic"
    assert refusal(grog, "vf_the_gift") == "not for grogs"
    assert refusal(grog, "vf_the_false_gift") == "not for grogs"
    assert refusal(grog, "vf_common_sense") == ""
    assert refusal(grog, "vf_covenfolk") == ""
    # Holding The Gift anyway doesn't open Hermetic entries to a grog.
    gifted_grog = VirtueFlawChooser.for_character(character("grog", "vf_the_gift"))
    assert refusal(gifted_grog, "vf_adept_laboratory_student")


def test_non_human_entries_are_only_for_their_audience():
    human = VirtueFlawChooser.for_character(character("magus"))
    assert refusal(human, "vf_faerie_beast") == "only for faeries"
    assert refusal(human, "vf_aggressive") == "only for animals"
    assert refusal(human, "vf_gift_of_speech") == "only for magic beings"
    assert refusal(human, "vf_corrupted_beast") == (
        "only for corrupted beasts or animals"
    )


def test_mythic_companion_virtues_are_only_for_mythic_companions():
    mythic = VirtueFlawChooser.for_character(character("mythic companion"))
    companion = VirtueFlawChooser.for_character(character("companion"))
    for vf_id in MYTHIC_COMPANION_VIRTUES:
        assert vf(vf_id).audience == ["mythic companion"], vf_id
        assert refusal(mythic, vf_id) == "", vf_id
        assert refusal(companion, vf_id) == "only for Mythic Companions", vf_id
    # Otherwise a Mythic Companion chooses as a companion does.
    assert refusal(mythic, "vf_common_sense") == ""
    assert refusal(mythic, "vf_adept_laboratory_student") == "needs The Gift"
    assert refusal(mythic, "vf_faerie_beast") == "only for faeries"


def test_familiars_are_offered_animal_and_magic_being_entries():
    familiar = VirtueFlawChooser.for_familiar(Familiar(id="f1", character_id="c1"))
    assert refusal(familiar, "vf_aggressive") == ""  # animal
    assert refusal(familiar, "vf_gift_of_speech") == ""  # magic being
    assert refusal(familiar, "vf_common_sense") == ""  # anyone
    assert refusal(familiar, "vf_true_friend") == ""
    assert refusal(familiar, "vf_faerie_beast") == "only for faeries"
    assert refusal(familiar, "vf_nephilim") == "only for Mythic Companions"
    assert refusal(familiar, "vf_adept_laboratory_student") == "needs The Gift"


def test_books_not_in_play_are_refused():
    # None means every book; the core book is always in play.
    assert refusal(VirtueFlawChooser(), "vf_ablating") == ""
    core = VirtueFlawChooser(books=frozenset())
    assert refusal(core, "vf_common_sense") == ""
    assert refusal(core, "vf_ablating") == "book not in play"  # RoP:I
    # An entry citing several books is in play if any of them is.
    assert vf("vf_adjuration").source == "RoP:D; TC&TC"
    tc = VirtueFlawChooser(books=frozenset({"TC&TC"}))
    assert refusal(tc, "vf_adjuration") == ""


def test_nobody_in_particular_may_take_anything_without_an_audience():
    anyone = VirtueFlawChooser(gifted=True)
    for entry in catalog.load_virtue_flaw_catalog():
        assert (anyone.refusal(entry) == "") == (not entry.audience), entry.id

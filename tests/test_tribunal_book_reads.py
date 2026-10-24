"""Fixes from reading The Sundered Eagle, Against the Dark and Guardians of
the Forests against their packs."""

from ars_magica_manager import catalog, meeting, theban_meeting, tribunal_packages
from ars_magica_manager.book_packs.rhine import tribunal as rhine_tribunal
from ars_magica_manager.models import Character, Saga, Tribunal, VirtueFlawInstance
from ars_magica_manager.rules import creation_character, hedge_casting
from ars_magica_manager.tribunal_packages import rhine as rhine_package
from ars_magica_manager.tribunal_packages import theban as theban_package


def test_ice_harvesting_rounds_up():
    # Against the Dark p. 130: (Int + Lore + aura) / 3, rounded up.
    storm = catalog.load_tradition_catalog_by_id()["trad_storm_wizards"]
    rule = next(r for r in storm.casting if r.name == "Ice harvesting")
    assert hedge_casting.casting_total(rule, 7) == 3


def test_a_rhine_rank_stands_for_hermetic_magus():
    # Guardians of the Forests p. 20.
    magus = Character(
        id="m",
        name="M",
        type="magus",
        virtues_flaws=[
            VirtueFlawInstance("vf_the_gift"),
            VirtueFlawInstance("vf_master_rhine_tribunal"),
        ],
    )
    assert creation_character.missing_type_virtues(magus) == []
    assert rhine_tribunal.rank_sigils(magus) == 1


def test_the_rhine_meets_a_year_early_in_a_grand_tribunal_year():
    # Guardians of the Forests pp. 140, 143: 1227, not 1228.
    assert meeting.grand_tribunal_year(1228) and meeting.grand_tribunal_year(1261)
    assert tribunal_packages.PACKAGES[rhine_package.KEY].skips_grand_tribunal


def test_thebes_needs_no_quaesitor_and_pays_the_tamias_as_an_arche():
    # The Sundered Eagle pp. 25, 32.
    assert not tribunal_packages.PACKAGES[theban_package.KEY].quorum_needs_quaesitor
    assert theban_meeting.term_tokens("Tamias") == 0


def test_in_thebes_the_archon_votes_and_redcaps_dont():
    # The Sundered Eagle pp. 26, 32.
    thebes = Tribunal(id="t", name="Thebes", package=theban_package.KEY, praeco_id="a")
    assert meeting.officers(thebes) == set()
    redcap = Character(id="r", name="R", type="magus")
    redcap.hermetic.house = meeting.REDCAP_HOUSE
    assert meeting._silent(Saga(id="s", name="S"), thebes, redcap)


def test_ungifted_redcaps_have_no_vote_at_any_tribunal_but_gifted_ones_do():
    # DE p. 15.
    rhine = Tribunal(id="t", name="Rhine")
    saga = Saga(id="s", name="S")
    courier = Character(id="r", name="R", type="companion")
    courier.hermetic.house = meeting.REDCAP_HOUSE
    magus = Character(id="m", name="M", type="magus")
    magus.hermetic.house = meeting.REDCAP_HOUSE
    assert meeting._silent(saga, rhine, courier)
    assert not meeting._silent(saga, rhine, magus)

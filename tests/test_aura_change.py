"""Auras that change: Realms of Power: Magic's tethers, yearly modifier
and tables, and Realms of Power: The Infernal's erosion and corruption
rolls."""

from __future__ import annotations

import random

from support import everything_saga

from ars_magica_manager.models import Neighbour, SeasonRecord, SeasonRecordLine
from ars_magica_manager.rules import activities, aura_change, lab_seasons


def _place(**details):
    place = Neighbour(id="spring", name="The Spring", kind="place", realm="Magic")
    place.details = {"aura": 3, **details}
    return place


def test_tethers_give_the_base_aura():
    # RoP: Magic p. 8: natural ones add, up to 5; preternatural ones are the
    # strongest plus one for each other, up to 5; the two add.
    place = _place(
        tethers="A waterfall (natural 1), its rainbow (natural 1); a deep pool "
        "(natural 1)\nwater elementals (preternatural 2), a lost temple"
    )
    found = aura_change.tethers(place)
    assert [t["score"] for t in found] == [1, 1, 1, 2]  # the temple has no score
    assert aura_change.base_aura(found) == 5
    many = [aura_change.Tether(kind="natural", score=2)] * 4
    many += [aura_change.Tether(kind="preternatural", score=4)] * 3
    assert aura_change.base_aura(many) == 10


def test_the_yearly_modifier_sums_what_moves_the_aura():
    saga = everything_saga()
    place = _place(
        tethers="The old wood (natural 2)",
        impinging_divine=True,
        aura_adjust=1,
    )
    saga.neighbours.append(place)
    covenant = saga.covenants[0]
    covenant.place_id = place.id
    covenant.covenant_season = "Summer"
    magus = next(c for c in saga.characters if c.covenant_id == covenant.id)
    saga.season_records.append(
        SeasonRecord(
            saga.current_year,
            "Spring",
            [
                SeasonRecordLine(
                    magus.id,
                    magus.name,
                    covenant.id,
                    activities.ACTIVITIES[lab_seasons.EXTRACT].label,
                )
            ],
        )
    )
    terms = dict(aura_change.magic_terms(saga, place, saga.current_year))
    assert terms["Base aura 2, now 3"] == -3
    assert terms["A stronger Divine aura impinges"] == -6
    assert terms["Magic worked by a Summer covenant"] == 2
    assert terms["Vis extraction (1 seasons)"] == -1
    assert terms["Botches and other magic this year"] == 1
    assert aura_change.yearly_modifier(list(terms.items())) == -7


def test_the_modifier_is_capped_and_a_quiet_year_rolls_nothing():
    assert aura_change.yearly_modifier([("a", 12)]) == 9
    assert aura_change.yearly_modifier([("a", -12)]) == -9
    saga = everything_saga()
    saga.rule_options["aura_change"] = True
    quiet = _place()
    assert aura_change.year(saga, quiet, 1220, random.Random(1)) is None
    # A quiet year takes a botch die away.
    quiet.details["aura_botch_dice"] = 2
    result = aura_change.year(saga, quiet, 1220, random.Random(1))
    assert result is not None
    assert (["aura_botch_dice"], 1) in result.sets


def test_the_tables_read_as_the_book_does():
    st, wk = aura_change.STRENGTHENING, aura_change.WEAKENING
    assert aura_change.table_row(st, 6) == "No change."
    assert aura_change.table_row(st, 9).startswith("Latent strengthening")
    assert aura_change.table_row(st, 15) == "The aura's score rises by 1 for good."
    assert aura_change.table_row(st, 20) == "The aura's score rises by 1 for good."
    assert aura_change.table_row(wk, 11) == "The aura is 1 weaker for one season."


def test_a_permanent_result_moves_the_top_level_of_a_regio():
    saga = everything_saga()
    saga.rule_options["aura_change"] = True
    place = _place(levels=[{"name": "Above", "realm": "Magic", "aura": 4}])
    place.details["aura_adjust"] = 9  # sure to strengthen
    for seed in range(200):
        result = aura_change.year(saga, place, 1220, random.Random(seed))
        assert result is not None
        if any(path == ["levels", 0, "aura"] for path, _ in result.sets):
            assert (["levels", 0, "aura"], 5) in result.sets
            break
    else:
        raise AssertionError("no seed gave a permanent rise")


def test_corruption_rolls_and_a_dominant_infernal_aura():
    pit = Neighbour(id="pit", name="Pit", kind="place", realm="Infernal")
    pit.details = {"aura": 2, "around": 3}
    assert aura_change.corruption_eases(pit) == (6, 9)
    pit.details = {"aura": 4, "around": 3}  # now the strongest
    assert aura_change.corruption_eases(pit) == (7, 10)
    saga = everything_saga()
    saga.rule_options["aura_change"] = True
    assert aura_change.year(saga, pit, 1220, random.Random(1)) is None
    # An older save's "focus_gone" is read as its erosion clock.
    old = Neighbour(id="old", name="Old", kind="place", realm="Infernal")
    old.details = {"aura": 1, "around": 3, "focus_gone": 1219}
    result = aura_change.year(saga, old, 1220, random.Random(1))
    assert result is not None and (["aura"], 0) in result.sets


def test_twilight_is_rolled_against_the_aura_where_it_happened(monkeypatch):
    from ars_magica_manager.rules import warping
    from ars_magica_manager.seasons import character_effects

    saga = everything_saga()
    magus = next(c for c in saga.characters if c.type == "magus")
    seen = []
    real = warping.twilight

    def spy(character, gained, aura, rng, saga_=None, **kw):
        seen.append(aura)
        return real(character, gained, aura, rng, saga_, **kw)

    monkeypatch.setattr(character_effects.warping_rules, "twilight", spy)
    character_effects.gain_warping(saga, magus, 2, random.Random(1), aura=9)
    assert seen == [9]


def test_an_infernal_aura_may_be_tarnished_and_corrupted():
    from ars_magica_manager import place_events

    saga = everything_saga()
    pit = Neighbour(id="pit", name="Pit", kind="place", realm="Infernal")
    pit.details = {"aura": 3, "tarnish": "Lust", "corruption": "Debauched"}
    keys = [f.key for f in place_events.place_fields(saga, pit)]
    assert {"tarnish", "corruption"} <= set(keys)
    facts = {f.label: f.value for f in place_events.place_facts(saga, pit)}
    assert facts["Infernal"] == "Tarnished with Lust, debauched"
    assert place_events.place_problem({"aura": 2, "corruption": "Malevolent"})
    assert place_events.place_problem({"aura": 3, "corruption": "Malevolent"}) is None

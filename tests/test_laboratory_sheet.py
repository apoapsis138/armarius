"""The laboratory page's figures (laboratory_sheet), without a front-end."""

from __future__ import annotations

from screen_helpers import _saga_with_bare_laboratory, _sample_saga_with_covenant

from ars_magica_manager.sheets import laboratory as ls


def _lab():
    saga = _sample_saga_with_covenant()
    return saga, saga.laboratories[0]


def test_the_subtitle_names_the_owner_covenant_and_season():
    saga, lab = _lab()
    assert ls.subtitle(saga, lab) == (
        "The sanctum of Leandro  ·  Test Covenant  ·  Spring 1220"
    )


def test_the_aura_comes_from_the_covenant():
    saga, lab = _lab()
    aura = ls.aura(saga, lab)
    assert (aura.covenant, aura.modifier, aura.total, aura.realm) == (
        3,
        0,
        3,
        "Magic",
    )


def test_each_characteristic_keeps_its_typed_part_and_virtues_apart():
    _saga, lab = _lab()
    rows = {row.key: row for row in ls.characteristics(lab)}
    assert len(rows) == 8
    assert (rows["size"].manual, rows["size"].total) == (1, 1)
    assert (rows["safety"].manual, rows["safety"].virtues, rows["safety"].total) == (
        0,
        1,
        1,
    )
    assert rows["general_quality"].name == "General Quality"
    assert "Safety +1" in ls.characteristic_text(rows["safety"])


def test_a_virtue_card_says_what_it_does():
    _saga, lab = _lab()
    (card,) = ls.virtue_flaw_cards(lab, "Virtue")
    assert (card.name, card.tier, card.summary) == (
        "Superior Construction",
        "Free",
        "Safety +1, Aesthetics +1",
    )
    assert ls.virtue_flaw_cards(lab, "Flaw") == []


def test_lab_totals_cover_every_art_pair_for_a_magus_only():
    saga, lab = _lab()
    totals = ls.lab_totals(saga, lab)
    assert totals is not None and len(totals) == 5 * 10
    assert int(totals["Creo", "Ignem"].total) == 26
    assert "Lab Total 26" in ls.lab_total_text(totals["Creo", "Ignem"])
    bare = _saga_with_bare_laboratory()
    bare.characters[0].type = "companion"
    assert ls.lab_totals(bare, bare.laboratories[0]) is None


def test_a_feature_card_names_what_it_still_needs():
    _saga, lab = _lab()
    (card,) = ls.feature_cards(lab)
    assert (card.name, card.problem) == ("Well-Stocked", "needs a Feature Virtue")

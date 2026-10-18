"""Stats generated for the magi a book describes but prints no stat
block for: each comes from a profile by the creation rules, balanced,
within the caps, the same on every build, and says it was generated."""

from __future__ import annotations

import pytest

from ars_magica_manager import book_packs, catalog
from ars_magica_manager.book_packs import generated
from ars_magica_manager.book_packs.rhine.stats_sketched import PROFILES
from ars_magica_manager.models import Character
from ars_magica_manager.rules import creation_characteristics, creation_virtues
from ars_magica_manager.rules.xp import score_from_xp

RHINE = book_packs.PACKS["rhine"]
GENERATED = "Guardians of the Forests: The Rhine Tribunal prints no stat block"


@pytest.fixture(scope="module")
def saga():
    return RHINE.build()


def _generated(saga) -> list[Character]:
    return [c for c in saga.characters if c.id in PROFILES]


def test_every_magus_of_the_rhine_is_statted(saga):
    magi = [c for c in saga.characters if c.type == "magus"]
    assert all(c.detail == "Full" for c in magi)
    assert len(_generated(saga)) == len(PROFILES) == 61
    for magus in _generated(saga):
        assert magus.description.biography.startswith(GENERATED)


def test_a_generated_magus_balances_their_virtues_and_flaws(saga):
    for magus in _generated(saga):
        found = creation_virtues.tally(magus)
        allowed, _ = creation_virtues.virtue_allowance(magus, found.flaw_points)
        assert found.virtue_points == allowed, magus.name
        assert found.flaw_points <= creation_virtues.MAX_FLAW_POINTS, magus.name
        assert not found.repeated, magus.name


def test_a_generated_magus_spends_seven_points_on_characteristics(saga):
    for magus in _generated(saga):
        bought = {
            name: getattr(magus.characteristics, name)
            for name in generated.CHARACTERISTICS
        }
        for vf in magus.virtues_flaws:
            if vf.vf_id == creation_characteristics.GREAT:
                bought[vf.params["characteristic"]] -= 1
        assert sum(creation_characteristics.cost(v) for v in bought.values()) == 7


def test_scores_stay_within_the_caps_and_spells_within_the_lab_total(saga):
    spells = catalog.load_spell_catalog_by_id()
    for magus in _generated(saga):
        arts = {a: score_from_xp(s.xp, 1) for a, s in magus.arts.items()}
        assert all(v <= generated.ART_CAP for v in arts.values())
        assert all(
            score_from_xp(a.xp, 5) <= generated.ABILITY_CAP
            for a in magus.abilities
            if not a.name.startswith("Living Language")
        )
        theory = next(
            (
                score_from_xp(a.xp, 5)
                for a in magus.abilities
                if a.name == "Magic Theory"
            ),
            0,
        )
        for known in magus.spells_known:
            spell = spells[known.spell_id]
            lowest = min(
                arts[a.lower()] for a in (spell.technique, *spell.requisites)
            ) + min(arts[a.lower()] for a in (spell.form, *spell.requisites))
            total = lowest + magus.characteristics.intelligence + theory + 3
            assert (spell.level or 0) <= total, (magus.name, spell.name)


def test_the_pack_generates_the_same_stats_every_build(saga):
    again = {c.id: c for c in RHINE.build().characters}
    for magus in _generated(saga):
        twin = again[magus.id]
        assert twin.arts == magus.arts
        assert twin.abilities == magus.abilities
        assert twin.spells_known == magus.spells_known


def test_an_age_the_book_leaves_out_is_assumed_and_said(saga):
    by_id = {c.id: c for c in saga.characters}
    tabanus = by_id["tabanus"]
    assert tabanus.background.year_born == saga.current_year - 50
    assert "no age: 50 is assumed" in tabanus.description.biography
    assert "assumed" not in by_id["murion"].description.biography


def test_an_ungifted_redcap_has_abilities_but_no_arts(saga):
    horst = next(c for c in saga.characters if c.id == "horst")
    names = {v.vf_id for v in horst.virtues_flaws}
    assert "vf_redcap" in names and "vf_the_gift" not in names
    assert not horst.arts and not horst.spells_known
    assert any(a.name == "Magic Theory" for a in horst.abilities)


def test_a_profile_whose_virtues_outweigh_its_flaws_fails_the_build():
    magus = Character(
        id="x", name="X", type="magus", summary="Master of House Bonisagus"
    )
    magus.hermetic.house = "house_bonisagus"
    with pytest.raises(ValueError, match="outweigh"):
        generated.stat_block(magus, generated.Profile(virtues=["Wealthy"]), 1220)
    block, age = generated.stat_block(
        magus, generated.Profile(virtues=["Wealthy", "Enemies"]), 1220
    )
    assert age == 50 and "Wealthy" in block["virtues_flaws"]


def _abilities(block) -> dict[str, tuple[int, str]]:
    return {name: (score, spec) for name, score, spec in block["abilities"]}


def test_a_theban_magus_learns_the_art_in_greek_and_knows_their_tribunal():
    magus = Character(id="y", name="Y", type="magus")
    magus.hermetic.house = "house_mercere"
    block, _ = generated.stat_block(
        magus, generated.Profile(native="Greek"), 1220, "TSE"
    )
    found = _abilities(block)
    score, specialty = found["Dead Language: Classical Greek"]
    assert score >= 4 and specialty == "Hermetic usage"
    assert "Dead Language: Latin" not in found
    assert "Area Lore: Rhine Tribunal" not in found
    lore = found.get("Organization Lore: Order of Hermes")
    assert lore is None or lore[1] == "the Theban Tribunal"
    # An incomer trained in the West keeps Latin.
    block, _ = generated.stat_block(
        magus, generated.Profile(hermetic="Latin"), 1220, "TSE"
    )
    assert "Dead Language: Latin" in _abilities(block)


def test_the_import_form_offers_the_book_s_sketches_instead():
    from ars_magica_manager import packs, transfer
    from ars_magica_manager.models import Saga

    data = book_packs.data(RHINE)
    fields = {f.key: f for f in packs.import_fields(data)}
    tick = fields[packs.GENERATED]
    assert tick.value is True and tick.label.startswith("Generated stats for magi (")
    assert packs.INFERRED in tick.hint
    assert tick.show_if is not None and not tick.show_if({"people": False})
    ticked = {key: True for key in fields}
    sketched = packs.narrow(data, {**ticked, packs.GENERATED: False})
    target = Saga(id="dst", name="Target")
    transfer.apply(target, transfer.plan_import(target, sketched))
    by_name = {c.name: c for c in target.characters}
    murion = by_name["Murion"]
    assert murion.detail == "Sketch" and not murion.arts and not murion.virtues_flaws
    assert not murion.description.biography
    assert by_name["Philippus Niger"].detail == "Full"
    assert data["saga"]["characters"], "the pack itself is untouched"
    full = Saga(id="full", name="Full")
    transfer.apply(full, transfer.plan_import(full, packs.narrow(data, ticked)))
    murion = next(c for c in full.characters if c.name == "Murion")
    assert murion.detail == "Full" and packs.INFERRED in murion.description.biography

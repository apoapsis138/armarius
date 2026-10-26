"""Vis by the book: extraordinary, dedicated and faerie vis, Things of
Virtue, vis storage, and magic creatures' Might recovery (RoP: Magic
pp. 30, 119-128; RoP: Faerie pp. 18-19)."""

from __future__ import annotations

from typing import Any

import pytest
from dialog_contract_support import Contract, covenant, run_contract
from textual.widgets import Select

from ars_magica_manager import possessions as pos
from ars_magica_manager import seasons, vis
from ars_magica_manager.casting_text import known_spell_casting_lines
from ars_magica_manager.models import (
    Ability,
    ArtScore,
    Character,
    Characteristics,
    Covenant,
    Creature,
    KnownSpell,
    Neighbour,
    Possession,
    Saga,
    Spell,
)
from ars_magica_manager.models.covenant import Covenant as CovenantModel
from ars_magica_manager.models.holdings import VIS_KINDS
from ars_magica_manager.rules import casting, sites, vis_kinds
from ars_magica_manager.rules import creation_covenant as cov
from ars_magica_manager.rules.xp import ability_xp, art_xp
from ars_magica_manager.sheets import creature as creature_sheet


def _store(id: str = "v", **kw: Any) -> Possession:
    fields = {"name": "Cask", "art": "Ignem", "pawns": 4, **kw}
    return Possession(id=id, kind="vis_store", **fields)


def _saga(*stores: Possession) -> Saga:
    covenant = Covenant(id="c", saga_id="s", name="Keep", aura=3)
    covenant.possessions = list(stores)
    magus = Character(
        id="m",
        name="Leandro",
        type="magus",
        covenant_id="c",
        characteristics=Characteristics(stamina=2, intelligence=2),
        arts={
            "creo": ArtScore(xp=art_xp(10)),
            "ignem": ArtScore(xp=art_xp(8)),
            "rego": ArtScore(xp=art_xp(4)),
        },
        abilities=[
            Ability("Artes Liberales", xp=ability_xp(2)),
            Ability("Philosophiae", xp=ability_xp(1)),
        ],
    )
    return Saga(
        id="s",
        name="S",
        current_season="Summer",
        covenants=[covenant, Covenant(id="far", saga_id="s", name="Far")],
        characters=[magus],
    )


# -- the kinds --


def test_the_kinds_table_and_the_model_agree_and_a_bad_kind_is_refused():
    assert tuple(k.key for k in vis_kinds.KINDS) == VIS_KINDS
    with pytest.raises(ValueError, match="unknown kind of vis 'golden'"):
        _store(vis_kind="golden")
    # An older save's store, with none of the new fields, is ordinary vis.
    old = CovenantModel.from_dict(
        {
            "id": "c",
            "saga_id": "s",
            "name": "Keep",
            "possessions": [{"id": "v", "kind": "vis_store", "art": "Vim", "pawns": 2}],
        }
    )
    [store] = old.possessions
    assert (store.vis_kind, store.paired_art, store.effect_level) == ("", "", None)


def test_a_form_offers_the_kinds_of_the_books_in_play():
    saga = _saga()
    saga.books_in_play = ["RoP:F"]
    offered = [key for _, key in vis_kinds.kind_options(saga)]
    assert offered == ["encased", "anchor", "accrued", "sleeping", "abstract"]
    # A store's own kind stays on offer.
    assert "dedicated" in [k for _, k in vis_kinds.kind_options(saga, "dedicated")]
    saga.books_in_play = []
    assert vis_kinds.kind_options(saga) == []
    saga.books_in_play = None  # every book
    assert len(vis_kinds.kind_options(saga)) == len(VIS_KINDS) - 1


def test_dedicated_vis_needs_a_technique_and_a_form_and_things_their_art():
    assert vis_kinds.problem({"vis_kind": "dedicated", "art": "Creo"}) == (
        "Dedicated vis needs its other Art: a Technique and a Form."
    )
    assert vis_kinds.problem(
        {"vis_kind": "dedicated", "art": "Creo", "paired_art": "Rego"}
    ) == ("Dedicated vis is one Technique and one Form together.")
    assert (
        vis_kinds.problem(
            {"vis_kind": "dedicated", "art": "Ignem", "paired_art": "Creo"}
        )
        is None
    )
    assert vis_kinds.problem(
        {"vis_kind": "object_of_virtue", "art": "Vim", "virtue_thing": "sapphire"}
    ) == ("Sapphire holds Intellego vis, not Vim.")
    # Changed back to ordinary vis, the store drops what went with its kind.
    cleaned = vis_kinds.clean(
        {
            "vis_kind": None,
            "paired_art": "Creo",
            "virtue_thing": "jet",
            "effect_level": 20,
        }
    )
    assert cleaned == {
        "vis_kind": "",
        "paired_art": "",
        "virtue_thing": "",
        "effect_level": None,
    }


# -- dedicated vis in casting, study and enchanting (RoP: Magic pp. 122-123) --


def test_dedicated_vis_of_the_spells_arts_is_worth_four_a_pawn_and_double_botches():
    magus = _saga().characters[0]
    score = casting.casting_score(
        magus, "Creo", "Ignem", vis_pawns=3, dedicated_pawns=2
    )
    vis_lines = [
        (line.label, line.amount) for line in score.lines if "vis" in line.label
    ]
    assert vis_lines == [("2 pawns of vis, dedicated", 8), ("1 pawns of vis", 2)]
    assert casting.botch_dice(vis_pawns=3) == 4
    assert casting.botch_dice(vis_pawns=3, dedicated_vis_pawns=2) == 6
    store = _store(vis_kind="dedicated", art="Ignem", paired_art="Creo")
    assert vis_kinds.dedicated_pair(store) == ("Creo", "Ignem")
    assert vis_kinds.dedicated_for(store, "Creo", "Ignem")
    assert not vis_kinds.dedicated_for(store, "Rego", "Ignem")  # ordinary for it
    assert vis_kinds.dedicated_pawns_to_pay(6) == 3
    assert vis_kinds.dedicated_pawns_to_pay(5) == 3


def test_studying_and_enchanting_dedicated_vis():
    # Source Quality (stress die + aura) / 2 for each Art; double botch dice.
    assert vis_kinds.dedicated_study_quality(9, 4) == 6
    assert vis_kinds.dedicated_study_botch_dice(3) == 6
    assert vis_kinds.dedicated_study_problem(2, 3) is not None
    assert vis_kinds.dedicated_study_problem(3, 3) is None
    # A human bone of Corpus vis: +3 / +4 doubled (p. 123).
    assert vis_kinds.dedicated_shape_bonus(4) == 8


def test_a_ritual_of_the_pair_notes_what_its_dedicated_store_does():
    saga = _saga(
        _store("d", name="Ember", vis_kind="dedicated", art="Ignem", paired_art="Creo"),
        _store("a", name="Promise", vis_kind="abstract", art="Creo"),
        _store("x", name="Ball of Light", vis_kind="lesser_enchantment"),
    )
    magus = saga.characters[0]
    ritual = Spell(
        id="r", name="Fire Ward", technique="Creo", form="Ignem", level=30, ritual=True
    )
    lines = known_spell_casting_lines(saga, magus, KnownSpell(spell_id="r"), ritual)
    text = "\n".join(lines)
    assert "Ember: dedicated Creo Ignem vis, +4 a pawn" in text
    assert "(3 of its pawns pay this Ritual's 6)" in text
    assert "Promise: faerie: abstract vis can't be spent." in text
    assert "Ball of Light: spending it as vis ends its power" in text
    # Another pair: the dedicated store is ordinary vis for it.
    notes = vis.casting_notes(saga, magus, "Rego", "Ignem", 6)
    assert not any("Ember" in note for note in notes)


# -- the covenant's stores --


def test_season_work_pays_ordinary_vis_first_and_never_abstract():
    plain = _store("p", name="Plain", pawns=2)
    special = _store("e", name="Ember", vis_kind="lesser_enchantment", pawns=3)
    promise = _store("a", name="Promise", vis_kind="abstract", pawns=5)
    saga = _saga(special, promise, plain)
    keep = saga.covenants[0]
    pool = vis.StorePool(saga, keep, "Leandro")
    assert pool["ignem"] == 5  # the abstract pawns aren't vis
    pool["ignem"] = 2
    assert plain not in keep.possessions  # spent first
    assert special.pawns == 2 and promise.pawns == 5
    # Vis added joins an ordinary store, never a special one.
    pool["ignem"] = 4
    assert special.pawns == 2
    [new] = [p for p in keep.possessions if not p.vis_kind]
    assert (new.art, new.pawns) == ("Ignem", 2)


def test_special_vis_keeps_its_kind_moving_between_covenants_and_harvested():
    ember = _store("e", name="Ember", vis_kind="dedicated", paired_art="Creo")
    saga = _saga(ember, _store("p", name="Plain", pawns=1))
    keep, far = saga.covenants
    [held] = [h for h in vis.held(keep) if h.store is ember]
    assert held.label == "Ember (Ignem: 4 pawn(s), Dedicated (Creo Ignem))"
    vis.move(saga, keep, held, 2, far)
    [moved] = far.possessions
    assert (moved.name, moved.vis_kind, moved.paired_art, moved.pawns) == (
        "Ember",
        "dedicated",
        "Creo",
        2,
    )
    assert "(Dedicated (Creo Ignem))" in far.diary[-1].name
    # A dedicated source's harvest goes into a store of its own kind.
    source = Possession(
        "well",
        "vis_source",
        name="Hearth",
        art="Ignem",
        pawns=2,
        season="Summer",
        vis_kind="dedicated",
        paired_art="Creo",
    )
    keep.possessions.append(source)
    seasons.covenant_season(saga, {})
    assert ember.pawns == 4  # 2 left + 2 harvested
    assert next(p for p in keep.possessions if p.name == "Plain").pawns == 1


def test_build_points_and_trade_value_of_special_vis():
    # RoP: Magic p. 124: dedicated 7.5 a pawn a year, lesser enchantment 5 +
    # 0-2 a magnitude (the middle, 1), spell-like 5 + 1-3 (2).
    dedicated = Possession(
        "s", "vis_source", name="Hearth", pawns=2, vis_kind="dedicated"
    )
    glass = Possession(
        "g",
        "vis_source",
        name="Glass",
        pawns=1,
        vis_kind="lesser_enchantment",
        effect_level=14,
    )
    seed = Possession(
        "e", "vis_source", name="Seed", pawns=1, vis_kind="spell_like", effect_level=40
    )
    stock = _store("k", name="Embers", pawns=10, vis_kind="dedicated")
    saga = _saga(dedicated, glass, seed, stock)
    costs = {c.label: c.points for c in cov.costs(saga, saga.covenants[0])}
    assert costs["Vis source: Hearth (2 a year)"] == 15
    assert costs["Vis source: Glass (1 a year)"] == 8  # 5 + 3 magnitudes
    assert costs["Vis source: Seed (1 a year)"] == 21  # 5 + 2 x 8
    assert costs["Vis stock: Embers (10 pawns)"] == 3  # 2 x 7.5 / 5
    assert vis_kinds.trade_value(dedicated) == 1.5
    assert vis_kinds.trade_value(_store(vis_kind="abstract")) == 0
    assert vis_kinds.suggested_pawns(25) == 3


# -- Things of Virtue (RoP: Magic pp. 124-128) --


def test_things_of_virtue_and_enrichment():
    stones = [t.name for t in vis_kinds.THINGS_OF_VIRTUE if t.formed_stone]
    assert "Thunderbolt" in stones and "Fairy Loaves" in stones
    fennel = vis_kinds.THINGS_BY_ID["fennel"]
    assert (fennel.kind, fennel.art, fennel.pawns) == ("herb_of_virtue", "Vim", 2)
    first, _ = vis_kinds.thing_options("herb_of_virtue")[0]
    assert first == "Centaury (2 Rego)"
    wise = Character(
        id="w",
        name="Wise woman",
        type="companion",
        characteristics=Characteristics(intelligence=2),
        abilities=[Ability("Magic Lore", xp=ability_xp(4))],
    )
    total = vis_kinds.enrichment_total(wise, 3)
    assert total.total == 9 >= vis_kinds.ENRICHMENT_LEVEL
    assert vis_kinds.enrichment_herb_years(2) == 2


def test_the_store_details_name_its_kind_thing_and_what_storing_it_does():
    jet = _store(
        "j",
        name="Black stone",
        art="Perdo",
        pawns=1,
        vis_kind="object_of_virtue",
        virtue_thing="jet",
    )
    hoard = _store("h", name="Rot", art="Perdo", pawns=24)
    saga = _saga(jet, hoard)
    entries = pos.entries_for_kind(saga, saga.covenants[0], "vis_store")
    text = pos.detail_text(entries[0])
    assert "Object of Virtue: Jet:" in text
    assert "Enriched: Puissant Stealth" in text
    # 25 pawns of Perdo vis together: second magnitude in a low-vis saga.
    assert entries[1].kept_together == 25
    assert "spontaneous Perdo spells of level 10 or less" in pos.detail_text(entries[1])
    assert "wood rots" in pos.detail_text(entries[1])
    dedicated = _store("d", vis_kind="dedicated", paired_art="Creo")
    assert "Worth 1.5 ordinary pawn(s) a pawn in trade" in "\n".join(
        pos.vis_kind_lines(dedicated)
    )


def test_vis_storage_magnitudes():
    # Four queens with a queen the least: spells of level 20 (p. 123).
    assert vis_kinds.storage_magnitude(400, vis_kinds.HIGH_VIS_LEAST) == 4
    assert vis_kinds.storage_magnitude(9, vis_kinds.LOW_VIS_LEAST) == 0
    assert vis_kinds.storage_note("Vim", 9) == ""


# -- magic creatures (RoP: Magic pp. 30, 54) --


def test_might_recovery_in_a_magic_aura():
    # The book's example: aura 3, Might 10: 12 hours, a point every 1:12.
    assert vis_kinds.might_recovery(3, 10) == (720, 72.0)
    assert vis_kinds.recovery_text(3, 10) == (
        "Resting in its Magic aura 3: all its Might in 12 hours, a point every "
        "1 hour 12 minutes (RoP: Magic p. 30)"
    )
    assert vis_kinds.might_recovery(1, 15) is None  # too weak for its Might
    assert vis_kinds.might_recovery(20, 5) == (2, 0.4)  # past the chart
    assert vis_kinds.recovery_text(20, 5).endswith(
        "a point every under a minute (RoP: Magic p. 30)"
    )


def test_a_magic_creatures_sheet_shows_its_might_recovery():
    saga = _saga()
    glade = Neighbour(
        id="glade", name="Glade", kind=sites.PLACE, realm="Magic", details={"aura": 5}
    )
    saga.neighbours.append(glade)
    hart = Creature(
        id="hart", name="White Hart", realm="Magic", might=15, place_id="glade"
    )
    facts = {f.label: f.value for f in creature_sheet.facts(saga, hart)}
    # 5 - 15 / 5 = 2: 6 hours, a point every 24 minutes.
    assert facts["Might recovery"].startswith(
        "Resting in its Magic aura 5: all its Might in 6 hours, a point every 24 minutes"
    )
    imp = Creature(id="imp", name="Imp", realm="Infernal", might=10, place_id="glade")
    assert "Might recovery" not in {f.label for f in creature_sheet.facts(saga, imp)}


# -- the form --


async def test_the_vis_store_form_takes_a_dedicated_pair():
    await run_contract(
        "add vis store",
        Contract(
            prefill={"Name": "", "Kind of vis": Select.NULL},
            edits={
                "Name": "Ember",
                "Art": "Ignem",
                "Pawns": "2",
                "Kind of vis": "dedicated",
                "Dedicated with": "Creo",
            },
            saved=lambda s: [
                (p.vis_kind, p.paired_art, p.virtue_thing)
                for p in covenant(s).possessions
                if p.name == "Ember"
            ],
            expected=[("dedicated", "Creo", "")],
            invalid=[
                {"Name": "Ember", "Art": "Ignem", "Kind of vis": "dedicated"},
                {
                    "Name": "Ember",
                    "Art": "Ignem",
                    "Kind of vis": "dedicated",
                    "Dedicated with": "Aquam",
                },
            ],
            shown={"#pos-vis_store-list": "Ember"},
        ),
    )

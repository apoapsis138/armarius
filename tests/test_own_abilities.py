"""A saga's own Abilities: Supernatural Abilities a troupe designs (Houses
of Hermes: Societates pp. 103-106), kept with the saga beside the Ability
catalog, made and changed in House Rules."""

from __future__ import annotations

import json
from dataclasses import asdict

import pytest
from support import strip_markup

from ars_magica_manager import books, catalog, storage, transfer
from ars_magica_manager import house_rules as hr
from ars_magica_manager import own_abilities as oa
from ars_magica_manager import saga_content as sc
from ars_magica_manager.commands import Confirm, Refuse
from ars_magica_manager.forms import saga_content as scf
from ars_magica_manager.models import (
    Ability,
    AbilityDef,
    Character,
    Covenant,
    Saga,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import creation_access, hybrid_magic
from ars_magica_manager.sheets import saga_content as scs


def _saga() -> Saga:
    return Saga(
        id="test_saga",
        name="Saga",
        covenants=[Covenant(id="cov1", saga_id="test_saga", name="Keep")],
        characters=[Character(id="c1", name="Ana", type="companion")],
    )


def _values(name: str = "Call the Tide", **more) -> dict:
    return {
        "name": name,
        "category": "Supernatural",
        "realm": "Magic",
        "characteristic": "Stamina",
        "with_virtue": True,
        **more,
    }


def test_an_ability_and_its_major_supernatural_virtue_join_the_catalogs():
    """A designed Ability is a Major Supernatural Virtue's (p. 104): adding
    one adds both, and a Virtue of its name grants it."""
    saga = _saga()
    ability = hr.add(saga, hr.ABILITY, _values())
    assert isinstance(ability, AbilityDef)
    assert (ability.id, ability.realm, ability.characteristic, ability.source) == (
        "custom_ability_call_the_tide",
        "Magic",
        "Stamina",
        "",
    )
    [virtue] = saga.custom_virtues_flaws
    assert (virtue.name, virtue.type, virtue.tier, virtue.cost, virtue.category) == (
        "Call the Tide",
        "Virtue",
        "Major",
        3,
        "Supernatural",
    )
    assert ability.id in catalog.load_ability_catalog_by_id()
    assert ability in catalog.load_ability_catalog()
    assert ability.id not in {a.id for a in sc.CATALOGS["abilities"].shared()}
    ana = saga.characters[0]
    assert "Call the Tide" not in creation_access.granted_supernatural(ana)
    ana.virtues_flaws.append(VirtueFlawInstance(virtue.id))
    assert "Call the Tide" in creation_access.granted_supernatural(ana)
    assert creation_access.may_learn(ana, "Call the Tide")
    assert creation_access.ability_category("Call the Tide") == "Supernatural"
    # The cached lookups of the catalog's names see it too.
    assert books.canonical_ability("call the tide") == "Call the Tide"
    assert hybrid_magic._supernatural("Call the Tide")
    catalog.use_saga(None)
    assert ability.id not in catalog.load_ability_catalog_by_id()
    assert books.canonical_ability("call the tide") is None


def test_a_virtue_already_offered_is_not_added_again_and_others_get_none():
    saga = _saga()
    hr.add(saga, hr.ABILITY, _values())
    hr.add(saga, hr.ABILITY, _values("Tide Sense", with_virtue=False))
    hr.add(saga, hr.ABILITY, _values("Sea Lore", category="Arcane", realm="Faerie"))
    assert [v.name for v in saga.custom_virtues_flaws] == ["Call the Tide"]
    lore = saga.custom_abilities[-1]
    # Realm and Accelerated belong to a Supernatural Ability only.
    assert (lore.category, lore.realm, lore.xp_table) == ("Arcane", "", "ability")


def test_the_form_refuses_a_blank_or_known_name_and_bad_choices():
    saga = _saga()
    assert hr.form_problem(saga, hr.ABILITY, _values("")) == "Name is required."
    assert "already an Ability of the catalog" in str(
        hr.form_problem(saga, hr.ABILITY, _values("summon animals"))
    )
    hr.add(saga, hr.ABILITY, _values())
    catalog.use_saga(None)  # whichever saga is in use, its own are checked
    assert "already an Ability of the saga" in str(
        hr.form_problem(saga, hr.ABILITY, _values("CALL THE TIDE"))
    )
    assert hr.form_problem(saga, hr.ABILITY, _values("Odd {x}"))
    assert hr.form_problem(saga, hr.ABILITY, _values(realm="Aether"))
    assert hr.form_problem(saga, hr.ABILITY, _values(characteristic="Luck"))
    assert hr.form_problem(saga, hr.ABILITY, _values(category="Hedge Art"))
    # Editing keeps its own name.
    own = saga.custom_abilities[0]
    assert hr.form_problem(saga, hr.ABILITY, _values(), own) is None


def test_renaming_follows_its_holders_and_its_virtue_and_a_held_one_stays():
    saga = _saga()
    ability = hr.add(saga, hr.ABILITY, _values())
    ana = saga.characters[0]
    ana.abilities.append(Ability("Call the Tide", "Supernatural", xp=15))
    # Whether it is Accelerated can't change while it's held.
    assert "can't change" in str(
        hr.form_problem(saga, hr.ABILITY, _values(accelerated=True), ability)
    )
    renamed = hr.update(saga, hr.ABILITY, ability, _values("Summon the Tide"))
    assert renamed.id == ability.id
    assert saga.custom_abilities == [renamed]
    assert [a.name for a in ana.abilities] == ["Summon the Tide"]
    assert [v.name for v in saga.custom_virtues_flaws] == ["Summon the Tide"]
    assert hr.used_by(saga, hr.ABILITY, renamed) == ["Ana"]
    # House Rules lists the Virtues first, the Abilities after them.
    at = [entry for _, entry in hr.all_entries(saga)].index(renamed)
    assert at == 1
    assert isinstance(scf.house_rule_ops(saga).remove(at), Refuse)
    ana.abilities.clear()
    confirm = scf.house_rule_ops(saga).remove(at)
    assert isinstance(confirm, Confirm)
    confirm.apply()
    assert saga.custom_abilities == []
    # Its Virtue stays: it may be held, and is deleted on its own.
    assert [v.name for v in saga.custom_virtues_flaws] == ["Summon the Tide"]
    assert renamed.id not in catalog.load_ability_catalog_by_id()


def test_the_details_give_its_roll_and_the_rules_of_p104():
    saga = _saga()
    ability = hr.add(saga, hr.ABILITY, _values(accelerated=True))
    assert oa.accelerated(ability)
    detail = strip_markup(hr.detail_text(saga, (hr.ABILITY, ability)))
    assert "Granted by: the Major Virtue Call the Tide   Held by: (no one yet)" in (
        detail
    )
    assert "Casting Total: Stamina + Call the Tide + aura + die" in detail
    assert "Casting Total - Ease Factor + Penetration bonus" in detail
    # Accelerated: its spell level is its Casting Total (p. 104; Errata p. 60).
    assert "As a spell: level its Casting Total" in detail
    assert "Puissant gives +2" in detail
    # Puissant +2 and no vis study are Societates'; the Errata adds only
    # that it isn't limited at creation.
    assert "not studied from vis (Societates p. 104)" in detail
    assert "not limited at creation (Errata p. 60)" in detail
    row = strip_markup(hr.row_label(hr.ABILITY, ability)).split()
    assert row == ["Call", "the", "Tide", "Ability", "Ability"]
    assert len(strip_markup(hr.row_label(hr.ABILITY, ability))) <= len(
        hr.table_header()
    )
    plain = hr.add(saga, hr.ABILITY, _values("Tide Lore", category="Academic"))
    plain_detail = strip_markup(hr.detail_text(saga, (hr.ABILITY, plain)))
    assert "Casting Total" not in plain_detail
    assert "Rolls: Stamina + Tide Lore" in plain_detail
    # The Virtue's card first, then a card for each Ability.
    _virtue, card, lore = scs.house_rule_cards(saga)
    assert (card.kind, card.type, card.tier, card.points, card.gives) == (
        "Supernatural",
        "Ability",
        "Magic",
        "Rolls Stamina + Call the Tide",
        False,
    )
    assert lore.category == "Academic"


def test_the_form_shows_its_fields_only_for_an_ability():
    saga = _saga()
    fields = {f.key: f for f in scf.house_rule_fields(saga, None)}
    ability = {"kind": hr.ABILITY, "category_ability": "Supernatural"}
    virtue = {"kind": hr.CHARACTER}
    for key in ("realm", "characteristic", "accelerated", "with_virtue"):
        assert fields[key].show_if is not None
        assert fields[key].show_if(ability), key
        assert not fields[key].show_if(virtue), key
    for key in ("tier", "repeatable", "vf_type"):
        assert not fields[key].show_if(ability), key
    assert not fields["realm"].show_if({**ability, "category_ability": "General"})
    assert fields["category_ability"].value == "Supernatural"
    assert fields["realm"].value == "Magic"
    built = scf.house_rule_values(
        None, {**ability, "name": "Call the Tide", "characteristic": "Presence"}
    )
    assert "Presence + Call the Tide + aura" in scf.house_rule_live(None, built)
    # Editing: what it is is fixed, and no second Virtue is offered.
    made = hr.add(saga, hr.ABILITY, _values())
    edit = {f.key for f in scf.house_rule_fields(saga, (hr.ABILITY, made))}
    assert "with_virtue" not in edit and "kind" not in edit


def test_a_saga_ability_loads_and_saves_and_a_bad_realm_is_named():
    saga = _saga()
    hr.add(saga, hr.ABILITY, _values(realm="Infernal"))
    storage.save_saga(saga)
    loaded = storage.load_saga("test_saga")
    assert [asdict(a) for a in loaded.custom_abilities] == [
        asdict(a) for a in saga.custom_abilities
    ]
    # An older save has none.
    old = asdict(saga)
    del old["custom_abilities"]
    assert Saga.from_dict(old).custom_abilities == []
    bad = asdict(saga)
    bad["custom_abilities"][0]["realm"] = "Aether"
    with pytest.raises(ValueError, match="Call the Tide"):
        Saga.from_dict(bad)


def test_an_exported_character_takes_the_saga_abilities_he_holds():
    saga = _saga()
    hr.add(saga, hr.ABILITY, _values())
    hr.add(saga, hr.ABILITY, _values("Unused Gift", with_virtue=False))
    ana = saga.characters[0]
    ana.abilities.append(Ability("Call the Tide", "Supernatural", xp=5))
    data = json.loads(json.dumps(transfer.export_data(saga, ana)))
    assert [a["name"] for a in data["saga"]["custom_abilities"]] == ["Call the Tide"]
    target = Saga(id="dst", name="Other")
    catalog.use_saga(target)
    transfer.apply(target, transfer.plan_import(target, data))
    assert [a.name for a in target.custom_abilities] == ["Call the Tide"]
    # A saga that already has it keeps its own.
    again = transfer.plan_import(target, data)
    assert again.custom["custom_abilities"] == []


def test_its_virtue_may_be_made_minor_instead():
    """Add its Virtue makes a Major Supernatural Virtue unless Minor is
    chosen, as the DE's Second Sight grants an Ability (DE p. 106)."""
    saga = _saga()
    fields = {f.key: f for f in scf.house_rule_fields(saga, None)}
    tier = fields["virtue_tier"]
    assert tier.value == "Major" and tier.show_if is not None
    ability = {"kind": hr.ABILITY, "category_ability": "Supernatural"}
    assert tier.show_if({**ability, "with_virtue": True})
    assert not tier.show_if({**ability, "with_virtue": False})
    built = scf.house_rule_values(
        None,
        {**ability, "name": "Sea Sight", "with_virtue": True, "virtue_tier": "Minor"},
    )
    made = hr.add(saga, hr.ABILITY, built)
    [virtue] = saga.custom_virtues_flaws
    assert (virtue.tier, virtue.cost) == ("Minor", 1)
    detail = strip_markup(hr.detail_text(saga, (hr.ABILITY, made)))
    assert "Granted by: the Minor Virtue Sea Sight" in detail

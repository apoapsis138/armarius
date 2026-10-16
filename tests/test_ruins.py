"""Ruined covenants: the marking, how a ruin shows, and founding a
covenant on one."""

from __future__ import annotations

from ars_magica_manager import (
    artwork,
    book_packs,
    neighbours,
    packs,
    places,
    region_sheet,
    ruins,
)
from ars_magica_manager.models import Neighbour, Saga


def _saga() -> tuple[Saga, Neighbour]:
    saga = Saga(id="s", name="Saga")
    ruin = neighbours.add(saga, places.PLACE, "Rethra")
    ruin.realm = "Faerie"
    ruin.details.update({"aura": 4, places.RUINED: True})
    return saga, ruin


def test_a_ruin_shows_as_a_ruin():
    saga, ruin = _saga()
    plain = neighbours.add(saga, places.PLACE, "The Black Forest")
    assert places.is_ruin(ruin) and not places.is_ruin(plain)
    assert region_sheet.kind_text(ruin) == "Ruin"
    assert region_sheet.kind_text(plain) == "Place"
    assert region_sheet.card_subtitle(ruin) == "Ruined covenant · Faerie 4"
    assert neighbours.icon_concept(ruin) == "ruin"
    assert neighbours.icon_concept(plain) == "place"
    assert artwork.icon("ruin").name == "ruin.svg"


def test_the_place_form_marks_a_ruin():
    saga, ruin = _saga()
    (marking,) = [f for f in places.fields(saga, ruin) if f.key == places.RUINED]
    assert marking.kind == "check" and marking.value is True


def test_founding_a_covenant_on_a_ruin():
    saga, ruin = _saga()
    fields = {f.key: f.value for f in ruins.found_fields(saga, ruin)}
    assert fields["name"] == "Rethra" and fields["aura_realm"] == "Faerie"
    assert fields["winter_ruins"] is True
    ruins.found(saga, ruin, {**fields, "name": "New Rethra"})
    (covenant,) = saga.covenants
    assert covenant.name == "New Rethra" and covenant.in_creation
    # Sited on the ruin, it takes the place's aura.
    assert covenant.place_id == ruin.id
    assert (covenant.aura, covenant.aura_realm) == (4, "Faerie")
    # Winter Ruins's Boons and Hooks: three Contested Resources among them.
    taken = [bh.vf_id for bh in covenant.boons_hooks]
    assert taken.count("covbh_hook_minor_contested_resource") == 3
    # The place is claimed, and no longer a ruin.
    assert not places.is_ruin(ruin)
    assert ruin.details["claimed_by"] == covenant.id


def test_founding_without_winter_ruins():
    saga, ruin = _saga()
    values = {f.key: f.value for f in ruins.found_fields(saga, ruin)}
    ruins.found(saga, ruin, {**values, "winter_ruins": False})
    assert saga.covenants[0].boons_hooks == []


def test_the_rhine_marks_its_fallen_covenants():
    data = packs.transfer.read(book_packs.PACKS_DIR / "rhine.amm.json")
    ruined = sorted(
        n["name"]
        for n in data["saga"]["neighbours"]
        if n.get("details", {}).get(places.RUINED)
    )
    assert ruined == ["Rethra", "Rüdesheim and the Brömserburg", "Treverorum"]


def _with_regio(saga: Saga, ruin: Neighbour, realm: str = "Magic") -> None:
    ruin.details["levels"] = [{"name": "The Painted Hall", "realm": realm, "aura": 7}]


def test_founding_in_a_ruins_regio_takes_the_regio_boon():
    saga, ruin = _saga()
    _with_regio(saga, ruin)
    fields = {f.key: f for f in ruins.found_fields(saga, ruin)}
    assert [label for label, _ in fields["site"].options] == [
        "Surface (Faerie 4)",
        "Level 1: The Painted Hall (Magic 7)",
    ]
    assert fields["site"].fills is not None
    assert fields["site"].fills({"site": "1"}) == {"aura_realm": "Magic"}
    values = {key: f.value for key, f in fields.items()}
    values.update(site="1", regio_boon="major", winter_ruins=False)
    ruins.found(saga, ruin, values)
    (covenant,) = saga.covenants
    assert covenant.place_level == 1
    assert (covenant.aura, covenant.aura_realm) == (7, "Magic")
    assert [bh.vf_id for bh in covenant.boons_hooks] == ["covbh_boon_major_regio"]


def test_founding_beside_a_regio_takes_the_regio_hook():
    saga, ruin = _saga()
    _with_regio(saga, ruin, realm="Faerie")
    values = {f.key: f.value for f in ruins.found_fields(saga, ruin)}
    ruins.found(saga, ruin, {**values, "winter_ruins": False})
    assert [bh.vf_id for bh in saga.covenants[0].boons_hooks] == [
        "covbh_hook_minor_regio",
        "covbh_hook_minor_non_magical_regio",
    ]


def test_a_ruin_without_a_regio_asks_no_site():
    saga, ruin = _saga()
    assert "site" not in {f.key for f in ruins.found_fields(saga, ruin)}

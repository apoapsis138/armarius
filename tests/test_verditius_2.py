"""The rest of House Verditius: Script components (The Mysteries Revised
Edition pp. 15-16; DE p. 388), the House's prices and forge-companions
(Houses of Hermes: Mystery Cults pp. 113-115), Hubris as it grows, its
Ordeals and vendettas, and the confraternities (pp. 115, 119-123; DE pp.
241-242)."""

from __future__ import annotations

import random

import pytest

from ars_magica_manager import catalog
from ars_magica_manager.forms import hubris as hubris_forms
from ars_magica_manager.forms import script_components as script_forms
from ars_magica_manager.models import (
    CHARGED,
    INVESTED,
    LESSER,
    Ability,
    Character,
    Characteristics,
    Covenant,
    EnchantedDevice,
    InstilledEffect,
    Laboratory,
    Saga,
    ScoredTrait,
    ScriptPart,
    SeasonPlan,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import enchantment, mysteries, verditius
from ars_magica_manager.rules import supplement_work as sw
from ars_magica_manager.rules import tradition_seasons as ts
from ars_magica_manager.rules.season_work import initiation
from ars_magica_manager.rules.xp import ability_xp
from ars_magica_manager.seasons.lab_apply import _apply_initiation

LORE = verditius.CULT_LORE
TRADITION = verditius.CULT_TRADITION


def _magus(
    *vf_ids: str, id_: str = "m", name: str = "Hephaestion", lore: int = 0
) -> Character:
    magus = Character(id=id_, name=name, type="magus", covenant_id="cov")
    magus.characteristics = Characteristics(intelligence=3, presence=2)
    magus.virtues_flaws = [VirtueFlawInstance(v) for v in vf_ids]
    magus.abilities = [
        Ability("Magic Theory", xp=ability_xp(5)),
        Ability("Philosophiae", xp=ability_xp(4)),
        Ability("Leadership", xp=ability_xp(2)),
    ]
    if lore:
        magus.abilities.append(Ability(LORE, xp=ability_xp(lore)))
    return magus


def _saga(*characters: Character) -> Saga:
    return Saga(
        id="s",
        name="S",
        covenants=[Covenant(id="cov", saga_id="s", name="Keep")],
        characters=list(characters),
        laboratories=[Laboratory(id="lab", covenant_id="cov", name="Forge")],
    )


def _plan(**kw: object) -> SeasonPlan:
    base: dict[str, object] = {"teacher_id": "v", "title": "Mercere Lore"}
    return SeasonPlan("m", 1220, "Spring", "undergo_initiation", [], **(base | kw))  # type: ignore[arg-type]


# -- Script components (TMRE pp. 15-16; DE p. 388) ---------------------------------


def test_the_components_table_holds_the_mysteries_revised_edition_s_too():
    by_key = {c.key: c for c in mysteries.COMPONENTS}
    assert by_key["unique_quest"].bonus == 6
    assert by_key["mystagogue_time"].bonus == 3
    assert (by_key["great_sacrifice"].least, by_key["great_sacrifice"].most) == (3, 6)
    assert (by_key["sympathy"].least, by_key["sympathy"].most) == (-5, 5)
    # One bonus only: the special place, material goods and time (TMRE p. 15).
    assert by_key["place"].once and by_key["goods"].once and by_key["time"].once
    assert not by_key["quest"].once  # several Quests are possible
    assert {s: c.bonus for s, c in mysteries.ORDEAL_COMPONENTS.items()} == {
        "Minor": 3,
        "Medium": 6,
        "Major": 9,
    }
    # The Ordeals' components aren't listed: the Ordeal chosen gives them.
    listed = {c.key for c in mysteries.listed_components(mysteries.COMPONENTS)}
    assert "ordeal_minor" not in listed and "quest" in listed


@pytest.mark.parametrize(
    ("parts", "problem"),
    [
        ([ScriptPart("quest"), ScriptPart("quest")], ""),
        ([ScriptPart("place"), ScriptPart("place")], "only once"),
        ([ScriptPart("ordeal_minor")], "comes from the Ordeal chosen"),
        ([ScriptPart("great_sacrifice", 7)], "+3 to +6"),
        ([ScriptPart("sympathy", -6)], "-5 to +5"),
        ([ScriptPart("dragon")], "isn't one this Initiation offers"),
    ],
)
def test_what_makes_a_script_invalid(parts, problem):
    found = mysteries.parts_problem(parts, mysteries.COMPONENTS)
    assert (problem in found) if problem else found == ""


def test_the_book_s_example_darius():
    # TMRE p. 16: a Minor Ordeal +3, a Quest +3, a talisman sacrificed +5
    # and sympathy +1 make +12.
    parts = [
        ScriptPart("quest", note="defeat his nemesis"),
        ScriptPart("great_sacrifice", 5, "his long spear talisman"),
        ScriptPart("sympathy", 1),
    ]
    plan = _plan(
        script_components=parts,
        ordeal_kind="gain",
        device_id="vf_dutybound",
    )
    initiate = _magus()
    lines = initiation.script_lines(initiate, plan)
    assert [line.amount for line in lines] == [3, 5, 1, 3]
    assert sum(line.amount or 0 for line in lines) == 12
    assert mysteries.lines_text(lines).endswith("= +12")


def test_an_initiation_built_from_components():
    initiate = _magus()
    mystagogue = _magus(id_="v", name="Sebastiano")
    mystagogue.characteristics.presence = 3
    mystagogue.abilities.append(Ability("Mercere Lore", xp=ability_xp(7)))
    initiate.abilities.append(Ability("Mercere Lore", xp=ability_xp(1)))
    saga = _saga(initiate, mystagogue)
    plan = _plan(
        effect_id="vf_self_confident",
        script_components=[ScriptPart("quest"), ScriptPart("place")],
        ordeal_kind="gain",
        device_id="vf_dutybound",
        other_modifier=1,
    )
    assert sw.problems(saga, initiate, plan) == []
    done = sw.work(saga, initiate, plan, random.Random(1))
    # Presence 3 + Lore 7 + Quest 3 + place 3 + Minor Ordeal 3 + 1 typed.
    assert done.notes[-1].startswith("Initiation Total 20")
    assert any(n.startswith("The Script: Specific Quest +3") for n in done.notes)
    assert any("with +1 more" in n for n in done.notes)
    plan.script_components.append(ScriptPart("place"))
    assert "only once" in sw.problems(saga, initiate, plan)[0]


def test_a_typed_bonus_alone_is_unchanged():
    # No components listed: the typed Script bonus is the whole Script, and
    # the Ordeal adds nothing more (as before).
    initiate = _magus()
    plan = _plan(other_modifier=12, ordeal_kind="gain", device_id="vf_dutybound")
    assert initiation.script_lines(initiate, plan) == []
    assert initiation._initiation_terms(initiate, plan)[3] == 12


def test_a_verditius_first_inner_mystery_counts_its_hubris_ordeal():
    initiate = _magus("vf_verditius_magic", lore=3)
    plan = _plan(
        title=LORE,
        effect_id="vf_items_of_quality",
        script_components=[
            ScriptPart("verditius_lesser_item"),
            ScriptPart("mystagogue_time"),
        ],
    )
    lines = initiation.script_lines(initiate, plan)
    assert [(line.label, line.amount) for line in lines][-1] == (
        "Minor Ordeal (Hubris)",
        3,
    )
    # The House's own components are offered only to a Verditius.
    keys = {c.key for c in initiation.components_for(initiate)}
    assert "verditius_greater_item" in keys
    assert "verditius_greater_item" not in {
        c.key for c in initiation.components_for(_magus())
    }


def test_the_house_s_scripts_add_up_to_their_bonus():
    tradition = catalog.load_tradition_catalog_by_id()[TRADITION]
    assert tradition.initiation is not None
    scripts = tradition.initiation.scripts
    assert all(s.components for s in scripts)
    differ = [s.name for s in scripts if sum(b for _, b in s.components) != s.bonus]
    # The Outer Mystery's components add to 14; the book prints +12 (p. 118).
    assert differ == ["Outer Mystery: Verditius Magic"]
    note = mysteries.printed_components_note(scripts[0].components, scripts[0].bonus)
    assert note.endswith("= +14; the book prints +12, which is used.")


def test_a_confraternity_s_script_notes_its_path():
    initiate = _magus("vf_verditius_magic", lore=3)
    mystagogue = _magus("vf_verditius_magic", id_="v", name="Valens", lore=6)
    saga = _saga(initiate, mystagogue)
    plan = _plan(
        title="",
        hedge_script=f"{TRADITION}/Confraternity of Irene: Puissant Imaginem or Mentem",
    )
    done = sw.work(saga, initiate, plan, None)
    path = next(n for n in done.notes if "Confraternity of Irene" in n)
    assert "Slow Caster" in path and "Automata" in path
    assert any(n.startswith("The Script's components") for n in done.notes)
    found = verditius.confraternity_of("Confraternity of Himinis: Bind Curse")
    assert found is not None and found.flaw == "Envious"
    assert verditius.confraternity_of("Automata") is None


def test_the_plan_keeps_its_components():
    plan = _plan(script_components=[ScriptPart("great_sacrifice", 5, "his talisman")])
    data = {
        **plan.__dict__,
        "script_components": [
            {"key": "great_sacrifice", "bonus": 5, "note": "his talisman"}
        ],
    }
    again = SeasonPlan.from_dict(data)
    assert again.script_components == plan.script_components
    with pytest.raises(ValueError, match="isn't a whole number"):
        ScriptPart.from_dict({"key": "quest", "bonus": "lots"})


def test_the_component_entry_form():
    table = initiation.components_for(_magus())
    fields = {f.key: f for f in script_forms.part_fields(table, None)}
    assert fields["component"].value == "place"
    assert fields["bonus"].show_if is not None
    assert not fields["bonus"].show_if({"component": "quest"})
    assert fields["bonus"].show_if({"component": "sympathy"})
    # A fixed component keeps the table's bonus whatever is typed.
    part = script_forms.part_from(
        {"component": "quest", "bonus": 9, "note": " x "}, table
    )
    assert part == ScriptPart("quest", 3, "x")
    assert script_forms.row(table)(ScriptPart("sympathy", 2)).endswith("+2")


# -- Prices for enchantments (pp. 114-115) -------------------------------------------


def _wand(maker: Character, **kw: object) -> EnchantedDevice:
    base: dict[str, object] = {
        "holder_kind": "character",
        "holder_id": maker.id,
        "maker_id": maker.id,
        "verditius_runes": True,
        "verditius_craft": "Craft: Metalsmith",
    }
    return EnchantedDevice("wand", "Iron wand", INVESTED, **(base | kw))  # type: ignore[arg-type]


def test_the_elder_runes_example_price():
    # p. 128: opening cost 2 pawns after his Craft, 6 for the power and 1
    # for the rune: 9 pawns, so 18 for the work and 27 in all.
    maker = _magus("vf_verditius_magic")
    maker.abilities.append(Ability("Craft: Metalsmith", xp=ability_xp(8)))
    wand = _wand(
        maker,
        pawns_opened=10,
        elder_runes=["Rego"],
        effects=[
            InstilledEffect(
                "e", "Earth Split", "Rego", "Terram", level=30, vis_override=6
            )
        ],
    )
    saga = _saga(maker)
    assert verditius.device_vis(saga, wand) == 9
    assert verditius.house_fee(9) == 18
    line = verditius.price_lines(saga, wand)[0]
    assert "18 pawns besides the 9 it takes (27 in all)" in line
    assert "135 Mythic Pounds" in line
    assert "3 Hubris experience" in line


def test_the_automaton_example_price_to_a_mundane():
    # p. 114: 15 Mythic Pounds times the vis cost; p. 132: 22 pawns, 330.
    assert verditius.mundane_price(22) == 330
    magpie = EnchantedDevice(
        "m", "Tin magpie", INVESTED, capacity_override=11, verditius_item="automaton"
    )
    assert verditius.sale_hubris_xp(magpie) == 3  # Might 11: 3 magnitudes


def test_hubris_for_each_kind_of_sale():
    maker = _magus()
    lesser = EnchantedDevice("l", "Ring", LESSER, maker_id="m")
    charged = EnchantedDevice("c", "Wands", CHARGED, maker_id="m")
    attuned = _wand(maker, verditius_item=enchantment.ATTUNED)
    assert [verditius.sale_hubris_xp(d) for d in (lesser, charged, attuned)] == [
        1,
        1,
        6,
    ]
    line = verditius.price_lines(_saga(maker), charged)[0]
    assert line.startswith("House price: it takes no vis")
    assert "twice the vis its maker could have extracted" in line
    assert "15 Mythic Pounds a pawn of that vis" in line


def test_forge_companions_help_with_their_master_s_craft():
    master = _magus("vf_verditius_magic")
    smiths = []
    for n, score in enumerate((10, 5, 4)):
        smith = Character(id=f"f{n}", name=f"Smith {n}", type="companion")
        smith.abilities = [Ability("Craft: Metalsmith", xp=ability_xp(score))]
        smiths.append(smith)
    lines, notes = verditius.forge_companion_lines(master, smiths, "Craft: Metalsmith")
    # Leadership 2: two help, +2 and +1; the third is beyond his Leadership.
    assert [line.amount for line in lines] == [2, 1]
    assert "only the first 2 help" in notes[0]
    lines, notes = verditius.forge_companion_lines(
        master, smiths[:1], "Craft: Carpenter"
    )
    assert lines == [] and "adds nothing" in notes[0]


# -- Hubris as it grows, Ordeals and vendettas (pp. 115, 119-121) ----------------------


def test_an_inner_mystery_keeps_hubris_on_the_sheet():
    initiate = _magus("vf_verditius_magic", "vf_proud", lore=3)
    mystagogue = _magus(
        "vf_verditius_magic", "vf_verditius_elder_runes", id_="v", name="V", lore=6
    )
    mystagogue.characteristics.presence = 1
    saga = _saga(initiate, mystagogue)
    plan = _plan(
        title="",
        hedge_script=f"{TRADITION}/Verditius Elder Runes",
        effect_id="vf_verditius_elder_runes",
    )
    done = sw.work(saga, initiate, plan, random.Random(1))
    assert done.initiated
    assert (done.hubris_start, done.hubris_xp, done.hubris_rises) == (2, 1, 0)
    _apply_initiation(initiate, done)
    trait = verditius.hubris_trait(initiate)
    assert trait is not None and (trait.score, trait.deeds) == (2, 1)


def test_the_increased_hubris_ordeal_gives_a_point():
    initiate = _magus("vf_verditius_magic", "vf_hubris", lore=3)
    initiate.personality_traits.append(ScoredTrait("Hubris", 2, deeds=4))
    mystagogue = _magus(
        "vf_verditius_magic", "vf_items_of_quality", id_="v", name="V", lore=6
    )
    saga = _saga(initiate, mystagogue)
    plan = _plan(
        title="",
        hedge_script=f"{TRADITION}/Items of Quality",
        effect_id="vf_items_of_quality",
        ordeal_kind="gain",
        device_id=verditius.INCREASED_HUBRIS,
    )
    assert sw.problems(saga, initiate, plan) == []
    done = sw.work(saga, initiate, plan, random.Random(1))
    assert done.initiated and done.hubris_rises == 1 and done.hubris_start == 0
    _apply_initiation(initiate, done)
    # +1 for learning the Minor Mystery (4 + 1 of the 15 needed), then the
    # Ordeal's 10 more: Hubris 3, with nothing toward 4.
    trait = verditius.hubris_trait(initiate)
    assert trait is not None and (trait.score, trait.deeds) == (3, 0)


def test_gaining_hubris_experience():
    magus = _magus("vf_hubris")
    assert verditius.gain_hubris(magus, 3) == ""  # no trait, no start
    assert (
        verditius.gain_hubris(magus, 0, start=1)
        == "Hubris 1: +0 experience (0 toward the next point)."
    )
    assert verditius.xp_to_next_hubris(magus) == 10
    assert verditius.gain_hubris(magus, 12) == "Hubris 1 -> 2 (+12 experience)."
    assert verditius.xp_to_next_hubris(magus) == 13


def test_refusing_a_vendetta():
    magus = _magus("vf_hubris")
    magus.personality_traits.append(ScoredTrait("Hubris", 3, deeds=7))
    said = verditius.refuse_vendetta(magus)
    trait = verditius.hubris_trait(magus)
    assert trait is not None and (trait.score, trait.deeds) == (2, 0)
    rep = next(r for r in magus.reputations if r.name == "Dishonorable")
    assert (rep.score, rep.reach) == (4, "House Verditius")
    assert said[0] == "Hubris falls to 2."
    assert [(r.magus, r.hubris, r.waged) for r in magus.refused_vendettas] == [
        ("", 3, False)
    ]


def test_a_refused_vendetta_made_good_loses_the_reputation():
    # p. 115: lost by regaining the Hubris score and waging a vendetta on
    # the magus refused.
    magus = _magus("vf_hubris")
    magus.personality_traits.append(ScoredTrait("Hubris", 3, deeds=7))
    verditius.refuse_vendetta(magus, "Rival")
    assert "Hubris back to 3 (now 2)" in verditius.refusal_lines(magus)[0]
    said = verditius.wage_refused_vendetta(magus, "Rival")
    assert said == ["Wages a vendetta on Rival."]  # Hubris not yet regained
    assert any(r.name == "Dishonorable" for r in magus.reputations)
    verditius.gain_hubris(magus, 15)
    said = verditius.settle_vendettas(magus)
    assert said and "Dishonorable lost" in said[0]
    assert magus.refused_vendettas == []
    assert not any(r.name == "Dishonorable" for r in magus.reputations)
    with pytest.raises(LookupError):
        verditius.wage_refused_vendetta(magus, "Rival")


def test_resisting_a_vendetta():
    assert verditius.vendetta_ease(6, 7) == 13
    held, said = verditius.resist_vendetta(random.Random(3), 30, 6, 7)
    assert held and "against 13: resisted." in said
    held, said = verditius.resist_vendetta(random.Random(3), -30, 6, 7)
    assert not held


def test_the_hubris_more_form():
    magus = _magus("vf_verditius_magic")
    saga = _saga(magus)
    assert not hubris_forms.offers(saga, magus)
    magus.virtues_flaws.append(VirtueFlawInstance("vf_hubris"))
    assert hubris_forms.offers(saga, magus)
    values = {"what": "Winning the Contest, masters"}
    said = hubris_forms.record(saga, magus, values, random.Random(1))
    # No trait yet: made at 1, then +6 experience.
    trait = verditius.hubris_trait(magus)
    assert trait is not None and (trait.score, trait.deeds) == (1, 6)
    assert said and magus.diary[-1].name == "Hubris"
    values = {"what": hubris_forms.RESIST, "resisting": 3, "challenger": 2}
    assert "against 3" in hubris_forms.hubris_lines(magus, values)[0]
    values = {"what": verditius.AUTOMATON, "might": 11}
    assert hubris_forms.hubris_lines(magus, values)[0].startswith(
        "+3 Hubris experience"
    )
    hubris_forms.record(
        saga, magus, {"what": hubris_forms.REFUSE, "refused": "Rival"}, random.Random(1)
    )
    assert magus.diary[-1].name == "Refused a vendetta"
    assert [r.magus for r in magus.refused_vendettas] == ["Rival"]
    fields = {f.key: f for f in hubris_forms.hubris_fields(magus)}
    assert (hubris_forms.WAGE_CHOICE[0], hubris_forms.WAGE) in fields["what"].options
    assert fields["target"].value == "Rival"
    hubris_forms.record(
        saga, magus, {"what": hubris_forms.WAGE, "target": "Rival"}, random.Random(1)
    )
    assert magus.diary[-1].name == "Waged a refused vendetta"
    assert magus.refused_vendettas[0].waged


def test_the_house_s_scripts_are_still_offered():
    initiate = _magus("vf_verditius_magic", lore=3)
    keys = [key for _, key in ts.script_options(_saga(initiate), initiate)]
    assert f"{TRADITION}/Confraternity of Balento: Bind Magical Creatures" in keys

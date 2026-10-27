"""The Verditius Mysteries: the House's Initiations, Script components,
Lore gates, Hubris and Ordeals, and the Inner Mysteries' laboratory rules
(Houses of Hermes: Mystery Cults pp. 116-135; DE pp. 240-243)."""

from __future__ import annotations

import random

from ars_magica_manager.forms import device as device_form
from ars_magica_manager.models import (
    INVESTED,
    LESSER,
    Ability,
    ArtScore,
    Character,
    Characteristics,
    Covenant,
    DeviceComponent,
    EnchantedDevice,
    InstilledEffect,
    Laboratory,
    Saga,
    ScoredTrait,
    SeasonPlan,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import enchant_seasons as es
from ars_magica_manager.rules import enchantment, lab_seasons, mysteries, verditius
from ars_magica_manager.rules import supplement_work as sw
from ars_magica_manager.rules import tradition_seasons as ts
from ars_magica_manager.rules.xp import ability_xp, art_xp

LORE = verditius.CULT_LORE
TRADITION = verditius.CULT_TRADITION


def _magus(
    *vf_ids: str, id_: str = "m", name: str = "Hephaestion", lore: int = 0
) -> Character:
    magus = Character(id=id_, name=name, type="magus", covenant_id="cov")
    magus.characteristics = Characteristics(intelligence=3, presence=1)
    magus.virtues_flaws = [VirtueFlawInstance("vf_verditius_magic")] + [
        VirtueFlawInstance(v) for v in vf_ids
    ]
    magus.abilities = [
        Ability("Magic Theory", xp=ability_xp(5)),
        Ability("Philosophiae", xp=ability_xp(4)),
    ]
    if lore:
        magus.abilities.append(Ability(LORE, xp=ability_xp(lore)))
    return magus


def _saga(*characters: Character) -> Saga:
    covenant = Covenant(id="cov", saga_id="s", name="Keep")
    lab = Laboratory(id="lab", covenant_id="cov", name="Forge", owner_id="m")
    return Saga(
        id="s",
        name="S",
        covenants=[covenant],
        characters=list(characters),
        laboratories=[lab],
    )


# -- Initiation (pp. 116-121) ----------------------------------------------------


def test_the_house_s_script_components():
    bonuses = {c.name: c.bonus for c in verditius.VERDITIUS_COMPONENTS}
    assert bonuses["A unique Quest (a legendary item lost since antiquity)"] == 6
    assert bonuses["The Outer Mystery taught as the Arts are opened"] == 6
    wealth = next(c for c in verditius.VERDITIUS_COMPONENTS if "wealth" in c.name)
    assert wealth.bonus == 1 and wealth.once
    # The Outer Mystery's Script: special place 3, the Initiate's time 1,
    # the Mystagogue's time 3, wealth 1, Arts opened 6 = +12 (p. 118).
    names = (
        "Travel to a Forge of Hephaestus, or a special place at a special time",
        "The Initiate sacrifices time serving the House",
        "The Mystagogue sacrifices time (teaching or training)",
        "The Mystagogue sacrifices wealth (a Mythic Pound per point of Hubris)",
        "The Outer Mystery taught as the Arts are opened",
    )
    script = [c for c in verditius.VERDITIUS_COMPONENTS if c.name in names]
    # The components named add to 14; the book prints +12, which is kept.
    assert mysteries.script_bonus(script) == 14
    assert verditius.OUTER_SCRIPT_BONUS == 12


def test_the_outer_mystery_s_mystagogue():
    master = _magus(lore=1)
    master.characteristics.presence = 2
    assert "needs Verditius Cult Lore 2" in verditius.outer_mystery_problem(master)
    assert verditius.outer_mystery_problem(master, opens_arts=False) == ""
    master.characteristics.presence = 0
    assert "below 3" in verditius.outer_mystery_problem(master, opens_arts=False)
    master = _magus(lore=2)
    assert verditius.outer_mystery_problem(master) == ""
    # Presence 1 + Lore 2 + 12 = 15, the Target.
    total = verditius.outer_initiation_total(master)
    assert int(total.total) == verditius.OUTER_TARGET == 15


def test_the_lore_an_inner_mystery_needs():
    initiate = _magus(lore=2)
    assert "Lore 3" in verditius.inner_mystery_problem(initiate, "vf_items_of_quality")
    initiate = _magus(lore=3)
    assert verditius.inner_mystery_problem(initiate, "vf_items_of_quality") == ""
    assert "Lore 5" in verditius.inner_mystery_problem(initiate, "vf_automata")
    outsider = Character(id="x", name="Outsider", type="magus")
    assert "Outer Mystery" in verditius.inner_mystery_problem(outsider, "vf_bind_curse")
    assert verditius.inner_mystery_problem(outsider, "vf_puissant_art") == ""
    # The other names of the Lore count.
    initiate.abilities[-1].name = "Verditius Cult Lore"
    assert verditius.cult_lore(initiate) == 3


def test_the_first_inner_mystery_brings_hubris():
    magus = _magus("vf_proud", id_="x", name="Milo", lore=3)
    notes = verditius.initiation_notes(magus, "vf_verditius_elder_runes")
    assert verditius.gives_hubris(magus, "vf_verditius_elder_runes")
    assert "Hubris Personality Trait to 2" in notes[0]
    assert "1 experience toward Hubris" in notes[1]
    magus.virtues_flaws.append(VirtueFlawInstance(verditius.HUBRIS_FLAW))
    assert not verditius.gives_hubris(magus, "vf_automata")
    assert verditius.initiation_notes(magus, "vf_automata") == [
        "Learning a Major Inner Mystery: 3 experience toward Hubris "
        f"({verditius.HUBRIS_SOURCE})."
    ]
    assert verditius.initiation_notes(magus, "vf_puissant_art") == []


def test_the_house_s_ordeals():
    magus = _magus(lore=3)
    assert verditius.ordeal_problem(magus, verditius.PRONE_TO_CHANCE) == ""
    magus.virtues_flaws.append(VirtueFlawInstance(verditius.AVERSE_TO_RISK))
    assert "can't both" in verditius.ordeal_problem(magus, verditius.PRONE_TO_CHANCE)
    assert "already" in verditius.ordeal_problem(magus, verditius.AVERSE_TO_RISK)
    magus.virtues_flaws.append(VirtueFlawInstance(verditius.PRIMOGENITURE))
    assert "Primus's line" in verditius.ordeal_problem(
        magus, "vf_sever_the_ties_that_bind"
    )
    assert verditius.ordeal_problem(magus, "vf_arthritis") == ""


def _initiation(**kw: object) -> SeasonPlan:
    base: dict[str, object] = {
        "teacher_id": "v",
        "title": "",
        "hedge_script": f"{TRADITION}/Verditius Elder Runes",
        "effect_id": "vf_verditius_elder_runes",
    }
    return SeasonPlan("m", 1220, "Spring", "undergo_initiation", [], **(base | kw))  # type: ignore[arg-type]


def test_the_house_s_scripts_are_offered_to_its_magi():
    initiate = _magus(lore=3)
    saga = _saga(initiate)
    keys = [key for _, key in ts.script_options(saga, initiate)]
    assert f"{TRADITION}/Item Attunement" in keys
    found = ts.hedge_script(f"{TRADITION}/Reforging Enchanted Items")
    assert found is not None and (found[1].ease_factor, found[1].bonus) == (15, 7)
    assert ts.belongs(initiate, TRADITION)
    stranger = Character(id="x", name="Stranger", type="magus")
    assert ts.script_options(_saga(stranger), stranger) == []


def test_an_inner_mystery_initiated_by_the_house_s_script():
    initiate = _magus(lore=3)
    mystagogue = _magus("vf_verditius_elder_runes", id_="v", name="Valens", lore=6)
    mystagogue.characteristics.presence = 1
    saga = _saga(initiate, mystagogue)
    plan = _initiation()
    assert sw.problems(saga, initiate, plan) == []
    # Ease 15 (known); Presence 1 + Lore 6 + Script 9, + 3 for the first
    # Inner Mystery's Hubris Ordeal (HoH:MC p. 117) = 19.
    assert sw.initiation_target(saga, initiate, plan) == 15
    done = sw.work(saga, initiate, plan, random.Random(1))
    assert done.initiated
    assert [vf.vf_id for vf in done.add_vfs] == [
        "vf_verditius_elder_runes",
        verditius.HUBRIS_FLAW,
    ]
    assert done.ordeal == "Minor"
    assert done.notes[-1].startswith("Initiation Total 19")
    assert any("Hubris Personality Trait to 1" in n for n in done.notes)


def test_what_stops_a_house_initiation():
    initiate = _magus(lore=2)
    mystagogue = _magus(id_="v", name="Valens", lore=6)
    saga = _saga(initiate, mystagogue)
    found = sw.problems(saga, initiate, _initiation())
    assert found and "Mystery Cult Lore: Verditius 3" in found[0]
    # The plain Initiation (no Script chosen) checks the Lore too.
    plan = _initiation(hedge_script="", title=LORE)
    assert "needs Verditius Cult Lore 3" in sw.problems(saga, initiate, plan)[0]
    initiate.abilities[-1].xp = ability_xp(3)
    initiate.virtues_flaws.append(VirtueFlawInstance(verditius.PRONE_TO_CHANCE))
    plan = _initiation(ordeal_kind="gain", device_id=verditius.AVERSE_TO_RISK)
    assert "can't both" in sw.problems(saga, initiate, plan)[0]


# -- Elder Runes (pp. 127-128) -----------------------------------------------------


def _enchanter(*vf_ids: str) -> tuple[Saga, Character, EnchantedDevice]:
    """The book's example (p. 128): Rego 8, Terram 19, Intelligence 3,
    Magic Theory 5, Philosophiae 4, a wand with the "Ice" rune."""
    magus = _magus(*vf_ids)
    magus.arts = {
        "rego": ArtScore(xp=art_xp(8)),
        "terram": ArtScore(xp=art_xp(19)),
        "vim": ArtScore(xp=art_xp(5)),
    }
    magus.raw_vis = {"vim": 20, "rego": 5, "terram": 10}
    wand = EnchantedDevice(
        "wand",
        "Iron wand",
        INVESTED,
        holder_kind="character",
        holder_id="m",
        capacity_override=10,
        elder_runes=["Rego"],
        effects=[
            InstilledEffect(
                "split",
                "The Earth Split Asunder",
                "Rego",
                "Terram",
                level=30,
                uses_per_day="",
                maintains_concentration=True,
                instilling_progress=0,
            )
        ],
    )
    saga = _saga(magus)
    saga.enchanted_devices = [wand]
    return saga, magus, wand


def _plan(activity: str, **kw: object) -> SeasonPlan:
    return SeasonPlan("m", 1220, "Spring", activity, lab_id="lab", **kw)  # type: ignore[arg-type]


def test_a_rune_raises_each_effect_s_level_and_takes_its_pawn():
    _, _, wand = _enchanter()
    effect = wand.effects[0]
    # 30 + 5 maintaining concentration + 5 for the rune = 40 (p. 128).
    assert enchantment.modified_level(wand, effect) == 40
    assert ("Elder rune (Rego)", 5) in enchantment.level_breakdown(wand, effect)
    assert enchantment.pawns_used(wand, effect) == 4 + 1
    assert verditius.rune_vis(wand) == {"Rego": 1}
    lesser = EnchantedDevice("r", "Ring", LESSER, elder_runes=["Rego"])
    assert enchantment.elder_runes(lesser) == []


def test_opening_inscribes_the_runes():
    saga, magus, _ = _enchanter()
    found, _ = lab_seasons.work(saga, magus, _plan(es.OPEN, device_id="wand"))
    assert found == ["Hephaestion hasn't been Initiated into Verditius Elder Runes."]
    magus.virtues_flaws.append(VirtueFlawInstance(verditius.ELDER_RUNES))
    found, work = lab_seasons.work(saga, magus, _plan(es.OPEN, device_id="wand"))
    assert found == [] and work is not None
    assert work.vis_cost == {"Vim": 10, "Rego": 1}


def test_the_rune_doubles_its_art_and_the_vis_limit_grows():
    saga, magus, wand = _enchanter(verditius.ELDER_RUNES)
    assert verditius.enchanting_vis_limit(magus) == 20  # 5 x 4, not 10
    wand.pawns_opened, wand.maker_id = 10, "m"
    plan = _plan(es.INSTIL, device_id="wand", effect_id="split", vis_art="Terram")
    found, work = lab_seasons.work(saga, magus, plan)
    assert found == [] and work is not None
    lines = {line.label: line.amount for line in work.lab_total.lines}
    assert lines["Elder rune doubles Rego"] == 8
    wand.components = [DeviceComponent("an alder wand", "wood", "small")]
    _, work = lab_seasons.work(saga, magus, plan)
    assert work is not None
    assert "Elder rune on alder wood" in [line.label for line in work.lab_total.lines]


def test_elder_runes_replace_the_vis_limit_even_when_lower():
    # The limit "becomes" Magic Theory x Philosophiae (HoH:MC pp. 126, 128).
    _, magus, _ = _enchanter(verditius.ELDER_RUNES)
    magus.abilities = [a for a in magus.abilities if a.name != "Philosophiae"]
    magus.abilities.append(Ability("Philosophiae", xp=ability_xp(1)))
    assert verditius.enchanting_vis_limit(magus) == 5  # 5 x 1, not 10
    assert "Philosophiae" in verditius.vis_limit_text(magus)


def test_what_the_runes_may_be():
    _, magus, wand = _enchanter(verditius.ELDER_RUNES)
    assert verditius.elder_rune_problems(magus, wand) == []
    wand.elder_runes = ["Rego", "Creo", "Terram"]
    found = verditius.elder_rune_problems(magus, wand)
    assert "No elder rune is adapted to Terram." in found
    assert any("at most two" in f for f in found)


def test_the_device_form_keeps_the_runes_and_the_item_kind():
    saga, _, wand = _enchanter()
    copy = device_form.device_from_values(
        saga,
        wand,
        {
            "elder_rune_technique": "Perdo",
            "elder_rune_form": "Corpus",
            "verditius_item": enchantment.ATTUNED,
        },
    )
    assert copy.elder_runes == ["Perdo", "Corpus"]
    assert copy.verditius_item == enchantment.ATTUNED


# -- Item Attunement and Automata (pp. 128-135) -------------------------------------


def test_an_attuned_item_s_capacity_and_hubris():
    saga, magus, wand = _enchanter(verditius.ITEM_ATTUNEMENT, verditius.HUBRIS_FLAW)
    magus.personality_traits = [ScoredTrait("Hubris", 3)]
    magus.abilities.append(Ability("Craft: Smith", xp=ability_xp(5)))
    wand.capacity_override, wand.elder_runes = None, []
    wand.verditius_item, wand.maker_id = enchantment.ATTUNED, "m"
    wand.verditius_craft = "Craft: Smith"
    # Highest Technique 8 + highest Form 19 + Philosophiae 4 + Craft 5.
    assert enchantment.capacity(saga, wand) == 36
    effect = wand.effects[0]
    line = verditius.hubris_item_line(magus, wand)
    assert line is not None and line.amount == 3
    assert verditius.item_problems(magus, wand, effect) == []
    magus.virtues_flaws = [
        vf for vf in magus.virtues_flaws if vf.vf_id != "vf_item_attunement"
    ]
    assert verditius.item_problems(magus, wand) == [
        "Hephaestion hasn't been Initiated into Item Attunement."
    ]
    assert verditius.sever_ease(36) == 46
    assert verditius.covet_device(5, 3) == 1
    assert verditius.covet_device(100, 3) == 3


def test_an_automaton():
    # The tin magpie (p. 132): Might 10 - 4 + 5 = 11.
    might = verditius.automaton_might(-4, 5)
    assert might == 11
    magus = _magus(verditius.AUTOMATA)
    magus.abilities.append(Ability(verditius.CRAFT_AUTOMATA, xp=ability_xp(2)))
    # Int 3 + Craft Automata 2 + Philosophiae 4 + 2 failed seasons.
    assert int(verditius.construct_total(magus, failed_seasons=2).total) == 11
    assert verditius.construct_cost(might, 10, failed_seasons=2) == 130
    assert verditius.tie_the_threads_level(might) == 26
    assert verditius.ability_power_level(3) == 35
    assert verditius.maintenance(11, 12) == 11
    assert verditius.maintenance(11, 4) == 10
    assert verditius.maintenance(11, 0, botches=2) == 1
    assert verditius.wear_penalty(11, 7) == -2
    assert verditius.spot_repair_ease(11) == 9
    device = EnchantedDevice("bird", "Magpie", INVESTED, verditius_item="automaton")
    focus = InstilledEffect(
        "hold", "Hold", "Rego", "Terram", maintains_concentration=True
    )
    assert verditius.item_problems(magus, device, focus) == [
        "An automaton can't maintain concentration: its powers can't have that "
        "modification."
    ]


# -- Items of Quality, Reforging, binding and Curses -------------------------------


def test_items_of_quality_and_reforging():
    magus = _magus()
    assert verditius.item_of_quality_bonus(magus, 7) == 4  # Philosophiae 4
    assert verditius.item_of_quality_bonus(magus, 3) == 3
    assert verditius.repair_ease(4) == 13
    assert verditius.reforge_result(23, [20]) == verditius.REFORGED
    assert verditius.reforge_result(15, [10, 20]) == verditius.UNCHANGED
    assert verditius.reforge_result(5, [10, 20]) == verditius.UNCHANGED
    assert verditius.reforge_result(5, [20]) == verditius.FLAWED
    assert verditius.reforge_result(50, [20], botched=True) == verditius.DESTROYED
    # The wand of the example: 4 pawns of Vim, 4 more held, +20 levels.
    assert verditius.reforged(4) == (4, 4, 20)
    assert verditius.reforge_opened_target(6) == 30
    assert verditius.smelting_limit(magus) == 10
    assert verditius.smelted(magus, 12) == 10
    assert verditius.smelted(magus, 5) == 4
    magus.virtues_flaws.append(VirtueFlawInstance(verditius.ELDER_RUNES))
    assert verditius.smelting_limit(magus) == 20


def test_binding_magical_creatures_and_curses():
    magus = _magus(verditius.BIND_MAGICAL_CREATURES)
    magus.personality_traits = [ScoredTrait("Hubris", 2)]
    saga = _saga(magus)
    total = verditius.binding_total(saga, magus, saga.laboratories[0])
    assert ("Hubris", 2) in [(line.label, line.amount) for line in total.lines]
    assert verditius.drained_pawns(25, 15) == 10
    assert verditius.drained_pawns(40, 15) == 15
    assert verditius.bind_power(29, 15) == []
    assert verditius.bind_power(40, 15, penetration=5) == [
        "The power is bound.",
        "It needs words or gestures, not both.",
        "It has Penetration 5.",
    ]
    assert verditius.bind_power_vis(15) == 8
    assert verditius.curse_level("Minor") == 25
    assert verditius.curse_level("Major", magnitudes=1, trigger="counted") == 61
    assert verditius.curse_duration("Major", 5) == "5 years"

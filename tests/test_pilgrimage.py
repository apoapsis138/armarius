"""The lacuna and the pilgrim: searching a city for its lacunae and casting
from one (HoH:S pp. 57-60; DE pp. 99, 218), and a pilgrimage's
Oppositional Elements and aim (The Church pp. 15-19)."""

import random
from dataclasses import replace

from ars_magica_manager import catalog, seasons
from ars_magica_manager.actions import NodeKind, available
from ars_magica_manager.commands import Form, Refuse
from ars_magica_manager.forms import lacuna as lacuna_forms
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.forms import pilgrimage as pilgrimage_forms
from ars_magica_manager.models import (
    Ability,
    ArtScore,
    Character,
    Characteristics,
    KnownSpell,
    Progress,
    Saga,
    ScoredTrait,
    SeasonPlan,
    Spell,
    VirtueFlawInstance,
    XpAllocation,
)
from ars_magica_manager.rules import lacunae
from ars_magica_manager.rules import pilgrimage as pil
from ars_magica_manager.rules import supplement_work as sw
from ars_magica_manager.rules.xp import ability_xp, art_xp

PARIS = "Area Lore: Paris"


def _magus() -> Character:
    magus = Character(id="m", name="Carmine", type="magus")
    magus.characteristics = Characteristics(intelligence=2, stamina=1)
    magus.abilities = [
        Ability(PARIS, xp=ability_xp(4)),
        Ability("Area Lore: Rome", xp=ability_xp(1)),
        Ability("Artes Liberales", xp=ability_xp(2)),
        Ability("Philosophiae", xp=ability_xp(1)),
    ]
    magus.arts = {"creo": ArtScore(xp=art_xp(10)), "ignem": ArtScore(xp=art_xp(6))}
    return magus


def _saga(*characters: Character) -> Saga:
    return Saga(id="s", name="S", characters=list(characters))


def _search(die: int | None, subject: str = PARIS) -> SeasonPlan:
    return SeasonPlan(
        "m",
        1220,
        "Spring",
        "search_lacuna",
        [XpAllocation(f"ability:{subject}")],
        die=die,
    )


# -- the lacuna search (HoH:S p. 57) --


def test_a_search_rolls_intelligence_and_the_chosen_area_lore_against_9():
    magus = _magus()
    saga = _saga(magus)
    found = sw.work(saga, magus, _search(3), None)
    # Int 2 + Area Lore: Paris 4 + 3 = 9.
    assert found.notes == [
        "Int + Area Lore + die = 9 against 9: the obvious lacunae are found. He "
        "knows 12 small lacunae there (3 per level of Area Lore: Paris)."
    ]
    assert found.progress == [("lacunae", "Lacunae of Paris", 9, 9)]
    short = sw.work(saga, magus, _search(2, "Area Lore: Rome"), None)
    assert short.notes == ["Int + Area Lore + die = 5 against 9: none found."]
    assert short.progress == []


def test_a_found_city_is_kept_and_later_seasons_are_practice():
    magus = _magus()
    saga = _saga(magus)
    seasons.set_plan(saga, _search(5))
    seasons.apply(saga, seasons.resolve(saga, random.Random(1)))
    assert lacunae.found_record(magus, "Paris") is not None
    assert lacunae.found_areas(magus) == ["Lacunae of Paris"]
    assert any(e.name == "Finished: Lacunae of Paris" for e in magus.diary)
    again = sw.work(saga, magus, _search(0), None)
    assert again.progress == []
    assert "Area Lore practice" in again.notes[0]
    assert "specialty may become lacunae" in again.notes[0]


def test_with_no_area_lore_the_search_finds_no_city_to_record():
    magus = _magus()
    magus.abilities = []
    found = sw.work(_saga(magus), magus, _search(9, "Latin"), None)
    assert found.notes[0].endswith("the obvious lacunae are found.")
    assert found.progress == []


def test_lacunae_known_and_their_limitations():
    assert lacunae.known_count(4) == 12
    assert lacunae.area_of("Area Lore: Paris") == "Paris"
    assert lacunae.needs_limitation(True, "search")
    assert not lacunae.needs_limitation(True, "covenant")
    assert not lacunae.needs_limitation(False, "search")


# -- casting from a lacuna (HoH:S pp. 57-58) --


def test_a_lacuna_spares_a_spell_the_dominion_unless_its_target_is_in_it():
    assert lacunae.casting_aura(3, in_lacuna=False) == ("Divine", 3)
    assert lacunae.casting_aura(3, in_lacuna=True) == ("Magic", 0)
    assert lacunae.casting_aura(
        3, in_lacuna=True, lacuna_realm="Faerie", lacuna_aura=2
    ) == ("Faerie", 2)
    assert lacunae.casting_aura(3, in_lacuna=True, target_in_dominion=True) == (
        "Divine",
        3,
    )


def test_ceremony_time_by_prepared_space_and_choreography():
    assert lacunae.ceremony_minutes(2, "none") == 30
    assert lacunae.ceremony_minutes(2, "temporary") == 24
    assert lacunae.ceremony_minutes(2, "laboratory") == 6
    assert lacunae.ceremony_minutes(2, "ceremonial_room") == 2
    # Mystical Choreography: 5 a magnitude, 1 in any prepared space (DE p. 99).
    assert lacunae.ceremony_minutes(2, "none", choreography=True) == 10
    assert lacunae.ceremony_minutes(2, "temporary", choreography=True) == 2


def _caster() -> tuple[Saga, Character]:
    magus = _magus()
    saga = _saga(magus)
    saga.spells.append(
        Spell(id="sp", name="Pilum of Fire", technique="Creo", form="Ignem", level=20)
    )
    magus.spells_known = [KnownSpell("sp")]
    return saga, magus


def _values(**kw):
    values = {
        "spell": "sp",
        "city_aura": 3,
        "in_lacuna": True,
        "realm": "",
        "lacuna_aura": 0,
        "target_in_dominion": False,
        "words": "Firm",
        "gestures": "Bold",
    }
    values.update(kw)
    return values


def test_the_casting_form_compares_the_lacuna_with_the_dominion():
    saga, magus = _caster()
    form = lacuna_forms.lacuna_form(saga, magus, random.Random(2))
    assert isinstance(form, Form)
    said = lacuna_forms.lines(saga, magus, _values())
    # Creo 10 + Ignem 6 + Stamina 1 = 17; in the Dominion 3, -9 = 8.
    assert said[0] == "Casting Score 17 in no aura."
    assert said[1] == "Outside the lacuna, in the Dominion: 8."
    assert "the die must reach 3" in said[2]
    into = lacuna_forms.lines(saga, magus, _values(target_in_dominion=True))
    assert into[0] == "Casting Score 8 in the Dominion 3."
    rolled = form.apply(_values())
    assert "against 20" in rolled[0] or "botch" in rolled[0]
    assert magus.diary == []


def test_a_spontaneous_ceremony_in_a_lacuna():
    saga, magus = _caster()
    values = _values(
        spell=lacuna_forms.SPONTANEOUS,
        technique="Creo",
        form="Ignem",
        level=10,
        ceremonial=True,
        props="2",
        space="designed",
    )
    said = lacuna_forms.lines(saga, magus, values)
    # 17 + Artes Liberales 2 + Philosophiae 1 + props 2 = 22.
    assert said[0] == "Casting Score 22 in no aura."
    assert any(line.startswith("The ceremony: 12 minutes") for line in said)


def test_only_a_magus_casts():
    saga = _saga(Character(id="c", name="Hugo", type="companion"))
    assert isinstance(lacuna_forms.lacuna_form(saga, saga.characters[0]), Refuse)


# -- pilgrimage (The Church pp. 15-19) --


def _pilgrim(target: int = pil.MAJOR, points: int = 0) -> Character:
    pilgrim = Character(id="p", name="Boniface", type="companion")
    pilgrim.progress = [Progress("pilgrimage", "Jerusalem", target, points)]
    return pilgrim


def test_elements_add_their_values_and_reach_the_target():
    pilgrim = _pilgrim(points=9)
    record = pil.find(pilgrim, "Jerusalem")
    assert pil.overcome(record, pilgrim, "bandits")[0] == 6
    assert pil.overcome(record, pilgrim, "supernatural")[0] == 9
    gained, said = pil.overcome(record, pilgrim, "demon")
    assert gained == 12 and record.points == 36 and record.done
    assert said.endswith("The Target Level is reached.")


def test_travel_counts_once_and_only_the_higher():
    pilgrim = _pilgrim()
    record = pil.find(pilgrim, "Jerusalem")
    assert pil.overcome(record, pilgrim, pil.CHRISTIAN_ABROAD)[0] == 3
    assert pil.overcome(record, pilgrim, pil.HEATHEN_LANDS)[0] == 3
    assert pil.overcome(record, pilgrim, pil.HEATHEN_LANDS)[0] == 0
    assert pil.overcome(record, pilgrim, pil.CHRISTIAN_ABROAD)[0] == 0
    assert record.points == 6 and pil.travel_counted(pilgrim, "Jerusalem") == 6


def test_a_failed_element_blocks_the_aim_until_remedied():
    pilgrim = _pilgrim(target=pil.MINOR, points=15)
    record = pil.find(pilgrim, "Jerusalem")
    assert "1 outstanding" in pil.failed(pilgrim, record)
    pil.overcome(record, pilgrim, "temptation")
    assert record.done and pil.claim_problem(pilgrim, record) is None
    pil.failed(pilgrim, record)
    assert "not remedied" in (pil.claim_problem(pilgrim, record) or "")
    # The story's record is finished, so This Season leaves it out.
    assert pil.story_of(pilgrim, "Jerusalem").done


def test_aims_by_target_level():
    assert [key for _l, key in pil.aims_for(18)] == [
        "gain_virtue",
        "lose_vf",
        "lose_trait",
        "penance",
    ]
    assert "miracle" in {key for _l, key in pil.aims_for(30)}
    assert "lose_trait" not in {key for _l, key in pil.aims_for(30)}


def test_what_a_pilgrimage_may_grant_and_take_away():
    entries = catalog.load_virtue_flaw_catalog()
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    pilgrim = Character(id="p", name="Boniface", type="magus")
    gained = pil.gainable(pilgrim, entries, pil.MINOR)
    assert gained and all(
        d.tier == "Minor" and d.category in ("General", "Supernatural") for d in gained
    )
    assert "vf_educated" not in {d.id for d in gained}
    hermetic = next(
        d for d in entries if d.category == "Hermetic" and d.tier == "Major"
    )
    general = next(
        d
        for d in entries
        if d.category == "General" and d.tier == "Major" and d.type == "Flaw"
    )
    pilgrim.virtues_flaws = [
        VirtueFlawInstance(hermetic.id),
        VirtueFlawInstance(general.id),
    ]
    assert pil.losable(pilgrim, by_id, pil.MAJOR) == [VirtueFlawInstance(general.id)]


def test_background_virtues_are_neither_gained_nor_lost():
    entries = catalog.load_virtue_flaw_catalog()
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    pilgrim = Character(id="p", name="Boniface", type="companion")
    gained = {d.id for d in pil.gainable(pilgrim, entries, pil.MINOR)}
    assert not gained & {"vf_privileged_upbringing", "vf_warrior", "vf_arcane_lore"}
    pilgrim.virtues_flaws = [VirtueFlawInstance("vf_warrior")]
    assert pil.losable(pilgrim, by_id, pil.MINOR) == []


def test_only_negative_or_sinful_traits_may_be_removed():
    pilgrim = Character(id="p", name="Boniface", type="companion")
    pilgrim.personality_traits = [
        ScoredTrait("Cruel", 3),
        ScoredTrait("Generous", 2),
        ScoredTrait("Likes figs", 1),
        ScoredTrait("Brave", -2),
        ScoredTrait("Humble", -1),
    ]
    names = [t.name for t in pil.removable_traits(pilgrim)]
    assert names == ["Cruel", "Brave", "Humble"]


def test_a_divine_ability_gained_starts_at_one():
    pilgrim = _pilgrim(target=pil.MINOR, points=18)
    pilgrim.progress[0].done = True
    saga = _saga(pilgrim)
    said = pilgrimage_forms.apply_pilgrimage(
        saga,
        pilgrim,
        {
            "what": "claim",
            "pilgrimage": "Jerusalem",
            "aim": "gain_virtue",
            "virtue_18": "vf_sense_holiness_and_unholiness",
        },
    )
    ability = next(
        a for a in pilgrim.abilities if a.name == "Sense Holiness and Unholiness"
    )
    assert ability.level == 1
    assert "starts at 1" in " ".join(said)


def test_holy_magic_needs_true_faith_and_devotion_points():
    pilgrim = _pilgrim()
    assert pil.holy_magic_problem(pilgrim)
    pilgrim.virtues_flaws = [VirtueFlawInstance("vf_true_faith")]
    assert pil.holy_magic_problem(pilgrim) is None
    assert pil.devotion_points(at_shrine=True, other_sites=1, relics=7) == 20
    assert pil.devotion_points(at_shrine=False, other_sites=2) == 0


def test_the_form_begins_records_and_claims_a_pilgrimage():
    pilgrim = Character(id="p", name="Siderius", type="grog")
    pilgrim.personality_traits = [ScoredTrait("Lazy", 2)]
    saga = _saga(pilgrim)
    form = pilgrimage_forms.pilgrimage_form(saga, pilgrim)
    assert isinstance(form, Form)
    assert form.validate({"what": "begin", "name": ""}) == "Name the pilgrimage."
    form.apply({"what": "begin", "name": "Canterbury", "target": "18"})
    assert pil.find(pilgrim, "Canterbury").target == 18
    assert pilgrim.diary[-1].name == "Pilgrimage begun: Canterbury"
    form = pilgrimage_forms.pilgrimage_form(saga, pilgrim)
    claim = {"what": "claim", "pilgrimage": "Canterbury", "aim": "lose_trait"}
    assert "must reach the Target Level" in (form.validate(claim) or "")
    for element in ("bandits", "storm", "trial_6"):
        form.apply({"what": "overcome", "pilgrimage": "Canterbury", "element": element})
    assert pil.find(pilgrim, "Canterbury").done
    assert form.validate(claim) == "Choose the Personality Trait removed."
    assert form.validate({**claim, "aim": "miracle"})
    form.apply({**claim, "trait": "Lazy"})
    assert pilgrimage_forms.pil.find(pilgrim, "Canterbury") is None
    assert pilgrim.personality_traits == []
    assert pilgrim.diary[-1].name == "Pilgrimage's aim: Canterbury"


def test_a_claimed_virtue_is_added():
    pilgrim = _pilgrim(target=pil.MINOR, points=18)
    pilgrim.progress[0].done = True
    saga = _saga(pilgrim)
    virtue = pil.gainable(pilgrim, catalog.load_virtue_flaw_catalog(), pil.MINOR)[0]
    pilgrimage_forms.apply_pilgrimage(
        saga,
        pilgrim,
        {
            "what": "claim",
            "pilgrimage": "Jerusalem",
            "aim": "gain_virtue",
            "virtue_18": virtue.id,
        },
    )
    assert VirtueFlawInstance(virtue.id) in pilgrim.virtues_flaws


def test_more_offers_them_where_they_belong():
    saga, _magus_on_show = _caster()
    page = menu_forms.page_for(saga, NodeKind.CHARACTER, character_id="m")
    assert available("cast_in_lacuna", replace(page, section="section-known-spells"))
    assert not available("cast_in_lacuna", replace(page, section="section-char-season"))
    assert available("pilgrimage", replace(page, section="section-char-season"))
    assert "pilgrimage" in {i.action for i in menu_forms.placed(page, "This Season")}
    saga.books_in_play = ["DE"]
    assert not available("pilgrimage", replace(page, section="section-char-season"))
    assert not available(
        "cast_in_lacuna", replace(page, section="section-known-spells")
    )

"""The realms' supplement leftovers: the Divine (relics, faith won in play,
Holy Magic, Divine regiones), the Infernal (regiones, vis, Chthonic Magic,
demons, Might and realm, infernalists) and Faerie and Magic (faerie auras,
Faerie Blood, charms, Hermetic rites, spirits, jinn, the Ríastradh)."""

from __future__ import annotations

import random

from ars_magica_manager import churches, faith, places, vis
from ars_magica_manager.models import (
    Ability,
    ArtScore,
    Book,
    Character,
    Characteristics,
    Covenant,
    Creature,
    CreaturePower,
    Laboratory,
    Neighbour,
    Possession,
    Saga,
    ScoredTrait,
    SeasonPlan,
    SeasonRecord,
    SeasonRecordLine,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import (
    activities,
    aura_change,
    battle_transformation,
    casting,
    creation_virtues,
    faerie_blood,
    infernal_build,
    infernalists,
    jinn_build,
    lab,
    lab_seasons,
    sites,
    spirit_build,
    study,
)
from ars_magica_manager.rules import hybrid_magic as hybrid
from ars_magica_manager.rules.xp import ability_xp, art_xp


def _magus(*abilities: tuple[str, int], vf_ids: tuple[str, ...] = ()) -> Character:
    return Character(
        id="m",
        name="Magus",
        type="magus",
        covenant_id="c",
        characteristics=Characteristics(intelligence=3, stamina=2, quickness=1),
        arts={"creo": ArtScore(xp=art_xp(10)), "ignem": ArtScore(xp=art_xp(6))},
        abilities=[
            Ability("Magic Theory", xp=ability_xp(5)),
            *(Ability(name, xp=ability_xp(score)) for name, score in abilities),
        ],
        virtues_flaws=[VirtueFlawInstance(v) for v in vf_ids],
    )


def _saga(magus: Character) -> tuple[Saga, Laboratory]:
    laboratory = Laboratory(id="l", covenant_id="c", name="Lab", owner_id="m")
    covenant = Covenant(id="c", saga_id="s", name="C", aura=3, aura_realm="Magic")
    saga = Saga(
        id="s",
        name="S",
        covenants=[covenant],
        characters=[magus],
        laboratories=[laboratory],
    )
    return saga, laboratory


# -- the Divine --


def _church(faith_score: int) -> Neighbour:
    church = Neighbour(id="ch", name="St. Ursula", kind="church")
    church.details = {
        "church": "Parish church",
        "relics": [{"name": "A finger", "faith": faith_score}],
    }
    return church


def test_a_relic_raises_the_dominion_with_or_without_the_growth_option():
    # RoP: The Divine p. 12: +1 a point of Faith score above 5.
    saga = Saga(id="s", name="S")
    assert churches.aura(saga, _church(7)) == 4 + 2
    assert churches.aura(saga, _church(5)) == 4
    saga.rule_options[churches.GROWTH] = True
    assert churches.aura(saga, _church(7)) == 4 + 2
    saga.books_in_play = ["TC"]  # the rule is RoP: The Divine's
    assert churches.aura(saga, _church(7)) == 4
    labels = [f.label for f in churches.relic_fields(saga, _church(1), None)]
    assert "Faith score" in labels


def test_the_mythic_companion_warning_is_for_creation_only():
    believer = Character(
        id="b",
        name="Brother",
        type="companion",
        virtues_flaws=[VirtueFlawInstance(faith.TRUE_FAITH_ID)],
    )
    believer.in_creation = True
    assert faith.faith_warnings(believer, 2, "companion")
    believer.in_creation = False
    assert faith.faith_warnings(believer, 2, "companion") == []


def test_faith_won_in_play_brings_the_virtue_and_a_diary_entry():
    # RoP: The Divine p. 58.
    saga = Saga(id="s", name="S")
    pilgrim = Character(id="p", name="Pilgrim", type="grog")
    line = faith.gain_in_play(saga, pilgrim, 1, 2)
    assert "True Faith Score 0 to 1" in line
    assert faith.has_true_faith(pilgrim)
    assert pilgrim.diary[-1].name == "Faith won in play"
    assert faith.gain_in_play(saga, pilgrim, 0, 0) == ""


def test_holy_magic_halves_a_lab_total_from_another_s_text():
    # RoP: The Divine p. 67.
    magus = _magus(("Holy Magic", 5), vf_ids=("vf_holy_magic",))
    saga, laboratory = _saga(magus)
    own = lab.lab_total(saga, magus, "Creo", "Ignem", laboratory, from_lab_text=True)
    other = lab.lab_total(
        saga,
        magus,
        "Creo",
        "Ignem",
        laboratory,
        from_lab_text=True,
        others_text=True,
    )
    assert other.total == own.total // 2
    assert any("Holy Magic" in line.label for line in other.lines)
    holy = lab.lab_total(
        saga,
        magus,
        "Creo",
        "Ignem",
        laboratory,
        from_lab_text=True,
        others_text=True,
        hermetic_text=False,
    )
    assert holy.total == own.total


def test_holy_magic_halves_reading_a_hermetic_book_on_an_art():
    # RoP: The Divine p. 67: "Hermetic study totals halved".
    magus = _magus(("Holy Magic", 5), vf_ids=("vf_holy_magic",))
    saga, _ = _saga(magus)
    brother = _magus(("Holy Magic", 3), vf_ids=("vf_holy_magic",))
    brother.id = "brother"
    saga.characters.append(brother)
    summa = Book(
        id="b", name="Of Fire", type="Art Summa", art="ignem", level=10, quality=11
    )
    assert hybrid.hermetic_source(saga, summa)
    halved = study.reading(magus, summa, hermetic=True)
    full = study.reading(magus, summa, hermetic=False)
    assert halved is not None and full is not None
    assert halved.advancement_total == full.advancement_total // 2
    summa.author_id = "brother"
    assert not hybrid.hermetic_source(saga, summa)
    summa.author_id, summa.holy = None, True
    assert not hybrid.hermetic_source(saga, summa)
    # Not learning magic: a mundane Ability is read at the full total.
    mundane = Book(
        id="m",
        name="Of Herbs",
        type="Ability Summa",
        ability="Medicine",
        level=5,
        quality=8,
    )
    assert not hybrid.halves_study(magus, mundane, True)


def test_regio_kinds_and_their_effects():
    celestial: sites.RegioLevel = {"realm": "Divine", "aura": 7, "kind": "Celestial"}
    assert sites.regio_kind(celestial) == "Celestial"
    assert sites.celestial_ease(7) == 21  # RoP: The Divine p. 14
    assert "against 21" in sites.kind_effects(celestial)
    # A kind not of its realm is ignored.
    assert sites.regio_kind({"realm": "Magic", "kind": "Celestial"}) == ""
    abyssal: sites.RegioLevel = {"realm": "Infernal", "aura": 4, "kind": "Abyssal"}
    text = sites.kind_effects(abyssal)
    assert "Holy Magic at -4" in text and "Characteristic -4" in text
    place = Neighbour(id="p", name="Vale", kind="place", realm="Infernal")
    place.details = {"aura": 3, "levels": [abyssal]}
    facts = {f.label: f.value for f in places.facts(Saga(id="s", name="S"), place)}
    assert "Level 1:" in facts["Within"]


# -- the Infernal --


def test_infernal_vis_doubles_botch_dice_or_follows_the_harsher_option():
    saga = Saga(id="s", name="S")
    assert casting.botch_dice(vis_pawns=2, infernal_vis_pawns=2, saga=saga) == 6
    saga.rule_options["harsher_infernal_vis"] = True
    # 1 + 2 pawns + 2 x 2 more; Mastery can't take them below the pawns.
    assert casting.botch_dice(vis_pawns=2, infernal_vis_pawns=2, saga=saga) == 7
    assert (
        casting.botch_dice(vis_pawns=2, infernal_vis_pawns=2, saga=saga, mastery=9) == 2
    )
    assert "+10 to the total" in casting.infernal_vis_text(saga, 2)
    magus = _magus()
    score = casting.casting_score(magus, "Creo", "Ignem", vis_pawns=3, sordida_pawns=2)
    amounts = {line.label: line.amount for line in score.lines}
    assert amounts["1 pawns of vis"] == 2
    assert amounts["2 pawns of vis, Infernal"] == 10


def test_infernal_vis_stores_are_found_for_a_casting():
    magus = _magus()
    saga, _ = _saga(magus)
    saga.covenants[0].possessions.append(
        Possession(
            id="v", kind=vis.STORE, name="Ash", art="Ignem", pawns=3, infernal=True
        )
    )
    assert [p.name for p in vis.infernal_stores(saga, magus, ("Creo", "Ignem"))] == [
        "Ash"
    ]
    assert vis.infernal_stores(saga, magus, ("Rego", "Aquam")) == []


def test_chthonic_magic_stands_in_for_magic_theory_and_ignores_infernal_vis():
    # RoP: The Infernal p. 123.
    magus = _magus(("Chthonic Magic", 8), vf_ids=("vf_chthonic_magic",))
    assert hybrid.chthonic_theory(magus) == 3
    assert hybrid.infernal_vis_limit(magus) == 8
    saga = Saga(id="s", name="S")
    assert (
        casting.botch_dice(vis_pawns=2, infernal_vis_pawns=2, saga=saga, magus=magus)
        == 3
    )
    plan = SeasonPlan("m", 1220, "Spring", lab_seasons.INVENT, chthonic=True)
    total = lab.LabTotal(total=20, lines=[])
    with_it = lab_seasons._with_options(magus, plan, "Creo", "Ignem", total)
    assert with_it.total == 23


def test_a_hermetic_rite_may_use_the_faerie_column():
    # RoP: Faerie p. 121.
    methods, powers = hybrid.methods_and_powers("Faerie")
    magus = _magus((min(methods), 4), (min(powers), 3))
    _, plain = hybrid.aura_label(magus, "Faerie", 4)
    label, ritual = hybrid.aura_label(magus, "Faerie", 4, ritual=True)
    assert plain < ritual == 4
    assert "Faerie column" in label


def _demon(**kw) -> Creature:
    values = {
        "id": "d",
        "name": "Bartholomew",
        "realm": "Infernal",
        "might": 15,
        "order": "Lord of the Tempters",
        "weakness": "Salt",
    }
    values.update(kw)
    return Creature(**values)


def test_a_demons_order_and_rank():
    # RoP: The Infernal pp. 30-31.
    demon = _demon()
    assert infernal_build.order_of(demon).name == "Tempters"
    assert infernal_build.rank_of(demon) == "Lord"
    assert infernal_build.most_might(demon) == 30
    assert infernal_build.hierarchy(demon) == 5
    found = " ".join(infernal_build.problems(demon))
    assert "Selfish +5" in found and "Coagulation" in found
    duke = _demon(order="Duke of the Accusers")
    assert "No demon of the Accusers is a Duke" in " ".join(
        infernal_build.problems(duke)
    )
    assert infernal_build.problems(_demon(order="")) == []  # a DE demon
    assert infernal_build.coagulation_cost(25) == 3
    assert infernal_build.lowest_physical(25) == -5
    assert infernal_build.hours_to_recover("Infernal", 6) == 12
    assert infernal_build.hours_to_recover("Divine", 3) is None


def test_with_infernal_might_no_virtue_of_another_realm():
    # RoP: The Infernal p. 84.
    character = Character(
        id="c",
        name="Child",
        type="companion",
        virtues_flaws=[
            VirtueFlawInstance("vf_demonic_blood"),
            VirtueFlawInstance(faith.TRUE_FAITH_ID),
        ],
    )
    checks = creation_virtues._realm_checks(character)
    assert checks[0].status == "warn" and "True Faith" in checks[0].detail
    character.virtues_flaws.pop()
    assert creation_virtues._realm_checks(character)[0].status == "pass"


def test_vituperation_and_sacrifice():
    # RoP: The Infernal p. 95.
    witch = Character(
        id="w",
        name="Witch",
        type="companion",
        characteristics=Characteristics(stamina=2),
        abilities=[Ability("Concentration", xp=ability_xp(3))],
        reputations=[ScoredTrait("Servant of Astaroth", 4, type="Infernal")],
    )
    witch.background.confidence_score = 1
    witch.aging.warping_score = 2
    assert infernalists.hierarchy(witch) == 4
    assert infernalists.avoid_total(witch) == 6
    assert infernalists.against_total(witch, 3, 2) == 2 + 3 + 4 + 2
    assert infernalists.confidence_after(witch, 3, botched=False) == (1, 3)
    assert infernalists.confidence_after(witch, 3, botched=True) == (1, 0)
    assert infernalists.SACRIFICES["an innocent human"] == 10
    # The local aura is in the total (p. 95): his home aura stands for it.
    assert "against 9 (with his home aura 3" in infernalists.vituperation_text(witch, 3)


# -- Faerie and Magic --


def _faerie(fid: str, might: int) -> Creature:
    return Creature(id=fid, name=fid.title(), realm="Faerie", might=might)


def test_a_faerie_aura_follows_its_glamour():
    # RoP: Faerie pp. 14-16.
    saga = Saga(
        id="s", name="S", creatures=[_faerie("queen", 25), _faerie("rival", 35)]
    )
    place = Neighbour(id="g", name="Glade", kind="place", realm="Faerie")
    place.details = {"aura": 2, "presiding": "queen"}
    saga.neighbours.append(place)
    assert aura_change.glamour_aura(saga, place) == (5, "Queen")
    place.details["contesting"] = "rival"
    assert aura_change.glamour_aura(saga, place)[0] == 9  # 2 + 35 / 5, at most 9
    del place.details["contesting"]
    saga.rule_options[aura_change.OPTION] = True
    found = aura_change.year(saga, place, saga.current_year, random.Random(1))
    assert found is not None and (["aura"], 5) in found.sets


def test_vis_taken_from_a_faerie_aura_lowers_it():
    magus = _magus()
    saga, _ = _saga(magus)
    saga.creatures.append(_faerie("queen", 25))
    place = Neighbour(id="g", name="Glade", kind="place", realm="Faerie")
    place.details = {"aura": 5, "presiding": "queen"}
    saga.neighbours.append(place)
    saga.covenants[0].place_id = place.id
    saga.season_records.append(
        SeasonRecord(
            saga.current_year,
            "Spring",
            lines=[
                SeasonRecordLine(
                    character_id="m",
                    name="Magus",
                    activity=activities.ACTIVITIES[lab_seasons.EXTRACT].label,
                    result="done",
                )
            ],
        )
    )
    found = aura_change.FaerieAura().year(
        saga, place, saga.current_year, random.Random(1)
    )
    assert found is not None
    assert (["glamour_lost"], 1) in found.sets and (["aura"], 4) in found.sets
    place.details["vis_bargain"] = True
    assert (
        aura_change.FaerieAura().year(saga, place, saga.current_year, random.Random(1))
        is None
    )


def test_faerie_blood_varieties_and_legacy():
    # RoP: Faerie pp. 106-110; The Cradle and the Crescent p. 78.
    blood = VirtueFlawInstance("vf_faerie_blood", params={"blood": "Selkie"})
    assert "Deprivation" in faerie_blood.blood_text([blood], blood)
    legacy = [blood, VirtueFlawInstance("vf_faerie_legacy")]
    assert "each minute" in faerie_blood.blood_text(legacy, blood)
    jann = VirtueFlawInstance("vf_faerie_blood", params={"blood": "Jann"})
    assert "The Cradle and the Crescent p. 78" in faerie_blood.blood_text([jann], jann)
    unknown = VirtueFlawInstance("vf_faerie_blood", params={"blood": "Bee King"})
    assert faerie_blood.blood_text([unknown], unknown) == ""


def test_spirits_and_ghosts():
    # RoP: Magic pp. 100-117.
    ghost = Creature(
        id="g",
        name="Sir Giles",
        realm="Magic",
        might=16,
        order="ghost",
        characteristics=Characteristics(quickness=2),
        virtues_flaws=[VirtueFlawInstance(spirit_build.MAGIC_SPIRIT)],
        powers=[CreaturePower("Control Human", might_cost=2, init=0)],
    )
    found = " ".join(spirit_build.problems(ghost))
    assert "Magical Air" in found and "Social Status" in found
    assert "Control Human: the book gives cost 2, Init +2" in found
    assert spirit_build.spirit_vis(4) == 0 and spirit_build.spirit_vis(16) == 4
    assert spirit_build.presence_area(20) == "a Structure"
    assert spirit_build.presence_vis(45) == 4


def test_a_jinni_by_the_book():
    # The Cradle and the Crescent pp. 62-63.
    jinni = Creature(
        id="j",
        name="Jumayl",
        realm="Divine",
        virtues_flaws=[VirtueFlawInstance(jinn_build.JINNI)],
    )
    found = " ".join(jinn_build.problems(jinni))
    assert "no Divine jinn" in found and "Arabic" in found
    jinni.realm = "Faerie"
    jinni.abilities = [Ability("Arabic", xp=5), Ability("Theology: Islam", xp=5)]
    jinni.virtues_flaws.append(VirtueFlawInstance("vf_skinchanger"))
    jinni.virtues_flaws.append(VirtueFlawInstance("vf_humanoid_faerie"))
    assert jinn_build.problems(jinni) == []


def test_the_riastradh_needs_fury_or_wrath():
    # The Contested Isle p. 120.
    hero = Character(
        id="h",
        name="Setanta",
        type="companion",
        virtues_flaws=[VirtueFlawInstance(battle_transformation.RIASTRADH)],
    )
    assert creation_virtues._requirement_checks(hero)[0].status == "warn"
    hero.virtues_flaws.append(VirtueFlawInstance("vf_fury"))
    assert creation_virtues._requirement_checks(hero) == []
    assert battle_transformation.resist_ease(3, rounds=2) == 11
    assert battle_transformation.selections(2) == 5
    totals = battle_transformation.form_totals(
        ["Huge", "Improved Soak", "Reduced Defense"]
    )
    assert totals["size"] == 2 and totals["soak"] == 3 and totals["defense"] == -3

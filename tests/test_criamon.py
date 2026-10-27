"""House Criamon's paths, stations and stigmata (Houses of Hermes: Mystery
Cults pp. 50-51, 58-73; Errata p. 55; DE pp. 235-236, 387-389)."""

from __future__ import annotations

import pytest

from ars_magica_manager import artwork, catalog
from ars_magica_manager.forms import criamon as cf
from ars_magica_manager.models import (
    Ability,
    Character,
    Characteristics,
    Enigma,
    Ordeal,
    Saga,
    SeasonPlan,
    Stigma,
    VirtueFlawInstance,
)
from ars_magica_manager.models.criamon import GHOST_GUIDE, HOUSE_GUIDE
from ars_magica_manager.rules import criamon as cr
from ars_magica_manager.rules import supplement_work as sw
from ars_magica_manager.rules import tradition_seasons as ts
from ars_magica_manager.rules.xp import ability_xp
from ars_magica_manager.seasons.lab_apply import apply_supplement
from ars_magica_manager.seasons.plans import plan_for

LORE = cr.CULT_LORE
SEEMING = cr.PATHS["seeming"]


def _magus(
    id_: str, name: str, *vf_ids: str, presence: int = 0, lore: int = 0
) -> Character:
    magus = Character(id=id_, name=name, type="magus")
    magus.hermetic.house = cr.HOUSE
    magus.characteristics = Characteristics(presence=presence)
    magus.virtues_flaws = [VirtueFlawInstance(v) for v in (cr.THE_ENIGMA, *vf_ids)]
    if lore:
        magus.abilities.append(Ability(LORE, xp=ability_xp(lore)))
    magus.abilities.append(Ability(cr.WISDOM, xp=ability_xp(5)))
    return magus


def _saga() -> Saga:
    """Kyrillos, two stations along the Path of Seeming (Lore 3, a Minor
    Ordeal behind him); Theodora, his guide (Presence +1, Lore 5)."""
    kyrillos = _magus(
        "k",
        "Kyrillos",
        "vf_station_of_differentiation_of_seeming",
        "vf_station_of_true_sight",
        "vf_disfigured",
        "vf_vow",
        lore=3,
    )
    kyrillos.ordeals = [Ordeal("Minor")]
    theodora = _magus("t", "Theodora", presence=1, lore=5)
    return Saga(id="s", name="S", characters=[kyrillos, theodora])


def _who(saga: Saga, id_: str) -> Character:
    found = saga.character(id_)
    assert found is not None
    return found


def _plan(who: str, place: int, path: cr.Path = SEEMING, **kw: object) -> SeasonPlan:
    plan = SeasonPlan(who, 1220, "Winter", "undergo_initiation", [])
    plan.hedge_script = cr.script_key(path, place)
    plan.effect_id = path.stations[place - 1].virtue_id
    for name, value in kw.items():
        setattr(plan, name, value)
    return plan


# -- the paths as data ------------------------------------------------------------


def test_every_station_virtue_is_in_the_catalog_and_each_script_too():
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    tradition = catalog.load_tradition_catalog_by_id()[cr.CULT_TRADITION]
    assert tradition.initiation is not None
    names = {s.name: s for s in tradition.initiation.scripts}
    missing = []
    for path in cr.PATHS.values():
        for place, station in enumerate(path.stations, start=1):
            entry = by_id.get(station.virtue_id)
            if entry is None or entry.tier != "Major":
                missing.append(station.virtue_id)
            for vf in station.flaw_ids:
                if vf not in by_id:
                    missing.append(vf)
            script = names.get(cr.script_name(path, place))
            if script is None or script.bonus != station.bonus:
                missing.append(cr.script_name(path, place))
            elif dict(script.requires) != {LORE: place + 1}:
                missing.append(f"{script.name}: Lore")
    assert missing == []
    assert len(cr.STATION_OF) == 20
    assert cr.MIRROR.stations == ()


@pytest.mark.parametrize(
    ("path", "bonuses", "targets"),
    [
        # The printed Script bonuses and Targets (pp. 61, 64, 67, 71), the
        # Path of Strife's fourth Target 18 by the Errata p. 55.
        ("body", (15, 6, 9, 9, 12), (21, 12, 15, 15, 17)),
        ("seeming", (15, 12, 12, 12, 12), (21, 18, 18, 15, 17)),
        ("strife", (15, 6, 9, 15, 12), (21, 12, 15, 18, 15)),
        ("walking_backwards", (15, 6, 9, 12, 9), (21, 12, 15, 18, 15)),
    ],
)
def test_the_printed_scripts(
    path: str, bonuses: tuple[int, ...], targets: tuple[int, ...]
):
    stations = cr.PATHS[path].stations
    assert tuple(s.bonus for s in stations) == bonuses
    assert tuple(s.printed_target for s in stations) == targets


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        # Each printed Target is 21 less the best reduction of the Ordeals
        # the stations before it bring (DE p. 388's 3/2/1, 6/4/2, 9/6/3).
        ("body", (21, 12, 15, 15, 17)),
        ("seeming", (21, 18, 18, 15, 17)),
        ("strife", (21, 12, 15, 18, 15)),
        ("walking_backwards", (21, 12, 15, 18, 15)),
    ],
)
def test_the_ordeal_sizes_give_the_printed_targets(
    path: str, expected: tuple[int, ...]
):
    reductions = {"Minor": (3, 2, 1), "Medium": (6, 4, 2), "Major": (9, 6, 3)}
    ordeals: list[list[object]] = []
    found = []
    for station in cr.PATHS[path].stations:
        best = max(
            (reductions[size][since] for size, since in ordeals if since < 3),  # type: ignore[index]
            default=0,
        )
        found.append(cr.target(best))
        for ordeal in ordeals:
            ordeal[1] += 1  # type: ignore[operator]
        if station.printed_reduction is not None:
            # As printed (p. 71), not worked out from the Ordeals' sizes.
            found[-1] = cr.target(station.printed_reduction[1])
        if station.ordeal:
            ordeals.append([station.ordeal, 0])
    assert tuple(found) == expected


def test_the_lore_a_station_needs_and_the_order():
    assert [cr.lore_needed(n) for n in range(1, 6)] == [2, 3, 4, 5, 6]
    saga = _saga()
    kyrillos = _who(saga, "k")
    assert cr.path_of(kyrillos) is SEEMING
    assert cr.station_reached(kyrillos, SEEMING) == 2
    nxt = cr.next_station(kyrillos, SEEMING)
    assert nxt is not None and nxt[0] == 3
    assert nxt[1].name == "Vivid Memories from Objects"


def test_the_path_named_wins_and_other_stations_are_set_aside():
    saga = _saga()
    kyrillos = _who(saga, "k")
    kyrillos.virtues_flaws.append(VirtueFlawInstance("vf_station_of_the_perfect_tool"))
    assert cr.path_of(kyrillos) is SEEMING  # two stations against one
    kyrillos.enigma.path = "body"
    assert cr.path_of(kyrillos) is cr.PATHS["body"]
    aside = cr.set_aside(kyrillos, cr.PATHS["body"])
    assert [s.name for _, s in aside] == ["Differentiation of Seeming", "True Sight"]
    # Only the Primus keeps them, on the Path of the Mirror (p. 58).
    assert len(cr.set_aside(kyrillos, cr.MIRROR)) == 3
    kyrillos.hermetic.primus = "Kyrillos"
    assert cr.set_aside(kyrillos, cr.MIRROR) == []


def test_only_the_primus_is_offered_the_path_of_the_mirror():
    saga = _saga()
    kyrillos = _who(saga, "k")

    def offered() -> list[str]:
        fields = {f.key: f for f in cf.path_fields(saga, kyrillos)}
        return [value for _, value in fields["path"].options or []]

    assert cr.MIRROR.key not in offered()
    kyrillos.hermetic.primus = "Someone else"
    assert not cr.is_primus(kyrillos) and cr.MIRROR.key not in offered()
    kyrillos.hermetic.primus = "kyrillos "
    assert cr.is_primus(kyrillos) and cr.MIRROR.key in offered()


def test_criamon_membership_and_the_tab():
    saga = _saga()
    kyrillos = _who(saga, "k")
    assert cr.is_criamon(kyrillos) and cr.has_enigma_tab(kyrillos)
    assert ts.belongs(kyrillos, cr.CULT_TRADITION)
    other = Character(id="o", name="Other", type="magus")
    assert not cr.has_enigma_tab(other)
    grog = _magus("g", "Grog")
    grog.type = "grog"
    assert not cr.has_enigma_tab(grog)
    assert cr.CULT_TRADITION in artwork.TRADITION_SYMBOLS


# -- the avenue ----------------------------------------------------------------------


def test_the_next_avenue_against_its_target():
    saga = _saga()
    kyrillos = _who(saga, "k")
    guide = cr.guide_of(saga, kyrillos, "t")
    assert guide is not None and guide.total == 6
    route = cr.avenue(kyrillos, SEEMING, 3, guide, 3)
    # Target 21 - 3 (first Initiation since a Minor Ordeal) = 18; 6 + 12.
    assert (route.target, route.total, route.enough) == (18, 18, True)
    assert "needs 4" in route.problems[0]
    ghost = cr.guide_of(saga, kyrillos, GHOST_GUIDE)
    assert ghost is not None and (ghost.lore, ghost.total) == (9, 9)


def test_head_binding_helps_only_the_first_station_of_its_path():
    magus = _magus("m", "M", lore=2)
    assert cr.avenue(magus, SEEMING, 1, None, 0).script == 15
    magus.enigma.aptitude_path = "seeming"
    assert cr.avenue(magus, SEEMING, 1, None, 0).script == 18
    assert cr.avenue(magus, SEEMING, 2, None, 0).script == 12
    assert cr.avenue(magus, cr.PATHS["body"], 1, None, 0).script == 15
    # The season adds it to the printed Script too (p. 51).
    assert cr.script_extra(magus, cr.script_key(SEEMING, 1)) == 3
    assert cr.script_extra(magus, cr.script_key(cr.PATHS["body"], 1)) == 0
    saga = _saga()
    saga.characters.append(magus)
    done = sw.work(saga, magus, _plan("m", 1, teacher_id="t"), None)
    # Theodora 6 + Script 15 + 3 = 24.
    assert any("Initiation Total 24" in note for note in done.notes)


def test_the_walking_backwards_fifth_keeps_the_printed_reduction():
    fifth = cr.PATHS["walking_backwards"].stations[4]
    assert fifth.printed_reduction == ("second Initiation since a Major Ordeal", 6)
    assert cr.target(fifth.printed_reduction[1]) == fifth.printed_target == 15
    info = cf.station_info(_walker(5), 4)
    assert "second Initiation since a Major Ordeal" in info
    assert "Intermediate" not in info


def _walker(stations: int) -> Character:
    walking = cr.PATHS["walking_backwards"]
    held = [s.virtue_id for s in walking.stations[:stations]]
    return _magus("w", "Walker", *held, lore=6)


def test_the_reduction_in_the_books_words():
    assert cr.reduction_words([("Minor", 0, 3)]) == (
        "his first Initiation since a Minor Ordeal"
    )
    assert cr.reduction_words([("Medium", 1, 4), ("Minor", 0, 3)]) == (
        "his second Initiation since a Medium Ordeal"
    )
    assert cr.reduction_words([]) == ""


# -- the Initiation season -----------------------------------------------------------


def test_an_avenue_through_the_initiation_season():
    saga = _saga()
    kyrillos = _who(saga, "k")
    kyrillos.abilities = [
        Ability(LORE, xp=ability_xp(4)) if a.name == LORE else a
        for a in kyrillos.abilities
    ]
    plan = _plan("k", 3, teacher_id="t")
    assert sw.problems(saga, kyrillos, plan) == []
    assert sw.initiation_target(saga, kyrillos, plan) == 18
    done = sw.work(saga, kyrillos, plan, None)
    assert done.initiated
    assert any("Initiation Total 18" in note for note in done.notes)
    added = {vf.vf_id for vf in done.add_vfs}
    assert {"vf_station_of_vivid_memories_from_objects", cr.PIOUS} <= added
    assert [vf.vf_id for vf in done.remove_vfs] == [cr.VOW]
    assert done.ordeal == "Medium"
    assert done.enigma_station == "vf_station_of_vivid_memories_from_objects"
    assert any("new stigma" in note for note in done.notes)
    apply_supplement(saga, kyrillos, plan, done)
    assert [r.vf_id for r in kyrillos.enigma.reached] == [
        "vf_station_of_vivid_memories_from_objects"
    ]
    assert cr.when_reached(kyrillos, done.enigma_station) == "Winter 1220"
    assert cr.station_reached(kyrillos, SEEMING) == 3
    assert any(o.size == "Medium" for o in kyrillos.ordeals)


def test_the_lore_requirement_and_the_order_are_checked():
    saga = _saga()
    kyrillos = _who(saga, "k")
    short = sw.problems(saga, kyrillos, _plan("k", 3, teacher_id="t"))
    assert "Mystery Cult Lore: Criamon 4" in short[0]
    skip = sw.problems(saga, kyrillos, _plan("k", 4, teacher_id="t"))
    assert skip  # Lore 5 and the station before it
    held = sw.problems(saga, kyrillos, _plan("k", 2, teacher_id="t"))
    assert "already" in held[0]
    stranger = Character(id="x", name="Stranger", type="magus")
    saga.characters.append(stranger)
    assert sw.problems(saga, stranger, _plan("x", 1, teacher_id="t"))


def test_a_ghostly_primus_guides_when_none_is_named():
    saga = _saga()
    kyrillos = _who(saga, "k")
    kyrillos.abilities = [
        Ability(LORE, xp=ability_xp(4)) if a.name == LORE else a
        for a in kyrillos.abilities
    ]
    kyrillos.enigma.primus_presence = 2
    kyrillos.enigma.guide_id = GHOST_GUIDE
    plan = _plan("k", 3)
    assert sw.problems(saga, kyrillos, plan) == []
    done = sw.work(saga, kyrillos, plan, None)
    assert any("ghostly Primus" in note for note in done.notes)
    # Presence +2 + Lore 9 + Script 12 = 23.
    assert any("Initiation Total 23" in note for note in done.notes)


def test_the_house_provides_a_guide_when_none_is_named():
    saga = _saga()
    kyrillos = _who(saga, "k")
    kyrillos.abilities = [
        Ability(LORE, xp=ability_xp(4)) if a.name == LORE else a
        for a in kyrillos.abilities
    ]
    kyrillos.enigma.primus_presence = 2
    plan = _plan("k", 3)
    assert sw.problems(saga, kyrillos, plan) == []
    done = sw.work(saga, kyrillos, plan, None)
    assert any("guide the House provides" in note for note in done.notes)
    # Presence + Lore 6 (p. 60) + Script 12 = 18, the printed Target.
    assert any("Initiation Total 18" in note for note in done.notes)
    guide = cr.guide_of(saga, kyrillos, "")
    assert guide is not None and guide.house and guide.total == 6
    assert cr.guide_of(saga, kyrillos, HOUSE_GUIDE) == guide
    assert cr.guide_of(saga, kyrillos, "gone") is None


def test_a_guide_needs_the_lore_and_one_from_outside_is_unusual():
    saga = _saga()
    kyrillos = _who(saga, "k")
    kyrillos.abilities = [
        Ability(LORE, xp=ability_xp(4)) if a.name == LORE else a
        for a in kyrillos.abilities
    ]
    outsider = Character(id="b", name="Brother", type="magus")
    outsider.hermetic.house = "house_bonisagus"
    outsider.abilities.append(Ability(LORE, xp=ability_xp(6)))
    unlearned = Character(id="u", name="Unlearned", type="magus")
    saga.characters += [outsider, unlearned]
    assert [c.id for c in cr.guides(saga, kyrillos)] == ["t", "b"]
    guide = cr.guide_of(saga, kyrillos, "b")
    assert guide is not None and guide.outsider
    route = cr.avenue(kyrillos, SEEMING, 3, guide, 3)
    assert route.problems == () and "unusual" in route.warnings[0]
    plan = _plan("k", 3, teacher_id="b")
    assert sw.problems(saga, kyrillos, plan) == []
    done = sw.work(saga, kyrillos, plan, None)
    assert done.initiated
    assert any("unusual" in note for note in done.notes)
    assert sw.problems(saga, kyrillos, _plan("k", 3, teacher_id="u"))


def test_the_book_name_for_the_lore_counts():
    saga = _saga()
    theodora = _who(saga, "t")
    theodora.abilities = [
        Ability("House Criamon Lore", xp=ability_xp(5)) if a.name == LORE else a
        for a in theodora.abilities
    ]
    assert cr.cult_lore(theodora) == 5
    novice = _magus("n", "Novice", lore=2)
    saga.characters.append(novice)
    plan = _plan("n", 1, teacher_id="t")
    assert sw.problems(saga, novice, plan) == []
    done = sw.work(saga, novice, plan, None)
    assert any("Initiation Total 21" in note for note in done.notes)
    assert {vf.vf_id for vf in done.add_vfs} >= {
        "vf_station_of_differentiation_of_seeming",
        "vf_disfigured",
        # The package the station gives (p. 64).
        "vf_clear_thinker",
        "vf_common_sense",
        "vf_keen_vision",
    }
    assert done.ordeal == "Minor"
    assert any("Keen Vision may be traded" in note for note in done.notes)


def test_station_virtues_are_not_given_twice_nor_without_initiation():
    saga = _saga()
    novice = _magus("n", "Novice", "vf_common_sense", lore=2)
    saga.characters.append(novice)
    done = sw.work(saga, novice, _plan("n", 1, teacher_id="t"), None)
    added = [vf.vf_id for vf in done.add_vfs]
    assert added.count("vf_common_sense") == 0 and "vf_clear_thinker" in added
    # Short of the Target: the Ordeal's Flaw only, no station Virtues.
    _who(saga, "t").characteristics = Characteristics(presence=-5)
    weak = _magus("v", "Weak", lore=2)
    saga.characters.append(weak)
    failed = sw.work(saga, weak, _plan("v", 1, teacher_id="t"), None)
    assert not failed.initiated
    assert "vf_clear_thinker" not in [vf.vf_id for vf in failed.add_vfs]


def test_expression_gives_free_expression_and_inspirational():
    saga = _saga()
    walker = _walker(2)
    saga.characters.append(walker)
    walking = cr.PATHS["walking_backwards"]
    done = sw.work(
        saga, walker, _plan("w", 3, walking, teacher_id="t", other_modifier=6), None
    )
    assert done.initiated
    assert {"vf_free_expression", "vf_inspirational"} <= {
        vf.vf_id for vf in done.add_vfs
    }


def test_a_plans_own_ordeal_replaces_the_stations():
    saga = _saga()
    novice = _magus("n", "Novice", lore=2)
    saga.characters.append(novice)
    plan = _plan(
        "n", 1, teacher_id="t", ordeal_kind="gain", device_id="vf_twilight_prone"
    )
    done = sw.work(saga, novice, plan, None)
    added = [vf.vf_id for vf in done.add_vfs]
    assert "vf_twilight_prone" in added and "vf_disfigured" not in added


def test_the_strife_path_ordeals_by_hand_and_the_blatant_gift_lifted():
    body = cr.PATHS["strife"].stations[4]
    assert "Incompatible Arts" in body.by_hand
    saga = _saga()
    magus = _magus("w", "Walker", cr.BLATANT_GIFT, lore=2)
    saga.characters.append(magus)
    walking = cr.PATHS["walking_backwards"]
    done = sw.work(saga, magus, _plan("w", 1, walking, teacher_id="t"), None)
    assert cr.BLATANT_GIFT in [vf.vf_id for vf in done.remove_vfs]
    added = [vf.vf_id for vf in done.add_vfs]
    # The Blatant Gift lifted to an ordinary Gift, and no Gentle Gift (p. 70).
    assert cr.PIOUS in added and cr.GENTLE_GIFT not in added
    plain = _magus("p", "Plain", lore=2)
    saga.characters.append(plain)
    done = sw.work(saga, plain, _plan("p", 1, walking, teacher_id="t"), None)
    assert cr.GENTLE_GIFT in [vf.vf_id for vf in done.add_vfs]
    assert cr.BLATANT_GIFT not in [vf.vf_id for vf in done.remove_vfs]


# -- the model ------------------------------------------------------------------------


def test_the_enigma_loads_and_refuses_bad_data():
    enigma = Enigma.from_dict(
        {
            "path": "seeming",
            "guide_id": "t",
            "reached": [
                {"vf_id": "vf_station_of_true_sight", "season": "Autumn", "year": 1214}
            ],
            "stigmata": [{"where": "Eyelids", "mark": "A spiral", "why": "station"}],
        }
    )
    assert enigma.stigmata[0].mark == "A spiral"
    assert enigma.aptitude_path == ""
    assert Enigma.from_dict({"aptitude_path": "body"}).aptitude_path == "body"
    with pytest.raises(ValueError, match="aptitude_path"):
        Enigma.from_dict({"aptitude_path": 3})
    assert enigma.reached[0].year == 1214
    with pytest.raises(ValueError, match="stigma"):
        Enigma.from_dict({"stigmata": [{"where": "x", "mark": "y", "why": "nonsense"}]})
    with pytest.raises(ValueError, match="year"):
        Enigma.from_dict({"reached": [{"vf_id": "v", "year": "soon"}]})
    with pytest.raises(ValueError, match="season"):
        Stigma.from_dict({"where": "x", "mark": "y", "season": "Monsoon"})
    assert (
        Character.from_dict({"id": "c", "name": "C", "type": "magus"}).enigma
        == Enigma()
    )


# -- the tab's words and forms --------------------------------------------------------


def test_the_path_text_says_what_the_next_avenue_needs():
    saga = _saga()
    kyrillos = _who(saga, "k")
    kyrillos.enigma.guide_id = "t"
    words = cf.path_text(saga, kyrillos)
    assert "of Seeming" in words and "2 of 5: True Sight" in words
    assert (
        "Target 21 − 3 (his first Initiation since a Minor Ordeal) = [b]18[/]" in words
    )
    assert "But his House Criamon Lore is 3: the third station needs 4." in words
    assert "needs 4" in words
    assert "Disfigured, Vow" in words
    rows = cf.station_rows(kyrillos)
    assert len(rows) == 5 and "needs Lore 4" in rows[2][1]


def test_follow_an_avenue_plans_the_initiation():
    saga = _saga()
    kyrillos = _who(saga, "k")
    form = cf.avenue_form(saga, kyrillos)
    fields = {f.key: f for f in form.fields()}
    values = {key: f.value for key, f in fields.items()}
    values.update(guide="t", season="Winter", year=1220)
    assert form.live is not None
    live = form.live(values)
    assert "against Target [b]18[/]" in live and "needs 4" in live
    form.apply(values)
    plan = plan_for(saga, kyrillos, "Winter", 1220)
    assert plan is not None
    assert plan.hedge_script == cr.script_key(SEEMING, 3)
    assert plan.effect_id == "vf_station_of_vivid_memories_from_objects"
    assert plan.teacher_id == "t"
    assert plan.other_modifier == 0
    assert kyrillos.enigma.guide_id == "t"


def test_the_guide_defaults_to_the_houses_and_the_talisman_adds_nothing():
    saga = _saga()
    kyrillos = _who(saga, "k")
    form = cf.avenue_form(saga, kyrillos)
    fields = {f.key: f for f in form.fields()}
    assert fields["guide"].value == HOUSE_GUIDE
    assert "(+3)" not in fields["talisman"].label
    assert "head" not in fields
    values = {key: f.value for key, f in fields.items()}
    values.update(season="Winter", year=1220)
    assert form.live is not None
    plain = form.live(values)
    values["talisman"] = True
    lost = form.live(values)
    assert "guide the House" in cf.path_text(saga, kyrillos)
    # Giving up the talisman replaces the special time and place's +3.
    assert "= [b]18[/] against Target [b]18[/]" in plain
    assert "= [b]18[/] against Target [b]18[/]" in lost
    form.apply(values)
    plan = plan_for(saga, kyrillos, "Winter", 1220)
    assert plan is not None and plan.teacher_id is None
    assert "in place of the special time" in plan.details


def test_the_stigmata_ops():
    saga = _saga()
    kyrillos = _who(saga, "k")
    ops = cf.stigma_ops(saga, kyrillos)
    assert ops.add is not None
    form = ops.add()
    assert hasattr(form, "apply")
    form.apply(  # type: ignore[union-attr]
        {
            "where": "Eyelids",
            "mark": "A spiral",
            "why": "station",
            "detail": "",
            "season": "Autumn",
            "year": 1214,
        }
    )
    assert cf.stigma_rows(kyrillos)[0][1].startswith("Eyelids")
    assert "a station reached, Autumn" in cf.stigma_rows(kyrillos)[0][1]

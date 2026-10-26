"""Ancient Magic's integrations as data (ancient_magic_catalog.json) and
the rules that read them: Grigori Magic (pp. 65-74), Heron's mechanica
(pp. 76-80), the Language of Adam (pp. 10-11) and Ptolemy's coordinates
(pp. 89-92), with the Errata (p. 58)."""

import random

import pytest

from ars_magica_manager import catalog, seasons
from ars_magica_manager.casting_text import casting_virtue_lines
from ars_magica_manager.models import (
    Ability,
    ArtScore,
    Breakthrough,
    Character,
    Characteristics,
    Covenant,
    Laboratory,
    Progress,
    Saga,
    SeasonPlan,
    Spell,
    VirtueFlawInstance,
)
from ars_magica_manager.models.ancient_magic import (
    AncientChapter,
    InsightSource,
    IntegrationNote,
)
from ars_magica_manager.rules import ancient_integrations as am
from ars_magica_manager.rules import integrations, lab_seasons, penetration
from ars_magica_manager.rules.season_work import BY_KEY, REGISTRY, SupplementWork
from ars_magica_manager.rules.xp import ability_xp, art_xp
from ars_magica_manager.sheet_text import goal_text


def _magus(*abilities: tuple[str, int], vfs: tuple[VirtueFlawInstance, ...] = ()):
    return Character(
        id="m",
        name="Tiberius",
        type="magus",
        covenant_id="cov",
        characteristics=Characteristics(intelligence=2),
        abilities=[Ability(name, xp=ability_xp(score)) for name, score in abilities],
        virtues_flaws=list(vfs),
    )


# -- the catalog ----------------------------------------------------------


def test_the_catalog_has_the_four_chapters_with_their_pages():
    pages = {c.id: c.pages for c in am.chapters()}
    assert pages == {
        "am_adamic": "10-11",
        "am_grigori": "65-74",
        "am_heron": "75-80",
        "am_hesperides": "89-92",
    }


def test_every_reference_in_the_catalog_names_a_record_that_exists():
    virtues = catalog.load_virtue_flaw_catalog_by_id()
    spells = catalog.load_spell_catalog_by_id()
    traditions = catalog.load_tradition_catalog_by_id()
    names = {i.name for i in integrations.INTEGRATIONS}
    wrong = []
    for chapter in am.chapters():
        wrong += [f"{chapter.id}: {s}" for s in chapter.spells if s not in spells]
        if chapter.tradition and chapter.tradition not in traditions:
            wrong.append(f"{chapter.id}: {chapter.tradition}")
        wrong += [
            f"{chapter.id}: {s.vf_id}"
            for s in chapter.secrets
            if s.vf_id not in virtues
        ]
        for note in chapter.integrations:
            if note.name not in names:
                wrong.append(f"{chapter.id}: integration {note.name}")
            if note.requires and note.requires not in names:
                wrong.append(f"{chapter.id}: requires {note.requires}")
            wrong += [
                f"{note.name}: {v}" for v in note.bonus_virtues if v not in virtues
            ]
            if note.grant_kind == "Virtue" and note.grant not in virtues:
                wrong.append(f"{note.name}: grant {note.grant}")
    assert not wrong, wrong


def test_the_catalogs_new_breakthroughs_join_the_integration_choices():
    after = integrations.BY_NAME["Awakened Device, after Mutable Device"]
    assert (after.kind, after.target, after.grant) == ("Minor", 30, "vf_awaken_device")
    second = integrations.BY_NAME["Mutable Device without the Virtue"]
    assert (second.kind, second.target, second.book) == ("Major", 45, "Ancient Magic")
    names = [i.name for i in integrations.INTEGRATIONS]
    assert len(names) == len(set(names))


def test_bad_catalog_values_are_reported_with_the_record():
    with pytest.raises(ValueError, match="Stone"):
        InsightSource.from_dict({"name": "Stone", "kind": "rock", "gives": ""})
    with pytest.raises(ValueError, match="Odd"):
        IntegrationNote.from_dict({"name": "Odd", "kind": "Grand", "target": 30})
    with pytest.raises(ValueError, match="needs a target"):
        IntegrationNote.from_dict({"name": "Odd", "kind": "Minor"})
    with pytest.raises(ValueError, match="values not numbers"):
        AncientChapter.from_dict(
            {"id": "x", "name": "X", "pages": "1", "values": {"a": "two"}}
        )


# -- integrations ---------------------------------------------------------


def test_a_secret_holder_gains_a_point_a_season_researching_its_legacy():
    secret = (VirtueFlawInstance("vf_araqiel_secret"),)
    goal = Breakthrough("Grigori Legacy", kind="Major", target=45)
    assert am.season_bonus(_magus(), goal) == 0
    assert am.season_bonus(_magus(vfs=secret), goal) == 1
    # A Legacy counts toward the Limit of Vis, not toward another Legacy.
    legacy = (VirtueFlawInstance("vf_grigori_legacy", {"secret": "Armaros"}),)
    assert am.season_bonus(_magus(vfs=legacy), goal) == 0
    limit = Breakthrough("Limit of Vis", kind="Hermetic", target=60)
    assert am.season_bonus(_magus(vfs=legacy), limit) == 1
    reached = Breakthrough("Limit of Vis", target=60, points=60, reached=True)
    assert am.season_bonus(_magus(vfs=legacy), reached) == 0


class _Dice(random.Random):
    def __init__(self, *faces: int) -> None:
        super().__init__(0)
        self.faces = list(faces)

    def randrange(self, *args, **kwargs):
        return self.faces.pop(0) if self.faces else 5


def test_a_research_season_adds_the_secrets_point_to_the_goal_and_its_log():
    covenant = Covenant(id="cov", saga_id="s", name="Keep")
    magus = _magus(("Magic Theory", 6), vfs=(VirtueFlawInstance("vf_ezeqeel_secret"),))
    magus.arts = {"muto": ArtScore(xp=art_xp(10)), "vim": ArtScore(xp=art_xp(10))}
    magus.assigned_lab_id = "lab"
    lab = Laboratory(id="lab", covenant_id="cov", name="Tower", owner_id="m")
    saga = Saga(
        id="s", name="S", covenants=[covenant], characters=[magus], laboratories=[lab]
    )
    saga.spells = [Spell("harness", "Harness", "Muto", "Vim", level=10)]
    plan = SeasonPlan(
        "m",
        1220,
        "Spring",
        lab_seasons.INVENT,
        lab_id="lab",
        spell_id="harness",
        experimenting=True,
        risk=1,
        research="Grigori Legacy",
        research_kind="Major",
    )
    seasons.set_plan(saga, plan)
    # Chart 3 + 1 = 4: no effect, nothing to move onto a Discovery.
    seasons.apply(saga, seasons.resolve(saga, _Dice(5, 3)))
    (goal,) = magus.breakthroughs
    assert goal.points == 1
    assert goal.log[-1].points == 1
    assert any("A Secret of the Grigori held: +1" in e.details for e in lab.diary)


def test_awakened_device_after_mutable_device_needs_it_reached():
    magus = _magus()
    name = "Awakened Device, after Mutable Device"
    assert am.missing_prerequisite(magus, name) == "Mutable Device"
    magus.breakthroughs = [Breakthrough("Mutable Device", reached=True)]
    assert am.missing_prerequisite(magus, name) == ""
    assert am.missing_prerequisite(magus, "Awakened Device") == ""


def test_a_goals_details_name_its_insight_sources_and_bonus():
    text = goal_text(Breakthrough("Limit of Vis", kind="Hermetic", target=60))
    assert "Sources of Insight: The Enigma of the Sons of God, second book" in text
    # The first book and Azael give no Insight.
    assert "first book" not in text and "Azael" not in text
    assert "(Muto Vim)" in text
    assert "a Secret of the Grigori or a Grigori Legacy" in text
    after = goal_text(Breakthrough("Awakened Device, after Mutable Device"))
    assert "Builds on Mutable Device" in after
    assert am.goal_lines(Breakthrough("A goal of my own")) == []


# -- Grigori Magic --------------------------------------------------------


def test_a_secret_makes_its_three_arts_vis_interchangeable():
    magus = _magus(vfs=(VirtueFlawInstance("vf_araqiel_secret"),))
    assert am.interchangeable_vis(magus, "Terram") == ["Corpus", "Creo"]
    assert am.interchangeable_vis(magus, "Ignem") == []
    assert am.ignored_requisites(magus, "Creo", "Corpus", ["Terram", "Ignem"]) == [
        "Terram"
    ]
    # A Rego Ignem spell uses none of its Arts: nothing is ignored.
    assert am.ignored_requisites(magus, "Rego", "Ignem", ["Terram"]) == []


def test_a_tainted_secret_doubles_vis_botch_dice_in_divine_and_infernal_auras():
    magus = _magus(vfs=(VirtueFlawInstance("vf_araqiel_secret"),))
    assert am.vis_botch_dice(magus, 2, "Terram", "Creo", "Divine") == 4
    assert am.vis_botch_dice(magus, 2, "Terram", "Creo", "Infernal") == 4
    assert am.vis_botch_dice(magus, 2, "Terram", "Creo", "Magic") == 2
    assert am.vis_botch_dice(magus, 2, "Creo", "Creo", "Divine") == 2
    # The Legacy (Araquiel's, as the book also spells it) has no taint.
    legacy = VirtueFlawInstance("vf_grigori_legacy", {"secret": "Araquiel"})
    magus.virtues_flaws.append(legacy)
    assert am.held_secrets(magus) == [(am.secrets()[0], False)]
    assert am.vis_botch_dice(magus, 2, "Terram", "Creo", "Divine") == 2


def test_azaels_secret_is_tied_to_the_infernal():
    azael = next(s for s in am.secrets() if s.vf_id == "vf_azael_secret")
    assert azael.realm == "Infernal" and azael.arts == ("Perdo", "Terram", "Imaginem")
    entry = catalog.load_virtue_flaw_catalog_by_id()["vf_azael_secret"]
    assert "Infernal" in entry.description and "(Divine)" not in entry.description


def test_araqiels_legacy_uses_terram_not_herbam():
    # Errata p. 58 corrects the Legacy's Herbam to Terram.
    araqiel = am.secrets()[0]
    assert araqiel.arts == ("Creo", "Terram", "Corpus")


# -- Heron's mechanica ----------------------------------------------------


def test_the_mechanica_creation_level_and_its_cost():
    # Errata p. 58: 3 x magnitude + modifiers.
    assert am.mechanica_creation_level(4) == 12
    assert am.mechanica_creation_level(4, "Hand-sized") == 18
    assert am.mechanica_creation_level(1, "Wagon- or boat-sized", extra_time=True) == 3
    assert am.mechanica_cost(18) == 6
    with pytest.raises(ValueError, match="Tiny"):
        am.mechanica_creation_level(1, "Tiny")


def test_an_animas_might_and_its_awakening():
    maker = _magus(
        ("Mechanica of Heron", 4), ("Philosophiae", 3), ("Artes Liberales", 5)
    )
    assert am.mechanica_total(maker, aura=3) == 2 + 4 + 3 + 3
    # Size 0 + 10 material points + the lower learning (3).
    assert am.anima_might(maker, 0, 10) == 13
    assert am.anima_points_a_season(maker) == 6
    assert am.awaken_anima_level(13) == 9 + 3
    assert am.awaken_anima_total(maker, aura=3, season=3) == 12 + 2


def test_copying_a_mechanica_hermetically_and_mutable_devices():
    assert am.copy_bonus(effect_magnitude=4) == 4
    assert am.copy_bonus(text_level=4, text_quality=9) == 4
    assert am.mutable_device_level(25) == 35
    assert am.mutable_change_allowed(35, 25)
    assert not am.mutable_change_allowed(35, 30)
    assert am.awakened_device_might(10, 6) == 16
    assert am.awakened_device_level(16, 1) == 21
    assert am.awakened_device_vis(3, 16) == 19


# -- The Language of Adam -------------------------------------------------


def test_adamic_adds_one_to_the_penetration_multiplier_with_a_connection():
    novice = _magus(("Penetration", 4), ("Dead Language: Adamic", 1))
    assert am.adamic_penetration(novice) == (None, [])
    connection, sympathies = am.adamic_penetration(novice, "Hours or days")
    bonus = penetration.penetration_bonus(
        novice, arcane_connection=connection, sympathies=sympathies
    )
    # The book's example: Adamic 1 and an Hours connection, +2 (x3).
    assert int(bonus.total) == 4 * 3


def test_a_fluent_speaker_always_has_a_lasting_connection():
    fluent = _magus(("Penetration", 4), ("Dead Language: Adamic", 5))
    assert am.adamic_fluent(fluent)
    connection, sympathies = am.adamic_penetration(fluent)
    assert connection == am.LASTING_CONNECTION
    bonus = penetration.penetration_bonus(
        fluent, arcane_connection=connection, sympathies=sympathies
    )
    # +5 in all (p. 11): x6.
    assert int(bonus.total) == 4 * 6
    assert am.adamic_untaught_cap() == 2
    assert am.adamic_penetration(_magus()) == (None, [])


def test_the_casting_panel_reminds_of_adamic_and_the_secrets():
    magus = _magus(
        ("Dead Language: Adamic", 2),
        vfs=(VirtueFlawInstance("vf_shamsiel_secret"),),
    )
    text = " ".join(casting_virtue_lines(magus))
    assert "Adamic 2: +1 to the Penetration multiplier" in text
    assert "Shamsiel's Secret: vis of Rego, Ignem, Vim" in text
    assert "double the botch dice" in text
    assert casting_virtue_lines(_magus()) == []


# -- The Hesperides -------------------------------------------------------


def test_a_stellar_observation_and_its_hours():
    observer = _magus(("Artes Liberales", 4))
    assert am.observation_ease() == 15
    assert am.observation_total(observer) == 6
    assert am.observation_total(observer, handy_tables=True) == 7
    assert am.observation_hours() == 8
    assert am.observation_hours(timepiece=True, tables="handy") == 3
    with pytest.raises(ValueError, match="atlas"):
        am.observation_hours(tables="atlas")


def test_the_measuring_season_records_the_method_and_stops_a_second():
    saga = Saga(id="s", name="S")
    magus = _magus()
    assert am.coordinates_problems(magus, calibrated=False) == [
        "Learn to measure the fixed stars (a season).",
        "Calibrate the system at the origin (the Purple Islands).",
    ]
    plan = SeasonPlan("m", 1220, "Spring", "measure_fixed_stars")
    entry = REGISTRY["measure_fixed_stars"]
    assert BY_KEY["measure_fixed_stars"].no_xp
    assert entry.check(saga, magus, plan) == []
    result = SupplementWork()
    entry.outcome(saga, magus, plan, None, result)
    assert result.progress == [(am.MEASURING_KIND, am.MEASURING, 1, 1)]
    magus.progress.append(Progress(am.MEASURING_KIND, am.MEASURING, 1, 1, done=True))
    assert am.knows_stellar_measurement(magus)
    assert am.coordinates_problems(magus, calibrated=True) == []
    assert entry.check(saga, magus, plan)


def test_the_fixed_stars_spell_follows_the_errata():
    spell = catalog.load_spell_catalog_by_id()[
        "spell_a_comparison_of_the_positions_of_the_fixed_stars"
    ]
    assert (spell.level, spell.range) == (15, "Touch")
    assert "Celestial Magic" not in spell.description
    assert "1000 paces" in spell.description

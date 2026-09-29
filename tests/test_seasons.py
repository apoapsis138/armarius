"""Season plans and advancing the season (STORY-903): the activities' rules
(rules.seasons), applying a season (seasons), and the character sheet's
This Season / Diary tab and Advance Season in the workspace."""

import copy
from dataclasses import asdict

from support import build_all_tabs, everything_saga, strip_markup, wait_until
from textual.widgets import Button, Collapsible, Select, Static, TabbedContent, Tree

from ars_magica_manager import seasons, storage
from ars_magica_manager.app import ArsMagicaManagerApp
from ars_magica_manager.models import (
    Ability,
    ArtScore,
    Character,
    Covenant,
    DiaryEntry,
    Inhabitant,
    KnownSpell,
    Saga,
    SeasonPlan,
    VirtueFlawInstance,
    XpAllocation,
)
from ars_magica_manager.rules import seasons as rules
from ars_magica_manager.rules.xp import ability_xp
from ars_magica_manager.screens import ConfirmScreen, FieldsDialog, WorkspaceScreen


def _magus() -> Character:
    magus = Character(id="m", name="Tiberius", type="magus")
    magus.abilities = [Ability("Latin", xp=ability_xp(4)), Ability("Magic Theory")]
    magus.arts = {"creo": ArtScore(xp=10)}
    magus.spells_known = [KnownSpell("spell-x", mastery_score=0, mastery_xp=3)]
    return magus


def _companion() -> Character:
    companion = Character(id="c", name="Alys", type="companion")
    companion.abilities = [Ability("Brawl", xp=ability_xp(2))]
    return companion


def _plan(
    character: Character, activity: str, *subjects: str | tuple[str, int], **kw
) -> SeasonPlan:
    allocations = [
        XpAllocation(*s) if isinstance(s, tuple) else XpAllocation(s) for s in subjects
    ]
    return SeasonPlan(character.id, 1220, "Spring", activity, allocations, **kw)


def _xp(outcome: rules.Outcome) -> list[tuple[str, int]]:
    return [(g.subject, g.result.xp) for g in outcome.gains]


# -- rules: who may plan what --------------------------------------------------


def test_grogs_are_not_planned_season_by_season():
    grog = Character(id="g", name="Hob", type="grog")
    assert not rules.is_planned(grog)
    assert rules.activities_for(grog) == []
    plan = _plan(grog, rules.OTHER, details="Drill")
    assert "Grogs aren't planned" in rules.problems(grog, plan)[0]


def test_magi_and_companions_plan_every_activity_built_so_far():
    for character in (_magus(), _companion()):
        keys = [a.key for a in rules.activities_for(character)]
        assert keys == [rules.EXPOSURE, rules.PRACTICE, rules.ADVENTURE, rules.OTHER]
    mythic = Character(id="y", name="Wode", type="mythic companion")
    assert rules.is_planned(mythic)


# -- rules: what a season gives ------------------------------------------------


def test_exposure_is_2_xp_in_one_subject_or_1_each_in_two():
    magus = _magus()
    one = rules.outcome(magus, _plan(magus, rules.EXPOSURE, "ability:Latin"))
    assert _xp(one) == [("ability:Latin", 2)]
    two = rules.outcome(
        magus, _plan(magus, rules.EXPOSURE, "ability:Latin", "art:Creo")
    )
    assert _xp(two) == [("ability:Latin", 1), ("art:Creo", 1)]


def test_practice_is_source_quality_4_or_5_for_a_spells_mastery():
    magus = _magus()
    practice = rules.outcome(magus, _plan(magus, rules.PRACTICE, "ability:Latin"))
    assert _xp(practice) == [("ability:Latin", 4)]
    mastery = rules.outcome(magus, _plan(magus, rules.PRACTICE, "mastery:spell-x"))
    assert _xp(mastery) == [("mastery:spell-x", 5)]
    # A typed Source Quality (a language among native speakers: 8).
    native = rules.outcome(
        magus, _plan(magus, rules.PRACTICE, "ability:Latin", source_quality=8)
    )
    assert _xp(native) == [("ability:Latin", 8)]


def test_arts_cant_be_practised():
    magus = _magus()
    worked = rules.outcome(magus, _plan(magus, rules.PRACTICE, "art:Creo"))
    assert not worked.ok
    assert "Arts can't be practised" in worked.problems[0]
    assert worked.gains == []


def test_adventure_splits_its_source_quality_at_most_5_to_each():
    magus = _magus()
    ok = _plan(
        magus,
        rules.ADVENTURE,
        ("ability:Latin", 5),
        ("art:Creo", 3),
        source_quality=8,
    )
    assert _xp(rules.outcome(magus, ok)) == [("ability:Latin", 5), ("art:Creo", 3)]
    too_much = _plan(magus, rules.ADVENTURE, ("ability:Latin", 6), source_quality=6)
    assert any("1 to 5" in p for p in rules.problems(magus, too_much))
    unsplit = _plan(magus, rules.ADVENTURE, ("ability:Latin", 5), source_quality=8)
    assert any("Split all 8" in p for p in rules.problems(magus, unsplit))
    no_quality = _plan(magus, rules.ADVENTURE, ("ability:Latin", 5))
    assert any("5 to 10" in p for p in rules.problems(magus, no_quality))


def test_months_lost_cut_a_third_a_month_rounded_up():
    magus = _magus()
    plan = _plan(
        magus, rules.PRACTICE, "ability:Latin", source_quality=8, months_lost=1
    )
    # 8 x 2/3 = 5.33 -> 6 (DE Ch. 10, Distractions).
    assert _xp(rules.outcome(magus, plan)) == [("ability:Latin", 6)]


def test_affinity_multiplies_a_seasons_xp():
    magus = _magus()
    magus.virtues_flaws = [
        VirtueFlawInstance("vf_affinity_with_ability", params={"ability": "Latin"})
    ]
    practice = _plan(magus, rules.PRACTICE, "ability:Latin")
    assert _xp(rules.outcome(magus, practice)) == [("ability:Latin", 6)]  # 4 x 1.5
    magus.virtues_flaws = [
        VirtueFlawInstance("vf_affinity_with_art", params={"art": "creo"})
    ]
    exposure = _plan(magus, rules.EXPOSURE, "art:Creo")
    assert _xp(rules.outcome(magus, exposure)) == [("art:Creo", 3)]  # 2 x 1.5


def test_other_needs_no_subject_and_gives_no_xp():
    magus = _magus()
    worked = rules.outcome(magus, _plan(magus, rules.OTHER, details="Tribunal"))
    assert worked.ok and worked.gains == []


def test_a_subject_the_character_lacks_is_a_problem():
    companion = _companion()
    worked = rules.outcome(companion, _plan(companion, rules.EXPOSURE, "art:Creo"))
    assert worked.problems == ["Alys doesn't have Creo."]


# -- applying a season ---------------------------------------------------------


def _saga(*characters: Character) -> Saga:
    return Saga(id="s", name="S", characters=list(characters))


def test_apply_adds_xp_writes_the_diary_and_drops_the_plan():
    magus = _magus()
    saga = _saga(magus)
    seasons.set_plan(
        saga, _plan(magus, rules.PRACTICE, "ability:Latin", details="Aloud")
    )
    applied = seasons.apply(saga, seasons.resolve(saga))
    assert applied == [magus]
    assert magus.abilities[0].xp == ability_xp(4) + 4
    entry = magus.diary[-1]
    assert (entry.year, entry.season, entry.activity) == (1220, "Spring", "Practice")
    assert entry.name == "Latin (+4 xp)"
    assert "Latin: Advancement Total 4, +4 xp (score 4, 50 -> 54 xp)." in entry.details
    assert "Notes: Aloud" in entry.details
    assert "Chapter 10: Long Term Events, Practice" in entry.details
    assert saga.season_plans == []


def test_mastery_practice_raises_a_score_but_never_lowers_one():
    magus = _magus()
    saga = _saga(magus)
    seasons.set_plan(saga, _plan(magus, rules.PRACTICE, "mastery:spell-x"))
    seasons.apply(saga, seasons.resolve(saga))
    known = magus.spells_known[0]
    assert (known.mastery_xp, known.mastery_score) == (8, 1)  # 3 + 5 xp


def test_applying_in_any_order_gives_the_same_saga():
    """Every outcome is worked out before any is applied, and applying one
    never changes another: the order can't matter (phase-3-goals.md)."""
    magus, companion = _magus(), _companion()
    saga = _saga(magus, companion)
    seasons.set_plan(
        saga,
        _plan(
            magus,
            rules.ADVENTURE,
            ("ability:Latin", 5),
            ("art:Creo", 5),
            source_quality=10,
        ),
    )
    seasons.set_plan(saga, _plan(companion, rules.EXPOSURE, "ability:Brawl"))
    worked = seasons.resolve(saga)
    forward, backward = copy.deepcopy(saga), copy.deepcopy(saga)
    seasons.apply(forward, worked)
    seasons.apply(backward, list(reversed(worked)))
    assert asdict(forward) == asdict(backward)


def test_outcomes_come_from_the_state_before_the_season():
    """An outcome worked out before applying isn't changed by applying: the
    xp figures in the Diary are the pre-season ones."""
    magus = _magus()
    saga = _saga(magus)
    seasons.set_plan(saga, _plan(magus, rules.EXPOSURE, "ability:Latin"))
    worked = seasons.resolve(saga)
    before = worked[0].gains[0].before
    seasons.apply(saga, worked)
    assert worked[0].gains[0].before == before == ability_xp(4)


def test_a_plan_that_cant_be_carried_out_is_skipped_and_dropped():
    magus = _magus()
    saga = _saga(magus)
    seasons.set_plan(saga, _plan(magus, rules.PRACTICE, "art:Creo"))
    summary = strip_markup(seasons.advance_summary(saga))
    assert "Tiberius's plan can't be carried out: Arts can't be practised" in summary
    assert seasons.apply(saga, seasons.resolve(saga)) == []
    assert magus.diary == [] and saga.season_plans == []


def test_later_plans_are_kept_and_older_ones_dropped():
    magus = _magus()
    saga = _saga(magus)
    saga.current_season = "Summer"
    later = SeasonPlan("m", 1220, "Autumn", rules.OTHER, details="Travel")
    older = SeasonPlan("m", 1220, "Spring", rules.OTHER, details="Missed")
    saga.season_plans = [later, older]
    seasons.apply(saga, seasons.resolve(saga))
    assert saga.season_plans == [later]


def test_set_plan_replaces_the_seasons_plan():
    magus = _magus()
    saga = _saga(magus)
    seasons.set_plan(saga, _plan(magus, rules.OTHER, details="One"))
    seasons.set_plan(saga, _plan(magus, rules.OTHER, details="Two"))
    assert [p.details for p in saga.season_plans] == ["Two"]
    assert seasons.clear_plan(saga, magus)
    assert not seasons.clear_plan(saga, magus)


def test_unplanned_lists_magi_and_companions_not_grogs_or_the_departed():
    magus, companion = _magus(), _companion()
    grog = Character(id="g", name="Hob", type="grog")
    gone = Character(id="x", name="Gone", type="magus", covenant_id="cov")
    saga = _saga(magus, companion, grog, gone)
    saga.covenants = [
        Covenant(
            id="cov",
            saga_id="s",
            name="Cov",
            inhabitants=[
                Inhabitant(id="i", kind="magus", character_id="x", departed=True)
            ],
        )
    ]
    assert seasons.unplanned(saga) == [magus, companion]
    seasons.set_plan(saga, _plan(magus, rules.OTHER, details="Rest"))
    assert seasons.unplanned(saga) == [companion]
    summary = strip_markup(seasons.advance_summary(saga))
    assert "1 planned season(s) will be applied." in summary
    assert "Nothing planned for: Alys (companion)." in summary


def test_a_companion_is_reminded_of_their_two_working_seasons():
    companion = _companion()
    plan = SeasonPlan(
        "c", 1220, "Autumn", rules.PRACTICE, [XpAllocation("ability:Brawl")]
    )
    # Autumn with none worked: Winter alone can't hold both.
    note = seasons.working_seasons_note(companion, plan)
    assert note is not None and "0 worked in 1220 so far" in note
    companion.diary = [
        DiaryEntry(1220, "Spring", "Smithing", activity="Work / Exposure"),
    ]
    assert seasons.working_seasons_note(companion, plan) is None
    working = SeasonPlan(
        "c", 1220, "Autumn", rules.EXPOSURE, [XpAllocation("ability:Brawl")]
    )
    assert seasons.working_seasons_note(_companion(), working) is None


def test_plans_and_the_character_diary_survive_a_save():
    magus = _magus()
    saga = _saga(magus)
    seasons.set_plan(
        saga, _plan(magus, rules.ADVENTURE, ("ability:Latin", 5), source_quality=5)
    )
    magus.diary = [DiaryEntry(1219, "Winter", "Rest", "Quiet", "Other")]
    storage.save_saga(saga)
    loaded = storage.load_saga("s")
    assert loaded.season_plans == saga.season_plans
    assert loaded.character("m").diary == magus.diary


def test_backup_is_kept_outside_the_saga_list():
    saga = _saga(_magus())
    storage.save_saga(saga)
    path = storage.backup_saga(saga)
    assert path.exists() and path.parent.name == "backups"
    assert storage.list_sagas() == ["s"]


# -- the character sheet and Advance Season ---------------------------------------


def _find(tree, data):
    pending = [tree.root]
    while pending:
        node = pending.pop()
        if node.data == data:
            return node
        pending.extend(node.children)
    return None


async def _open_season(pilot, app) -> None:
    await pilot.press("enter")  # saga picker -> workspace
    await pilot.pause()
    tree = app.screen.query_one("#nav-tree", Tree)
    tree.select_node(_find(tree, ("character", "mag1")))
    await wait_until(pilot, lambda: app.screen._character_sheet_view is not None)
    view = app.screen._character_sheet_view
    await wait_until(pilot, lambda: view.initial_tab_seen)
    await pilot.pause()
    view.query_one(TabbedContent).active = "tab-planning"
    await pilot.pause()
    view.query_one("#section-char-season", Collapsible).query_one(
        "CollapsibleTitle"
    ).focus()
    await wait_until(
        pilot, lambda: app.screen._active_section() == "section-char-season"
    )


async def test_plan_a_season_then_advance_applies_it():
    storage.save_saga(everything_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _open_season(pilot, app)
        view = app.screen._character_sheet_view
        await build_all_tabs(pilot, view)
        text = str(view.query_one("#char-season-content", Static).content)
        assert "Nothing planned for Spring 1220" in text

        await pilot.press("e")
        assert await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
        dialog = app.screen
        dialog.query_one("#fld-activity", Select).value = rules.PRACTICE
        await pilot.pause()
        dialog.query_one("#fld-subject_1", Select).value = "ability:Latin"
        await pilot.pause()
        live = strip_markup(str(dialog.query_one("#fields-live", Static).content))
        assert "Latin: Advancement Total 4, +4 xp" in live
        dialog.query_one("#btn-save", Button).press()
        assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        text = strip_markup(str(view.query_one("#char-season-content", Static).content))
        assert text.splitlines()[0] == "Practice: Latin"

        workspace = app.screen
        await pilot.press("t")
        await pilot.pause()
        plans = strip_markup(
            str(app.screen.query_one("#advance-plans", Static).content)
        )
        assert "1 planned season(s) will be applied." in plans
        assert "Nothing planned for: Alys (companion)." in plans
        app.screen.query_one("#btn-advance", Button).press()
        assert await wait_until(
            pilot, lambda: workspace.saga.current_season == "Summer"
        )
        await pilot.pause()

        saga = storage.load_saga("test_saga")
        magus = saga.character("mag1")
        assert magus.abilities[0].xp == ability_xp(4) + 4
        assert [e.name for e in magus.diary] == ["Latin (+4 xp)"]
        assert saga.season_plans == []
        assert storage.backup_path("test_saga").exists()
        text = str(view.query_one("#char-season-content", Static).content)
        assert "Nothing planned for Summer 1220" in text


async def test_planning_and_the_diary_are_separate_tabs():
    """Planning sits just before the Diary (STORY-925); the Diary tab holds
    only the Diary, and its keys act on it."""
    saga = everything_saga()
    saga.characters[0].diary = [DiaryEntry(1219, "Winter", "Rested", activity="Other")]
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _open_season(pilot, app)
        view = app.screen._character_sheet_view
        tabbed = view.query_one(TabbedContent)
        tabs = [pane.id for pane in tabbed.query("TabPane")]
        assert tabs[-2:] == ["tab-planning", "tab-diary"]
        assert not view.query("#tab-diary #section-char-season")
        tabbed.active = "tab-diary"
        await wait_until(pilot, lambda: app.screen._active_section() == "tab-diary")
        await pilot.press("a")
        assert await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
        assert app.screen.title_text == "Add a Diary Entry"


async def test_a_grogs_planning_tab_says_they_update_yearly():
    saga = everything_saga()
    saga.characters.append(
        Character(id="grog1", name="Hob", type="grog", covenant_id="cov1")
    )
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await pilot.press("enter")
        await pilot.pause()
        saga = app.screen.saga
        grog = next(c for c in saga.characters if c.type == "grog")
        tree = app.screen.query_one("#nav-tree", Tree)
        tree.select_node(_find(tree, ("character", grog.id)))
        await wait_until(
            pilot,
            lambda: (
                app.screen._character_sheet_view is not None
                and app.screen._character_sheet_view.character is grog
            ),
        )
        view = app.screen._character_sheet_view
        await build_all_tabs(pilot, view)
        text = str(view.query_one("#char-season-content", Static).content)
        assert "updated once a year" in text


async def test_clear_a_plan_after_confirming():
    saga = everything_saga()
    seasons.set_plan(
        saga, SeasonPlan("mag1", 1220, "Spring", rules.OTHER, details="Tribunal")
    )
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _open_season(pilot, app)
        await pilot.press("A")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        await pilot.press("y")
        assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        await pilot.pause()
    assert storage.load_saga("test_saga").season_plans == []


def test_the_lab_planning_tab_shows_the_owners_season():
    saga = everything_saga()
    lab = saga.laboratories[0]
    text = strip_markup(seasons.lab_planning_text(saga, lab))
    assert text.splitlines()[0] == "Leandro: Spring 1220"
    assert "Nothing planned for Spring 1220. Plan it on Leandro's Planning tab." in text
    seasons.set_plan(
        saga, SeasonPlan("mag1", 1220, "Spring", rules.OTHER, details="Tribunal")
    )
    assert "Other: Tribunal" in strip_markup(seasons.lab_planning_text(saga, lab))
    lab.owner_id = None
    assert "No owner" in seasons.lab_planning_text(saga, lab)


async def test_lab_totals_live_on_the_laboratory_sheet():
    """STORY-925: the magus's sheet has no Laboratory tab; the laboratory
    sheet has a Lab Totals tab after Planning."""
    storage.save_saga(everything_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _open_season(pilot, app)
        view = app.screen._character_sheet_view
        assert not view.query("#tab-lab")
        tree = app.screen.query_one("#nav-tree", Tree)
        tree.select_node(_find(tree, ("laboratory", "lab1")))
        await wait_until(pilot, lambda: app.screen._laboratory_sheet_view is not None)
        lab_view = app.screen._laboratory_sheet_view
        await build_all_tabs(pilot, lab_view)
        tabs = [pane.id for pane in lab_view.query_one(TabbedContent).query("TabPane")]
        assert tabs[:2] == ["tab-lab-planning", "tab-lab-totals"]
        totals = str(lab_view.query_one("#lab-totals-content", Static).content)
        assert "Lab Totals for Leandro" in totals
        planning = strip_markup(
            str(lab_view.query_one("#lab-planning-content", Static).content)
        )
        assert planning.splitlines()[0] == "Leandro: Spring 1220"

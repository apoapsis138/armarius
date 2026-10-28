"""Season plans and advancing the season: the activities' rules
(rules.activities), applying a season (seasons), and the character sheet's
This Season / Diary tab and Advance Season in the workspace."""

import copy
import json
import random
from dataclasses import asdict

from support import build_all_tabs, everything_saga, strip_markup, wait_until
from textual.widgets import Button, Collapsible, Select, Static, TabbedContent, Tree

from ars_magica_manager import seasons, storage
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
    Wounds,
    XpAllocation,
)
from ars_magica_manager.rules import activities as rules
from ars_magica_manager.rules import apprentice_seasons as aps
from ars_magica_manager.rules import book_seasons as bs
from ars_magica_manager.rules import experiment
from ars_magica_manager.rules import laboratory_seasons as ls
from ars_magica_manager.rules import supplement_seasons as sup
from ars_magica_manager.rules.xp import ability_xp
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens import ConfirmScreen, FieldsDialog, WorkspaceScreen
from ars_magica_manager.tui.screens.widgets import section_stop


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
    # Only a scribe's copying is planned for a grog (DE p. 380).
    assert [a.key for a in rules.activities_for(grog)] == [
        bs.COPY_BOOK,
        bs.COPY_TEXTS,
    ]
    plan = _plan(grog, rules.OTHER, details="Drill")
    assert "Grogs aren't planned" in rules.problems(grog, plan)[0]


def test_supplement_activities_are_offered_only_with_their_book_in_play():
    """A supplement's season activities are in the menu only while the saga
    has that book in play; a plan's own activity stays, so editing it still
    shows it."""
    magus = _magus()
    every = {a.key for a in rules.activities_for(magus)}
    core = {a.key for a in rules.activities_for(magus, books={"DE"})}
    assert sup.ACTIVITIES and core < every
    for activity in sup.ACTIVITIES:
        if magus.type in activity.who:
            assert (activity.key in core) == (activity.book == "DE"), activity.key
    with_covenants = {
        a.key for a in rules.activities_for(magus, books={"DE", "Covenants"})
    }
    assert "inspeximus" in with_covenants - core
    kept = {a.key for a in rules.activities_for(magus, books={"DE"}, keep="inspeximus")}
    assert kept == core | {"inspeximus"}


def test_every_supplement_activity_names_a_known_book():
    from ars_magica_manager import sourcebooks

    for activity in sup.ACTIVITIES:
        assert activity.book in sourcebooks.SOURCEBOOKS, activity.key


def test_magi_and_companions_plan_every_activity_built_so_far():
    study = [rules.READ, rules.TAUGHT, rules.TEACH, rules.TRAINED]
    writing = [bs.WRITE_SUMMA, bs.WRITE_TRACTATUS, bs.COPY_BOOK, bs.TRANSLATE_BOOK]
    magus_only = [
        rules.VIS_STUDY,
        # The one lab work on the sheet, where it sits in the registry.
        ls.TAKE_OVER,
        *writing,
        bs.REWRITE_TEXTS,
        bs.COPY_TEXTS,
        bs.EDIT_FLORILEGIUM,
        bs.WRITE_TABLET,
    ]
    for character, extra in (
        (
            _magus(),
            [
                *magus_only,
                bs.TEACH_ABBREVIATIONS,
                aps.SEARCH,
                aps.OPEN_ARTS,
                aps.TEACH_VIRTUE,
                experiment.INTEGRATE,
                ls.NEW,
                ls.ASSIST,
            ],
        ),
        (_companion(), [*writing, bs.COPY_TEXTS, bs.EDIT_FLORILEGIUM, ls.ASSIST]),
    ):
        keys = [a.key for a in rules.activities_for(character)]
        assert keys == [
            rules.EXPOSURE,
            # Life on campaign (Lords of Men p. 102).
            rules.CAMPAIGNING,
            rules.PRACTICE,
            *study,
            *extra,
            rules.ADVENTURE,
            *[
                a.key
                for a in sup.ACTIVITIES
                if character.type in a.who and not a.retired
            ],
            rules.OTHER,
        ]
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
    assert "Alys" not in summary  # a non-player character
    saga.notify_npc_unplanned = True
    summary = strip_markup(seasons.advance_summary(saga))
    assert "Nothing planned for: Alys (companion: " in summary


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


def test_backup_is_kept_outside_the_saga_list():
    saga = _saga(_magus())
    storage.save_saga(saga)
    path = storage.backup_saga(saga)
    assert path.exists() and path.parent.name == "backups"
    assert storage.list_sagas() == ["s"]


def test_backups_rotate_keeping_the_last_five():
    """Each backup is kept as the newest and the older ones move back a
    place, up to BACKUPS_KEPT; nothing else is written."""
    saga = _saga(_magus())
    for year in range(1220, 1227):
        saga.current_year = year
        storage.backup_saga(saga)

    folder = storage.backup_path("s").parent
    assert sorted(p.name for p in folder.iterdir()) == [
        "s.1.json", "s.2.json", "s.3.json", "s.4.json", "s.json",
    ]  # fmt: skip
    years = [
        Saga.from_dict(
            json.loads(storage.backup_path("s", age).read_text("utf-8"))
        ).current_year
        for age in range(storage.BACKUPS_KEPT)
    ]
    assert years == [1226, 1225, 1224, 1223, 1222]
    assert storage.list_sagas() == []


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
    section_stop(view.query_one("#section-char-season", Collapsible)).focus()
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
        dialog._picked["activity"] = rules.PRACTICE
        dialog._react()
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
        assert "Alys" not in plans  # a non-player character takes the default
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
        await pilot.press("d")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        await pilot.press("y")
        assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        await pilot.pause()
    assert storage.load_saga("test_saga").season_plans == []


async def test_lab_totals_live_on_the_laboratory_sheet():
    """The magus's sheet has no Laboratory tab; the laboratory
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
        totals = str(
            lab_view.query_one("#section-lab-totals-grid-content", Static).content
        )
        assert "Leandro working here" in totals
        planning = strip_markup(
            str(lab_view.query_one("#lab-planning-heading", Static).content)
        )
        assert planning.startswith("Leandro's seasons")


# -- the covenant's Seasons tab ---------------------------------------


def test_seasons_lists_the_covenants_people_by_kind():
    saga = everything_saga()
    saga.characters += [
        Character(id="grog1", name="Hob", type="grog", covenant_id="cov1"),
        Character(id="myth1", name="Wode", type="mythic companion", covenant_id="cov1"),
    ]
    covenant = saga.covenants[0]
    seasons.set_plan(
        saga,
        SeasonPlan(
            "mag1", 1220, "Spring", rules.PRACTICE, [XpAllocation("ability:Latin")]
        ),
    )

    def rows(kind):
        return [
            strip_markup(label)
            for _, label in seasons.season_rows(saga, covenant, kind)
        ]

    # A heading of the year's seasons, then a row per person.
    assert rows("magus")[0].split()[:3] == ["Name", "Spring", "1220"]
    assert rows("magus")[1].split() == [
        "Leandro", "Practice", "nothing", "nothing", "nothing",
    ]  # fmt: skip
    assert rows("companion")[0].split()[-1] == "Worked"
    assert rows("companion")[1].split()[1:] == [
        "nothing", "nothing", "nothing", "nothing", "0", "of", "2",
    ]  # fmt: skip
    assert rows("companion")[2].startswith("Wode (Mythic)")
    assert rows("grog")[1].split()[1:] == ["yearly"]
    assert (
        seasons.season_title(saga, covenant, "magus", "Magi") == "Magi (1 of 1 planned)"
    )
    assert (
        seasons.season_title(saga, covenant, "companion", "Companions")
        == "Companions (0 of 2 planned)"
    )
    assert seasons.season_title(saga, covenant, "grog", "Grogs") == "Grogs (1)"


async def test_plan_a_season_from_the_covenant_seasons_tab():
    storage.save_saga(everything_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await pilot.press("enter")
        await pilot.pause()
        tree = app.screen.query_one("#nav-tree", Tree)
        tree.select_node(_find(tree, ("covenant", "cov1")))
        await wait_until(pilot, lambda: app.screen._covenant_sheet_view is not None)
        view = app.screen._covenant_sheet_view
        await wait_until(pilot, lambda: view.initial_tab_seen)
        view.query_one(TabbedContent).active = "tab-cov-seasons"
        # Let the tab's own focus (its first section, Magi) land first, or it
        # can arrive after ours and take 'e' to the wrong list.
        await wait_until(
            pilot, lambda: app.screen._active_section() == "section-cov-seasons-magus"
        )
        section_stop(
            view.query_one("#section-cov-seasons-companion", Collapsible)
        ).focus()
        await wait_until(
            pilot,
            lambda: app.screen._active_section() == "section-cov-seasons-companion",
        )
        workspace = app.screen
        await pilot.press("e")  # the first Companion is chosen: Alys
        assert await wait_until(pilot, lambda: app.screen is not workspace)
        assert await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
        dialog = app.screen
        assert dialog.title_text == "Plan Alys's Season (Spring 1220)"
        dialog._picked["activity"] = rules.OTHER
        dialog._react()
        await pilot.pause()
        from textual.widgets import TextArea

        dialog.query_one("#fld-details", TextArea).text = "Visiting family"
        dialog.query_one("#btn-save", Button).press()
        assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        await pilot.pause()
        rows = view.query_one("#cov-seasons-companion-list")
        text = " ".join(str(o.prompt) for o in rows.options)
        assert "Alys  Other" in text and "0 of 2" in text
    saga = storage.load_saga("test_saga")
    assert [p.details for p in saga.season_plans] == ["Visiting family"]


# -- season records ----------------------------------------------------


def test_a_seasons_record_lists_everyone_by_covenant():
    saga = everything_saga()
    seasons.set_plan(
        saga,
        SeasonPlan(
            "mag1", 1220, "Spring", rules.PRACTICE, [XpAllocation("ability:Latin")]
        ),
    )
    record = seasons.make_record(saga, seasons.resolve(saga))
    assert (record.year, record.season) == (1220, "Spring")
    assert [(r.name, r.activity, r.what, r.result) for r in record.lines] == [
        ("Leandro", "Practice", "Latin", "Latin +4 xp"),
        ("Alys", "", "", ""),
    ]
    assert seasons.record_label(record) == "Spring 1220 (2 people)"
    text = strip_markup(seasons.record_text(saga, record)).splitlines()
    assert text == [
        "Spring 1220",
        "",
        "Keep",
        "  Leandro: Practice: Latin -- Latin +4 xp",
        "  Alys: ☞ nothing planned",
    ]


def test_a_plan_that_cant_be_carried_out_is_recorded_as_such():
    saga = everything_saga()
    seasons.set_plan(
        saga,
        SeasonPlan("mag1", 1220, "Spring", rules.PRACTICE, [XpAllocation("art:Creo")]),
    )
    record = seasons.make_record(saga, seasons.resolve(saga))
    assert record.lines[0].result.startswith("not carried out: Arts can't be practised")


async def _advance(pilot, app):
    await pilot.press("enter")  # saga picker -> workspace
    await pilot.pause()
    workspace = app.screen
    await pilot.press("t")
    await pilot.pause()
    app.screen.query_one("#btn-advance", Button).press()
    assert await wait_until(
        pilot,
        lambda: (
            type(app.screen).__name__ == "SeasonSummaryScreen"
            and bool(app.screen.query("#summary-text"))
        ),
    )
    return workspace


async def test_advancing_shows_the_seasons_results_and_keeps_them():
    saga = everything_saga()
    seasons.set_plan(
        saga,
        SeasonPlan(
            "mag1", 1220, "Spring", rules.PRACTICE, [XpAllocation("ability:Latin")]
        ),
    )
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        workspace = await _advance(pilot, app)
        text = strip_markup(str(app.screen.query_one("#summary-text", Static).content))
        assert "Leandro: Practice: Latin -- Latin +4 xp" in text
        await pilot.press("enter")
        assert await wait_until(pilot, lambda: app.screen is workspace)
        tree = workspace.query_one("#nav-tree", Tree)
        node = _find(tree, ("seasons",))
        assert str(node.label) == "Seasons (1)"
        tree.select_node(node)
        assert await wait_until(
            pilot, lambda: bool(workspace.query("#season-record-text"))
        )
        shown = strip_markup(
            str(workspace.query_one("#season-record-text", Static).content)
        )
        assert shown.splitlines()[0] == "Spring 1220"
    assert len(storage.load_saga("test_saga").season_records) == 1


async def test_with_records_off_the_summary_shows_but_nothing_is_kept():
    saga = everything_saga()
    saga.keep_season_records = False
    seasons.set_plan(
        saga, SeasonPlan("mag1", 1220, "Spring", rules.OTHER, details="Rest")
    )
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _advance(pilot, app)
        note = str(app.screen.query_one("#summary-note", Static).content)
        assert "Season records are off" in note
    assert storage.load_saga("test_saga").season_records == []


async def test_a_season_with_nothing_planned_is_neither_summarised_nor_kept():
    from support import quiet

    storage.save_saga(quiet(everything_saga()))
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await pilot.press("enter")
        await pilot.pause()
        workspace = app.screen
        await pilot.press("t")
        await pilot.pause()
        app.screen.query_one("#btn-advance", Button).press()
        assert await wait_until(
            pilot, lambda: workspace.saga.current_season == "Summer"
        )
        await pilot.pause()
        assert app.screen is workspace
    assert storage.load_saga("test_saga").season_records == []


def test_finishing_a_winter_season_runs_the_year_end_in_order():
    """seasons.finish_season: back up before applying, apply the
    plans, then the year's end, the covenant's season and its Wealth, the
    record, then the new date -- without the workspace screen."""
    from ars_magica_manager.models import Covenant, IncomeSource

    magus = _magus()
    magus.covenant_id = "cov"
    magus.background.year_born = 1180
    saga = _saga(magus)
    saga.covenants = [Covenant(id="cov", saga_id="s", name="Keep")]
    saga.covenants[0].economics.income_sources = [IncomeSource("i", "Mill", income=40)]
    saga.keep_season_records = True
    saga.current_season = "Winter"
    plan = _plan(magus, rules.PRACTICE, "ability:Latin")
    plan.season = "Winter"
    seasons.set_plan(saga, plan)
    worked = seasons.resolve(saga, random.Random(1))

    backed_up: list[int] = []

    def backup(saga_) -> None:
        # Taken before anything is applied: Latin hasn't moved yet.
        backed_up.append(saga_.character("m").abilities[0].xp)

    done = seasons.finish_season(saga, worked, {}, random.Random(1), backup=backup)

    assert backed_up == [ability_xp(4)]
    assert [c.name for c in done.applied] == ["Tiberius"]
    assert magus.abilities[0].xp > ability_xp(4)
    assert [line.activity for line in done.year_end] == ["Aging"]
    assert saga.season_records == [done.record]
    assert done.record.lines[-len(done.year_end) :] == done.year_end
    assert [name for name, _ in done.added] == ["Keep"]
    assert (saga.current_season, saga.current_year) == ("Spring", 1221)


def test_finishing_a_season_with_nothing_planned_takes_no_backup():
    saga = _saga(_magus())
    calls: list[object] = []
    done = seasons.finish_season(saga, [], {}, random.Random(1), backup=calls.append)
    assert calls == [] and done.applied == [] and done.added == []
    assert (saga.current_season, saga.current_year) == ("Summer", 1220)
    assert saga.season_records == []


def test_every_activity_that_gives_experience_has_one_family():
    """rules.HANDLERS: each activity's checks and outcome come
    from exactly one family; one with none would fail only when planned."""
    gives_xp = {key for key, a in rules.ACTIVITIES.items() if a.gives_xp}
    assert gives_xp <= set(rules.HANDLERS)


def test_a_family_that_works_from_the_saga_says_so_without_one():
    magus = _magus()
    plan = _plan(magus, rules.READ)
    assert rules.problems(magus, plan) == [rules.NEEDS_SAGA]
    lab = _plan(magus, ls.ASSIST)  # assisting: not lab work itself
    assert rules.problems(magus, lab) == [rules.NEEDS_SAGA]


def test_independent_study_adds_to_the_adventure_before_its_split():
    magus = _magus()
    magus.virtues_flaws = [VirtueFlawInstance("vf_independent_study")]
    # 8 + 3 = 11 to split, at most 5 a subject (DE pp. 86, 377).
    split = _plan(
        magus,
        rules.ADVENTURE,
        ("ability:Latin", 5),
        ("art:Creo", 5),
        ("ability:Magic Theory", 1),
        source_quality=8,
    )
    assert rules.problems(magus, split) == []
    assert sum(xp for _, xp in _xp(rules.outcome(magus, split))) == 11
    short = _plan(
        magus, rules.ADVENTURE, ("ability:Latin", 5), ("art:Creo", 3), source_quality=8
    )
    assert any("Split all 11" in p for p in rules.problems(magus, short))


def test_wounds_halve_the_advancement_total_before_affinity():
    magus = _magus()
    magus.wounds = Wounds(heavy=1)  # -5
    magus.virtues_flaws = [
        VirtueFlawInstance("vf_affinity_with_ability", params={"ability": "Latin"})
    ]
    plan = _plan(magus, rules.PRACTICE, "ability:Latin", source_quality=4)
    # 4 halved to 2, then Affinity's x1.5 rounded up: 3.
    assert _xp(rules.outcome(magus, plan)) == [("ability:Latin", 3)]

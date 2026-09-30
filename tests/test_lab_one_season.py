"""One-season lab work (STORY-907): extracting vis, fixing an Arcane
Connection and Longevity Rituals, planned on the laboratory's Planning tab."""

from support import strip_markup, wait_until
from textual.widgets import Button, Input, Select, Static, Tree

from ars_magica_manager import laboratories, seasons, storage
from ars_magica_manager.app import ArsMagicaManagerApp
from ars_magica_manager.models import (
    Ability,
    ArcaneConnection,
    ArtScore,
    Character,
    Characteristics,
    Covenant,
    Laboratory,
    Saga,
    SeasonPlan,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import lab_seasons
from ars_magica_manager.rules.xp import ability_xp, art_xp
from ars_magica_manager.screens.invent_spell import InventSpellScreen


def _saga() -> Saga:
    covenant = Covenant(id="cov", saga_id="s", name="Keep")
    magus = Character(id="m", name="Tiberius", type="magus", covenant_id="cov")
    magus.characteristics = Characteristics(intelligence=2)
    magus.abilities = [Ability("Magic Theory", xp=ability_xp(3))]
    # CrVi 5 + 4 + 2 + 3 = 14; CrCo 5 + 3 + 2 + 3 = 13.
    magus.arts = {
        "creo": ArtScore(xp=art_xp(5)),
        "vim": ArtScore(xp=art_xp(4)),
        "corpus": ArtScore(xp=art_xp(3)),
    }
    magus.background.year_born = 1195  # 25: a ritual takes 5 pawns
    magus.raw_vis = {"creo": 8, "vim": 1}
    magus.assigned_lab_id = "lab"
    friend = Character(id="f", name="Banna", type="companion", covenant_id="cov")
    friend.background.year_born = 1200  # 20: 4 pawns
    lab = Laboratory(id="lab", covenant_id="cov", name="Tower", owner_id="m")
    return Saga(
        id="s",
        name="S",
        covenants=[covenant],
        characters=[magus, friend],
        laboratories=[lab],
    )


def _plan(activity, **kw):
    return SeasonPlan("m", 1220, "Spring", activity, lab_id="lab", **kw)


def _work(saga, plan):
    return lab_seasons.work(saga, saga.character("m"), plan)


def _run(saga):
    worked = seasons.resolve(saga)
    seasons.apply(saga, worked)
    return worked


def test_extracting_vis_gives_a_tenth_of_the_creo_vim_lab_total():
    saga = _saga()
    found, work = _work(saga, _plan(lab_seasons.EXTRACT, vis_from="laboratory"))
    assert found == [] and int(work.lab_total.total) == 14
    assert work.vis_gained == 2  # 14 / 10, rounded up
    seasons.plan_lab_work(saga, _plan(lab_seasons.EXTRACT, vis_from="laboratory"))
    (worked,) = _run(saga)
    assert saga.laboratories[0].raw_vis == {"vim": 2}
    assert [g.result.xp for g in worked.gains] == [2]  # Magic Theory Exposure
    entry = saga.laboratories[0].diary[-1]
    assert (entry.name, entry.activity) == ("Extract vis: Vim vis", "Extract Vis")
    assert entry.details == "Tiberius: Lab Total 14: 2 pawn(s) of Vim vis."


def test_vis_is_extracted_only_in_a_magic_aura():
    saga = _saga()
    saga.covenants[0].aura_realm = "Divine"
    found, _ = _work(saga, _plan(lab_seasons.EXTRACT))
    assert found == ["Vis is extracted only in a Magic aura; Tower's is Divine."]


def test_fixing_an_arcane_connection_takes_a_pawn_of_vim_and_marks_it_fixed():
    saga = _saga()
    lab = saga.laboratories[0]
    lab.arcane_connections = [
        ArcaneConnection("ac", "a lock of hair", lasts="until Summer 1222")
    ]
    found, _ = _work(saga, _plan(lab_seasons.FIX_AC))
    assert found[0].startswith("Choose the Arcane Connection to fix")
    plan = _plan(lab_seasons.FIX_AC, connection_id="ac", vis_from="laboratory")
    found, _ = _work(saga, plan)
    assert "the laboratory's raw vis has none" in found[0]
    seasons.plan_lab_work(saga, _plan(lab_seasons.FIX_AC, connection_id="ac"))
    _run(saga)
    assert saga.character("m").raw_vis == {"creo": 8}
    (connection,) = lab.arcane_connections
    assert (connection.fixed, connection.lasts, connection.fixed_season) == (
        True,
        "",
        "Spring",
    )
    assert lab.diary[-1].name == "Fix an Arcane Connection: a lock of hair"
    # A fixed one can't be fixed again.
    found, _ = _work(saga, _plan(lab_seasons.FIX_AC, connection_id="ac"))
    assert found == ["The Arcane Connection to a lock of hair is already fixed."]


def test_arcane_connections_are_listed_on_the_inventory_tab():
    lab = _saga().laboratories[0]
    lab.arcane_connections = [
        ArcaneConnection("a", "a lock of hair", lasts="until Summer 1222"),
        ArcaneConnection("b", "Banna's ring", fixed=True, source="her gift"),
    ]
    rows = [strip_markup(r) for _, r in laboratories.connection_rows(lab)]
    assert rows == [
        "a lock of hair  lasts until Summer 1222",
        "Banna's ring    fixed",
    ]
    info = strip_markup(laboratories.connection_info_text(lab, 1))
    assert info.splitlines()[:3] == [
        "Arcane Connection to Banna's ring",
        "Fixed (lasts indefinitely).",
        "From: her gift",
    ]


def test_a_longevity_ritual_gives_its_subject_an_aging_modifier():
    saga = _saga()
    plan = _plan(lab_seasons.LONGEVITY, vis_art="Creo")
    found, work = _work(saga, plan)
    assert found == [] and int(work.lab_total.total) == 13
    assert (work.longevity, work.vis_cost) == (3, {"Creo": 5})  # 13 / 5; 25 / 5
    seasons.plan_lab_work(saga, plan)
    _run(saga)
    magus = saga.character("m")
    assert (
        magus.aging.longevity_modifier,
        magus.aging.longevity_year,
        magus.aging.longevity_by,
    ) == (3, 1220, "Tiberius")
    assert magus.raw_vis == {"creo": 3, "vim": 1}


def test_extra_vis_adds_to_the_ritual_and_its_cost():
    saga = _saga()
    _, work = _work(saga, _plan(lab_seasons.LONGEVITY, vis_art="Creo", extra_vis=1))
    assert int(work.lab_total.total) == 14 and work.vis_cost == {"Creo": 6}


def test_a_ritual_needs_the_vis_within_the_limit():
    saga = _saga()
    found, _ = _work(saga, _plan(lab_seasons.LONGEVITY, vis_art="Creo", extra_vis=2))
    assert found == [
        "The ritual takes 7 pawns of vis; Tiberius can handle 6 in a season "
        "(twice Magic Theory)."
    ]
    found, _ = _work(saga, _plan(lab_seasons.LONGEVITY, vis_art="Vim"))
    assert found == ["The ritual takes 5 pawns of Vim vis; Tiberius's raw vis has 1."]
    saga.character("m").background.year_born = None
    found, _ = _work(saga, _plan(lab_seasons.LONGEVITY, vis_art="Creo"))
    assert found == ["Set Tiberius's Year Born: the ritual's vis is by age."]


def test_a_ritual_for_someone_else_needs_30_and_plans_their_season():
    saga = _saga()
    plan = _plan(lab_seasons.LONGEVITY, vis_art="Creo", subject_id="f")
    found, _ = _work(saga, plan)
    assert found == ["Lab Total 13: a Longevity Ritual for someone else needs 30."]
    plan = _plan(
        lab_seasons.LONGEVITY, vis_art="Creo", subject_id="f", other_modifier=20
    )
    found, work = _work(saga, plan)
    assert found == [] and work.longevity == 4  # mundane: 33 / 10, rounded up
    seasons.plan_lab_work(saga, plan)
    theirs = seasons.plan_for(saga, saga.character("f"), "Spring", 1220)
    assert theirs.activity == lab_seasons.LONGEVITY_SUBJECT
    # Clearing the ritual clears their season too.
    assert seasons.scheduled_with(saga, plan) == [plan, theirs]
    _run(saga)
    assert saga.character("f").aging.longevity_modifier == 4
    assert (
        saga.character("f")
        .diary[-1]
        .details.startswith("The subject of Tiberius's Longevity Ritual.")
    )


def test_the_subject_must_be_free_that_season():
    saga = _saga()
    seasons.set_plan(saga, SeasonPlan("f", 1220, "Spring", "other", details="Away"))
    plan = _plan(
        lab_seasons.LONGEVITY, vis_art="Creo", subject_id="f", other_modifier=20
    )
    found, _ = _work(saga, plan)
    assert found == [
        "Banna has other plans for Spring 1220: the subject spends the season "
        "with the magus."
    ]


def test_difficult_longevity_ritual_halves_the_lab_total():
    saga = _saga()
    saga.character("m").virtues_flaws = [
        VirtueFlawInstance(lab_seasons.DIFFICULT_LONGEVITY)
    ]
    _, work = _work(saga, _plan(lab_seasons.LONGEVITY, vis_art="Creo"))
    assert int(work.lab_total.total) == 6 and work.longevity == 2


def test_the_planning_tab_shows_one_season_work():
    saga = _saga()
    seasons.plan_lab_work(saga, _plan(lab_seasons.EXTRACT))
    rows = [
        strip_markup(r) for _, r in seasons.lab_queue_rows(saga, saga.laboratories[0])
    ]
    assert rows[0].startswith("Spring 1220")
    assert rows[0].endswith("Extract vis: Vim vis  +2 Vim")


def _find(tree, data):
    pending = [tree.root]
    while pending:
        node = pending.pop()
        if node.data == data:
            return node
        pending.extend(node.children)
    return None


async def test_the_lab_work_screen_plans_a_longevity_ritual():
    storage.save_saga(_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        await pilot.press("enter")
        await pilot.pause()
        ws = app.screen
        tree = ws.query_one("#nav-tree", Tree)
        tree.select_node(_find(tree, ("laboratory", "lab")))
        await wait_until(pilot, lambda: ws._laboratory_sheet_view is not None)
        view = ws._laboratory_sheet_view
        await wait_until(pilot, lambda: view.initial_tab_seen)
        await wait_until(pilot, lambda: ws._active_section() == "tab-lab-planning")
        await pilot.press("e")
        assert await wait_until(
            pilot, lambda: isinstance(app.screen, InventSpellScreen)
        )
        screen = app.screen
        await wait_until(pilot, lambda: bool(screen.query("#inv-activity")))
        screen.query_one("#inv-activity", Select).value = lab_seasons.LONGEVITY
        screen.query_one("#inv-vis-from", Select).value = "character"
        await pilot.pause()
        header = strip_markup(str(screen.query_one("#inv-header", Static).content))
        assert header.startswith("Longevity Ritual -- Tiberius")
        assert not screen.query_one("#inv-design").display
        when = strip_markup(str(screen.query_one("#inv-when", Static).content))
        assert "aging rolls -3 for Tiberius" in when
        screen.query_one("#inv-extra-vis", Input).value = "1"
        screen.query_one("#btn-save", Button).press()
        assert await wait_until(pilot, lambda: app.screen is ws)
        await pilot.pause()
    (plan,) = storage.load_saga("s").season_plans
    assert (plan.activity, plan.vis_art, plan.extra_vis, plan.vis_from) == (
        lab_seasons.LONGEVITY,
        "Creo",
        1,
        "character",
    )
    assert plan.design is None

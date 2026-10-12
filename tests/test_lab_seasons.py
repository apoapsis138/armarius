"""Lab work as seasons: inventing spells from scratch or from a
Lab Text on the laboratory's Planning tab, points over several seasons, and
what finishing gives."""

from support import strip_markup, wait_until
from textual.widgets import Button, Input, Select, Static, Tree

from ars_magica_manager import seasons, storage
from ars_magica_manager.models import (
    Ability,
    ArtScore,
    Book,
    Character,
    Characteristics,
    Covenant,
    KnownSpell,
    Laboratory,
    Saga,
    SeasonPlan,
    Spell,
    SpellDesign,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import activities as rules
from ars_magica_manager.rules import lab_seasons
from ars_magica_manager.rules.xp import ability_xp, art_xp
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens.invent_spell import OTHER, InventSpellScreen


def _saga() -> Saga:
    covenant = Covenant(id="cov", saga_id="s", name="Keep")
    magus = Character(id="m", name="Tiberius", type="magus", covenant_id="cov")
    magus.characteristics = Characteristics(intelligence=2)
    magus.abilities = [Ability("Magic Theory", xp=ability_xp(3))]
    # Creo 5, Ignem 5, Rego 2: CrIg Lab Total 5 + 5 + 2 + 3 = 15.
    magus.arts = {
        "creo": ArtScore(xp=art_xp(5)),
        "ignem": ArtScore(xp=art_xp(5)),
        "rego": ArtScore(xp=art_xp(2)),
    }
    magus.assigned_lab_id = "lab"
    lab = Laboratory(id="lab", covenant_id="cov", name="Tower", owner_id="m")
    saga = Saga(
        id="s", name="S", covenants=[covenant], characters=[magus], laboratories=[lab]
    )
    saga.spells = [
        Spell("bolt", "Bolt", "Creo", "Ignem", level=10),
        Spell("spark", "Spark", "Creo", "Ignem", level=5),
        Spell("guided", "Guided Bolt", "Creo", "Ignem", level=10, requisites=["Rego"]),
        Spell("text-spell", "Warm Hands", "Creo", "Ignem", level=15),
    ]
    saga.books = [
        Book(
            "text",
            "Lab Text: Warm Hands",
            "Lab Text",
            owner_kind="covenant",
            owner_id="cov",
            spell_id="text-spell",
        )
    ]
    return saga


def _plan(spell_id=None, activity=lab_seasons.INVENT, season="Spring", **kw):
    return SeasonPlan(
        "m", 1220, season, activity, lab_id="lab", spell_id=spell_id, **kw
    )


def _work(saga, plan):
    return lab_seasons.work(saga, saga.character("m"), plan)


def test_lab_work_is_planned_only_on_the_laboratory():
    magus = _saga().character("m")
    sheet = [a.key for a in rules.activities_for(magus)]
    lab = [a.key for a in rules.activities_for(magus, lab=True)]
    assert lab_seasons.INVENT not in sheet and rules.READ in sheet
    assert lab == list(lab_seasons.LAB_ACTIVITIES)


def test_inventing_adds_lab_total_minus_level_points_a_season():
    saga = _saga()
    found, work = _work(saga, _plan("bolt"))
    assert found == []
    assert int(work.lab_total.total) == 15
    assert (work.points_gained, work.points_after, work.finished) == (5, 5, False)
    assert lab_seasons.seasons_left(work) == 1


def test_twice_the_level_invents_in_one_season():
    _, work = _work(_saga(), _plan("spark"))
    assert work.points_gained == 10 and work.finished


def test_the_lab_total_must_be_above_the_level():
    saga = _saga()
    saga.spells[0].level = 15
    found, _ = _work(saga, _plan("bolt"))
    assert "Lab Total 15 isn't above Bolt's level 15" in found[0]


def test_a_similar_spell_adds_its_magnitude():
    saga = _saga()
    saga.character("m").spells_known = [KnownSpell("spark")]
    _, work = _work(saga, _plan("bolt", similar_spell_id="spark"))
    assert int(work.lab_total.total) == 16  # + magnitude 1


def test_a_requisite_counts_the_lower_art():
    _, work = _work(_saga(), _plan("guided"))
    assert int(work.lab_total.total) == 12  # Rego 2 in place of Creo 5


def test_days_away_lower_or_rule_out_lab_work():
    saga = _saga()
    _, ten = _work(saga, _plan("bolt", days_away=10))
    assert int(ten.lab_total.total) == 15
    found, _ = _work(saga, _plan("spark", days_away=12))
    assert "Lab Total 1 isn't above" in found[0]  # 15 - 14
    found, _ = _work(saga, _plan("bolt", days_away=21))
    assert "no lab work is possible" in found[0]


def test_a_lab_text_takes_one_season_if_the_total_reaches_its_level():
    saga = _saga()
    found, work = _work(saga, _plan(activity=lab_seasons.LAB_TEXT, book_id="text"))
    assert found == [] and work.finished  # Lab Total 15 >= level 15
    saga.character("m").arts["creo"] = ArtScore(xp=art_xp(4))
    found, _ = _work(saga, _plan(activity=lab_seasons.LAB_TEXT, book_id="text"))
    assert "can't be used yet" in found[0]


def test_only_the_labs_owner_works_in_it():
    saga = _saga()
    saga.laboratories[0].owner_id = None
    found, _ = _work(saga, _plan("bolt"))
    assert found == ["Tiberius doesn't work in Tower."]


def test_planning_an_invention_plans_the_seasons_it_will_need():
    saga = _saga()
    added = seasons.plan_lab_work(saga, _plan("bolt"))
    assert [(p.season, p.year) for p in added] == [("Summer", 1220)]
    rows = [
        strip_markup(r) for _, r in seasons.lab_queue_rows(saga, saga.laboratories[0])
    ]
    # One row for the whole invention, with the seasons it spans.
    assert rows[0].startswith("Spring 1220 - Summer 1220  Invent a spell: Bolt")
    assert rows[0].endswith("invented")
    assert rows[1].startswith("Autumn 1220") and rows[1].endswith("nothing planned")


def test_replanning_an_invention_replaces_the_seasons_planned_to_continue_it():
    saga = _saga()
    seasons.plan_lab_work(saga, _plan("bolt"))
    seasons.plan_lab_work(saga, _plan("bolt", days_away=21))  # can't work now
    assert [p.season for p in saga.season_plans] == ["Spring"]


def test_clearing_an_invention_clears_every_season_it_spans():
    saga = _saga()
    seasons.plan_lab_work(saga, _plan("bolt"))
    first = seasons.plan_for(saga, saga.character("m"), "Spring", 1220)
    assert [p.season for p in seasons.scheduled_with(saga, first)] == [
        "Spring",
        "Summer",
    ]


def test_lab_options_add_to_the_lab_total():
    saga = _saga()
    magus = saga.character("m")
    magus.virtues_flaws = [VirtueFlawInstance("vf_minor_magical_focus")]
    magus.abilities[0].specialty = "Inventing spells"
    _, work = _work(
        saga, _plan("bolt", focus=True, theory_specialty=True, other_modifier=2)
    )
    # 15 + Focus 5 (the lower Art again) + Specialty 1 + Other 2.
    assert int(work.lab_total.total) == 23


def _design(**kw):
    values = {
        "key": "k",
        "name": "Hot Ward",
        "technique": "Creo",
        "form": "Ignem",
        "base_level": 5,
        "range": "Touch",
        "duration": "Momentary",
        "target": "Individual",
    }
    return SpellDesign(**(values | kw))


def test_a_design_is_invented_at_the_level_its_parameters_give():
    saga = _saga()
    _, work = _work(saga, _plan(design=_design()))
    assert work.level == 10  # base 5, Touch +1 magnitude
    found, _ = _work(saga, _plan(design=_design(name="")))
    assert found == ["Name the spell."]


def test_a_finished_design_becomes_the_maguss_own_spell():
    saga = _saga()
    seasons.plan_lab_work(saga, _plan(design=_design(base_level=4, range="Personal")))
    seasons.apply(saga, seasons.resolve(saga))
    magus = saga.character("m")
    (mine,) = magus.invented_spells
    assert (mine.name, mine.level, mine.range, mine.source) == (
        "Hot Ward",
        4,
        "Personal",
        "Invented",
    )
    assert [k.spell_id for k in magus.spells_known] == [mine.id]
    assert saga.books[-1].spell_id == mine.id


def test_an_unchanged_design_invents_the_spell_it_started_from():
    saga = _saga()
    saga.spells.append(
        Spell(
            "ward",
            "Hot Ward",
            "Creo",
            "Ignem",
            level=4,
            base_level=4,
            range="Personal",
            duration="Momentary",
            target="Individual",
        )
    )
    design = _design(base_level=4, range="Personal", source_spell_id="ward")
    seasons.plan_lab_work(saga, _plan(design=design))
    seasons.apply(saga, seasons.resolve(saga))
    magus = saga.character("m")
    assert magus.invented_spells == []
    assert [k.spell_id for k in magus.spells_known] == ["ward"]


def test_two_seasons_of_invention_give_the_spell_and_a_lab_text():
    saga = _saga()
    seasons.plan_lab_work(saga, _plan("bolt"))
    seasons.apply(saga, seasons.resolve(saga))
    assert [(p.spell_id, p.points) for p in saga.lab_projects] == [("bolt", 5)]
    magus = saga.character("m")
    assert magus.abilities[0].xp == ability_xp(3) + 2  # Magic Theory Exposure
    saga.current_season = "Summer"
    seasons.apply(saga, seasons.resolve(saga))
    assert [k.spell_id for k in magus.spells_known] == ["bolt"]
    assert saga.lab_projects == []
    text = saga.books[-1]
    assert (text.type, text.spell_id, text.owner_kind, text.owner_id) == (
        "Lab Text",
        "bolt",
        "laboratory",
        "lab",
    )
    diary = saga.laboratories[0].diary
    assert [d.season for d in diary] == ["Spring", "Summer"]
    assert diary[-1].details.endswith("A Lab Text was written.")


def test_an_unfinished_invention_is_planned_again_next_season():
    saga = _saga()
    seasons.set_plan(saga, _plan("bolt"))  # only this season
    seasons.apply(saga, seasons.resolve(saga))
    assert [(p.season, p.spell_id) for p in saga.season_plans] == [("Summer", "bolt")]


def test_the_character_sheet_shows_a_lab_plan_as_lab_work():
    saga = _saga()
    seasons.set_plan(saga, _plan("bolt"))
    text = strip_markup(seasons.plan_text(saga, saga.character("m")))
    assert "Invent a spell: Bolt (CrIg 10)" in text
    assert "Lab work, planned on Tower's Planning tab." in text


def _find(tree, data):
    pending = [tree.root]
    while pending:
        node = pending.pop()
        if node.data == data:
            return node
        pending.extend(node.children)
    return None


async def _open_invent(pilot, app, *, key="e"):
    ws = app.screen
    tree = ws.query_one("#nav-tree", Tree)
    tree.select_node(_find(tree, ("laboratory", "lab")))
    await wait_until(pilot, lambda: ws._laboratory_sheet_view is not None)
    view = ws._laboratory_sheet_view
    await wait_until(pilot, lambda: view.initial_tab_seen)
    await wait_until(pilot, lambda: ws._active_section() == "tab-lab-planning")
    await pilot.press(key)
    assert await wait_until(pilot, lambda: isinstance(app.screen, InventSpellScreen))
    screen = app.screen
    await wait_until(pilot, lambda: bool(screen.query("#inv-name")))
    await pilot.pause()
    return ws, screen


def _text(screen, selector):
    return strip_markup(str(screen.query_one(selector, Static).content))


async def test_e_on_the_lab_planning_tab_invents_a_spell_started_from_one():
    saga = _saga()
    saga.spells.append(
        Spell(
            "ward",
            "Hot Ward",
            "Creo",
            "Ignem",
            level=5,
            base_level=5,
            range="Personal",
            duration="Momentary",
            target="Individual",
        )
    )
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await pilot.press("enter")
        await pilot.pause()
        ws, screen = await _open_invent(pilot, app)
        # A free season opens with no lab work chosen.
        assert screen.query_one("#inv-activity", Select).value == Select.NULL
        assert (
            _text(screen, "#inv-header") == "Lab work -- Tiberius in Tower, Spring 1220"
        )
        assert not screen.query_one("#inv-design").display
        screen.query_one("#btn-save", Button).press()
        await pilot.pause()
        assert _text(screen, "#inv-error") == "Choose the lab work."
        screen.query_one("#inv-activity", Select).value = lab_seasons.INVENT
        await pilot.pause()
        header = _text(screen, "#inv-header")
        assert header == "Invent a spell -- Tiberius in Tower, Spring 1220"
        screen._start_from("ward")
        await pilot.pause()
        assert screen.query_one("#inv-name", Input).value == "Hot Ward"
        assert _text(screen, "#inv-level").startswith("Level 5")
        # Changing a parameter changes the level, and so the seasons needed.
        screen.query_one("#inv-range", Select).value = "Voice"
        screen.query_one("#inv-name", Input).value = "Distant Ward"
        await pilot.pause()
        assert _text(screen, "#inv-level").startswith("Level 15")
        assert "isn't above" in _text(screen, "#inv-error")
        screen.query_one("#inv-range", Select).value = "Touch"
        await pilot.pause()
        assert "Invented Summer 1220 (projected: 2 seasons)" in _text(
            screen, "#inv-when"
        )
        screen.query_one("#btn-save", Button).press()
        assert await wait_until(pilot, lambda: app.screen is ws)
        await pilot.pause()
    saved = storage.load_saga("s")
    assert [(p.season, p.design.name, p.design.range) for p in saved.season_plans] == [
        ("Spring", "Distant Ward", "Touch"),
        ("Summer", "Distant Ward", "Touch"),
    ]


async def test_reset_and_new_spell_clear_the_form_without_closing_it():
    storage.save_saga(_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await pilot.press("enter")
        await pilot.pause()
        _, screen = await _open_invent(pilot, app, key="a")  # a new spell
        screen._start_from("bolt")
        await pilot.pause()
        assert screen.query_one("#inv-name", Input).value == "Bolt"
        screen.query_one("#btn-reset", Button).press()
        await pilot.pause()
        assert screen.query_one("#inv-name", Input).value == ""
        assert app.screen is screen
        screen._start_from("bolt")
        await pilot.pause()
        screen.query_one("#inv-new", Button).press()
        await pilot.pause()
        assert screen.query_one("#inv-name", Input).value == ""
        screen.query_one("#btn-save", Button).press()
        await pilot.pause()
        assert _text(screen, "#inv-error") == "Name the spell."
        assert app.screen is screen


async def test_the_invent_spell_screen_offers_parameters_from_virtues():
    saga = _saga()
    saga.character("m").virtues_flaws = [VirtueFlawInstance("vf_spell_timing")]
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        await pilot.press("enter")
        await pilot.pause()
        _, screen = await _open_invent(pilot, app, key="a")
        durations = [v for _, v in screen.parameter_options["duration"]]
        assert "Held" in durations and durations[-1] == OTHER
        ranges = [v for _, v in screen.parameter_options["range"]]
        assert "Adelphixis" not in ranges
        # Everything that matters fits a 120x45 terminal.
        for selector in ("#inv-dialog", "#inv-buttons"):
            region = screen.query_one(selector).region
            assert region.right <= 120 and region.bottom <= 45, selector

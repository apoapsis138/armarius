"""Help: the help files are well formed, every tab and section
of every sheet has help, and ? / F1 open Help on what has focus."""

import pytest
from support import NODES, build_all_tabs, everything_saga, screen_lines, wait_until
from textual.widgets import Markdown, OptionList, TabbedContent, TextArea, Tree

from ars_magica_manager import __version__, staged_projects, storage
from ars_magica_manager import help_text as ht
from ars_magica_manager.models import (
    SKETCH,
    Covenant,
    DeepCover,
    HermeticProject,
    Marriage,
    Tribunal,
)
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens import SelectableList, WorkspaceScreen
from ars_magica_manager.tui.screens.creation_worksheet import CreationWorksheetScreen
from ars_magica_manager.tui.screens.help import HelpScreen, page_chunks, whats_new_text
from ars_magica_manager.tui.screens.invent_spell import InventSpellScreen
from ars_magica_manager.tui.screens.prompts import AdvanceSeasonScreen
from ars_magica_manager.tui.screens.saga_picker import SagaPickerScreen
from ars_magica_manager.tui.screens.season_records import SeasonSummaryScreen
from ars_magica_manager.tui.screens.workspace.base import _HELP_PAGES

BOOK = ht.load(ht.TUI)
#: The help as the desktop shows it.
GUI_BOOK = ht.load(ht.GUI)

#: The process dialogs with a page of their own (help_id); the forms
#: built by functions set theirs on the instance.
DIALOG_PAGES = {
    *(
        cls.help_id
        for cls in (
            InventSpellScreen,
            AdvanceSeasonScreen,
            SeasonSummaryScreen,
            CreationWorksheetScreen,
        )
    ),
    "plan-season",
    "grog-year",
    "artist-career",
    "scholar-career",
    # The core's steps that name their page (commands.Form/Choose.help_id).
    "import-data",
    "import-spells",
    "import-pack",
    "battle-event",
    "disputatio",
    "travel",
    "labor-from-story",
    "merchant-investment",
    "grog-discipline",
    "grog-pension",
    "craft-magic",
    "agent-task-resolve",
    "sell-finished-goods",
    "ligature",
    "apothecary-store",
    "theban-customs",
    "confidence-through-sin",
    "infernal-influence",
    "ars-goetia",
    "philosophic-alchemy",
    "tmre-divination",
    "tmre-astrology",
    "house-acclaim",
    "reputation-roll",
    "spirits-and-names",
    "dream-working",
    "hermetic-sacrifice",
    "turbulence",
    "gauntlet",
    "lose-the-gift",
    "learn-cantation",
    "ars-fabulosa",
    "faerie-bargain",
    "faerie-offer",
    "cast-in-lacuna",
    "pilgrimage-more",
    "holy-influence",
    "devotion",
    "verditius-hubris",
    "mystic-path",
    "spiritual-path",
    "monistic-revelation",
    "gods-aid",
    "font-of-knowledge",
    "commanding-aura",
    "vf-change",
    "overcome-trap",
    "land-shaping",
    "invent-spell-guideline",
    "great-library-search",
    "great-library-contribute",
    "open-tunnel",
    "petition-church",
    "canon-case",
    "perform-exorcism",
    "edit-holy-orders",
    "arrange-marriage",
    "end-marriage",
    "follow-avenue",
    "change-path",
    "circulate-text",
    "draft-charter",
    "seek-loophole",
}

#: The sample saga's nodes, and the Grand Tribunal the help test adds.
HELP_NODES = {**NODES, "grand_tribunal": ("tribunal", "grand")}

#: The sheets whose tabs and sections need help, by tree node.
SHEETS = {
    "character": "_character_sheet_view",
    "covenant": "_covenant_sheet_view",
    "laboratory": "_laboratory_sheet_view",
    "familiar": "_familiar_sheet_view",
    "saga_content": "_saga_content_view",
    "tribunal": "_tribunal_sheet_view",
    "theban_tribunal": "_tribunal_sheet_view",
    "normandy_tribunal": "_tribunal_sheet_view",
    "transylvania_tribunal": "_tribunal_sheet_view",
    "hibernia_tribunal": "_tribunal_sheet_view",
    "grand_tribunal": "_tribunal_sheet_view",
    "region": "_region_sheet_view",
    "neighbour": "_neighbour_sheet_view",
    "town": "_neighbour_sheet_view",
    "church": "_neighbour_sheet_view",
    "university": "_neighbour_sheet_view",
    "faction": "_neighbour_sheet_view",
    "threat": "_neighbour_sheet_view",
    "place": "_neighbour_sheet_view",
    "seasons": "_seasons_view",
    "bestiary": "_bestiary_view",
    "creature": "_creature_sheet_view",
    "conflicts": "_conflicts_view",
}


@pytest.mark.parametrize("book", [BOOK, GUI_BOOK], ids=ht.FRONT_ENDS)
def test_help_files_load_and_every_link_leads_somewhere(book):
    for page, targets in book.links().items():
        missing = targets - book.topics.keys()
        assert not missing, f"{page} links to {missing}"


@pytest.mark.parametrize("book", [BOOK, GUI_BOOK], ids=ht.FRONT_ENDS)
def test_every_go_there_link_opens_a_tab_or_section(book):
    for page, targets in book.go_links().items():
        wrong = {t for t in targets if not book.is_place(t)}
        assert not wrong, f"{page}'s Go there links to {wrong}"


def test_go_there_says_where_a_place_is():
    assert BOOK.not_here("section-arts") == (
        "The Magical Arts isn't on what Help was opened from. "
        "It is on the Character sheet."
    )
    assert BOOK.not_here("section-cr-powers").endswith("It is on a creature.")
    assert BOOK.not_here("keys") == "There's no place to go to for this topic."


@pytest.mark.parametrize("book", [BOOK, GUI_BOOK], ids=ht.FRONT_ENDS)
def test_headings_on_a_page_are_unique(book):
    """Help scrolls to a topic by its heading, so none may repeat on a
    page."""
    for page in book.pages.values():
        titles = [book.topics[t].title for t in page.topics]
        assert len(titles) == len(set(titles)), page.id


@pytest.mark.parametrize("book", [BOOK, GUI_BOOK], ids=ht.FRONT_ENDS)
def test_no_front_end_marker_is_left_on_a_page(book):
    for page in book.pages.values():
        assert "<!-- tui" not in page.text and "<!-- gui" not in page.text, page.id
        assert "<!-- /" not in page.text, page.id


def test_each_front_end_has_its_own_workspace_and_keys():
    for topic_id in ("workspace", "keys"):
        assert BOOK.topics[topic_id].front_end == ht.TUI
        assert GUI_BOOK.topics[topic_id].front_end == ht.GUI
    assert "navigation tree" in BOOK.pages["workspace"].text
    assert "navigation tree" not in GUI_BOOK.pages["workspace"].text


def test_a_topic_for_one_front_end_is_left_out_of_the_other():
    text = (
        "# Shared\n<!-- help: shared -->\nBoth.\n<!-- tui -->\nPress `e`.\n"
        "<!-- /tui -->\n<!-- gui -->\nClick Edit.\n<!-- /gui -->\nAfter.\n"
        "# Screen\n<!-- help: screen; tui -->\nThe tree.\n"
        "### Keys\n<!-- help: screen-keys -->\nArrows.\n"
        "# Screen\n<!-- help: screen; gui -->\nThe pages.\n"
    )
    tui = ht.parse("x.md", text, ht.TUI)
    gui = ht.parse("x.md", text, ht.GUI)
    assert [(t.id, t.front_end) for t in tui] == [
        ("shared", None),
        ("screen", ht.TUI),
        ("screen-keys", ht.TUI),
    ]
    assert [(t.id, t.front_end) for t in gui] == [
        ("shared", None),
        ("screen", ht.GUI),
    ]
    assert tui[0].text == "# Shared\nBoth.\nPress `e`.\nAfter.\n"
    assert gui[0].text == "# Shared\nBoth.\nClick Edit.\nAfter.\n"
    assert gui[1].text == "# Screen\nThe pages.\n"


@pytest.mark.parametrize(
    ("text", "error"),
    [
        ("# A\n<!-- help: a; web -->\n", "not a front-end"),
        ("# A\n<!-- help: a -->\n<!-- tui -->\nx\n", "never closed"),
        ("# A\n<!-- help: a -->\n<!-- /gui -->\n", "doesn't match"),
        ("# A\n<!-- help: a -->\n<!-- tui -->\n<!-- /gui -->\n", "doesn't match"),
        ("# A\n<!-- help: a -->\n<!-- gui -->\n### B\n<!-- /gui -->\n", "inside"),
        ("# A\n<!-- help: a; gui -->\n### B\n<!-- help: b; tui -->\n", "its page"),
        ("# A\n<!-- help: a -->\n<!-- tui -->\nx\n<!-- /tui --> y\n", "own"),
    ],
)
def test_a_misused_front_end_marker_is_refused(text, error):
    with pytest.raises(ht.HelpError, match=error):
        ht.parse("x.md", text, ht.GUI)


def test_a_malformed_file_is_refused(tmp_path):
    (tmp_path / "a.md").write_text("# Page\nno id\n", encoding="utf-8")
    with pytest.raises(ht.HelpError, match="no help id"):
        ht.load(ht.TUI, tmp_path)
    (tmp_path / "a.md").write_text("# A\n<!-- help: x -->\n", encoding="utf-8")
    (tmp_path / "b.md").write_text("# B\n<!-- help: x -->\n", encoding="utf-8")
    with pytest.raises(ht.HelpError, match="also in"):
        ht.load(ht.TUI, tmp_path)
    # Once for each front-end is allowed.
    (tmp_path / "a.md").write_text("# A\n<!-- help: x; tui -->\n", encoding="utf-8")
    (tmp_path / "b.md").write_text("# B\n<!-- help: x; gui -->\n", encoding="utf-8")
    assert ht.load(ht.GUI, tmp_path).topics["x"].title == "B"


def test_parse_puts_level_three_topics_on_the_page_above():
    topics = ht.parse(
        "x.md",
        "# Sheet\n<!-- help: sheet -->\nIntro.\n### Top\n<!-- help: top -->\n"
        "## Tab\n<!-- help: tab -->\nText.\n### Part\n<!-- help: part -->\nMore.\n",
        ht.TUI,
    )
    assert [(t.id, t.page) for t in topics] == [
        ("sheet", "sheet"),
        ("top", "sheet"),
        ("tab", "tab"),
        ("part", "tab"),
    ]
    assert "<!--" not in ht.display_text(topics[3].text)


def test_every_tree_node_and_process_dialog_has_a_page():
    wanted = {
        *_HELP_PAGES.values(),
        *DIALOG_PAGES,
        "workspace",
        "saga-picker",
        "title-page",
        "keys",
    }
    assert not wanted - BOOK.pages.keys()


def test_search_finds_titles_before_text():
    found = BOOK.search("lab totals")
    assert found[0].id == "tab-lab-totals"
    assert len(BOOK.search("")) == len(BOOK.topics)


async def test_every_tab_and_section_has_help():
    """The coverage rule: a tab or section without help fails
    here, and so does help for one that no longer exists."""
    saga = everything_saga()
    # The Church tab, the Projects tab and The Enigma show only once the record has
    # something for them.
    next(
        c for c in saga.characters if c.id == NODES["character"][1]
    ).church.grade = "Doorkeeper"
    # The Enigma tab shows only for a magus of House Criamon.
    next(
        c for c in saga.characters if c.id == NODES["character"][1]
    ).hermetic.house = "house_criamon"
    # Covers and Marriages show once the character has one.
    magus = next(c for c in saga.characters if c.id == NODES["character"][1])
    magus.covers.append(DeepCover("Reynard", role="a mercenary"))
    magus.hermetic.parens = "Prudentius"  # Lineage shows with a parens
    saga.marriages.append(Marriage(bride="Adela", groom_ref="character:" + magus.id))
    next(
        c for c in saga.covenants if c.id == NODES["covenant"][1]
    ).hermetic_projects = [
        HermeticProject(id="project-tower", name="The Tower"),
        HermeticProject(id="project-menagerie", name="The Menagerie", kind="Menagerie"),
        HermeticProject(
            id="project-city",
            name="The Burning City",
            kind="Burning City",
            stages=staged_projects.seed("Burning City"),
        ),
    ]
    # A sketch's sheet has tabs of its own: the companion is drawn as one,
    # and a sketch covenant is added.
    sketch = next(c for c in saga.characters if c.id != NODES["character"][1])
    sketch.detail = SKETCH
    saga.covenants.append(
        Covenant(
            id="sketch_cov",
            saga_id=saga.id,
            name="Fengheld",
            detail=SKETCH,
            played=False,
        )
    )
    # The Grand Tribunal's customs have a tab of their own.
    saga.tribunals.append(
        Tribunal(id="grand", name="The Grand Tribunal", package="grand")
    )
    extra = {
        ("character", sketch.id): "_character_sheet_view",
        ("covenant", "sketch_cov"): "_covenant_sheet_view",
    }
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    on_sheets: set[str] = set()
    async with app.run_test(size=(140, 60)) as pilot:
        await pilot.press("enter")
        assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        workspace = app.screen
        tree = workspace.query_one("#nav-tree", Tree)
        for kind, attr in SHEETS.items():
            node = _node(tree, HELP_NODES[kind])
            before = getattr(workspace, attr)
            tree.select_node(node)
            assert await wait_until(
                pilot,
                lambda attr=attr, before=before: (
                    getattr(workspace, attr) not in (None, before)
                ),
            )
            view = getattr(workspace, attr)
            await build_all_tabs(pilot, view)
            on_sheets |= {w.id for w in view.query("Collapsible, TabPane") if w.id}
            # Showing the Menagerie, then the Burning City, rebuilds the
            # Projects tab with their sections in place of the tower's.
            for shown in (1, 2) if kind == "covenant" else ():
                rows = view.query_one("#cov-projects-list", SelectableList)
                rows.select_data_index(shown)
                assert await wait_until(
                    pilot,
                    lambda rows=rows, shown=shown: rows.selected_data_index == shown,
                )
                workspace.action_show_project()
                assert await wait_until(
                    pilot,
                    lambda attr=attr, view=view: getattr(workspace, attr) is not view,
                )
                view = getattr(workspace, attr)
                await build_all_tabs(pilot, view)
                on_sheets |= {w.id for w in view.query("Collapsible, TabPane") if w.id}
        for (kind, record_id), attr in extra.items():
            tree.select_node(_node(tree, (kind, record_id)))
            assert await wait_until(
                pilot,
                lambda attr=attr, record_id=record_id: (
                    (view := getattr(workspace, attr)) is not None
                    and view.creation_record.id == record_id
                ),
            )
            view = getattr(workspace, attr)
            await build_all_tabs(pilot, view)
            on_sheets |= {w.id for w in view.query("Collapsible, TabPane") if w.id}
    missing = {i for i in on_sheets if ht.shared_topic(i) not in BOOK.topics}
    assert not missing, f"no help for {sorted(missing)}"
    stale = {
        t
        for t in BOOK.topics
        if t.startswith(("section-", "tab-")) and t not in on_sheets
    }
    assert not stale, f"help for what no sheet has: {sorted(stale)}"


def _node(tree, data):
    stack = [tree.root]
    while stack:
        node = stack.pop()
        if node.data == data:
            return node
        stack.extend(node.children)
    raise AssertionError(data)


async def _workspace(pilot, app) -> WorkspaceScreen:
    await pilot.press("enter")
    assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
    return app.screen


def _listed(app) -> list[str]:
    topics = app.screen.query_one("#help-topics", OptionList)
    return [
        str(topics.get_option_at_index(i).id or "") for i in range(topics.option_count)
    ]


async def test_question_mark_opens_help_on_the_focused_section():
    storage.save_saga(everything_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        workspace = await _workspace(pilot, app)
        tree = workspace.query_one("#nav-tree", Tree)
        tree.select_node(_node(tree, NODES["character"]))
        assert await wait_until(pilot, lambda: workspace._character_sheet_view)
        view = workspace._character_sheet_view
        await build_all_tabs(pilot, view)
        view.query_one(TabbedContent).active = "tab-hermetic"
        await pilot.pause()
        view.query_one("#section-arts").focus_section()
        await wait_until(pilot, lambda: workspace._active_section() == "section-arts")

        await pilot.press("question_mark")
        assert await wait_until(pilot, lambda: isinstance(app.screen, HelpScreen))
        help_screen = app.screen
        assert await wait_until(pilot, lambda: help_screen.topic_id == "section-arts")
        here = [i for i in _listed(app) if i.startswith("here:")]
        assert here == [
            "here:section-arts",
            "here:tab-hermetic",
            "here:character",
            "here:workspace",
        ]
        assert "e Edit" in str(help_screen.query_one("#help-keys").render())

        # / filters the topics; a link-free search still finds the page.
        await pilot.press("slash", *"familiar")
        assert await wait_until(
            pilot, lambda: "found:familiar" in _listed(app), timeout=2.0
        )

        await pilot.press("escape")
        assert await wait_until(pilot, lambda: app.screen is workspace)


async def test_go_there_opens_the_topic_on_the_sheet_or_says_where_it_is():
    storage.save_saga(everything_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        workspace = await _workspace(pilot, app)
        tree = workspace.query_one("#nav-tree", Tree)
        tree.select_node(_node(tree, NODES["character"]))
        assert await wait_until(pilot, lambda: workspace._character_sheet_view)
        view = workspace._character_sheet_view
        await wait_until(pilot, lambda: view.initial_tab_seen)

        # A section in a tab not built yet: g opens the tab and focuses it.
        await pilot.press("question_mark")
        assert await wait_until(pilot, lambda: isinstance(app.screen, HelpScreen))
        help_screen = app.screen
        help_screen.show_topic("section-arts")
        assert "g Go there" in str(help_screen.query_one("#help-hint").render())
        await pilot.press("g")
        assert await wait_until(pilot, lambda: app.screen is workspace)
        assert await wait_until(
            pilot, lambda: workspace._active_section() == "section-arts"
        )
        assert view.query_one(TabbedContent).active == "tab-hermetic"

        # A tab on another kind of sheet: Help stays and says where it is.
        await pilot.press("question_mark")
        assert await wait_until(pilot, lambda: isinstance(app.screen, HelpScreen))
        help_screen = app.screen
        help_screen.show_topic("tab-lab-totals")
        await pilot.press("g")
        await pilot.pause()
        assert app.screen is help_screen
        assert [n.message for n in app._notifications] == [
            "The Lab Totals tab isn't on what Help was opened from. "
            "It is on the Laboratory sheet."
        ]

        # A guide's go: link opens a tab.
        help_screen.post_message(
            Markdown.LinkClicked(help_screen.query_one(Markdown), "go:tab-vf")
        )
        assert await wait_until(pilot, lambda: app.screen is workspace)
        assert await wait_until(
            pilot, lambda: view.query_one(TabbedContent).active == "tab-vf"
        )


async def test_f1_in_a_form_opens_its_page_and_question_mark_is_typed():
    storage.save_saga(everything_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        workspace = await _workspace(pilot, app)
        character = next(c for c in workspace.saga.characters if c.type == "companion")
        workspace._plan_season_for(character, "section-char-season")
        assert await wait_until(pilot, lambda: app.screen is not workspace)
        form = app.screen
        assert form.help_id == "plan-season"
        assert await wait_until(pilot, lambda: form.query("#fdw-details TextArea"))
        notes = form.query_one("#fdw-details TextArea", TextArea)
        notes.focus()
        await pilot.press("question_mark")
        await pilot.pause()
        assert app.screen is form
        assert notes.text.endswith("?")

        await pilot.press("f1")
        assert await wait_until(pilot, lambda: isinstance(app.screen, HelpScreen))
        assert await wait_until(pilot, lambda: app.screen.topic_id == "plan-season")
        await pilot.press("f1")  # never Help on Help
        await pilot.pause()
        assert len([s for s in app.screen_stack if isinstance(s, HelpScreen)]) == 1
        # No Go there from a form's page, or through the form to the sheet.
        assert app.screen.context.go_to is None
        assert "Go there" not in str(app.screen.query_one("#help-hint").render())


async def test_a_form_without_a_page_shows_the_section_help():
    storage.save_saga(everything_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        workspace = await _workspace(pilot, app)
        await pilot.press("e")  # Edit Saga, on the saga node
        assert await wait_until(pilot, lambda: app.screen is not workspace)
        await pilot.press("f1")
        assert await wait_until(pilot, lambda: isinstance(app.screen, HelpScreen))
        assert await wait_until(pilot, lambda: app.screen.topic_id == "saga")


async def test_help_on_the_saga_picker():
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        await wait_until(pilot, lambda: isinstance(app.screen, SagaPickerScreen))
        await pilot.press("question_mark")
        assert await wait_until(pilot, lambda: isinstance(app.screen, HelpScreen))
        assert await wait_until(pilot, lambda: app.screen.topic_id == "saga-picker")
        assert "ref:about" in _listed(app)


# -- The how-to guides ---------------------------------------------

#: The first guides written, then the rest, in the order Help lists them.
GUIDES = [
    "guide-seasons",
    "guide-covenant",
    "guide-advancement",
    "guide-lab-planning",
    "guide-getting-started",
    "guide-creation",
    "guide-familiars",
    "guide-initiation",
    "guide-import-export",
    "guide-hosting",
    "guide-book-packs",
    "guide-bestiary",
    "guide-faction",
    "guide-battle",
    "guide-fights",
    "guide-sieges",
    "guide-hedge-magic",
    "guide-tribunal",
    "guide-formatting",
    "guide-lab-magic-item",
    "guide-mythic-locations",
    "guide-staged-project",
]


def test_the_guides_are_there_in_order():
    assert [p for p in BOOK.pages if p.startswith("guide-")] == GUIDES


async def test_help_lists_the_guides_on_their_own():
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await wait_until(pilot, lambda: isinstance(app.screen, SagaPickerScreen))
        await pilot.press("question_mark")
        assert await wait_until(pilot, lambda: isinstance(app.screen, HelpScreen))
        listed = _listed(app)
        assert [i for i in listed if i.startswith("guide:")] == [
            f"guide:{g}" for g in GUIDES
        ]
        assert not [i for i in listed if i.startswith("all:guide-")]
        topics = app.screen.query_one("#help-topics", OptionList)
        topics.highlighted = topics.get_option_index("guide:guide-seasons")
        assert await wait_until(pilot, lambda: app.screen.topic_id == "guide-seasons")


# -- What's New -------------------------------------------------


def test_whats_new_is_the_changelog_by_feature():
    text = whats_new_text()
    assert text.startswith("# What's New\n")
    assert "# Changelog" not in text
    headings = [line for line in text.splitlines() if line.startswith("## ")]
    assert headings[0] == "## Latest"
    assert headings[-2:] == ["## Chronicle", "## The names and numbers"]
    assert "## Peregrinatio" in headings
    assert f"- **{__version__}** · " in text


async def test_whats_new_is_listed_after_about_and_shows_the_changelog():
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        await wait_until(pilot, lambda: isinstance(app.screen, SagaPickerScreen))
        await pilot.press("question_mark")
        assert await wait_until(pilot, lambda: isinstance(app.screen, HelpScreen))
        listed = _listed(app)
        assert listed.index("ref:whats-new") == listed.index("ref:about") + 1
        topics = app.screen.query_one("#help-topics", OptionList)
        topics.highlighted = topics.get_option_index("ref:whats-new")
        assert await wait_until(pilot, lambda: app.screen.topic_id == "whats-new")
        assert await wait_until(
            pilot, lambda: "Chronicle" in "\n".join(screen_lines(app))
        )


async def test_whats_new_fills_in_and_another_topic_can_replace_it_midway():
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        await wait_until(pilot, lambda: isinstance(app.screen, SagaPickerScreen))
        await pilot.press("question_mark")
        assert await wait_until(pilot, lambda: isinstance(app.screen, HelpScreen))
        topics = app.screen.query_one("#help-topics", OptionList)
        page = app.screen.query_one("#help-page", Markdown)
        topics.highlighted = topics.get_option_index("ref:whats-new")
        assert await wait_until(pilot, lambda: page.source.startswith("# What's New"))
        topics.highlighted = topics.get_option_index("ref:keys")  # still filling
        assert await wait_until(pilot, lambda: page.source.startswith("# Keys"))
        await pilot.pause()
        assert "What's New" not in page.source

        topics.highlighted = topics.get_option_index("ref:whats-new")
        assert await wait_until(
            pilot, lambda: page.source == whats_new_text(), timeout=10.0
        )


def test_a_long_page_is_cut_at_headings_into_pieces_that_join_up():
    text = whats_new_text()
    pieces = page_chunks(text)
    assert len(pieces) > 1 and "".join(pieces) == text
    assert all(piece.startswith("## ") for piece in pieces[1:])
    assert page_chunks("# Short\n\n## A\n\ntext\n") == ["# Short\n\n## A\n\ntext\n"]

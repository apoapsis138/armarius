"""Help: the help files are well formed, every tab and section
of every sheet has help, and ? / F1 open Help on what has focus."""

import re

import pytest
from support import NODES, build_all_tabs, everything_saga, screen_lines, wait_until
from textual.widgets import Markdown, OptionList, TabbedContent, TextArea, Tree

from ars_magica_manager import ROOT, __version__, storage
from ars_magica_manager import help_text as ht
from ars_magica_manager.models import SKETCH, Covenant
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens import WorkspaceScreen
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
    # The core's steps that name their page (commands.Form/Choose.help_id).
    "import-data",
    "import-spells",
}

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
    "region": "_region_sheet_view",
    "neighbour": "_neighbour_sheet_view",
}


@pytest.mark.parametrize("book", [BOOK, GUI_BOOK], ids=ht.FRONT_ENDS)
def test_help_files_load_and_every_link_leads_somewhere(book):
    for page, targets in book.links().items():
        missing = targets - book.topics.keys()
        assert not missing, f"{page} links to {missing}"


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
            node = _node(tree, NODES[kind])
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
    missing = on_sheets - BOOK.topics.keys()
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


# -- What's New and the release names -----------------------------

#: A named release's heading: "## 2.10.0 — 2026-10-05 — Summa".
NAMED_HEADING = re.compile(
    r"^## (\d+\.\d+\.\d+) — \d{4}-\d{2}-\d{2} — (.+)$", re.MULTILINE
)


def test_whats_new_is_the_changelog_under_its_own_title():
    text = whats_new_text()
    assert text.startswith("# What's New\n")
    assert "# Changelog" not in text
    assert f"## {__version__} " in text
    assert "## Release names" in text


def test_every_release_name_is_in_the_table_and_on_a_heading():
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    table = changelog.split("## Release names", 1)[1].split("\n## ", 1)[0]
    named = {name for _, name in NAMED_HEADING.findall(changelog)}
    in_table = set(re.findall(r"^\| ([^|]+?) \| \d", table, re.MULTILINE))
    assert "Summa" in named
    assert named == in_table


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
            pilot, lambda: "Release names" in "\n".join(screen_lines(app))
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

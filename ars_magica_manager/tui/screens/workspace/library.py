"""Saga Content (books in play, saga sources, hidden catalogs, House Rules,
the saga's spells, players) and Books (every book list)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from textual.css.query import NoMatches

from .... import books as bk
from .... import lab_texts as lt
from .... import saga_content as sc
from .... import storage
from ....form_spec import DialogField
from ....forms import goods as goods_forms
from ....forms import importing as import_forms
from ....forms import saga_content as content_forms
from ....markup import escape
from ....models import (
    Book,
)
from ....sections import GOODS_SECTION
from ..fields import FieldsDialog
from ..forms import (
    _book_fields,
    _book_from_values,
    _book_live,
    _research_fields,
    _research_from_values,
)
from ..pickers import (
    CatalogEntryPickerScreen,
    SourcebookPickerScreen,
)
from ..prompts import (
    ConfirmScreen,
    _catalog_dialog,
    _hide_entry_dialog,
    _lab_text_filter_dialog,
)
from ..sheets import (
    BOOK_SECTIONS,
    BOOKS_SECTION,
    CATALOGS_SECTION,
    HIDDEN_SECTION,
    HOUSE_RULES_SECTION,
    LAB_TEXTS_SECTION,
    LIBRARY_SECTIONS,
    PLAYERS_SECTION,
    SESSIONS_SECTION,
    SOURCES_SECTION,
    SPELL_SECTION,
    TRADITIONS_SECTION,
    BookListView,
    HouseRulesView,
    LabTextListView,
    SpellListView,
)
from ..steps import run_steps
from .base import (
    NodeKind,
    WorkspaceBase,
    _SectionOps,
    _tree_node_with_data,
)


class LibraryActions(WorkspaceBase):
    """WorkspaceScreen's actions for spells (the saga's Spells view) and Books
    (every book list)."""

    def _spell_view(self) -> SpellListView | None:
        try:
            return self._detail_pane().query(SpellListView).first()
        except NoMatches:
            return None

    def _spells_changed(self) -> None:
        view = self._spell_view()
        if view is not None:
            view.refilter()

    # -- House Rules: the saga's user-made catalog entries --

    def _house_rules_view(self) -> HouseRulesView | None:
        try:
            return self._detail_pane().query(HouseRulesView).first()
        except NoMatches:
            return None

    # -- Players: who can sign in from a browser --

    # -- Saga Content: books in play, saga sources, hidden catalogs --

    def _refresh_saga_content(self, *sections: str) -> None:
        view = self._saga_content_view
        if view is not None:
            for section in sections:
                view.refresh_section(section)

    def _saga_content_changed(self, *sections: str) -> None:
        storage.save_saga(self.saga)
        self._refresh_saga_content(*sections)
        # Pickers and lists elsewhere follow the books in play.
        house_rules = self._house_rules_view()
        if house_rules is not None:
            house_rules.rebuild()
        spells = self._spell_view()
        if spells is not None:
            spells.refilter()

    def _edit_books_in_play(self) -> None:
        saga = self.saga

        def handle_result(ticked: list[str] | None) -> None:
            if ticked is not None:
                sc.set_books_in_play(saga, ticked)
                self._saga_content_changed(BOOKS_SECTION, SOURCES_SECTION)

        self.app.push_screen(
            SourcebookPickerScreen(saga.books_in_play, saga.sources), handle_result
        )

    def _edit_traditions(self) -> None:
        """Choose the non-Hermetic traditions the saga offers."""
        saga = self.saga

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is not None:
                content_forms.apply_traditions(saga, values)
                self._saga_content_changed(TRADITIONS_SECTION)

        self.app.push_screen(
            FieldsDialog("Traditions offered", content_forms.traditions_fields(saga)),
            handle_result,
        )

    def _edit_catalog(self) -> None:
        view = self._saga_content_view
        keys = list(sc.CATALOGS)
        chosen = view.selected_catalog() if view is not None else None
        self._chosen_or_pick(
            keys.index(chosen) if chosen is not None else None,
            keys,
            empty="",
            then=lambda index: self._catalog_form(keys[index]),
        )

    def _catalog_form(self, key: str) -> None:
        def handle_result(values: dict[str, Any] | None) -> None:
            if values is not None:
                sc.set_catalog_shown(self.saga, key, bool(values["shown"]))
                self._saga_content_changed(CATALOGS_SECTION)

        self.app.push_screen(_catalog_dialog(self.saga, key), handle_result)

    def _hide_catalog_entry(self) -> None:
        """Hide one more shared entry: which catalog, then which entry."""
        saga = self.saga
        view = self._saga_content_view
        chosen = view.selected_hidden() if view is not None else None

        def handle_entry(key: str, entry_id: str | None) -> None:
            if entry_id is not None:
                sc.hide_entry(saga, key, entry_id)
                self._saga_content_changed(CATALOGS_SECTION, HIDDEN_SECTION)

        def handle_catalog(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            key = values["catalog"]
            self.app.push_screen(
                CatalogEntryPickerScreen(saga, key),
                lambda entry_id: handle_entry(key, entry_id),
            )

        self.app.push_screen(
            _hide_entry_dialog(chosen[0] if chosen is not None else None),
            handle_catalog,
        )

    def action_add_purity(self) -> None:
        """More's Add a Purity on the Goods list's chosen good."""
        view = self._saga_content_view
        if view is None:
            return
        self._run_commit(
            goods_forms.add_purity(self.saga, view.section_row(GOODS_SECTION)),
            GOODS_SECTION,
        )

    def action_move_to_source(self) -> None:
        """More's Move to Source on House Rules: several entries into one of
        the saga's sources at once."""
        self._run_commit(content_forms.move_to_source(self.saga), HOUSE_RULES_SECTION)

    def _show_catalog_entry(self) -> None:
        """Offer the chosen hidden entry again, after confirming."""
        view = self._saga_content_view
        listed = sc.hidden_entries(self.saga)
        chosen = view.selected_hidden() if view is not None else None

        def confirm(index: int) -> None:
            key, entry = listed[index]

            def handle_confirmed(confirmed: bool | None) -> None:
                if confirmed:
                    sc.show_entry(self.saga, key, entry.id)
                    self._saga_content_changed(CATALOGS_SECTION, HIDDEN_SECTION)

            self.app.push_screen(
                ConfirmScreen(f"Offer {escape(entry.name)} again?"),
                handle_confirmed,
            )

        self._chosen_or_pick(
            listed.index(chosen) if chosen in listed else None,
            [entry.name for _, entry in listed],
            empty="No entries are hidden: 'a' hides one.",
            then=confirm,
        )

    # -- Books (Library tab, laboratory/character Books, Unassigned Books) --

    def _book_view(self) -> BookListView | None:
        """The book list showing in the detail pane, if any: the active
        section's when a sheet shows two (a laboratory's Lab Texts and its
        other Books), else its Books."""
        views = list(self._detail_pane().query(BookListView))
        active = self._active_section()
        views.sort(
            key=lambda v: (v.section_id != active, isinstance(v, LabTextListView))
        )
        return views[0] if views else None

    def _chosen_book_id(self) -> str | None:
        view = self._book_view()
        chosen = view.selected_book() if view is not None else None
        return chosen.id if chosen is not None else None

    def action_filter_lab_texts(self) -> None:
        """/ on a laboratory's Lab Texts: narrow the list by kind, Art,
        level and whether its owner can read them."""
        view = self._book_view()
        if not isinstance(view, LabTextListView):
            return

        def handle_result(wanted: lt.Filter | None) -> None:
            if wanted is not None:
                view.set_filter(wanted)
                self._refresh_laboratory_section(LAB_TEXTS_SECTION)

        self.app.push_screen(_lab_text_filter_dialog(view.filter), handle_result)

    def _default_book_owner(self) -> str:
        """Owner a new book starts with: wherever it's being added from."""
        if self.selected_kind == NodeKind.CHARACTER and self.selected_character:
            return bk.owner_value("character", self.selected_character.id)
        if self.selected_kind == NodeKind.LABORATORY and self.selected_laboratory:
            return bk.owner_value("laboratory", self.selected_laboratory.id)
        if self.selected_kind == NodeKind.COVENANT and self.selected_covenant:
            return bk.owner_value("covenant", self.selected_covenant.id)
        return ""

    def _pick_book(self, then: Callable[[Book], None]) -> None:
        """Act on the chosen book."""
        view = self._book_view()
        if view is None:
            return
        chosen = view.selected_book()
        if chosen is not None:
            then(chosen)
            return
        listed = list(view.books)
        self._chosen_or_pick(
            None,
            [b.name for b in listed],
            empty="No books here yet.",
            then=lambda index: then(listed[index]),
        )

    def action_research_bonuses(self) -> None:
        """Set the covenant library's research bonus per subject."""
        covenant = self.selected_covenant
        if covenant is None:
            return
        saga = self.saga

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            _research_from_values(saga, covenant, values)
            storage.save_saga(saga)
            self._books_changed()

        self.app.push_screen(
            FieldsDialog(
                f"Research Bonuses: {escape(covenant.name)}'s library",
                _research_fields(saga, covenant),
            ),
            handle_result,
        )

    def _marked_books(self) -> list[Book]:
        view = self._book_view()
        return view.checked_books() if view is not None else []

    def _edit_book(self) -> None:
        """Edit the chosen book; with books marked, change their owner."""
        marked = self._marked_books()
        if marked:
            self._change_owner_of(marked)
            return
        self._pick_book(self._book_form)

    def _change_owner_of(self, books: list[Book]) -> None:
        """Give several books one new owner (the only edit that makes sense
        for many at once), confirming first."""
        saga = self.saga
        count = len(books)
        plural = "s" if count != 1 else ""
        owners = {bk.owner_value(b.owner_kind, b.owner_id) for b in books}
        current = owners.pop() if len(owners) == 1 else None
        if current is not None and bk.is_unassigned(saga, books[0]):
            current = ""

        def handle_owner(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            owner = values["owner"]
            label = next(lbl for lbl, value in bk.owner_options(saga) if value == owner)

            def handle_confirmed(confirmed: bool | None) -> None:
                if not confirmed:
                    return
                kind, owner_id = bk.parse_owner_value(owner)
                for book in books:
                    bk.set_owner(saga, book, kind, owner_id)
                storage.save_saga(saga)
                self._books_changed()

            self.app.push_screen(
                ConfirmScreen(
                    f"Changing ownership of {count} book{plural} to "
                    f"[b]{escape(label)}[/]. Continue?",
                    yes_label="Change",
                    yes_variant="success",
                ),
                handle_confirmed,
            )

        self.app.push_screen(
            FieldsDialog(
                f"Change the owner of {count} book{plural}",
                [
                    DialogField(
                        "_books",
                        "Books",
                        "info",
                        ", ".join(b.name or "(untitled)" for b in books),
                    ),
                    DialogField(
                        "owner",
                        "New owner",
                        "select",
                        current,
                        options=bk.owner_options(saga),
                        required=True,
                        allow_blank=True,
                        placeholder="(choose the new owner)",
                    ),
                ],
            ),
            handle_owner,
        )

    def _book_form(self, book: Book | None) -> None:
        saga = self.saga
        title = (
            "Add a Book" if book is None else f"Edit {escape(book.name or 'this book')}"
        )

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            target = book
            if target is None:
                target = bk.add_book(saga, values["name"], values["type"])
            _book_from_values(target, values, saga)
            storage.save_saga(saga)
            self._books_changed()

        # The Lab Texts list adds Lab Texts.
        default_type = "Lab Text" if self._active_section() == LAB_TEXTS_SECTION else ""
        self.app.push_screen(
            FieldsDialog(
                title,
                _book_fields(saga, book, self._default_book_owner(), default_type),
                validate=bk.form_problem,
                live=lambda values: _book_live(values, saga, book),
            ),
            handle_result,
        )

    def _remove_book(self) -> None:
        """Delete the chosen book, or every marked one, after confirming."""
        marked = self._marked_books()
        if marked:
            count = len(marked)

            def handle_all(confirmed: bool | None) -> None:
                if not confirmed:
                    return
                for book in marked:
                    if book in self.saga.books:
                        self.saga.books.remove(book)
                bk.prune_codices(self.saga)
                storage.save_saga(self.saga)
                self._books_changed()

            self.app.push_screen(
                ConfirmScreen(
                    f"Are you sure you want to delete {count} "
                    f"book{'s' if count != 1 else ''}?"
                ),
                handle_all,
            )
            return

        self._pick_book(self._delete_book)

    def _delete_book(self, book: Book) -> None:
        """Delete `book` after confirming."""

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed and book in self.saga.books:
                self.saga.books.remove(book)
                bk.prune_codices(self.saga)
                storage.save_saga(self.saga)
                self._books_changed()

        self.app.push_screen(
            ConfirmScreen(f"Delete {escape(book.name or 'this book')}?"),
            handle_confirmed,
        )

    def action_import_data(self) -> None:
        """More's Import (import_forms): on the saga, choose what to import;
        on a covenant's Library tab, import books straight into its
        library."""
        covenant = None
        if self.selected_kind != NodeKind.SAGA:
            covenant = self.selected_covenant
            if covenant is None or self._active_section() not in LIBRARY_SECTIONS:
                return

        def done(end: object) -> None:
            if not isinstance(end, list):
                return
            storage.save_saga(self.saga)
            self._books_changed()
            self._spells_changed()
            self._rebuild_tree()
            if self.selected_kind == NodeKind.SAGA:
                self.call_later(self._show_saga_detail)  # its Books count
            if end:
                self.notify("\n".join(end))

        run_steps(self.app, import_forms.import_data(self.saga, covenant), done)

    def _books_changed(self) -> None:
        """After any book edit: re-render the book list on show, and keep the
        tree's Unassigned Books node in step (it appears, changes count or goes
        away as books lose and gain owners)."""
        # Every list on show: an edit can move a book between a laboratory's
        # Lab Texts and its other Books.
        for view in self._detail_pane().query(BookListView):
            view.rebuild()
        tree = self._nav_tree()
        node = _tree_node_with_data(tree, (NodeKind.BOOK_GROUP,))
        count = len(bk.unassigned_books(self.saga))
        if node is not None and count:
            node.set_label(f"Unassigned Books ({count})")
        elif node is not None:
            node.remove()
        elif count:
            tree.root.add_leaf(
                f"Unassigned Books ({count})", data=(NodeKind.BOOK_GROUP,)
            )

    def _library_section_ops(self) -> dict[str, _SectionOps]:
        """a / d / e on the saga's own sections and the library's (see
        WorkspaceScreen._section_ops)."""
        ops: dict[str, _SectionOps] = {
            SPELL_SECTION: self._core_ops_of(SPELL_SECTION),
            HOUSE_RULES_SECTION: self._core_ops_of(HOUSE_RULES_SECTION),
            PLAYERS_SECTION: self._core_ops_of(PLAYERS_SECTION),
            SESSIONS_SECTION: self._core_ops_of(SESSIONS_SECTION),
            BOOKS_SECTION: _SectionOps(edit=self._edit_books_in_play),
            TRADITIONS_SECTION: _SectionOps(edit=self._edit_traditions),
            SOURCES_SECTION: self._core_ops_of(SOURCES_SECTION),
            CATALOGS_SECTION: _SectionOps(edit=self._edit_catalog),
            HIDDEN_SECTION: _SectionOps(
                add=self._hide_catalog_entry, remove=self._show_catalog_entry
            ),
        }
        for section in BOOK_SECTIONS:
            listed = section != "section-lib-summary"  # the summary lists none
            ops[section] = _SectionOps(
                lambda: self._book_form(None),
                self._remove_book if listed else None,
                self._edit_book if listed else None,
            )
        return ops

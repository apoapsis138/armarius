"""Saga Content (books in play, saga sources, hidden catalogs, House Rules,
the saga's spells, players) and Books (every book list)."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from textual.css.query import NoMatches

from .... import books as bk
from .... import house_rules as hr
from .... import lab_texts as lt
from .... import players as pl
from .... import saga_content as sc
from .... import seasons, storage, transfer
from .... import spells as spl
from ....form_spec import DialogField
from ....markup import escape
from ....models import (
    TEXT_LONGEVITY,
    Book,
    Covenant,
    Player,
    SagaSource,
    Spell,
)
from ..fields import FieldsDialog
from ..forms import (
    DuplicateBookScreen,
    ImportScreen,
    SpellImportHelperScreen,
    _book_fields,
    _book_from_values,
    _book_live,
    _research_fields,
    _research_from_values,
    _spell_fields,
    _spell_from_values,
    _spell_live,
    _spell_problem,
)
from ..pickers import (
    CatalogEntryPickerScreen,
    CsvFilePickerScreen,
    RemovalPickerScreen,
    SourcebookPickerScreen,
)
from ..prompts import (
    ConfirmScreen,
    _catalog_dialog,
    _hide_entry_dialog,
    _house_rule_dialog,
    _lab_text_filter_dialog,
    _player_dialog,
    _ritual_again_dialog,
    _saga_source_dialog,
)
from ..sheets import (
    BOOKS_SECTION,
    CATALOGS_SECTION,
    HIDDEN_SECTION,
    LAB_TEXTS_SECTION,
    LIBRARY_SECTIONS,
    SOURCES_SECTION,
    BookListView,
    HouseRulesView,
    LabTextListView,
    PlayersView,
    SpellListView,
)
from .base import (
    NodeKind,
    WorkspaceBase,
    _tree_node_with_data,
)

#: The Import dialog's entries that take an exported record, and the kind
#: of export each takes.
_RECORD_IMPORTS: dict[str, str] = {
    "characters": transfer.CHARACTER,
    "covenants": transfer.COVENANT,
    "laboratories": transfer.LABORATORY,
}


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

    def _chosen_own_spell(self, verb: str) -> Spell | None:
        """The chosen spell if it's one of the saga's own; otherwise say why
        not (nothing chosen, or a read-only catalog spell)."""
        view = self._spell_view()
        spell = view.selected_spell() if view is not None else None
        if spell is None:
            self.notify(f"Choose a spell to {verb} first.")
            return None
        if not spl.is_own(self.saga, spell):
            self.notify(
                f"{escape(spell.name)} is a catalog spell, so it's read-only. To "
                "make your own version, add a spell with a."
            )
            return None
        return spell

    def _edit_saga_spell(self) -> None:
        spell = self._chosen_own_spell("edit")
        if spell is not None:
            self._spell_form(spell)

    def _spell_form(self, spell: Spell | None) -> None:
        saga = self.saga
        title = "Add a Spell" if spell is None else f"Edit {escape(spell.name)}"

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            target = spell
            if target is None:
                target = spl.add_own_spell(
                    saga, values["name"], values["technique"], values["form"]
                )
            _spell_from_values(target, values)
            storage.save_saga(saga)
            self._spells_changed()

        self.app.push_screen(
            FieldsDialog(
                title,
                _spell_fields(spell),
                validate=_spell_problem,
                live=_spell_live,
            ),
            handle_result,
        )

    def _remove_saga_spell(self) -> None:
        spell = self._chosen_own_spell("delete")
        if spell is None:
            return

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed and spell in self.saga.spells:
                self.saga.spells.remove(spell)
                storage.save_saga(self.saga)
                self._spells_changed()

        self.app.push_screen(
            ConfirmScreen(f"Delete {escape(spell.name)}?"), handle_confirmed
        )

    # -- House Rules: the saga's user-made catalog entries --

    def _house_rules_view(self) -> HouseRulesView | None:
        try:
            return self._detail_pane().query(HouseRulesView).first()
        except NoMatches:
            return None

    def _house_rules_changed(self) -> None:
        storage.save_saga(self.saga)
        view = self._house_rules_view()
        if view is not None:
            view.rebuild()
        self._refresh_saga_content(BOOKS_SECTION, SOURCES_SECTION)

    def _pick_house_rule(self, then: Callable[[str, hr.Entry], None]) -> None:
        """Act on the chosen entry."""
        view = self._house_rules_view()
        listed = hr.all_entries(self.saga)
        chosen = view.selected_entry() if view is not None else None
        if chosen is not None:
            then(*chosen)
            return
        self._chosen_or_pick(
            None,
            [entry.name for _, entry in listed],
            empty="No House Rules yet: 'a' adds one.",
            then=lambda index: then(*listed[index]),
        )

    def _house_rule_form(self, existing: tuple[str, hr.Entry] | None) -> None:
        saga = self.saga

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            if existing is None:
                hr.add(saga, values["kind"], values)
            else:
                hr.update(saga, existing[0], existing[1], values)
            self._house_rules_changed()

        self.app.push_screen(_house_rule_dialog(saga, existing), handle_result)

    def _edit_house_rule(self) -> None:
        self._pick_house_rule(
            lambda kind, entry: self._house_rule_form((kind, entry)),
        )

    def _remove_house_rule(self) -> None:
        """Delete the chosen entry after confirming -- unless a record
        still holds it."""

        def confirm(kind: str, entry: hr.Entry) -> None:
            holders = hr.used_by(self.saga, kind, entry)
            if holders:
                self.notify(
                    f"{escape(entry.name)} is held by {escape(', '.join(holders))}: "
                    "remove it there first.",
                    severity="warning",
                )
                return

            def handle_confirmed(confirmed: bool | None) -> None:
                if confirmed and entry in hr.entries_of(self.saga, kind):
                    hr.remove(self.saga, kind, entry)
                    self._house_rules_changed()

            self.app.push_screen(
                ConfirmScreen(f"Delete {escape(entry.name)}?"), handle_confirmed
            )

        self._pick_house_rule(confirm)

    # -- Players: who can sign in from a browser --

    def _players_view(self) -> PlayersView | None:
        try:
            return self._detail_pane().query(PlayersView).first()
        except NoMatches:
            return None

    def _players_changed(self) -> None:
        storage.save_saga(self.saga)
        view = self._players_view()
        if view is not None:
            view.rebuild()

    def _pick_player(self, then: Callable[[Player], None]) -> None:
        """Act on the chosen player."""
        view = self._players_view()
        chosen = view.selected_player() if view is not None else None
        if chosen is not None:
            then(chosen)
            return
        players = list(self.saga.players)
        self._chosen_or_pick(
            None,
            [p.name for p in players],
            empty="No players yet: 'a' adds one.",
            then=lambda index: then(players[index]),
        )

    def _player_form(self, existing: Player | None) -> None:
        saga = self.saga

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            if existing is None:
                pl.add(saga, values)
            else:
                pl.update(existing, values)
            self._players_changed()

        self.app.push_screen(_player_dialog(saga, existing), handle_result)

    def _edit_player(self) -> None:
        self._pick_player(self._player_form)

    def _remove_player(self) -> None:
        """Delete the chosen player after confirming: they can no longer
        sign in (a browser copy they already have open stays open)."""

        def confirm(player: Player) -> None:
            def handle_confirmed(confirmed: bool | None) -> None:
                if confirmed and player in self.saga.players:
                    pl.remove(self.saga, player)
                    self._players_changed()

            self.app.push_screen(
                ConfirmScreen(
                    f"Delete the player {escape(player.name)}?\n\n"
                    "They will no longer be able to sign in."
                ),
                handle_confirmed,
            )

        self._pick_player(confirm)

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

    def _pick_saga_source(self, then: Callable[[SagaSource], None]) -> None:
        view = self._saga_content_view
        chosen = view.selected_source() if view is not None else None
        if chosen is not None:
            then(chosen)
            return
        sources = list(self.saga.sources)
        self._chosen_or_pick(
            None,
            [s.abbreviation for s in sources],
            empty="No saga sources yet: 'a' adds one.",
            then=lambda index: then(sources[index]),
        )

    def _saga_source_form(self, existing: SagaSource | None) -> None:
        saga = self.saga

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            if existing is None:
                sc.add_source(saga, values)
            else:
                sc.update_source(saga, existing, values)
            self._saga_content_changed(BOOKS_SECTION, SOURCES_SECTION)

        self.app.push_screen(_saga_source_dialog(saga, existing), handle_result)

    def _edit_saga_source(self) -> None:
        self._pick_saga_source(self._saga_source_form)

    def _remove_saga_source(self) -> None:
        """Delete the chosen source after confirming -- unless an entry
        still cites it."""

        def confirm(source: SagaSource) -> None:
            citing = hr.citing(self.saga, source.abbreviation)
            if citing:
                self.notify(
                    f"{escape(source.abbreviation)} is cited by "
                    f"{escape(', '.join(e.name for e in citing))}: change them "
                    "first.",
                    severity="warning",
                )
                return

            def handle_confirmed(confirmed: bool | None) -> None:
                if confirmed and source in self.saga.sources:
                    sc.remove_source(self.saga, source)
                    self._saga_content_changed(BOOKS_SECTION, SOURCES_SECTION)

            self.app.push_screen(
                ConfirmScreen(f"Delete {escape(source.abbreviation)}?"),
                handle_confirmed,
            )

        self._pick_saga_source(confirm)

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

    def _ritual_texts(self) -> list[Book]:
        """The Longevity Ritual texts the laboratory on show keeps."""
        lab = self.selected_laboratory
        if lab is None:
            return []
        return [
            b
            for b in lt.texts_of(self.saga, "laboratory", lab.id)
            if lt.kind(b) == TEXT_LONGEVITY
        ]

    def action_perform_ritual(self) -> None:
        """More on a laboratory's Lab Texts: perform a Longevity Ritual again
        from its text -- the chosen one, else the one picked. It
        takes vis but no season, so it is done at once."""
        lab = self.selected_laboratory
        view = self._book_view()
        texts = self._ritual_texts()
        if lab is None or not texts:
            return
        magus = self.saga.character(lab.owner_id)
        if magus is None:
            self.notify("The laboratory has no owner to perform the ritual.")
            return

        def perform(text: Book) -> None:
            def handle_result(result: tuple[str, str] | None) -> None:
                if result is None:
                    return
                found = seasons.perform_ritual_again(
                    self.saga, magus, lab, text, *result
                )
                if found:
                    self.notify(found[0], severity="warning")
                    return
                self._commit("section-lab-raw-vis", "tab-lab-diary")
                self.notify(f"{escape(text.ritual_subject)}'s ritual is renewed.")

            self.app.push_screen(
                _ritual_again_dialog(self.saga, magus, lab, text), handle_result
            )

        chosen = view.selected_book() if view is not None else None
        if chosen is not None and chosen in texts:
            perform(chosen)
        elif len(texts) == 1:
            perform(texts[0])
        else:
            self.app.push_screen(
                RemovalPickerScreen(
                    "Perform which Longevity Ritual again?",
                    [escape(b.name) for b in texts],
                ),
                lambda index: perform(texts[index]) if index is not None else None,
            )

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
        """More's Import: on the saga, choose what to import (Books or Spells so far);
        on a covenant's Library tab, import books straight into its library."""
        if self.selected_kind == NodeKind.SAGA:

            def handle_kind(kind: str | None) -> None:
                if kind == "books":
                    self._import_books(None)
                elif kind == "spells":
                    self._import_spells()
                elif kind in _RECORD_IMPORTS:
                    self._import_record(_RECORD_IMPORTS[kind])

            self.app.push_screen(ImportScreen(), handle_kind)
        elif (
            self.selected_covenant is not None
            and self._active_section() in LIBRARY_SECTIONS
        ):
            self._import_books(self.selected_covenant)

    def _import_record(self, kind: str) -> None:
        """Pick an exported character, covenant or laboratory -- a file of
        the `kind` chosen in the Import dialog --, preview what
        importing it adds and which of its links this saga can keep, then
        add it."""
        saga = self.saga
        wanted = transfer.KIND_LABELS[kind].lower()

        def handle_path(path: Path | None) -> None:
            if path is None:
                return
            try:
                data = transfer.read(path)
                if data["kind"] != kind:
                    found = transfer.KIND_LABELS[data["kind"]].lower()
                    raise ValueError(
                        f"it holds a {found}, not a {wanted}: choose "
                        f"{transfer.KIND_LABELS[data['kind']]} in the Import list"
                    )
                plan = transfer.plan_import(saga, data)
            except (OSError, ValueError, KeyError, TypeError) as problem:
                self.notify(
                    f"Couldn't import {escape(path.name)}: {escape(str(problem))}",
                    severity="error",
                )
                return

            def handle_confirmed(confirmed: bool | None) -> None:
                if not confirmed:
                    return
                transfer.apply(saga, plan)
                storage.save_saga(saga)
                self._rebuild_tree()
                self.notify(
                    f"Imported {escape(plan.name)} "
                    f"({transfer.KIND_LABELS[plan.kind].lower()})."
                )

            self.app.push_screen(
                ConfirmScreen(
                    escape(transfer.preview(plan)),
                    yes_label="Import",
                    yes_variant="success",
                ),
                handle_confirmed,
            )

        start = storage.EXPORTS_DIR if storage.EXPORTS_DIR.is_dir() else Path.cwd()
        self.app.push_screen(
            CsvFilePickerScreen(f"Import a {wanted}", start, suffix=".json"),
            handle_path,
        )

    def _import_books(self, covenant: Covenant | None) -> None:
        """Pick a CSV file, preview what it holds, then add its books: all
        owned by `covenant`, or all unassigned when it's None (the file's own
        owner column isn't used)."""
        saga = self.saga
        destination = (
            f"into {covenant.name}'s library"
            if covenant is not None
            else "as unassigned books"
        )

        def handle_path(path: Path | None) -> None:
            if path is None:
                return
            try:
                result = bk.read_books_csv(path)
            except (OSError, ValueError) as problem:
                self.notify(
                    f"Couldn't read {escape(path.name)}: {escape(str(problem))}",
                    severity="error",
                )
                return
            if not result.books:
                reason = f" {escape(result.skipped[0])}" if result.skipped else ""
                self.notify(
                    f"No books to import from {escape(path.name)}.{reason}",
                    severity="warning",
                )
                return

            def handle_confirmed(confirmed: bool | None) -> None:
                if confirmed:
                    self._add_imported_books(
                        result.books, covenant, destination, result.encyclopedias
                    )

            self.app.push_screen(
                ConfirmScreen(
                    bk.import_preview(
                        result, path.name, destination, {b.name for b in saga.books}
                    ),
                    yes_label="Import",
                    yes_variant="success",
                ),
                handle_confirmed,
            )

        title = (
            f"Import books into {covenant.name}'s library"
            if covenant is not None
            else "Import books (as unassigned books)"
        )
        self.app.push_screen(CsvFilePickerScreen(title, Path.cwd()), handle_path)

    def _add_imported_books(
        self,
        books: list[Book],
        covenant: Covenant | None,
        destination: str,
        encyclopedias: set[str] | None = None,
    ) -> None:
        """Add confirmed imported books, asking about each one whose name is
        already taken (Duplicate / Duplicate All / Skip / Skip All). Nothing
        is added until every question is answered."""
        saga = self.saga

        def finish(accepted: list[Book], skipped: int) -> None:
            bk.add_imported_books(saga, accepted, covenant, encyclopedias)
            if accepted:
                storage.save_saga(saga)
                self._books_changed()
                if self.selected_kind == NodeKind.SAGA:
                    self.call_later(self._show_saga_detail)  # its Books count
            count = len(accepted)
            message = f"Imported {count} book{'s' if count != 1 else ''}"
            message += f" {destination}" if count else ""
            if skipped:
                message += f"; skipped {skipped} duplicate{'s' if skipped != 1 else ''}"
            self.notify(escape(message + "."))

        self._ask_about_duplicates(books, {b.name for b in saga.books}, "book", finish)

    def _ask_about_duplicates(
        self,
        items: list[Any],
        names: set[str],
        noun: str,
        finish: Callable[[list[Any], int], None],
        key: Callable[[str], str] = str,
    ) -> None:
        """Go through imported items (anything with a `.name`), asking about
        each whose name is already taken -- by `names` or earlier in `items`,
        comparing names by `key` -- (Duplicate / Duplicate All / Skip / Skip
        All), then call `finish(accepted, skipped)`. Nothing is added until
        every question is answered."""
        pending = list(items)
        accepted: list[Any] = []
        taken = {key(name) for name in names}
        state: dict[str, Any] = {"all": None, "skipped": 0}

        def take(item: Any, answer: str) -> None:
            if answer == "skip":
                state["skipped"] += 1
            else:
                accepted.append(item)
                taken.add(key(item.name))

        def step() -> None:
            while pending:
                item = pending[0]
                if key(item.name) in taken and state["all"] is None:
                    remaining = len(bk.duplicate_names(pending[1:], taken, key))

                    def handle_answer(answer: str | None, item=item) -> None:
                        answer = answer or "skip"
                        if answer.endswith("_all"):
                            answer = answer[: -len("_all")]
                            state["all"] = answer
                        pending.pop(0)
                        take(item, answer)
                        step()

                    self.app.push_screen(
                        DuplicateBookScreen(item.name, remaining, noun=noun),
                        handle_answer,
                    )
                    return
                pending.pop(0)
                take(item, state["all"] if key(item.name) in taken else "duplicate")
            finish(accepted, state["skipped"])

        step()

    def _import_spells(self) -> None:
        """The Import Spells helper, then pick a CSV, preview it, and add its
        spells to the saga's own (asking about duplicate names)."""
        saga = self.saga

        def handle_path(path: Path | None) -> None:
            if path is None:
                return
            try:
                result = spl.read_spells_csv(path)
            except (OSError, ValueError) as problem:
                self.notify(
                    f"Couldn't read {escape(path.name)}: {escape(str(problem))}",
                    severity="error",
                )
                return
            if not result.spells:
                reason = f" {escape(result.skipped[0])}" if result.skipped else ""
                self.notify(
                    f"No spells to import from {escape(path.name)}.{reason}",
                    severity="warning",
                )
                return
            existing = {sp.name for sp in spl.all_spells(saga)}

            def finish(accepted: list[Spell], skipped: int) -> None:
                spl.add_imported_spells(saga, accepted)
                if accepted:
                    storage.save_saga(saga)
                    self._spells_changed()
                count = len(accepted)
                message = f"Imported {count} spell{'s' if count != 1 else ''}"
                if skipped:
                    message += (
                        f"; skipped {skipped} duplicate{'s' if skipped != 1 else ''}"
                    )
                self.notify(escape(message + "."))

            def handle_confirmed(confirmed: bool | None) -> None:
                if confirmed:
                    self._ask_about_duplicates(
                        result.spells, existing, "spell", finish, spl.name_key
                    )

            self.app.push_screen(
                ConfirmScreen(
                    spl.spell_import_preview(result, path.name, existing),
                    yes_label="Import",
                    yes_variant="success",
                ),
                handle_confirmed,
            )

        def handle_helper(choice: str | None) -> None:
            if choice == "choose":
                self.app.push_screen(
                    CsvFilePickerScreen(
                        "Import spells (into the saga's own spells)", Path.cwd()
                    ),
                    handle_path,
                )

        self.app.push_screen(SpellImportHelperScreen(Path.cwd()), handle_helper)

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

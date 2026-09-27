"""Spells (the saga's Spells view) and Books (every book list)."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from textual.css.query import NoMatches

from ... import books as bk
from ... import spells as spl
from ... import storage
from ...markup import escape
from ...models import (
    Book,
    Covenant,
    Spell,
)
from ..fields import (
    DialogField,
    FieldsDialog,
)
from ..forms import (
    DuplicateBookScreen,
    ImportScreen,
    SpellImportHelperScreen,
    _book_fields,
    _book_from_values,
    _book_live,
    _spell_fields,
    _spell_from_values,
    _spell_live,
    _spell_problem,
)
from ..pickers import (
    CsvFilePickerScreen,
    RemovalPickerScreen,
)
from ..prompts import (
    ConfirmScreen,
)
from ..sheets import (
    _LIBRARY_SECTIONS,
    BookListView,
    SpellListView,
)
from .base import (
    NodeKind,
    WorkspaceBase,
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
        node = _tree_node_with_data(self._nav_tree(), (NodeKind.SPELLS,))
        if node is not None:
            node.set_label(self._spells_label())

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

    # -- Books (Library tab, laboratory/character Books, Unassigned Books) --

    def _book_view(self) -> BookListView | None:
        """The book list showing in the detail pane, if any (a sheet shows at
        most one)."""
        try:
            return self._detail_pane().query(BookListView).first()
        except NoMatches:
            return None

    def _default_book_owner(self) -> str:
        """Owner a new book starts with: wherever it's being added from."""
        if self.selected_kind == NodeKind.CHARACTER and self.selected_character:
            return bk.owner_value("character", self.selected_character.id)
        if self.selected_kind == NodeKind.LABORATORY and self.selected_laboratory:
            return bk.owner_value("laboratory", self.selected_laboratory.id)
        if self.selected_kind == NodeKind.COVENANT and self.selected_covenant:
            return bk.owner_value("covenant", self.selected_covenant.id)
        return ""

    def _pick_book(self, title: str, then: Callable[[Book], None]) -> None:
        """Act on the chosen book; with none chosen, ask which one."""
        view = self._book_view()
        if view is None:
            return
        chosen = view.selected_book()
        if chosen is not None:
            then(chosen)
            return
        listed = list(view.books)
        if not listed:
            self.notify("No books here yet.")
            return

        def handle_index(index: int | None) -> None:
            if index is not None:
                then(listed[index])

        self.app.push_screen(
            RemovalPickerScreen(
                title, [escape(b.name) or "(untitled)" for b in listed]
            ),
            handle_index,
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
        self._pick_book("Edit which book?", self._book_form)

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
                    book.owner_kind, book.owner_id = kind, owner_id
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

        self.app.push_screen(
            FieldsDialog(
                title,
                _book_fields(saga, book, self._default_book_owner()),
                validate=bk.form_problem,
                live=lambda values: _book_live(values, saga),
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

        def confirm(book: Book) -> None:
            def handle_confirmed(confirmed: bool | None) -> None:
                if confirmed and book in self.saga.books:
                    self.saga.books.remove(book)
                    storage.save_saga(self.saga)
                    self._books_changed()

            self.app.push_screen(
                ConfirmScreen(f"Delete {escape(book.name or 'this book')}?"),
                handle_confirmed,
            )

        self._pick_book("Remove a Book", confirm)

    def action_import_data(self) -> None:
        """'I': on the saga, choose what to import (Books or Spells so far);
        on a covenant's Library tab, import books straight into its library."""
        if self.selected_kind == NodeKind.SAGA:

            def handle_kind(kind: str | None) -> None:
                if kind == "books":
                    self._import_books(None)
                elif kind == "spells":
                    self._import_spells()

            self.app.push_screen(ImportScreen(), handle_kind)
        elif (
            self.selected_covenant is not None
            and self._active_section() in _LIBRARY_SECTIONS
        ):
            self._import_books(self.selected_covenant)

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
                    self._add_imported_books(result.books, covenant, destination)

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
        self, books: list[Book], covenant: Covenant | None, destination: str
    ) -> None:
        """Add confirmed imported books, asking about each one whose name is
        already taken (Duplicate / Duplicate All / Skip / Skip All). Nothing
        is added until every question is answered."""
        saga = self.saga

        def finish(accepted: list[Book], skipped: int) -> None:
            bk.add_imported_books(saga, accepted, covenant)
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
    ) -> None:
        """Go through imported items (anything with a `.name`), asking about
        each whose name is already taken -- by `names` or earlier in `items` --
        (Duplicate / Duplicate All / Skip / Skip All), then call
        `finish(accepted, skipped)`. Nothing is added until every question is
        answered."""
        pending = list(items)
        accepted: list[Any] = []
        taken = set(names)
        state: dict[str, Any] = {"all": None, "skipped": 0}

        def take(item: Any, answer: str) -> None:
            if answer == "skip":
                state["skipped"] += 1
            else:
                accepted.append(item)
                taken.add(item.name)

        def step() -> None:
            while pending:
                item = pending[0]
                if item.name in taken and state["all"] is None:
                    remaining = len(bk.duplicate_names(pending[1:], taken))

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
                take(item, state["all"] if item.name in taken else "duplicate")
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
                    self._ask_about_duplicates(result.spells, existing, "spell", finish)

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
        view = self._book_view()
        if view is not None:
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

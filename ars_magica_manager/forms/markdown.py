"""Export as Markdown, as the core's command steps (commands.py): a
character's, covenant's, laboratory's or familiar's sheet written as a
Markdown file (markdown_sheet.py), in the same copy and, for a
character, the same play sheet or full record as Print to PDF. Both
front-ends offer it: the terminal in More (`m`), the desktop in Manage.

The copy follows print_layout.reader_for, as printing does: only someone
who reads the whole saga is asked, and anyone else gets the Player copy.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from .. import markdown_sheet, print_records, viewing
from ..commands import Form, Refuse
from ..form_spec import DialogField
from ..markup import escape, todo
from ..models import Saga
from ..print_layout import PrintOptions
from . import printing as print_forms

#: A Markdown file's suffix.
SUFFIX = ".md"

#: Hands the written words to a browser to download (a hosted copy's
#: player), by file name; what to tell.
Deliver = Callable[[str, str], list[str]]


def markdown_path(values: dict[str, Any]) -> Path:
    """The form's file, with .md on the end if it has none."""
    name = (values.get("file") or "").strip().strip('"')
    path = Path(name).expanduser()
    if name and path.suffix.lower() != SUFFIX:
        path = path.with_name(path.name + SUFFIX)
    return path


def export_markdown(
    saga: Saga, record: Any, folder: Path, deliver: Deliver | None = None
) -> Form | Refuse:
    """Export `record`'s sheet as Markdown: its copy and sheet, then the
    file (in the exports `folder`), or with `deliver` straight to a
    browser."""
    kind = print_records.kind_of(record)
    if kind is None:
        return Refuse("Export as Markdown", "This page has no sheet to export.")
    asks_copy = print_forms.offers_copy(saga)
    character = kind == "character"
    default = folder / f"{print_records.file_stem(record.name or 'Untitled')}{SUFFIX}"

    def fields() -> list[DialogField]:
        saved = print_forms.saved_options()
        found = [
            f
            for f in print_forms.print_fields(
                saved, character=character, asks_copy=asks_copy
            )
            if f.key in ("copy", "sheet")
        ]
        if deliver is None:
            found.append(
                DialogField(
                    "file",
                    "File",
                    "text",
                    str(default),
                    hint="A Markdown file: any text editor, wiki or notes app "
                    "reads it.",
                )
            )
        return found

    def problem(values: dict[str, Any]) -> str | None:
        if deliver is not None:
            return None
        if not (values.get("file") or "").strip():
            return "Give the file to write."
        if markdown_path(values).is_dir():
            return "That is a folder: add a file name."
        return None

    def live(values: dict[str, Any]) -> str:
        if deliver is not None or problem(values):
            return ""
        path = markdown_path(values)
        if path.exists():
            return todo(f"{escape(path.name)} exists: it will be replaced.")
        return f"[dim]Writes {escape(str(path))}[/]"

    def apply(values: dict[str, Any]) -> list[str] | Refuse:
        options: PrintOptions = print_forms.options_from(values, asks_copy=asks_copy)
        doc = print_records.document(saga, kind, record, options, viewing.current())
        words = markdown_sheet.render(doc)
        if deliver is not None:
            return deliver(default.name, words)
        path = markdown_path(values)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(words, encoding="utf-8")
        except OSError as problem_found:
            return Refuse(
                "Export as Markdown",
                f"Couldn't write {escape(path.name)}: {escape(str(problem_found))}",
            )
        return [f"Exported {escape(record.name)} as Markdown to {escape(str(path))}."]

    return Form(
        f"Export {escape(record.name)} as Markdown",
        fields,
        apply,
        validate=problem,
        live=live,
        save_label="Export",
        help_id="export-markdown",
    )

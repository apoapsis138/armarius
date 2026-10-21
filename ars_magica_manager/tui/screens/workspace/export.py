"""WorkspaceScreen's export actions: a record, the saga or a pack written to a
file, and a record updated from one."""

from __future__ import annotations

import io
import json
from pathlib import Path
from typing import Any

from .... import packs, storage, transfer
from ....forms import importing as import_forms
from ....forms import menu as menu_forms
from ....markup import escape
from ..prompts import (
    _export_dialog,
)
from ..steps import run_steps
from .base import WorkspaceBase


class ExportActions(WorkspaceBase):
    def action_export_record(self) -> None:
        """More's Export on a covenant, laboratory or character: write it to a file
        that another saga can import."""
        record = self._record_to_export()
        if record is None:
            return

        def handle_result(result: tuple[Path, bool] | None) -> None:
            if result is None:
                return
            path, with_members = result
            if self.app.is_web:
                # A browser copy: the file goes to the player's
                # computer as a download, not to a folder on the host.
                data = transfer.export_data(
                    self.saga, record, with_members=with_members
                )
                if not self._is_storyguide():
                    data = transfer.without_secrets(data)
                self.app.deliver_binary(
                    io.BytesIO(json.dumps(data, indent=2).encode("utf-8")),
                    save_filename=path.name,
                    mime_type="application/json",
                )
                self.notify(
                    f"Exported {escape(record.name)}: your browser downloads it."
                )
                return
            try:
                transfer.export_to(path, self.saga, record, with_members=with_members)
            except OSError as problem:
                self.notify(
                    f"Couldn't write {escape(path.name)}: {escape(str(problem))}",
                    severity="error",
                )
                return
            self.notify(f"Exported {escape(record.name)} to {escape(str(path))}.")

        self.app.push_screen(_export_dialog(record, storage.EXPORTS_DIR), handle_result)

    def action_export_saga(self) -> None:
        """More's Export Saga on the saga: write every record to a file
        that Import reads back (A Whole Saga)."""
        if self.app.is_web:
            # A browser copy: the file goes to the player's computer.
            data = transfer.export_saga_data(self.saga)
            self.app.deliver_binary(
                io.BytesIO(json.dumps(data, indent=2).encode("utf-8")),
                save_filename=transfer.saga_file_name(self.saga),
                mime_type="application/json",
            )
            self.notify(
                f"Exported {escape(self.saga.name)}: your browser downloads it."
            )
            return

        def done(end: object) -> None:
            if isinstance(end, list) and end:
                self.notify("\n".join(end))

        run_steps(
            self.app, menu_forms.export_saga(self.saga, storage.EXPORTS_DIR), done
        )

    def action_export_pack(self) -> None:
        """More's Export Pack on the saga: write the chosen Tribunals,
        covenants, places and neighbours to a content pack."""

        def download(name: str, data: dict[str, Any]) -> list[str]:
            self.app.deliver_binary(
                io.BytesIO(json.dumps(data, indent=2).encode("utf-8")),
                save_filename=name,
                mime_type="application/json",
            )
            return [f"Exported {escape(data['name'])}: your browser downloads it."]

        # A browser copy: the file goes to the player's computer.
        deliver = download if self.app.is_web else None

        def done(end: object) -> None:
            if isinstance(end, list) and end:
                self.notify("\n".join(end))

        run_steps(
            self.app, packs.export_pack(self.saga, storage.EXPORTS_DIR, deliver), done
        )

    def action_update_record(self) -> None:
        """More's Update from a File on a covenant, laboratory or
        character: read an export of it over it, after showing what
        changes."""
        record = self._record_to_export()
        if record is None:
            return

        def done(end: object) -> None:
            if not isinstance(end, list):
                return
            view = self._current_sheet_view()
            self._commit(*(view._refreshers if view is not None else ()), tree=True)
            if end:
                self.notify("\n".join(end))

        run_steps(self.app, import_forms.update_record(self.saga, record), done)

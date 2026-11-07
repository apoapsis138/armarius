"""Setup for a throwaway probe script that looks at the real app.

    import sys; sys.path.insert(0, "<repo>/tools")
    import probe_kit            # before any ars_magica_manager import
    from probe_kit import temp_saga, tui_dump, window_png

Importing it makes a probe safe to run: sounds off, Qt offscreen, UTF-8
output (a bare print of a glyph like the eye crashes the Windows console),
the repo and tests/ on sys.path.

* `temp_saga(saga_id=None, saga=None)` -- a context manager that points the
  data folder at a temp dir holding a copy of the real save (the first, or
  `saga_id`) or an in-memory `Saga`, so the real files are never written.
* `await tui_dump(app, pilot, label, out)` -- appends `===== label` and the
  screen's lines to the UTF-8 file `out`; slice it afterwards with
  `awk '/=====/{keep=($0 ~ /label/)} keep'`.
* `window_png(window, path)` -- saves a desktop window or dialog as a PNG
  (fonts registered first).

`uv run python tools/probe_kit.py` dumps the workspace at 140x60 and 120x45
into `probe_out.txt` in the current folder.
"""

from __future__ import annotations

import asyncio
import contextlib
import importlib
import json
import os
import sys
import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import Any

os.environ["ARMARIUS_SOUNDS"] = "off"
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
for folder in (ROOT, ROOT / "tests"):
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))

from ars_magica_manager import paths, storage
from ars_magica_manager.models import Saga


@contextlib.contextmanager
def temp_saga(saga_id: str | None = None, saga: Saga | None = None) -> Generator[str]:
    """Use a temp data folder holding one saga; yields its id."""
    source = ""
    if saga is None:
        saga_id = saga_id or storage.list_sagas()[0]
        source = (storage.sagas_dir() / f"{saga_id}.json").read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory() as tmp:
        paths.use_data_dir(Path(tmp))
        try:
            storage.sagas_dir().mkdir(parents=True, exist_ok=True)
            if saga is not None:
                storage.save_saga(saga)
                yield saga.id
            else:
                assert saga_id is not None
                json.loads(source)
                (storage.sagas_dir() / f"{saga_id}.json").write_text(
                    source, encoding="utf-8"
                )
                yield saga_id
        finally:
            paths.use_data_dir(None)


async def tui_dump(app: Any, pilot: Any, label: str, out: Path) -> None:
    """Append the screen as it renders, under a `===== label` line."""
    support = importlib.import_module("support")  # tests/support.py

    await pilot.pause()
    with out.open("a", encoding="utf-8") as handle:
        handle.write(f"===== {label}\n")
        handle.write("\n".join(support.screen_lines(app)) + "\n")


def window_png(window: Any, path: Path) -> None:
    """Save a desktop window or dialog as a PNG, styled as the app is."""
    from PySide6.QtWidgets import QApplication

    from ars_magica_manager.gui.style.fonts import register_fonts

    app = QApplication.instance() or QApplication([])
    register_fonts()
    window.show()
    app.processEvents()
    window.grab().save(str(path))


async def _demo(out: Path) -> None:
    from ars_magica_manager.tui.app import ArsMagicaManagerApp
    from ars_magica_manager.tui.screens import WorkspaceScreen

    for size in ((140, 60), (120, 45)):
        app = ArsMagicaManagerApp()
        async with app.run_test(size=size) as pilot:
            await pilot.pause()
            await pilot.press("enter")
            for _ in range(100):
                if isinstance(app.screen, WorkspaceScreen):
                    break
                await pilot.pause(0.05)
            await tui_dump(app, pilot, f"workspace {size[0]}x{size[1]}", out)


if __name__ == "__main__":
    target = Path("probe_out.txt")
    target.unlink(missing_ok=True)
    with temp_saga():
        asyncio.run(_demo(target))
    print(f"wrote {target.resolve()}")

"""Setup for a throwaway probe script that looks at the real app.

    import sys; sys.path.insert(0, "<repo>/tools")
    import probe_kit            # before any ars_magica_manager import
    from probe_kit import temp_saga, tui_dump, window_png

Importing it makes a probe safe to run: sounds and motion off, Qt offscreen, UTF-8
output (a bare print of a glyph like the eye crashes the Windows console),
the repo and tests/ on sys.path.

* `temp_saga(saga_id=None, saga=None)` -- a context manager that points the
  data folder at a temp dir holding a copy of the real save (the first, or
  `saga_id`) or an in-memory `Saga`, so the real files are never written.
* `real_saves()` -- each real save's id and parsed data, read-only, for a
  scan over every save (`for saga_id, data in real_saves(): ...`).
* `await tui_dump(app, pilot, label, out)` -- appends `===== label` and the
  screen's lines to the UTF-8 file `out`; slice it afterwards with
  `awk '/=====/{keep=($0 ~ /label/)} keep'`.
* `desktop(theme=0)` -- dresses Qt as the desktop window does (fonts, app
  font, style sheet, gilding) in that palette, saved as the theme so a
  MainWindow opens in it; inside `temp_saga()` only. Returns the palette.
* `window_png(window, path, size=None)` -- saves a desktop window or dialog
  as a PNG, after `desktop()`.
* `contact_sheet(pngs, out)` -- one scaled PNG of many: look at that.

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
# No fades: a picture taken mid-fade comes out blank.
os.environ["ARMARIUS_MOTION"] = "off"
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


def real_saves() -> Generator[tuple[str, dict[str, Any]]]:
    """Each real save's id and data, read-only: for a scan over every save
    (a new check refusing none of them). Hands out parsed data, never a
    path, so nothing here can write a real file. Call it before temp_saga()
    points the data folder elsewhere."""
    for path in sorted(storage.sagas_dir().glob("*.json")):
        yield path.stem, json.loads(path.read_text(encoding="utf-8"))


async def tui_dump(app: Any, pilot: Any, label: str, out: Path) -> None:
    """Append the screen as it renders, under a `===== label` line."""
    support = importlib.import_module("support")  # tests/support.py

    await pilot.pause()
    with out.open("a", encoding="utf-8") as handle:
        handle.write(f"===== {label}\n")
        handle.write("\n".join(support.screen_lines(app)) + "\n")


def desktop(theme: int = 0) -> Any:
    """The QApplication, dressed as the desktop window dresses it (fonts,
    app font, style sheet, gilding) in PALETTES[theme], which is also saved
    as the theme, so a MainWindow made afterwards opens in it. Call it
    inside temp_saga() (or another temp data folder): it writes the
    settings. Returns the palette."""
    # start-up: Qt loads only for desktop probes, not terminal ones.
    from PySide6.QtWidgets import QApplication

    from ars_magica_manager.gui import pictures, themes
    from ars_magica_manager.gui.window import dress_application

    if paths.data_dir() == paths.default_data_dir():
        raise RuntimeError("desktop() would write the real settings: use temp_saga()")
    os.environ.setdefault("QT_QPA_FONTDIR", "C:/Windows/Fonts")
    found = QApplication.instance()
    app = found if isinstance(found, QApplication) else QApplication([])
    pictures.register_fonts()
    p = themes.PALETTES[theme]
    themes.remember_theme(theme)
    dress_application(app, p)
    return p


def window_png(window: Any, path: Path, size: tuple[int, int] | None = None) -> Path:
    """Save a desktop window or dialog as a PNG (after desktop()), resized
    to `size` first if given."""
    from PySide6.QtWidgets import QApplication

    if size is not None:
        window.resize(*size)
    window.show()
    for _ in range(8):
        QApplication.processEvents()
    window.grab().save(str(path))
    return path


def contact_sheet(
    pictures: list[Path], out: Path, across: int = 3, width: int = 600
) -> Path:
    """One PNG of `pictures`, `across` to a row, each scaled to `width`:
    look at this, not each picture alone (one image read, not a dozen)."""
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QColor, QPainter, QPixmap

    gap = 20
    tiles = [
        QPixmap(str(p)).scaledToWidth(width, Qt.TransformationMode.SmoothTransformation)
        for p in pictures
    ]
    rows = [tiles[i : i + across] for i in range(0, len(tiles), across)]
    heights = [max(tile.height() for tile in row) for row in rows]
    sheet = QPixmap(across * (width + gap) + gap, sum(heights) + gap * (len(rows) + 1))
    sheet.fill(QColor("#808080"))
    painter = QPainter(sheet)
    y = gap
    for row, height in zip(rows, heights, strict=True):
        for i, tile in enumerate(row):
            painter.drawPixmap(gap + i * (width + gap), y, tile)
        y += height + gap
    painter.end()
    sheet.save(str(out))
    return out


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

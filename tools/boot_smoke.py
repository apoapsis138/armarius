"""Start both front-ends, as a person would, on a throwaway saga.

    uv run python tools/boot_smoke.py

The terminal app opens on its title page and goes on into the saga; the
desktop window opens with the same saga. Each runs offscreen
in a temp data folder, so the real saves and settings are never touched.
Prints one line per front-end; one that fails to start ends the run with
its traceback and a nonzero exit code. `story_check.py --full` runs it last.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import probe_kit  # before any ars_magica_manager import

from ars_magica_manager.models import Covenant, Saga

#: The terminal size the app is started at: the one the user works at.
SIZE = (140, 60)


def boot_saga() -> Saga:
    """A small saga for the windows to open."""
    covenant = Covenant(id="cov", saga_id="boot", name="Keep")
    return Saga(id="boot", name="Boot", covenants=[covenant])


async def _terminal() -> str:
    # start-up: the terminal app loads only for this check.
    from ars_magica_manager.tui.app import ArsMagicaManagerApp

    app = ArsMagicaManagerApp()
    app.show_title = True
    seen = []
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        seen.append(type(app.screen).__name__)
        await pilot.press("enter")  # past the title page, into the saga
        await pilot.pause()
        seen.append(type(app.screen).__name__)
    if seen[-1] != "WorkspaceScreen":
        raise RuntimeError(f"didn't reach the saga: {' -> '.join(seen)}")
    return " -> ".join(seen)


def terminal() -> str:
    return asyncio.run(_terminal())


def desktop() -> str:
    # start-up: Qt loads only for the desktop check.
    from PySide6.QtWidgets import QApplication

    from ars_magica_manager.gui.window import MainWindow

    probe_kit.desktop()
    window = MainWindow(saga_ids=["boot"])
    window.show()
    for _ in range(8):
        QApplication.processEvents()
    name = type(window).__name__
    window.close()
    return name


def main() -> int:
    """Each front-end in turn; one that fails to start ends the run with
    its traceback (exit code 1)."""
    with probe_kit.temp_saga(saga=boot_saga()):
        print(f"ok    terminal boots: {terminal()}")
        print(f"ok    desktop boots: {desktop()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Time what the app does, against a copy of a real saga (STORY-1118).

    uv run python tools/perf_probe.py [saga_id] [--scale N] [--profile OUT]

Works on a temporary copy: the saga file and app settings are never
written. Reports, in milliseconds:

* file: reading + parsing the saga, and saving it (what every edit does);
* catalogs: the first (uncached) load of each reference catalog;
* ui: booting to the saga picker, opening the workspace, showing every
  tree node, switching to every tab of each sheet, refreshing all of a
  sheet's sections (what an edit redraws), and a full `_commit` of one
  section (save + refresh).

`--scale N` multiplies the saga's characters, familiars and books N times
(new ids), to see how times grow with a bigger saga. `--profile OUT`
runs the UI pass under cProfile and writes the stats to OUT (and prints
the top functions by cumulative time).
"""

from __future__ import annotations

import argparse
import asyncio
import copy
import cProfile
import io
import json
import pstats
import sys
import tempfile
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ars_magica_manager import DATA_DIR, catalog, settings, storage
from ars_magica_manager.models import Saga

SIZE = (140, 60)
#: Also wait for animations (the tab underline slide) to finish.
WAIT_ANIMATIONS = False
SHEETS = {"covenant", "character", "laboratory", "familiar"}


def _ms(seconds: float) -> str:
    return f"{seconds * 1000:8.1f}"


def _time(fn: Callable[[], Any], repeat: int = 5) -> float:
    """Best of `repeat` runs, in seconds."""
    best = float("inf")
    for _ in range(repeat):
        start = time.perf_counter()
        fn()
        best = min(best, time.perf_counter() - start)
    return best


def scaled(data: dict[str, Any], factor: int) -> dict[str, Any]:
    """`data` (a saga's JSON) with its characters, familiars and books
    repeated `factor` times under new ids."""
    if factor <= 1:
        return data
    data = copy.deepcopy(data)
    for key in ("characters", "familiars", "books"):
        originals = list(data[key])
        for n in range(2, factor + 1):
            for entry in originals:
                clone = copy.deepcopy(entry)
                clone["id"] = f"{entry['id']}_x{n}"
                if "name" in clone:
                    clone["name"] = f"{entry['name']} {n}"
                if key == "familiars" and clone.get("character_id"):
                    clone["character_id"] = f"{clone['character_id']}_x{n}"
                data[key].append(clone)
    return data


def file_timings(saga_id: str) -> None:
    path = storage.saga_path(saga_id)
    size = path.stat().st_size
    print(f"\n== file ({size / 1024:.0f} KB)")
    text = path.read_text(encoding="utf-8")
    print(f"{_ms(_time(lambda: json.loads(text)))}  json.loads")
    data = json.loads(text)
    print(f"{_ms(_time(lambda: Saga.from_dict(data)))}  Saga.from_dict")
    print(f"{_ms(_time(lambda: storage.load_saga(saga_id)))}  load_saga (all)")
    saga = storage.load_saga(saga_id)
    print(f"{_ms(_time(lambda: storage.save_saga(saga)))}  save_saga")


def catalog_timings() -> None:
    print("\n== catalogs (first, uncached load)")
    loaders = [
        ("virtue/flaw", catalog.load_virtue_flaw_catalog, "virtue_flaw_catalog"),
        ("spells", catalog.load_spell_catalog, "spell_catalog"),
        (
            "boons/hooks",
            catalog.load_covenant_boon_hook_catalog,
            "covenant_boon_hook_catalog",
        ),
        ("abilities", catalog.load_ability_catalog, "ability_catalog"),
        ("lab features", catalog.load_lab_feature_catalog, "lab_feature_catalog"),
    ]
    for label, load, file in loaders:
        kb = (DATA_DIR / f"{file}.json").stat().st_size / 1024
        start = time.perf_counter()
        load()
        first = time.perf_counter() - start
        again = _time(load)
        print(f"{_ms(first)}  {label} ({kb:.0f} KB); cached call {again * 1e6:.0f} us")


async def _settle(pilot) -> None:
    await pilot.pause()
    if WAIT_ANIMATIONS:
        await pilot.wait_for_scheduled_animations()
    await pilot.pause()


async def _until(pilot, condition, timeout: float = 30.0) -> None:
    start = time.perf_counter()
    while not condition():
        if time.perf_counter() - start > timeout:
            raise TimeoutError
        await pilot.pause(0.005)


async def ui_timings(rows: list[tuple[str, float]]) -> None:
    from textual.widgets import TabbedContent, TabPane, Tree

    from ars_magica_manager.app import ArsMagicaManagerApp
    from ars_magica_manager.screens import SagaPickerScreen, WorkspaceScreen

    app = ArsMagicaManagerApp()
    start = time.perf_counter()
    async with app.run_test(size=SIZE) as pilot:
        await _until(pilot, lambda: isinstance(app.screen, SagaPickerScreen))
        await _settle(pilot)
        rows.append(("boot to saga picker", time.perf_counter() - start))

        start = time.perf_counter()
        await pilot.press("enter")
        await _until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        workspace = app.screen
        assert isinstance(workspace, WorkspaceScreen)
        await _settle(pilot)
        rows.append(("open workspace", time.perf_counter() - start))

        tree = workspace.query_one(Tree)
        nodes = []
        stack = [tree.root]
        while stack:
            node = stack.pop()
            if node.data is not None:
                nodes.append(node)
            stack.extend(reversed(node.children))

        for node in nodes:
            kind = str(node.data[0])
            label = f"{kind}:{node.data[1] if len(node.data) > 1 else ''}"
            start = time.perf_counter()
            tree.select_node(node)
            await _until(
                pilot, lambda node=node: workspace.selected_kind == node.data[0]
            )
            view = None
            if kind in SHEETS:
                await _until(pilot, lambda: workspace._current_sheet_view() is not None)
                view = workspace._current_sheet_view()
                assert view is not None
                await _until(pilot, lambda view=view: view.initial_tab_seen)
            await _settle(pilot)
            rows.append((f"show {label}", time.perf_counter() - start))
            if view is None:
                continue
            tabbed = next(iter(view.query(TabbedContent)), None)
            if tabbed is not None:
                panes = list(tabbed.query(TabPane))
                for tab in panes[1:] + panes[:1]:
                    start = time.perf_counter()
                    app.screen.set_focus(None)
                    tabbed.active = tab.id or ""
                    await _until(
                        pilot,
                        lambda tabbed=tabbed, tab=tab: tabbed.active == tab.id,
                    )
                    await _settle(pilot)
                    rows.append((f"  tab {tab.id}", time.perf_counter() - start))
            sections = list(view._refreshers)
            start = time.perf_counter()
            for section in sections:
                view.refresh_section(section)
            await _settle(pilot)
            rows.append(
                (f"  refresh all {len(sections)} sections", time.perf_counter() - start)
            )
            # The most expensive single section, as one edit would redraw it.
            worst, worst_t = "", 0.0
            for section in sections:
                start = time.perf_counter()
                workspace._commit(section)
                await _settle(pilot)
                elapsed = time.perf_counter() - start
                if elapsed > worst_t:
                    worst, worst_t = section, elapsed
            rows.append((f"  slowest one-section edit ({worst})", worst_t))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("saga_id", nargs="?", default=None)
    parser.add_argument("--scale", type=int, default=1)
    parser.add_argument("--profile", type=Path, default=None)
    parser.add_argument("--no-ui", action="store_true")
    args = parser.parse_args()

    real_dir = storage.SAGAS_DIR
    saga_id = args.saga_id or storage.list_sagas()[0]
    data = json.loads((real_dir / f"{saga_id}.json").read_text(encoding="utf-8"))

    with tempfile.TemporaryDirectory() as tmp:
        storage.SAGAS_DIR = Path(tmp) / "sagas"
        storage.SAGAS_DIR.mkdir()
        settings.SETTINGS_PATH = Path(tmp) / "app_settings.json"
        (storage.SAGAS_DIR / f"{saga_id}.json").write_text(
            json.dumps(scaled(data, args.scale), indent=2), encoding="utf-8"
        )
        print(f"saga {saga_id}, scale x{args.scale}")
        catalog_timings()
        file_timings(saga_id)
        if args.no_ui:
            return
        rows: list[tuple[str, float]] = []
        profiler = cProfile.Profile() if args.profile else None
        if profiler:
            profiler.enable()
        asyncio.run(ui_timings(rows))
        if profiler:
            profiler.disable()
            profiler.dump_stats(args.profile)
        print(f"\n== ui at {SIZE[0]}x{SIZE[1]} (includes Pilot's settle, ~a few ms)")
        for label, seconds in rows:
            print(f"{_ms(seconds)}  {label}")
        if profiler:
            out = io.StringIO()
            pstats.Stats(profiler, stream=out).sort_stats("cumulative").print_stats(60)
            print(out.getvalue())


if __name__ == "__main__":
    main()

"""Rebuild the tutorial sagas in data/tutorials from the guides' start
saves in the sagas folder, each opened and saved again by the app as it is
now, so every change to the save format is applied.

    uv run python tools/build_tutorials.py [--book PATH]

The start saves are the sagas named "NN_title.json" (01 to 17, one per
walkthrough guide) in the sagas folder in use (paths.data_dir()). --book
copies the walkthroughs' compiled book (the phone-sized master tome) in as
data/tutorials/The Walkthroughs.pdf. The folder's other tutorials are
replaced; a tutorial with no save beside it is left alone and named.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ars_magica_manager import __version__, storage, tutorials

_START_SAVE = re.compile(r"^\d{2}_.+$")


def main() -> int:
    parser = argparse.ArgumentParser(description="Rebuild the tutorial sagas.")
    parser.add_argument("--book", type=Path, help="the compiled walkthroughs PDF")
    args = parser.parse_args()
    found = [s for s in storage.list_sagas() if _START_SAVE.match(s)]
    if not found:
        print(f"No guide start saves (NN_title.json) in {storage.sagas_dir()}.")
        return 1
    tutorials.TUTORIALS_DIR.mkdir(parents=True, exist_ok=True)
    for saga_id in sorted(found):
        saga = storage.load_saga(saga_id)
        target = tutorials.TUTORIALS_DIR / f"{saga_id}.json"
        saga.app_version = __version__
        target.write_text(json.dumps(asdict(saga), indent=2), encoding="utf-8")
        print(f"{saga_id}: {saga.name}, {saga.current_season} {saga.current_year}")
    stale = sorted(
        p.name for p in tutorials.TUTORIALS_DIR.glob("*.json") if p.stem not in found
    )
    if stale:
        print("Left alone (no start save for them):", ", ".join(stale))
    if args.book:
        shutil.copy2(args.book, tutorials.GUIDE_BOOK)
        print(f"Book: {tutorials.GUIDE_BOOK.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

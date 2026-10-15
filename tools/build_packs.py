"""Build the shipped content packs (data/packs/*.amm.json) from the book
modules in ars_magica_manager/book_packs: run after changing a book's
module or the save format.

    uv run python tools/build_packs.py [folder]
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ars_magica_manager import book_packs, packs


def main(argv: list[str]) -> int:
    folder = Path(argv[1]) if len(argv) > 1 else book_packs.PACKS_DIR
    for path in book_packs.write_all(folder):
        print(f"{path}: {packs.summary(packs.transfer.read(path))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

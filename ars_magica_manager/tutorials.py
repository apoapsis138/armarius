"""The tutorial sagas: the walkthrough guides' starting states, shipped
with the app in data/tutorials. Starting one copies it into the sagas
folder as a saga of its own, with an id no saved saga uses, so it can be
started again from the beginning at any time. The guides themselves ship
beside them as one book, the walkthroughs' master tome.

A tutorial file is a saved saga, named "NN_title.json" for its guide's
number; it is read as a saga file is opened (storage.saga_from_data).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from . import DATA_DIR, storage
from .models import Saga

#: The tutorial sagas shipped with the app.
TUTORIALS_DIR = DATA_DIR / "tutorials"
#: The walkthrough guides, all in one book sized for reading on a phone.
GUIDE_BOOK = TUTORIALS_DIR / "The Walkthroughs.pdf"

_FILE = re.compile(r"^(\d+)_.+\.json$")
#: A saga name's leading guide number ("03 A Year at Rabenstein").
_NUMBERED = re.compile(r"^\d+\s+")


@dataclass(frozen=True)
class Tutorial:
    #: The guide's number in the walkthroughs.
    number: int
    #: The guide's title, the saga's name.
    title: str
    #: Its opening date, as "Spring 1220".
    when: str
    path: Path

    @property
    def label(self) -> str:
        """As the list shows it: "3. A Year at Rabenstein (Spring 1220)"."""
        return f"{self.number}. {self.title} ({self.when})"


def listed(folder: Path = TUTORIALS_DIR) -> list[Tutorial]:
    """Every tutorial in `folder`, by guide number. A file that can't be
    read as a saga's data raises ValueError naming it."""
    found = []
    for path in folder.glob("*.json"):
        match = _FILE.match(path.name)
        if match is None:
            continue
        data = _data(path)
        found.append(
            Tutorial(
                int(match.group(1)),
                _NUMBERED.sub("", str(data.get("name") or path.stem)),
                f"{data.get('current_season', '')} {data.get('current_year', '')}".strip(),
                path,
            )
        )
    return sorted(found, key=lambda t: t.number)


def _data(path: Path) -> dict[str, object]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"The tutorial {path.name} can't be read: {error}") from None
    if not isinstance(data, dict):
        raise ValueError(f"The tutorial {path.name} isn't a saga's data.")
    return data


def start(tutorial: Tutorial) -> Saga:
    """A fresh copy of `tutorial` as a saga of the user's own, saved under
    an id no saved saga uses, so starting it twice gives two sagas."""
    saga = storage.saga_from_data(_data(tutorial.path))
    saga.name = tutorial.title
    saga.id = storage.generate_saga_id(tutorial.title)
    for covenant in saga.covenants:
        covenant.saga_id = saga.id
    storage.save_saga(saga)
    return saga

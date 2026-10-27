"""A saga's own Mystery Cult to a file and back: Export a Cult writes one
cult (its Lore, degrees, Scripts and their components) as JSON, and
Import Data's A Mystery Cult reads it into another saga's own cults
(Saga Content). The file is checked once as it is read, with a message
naming what is wrong."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from . import __version__
from . import mystery_cults as mc
from .files import write_atomic
from .models import MysteryCult, Saga

FORMAT = "armarius-cult"
SUFFIX = ".cult.json"


def file_name(cult: MysteryCult) -> str:
    stem = "".join(ch for ch in cult.name if ch.isalnum() or ch in " -_").strip()
    return f"{stem or 'Mystery Cult'}{SUFFIX}"


def export_data(cult: MysteryCult) -> dict[str, Any]:
    return {"format": FORMAT, "version": __version__, "cult": asdict(cult)}


def export_to(path: Path, cult: MysteryCult) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    write_atomic(path, json.dumps(export_data(cult), indent=2))
    return path


def read(path: Path) -> MysteryCult:
    """The cult a file holds. Raises ValueError for anything else."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as problem:
        raise ValueError(f"not a JSON file ({problem.msg})") from problem
    if not isinstance(data, dict) or data.get("format") != FORMAT:
        raise ValueError(
            "not a Mystery Cult export (export one with More's Export a "
            "Cult on Saga Content first)"
        )
    cult = data.get("cult")
    if not isinstance(cult, dict):
        raise ValueError("the export holds no cult")
    return MysteryCult.from_dict(cult)


def add(saga: Saga, cult: MysteryCult) -> MysteryCult:
    """Add `cult` to the saga's own cults with an id of its own, and a name
    marked as imported when the saga has one of that name already. Its
    founder was a character of the other saga, so the link is dropped."""
    names = {c.name for c in saga.custom_cults}
    if cult.name in names:
        cult.name = f"{cult.name} (imported)"
    cult.id = mc.new_cult_id(saga, cult.name)
    cult.founder_id = ""
    saga.custom_cults.append(cult)
    mc.changed(saga)
    return cult

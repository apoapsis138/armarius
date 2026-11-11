"""A character's portrait: a picture chosen from anywhere on the computer
and copied into the save folder's portraits folder, so it travels with the
saves and survives the original being moved or deleted.

The saga holds only the copy's file name (Character.portrait); a name whose
file is missing (a character imported from another computer) shows no
portrait, as does an older save, which has none.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from . import storage
from .commands import Choice, Choose, ChooseFile, Command
from .markup import escape
from .models import Character, Saga
from .picture_files import SUFFIXES, safe_name


def path(character: Character) -> Path | None:
    """The character's portrait file, if they have one and it is there."""
    if not safe_name(character.portrait):
        return None
    found = storage.portraits_dir() / character.portrait
    return found if found.is_file() else None


def file_name(saga: Saga, character: Character, suffix: str) -> str:
    """The copy's name: the saga's and character's ids, so no two
    characters share one."""
    return f"{saga.id}--{character.id}{suffix.lower()}"


def set_portrait(saga: Saga, character: Character, picture: Path) -> None:
    """Copy `picture` into the portraits folder as the character's
    portrait, in place of any they had."""
    if picture.suffix.lower() not in SUFFIXES:
        raise ValueError(f"{picture.name} isn't a picture.")
    folder = storage.portraits_dir()
    folder.mkdir(parents=True, exist_ok=True)
    name = file_name(saga, character, picture.suffix)
    old = path(character)
    shutil.copyfile(picture, folder / name)
    if old is not None and old.name != name:
        old.unlink(missing_ok=True)
    character.portrait = name


def remove_portrait(character: Character) -> None:
    """Take the portrait off (its copy in the portraits folder goes too)."""
    old = path(character)
    if old is not None:
        old.unlink(missing_ok=True)
    character.portrait = ""


def _pictures_folder() -> Path:
    home = Path.home()
    pictures = home / "Pictures"
    return pictures if pictures.is_dir() else home


def choose_picture(saga: Saga, character: Character) -> ChooseFile:
    return ChooseFile(
        f"A portrait of {escape(character.name)}",
        SUFFIXES[0],
        _pictures_folder(),
        lambda picture: set_portrait(saga, character, picture),
        more=SUFFIXES[1:],
    )


def portrait(saga: Saga, character: Character) -> Command:
    """Choose the character's portrait: straight to the pictures while
    they have none, else a new one or none."""
    if path(character) is None:
        return choose_picture(saga, character)

    def chosen(key: str) -> Command | None:
        if key == "choose":
            return choose_picture(saga, character)
        remove_portrait(character)
        return None

    return Choose(
        f"Portrait of {escape(character.name)}",
        lambda: [
            Choice("Choose another picture", "choose", "Copied into the save folder."),
            Choice(
                "Remove the portrait", "remove", "The sheet shows the House symbol."
            ),
        ],
        chosen,
    )

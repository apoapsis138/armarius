"""Take Up the Tale on a chosen row, for either front-end: an open story
in a covenant's Diary or the Region's Open Stories, or a story or threat
on Needs You (story_chapters writes the chapter). On a threat's own page
it acts on the threat (story_chapters.take_up_threat).

Pattern: Strategy as a dict, one function per list, each finding what
its chosen row takes up."""

from __future__ import annotations

from collections.abc import Callable

from .. import attention, open_stories, story_chapters
from ..commands import Command, Refuse
from ..models import Covenant, Saga
from ..sections import ATTENTION_SECTION, COV_DIARY_TAB, REGION_STORIES_SECTION

_NONE = Refuse(story_chapters.TAKE_UP, "Choose an open story or a threat first.")


def _region(saga: Saga, row: int, _covenant: Covenant | None) -> Command | None:
    found = open_stories.stories(saga)
    if not 0 <= row < len(found):
        return None
    story = found[row]
    return story_chapters.take_up_story(saga, story.covenant, story.entry)


def _diary(saga: Saga, row: int, covenant: Covenant | None) -> Command | None:
    if covenant is None or not 0 <= row < len(covenant.diary):
        return None
    entry = covenant.diary[row]
    if not story_chapters.is_open(entry):
        return None
    return story_chapters.take_up_story(saga, covenant, entry)


def _attention(saga: Saga, row: int, _covenant: Covenant | None) -> Command | None:
    found = attention.items(saga)
    if not 0 <= row < len(found) or found[row].take_up is None:
        return None
    take_up = found[row].take_up
    assert take_up is not None
    return take_up()


#: Each list Take Up the Tale is offered on, and what its row takes up.
LISTS: dict[str, Callable[[Saga, int, Covenant | None], Command | None]] = {
    REGION_STORIES_SECTION: _region,
    COV_DIARY_TAB: _diary,
    ATTENTION_SECTION: _attention,
}


def offered(
    saga: Saga, section: str, row: int | None, covenant: Covenant | None
) -> bool:
    """Whether the chosen row of `section` can be taken up."""
    found = LISTS.get(section)
    return (
        found is not None and row is not None and found(saga, row, covenant) is not None
    )


def command(
    saga: Saga, section: str, row: int | None, covenant: Covenant | None
) -> Command:
    """Take Up the Tale on `section`'s chosen row."""
    found = LISTS.get(section)
    step = found(saga, row, covenant) if found is not None and row is not None else None
    return step if step is not None else _NONE

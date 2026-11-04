"""A story's chapters: Take Up the Tale on an open story or a threat,
the last chapter Resolve asks for, a stage's optional chapter, and the
thread from a story into the threat it grew into."""

from __future__ import annotations

from support import everything_saga, strip_markup

from ars_magica_manager import (
    attention,
    connections,
    covenant_diary,
    open_stories,
    story_chapters,
    threats,
)
from ars_magica_manager.commands import Choose, Confirm, Form, Refuse, Then
from ars_magica_manager.forms import diary as diary_forms
from ars_magica_manager.forms import take_up
from ars_magica_manager.models import CHAPTER, STORY_EVENT, CovenantDiaryEntry
from ars_magica_manager.sections import (
    ATTENTION_SECTION,
    COV_DIARY_TAB,
    REGION_STORIES_SECTION,
)


def _saga():
    """The sample saga with its covenant played and one open story."""
    saga = everything_saga()
    covenant = saga.covenants[0]
    covenant.played = True
    covenant.diary.append(
        CovenantDiaryEntry(
            1219, "Spring", "Mother Agathe's silence", "She knows.", STORY_EVENT
        )
    )
    return saga, covenant, covenant.diary[-1]


def _write(form, **values):
    assert isinstance(form, Form)
    shown = {f.key: f.value for f in form.fields()}
    return form.apply({**shown, **values})


def test_taking_up_a_story_writes_a_dated_chapter_in_its_diary():
    saga, covenant, story = _saga()
    form = story_chapters.take_up_story(saga, covenant, story)
    assert isinstance(form, Form) and story_chapters.TAKE_UP in form.title
    fields = {f.key: f.value for f in form.fields()}
    assert (fields["year"], fields["season"]) == (
        saga.current_year,
        saga.current_season,
    )
    _write(form, year=1220, season="Summer", words="We sent Leandro to her.")
    chapter = covenant.diary[-1]
    assert chapter.category == CHAPTER
    assert chapter.name == story.name and chapter.story_id == story.id != ""
    assert (chapter.year, chapter.season) == (1220, "Summer")
    # A chapter is not an open story itself.
    assert [s.entry.name for s in open_stories.stories(saga)] == [story.name]
    thread = strip_markup("\n".join(story_chapters.story_thread(saga, covenant, story)))
    assert "Summer 1220: We sent Leandro to her." in thread
    shown = strip_markup(
        covenant_diary.info_text(covenant, len(covenant.diary) - 1, saga)
    )
    assert f"Chapter of: {story.name}" in shown


def test_chapters_are_listed_oldest_first():
    _unused, covenant, story = _saga()
    story_chapters.write_story_chapter(covenant, story, 1221, "Spring", "Second")
    story_chapters.write_story_chapter(covenant, story, 1220, "Winter", "First")
    assert [c.words for c in story_chapters.story_chapters(covenant, story)] == [
        "First",
        "Second",
    ]


def test_a_told_or_grown_story_is_not_taken_up():
    saga, covenant, story = _saga()
    story.status = "Resolved"
    assert isinstance(story_chapters.take_up_story(saga, covenant, story), Refuse)
    story.status = "Open"
    threat = open_stories.grow(
        saga, open_stories.stories(saga)[0], {"name": "The Silence Spreads"}
    )
    refused = story_chapters.take_up_story(saga, covenant, story)
    assert isinstance(refused, Refuse) and "The Silence Spreads" in refused.why
    assert not take_up.offered(saga, COV_DIARY_TAB, len(covenant.diary) - 1, covenant)
    assert threat.id == story.threat_id


def test_resolving_an_open_story_asks_for_its_last_chapter():
    saga, covenant, story = _saga()
    index = covenant.diary.index(story)
    ops = diary_forms.covenant_diary_ops(saga, covenant)
    assert ops.edit is not None
    form = ops.edit(index)
    assert isinstance(form, Form)
    values = {f.key: f.value for f in form.fields()}
    end = form.apply({**values, "status": "Resolved"})
    assert isinstance(end, Then) and story_chapters.ENDING in end.step.title
    resolved = covenant.diary[index]
    _write(end.step, words="She spoke at last.")
    assert covenant.diary[-1].story_id == resolved.id
    # Editing it again keeps its id, and asks nothing.
    form = ops.edit(index)
    assert isinstance(form, Form)
    values = {f.key: f.value for f in form.fields()}
    assert form.apply(values) is None
    assert covenant.diary[index].id == resolved.id


def test_a_threat_is_taken_up_in_its_diary_and_the_troupe_s():
    saga, covenant, _story = _saga()
    crown = saga.neighbour("crown")
    assert crown is not None
    _write(story_chapters.take_up_threat(saga, crown), words="We rode to the ford.")
    assert crown.details["diary"][-1]["chapter"] is True
    assert covenant.diary[-1].category == CHAPTER
    assert covenant.diary[-1].threat_id == crown.id
    assert [c.words for c in story_chapters.threat_chapters(crown)] == [
        "We rode to the ford."
    ]
    shown = strip_markup(
        covenant_diary.info_text(covenant, len(covenant.diary) - 1, saga)
    )
    assert f"Chapter of: {crown.name} (a threat)" in shown


def test_a_stage_s_outcome_can_take_a_chapter_not_kept_on_the_stage():
    saga, _covenant, _story = _saga()
    crown = saga.neighbour("crown")
    assert crown is not None
    ops = threats.stage_ops(saga, crown)
    assert ops.edit is not None
    form = ops.edit(0)
    assert isinstance(form, Form)
    values = {f.key: f.value for f in form.fields()}
    form.apply({**values, "outcome": "Stopped", "chapter": "We drove the cattle home."})
    assert "chapter" not in threats.stages(crown)[0]
    assert [c.words for c in story_chapters.threat_chapters(crown)] == [
        "Cattle go missing: We drove the cattle home."
    ]


def test_one_thread_runs_from_the_story_into_its_threat():
    saga, covenant, story = _saga()
    story_chapters.write_story_chapter(covenant, story, 1219, "Summer", "First visit")
    threat = open_stories.grow(
        saga, open_stories.stories(saga)[0], {"name": "The Silence Spreads"}
    )
    threats.write_chapter(saga, threat, 1220, "Spring", "The valley falls quiet")
    story_thread = strip_markup(
        "\n".join(story_chapters.story_thread(saga, covenant, story))
    )
    assert story_thread.index("First visit") < story_thread.index("Grew into")
    assert story_thread.index("Grew into") < story_thread.index(
        "The valley falls quiet"
    )
    threat_thread = strip_markup("\n".join(story_chapters.threat_thread(saga, threat)))
    assert threat_thread.index("Grew from") < threat_thread.index("First visit")
    assert "The valley falls quiet" in threat_thread
    header = strip_markup(story_chapters.threat_header(saga, threat))
    assert "First visit" in header and "The valley falls quiet" not in header
    facts = {f.label: f for f in story_chapters.threat_facts(saga, threat)}
    assert facts["Grew from"].refs[0].id == covenant.id
    linked = {f.label: f for f in connections.facts(saga, covenant)}
    assert linked["Stories grown into threats"].refs[0].id == threat.id
    shown = strip_markup(
        covenant_diary.info_text(covenant, covenant.diary.index(story), saga)
    )
    assert "Grew into: The Silence Spreads" in shown


def test_take_up_is_offered_on_an_open_story_s_row_in_each_list():
    saga, covenant, story = _saga()
    index = covenant.diary.index(story)
    assert take_up.offered(saga, COV_DIARY_TAB, index, covenant)
    covenant.diary.append(CovenantDiaryEntry(1219, "Summer", "Bought a mill"))
    other = len(covenant.diary) - 1
    assert not take_up.offered(saga, COV_DIARY_TAB, other, covenant)
    assert take_up.offered(saga, REGION_STORIES_SECTION, 0, None)
    row = next(
        i for i, item in enumerate(attention.items(saga)) if item.title == story.name
    )
    assert take_up.offered(saga, ATTENTION_SECTION, row, None)
    assert isinstance(take_up.command(saga, ATTENTION_SECTION, row, None), Form)
    assert isinstance(take_up.command(saga, "section-nowhere", 0, None), Refuse)


def test_deleting_a_story_with_chapters_asks_what_becomes_of_them():
    saga, covenant, story = _saga()
    story_chapters.write_story_chapter(covenant, story, 1220, "Spring", "A visit")
    ops = diary_forms.covenant_diary_ops(saga, covenant)
    assert ops.remove is not None
    asked = ops.remove(covenant.diary.index(story))
    assert isinstance(asked, Choose) and "1 chapter" in asked.title
    asked.apply(story_chapters.KEEP)
    assert story not in covenant.diary
    assert covenant.diary[-1].category == CHAPTER
    shown = strip_markup(
        covenant_diary.info_text(covenant, len(covenant.diary) - 1, saga)
    )
    assert "Chapter of: a story since deleted" in shown


def test_deleting_a_story_can_take_its_chapters_too():
    saga, covenant, story = _saga()
    story_chapters.write_story_chapter(covenant, story, 1220, "Spring", "A visit")
    before = len(covenant.diary)
    ops = diary_forms.covenant_diary_ops(saga, covenant)
    assert ops.remove is not None
    asked = ops.remove(covenant.diary.index(story))
    assert isinstance(asked, Choose)
    asked.apply(story_chapters.DROP)
    assert len(covenant.diary) == before - 2
    # Anything else is deleted after the usual confirmation.
    covenant.diary.append(CovenantDiaryEntry(1220, "Summer", "Bought a mill"))
    plain = ops.remove(len(covenant.diary) - 1)
    assert isinstance(plain, Confirm)

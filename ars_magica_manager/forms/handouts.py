"""The Handouts list's form, independent of how it is drawn (handouts.py).

Add, Edit and Delete a written Handout. Its form asks for a title, a
Stationery, its text (the app's markup with the six handout tags), up to
four pictures (one already in the saga, or a new file copied into the
handouts folder), who found it, where, and the Story it belongs to. Its
Preview lays what it holds on its Stationery (handout_layout), unsaved.

Pattern: one core Form, with the list's verbs one commands.SectionOps
registered in section_verbs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .. import handouts, scenes
from ..commands import (
    Choice,
    Choose,
    ChooseFile,
    Command,
    Confirm,
    Form,
    Picked,
    SectionOps,
    confirm_delete,
)
from ..form_spec import DialogField, ListEditor
from ..handout_layout import Preview
from ..markup import escape
from ..models import STATIONERY, VELLUM, Handout, Saga
from ..picture_files import SUFFIXES

HANDOUTS_HELP = "handouts-written"

#: A picture choice that opens this computer's files instead.
_NEW = "__new__"


def _choose_file(_current: object) -> ChooseFile:
    home = Path.home()
    start = home / "Pictures" if (home / "Pictures").is_dir() else home
    return ChooseFile(
        "A Handout's picture",
        SUFFIXES[0],
        start,
        lambda chosen: Picked(handouts.new_picture_ref(chosen)),
        more=SUFFIXES[1:],
    )


def _choose_picture(saga: Saga) -> Command:
    def chosen(value: str) -> Any:
        return _choose_file(None) if value == _NEW else Picked(value)

    return Choose(
        "Choose a Picture",
        lambda: [
            Choice("A new picture file...", _NEW),
            *(
                Choice(escape(label), ref)
                for label, ref in handouts.picture_choices(saga)
            ),
        ],
        chosen,
    )


def handout_fields(saga: Saga, existing: Handout | None) -> list[DialogField]:
    stories = scenes.story_options(saga)
    finders = handouts.finder_options(saga)
    places = handouts.place_options(saga)
    return [
        DialogField(
            "title",
            "Title",
            "text",
            existing.title if existing else "",
            required=True,
        ),
        DialogField(
            "stationery",
            "Stationery",
            "select",
            existing.stationery if existing else VELLUM,
            options=[(s.capitalize(), s) for s in STATIONERY],
            hint="What it is drawn on: vellum, a sealed letter or a proclamation.",
        ),
        DialogField(
            "text",
            "Text",
            "area",
            existing.text if existing else "",
            rows=12,
            # Escaped: the tags are words to read here, not markup.
            hint=escape(
                "**bold** and *italic* as anywhere. Start a line with "
                "[heading], [centre], [right] or [initial] (a paragraph opening "
                "on an illuminated initial), or put [flourish] or [picture 1] "
                f"alone on a line. At most {handouts.MOST_TEXT:,} characters."
            ),
        ),
        DialogField(
            "pictures",
            "Pictures",
            "picker",
            [handouts.picture_ref(p) for p in existing.pictures] if existing else [],
            display=lambda refs: (
                "; ".join(handouts.ref_label(saga, r) for r in refs) or "(none)"
            ),
            items=ListEditor(
                lambda ref: handouts.ref_label(saga, ref),
                lambda _current: _choose_picture(saga),
                "Pictures",
            ),
            hint=escape(
                f"Up to {handouts.MOST_PICTURES}: a map or portrait already in "
                "the saga, or a new picture, copied into the handouts folder. "
                "[picture 1] places the first."
            ),
        ),
        DialogField(
            "found_by",
            "Found by",
            "select",
            existing.found_by_id if existing and existing.found_by_id else None,
            options=finders,
            allow_blank=True,
            placeholder="(no one yet)",
        ),
        DialogField(
            "place",
            "Where",
            "select",
            existing.place_id if existing and existing.place_id else None,
            options=places,
            allow_blank=True,
            placeholder="(nowhere set)" if places else "(no Place in the saga)",
        ),
        DialogField(
            "story",
            "Story",
            "select",
            existing.story_id if existing and existing.story_id else None,
            options=stories,
            allow_blank=True,
            placeholder="(none)" if stories else "(no open story)",
            hint="The open story it belongs to: the list can be narrowed to one.",
        ),
    ]


def _validate(values: dict[str, Any]) -> str | None:
    return handouts.why_not(
        values.get("title") or "",
        values.get("text") or "",
        len(dict.fromkeys(values.get("pictures") or [])),
    )


def _store(saga: Saga, existing: Handout | None, values: dict[str, Any]) -> Handout:
    handout = existing or Handout(id=handouts.new_id())
    handout.title = (values.get("title") or "").strip()
    handout.stationery = values.get("stationery") or VELLUM
    handout.text = values.get("text") or ""
    handout.pictures = handouts.pictures_from(list(values.get("pictures") or []))
    finder = values.get("found_by") or ""
    if finder != handout.found_by_id:
        handout.found_by_id, handout.found_by = finder, ""
    place = values.get("place") or ""
    if place != handout.place_id:
        handout.place_id, handout.place_name = place, ""
    handout.story_id = scenes.story_from(saga, values.get("story"))
    if existing is None:
        saga.handouts.append(handout)
    return handout


def handout_form(saga: Saga, existing: Handout | None) -> Form:
    """Write a new Handout (None), or Edit one."""
    title = (
        "Write a Handout"
        if existing is None
        else f"Edit the Handout: {escape(existing.title or '(untitled)')}"
    )
    return Form(
        title,
        lambda: handout_fields(saga, existing),
        lambda values: _store(saga, existing, values),
        validate=_validate,
        help_id=HANDOUTS_HELP,
        preview=lambda values: _preview(saga, values),
    )


def _preview(saga: Saga, values: dict[str, Any]) -> Preview:
    """The Handout as the form holds it, laid on its Stationery."""
    return handouts.preview(
        saga,
        values.get("title") or "",
        values.get("stationery") or VELLUM,
        values.get("text") or "",
        list(values.get("pictures") or []),
    )


def delete_handout(saga: Saga, handout: Handout) -> Confirm:
    return confirm_delete(
        saga,
        handout,
        handouts.delete,
        f"Delete the Handout {escape(handout.title or '(untitled)')}?",
    )


def handout_ops(saga: Saga) -> SectionOps:
    """Add, Edit and Delete for the saga's written Handouts, by their row
    in the list as shown (handouts.shown: narrowed to a Story or not)."""
    return SectionOps(
        add=lambda: handout_form(saga, None),
        edit=lambda index: handout_form(saga, handouts.shown(saga)[index]),
        remove=lambda index: delete_handout(saga, handouts.shown(saga)[index]),
        rows=lambda: [handouts.row(h) for h in handouts.shown(saga)],
    )


def filter_form(saga: Saga) -> Form:
    """Narrow the Handouts list to the Handouts of one Story; blank shows
    them all."""

    def apply(values: dict[str, Any]) -> None:
        handouts.choose_story(saga, values.get("story") or "")

    return Form(
        "Narrow the Handouts",
        lambda: [
            DialogField(
                "story",
                "Story",
                "select",
                handouts.current_story(saga) or None,
                options=[(escape(n), i) for n, i in handouts.story_filters(saga)],
                allow_blank=True,
                placeholder="(every story)",
                hint="Only the Handouts of this story.",
            )
        ],
        apply,
        save_label="Show",
        help_id=HANDOUTS_HELP,
    )

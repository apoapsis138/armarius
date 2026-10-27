"""More's Gain or Lose in Play on a character's Virtues & Flaws -- no UI
in here.

A Flaw or Virtue gained during the saga (one gained by magic may be
marked temporary, with the season it ends), a Flaw lost, a temporary one
ended, a change of Social Status, or one chosen wrongly exchanged, each with how it came about; the
inspector says what Save will do and what the books warn of, and the
change is kept in the Diary. The rules and their pages are
rules.vf_change's."""

from __future__ import annotations

import copy
from collections.abc import Callable
from dataclasses import replace
from typing import Any

from .. import catalog
from ..commands import Command, Form, Refuse, notes
from ..form_spec import DialogField
from ..markup import BULLET, escape
from ..models import (
    SEASONS,
    Character,
    DiaryEntry,
    Saga,
    VirtueFlawDef,
    VirtueFlawInstance,
)
from ..rules import creation_characteristics as cch
from ..rules import vf_change as vc
from . import virtue as virtue_forms

TITLE = "Gain or Lose in Play"
HELP = "vf-change"
INSPECTOR = "In Play"

#: The pickers' keys: what each holds.
FLAW, VIRTUE, NEW_STATUS, NEW_VIRTUE, NEW_FLAW = (
    "flaw",
    "virtue",
    "new_status",
    "new_virtue",
    "new_flaw",
)


def _by_id() -> dict[str, VirtueFlawDef]:
    return dict(catalog.load_virtue_flaw_catalog_by_id())


def _is(*changes: str) -> Callable[[dict[str, Any]], bool]:
    return lambda values: values.get("change", vc.GAIN_FLAW) in changes


def _own_options(
    character: Character,
    keep: Callable[[VirtueFlawDef], bool],
    held: Callable[[VirtueFlawInstance], bool] = lambda _vf: True,
) -> list[tuple[str, str]]:
    """The character's own Virtues and Flaws that `keep` (and `held`, of
    the instance) allow, as select options keyed by their place in the
    list."""
    by_id = _by_id()

    def label(vf: VirtueFlawInstance, entry: VirtueFlawDef) -> str:
        temporary = vc.temporary_text(vf)
        return (
            f"{catalog.describe_virtue_flaw(vf, by_id)} ({entry.tier} {entry.side}"
            f"{f', {temporary}' if temporary else ''})"
        )

    return [
        (escape(label(vf, entry)), str(i))
        for i, vf in enumerate(character.virtues_flaws)
        if (entry := by_id.get(vf.vf_id)) is not None and keep(entry) and held(vf)
    ]


def _by_magic(values: dict[str, Any]) -> bool:
    """Whether the form gains a Virtue or Flaw by magic."""
    change = values.get("change", vc.GAIN_FLAW)
    return (change == vc.GAIN_FLAW and values.get("flaw_cause") == vc.MAGIC) or (
        change == vc.GAIN_VIRTUE and values.get("virtue_cause") == vc.MAGIC
    )


def _temporary(values: dict[str, Any]) -> bool:
    """Whether the Virtue or Flaw gained by magic is marked temporary."""
    return _by_magic(values) and bool(values.get("temporary"))


def _own(character: Character, values: dict[str, Any], key: str) -> int | None:
    """The index of the character's own Virtue or Flaw chosen in `key`."""
    raw = values.get(key)
    if raw is None or not str(raw).isdigit():
        return None
    index = int(raw)
    return index if index < len(character.virtues_flaws) else None


def _entry(instance: VirtueFlawInstance | None) -> VirtueFlawDef | None:
    return _by_id().get(instance.vf_id) if instance is not None else None


def _old_side(character: Character, values: dict[str, Any]) -> str | None:
    index = _own(character, values, "old")
    if index is None:
        return None
    entry = _by_id().get(character.virtues_flaws[index].vf_id)
    return entry.side if entry is not None else None


def _picker(
    saga: Saga,
    character: Character,
    key: str,
    label: str,
    side: str | None,
    show_if: Callable[[dict[str, Any]], bool],
    category: str | None = None,
) -> DialogField:
    """A field choosing a Virtue or Flaw the character could gain in play."""
    by_id = _by_id()

    def display(instance: VirtueFlawInstance) -> str:
        entry = by_id.get(instance.vf_id)
        tier = f" ({entry.tier} {entry.side})" if entry else ""
        return catalog.describe_virtue_flaw(instance, by_id) + tier

    what = category or side or "Virtue or Flaw"
    return DialogField(
        key,
        label,
        "picker",
        None,
        allow_blank=True,
        placeholder=f"(choose the {what}...)",
        choose=lambda _current: virtue_forms.choose_virtue_flaw(
            saga, character, side, in_play=True, category=category
        ),
        display=display,
        show_if=show_if,
    )


def change_fields(saga: Saga, character: Character) -> list[DialogField]:
    """What changes, how it came about, and the Virtues and Flaws it
    concerns."""

    def causes(table: dict[str, tuple[str, str]]) -> list[tuple[str, str]]:
        return [(label, key) for key, (label, _) in table.items()]

    return [
        DialogField(
            "change",
            "What changes",
            "select",
            vc.GAIN_FLAW,
            options=[(label, key) for key, label in vc.CHANGES.items()],
        ),
        DialogField(
            "flaw_cause",
            "How it came about",
            "select",
            vc.MISHAP,
            options=causes(vc.FLAW_CAUSES),
            show_if=_is(vc.GAIN_FLAW),
        ),
        _picker(saga, character, FLAW, "Flaw gained", "Flaw", _is(vc.GAIN_FLAW)),
        DialogField(
            "virtue_cause",
            "How it came about",
            "select",
            vc.ACTIONS,
            options=causes(vc.VIRTUE_CAUSES),
            show_if=_is(vc.GAIN_VIRTUE),
        ),
        _picker(
            saga, character, VIRTUE, "Virtue gained", "Virtue", _is(vc.GAIN_VIRTUE)
        ),
        DialogField(
            "temporary",
            "Temporary (it ends in play)",
            "check",
            True,
            show_if=_by_magic,
            hint="Most Virtues granted by magic are temporary, and hedge curses "
            "are usually limited in duration (Grogs pp. 62-63).",
        ),
        DialogField(
            "ends_season",
            "Ends in season",
            "select",
            None,
            options=[(season, season) for season in SEASONS],
            allow_blank=True,
            placeholder="(not known)",
            show_if=_temporary,
        ),
        DialogField(
            "ends_year",
            "Ends in year",
            "optint",
            None,
            show_if=_temporary,
            hint="Leave blank if the end isn't known; a year alone ends at its Winter.",
        ),
        DialogField(
            "lost_flaw",
            "Flaw lost",
            "select",
            None,
            options=_own_options(character, lambda e: e.side == "Flaw"),
            allow_blank=True,
            placeholder="(choose one of their Flaws)",
            show_if=_is(vc.LOSE_FLAW),
        ),
        DialogField(
            "loss_cause",
            "How it was lost",
            "select",
            vc.STORY,
            options=causes(vc.LOSS_CAUSES),
            show_if=_is(vc.LOSE_FLAW),
        ),
        DialogField(
            "ended",
            "Virtue or Flaw ending",
            "select",
            None,
            options=_own_options(character, lambda _e: True, lambda vf: vf.temporary),
            allow_blank=True,
            placeholder="(choose one of their temporary Virtues or Flaws)",
            show_if=_is(vc.TEMPORARY_ENDS),
        ),
        DialogField(
            "old_status",
            "Old Social Status",
            "select",
            None,
            options=_own_options(character, vc.is_social_status),
            allow_blank=True,
            placeholder="(choose their Social Status)",
            show_if=_is(vc.SOCIAL_STATUS),
        ),
        _picker(
            saga,
            character,
            NEW_STATUS,
            "New Social Status",
            None,
            _is(vc.SOCIAL_STATUS),
            category="Social Status",
        ),
        DialogField(
            "keep_old",
            "Keep the old status too (its description allows it)",
            "check",
            False,
            show_if=_is(vc.SOCIAL_STATUS),
            hint="Only a status whose description says so is kept beside the "
            "new one (Grogs p. 61).",
        ),
        DialogField(
            "old",
            "Chosen wrongly",
            "select",
            None,
            options=_own_options(character, lambda _e: True),
            allow_blank=True,
            placeholder="(choose one of their Virtues or Flaws)",
            show_if=_is(vc.EXCHANGE),
        ),
        _picker(
            saga,
            character,
            NEW_VIRTUE,
            "Exchanged for",
            "Virtue",
            lambda v: _is(vc.EXCHANGE)(v) and _old_side(character, v) == "Virtue",
        ),
        _picker(
            saga,
            character,
            NEW_FLAW,
            "Exchanged for",
            "Flaw",
            lambda v: _is(vc.EXCHANGE)(v) and _old_side(character, v) == "Flaw",
        ),
        DialogField(
            "new_to_saga",
            "New to the saga (larger changes allowed)",
            "check",
            False,
            show_if=_is(vc.EXCHANGE),
            hint="An established character exchanges only like for like: Minor "
            "for Minor, Major for Major (Grogs p. 61).",
        ),
        DialogField(
            "story",
            "What happened",
            "text",
            "",
            placeholder="for the Diary, e.g. lost his hand at the ford",
        ),
    ]


# -- what Save does --


class _Change:
    """The change the form's values describe: what goes, what comes, why
    it can't be made and what the books say of it."""

    def __init__(self, saga: Saga, character: Character, values: dict[str, Any]):
        self.saga, self.character, self.values = saga, character, values
        self.kind = values.get("change", vc.GAIN_FLAW)
        self.by_id = _by_id()
        self.removed: int | None = None
        self.added: VirtueFlawInstance | None = None
        self.cause = ""
        self.subject = ""
        self.problem = ""
        self.lines: list[str] = []
        getattr(self, f"_{self.kind}")()

    def _name(self, instance: VirtueFlawInstance) -> str:
        return catalog.describe_virtue_flaw(instance, self.by_id)

    def _gain(self, key: str, side: str, causes: dict[str, tuple[str, str]]) -> None:
        cause = str(self.values.get(f"{side.lower()}_cause") or "")
        self.cause = causes.get(cause, ("", ""))[0]
        instance = self.values.get(key)
        entry = _entry(instance)
        if instance is None or entry is None:
            self.problem = f"Choose the {side} gained."
            return
        self.added = instance
        self.subject = self._name(instance)
        self.problem = vc.gain_refusal(self.character, entry, self.by_id)
        self.lines.append(f"{self._name(instance)} ({entry.tier} {side}) is added.")
        if _temporary(self.values):
            self._mark_temporary(instance)
        self.lines += vc.gain_notes(self.character, entry, self.by_id)
        if cause in causes:
            self.lines.append(causes[cause][1])
        if cause == vc.INITIATION:
            self.lines.append(vc.initiation_note(self.character))
        if cause == vc.WARPING:
            self.lines += vc.warping_notes(self.character)

    def _mark_temporary(self, instance: VirtueFlawInstance) -> None:
        """Mark the Virtue or Flaw gained temporary, ending in the season
        given (if any)."""
        raw_year = str(self.values.get("ends_year") or "")
        year = int(raw_year) if raw_year.isdigit() else None
        season = str(self.values.get("ends_season") or "")
        self.added = replace(
            instance, temporary=True, ends_year=year, ends_season=season
        )
        self.problem = self.problem or vc.end_problem(
            year, season or None, self.saga.current_year, self.saga.current_season
        )
        ends = vc.ends_text(self.added)
        self.lines.append(
            f"It is temporary, ending {ends}." if ends else "It is temporary."
        )

    def _temporary_ends(self) -> None:
        self.cause = "Its time is up"
        index = _own(self.character, self.values, "ended")
        if index is None or not self.character.virtues_flaws[index].temporary:
            self.problem = "Choose the temporary Virtue or Flaw that ends."
            return
        self.removed = index
        instance = self.character.virtues_flaws[index]
        self.subject = self._name(instance)
        self.lines.append(f"{self._name(instance)} is taken off the sheet.")
        self.lines.append(vc.TEMPORARY_RULE)

    def _gain_flaw(self) -> None:
        self._gain(FLAW, "Flaw", vc.FLAW_CAUSES)

    def _gain_virtue(self) -> None:
        self._gain(VIRTUE, "Virtue", vc.VIRTUE_CAUSES)

    def _lose_flaw(self) -> None:
        cause = str(self.values.get("loss_cause") or vc.STORY)
        self.cause = vc.LOSS_CAUSES.get(cause, ("", ""))[0]
        index = _own(self.character, self.values, "lost_flaw")
        if index is None:
            self.problem = "Choose the Flaw lost."
            return
        self.removed = index
        instance = self.character.virtues_flaws[index]
        self.subject = self._name(instance)
        entry = self.by_id.get(instance.vf_id)
        self.lines.append(f"{self._name(instance)} is taken off the sheet.")
        if entry is not None:
            self.lines += vc.loss_notes(entry, cause)
        if cause in vc.LOSS_CAUSES:
            self.lines.append(vc.LOSS_CAUSES[cause][1])

    def _social_status(self) -> None:
        self.cause = "A change of Social Status"
        index = _own(self.character, self.values, "old_status")
        new = self.values.get(NEW_STATUS)
        new_entry = _entry(new)
        if index is None:
            self.problem = "Choose their old Social Status."
            return
        if new is None or new_entry is None:
            self.problem = "Choose the new Social Status."
            return
        old = self.character.virtues_flaws[index]
        old_entry = self.by_id.get(old.vf_id)
        if old_entry is not None:
            self.problem = vc.status_refusal(old_entry, new_entry)
        self.added = new
        self.subject = self._name(new)
        keep = bool(self.values.get("keep_old"))
        if not keep:
            self.removed = index
        self.lines.append(
            f"{self._name(new)} ({new_entry.tier} {new_entry.side}) "
            + (
                f"is added beside {self._name(old)}."
                if keep
                else f"replaces {self._name(old)}."
            )
        )
        self.lines.append(
            "The old Social Status is replaced by the new; only one whose "
            "description says so is kept as well (Grogs p. 61)."
        )

    def _exchange(self) -> None:
        self.cause = "Exchanged with the troupe's approval"
        index = _own(self.character, self.values, "old")
        if index is None:
            self.problem = "Choose the Virtue or Flaw chosen wrongly."
            return
        old = self.character.virtues_flaws[index]
        old_entry = self.by_id.get(old.vf_id)
        if old_entry is None:
            self.problem = "That one isn't in the catalog."
            return
        new = self.values.get(NEW_VIRTUE if old_entry.side == "Virtue" else NEW_FLAW)
        new_entry = _entry(new)
        if new is None or new_entry is None:
            self.problem = f"Choose the {old_entry.side} it is exchanged for."
            return
        self.removed, self.added = index, new
        self.subject = f"{self._name(old)} for {self._name(new)}"
        self.problem = vc.exchange_refusal(
            old_entry, new_entry, bool(self.values.get("new_to_saga"))
        )
        if not self.problem and (
            cch.removal_changes(self.saga, self.character, old) or self._moves()
        ):
            self.problem = (
                "An exchange shouldn't change the character's Characteristics "
                "(Grogs p. 61)."
            )
        self.lines.append(f"{self._name(old)} becomes {self._name(new)}.")
        self.lines += vc.exchange_notes(old_entry, new_entry)

    def _moves(self) -> list[str]:
        """The Characteristics the change moves, as "Strength +3 to +4"."""
        after = copy.deepcopy(self.character)
        _apply(self.saga, after, self.removed, self.added)
        return [
            f"{label} {getattr(self.character.characteristics, key):+d} to "
            f"{getattr(after.characteristics, key):+d}"
            for key, label in cch.CHARACTERISTICS
            if getattr(self.character.characteristics, key)
            != getattr(after.characteristics, key)
        ]

    def said(self) -> list[str]:
        """What the inspector shows."""
        found = list(self.lines)
        if not self.problem and (self.removed is not None or self.added is not None):
            moved = self._moves()
            if moved:
                found.insert(1, f"Moves {', '.join(moved)}.")
        return found


def _apply(
    saga: Saga,
    character: Character,
    removed: int | None,
    added: VirtueFlawInstance | None,
) -> None:
    """Take the Virtue or Flaw at `removed` off (its Characteristic point
    back) and put `added` in its place, or at the end."""
    place = len(character.virtues_flaws)
    if removed is not None:
        cch.unapply_virtue(saga, character, character.virtues_flaws[removed])
        del character.virtues_flaws[removed]
        place = removed
    if added is not None:
        instance = replace(added, params=dict(added.params))
        character.virtues_flaws.insert(place, instance)
        cch.apply_virtue(saga, character, instance)


def change_lines(saga: Saga, character: Character, values: dict[str, Any]) -> list[str]:
    """What Save will do, said in the inspector."""
    change = _Change(saga, character, values)
    return [*change.said(), *([change.problem] if change.problem else [])]


def _live(saga: Saga, character: Character) -> Callable[[dict[str, Any]], str]:
    return lambda values: "\n".join(
        f"{BULLET} {escape(line)}" for line in change_lines(saga, character, values)
    )


def _problem(
    saga: Saga, character: Character
) -> Callable[[dict[str, Any]], str | None]:
    def problem(values: dict[str, Any]) -> str | None:
        return _Change(saga, character, values).problem or None

    return problem


def record(saga: Saga, character: Character, values: dict[str, Any]) -> list[str]:
    """The change made on the sheet and kept in the Diary."""
    change = _Change(saga, character, values)
    lines = change.said()
    _apply(saga, character, change.removed, change.added)
    story = str(values.get("story") or "").strip()
    head = vc.CHANGES.get(change.kind, TITLE)
    details = [
        *([story] if story else []),
        *([f"How: {change.cause}."] if change.cause else []),
        *lines,
        f"Rules: {vc.SOURCE}; {vc.DE_SOURCE}",
    ]
    character.diary.append(
        DiaryEntry(
            saga.current_year,
            saga.current_season,
            f"{head}: {change.subject}" if change.subject else head,
            "\n".join(details),
        )
    )
    return notes(lines[0] if lines else head)


def change_form(saga: Saga, character: Character | None) -> Command:
    """More's Gain or Lose in Play on the character's Virtues & Flaws."""
    if character is None:
        return Refuse(TITLE, "Choose a character first.")
    who = character
    return Form(
        f"{TITLE}: {escape(who.name)}",
        lambda: change_fields(saga, who),
        lambda values: record(saga, who, values),
        validate=_problem(saga, who),
        live=_live(saga, who),
        help_id=HELP,
        inspector=INSPECTOR,
    )

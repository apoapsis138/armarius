"""The first step of each More action and of Delete, as commands.py
steps: what forms.menu's command() runs. Each mutates the saga only in its
last step's apply, so cancelling any step changes nothing.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from .. import (
    arms,
    creation,
    creatures,
    cult_transfer,
    deletion,
    neighbours,
    packs,
    places,
    record_links,
    ruins,
    seasons,
    sessions,
    storage,
    story_chapters,
    threats,
    traditions,
    transfer,
    tribunals,
    world,
)
from .. import economics as eco
from .. import inhabitants as inh
from .. import lab_texts as lt
from .. import spells as spl
from ..actions import (
    NodeKind,
)
from ..commands import (
    Choice,
    Choose,
    Command,
    Confirm,
    Form,
    Refuse,
    confirm_delete,
    notes,
)
from ..form_spec import DialogField, pairs
from ..markup import escape, todo
from ..models import (
    FULL,
    INCOME_EFFECTS,
    LINE,
    SEASONS,
    SKETCH,
    TEXT_LONGEVITY,
    Book,
    Character,
    Covenant,
    Creature,
    Familiar,
    IncomeSource,
    Laboratory,
    LabTextAccess,
    Neighbour,
    Saga,
    Session,
    Spell,
    Tribunal,
)
from ..models.definitions import ROLL_CHARACTERISTICS
from ..rules import covenfolk, creation_tradition, lab_seasons
from ..rules import creation as creation_rules
from ..rules import creation_covenant as cov_creation
from ..rules import hedge_casting as hc
from . import creation as creation_forms
from . import importing as import_forms
from . import interests as interests_forms
from . import library as library_forms
from . import markdown as markdown_forms
from . import sheet_roll as sheet_roll_forms
from .page import (
    Deliver,
    Page,
    Record,
)

#: Delete's action: the record on show, after a confirmation that says
#: what happens to what it owns.


def familiar_binder(page: Page) -> Character | None:
    """The magus a familiar would be bound to from the page: the magus on
    show, or the laboratory's owner, while they have none."""
    if page.kind == NodeKind.CHARACTER:
        magus = page.character
    elif page.kind == NodeKind.LABORATORY and page.laboratory is not None:
        magus = page.saga.character(page.laboratory.owner_id)
    else:
        return None
    if (
        magus is None
        or magus.type != "magus"
        or page.saga.familiar_of(magus.id) is not None
    ):
        return None
    return magus


def delete_record(saga: Saga, record: Record) -> Confirm:
    """ "Delete <name>?", saying what happens to what it owns, then what
    else changes (record_links.warning)."""
    consequences, delete = _deletion_of(saga, record)
    return confirm_delete(
        saga, record, delete, f"Delete {escape(record.name)}?", consequences
    )


def _deletion_of(saga: Saga, record: Record) -> tuple[list[str], record_links.Delete]:
    if isinstance(record, Creature):
        return [], creatures.delete
    if isinstance(record, Tribunal):
        return [], tribunals.delete
    if isinstance(record, Neighbour):
        return [], neighbours.delete
    if isinstance(record, Covenant):
        return deletion.covenant_consequences(saga, record), deletion.delete_covenant
    if isinstance(record, Character):
        return deletion.character_consequences(saga, record), deletion.delete_character
    if isinstance(record, Familiar):
        return deletion.familiar_consequences(saga, record), deletion.delete_familiar
    return deletion.laboratory_consequences(saga, record), deletion.delete_laboratory


def toggle_mode(saga: Saga, record: Character | Covenant | Laboratory) -> Command:
    """In Creation / In Play: asks first either way. With strict creation
    rules on, a record that breaks a rule it must follow stays In
    Creation."""
    name = escape(record.name)
    if record.in_creation:
        if not creation_rules.can_move_to_play(saga, record):
            broken = creation_rules.broken_musts(creation_rules.checks(saga, record))
            return Refuse(
                "In Creation / In Play",
                f"{name} stays In Creation: it breaks {len(broken)} "
                "creation rule(s) it must follow, and this saga enforces "
                "them strictly.",
            )
        found = creation_rules.checks(saga, record)
        message = (
            f"Move {name} to In Play? Creation checks: "
            f"{creation_rules.summary(found)}. They stop once it is In Play."
        )
        if isinstance(record, Covenant):
            note = cov_creation.leftover_note(saga, record)
            if note:
                message += f"\n\n{escape(note)}"
    else:
        message = (
            f"Move {name} back to In Creation? The creation checks come "
            "back until it moves to In Play again."
        )

    def apply() -> None:
        creation.set_in_creation(saga, record, not record.in_creation)

    return Confirm(message, apply, yes_label="Yes")


#: What moving to each detail level does, said before it is done.
_DETAIL_WORDS: dict[str, str] = {
    LINE: "a line: a name and who they are, nothing more",
    SKETCH: "a sketch: the statblock play needs, left out of seasons, "
    "ageing and creation budgets",
    FULL: "a full character, In Creation, with the Creation Worksheet "
    "open on what the sketch already has",
}

#: The same for a covenant.
_COVENANT_DETAIL_WORDS: dict[str, str] = {
    LINE: "a line: a name, its Tribunal and who they are",
    SKETCH: "a sketch: its magi, what matters to it and its attitudes, "
    "left out of upkeep, income and Loyalty",
    FULL: "a full covenant, In Creation, with the Creation Worksheet "
    "open on what the sketch already has",
}


def change_detail(saga: Saga, record: Character | Covenant, detail: str) -> Command:
    """Promote or Demote `record` to `detail`, asking first. Nothing is
    copied or deleted: a promoted sketch keeps every score it had, and a
    demoted record keeps what its hidden chapters hold. Promoted to
    Full, it is In Creation so its budget checks apply from there."""
    name = escape(record.name)

    def apply() -> None:
        record.detail = detail
        if detail == FULL:
            creation.set_in_creation(saga, record, True)
        else:
            record.in_creation = False

    verb = (
        "Promote"
        if world.DETAIL_LEVELS.index(detail) > world.DETAIL_LEVELS.index(record.detail)
        else "Demote"
    )
    words = _COVENANT_DETAIL_WORDS if isinstance(record, Covenant) else _DETAIL_WORDS
    return Confirm(f"{verb} {name} to {words[detail]}?", apply, yes_label=verb)


def detail_command(action: str) -> Callable[[Page], Command]:
    step = world.promoted if action == "promote" else world.demoted

    def command(page: Page) -> Command:
        record = page.creation_record()
        if not isinstance(record, (Character, Covenant)):
            return Refuse(action.title(), "That isn't available here.")
        detail = step(record.detail)
        if detail is None:
            return Refuse(action.title(), "That isn't available here.")
        return change_detail(page.saga, record, detail)

    return command


def export_fields(record: transfer.Record, folder: Path) -> list[DialogField]:
    kind = transfer.kind_of(record)
    fields = [
        DialogField(
            "_what", "Exporting", "info", f"{transfer.KIND_LABELS[kind]}: {record.name}"
        ),
        DialogField(
            "file",
            "File",
            "text",
            str(folder / transfer.default_file_name(record)),
            hint="Its contents travel with it: a character's familiar, devices, books "
            "and Diary; a lab's books and devices. Import it with More's Import.",
        ),
    ]
    if kind == transfer.COVENANT:
        fields.append(
            DialogField(
                "with_members",
                "With its laboratories and characters",
                "check",
                False,
            )
        )
    return fields


def export_path(values: dict[str, Any]) -> Path:
    """The export form's file, with the export suffix if it has none."""
    name = (values.get("file") or "").strip().strip('"')
    path = Path(name).expanduser()
    if name and not path.name.lower().endswith((".json", ".zip")):
        path = path.with_name(path.name + transfer.SUFFIX)
    return path


def export_problem(values: dict[str, Any]) -> str | None:
    if not (values.get("file") or "").strip():
        return "Give the file to write."
    if export_path(values).is_dir():
        return "That is a folder: add a file name."
    return None


def export_live(values: dict[str, Any]) -> str:
    if export_problem(values):
        return ""
    path = export_path(values)
    if path.exists():
        return todo(f"{escape(path.name)} exists: it will be replaced.")
    return f"[dim]Writes {escape(str(path))}[/]"


def downloaded(
    deliver: Deliver, name: str, data: dict[str, Any], what: str
) -> list[str]:
    """Send `data` as a JSON file called `name` with `deliver`, and say so."""
    deliver(name, json.dumps(data, indent=2).encode("utf-8"), "application/json")
    return notes(f"Exported {escape(what)}: your browser downloads it.")


def export_record(
    saga: Saga,
    record: transfer.Record,
    folder: Path,
    deliver: Deliver | None = None,
) -> Form:
    """Export a covenant, laboratory or character to a file another saga
    can import; with `deliver`, straight to a browser."""

    def apply(values: dict[str, Any]) -> Command | list[str]:
        path = export_path(values)
        with_members = bool(values.get("with_members"))
        if deliver is not None:
            data = transfer.export_data(saga, record, with_members=with_members)
            return downloaded(
                deliver, path.name, transfer.for_reader(data), record.name
            )
        try:
            written = transfer.export_to(path, saga, record, with_members=with_members)
        except OSError as problem:
            return Refuse(
                f"Export {escape(record.name)}",
                f"Couldn't write {escape(path.name)}: {escape(str(problem))}",
            )
        return notes(f"Exported {escape(record.name)} to {escape(str(written))}.")

    return Form(
        f"Export {escape(record.name)}",
        lambda: export_fields(record, folder),
        apply,
        validate=export_problem,
        live=export_live,
        save_label="Export",
    )


# ---------------------------------------------------------------- the saga


def date_fields(season: str, year: int) -> list[DialogField]:
    """Set the saga's date."""
    return [
        DialogField("season", "Season", "select", season, options=pairs(SEASONS)),
        DialogField("year", "Year", "int", year),
    ]


def set_date(saga: Saga) -> Form:
    def apply(values: dict[str, Any]) -> list[str] | None:
        season, year = values["season"], values["year"]
        if (season, year) == (saga.current_season, saga.current_year):
            return None
        saga.current_season, saga.current_year = season, year
        places.sync(saga)
        return notes(f"Date set to {season} {year}.")

    return Form(
        "Set the Saga's Date",
        lambda: date_fields(saga.current_season, saga.current_year),
        apply,
        save_label="Set",
    )


# ---------------------------------------------------------------- choosing


def _one_of[T](
    title: str,
    entries: list[T],
    label: Callable[[T], str],
    then: Callable[[T], Command],
) -> Command:
    """`then` the only entry, or the one chosen from a list."""
    if len(entries) == 1:
        return then(entries[0])
    return Choose(
        title,
        lambda: [Choice(label(e), i) for i, e in enumerate(entries)],
        lambda index: then(entries[index]),
    )


# ------------------------------------------------------------- the covenant


def restore(saga: Saga, covenant: Covenant) -> Command:
    """Bring back a departed Magus or Companion: still on their sheet,
    they start counting as an inhabitant again."""
    kinds = [
        kind
        for kind in covenfolk.AUTO_KINDS
        if inh.departed_entries_for_kind(saga, covenant, kind)
    ]
    entries = [
        (kind, entry)
        for kind in kinds
        for entry in inh.departed_entries_for_kind(saga, covenant, kind)
    ]
    if not entries:
        return Refuse("Restore", "No departed Magi or Companions to restore.")
    who = inh.KIND_SINGULAR[kinds[0]] if len(kinds) == 1 else "Magus or Companion"

    def label(pair: tuple[str, covenfolk.InhabitantEntry]) -> str:
        kind, entry = pair
        name = escape(entry.name) or "(unnamed)"
        return name if len(kinds) == 1 else f"{name} ({inh.KIND_SINGULAR[kind]})"

    def choose(pair: tuple[str, covenfolk.InhabitantEntry]) -> None:
        _, entry = pair
        if entry.record is not None:
            entry.record.departed = False

    return Choose(
        f"Restore which {who}?",
        lambda: [Choice(label(pair), i) for i, pair in enumerate(entries)],
        lambda index: choose(entries[index]),
    )


def improve_fields(source: IncomeSource) -> list[DialogField]:
    return [
        DialogField("name", "Name", "info", source.name or "(unnamed)"),
        DialogField("current", "Current Income", "info", str(source.current_income)),
        DialogField(
            "effect",
            "Annual Improvement Effect",
            "select",
            "Status Quo",
            options=pairs(INCOME_EFFECTS),
            required=True,
        ),
        # A Note is a sentence or two: shown under its label, wrapped.
        DialogField(
            "note",
            "Note",
            "info",
            "" if source.note.strip() else "(none)",
            hint=escape(source.note.strip()),
        ),
        *magic_fields(),
    ]


def magic_fields() -> list[DialogField]:
    """Whether the year's change is the magi's doing, and the wealth the
    magic makes a year (Covenants pp. 57-58)."""
    return [
        DialogField(
            "magic",
            "Improved by magic",
            "check",
            False,
            hint="The storyguide picks the Effect the magic merits (Covenants "
            "pp. 57-58; City & Guild p. 130 has ways magic makes a profit).",
        ),
        DialogField(
            "made",
            "Pounds the magic makes yearly",
            "optint",
            None,
            placeholder="(the gain: Projected less Current)",
            show_if=lambda v: bool(v.get("magic")),
        ),
    ]


def magic_made(current: int, values: dict[str, Any]) -> int:
    """The wealth an improvement by magic makes a year: as typed, else the
    income it adds."""
    effect = values.get("effect") or "Status Quo"
    typed = values.get("made")
    if typed is not None:
        return max(0, int(typed))
    return max(0, eco.projected_income(current, effect) - current)


def improve_live(
    source: IncomeSource, magic_limit: tuple[int, int] | None = None
) -> Callable[[dict[str, Any]], str]:
    """The Multiplier and Projected Income; with magic ticked, the wealth it
    makes against `magic_limit` (the covenant's limit and its magi)."""

    def live(values: dict[str, Any]) -> str:
        effect = values.get("effect") or "Status Quo"
        text = (
            f"Income Multiplier {eco.income_multiplier_text(effect)}. "
            f"Projected Income {eco.projected_income(source.current_income, effect)}"
        )
        if values.get("magic") and magic_limit is not None:
            made = magic_made(source.current_income, values)
            text += ". " + eco.magic_wealth_text(made, *magic_limit)
        return text

    return live


def improve_form(
    saga: Saga, source: IncomeSource, covenant: Covenant | None = None
) -> Form:
    """Manually simulate a year's Income Modification: choosing an Effect
    shows the Multiplier and Projected Income (and, improved by magic, the
    Tribunals' limit on wealth made by magic); Commit asks to confirm."""
    name = escape(source.name or "this source of income")
    limit = (
        (eco.magic_limit(saga, covenant), eco.magi_count(saga, covenant))
        if covenant is not None
        else None
    )

    def apply(values: dict[str, Any]) -> Confirm:
        current = source.current_income
        effect = values["effect"]
        projected = eco.projected_income(current, effect)

        def update() -> None:
            source.income = projected
            source.note = eco.improvement_note(
                saga.current_year,
                source.name,
                effect,
                current,
                projected,
                magic=bool(values.get("magic")),
            )

        return Confirm(
            f"Update {name}'s income from {current} to {projected}?",
            update,
            yes_label="Update",
        )

    return Form(
        f"Improve {name}",
        lambda: improve_fields(source),
        apply,
        live=improve_live(source, limit),
        save_label="Commit",
    )


def improve(saga: Saga, covenant: Covenant, row: int | None = None) -> Command:
    """Improve a source of income: the one chosen in the Income list
    (`row`), or asked for."""
    sources = covenant.economics.income_sources
    if not sources:
        return Refuse("Improve Income", "No sources of income to improve.")
    if row is not None and 0 <= row < len(sources):
        return improve_form(saga, sources[row], covenant)
    return _one_of(
        "Improve which source of income?",
        list(sources),
        lambda s: escape(s.name) or "(unnamed)",
        lambda s: improve_form(saga, s, covenant),
    )


def research_bonuses(saga: Saga, covenant: Covenant) -> Command:
    """Set up the covenant library's research bonuses, a subject at a
    time."""
    return library_forms.research_walkthrough(saga, covenant)


# ------------------------------------------------------------- the character


def share_spell(saga: Saga, character: Character, row: int | None = None) -> Command:
    """Make one of the magus's invented spells available to the saga: it
    moves to the saga's Spells, and they still know it. On a Known Spells
    row (`row`) that is one of his own, that one is asked about."""
    shareable = spl.shareable_spells(character)
    if not shareable:
        return Refuse("Share Spell", "No invented spells to share.")

    def confirm(spell: Spell) -> Confirm:
        return Confirm(
            f"Make {escape(spell.name)} available to the whole saga? It "
            f"moves to the saga's Spells, where anyone can learn it or "
            f"write it up; {escape(character.name)} still knows it.",
            lambda: spl.share_invented_spell(saga, character, spell),
            yes_label="Share",
        )

    if row is not None and row < len(character.spells_known):
        spell_id = character.spells_known[row].spell_id
        own = next((s for s in shareable if s.id == spell_id), None)
        if own is not None:
            return confirm(own)
    return _one_of(
        "Share which invented spell?",
        shareable,
        lambda s: f"{escape(s.name)} ({spl.shorthand(s)})",
        confirm,
    )


def share_command(page: Page) -> Command:
    if page.character is None:
        return Refuse("More", "That isn't available here.")
    row = page.row if page.section == "section-known-spells" else None
    return share_spell(page.saga, page.character, row)


#: A traditions form's check for a tradition is keyed by this and its id.
TRADITION_KEY = "tradition-"


def character_traditions_fields(saga: Saga, character: Character) -> list[DialogField]:
    """A tick for each tradition the character could belong to: those the
    saga offers, and any they already belong to."""
    choices = traditions.offered(saga) + [
        t for t in traditions.of(character) if not traditions.is_on(saga, t.id)
    ]
    return [
        *_sihr_realm_field(character),
        *(
            DialogField(
                TRADITION_KEY + t.id,
                f"{t.name} ({t.source})",
                "check",
                t.id in character.traditions,
            )
            for t in choices
        ),
    ]


def _sihr_realm_field(character: Character) -> list[DialogField]:
    """The realm of a sahir's Sihr, for one who has the Ability: Magic is
    its most common form (The Cradle and the Crescent p. 47)."""
    if not any(a.name == hc.SIHR for a in character.abilities):
        return []
    return [
        DialogField(
            "sihr_realm",
            "Realm of Sihr",
            "select",
            character.sihr_realm or "Magic",
            options=pairs(("Magic", *hc.SIHR_VERSIONS)),
            hint="Reads the aura for summoning; the Solomonic arts stay Magic.",
        )
    ]


def apply_character_traditions(
    character: Character, values: dict[str, Any]
) -> list[str]:
    """Join or leave each tradition listed; an Ability of a tradition left
    stays, in the Abilities chapter. A tradition joined brings what its
    membership requires and a Gifted member's Opening (creation_tradition.join)."""
    chosen = [
        key.removeprefix(TRADITION_KEY)
        for key, ticked in values.items()
        if key.startswith(TRADITION_KEY) and ticked
    ]
    listed = {
        key.removeprefix(TRADITION_KEY)
        for key in values
        if key.startswith(TRADITION_KEY)
    }
    if "sihr_realm" in values:
        realm = values["sihr_realm"]
        character.sihr_realm = "" if realm == "Magic" else realm
    kept = [i for i in character.traditions if i not in listed]
    joined = [i for i in chosen if i not in character.traditions]
    character.traditions = kept + [i for i in chosen if i not in kept]
    told: list[str] = []
    for tradition_id in joined:
        added = creation_tradition.join(character, tradition_id)
        if added:
            told.append(f"Joining brings {', '.join(escape(a) for a in added)}.")
        if creation_tradition.gifted(character):
            told.append(
                "A Gifted member's Gift is Opened by a Gifted master of the tradition: "
                "plan Open a student's Gift to a tradition for them (Hedge Magic "
                "Revised p. 7)."
            )
    return notes(*told)


def character_traditions(saga: Saga, character: Character) -> Form:
    """Choose the non-Hermetic traditions the character belongs to: each
    one's Arts and Abilities get a chapter of their own."""
    return Form(
        "Traditions",
        lambda: character_traditions_fields(saga, character),
        lambda values: apply_character_traditions(character, values),
    )


def lab_text_access_fields(saga: Saga, character: Character) -> list[DialogField]:
    """Whose raw Lab Texts a magus reads: an author -- a magus of the saga,
    or a name typed for one outside it --, the level he reads them to (0
    forgets the author) and how he came to. Choosing an author he already
    reads fills in what is recorded."""
    magi = lt.author_options(saga, character)
    known = dict(lt.access_rows(saga, character))
    outside = [key for key in known if saga.character(key) is None]

    def recorded(values: dict[str, Any]) -> dict[str, Any]:
        access = character.lab_text_access.get(values.get("author") or "")
        if access is None:
            return {}
        return {"level": access.level, "via": access.via or None}

    return [
        DialogField(
            "_known",
            "Reads now",
            "info",
            "; ".join(known.values()) or "(only their own and general texts)",
        ),
        DialogField(
            "author",
            "Author",
            "select",
            None,
            options=magi,
            allow_blank=True,
            placeholder="(a magus of the saga)",
            fills=recorded,
        ),
        DialogField(
            "name",
            "or an author outside it",
            "text",
            outside[0] if len(outside) == 1 and not magi else "",
            show_if=lambda values: not values.get("author"),
        ),
        DialogField(
            "level",
            "Reads to level",
            "int",
            0,
            hint="0 forgets this author. A text above the level needs more decoding.",
        ),
        DialogField(
            "via",
            "How",
            "select",
            None,
            options=[("Decoded", "decoded"), ("Taught", "taught")],
            allow_blank=True,
            placeholder="(not recorded)",
        ),
    ]


def _access_author(values: dict[str, Any]) -> str:
    return values.get("author") or (values.get("name") or "").strip()


def lab_text_access_problem(values: dict[str, Any]) -> str | None:
    if not _access_author(values):
        return "Choose the author, or type the name of one outside the saga."
    if values["level"] < 0:
        return "Level can't be negative."
    return None


def lab_text_access(saga: Saga, character: Character) -> Form:
    """Set whose raw Lab Texts the magus reads, and to what level: an
    author's entry is added, changed, or -- at level 0 -- removed."""

    def apply(values: dict[str, Any]) -> None:
        author, level = _access_author(values), values["level"]
        if level > 0:
            character.lab_text_access[author] = LabTextAccess(
                level, values.get("via") or ""
            )
        else:
            character.lab_text_access.pop(author, None)

    return Form(
        f"Lab Texts {escape(character.name)} reads",
        lambda: lab_text_access_fields(saga, character),
        apply,
        validate=lab_text_access_problem,
    )


# ------------------------------------------------------------ the laboratory


def ritual_texts(saga: Saga, lab: Laboratory) -> list[Book]:
    """The laboratory's Longevity Ritual Lab Texts."""
    return [
        b
        for b in lt.texts_of(saga, "laboratory", lab.id)
        if lt.kind(b) == TEXT_LONGEVITY
    ]


def ritual_again_fields(magus: Character, text: Book) -> list[DialogField]:
    """The fields of the form that performs a Longevity Ritual again: the
    text and who performs it, the Art of the vis and whose it is."""
    return [
        DialogField("_text", "Lab Text", "info", text.name),
        DialogField("_by", "Performed by", "info", magus.name),
        DialogField(
            "vis_art",
            "Vis",
            "select",
            "Creo",
            options=[(art, art) for art in lab_seasons.LONGEVITY_VIS_ARTS],
        ),
        DialogField(
            "vis_from",
            "Vis from",
            "select",
            "laboratory",
            options=[
                ("The laboratory's raw vis", "laboratory"),
                (f"{magus.name}'s raw vis", "character"),
                ("The covenant's vis stores", "covenant"),
            ],
        ),
    ]


def ritual_again_checks(
    saga: Saga, magus: Character, lab: Laboratory, text: Book
) -> tuple[Callable[[dict[str, Any]], str | None], Callable[[dict[str, Any]], str]]:
    """What the ritual-again form says as it is filled in: the reason it
    can't be done (or None), and the live line with its cost."""

    def check(values: dict[str, Any]):
        return lab_seasons.ritual_again(
            saga,
            magus,
            lab,
            text,
            values.get("vis_art") or "",
            values.get("vis_from") or "laboratory",
        )

    def problem(values: dict[str, Any]) -> str | None:
        found, _ = check(values)
        return found[0] if found else None

    def live(values: dict[str, Any]) -> str:
        found, again = check(values)
        if again is None:
            return todo(escape(found[0]))
        return (
            f"{again.pawns} pawn(s) of {values['vis_art']} vis; "
            f"{escape(again.subject.name)}'s aging rolls -{again.modifier}. "
            "No season is taken."
        )

    return problem, live


def ritual_again_form(
    saga: Saga, magus: Character, lab: Laboratory, text: Book
) -> Form:
    """Perform a Longevity Ritual again from its Lab Text: the vis to pay
    with and whose. It takes no season, so it is done at once."""
    problem, live = ritual_again_checks(saga, magus, lab, text)

    def apply(values: dict[str, Any]) -> Command | list[str]:
        found = seasons.perform_ritual_again(
            saga, magus, lab, text, values["vis_art"], values["vis_from"]
        )
        if found:
            return Refuse("Perform the Longevity Ritual again", escape(found[0]))
        return notes(f"{escape(text.ritual_subject)}'s ritual is renewed.")

    return Form(
        "Perform the Longevity Ritual again",
        lambda: ritual_again_fields(magus, text),
        apply,
        validate=problem,
        live=live,
        save_label="Perform",
    )


def perform_ritual(
    saga: Saga, lab: Laboratory, chosen_book: str | None = None
) -> Command:
    texts = ritual_texts(saga, lab)
    if not texts:
        return Refuse("Perform Ritual", "No Longevity Ritual texts here.")
    magus = saga.character(lab.owner_id)
    if magus is None:
        return Refuse(
            "Perform Ritual", "The laboratory has no owner to perform the ritual."
        )
    chosen = next((b for b in texts if b.id == chosen_book), None)
    if chosen is not None:
        return ritual_again_form(saga, magus, lab, chosen)
    return _one_of(
        "Perform which Longevity Ritual again?",
        texts,
        lambda b: escape(b.name),
        lambda b: ritual_again_form(saga, magus, lab, b),
    )


# --------------------------------------------------------------- New


def default_magus(page: Page) -> str | None:
    """The magus on show, or the laboratory's owner, if they have no
    Familiar yet: Bind Familiar's first choice."""
    magus = familiar_binder(page)
    return magus.id if magus is not None else None


def covenant_id(page: Page) -> str | None:
    return page.covenant.id if page.covenant is not None else None


def record_command(page: Page) -> Command:
    record = page.creation_record()
    if record is None:
        return Refuse("In Creation / In Play", "Nothing here has a creation mode.")
    return toggle_mode(page.saga, record)


def export_cult(saga: Saga, folder: Path) -> Form | Refuse:
    """Export one of the saga's own Mystery Cults to a file Import reads
    back into another saga (A Mystery Cult)."""
    if not saga.custom_cults:
        return Refuse(
            "Export a Cult",
            "The saga has no Mystery Cult of its own: add one on Saga Content.",
        )

    def apply(values: dict[str, Any]) -> Command | list[str]:
        cult = next(c for c in saga.custom_cults if c.id == values["cult"])
        name = (values.get("file") or "").strip().strip('"')
        path = (
            Path(name).expanduser() if name else folder / cult_transfer.file_name(cult)
        )
        if not path.name.lower().endswith(".json"):
            path = path.with_name(path.name + cult_transfer.SUFFIX)
        try:
            cult_transfer.export_to(path, cult)
        except OSError as problem:
            return Refuse(
                "Export a Cult",
                f"Couldn't write {escape(path.name)}: {escape(str(problem))}",
            )
        return notes(f"Exported {escape(cult.name)} to {escape(str(path))}.")

    first = saga.custom_cults[0]
    return Form(
        "Export a Cult",
        lambda: [
            DialogField(
                "cult",
                "Cult",
                "select",
                first.id,
                options=[(escape(c.name), c.id) for c in saga.custom_cults],
            ),
            DialogField(
                "file",
                "File",
                "text",
                str(folder / cult_transfer.file_name(first)),
                hint="Its Lore, degrees, Scripts and their components. Import it "
                "into another saga with Import, A Mystery Cult.",
            ),
        ],
        apply,
        save_label="Export",
        help_id="import-data",
    )


def export_saga(saga: Saga, folder: Path, deliver: Deliver | None = None) -> Form:
    """Export the whole saga to a file Import reads back (A Whole Saga);
    with `deliver`, straight to a browser."""

    def apply(values: dict[str, Any]) -> Command | list[str]:
        path = export_path(values)
        if deliver is not None:
            data = transfer.for_reader(transfer.export_saga_data(saga))
            return downloaded(deliver, path.name, data, saga.name)
        try:
            written = transfer.export_saga_to(path, saga)
        except OSError as problem:
            return Refuse(
                "Export Saga",
                f"Couldn't write {escape(path.name)}: {escape(str(problem))}",
            )
        return notes(f"Exported {escape(saga.name)} to {escape(str(written))}.")

    return Form(
        f"Export {escape(saga.name)}",
        lambda: [
            DialogField(
                "_what",
                "Exporting",
                "info",
                f"Saga: {saga.name} ({_saga_count(saga)})",
            ),
            DialogField(
                "file",
                "File",
                "text",
                str(folder / transfer.saga_file_name(saga)),
                hint="Every covenant, laboratory, character and familiar, with books, "
                "devices, spells and house rules. Import it with Import, A Whole "
                "Saga.",
            ),
        ],
        apply,
        validate=export_problem,
        live=export_live,
        save_label="Export",
    )


def _saga_count(saga: Saga) -> str:
    """ "1 covenant, 2 laboratories, 5 characters, 12 books"."""
    return ", ".join(
        f"{len(found)} {one if len(found) == 1 else many}"
        for found, one, many in (
            (saga.covenants, "covenant", "covenants"),
            (saga.laboratories, "laboratory", "laboratories"),
            (saga.characters, "character", "characters"),
            (saga.books, "book", "books"),
        )
    )


def export_command(page: Page) -> Command:
    record = page.record_to_export()
    if record is None:
        return Refuse("Export", "Nothing here to export.")
    return export_record(page.saga, record, storage.exports_dir(), page.deliver)


def markdown_command(page: Page) -> Command:
    deliver = page.deliver
    record = page.record_to_delete()

    def download(name: str, words: str) -> list[str]:
        assert deliver is not None
        deliver(name, words.encode("utf-8"), "text/markdown")
        return notes(f"Exported {escape(name)}: your browser downloads it.")

    return markdown_forms.export_markdown(
        page.saga, record, storage.exports_dir(), download if deliver else None
    )


def pack_command(page: Page) -> Command:
    deliver = page.deliver

    def download(name: str, data: dict[str, Any]) -> list[str]:
        assert deliver is not None
        return downloaded(deliver, name, data, data["name"])

    return packs.export_pack(
        page.saga, storage.exports_dir(), download if deliver else None
    )


def update_command(page: Page) -> Command:
    record = page.record_to_export()
    if record is None:
        return Refuse("Update from a File", "Nothing here to update.")
    return import_forms.update_record(page.saga, record)


def on_session(page: Page, step: Callable[[Saga, Session], Command]) -> Command:
    """`step` for the Session on show on its own page, or chosen in the
    Sessions list."""
    if page.session is not None:
        return step(page.saga, page.session)
    shown = sessions.in_order(page.saga)
    if page.row is None or not 0 <= page.row < len(shown):
        return Refuse("Sessions", "Choose a Session first.")
    return step(page.saga, shown[page.row])


def needs[T](
    get: Callable[[Page], T | None], build: Callable[[Saga, T], Command]
) -> Callable[[Page], Command]:
    def run(page: Page) -> Command:
        record = get(page)
        if record is None:
            return Refuse("More", "That isn't available here.")
        return build(page.saga, record)

    return run


def import_command(page: Page) -> Command:
    return import_forms.import_data(
        page.saga, page.covenant if page.kind == NodeKind.COVENANT else None
    )


def covenant(page: Page) -> Covenant | None:
    return page.covenant


def neighbour(page: Page) -> Neighbour | None:
    return page.neighbour


def character(page: Page) -> Character | None:
    return page.character


def sheet_roll_step(page: Page) -> Command:
    """Roll from the sheet: the chosen Ability or Characteristic (the
    terminal knows the row; the desktop's button asks)."""
    character = page.character
    if character is None:
        return Refuse("Roll", "That isn't available here.")
    problem = sheet_roll_forms.why_not_roll_here(page.saga, character)
    if problem:
        return Refuse("Roll", escape(problem))
    ability, characteristic = "", ""
    row = page.row if page.row is not None else -1
    if page.section == sheet_roll_forms.ABILITIES and 0 <= row < len(
        character.abilities
    ):
        ability = character.abilities[row].name
    if page.section == sheet_roll_forms.CHARACTERISTICS and 0 <= row < len(
        ROLL_CHARACTERISTICS
    ):
        characteristic = ROLL_CHARACTERISTICS[row]
    return sheet_roll_forms.roll_form(
        page.saga, character, ability=ability, characteristic=characteristic
    )


def on_agent(
    build: Callable[[Page, Character, int], Command],
) -> Callable[[Page], Command]:
    """A More command on the Agents list's chosen agent (`page.row`)."""

    def run(page: Page) -> Command:
        if page.character is None or page.row is None:
            return Refuse("More", "Choose an agent first.")
        return build(page, page.character, page.row)

    return run


def interests_command(page: Page, names: Mapping[str, str]) -> Command:
    """Edit Interests: `names` the label of each action an interest brings."""
    if page.character is not None:
        return interests_forms.interests_form(page.saga, page.character, names)
    if page.covenant is not None:
        return interests_forms.covenant_interests_form(page.saga, page.covenant, names)
    return Refuse("Interests", "That isn't available here.")


def _laboratory(page: Page) -> Laboratory | None:
    return page.laboratory


def found_command(page: Page) -> Command:
    record = page.record_to_delete()
    if not isinstance(record, Neighbour) or not places.is_ruin(record):
        return Refuse(
            "Found a Covenant Here", "Only a ruined covenant's site can be refounded."
        )
    return ruins.found_form(page.saga, record)


def begin_command(page: Page) -> Command:
    record = page.record_to_delete()
    if not isinstance(record, Neighbour) or not threats.is_dormant(record):
        return Refuse("Begin This Story", "Only a dormant threat can be begun.")
    return threats.begin_command(page.saga, record)


def take_up_command(page: Page) -> Command:
    record = page.record_to_delete()
    if not isinstance(record, Neighbour) or threats.is_dormant(record):
        return Refuse(story_chapters.TAKE_UP, "Only a threat under way is taken up.")
    return story_chapters.take_up_threat(page.saga, record)


def delay_command(page: Page) -> Command:
    record = page.record_to_delete()
    if not threats.is_threat(record) or threats.is_dormant(record):
        return Refuse(threats.DELAY_TITLE, "Only a threat under way can be delayed.")
    assert isinstance(record, Neighbour)
    return threats.delay_form(page.saga, record)


def arms_command(page: Page) -> Command:
    record = page.record_to_delete()
    if record is None or not arms.bears_arms(record):
        return Refuse("Arms", "Only a covenant, lord, town or faction bears arms.")
    return arms.arms_form(record)


#: The first steps of the page's actions that aren't More's or New's
#: (registry.STEPS has those).
OTHER_STEPS: dict[str, Callable[[Page], Command]] = {
    "edit_saga": lambda page: creation_forms.saga_details_form(page.saga),
}

"""The More and New menus and deleting a record, for a front-end that
shows one record's page at a time (the desktop), independent of how they
are drawn.

A `Page` is actions.ActionFacts for such a front-end: the record on show,
and no focused section. Its menus offer what actions.available offers
anywhere on the page: each More command is asked about with the page's
sections (PAGE_SECTIONS) one by one, and kept if any offers it. Every
command acts on the record on show, so the page counts as being "on the
record" (Delete, Export, In Creation / In Play); a command that would act
on a chosen row asks which first (a commands.Choose).

`command(page, action)` builds the first step of a menu entry, or of
Delete (`DELETE_RECORD`), as commands.py steps: mutating the saga only in
the last step's apply, so cancelling any step changes nothing.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, NamedTuple

from . import (
    creation,
    creation_forms,
    deletion,
    giving,
    import_forms,
    library_forms,
    neighbour_forms,
    neighbours,
    seasons,
    storage,
    transfer,
    tribunal_forms,
    tribunals,
    world,
)
from . import economics as eco
from . import familiars as fam
from . import inhabitants as inh
from . import lab_texts as lt
from . import spells as spl
from .actions import (
    MORE_MENU,
    NEW_MENU,
    RECORD_SECTION,
    MenuItem,
    NodeKind,
    available,
    silver_purse,
)
from .commands import Choice, Choose, Command, Confirm, Form, Refuse, notes
from .form_spec import DialogField, pairs
from .markup import escape, todo
from .models import (
    FULL,
    INCOME_EFFECTS,
    LINE,
    SEASONS,
    SKETCH,
    TEXT_LONGEVITY,
    Book,
    Character,
    Covenant,
    Familiar,
    IncomeSource,
    Laboratory,
    LabTextAccess,
    Neighbour,
    Saga,
    Spell,
    Tribunal,
)
from .rules import creation as creation_rules
from .rules import creation_covenant as cov_creation
from .rules import lab_seasons
from .sections import LAB_TEXTS_SECTION

#: The record a page shows, as deletion and actions take it.
Record = Covenant | Character | Laboratory | Familiar | Tribunal | Neighbour

#: Delete's action: the record on show, after a confirmation that says
#: what happens to what it owns.
DELETE_RECORD = "delete_record"

#: The More commands a page offers nowhere: the desktop shows them as the
#: section's own button (Fatigue beside Wounds in Health; Instill and Use
#: a Charge beside Enchanted Devices). The Creation Worksheet is offered,
#: but opens a page rather than running a command.
NOT_ON_PAGES = frozenset(
    {
        "edit_fatigue",
        "edit_familiar_fatigue",
        "instill_effect",
        "use_charge",
        "give",
        "withdraw_case",
        "roll_fair",
        "roll_table",
    }
)

#: Per page, the sections whose More commands its menu offers (None: the
#: page itself, with no section).
PAGE_SECTIONS: dict[NodeKind, tuple[str | None, ...]] = {
    NodeKind.SAGA: (None,),
    NodeKind.CHARACTER: (
        RECORD_SECTION[NodeKind.CHARACTER],
        "section-hermetic-background",
        "section-known-spells",
        "section-raw-vis-hermetic",
        "section-raw-vis-inventory",
        "section-inventory",
    ),
    NodeKind.FAMILIAR: (RECORD_SECTION[NodeKind.FAMILIAR],),
    NodeKind.TRIBUNAL: (RECORD_SECTION[NodeKind.TRIBUNAL],),
    NodeKind.NEIGHBOUR: (RECORD_SECTION[NodeKind.NEIGHBOUR],),
    NodeKind.LABORATORY: (
        RECORD_SECTION[NodeKind.LABORATORY],
        "section-lab-raw-vis",
        LAB_TEXTS_SECTION,
    ),
    NodeKind.COVENANT: (
        RECORD_SECTION[NodeKind.COVENANT],
        *(f"section-inh-{kind}" for kind in inh.AUTO_KINDS),
        "section-eco-income",
        "section-eco-wealth",
        "section-pos-vis_store",
        "section-lib-books",
    ),
}


@dataclass(frozen=True)
class Page:
    """The page on show, as actions.available asks about it
    (actions.ActionFacts): the saga, what kind of page, whose, and the
    section a command is being asked about (None: the page itself)."""

    saga: Saga
    kind: NodeKind | None
    covenant: Covenant | None = None
    character: Character | None = None
    laboratory: Laboratory | None = None
    familiar: Familiar | None = None
    tribunal: Tribunal | None = None
    neighbour: Neighbour | None = None
    section: str | None = None

    # -- actions.ActionFacts --

    @property
    def selected_kind(self) -> NodeKind | None:
        return self.kind

    @property
    def selected_covenant(self) -> Covenant | None:
        return self.covenant

    @property
    def selected_character(self) -> Character | None:
        return self.character

    @property
    def selected_laboratory(self) -> Laboratory | None:
        return self.laboratory

    def active_section(self) -> str | None:
        return self.section

    def player_may(self, action: str) -> bool:
        # The desktop is the storyguide's own copy.
        return True

    def on_record(self) -> bool:
        return True

    def creation_record(self) -> Character | Covenant | Laboratory | None:
        if self.kind == NodeKind.CHARACTER:
            return self.character
        if self.kind == NodeKind.COVENANT:
            return self.covenant
        if self.kind == NodeKind.LABORATORY:
            return self.laboratory
        return None

    def device_action_enabled(self, action: str) -> bool:
        return False

    def to_give(self) -> giving.Gift | None:
        # The desktop gives from each row's own Give.
        return None

    def record_to_export(self) -> transfer.Record | None:
        return self.creation_record()

    def record_to_delete(self) -> Record | None:
        if self.kind == NodeKind.FAMILIAR:
            return self.familiar
        if self.kind == NodeKind.TRIBUNAL:
            return self.tribunal
        if self.kind == NodeKind.NEIGHBOUR:
            return self.neighbour
        return self.creation_record()

    def can_send_files(self) -> bool:
        return True


def page_for(
    saga: Saga,
    kind: NodeKind | None,
    *,
    covenant_id: str | None = None,
    character_id: str | None = None,
    laboratory_id: str | None = None,
    familiar_id: str | None = None,
    tribunal_id: str | None = None,
    neighbour_id: str | None = None,
) -> Page:
    """The Page for a record's page, found by id: a character's or
    laboratory's covenant comes with it, and a familiar's magus."""
    character = saga.character(character_id)
    laboratory = saga.laboratory(laboratory_id)
    familiar = next((f for f in saga.familiars if f.id == familiar_id), None)
    if familiar is not None and character is None:
        character = fam.magus_of(saga, familiar)
    if covenant_id is None:
        covenant_id = (
            character.covenant_id
            if character is not None
            else laboratory.covenant_id
            if laboratory is not None
            else None
        )
    return Page(
        saga,
        kind,
        covenant=saga.covenant(covenant_id),
        character=character,
        laboratory=laboratory,
        familiar=familiar,
        tribunal=saga.tribunal(tribunal_id),
        neighbour=saga.neighbour(neighbour_id),
    )


#: The sections only a magus's sheet has.
_MAGUS_SECTIONS = frozenset(
    {"section-hermetic-background", "section-known-spells", "section-raw-vis-hermetic"}
)


def page_sections(page: Page) -> tuple[str | None, ...]:
    """The sections of PAGE_SECTIONS the page shows."""
    sections = PAGE_SECTIONS.get(page.kind, ()) if page.kind else ()
    if page.kind == NodeKind.CHARACTER and (
        page.character is None or page.character.type != "magus"
    ):
        sections = tuple(s for s in sections if s not in _MAGUS_SECTIONS)
    return sections


def _anything(_page: Page) -> bool:
    return True


#: More commands the page's menu leaves out while they have nothing to act
#: on (the terminal offers them in their section and then says so).
_PAGE_CHECKS: dict[str, Callable[[Page], bool]] = {
    "improve": lambda page: bool(
        page.covenant is not None and page.covenant.economics.income_sources
    ),
}


def more_items(page: Page) -> list[MenuItem]:
    """What More offers on the page, in the menu's order."""
    sections = page_sections(page)
    return [
        item
        for item in MORE_MENU
        if item.action not in NOT_ON_PAGES
        and _PAGE_CHECKS.get(item.action, _anything)(page)
        and any(
            available(item.action, replace(page, section=section))
            for section in sections
        )
    ]


def section_of(page: Page, action: str) -> str | None:
    """The first of the page's sections that offers `action`."""
    for section in page_sections(page):
        if available(action, replace(page, section=section)):
            return section
    return None


class ManageItem(NamedTuple):
    """One entry of a record's Manage chapter: its action (a More
    command's, or DELETE_RECORD), its label and a line on what it does."""

    action: str
    label: str
    detail: str


#: A record's Manage chapter: what manages it as a file rather than as
#: part of the saga, each with what it does; Delete is last.
MANAGE: dict[str, str] = {
    "export_record": "Write it to a file that another saga, or this saga on "
    "another computer, can import.",
    "update_record": "Read an export of it over it, for example after working "
    "on it elsewhere: shows what would change first, and keeps its place in "
    "this saga.",
    "promote": "Write more of it down: a line becomes a sketch with a "
    "statblock, and a sketch a full record, In Creation, keeping everything "
    "it had.",
    "demote": "Keep less of it: a full record becomes a sketch, left out "
    "of seasons, ageing and upkeep, and a sketch a line. Nothing is deleted; the "
    "chapters it no longer shows keep what they hold.",
    DELETE_RECORD: "Remove it from the saga, after saying what happens to "
    "what it holds.",
}

#: The More commands a record's own page offers instead: in its Manage
#: chapter, or as its In Creation / In Play toggle and the Creation
#: Worksheet beside it.
ON_THE_PAGE = frozenset({*MANAGE, "toggle_mode", "creation_worksheet"})


def manage_items(page: Page) -> list[ManageItem]:
    """What the page's Manage chapter offers, in order."""
    labels = {item.action: item.label for item in MORE_MENU}
    items = [
        ManageItem(action, labels[action], detail)
        for action, detail in MANAGE.items()
        if action != DELETE_RECORD and available(action, page)
    ]
    record = deletes(page)
    if record is not None:
        items.append(
            ManageItem(
                DELETE_RECORD,
                f"Delete {escape(record.name or '(unnamed)')}",
                MANAGE[DELETE_RECORD],
            )
        )
    return items


#: Edit Saga: in the saga page's Saga Management, where the terminal's e
#: edits it.
EDIT_SAGA = MenuItem("e", "edit_saga", "Edit Saga")

#: Where a front-end that shows one page at a time (the desktop), and so
#: has no New or More menu, offers each New and More action: in one of the
#: page's chapters or sections, by its name. A New action there is a New
#: card at the end of the cards it adds to. An action is offered only
#: where it is listed (Restore nowhere: Add on the Magi and Companions
#: lists brings someone back); every New and More action is listed, or
#: is one a record's page offers itself (ON_THE_PAGE) or a section's own
#: button (NOT_ON_PAGES).
PLACES: dict[str, tuple[tuple[NodeKind, str], ...]] = {
    "edit_saga": ((NodeKind.SAGA, "Saga Management"),),
    # On a covenant, books straight into its library.
    "import_data": ((NodeKind.SAGA, "Saga Management"), (NodeKind.COVENANT, "Library")),
    "export_saga": ((NodeKind.SAGA, "Saga Management"),),
    "set_date": ((NodeKind.SAGA, "Seasons"),),
    "create_covenant": ((NodeKind.SAGA, "Covenants"),),
    "create_tribunal": ((NodeKind.SAGA, "Tribunals"),),
    "create_neighbour": ((NodeKind.SAGA, "Neighbours"),),
    "create_character": (
        (NodeKind.SAGA, "Unassigned Characters"),
        (NodeKind.COVENANT, "People"),
        (NodeKind.CHARACTER_GROUP, "People"),
    ),
    "create_laboratory": (
        (NodeKind.SAGA, "Unassigned Laboratories"),
        (NodeKind.COVENANT, "Laboratories"),
    ),
    "create_familiar": (
        (NodeKind.CHARACTER, "Familiar"),
        (NodeKind.LABORATORY, "Planning"),
    ),
    "restore": (),
    # On each source of income's row.
    "improve": ((NodeKind.COVENANT, "Income"),),
    "lab_text_access": (
        (NodeKind.CHARACTER, "Hermetic Background"),
        (NodeKind.LABORATORY, "Lab Texts"),
    ),
    # The Shared tick in a known spell's form.
    "share_spell": ((NodeKind.CHARACTER, "Known Spells"),),
    "perform_ritual": ((NodeKind.LABORATORY, "Planning"),),
    "give_silver": (
        (NodeKind.CHARACTER, "Personal Gear"),
        (NodeKind.COVENANT, "Wealth"),
    ),
    "research_bonuses": ((NodeKind.COVENANT, "Library"),),
}

#: The saga page's Saga Management: each entry with what it does.
SAGA_MANAGEMENT: dict[str, str] = {
    "edit_saga": "Its name, storyguide and description, whether season "
    "records are kept, and the optional rules of the books in play.",
    "import_data": "Bring books, spells or records in from a file, such as "
    "another saga's export or a list of books.",
    "export_saga": "Write the whole saga, every record and what it holds, to "
    "one file that another saga, or this one on another computer, can import.",
}


def lives_at(action: str, kind: NodeKind, spot: str) -> bool:
    """Whether PLACES puts `action` at `spot` on a `kind` page."""
    return (kind, spot) in PLACES.get(action, ())


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
        or fam.familiar_of(page.saga, magus.id) is not None
    ):
        return None
    return magus


#: Whether the page offers a placed action where `available`, which
#: answers for the terminal's New and More, doesn't say.
_PLACED_CHECKS: dict[str, Callable[[Page], bool]] = {
    "edit_saga": lambda page: page.kind == NodeKind.SAGA,
    "create_familiar": lambda page: familiar_binder(page) is not None,
}


def placed(page: Page, spot: str) -> list[MenuItem]:
    """The actions the page offers at `spot` (a chapter's or section's
    name, or "New" / "More"), in PLACES's order."""
    items = {item.action: item for item in (EDIT_SAGA, *NEW_MENU, *MORE_MENU)}
    offered = {i.action for i in (*new_items(page), *more_items(page))}
    return [
        items[action]
        for action, places in PLACES.items()
        if (page.kind, spot) in places
        and (
            _PLACED_CHECKS[action](page)
            if action in _PLACED_CHECKS
            else action in offered
        )
    ]


def new_items(page: Page) -> list[MenuItem]:
    """What New can make from the page."""
    return [item for item in NEW_MENU if available(item.action, page)]


def deletes(page: Page) -> Record | None:
    """The record Delete deletes on the page, if any."""
    if page.kind is None or not available(DELETE_RECORD, page):
        return None
    return page.record_to_delete()


def command(page: Page, action: str) -> Command:
    """The first step of the menu entry `action` on the page."""
    saga = page.saga
    if action == DELETE_RECORD:
        record = deletes(page)
        if record is None:
            return Refuse("Delete", "Nothing here to delete.")
        return delete_record(saga, record)
    builder = _COMMANDS.get(action)
    if builder is None:
        return Refuse("More", "That isn't available here.")
    return builder(page)


# ------------------------------------------------------------ the record


def delete_record(saga: Saga, record: Record) -> Confirm:
    """ "Delete <name>?", saying what happens to what it owns."""
    consequences, do = _deletion_of(saga, record)
    message = f"Delete {escape(record.name)}?"
    if consequences:
        message += "\n\n" + "\n".join(map(escape, consequences))
    return Confirm(message, do)


def _deletion_of(saga: Saga, record: Record) -> tuple[list[str], Callable[[], None]]:
    if isinstance(record, Tribunal):
        return (
            tribunals.deletion_consequences(saga, record),
            lambda: tribunals.delete(saga, record),
        )
    if isinstance(record, Neighbour):
        return (
            neighbours.deletion_consequences(saga, record),
            lambda: neighbours.delete(saga, record),
        )
    if isinstance(record, Covenant):
        return (
            deletion.covenant_consequences(saga, record),
            lambda: deletion.delete_covenant(saga, record),
        )
    if isinstance(record, Character):
        return (
            deletion.character_consequences(saga, record),
            lambda: deletion.delete_character(saga, record),
        )
    if isinstance(record, Familiar):
        return (
            deletion.familiar_consequences(saga, record),
            lambda: deletion.delete_familiar(saga, record),
        )
    return (
        deletion.laboratory_consequences(saga, record),
        lambda: deletion.delete_laboratory(saga, record),
    )


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


def _detail_command(action: str) -> Callable[[Page], Command]:
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
            hint="What it holds travels with it: a character's familiar, devices, "
            "books and Diary; a laboratory's books and devices. Import it into "
            "another saga with More's Import on that saga.",
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
    if name and not path.name.lower().endswith(".json"):
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


def export_record(saga: Saga, record: transfer.Record, folder: Path) -> Form:
    """Export a covenant, laboratory or character to a file another saga
    can import."""

    def apply(values: dict[str, Any]) -> Command | list[str]:
        path = export_path(values)
        try:
            transfer.export_to(
                path, saga, record, with_members=bool(values.get("with_members"))
            )
        except OSError as problem:
            return Refuse(
                f"Export {escape(record.name)}",
                f"Couldn't write {escape(path.name)}: {escape(str(problem))}",
            )
        return notes(f"Exported {escape(record.name)} to {escape(str(path))}.")

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
        for kind in inh.AUTO_KINDS
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

    def label(pair: tuple[str, inh.InhabitantEntry]) -> str:
        kind, entry = pair
        name = escape(entry.name) or "(unnamed)"
        return name if len(kinds) == 1 else f"{name} ({inh.KIND_SINGULAR[kind]})"

    def choose(pair: tuple[str, inh.InhabitantEntry]) -> None:
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
    ]


def improve_live(source: IncomeSource) -> Callable[[dict[str, Any]], str]:
    def live(values: dict[str, Any]) -> str:
        effect = values.get("effect") or "Status Quo"
        return (
            f"Income Multiplier {eco.income_multiplier_text(effect)}. "
            f"Projected Income {eco.projected_income(source.current_income, effect)}"
        )

    return live


def improve_form(saga: Saga, source: IncomeSource) -> Form:
    """Manually simulate a year's Income Modification: choosing an Effect
    shows the Multiplier and Projected Income; Commit asks to confirm."""
    name = escape(source.name or "this source of income")

    def apply(values: dict[str, Any]) -> Confirm:
        current = source.current_income
        effect = values["effect"]
        projected = eco.projected_income(current, effect)

        def update() -> None:
            source.income = projected
            source.note = eco.improvement_note(
                saga.current_year, source.name, effect, current, projected
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
        live=improve_live(source),
        save_label="Commit",
    )


def improve(saga: Saga, covenant: Covenant) -> Command:
    sources = covenant.economics.income_sources
    if not sources:
        return Refuse("Improve Income", "No sources of income to improve.")
    return _one_of(
        "Improve which source of income?",
        list(sources),
        lambda s: escape(s.name) or "(unnamed)",
        lambda s: improve_form(saga, s),
    )


def research_bonuses(saga: Saga, covenant: Covenant) -> Command:
    """Set up the covenant library's research bonuses, a subject at a
    time."""
    return library_forms.research_walkthrough(saga, covenant)


# ------------------------------------------------------------- the character


def share_spell(saga: Saga, character: Character) -> Command:
    """Make one of the magus's invented spells available to the saga: it
    moves to the saga's Spells, and they still know it."""
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

    return _one_of(
        "Share which invented spell?",
        shareable,
        lambda s: f"{escape(s.name)} ({spl.shorthand(s)})",
        confirm,
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
            "; ".join(known.values()) or "(only his own and general texts)",
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


def ritual_again_form(
    saga: Saga, magus: Character, lab: Laboratory, text: Book
) -> Form:
    """Perform a Longevity Ritual again from its Lab Text: the vis to pay
    with and whose. It takes no season, so it is done at once."""

    def check(values: dict[str, Any]):
        return lab_seasons.ritual_again(
            saga,
            magus,
            lab,
            text,
            values.get("vis_art") or "",
            values.get("vis_from") or "laboratory",
        )

    def live(values: dict[str, Any]) -> str:
        found, again = check(values)
        if again is None:
            return todo(escape(found[0]))
        return (
            f"{again.pawns} pawn(s) of {values['vis_art']} vis; "
            f"{escape(again.subject.name)}'s aging rolls -{again.modifier}. "
            "No season is taken."
        )

    def problem(values: dict[str, Any]) -> str | None:
        found, _ = check(values)
        return found[0] if found else None

    def apply(values: dict[str, Any]) -> Command | list[str]:
        found = seasons.perform_ritual_again(
            saga, magus, lab, text, values["vis_art"], values["vis_from"]
        )
        if found:
            return Refuse("Perform the Longevity Ritual again", escape(found[0]))
        return notes(f"{escape(text.ritual_subject)}'s ritual is renewed.")

    return Form(
        "Perform the Longevity Ritual again",
        lambda: [
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
        ],
        apply,
        validate=problem,
        live=live,
        save_label="Perform",
    )


def perform_ritual(saga: Saga, lab: Laboratory) -> Command:
    texts = ritual_texts(saga, lab)
    if not texts:
        return Refuse("Perform Ritual", "No Longevity Ritual texts here.")
    magus = saga.character(lab.owner_id)
    if magus is None:
        return Refuse(
            "Perform Ritual", "The laboratory has no owner to perform the ritual."
        )
    return _one_of(
        "Perform which Longevity Ritual again?",
        texts,
        lambda b: escape(b.name),
        lambda b: ritual_again_form(saga, magus, lab, b),
    )


# --------------------------------------------------------------- New


def _default_magus(page: Page) -> str | None:
    """The magus on show, or the laboratory's owner, if they have no
    Familiar yet: Bind Familiar's first choice."""
    magus = familiar_binder(page)
    return magus.id if magus is not None else None


def _covenant_id(page: Page) -> str | None:
    return page.covenant.id if page.covenant is not None else None


def _record_command(page: Page) -> Command:
    record = page.creation_record()
    if record is None:
        return Refuse("In Creation / In Play", "Nothing here has a creation mode.")
    return toggle_mode(page.saga, record)


def export_saga(saga: Saga, folder: Path) -> Form:
    """Export the whole saga to a file Import reads back (A Whole Saga)."""

    def apply(values: dict[str, Any]) -> Command | list[str]:
        path = export_path(values)
        try:
            transfer.export_saga_to(path, saga)
        except OSError as problem:
            return Refuse(
                "Export Saga",
                f"Couldn't write {escape(path.name)}: {escape(str(problem))}",
            )
        return notes(f"Exported {escape(saga.name)} to {escape(str(path))}.")

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
                hint="Every covenant, laboratory, character and familiar, with "
                "their books, devices and the saga's own spells and house rules. "
                "Import it into another saga with Import, A Whole Saga.",
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


def _export_command(page: Page) -> Command:
    record = page.record_to_export()
    if record is None:
        return Refuse("Export", "Nothing here to export.")
    return export_record(page.saga, record, storage.EXPORTS_DIR)


def _update_command(page: Page) -> Command:
    record = page.record_to_export()
    if record is None:
        return Refuse("Update from a File", "Nothing here to update.")
    return import_forms.update_record(page.saga, record)


def _needs[T](
    get: Callable[[Page], T | None], build: Callable[[Saga, T], Command]
) -> Callable[[Page], Command]:
    def run(page: Page) -> Command:
        record = get(page)
        if record is None:
            return Refuse("More", "That isn't available here.")
        return build(page.saga, record)

    return run


def _silver_command(page: Page) -> Command:
    section = section_of(page, "give_silver")
    purse = silver_purse(replace(page, section=section))
    if purse is None:
        return Refuse("Give Silver", "No silver to give here.")
    return giving.give(page.saga, giving.SILVER, purse)


def _import_command(page: Page) -> Command:
    return import_forms.import_data(
        page.saga, page.covenant if page.kind == NodeKind.COVENANT else None
    )


def _covenant(page: Page) -> Covenant | None:
    return page.covenant


def _character(page: Page) -> Character | None:
    return page.character


def _laboratory(page: Page) -> Laboratory | None:
    return page.laboratory


#: Each menu entry's first step, by its action.
_COMMANDS: dict[str, Callable[[Page], Command]] = {
    "restore": _needs(_covenant, restore),
    "improve": _needs(_covenant, improve),
    "perform_ritual": _needs(_laboratory, perform_ritual),
    "share_spell": _needs(_character, share_spell),
    "give_silver": _silver_command,
    "lab_text_access": _needs(_character, lab_text_access),
    "import_data": _import_command,
    "research_bonuses": _needs(_covenant, research_bonuses),
    "export_record": _export_command,
    "export_saga": lambda page: export_saga(page.saga, storage.EXPORTS_DIR),
    "update_record": _update_command,
    "toggle_mode": _record_command,
    "promote": _detail_command("promote"),
    "demote": _detail_command("demote"),
    "set_date": lambda page: set_date(page.saga),
    "edit_saga": lambda page: creation_forms.edit_saga_form(page.saga),
    "create_covenant": lambda page: creation_forms.new_covenant_form(page.saga),
    "create_tribunal": lambda page: tribunal_forms.new_tribunal_form(page.saga),
    "create_neighbour": lambda page: neighbour_forms.new_neighbour(page.saga),
    "create_character": lambda page: creation_forms.new_character_form(
        page.saga, _covenant_id(page)
    ),
    "create_laboratory": lambda page: creation_forms.new_laboratory_form(
        page.saga, _covenant_id(page)
    ),
    "create_familiar": lambda page: creation_forms.bind_familiar_form(
        page.saga, _default_magus(page)
    ),
}

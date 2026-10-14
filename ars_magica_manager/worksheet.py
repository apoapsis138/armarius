"""The Creation Worksheet, independent of how it is drawn: for each step
of a record In Creation (rules.creation.steps_for), what the step shows
and what its buttons and list rows do.

A step's `Panel` has its budget text, its buttons (`Action`s) and its
list (`StepList`: a heading line and `Row`s, with what Add does). Every
button and row verb starts a command (commands.py), the same steps the
sheets' own buttons run, so a front-end draws the worksheet once and runs
its commands as it runs the sheets'. `PANELS` holds each step's panel; a
step with none shows only its checks. The last step ends with
worksheet_forms.move_to_play.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any

from . import books as bk
from . import catalog, creation, device_forms, library_forms
from . import character_forms as cf
from . import covenant_forms as covf
from . import covenant_templates as templates
from . import covenants as cov_rules
from . import inhabitant_forms as inhf
from . import inhabitants as inh
from . import laboratories as lab_rules
from . import laboratory_forms as labf
from . import possession_forms as posf
from . import possessions as pos
from . import sheet_text as st
from . import spells as spl
from . import trait_forms as tf
from . import virtue_forms as vf
from . import worksheet_forms as wf
from .arts import ART_DESCRIPTIONS, ARTS
from .boon_hook_text import boon_hook_info_text
from .commands import Act, Choice, Choose, Command, Confirm
from .covenants import boon_hook_points, covenant_boon_points, covenant_hook_points
from .markup import aligned, escape
from .models import (
    INCOME_TYPE_DEFAULTS,
    ArtScore,
    Book,
    Character,
    Covenant,
    CreationXp,
    EnchantedDevice,
    IncomeSource,
    Inhabitant,
    Laboratory,
    Possession,
    Saga,
)
from .rules import creation as rules
from .rules import creation_access as access
from .rules import creation_character as cc
from .rules import creation_characteristics as cch
from .rules import creation_covenant as cov
from .rules import creation_later as later
from .rules import creation_magus as magus
from .rules import creation_packages as packages
from .rules import creation_virtues as cv
from .rules import creation_xp as cx
from .rules import scores
from .rules import xp as xp_rules
from .worksheet_forms import MARKS, Record

Start = Callable[[], Command]


@dataclass
class Action:
    """A button on a step: `start` builds its first step."""

    label: str
    start: Start


@dataclass
class Row:
    """A row of a step's list: its label (markup, in the list's columns),
    the details shown while it is chosen, and what Edit and Delete start
    (None: that verb does nothing on this row). A heading row has no
    verbs and can't be chosen. `cells` is the same row a cell per column
    of its list's `columns`, for a front-end that draws a real table (a
    heading's other cells, when set, title the columns of the rows under
    it)."""

    label: str
    details: str = ""
    edit: Start | None = None
    delete: Start | None = None
    heading: bool = False
    cells: list[str] | None = None


@dataclass
class StepList:
    """A step's list: its column headings, rows, and what Add starts."""

    header: str
    rows: Callable[[Saga, Record], list[Row]]
    add: Callable[[Saga, Record], Command] | None = None
    #: What Add, Edit and Delete do here, as their buttons say ("Spend xp").
    add_label: str = "Add"
    #: None: no row can be edited.
    edit_label: str | None = "Edit"
    delete_label: str = "Delete"
    #: The details before a row is chosen.
    hint: str = "Choose a row to see its details."
    #: `header`'s column titles, one a cell of each row (Row.cells).
    columns: list[str] = field(default_factory=list)


@dataclass
class Panel:
    """What a step shows above its checks."""

    #: The step's budget and what's spent, as markup (may be "").
    budget: Callable[[Saga, Record], str] = lambda saga, record: ""
    #: The step's buttons for this record.
    actions: Callable[[Saga, Record], list[Action]] = lambda saga, record: []
    #: The step's list (None: it has none).
    list: StepList | None = field(default=None)


#: (record kind, step key) -> the step's panel. Record kind:
#: "character", "covenant" or "laboratory".
PANELS: dict[tuple[str, str], Panel] = {}


def record_kind(record: Record) -> str:
    if isinstance(record, Character):
        return "character"
    if isinstance(record, Covenant):
        return "covenant"
    return "laboratory"


def panel_for(record: Record, step: str) -> Panel:
    return PANELS.get((record_kind(record), step), Panel())


def check_lines(found: list[rules.Check]) -> str:
    """Creation checks as worksheet lines: a mark, the rule, what the record
    has."""
    if not found:
        return "[dim]No creation checks at this step.[/]"
    return "\n".join(
        f"{MARKS[c.status]} {escape(c.label)}: {escape(c.detail)}" for c in found
    )


def step_label(saga: Saga, record: Record, step: rules.Step) -> str:
    """A step as the progress list shows it: its mark and title."""
    return (
        f"{MARKS[rules.step_status(rules.checks(saga, record, step.key))]} {step.title}"
    )


def progress_text(saga: Saga, record: Record) -> str:
    """How many steps pass, and every check's tally."""
    statuses = [
        rules.step_status(rules.checks(saga, record, s.key))
        for s in rules.steps_for(record)
    ]
    # Steps with no checks (a review) don't count either way.
    checked = [status for status in statuses if status != "none"]
    done = sum(status == "pass" for status in checked)
    return (
        f"{done} of {len(checked)} steps pass\n"
        f"{rules.summary(rules.checks(saga, record))}"
    )


def title(record: Record) -> str:
    mode = "In Creation" if record.in_creation else "In Play"
    return f"Creation Worksheet: {escape(record.name)} ({mode})"


def pad(text: str, width: int) -> str:
    """`text` escaped for markup and padded to `width` columns (cut with an
    ellipsis if it's longer), counting the text as shown."""
    if len(text) >= width:
        text = text[: width - 2] + "…"
    return escape(text) + " " * (width - len(text))


def review_lines(saga: Saga, record: Record) -> list[str]:
    """Each step with its open checks: "Concept: 1 warning"."""
    lines = []
    for step in rules.steps_for(record):
        found = rules.checks(saga, record, step.key)
        open_checks = [c for c in found if c.status != "pass"]
        if open_checks:
            lines.append(f"  {step.title}: {rules.summary(open_checks)}")
    return lines or ["  every check passes"]


def _character(record: Record) -> Character:
    assert isinstance(record, Character)
    return record


def _covenant(record: Record) -> Covenant:
    assert isinstance(record, Covenant)
    return record


def _laboratory(record: Record) -> Laboratory:
    assert isinstance(record, Laboratory)
    return record


# -- Concept: type, House and age --


def _concept_budget(saga: Saga, record: Record) -> str:
    character = _character(record)
    years = cc.age(saga, character)
    rows: list[tuple[str, object]] = [("Type", character.type)]
    if character.type == "magus":
        house = character.hermetic.house
        rows.append(("House", escape(cc.house_name(house)) if house else "(none)"))
        house_def = catalog.load_house_catalog_by_id().get(house or "")
        if house_def is not None and house_def.benefit:
            rows.append(("House benefit", escape(house_def.benefit)))
    rows.append(
        (
            "Age",
            f"{years} (born {character.background.year_born})"
            if years is not None
            else "(set Year Born)",
        )
    )
    return aligned(rows)


def _description_edit(saga: Saga, character: Character, section: str) -> Start:
    return lambda: cf.description_edits(saga, character)[section]


def _concept_actions(saga: Saga, record: Record) -> list[Action]:
    character = _character(record)
    actions = [
        Action("Edit type", lambda: cf.character_info_form(saga, character)),
        Action(
            "Edit Year Born",
            _description_edit(saga, character, "Biographical Detail"),
        ),
    ]
    if character.type == "magus":
        actions.append(
            Action(
                "Edit House", _description_edit(saga, character, "Hermetic Background")
            )
        )
        missing = cc.missing_type_virtues(character)
        if missing:
            by_id = catalog.load_virtue_flaw_catalog_by_id()
            names = " and ".join(by_id[vf_id].name for vf_id in missing)
            actions.append(
                Action(f"Add {names}", lambda: wf.add_type_virtues(character))
            )
        house = catalog.load_house_catalog_by_id().get(character.hermetic.house or "")
        if (
            house is not None
            and house.virtues
            and not any(cv.held_option(character, o) for o in house.virtues)
        ):
            actions.append(
                Action("Add the House Virtue", lambda: wf.add_house_virtue(character))
            )
    if character.type == "mythic companion":
        actions.append(
            Action("Choose status Virtue", lambda: wf.mythic_status(saga, character))
        )
    return actions


PANELS[("character", "concept")] = Panel(_concept_budget, _concept_actions)


# -- Virtues and Flaws --


def _virtues_budget(saga: Saga, record: Record) -> str:
    character = _character(record)
    t = cv.tally(character)
    fewest, most = cv.virtue_allowance(character, t.flaw_points)
    allowed = f"{most}" if fewest == most else f"{fewest}-{most}"
    rows: list[tuple[str, object]] = [
        ("Virtue points", f"{t.virtue_points} (allowed {allowed})"),
        (
            "Flaw points",
            f"{t.flaw_points} of {cv.max_flaw_points(character)}, "
            f"{t.minor_flaws} of {cv.max_minor_flaws(character)} Minor Flaws",
        ),
    ]
    house = cv.house_benefit(character)
    if house.held:
        rows.append(("Free from the House", escape(", ".join(house.held))))
    if house.missing:
        rows.append(("House still gives", escape("; ".join(house.missing))))
    return aligned(rows)


#: The Virtues and Flaws list's columns.
VF_NAME = 44
VF_TIER = 8
VF_HEADER = f"  {'Virtue or Flaw':<{VF_NAME}}{'Tier':<{VF_TIER}}Type"
VF_COLUMNS = ["Virtue or Flaw", "Tier", "Type"]


def _remove_virtue_flaw(saga: Saga, owner: Any, instance: Any) -> Start:
    """Delete `instance` from the owner's Virtues and Flaws (found again
    when asked, since the list may have changed)."""
    return lambda: vf.remove_virtue_flaw(
        saga, owner, owner.virtues_flaws.index(instance)
    )


def _virtue_rows(saga: Saga, record: Record) -> list[Row]:
    """The character's Virtues, then its Flaws, each with its book text."""
    character = _character(record)
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    rows: list[Row] = []
    for side, heading in (("Virtue", "Virtues"), ("Flaw", "Flaws")):
        taken = [
            (index, instance, definition)
            for index, instance in enumerate(character.virtues_flaws)
            if (definition := by_id.get(instance.vf_id)) is not None
            and definition.side == side
        ]
        if not taken:
            continue
        rows.append(Row(heading, heading=True, cells=[heading]))
        for index, instance, definition in taken:
            name = catalog.describe_virtue_flaw(instance, by_id)
            rows.append(
                Row(
                    f"{pad(name, VF_NAME)}{definition.tier:<{VF_TIER}}"
                    f"{escape(definition.category_label)}",
                    st.vf_info_text(character.virtues_flaws, index),
                    delete=_remove_virtue_flaw(saga, character, instance),
                    cells=[
                        escape(name),
                        definition.tier,
                        escape(definition.category_label),
                    ],
                )
            )
    return rows


def _add_virtue_flaw(saga: Saga, owner: Any, side: str | None) -> Command:
    add = vf.virtue_flaw_ops(saga, owner, side).add
    assert add is not None
    return add()


PANELS[("character", "virtues_flaws")] = Panel(
    _virtues_budget,
    lambda saga, record: [
        Action("Add a Flaw", lambda: _add_virtue_flaw(saga, record, "Flaw"))
    ],
    StepList(
        VF_HEADER,
        _virtue_rows,
        columns=VF_COLUMNS,
        add=lambda saga, record: _add_virtue_flaw(saga, record, "Virtue"),
        add_label="Add a Virtue",
        edit_label=None,
        delete_label="Remove",
        hint="Choose a Virtue or Flaw to read its rules.",
    ),
)


# -- Characteristics --


def _characteristics_budget(saga: Saga, record: Record) -> str:
    character = _character(record)
    found = cch.lines(saga, character)
    spent = sum(line.cost for line in found)
    rows = [
        (
            line.name,
            f"{line.score:+d}  (bought {line.bought:+d}, cost {line.cost:+d}"
            + (f", Great x{line.virtue}" if line.virtue > 0 else "")
            + (f", Poor x{-line.virtue}" if line.virtue < 0 else "")
            + (f", heritage {line.free:+d}" if line.free else "")
            + ")",
        )
        for line in found
    ]
    rows.append(("Points", f"{spent} of {cch.budget(character)}"))
    return aligned(rows)


def _characteristics_actions(saga: Saga, record: Record) -> list[Action]:
    character = _character(record)
    actions = [
        Action("Edit Characteristics", lambda: cf.characteristics_form(saga, character))
    ]
    if cch.grog_arrays_offered(saga, character):
        actions.append(
            Action("Fill from a Grogs array", lambda: wf.grog_array(character))
        )
    return actions


PANELS[("character", "characteristics")] = Panel(
    _characteristics_budget, _characteristics_actions
)


# -- the xp steps --


#: Each kind of creation entry, as the details say where xp came from.
ENTRY_STEPS: dict[str, str] = {
    "childhood": "Early Childhood",
    "later_life": "Later Life",
    "package": "Training package",
    "virtue": "Virtue xp",
    "free": "Free Virtue score",
    "apprenticeship": "Apprenticeship",
    "gauntlet": "Years past Gauntlet",
}

#: The xp list's columns.
XP_NAME = 30
XP_HEADER = (
    f"  {'Ability or Art':<{XP_NAME}}{'Spent':>6}{'Gained':>8}{'Score':>7}   Specialty"
)
XP_COLUMNS = ["Ability or Art", "Spent", "Gained", "Score", "Specialty"]


def target_score(character: Character, target: str) -> tuple[xp_rules.Progress, str]:
    """`target`'s score and xp on the sheet, and its Specialty."""
    if target in ARTS:
        score = character.arts.get(target.lower(), ArtScore())
        return score.progress, ""
    ability = next((a for a in character.abilities if a.name == target), None)
    if ability is None:
        return xp_rules.progress(0, xp_rules.ABILITY_FACTOR), ""
    return ability.progress, ability.specialty or ""


def xp_label(character: Character, entry: CreationXp, suffix: str = "") -> str:
    """An xp row: what it went on, the pool xp spent and the xp it gained
    (more with an Affinity), the score now and the Specialty."""
    progress, specialty = target_score(character, entry.target)
    gained = creation.gained_xp(entry)
    gained_text = f"{gained:>8}"
    if gained != entry.xp:
        gained_text = f"[$text-success]{gained_text}[/]"
    return (
        f"{pad(entry.target + suffix, XP_NAME)}{entry.xp:>6}{gained_text}"
        f"{progress.score:>7}   {escape(specialty)}"
    )


def xp_cells(character: Character, entry: CreationXp, suffix: str = "") -> list[str]:
    """xp_label's row, a cell per XP_COLUMNS."""
    progress, specialty = target_score(character, entry.target)
    gained = creation.gained_xp(entry)
    gained_text = str(gained)
    if gained != entry.xp:
        gained_text = f"[$text-success]{gained_text}[/]"
    return [
        escape(entry.target + suffix),
        str(entry.xp),
        gained_text,
        str(progress.score),
        escape(specialty),
    ]


def xp_details(saga: Saga, character: Character, target: str) -> str:
    """The details of an Art or Ability xp was spent on: its score and xp,
    any Affinity and the creation cap, every worksheet spend on it, and
    what it is."""
    progress, _ = target_score(character, target)
    is_art = target in ARTS
    if is_art:
        bonus, bonus_from = 0, []
        description = ART_DESCRIPTIONS.get(target, "")
        kind = "Art"
    else:
        bonus, bonus_from = scores.ability_bonus(character.virtues_flaws, target)
        definition = st.ability_definition(target)
        description = definition.description if definition else ""
        kind = f"{definition.category} Ability" if definition else "Ability"
    lines = [f"[b]{escape(target)}[/]  [dim]{escape(kind)}[/]"]
    lines.append(st.xp_line(progress, bonus, bonus_from))
    if access.xp_multiplier(character, target) > 1:
        lines.append("[b]Affinity:[/] pool xp spent on it gains half again, rounded up")
    if not is_art:
        cap = access.ability_cap_for(character, cc.age(saga, character), target)
        if cap is None:
            lines.append("[b]Creation cap:[/] none (Mentored by Demons)")
        else:
            over = " [$text-error](over it)[/]" if progress.score > cap else ""
            lines.append(f"[b]Creation cap:[/] {cap}{over}")
    spends = [
        f"{ENTRY_STEPS.get(x.step, x.step)} {x.xp}"
        + (
            f" (gained {creation.gained_xp(x)})"
            if creation.gained_xp(x) != x.xp
            else ""
        )
        for x in character.creation_xp
        if x.target == target and x.step in ENTRY_STEPS
    ]
    if spends:
        lines.append(f"[b]Spent on it:[/] {escape(', '.join(spends))}")
    if description:
        lines += ["", escape(description)]
    return "\n".join(lines)


def xp_row(
    saga: Saga,
    character: Character,
    entry: CreationXp,
    targets: Sequence[str] | None,
) -> Row:
    """A row for an xp spend: Edit changes it (with `targets` to choose
    from; None: it can't be changed, only taken back), Delete takes it
    back."""
    return Row(
        xp_label(character, entry),
        xp_details(saga, character, entry.target),
        edit=(
            None
            if targets is None
            else lambda: wf.change_xp(saga, character, entry, targets)
        ),
        delete=lambda: wf.refund_xp(character, entry),
        cells=xp_cells(character, entry),
    )


def xp_rows(
    saga: Saga, character: Character, step: str, targets: Sequence[str]
) -> list[Row]:
    return [xp_row(saga, character, x, targets) for x in cx.entries(character, step)]


def xp_list(
    step: str,
    targets: Callable[[Saga, Character], Sequence[str]],
    rows: Callable[[Saga, Record], list[Row]] | None = None,
    add_label: str = "Spend xp",
) -> StepList:
    """An xp step's list: Add spends the step's pool xp, Edit changes the
    chosen spend, Delete takes it back."""
    return StepList(
        XP_HEADER,
        rows
        or (
            lambda saga, record: xp_rows(
                saga, _character(record), step, targets(saga, _character(record))
            )
        ),
        add=lambda saga, record: wf.spend_xp(
            saga, _character(record), step, targets(saga, _character(record))
        ),
        add_label=add_label,
        edit_label="Change its xp",
        delete_label="Take it back",
        hint="Choose a row to see what the xp bought.",
        columns=XP_COLUMNS,
    )


# -- Early Childhood --


def _childhood_budget(saga: Saga, record: Record) -> str:
    character = _character(record)
    native = wf.native_entry(character)
    others = cx.spent(character, "childhood") - (native.xp if native else 0)
    return aligned(
        [
            (
                "Native Language",
                f"{escape(native.target)} ({native.xp} xp)" if native else "(not set)",
            ),
            ("Other childhood xp", f"{others} of {cx.CHILDHOOD_XP}"),
        ]
    )


def _childhood_rows(saga: Saga, record: Record) -> list[Row]:
    """The childhood's spends; the Native Language's row changes the
    language."""
    character = _character(record)
    targets = cx.childhood_targets()
    rows = []
    for entry in cx.entries(character, "childhood"):
        row = xp_row(saga, character, entry, targets)
        if entry.note == cx.NATIVE:
            row.label = xp_label(character, entry, " (native)")
            row.cells = xp_cells(character, entry, " (native)")
            row.edit = lambda: wf.native_language(character)
        rows.append(row)
    return rows


PANELS[("character", "childhood")] = Panel(
    _childhood_budget,
    lambda saga, record: [
        Action("Native Language", lambda: wf.native_language(_character(record))),
        Action(
            "Use a sample childhood",
            lambda: wf.sample_childhood(saga, _character(record)),
        ),
    ],
    xp_list("childhood", lambda saga, c: cx.childhood_targets(), rows=_childhood_rows),
)


# -- Later Life --


def _later_life_budget(saga: Saga, record: Record) -> str:
    character = _character(record)
    years = later.bought_years(saga, character)
    ends = later.later_life_ends(saga, character)
    until = "apprenticeship" if character.type == "magus" else "now"
    budget = later.later_life_budget(saga, character)
    spent = cx.spent(character, "later_life")
    lines = [
        f"Later Life: age 5 to {ends if ends is not None else '?'} ({until}), "
        f"{years} years at {later.xp_a_year(character)} xp = {budget} xp, "
        f"[b]{spent} spent, {budget - spent} left[/]"
    ]
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    for vf_id, rule in access.virtue_xp(character).items():
        own = sum(x.xp for x in cx.entries(character, "virtue") if x.note == vf_id)
        lines.append(f"{escape(by_id[vf_id].name)}: {rule.xp} xp, {own} spent")
    cap = access.ability_cap(cc.age(saga, character))
    lines.append(f"Ability cap at this age: {cap} (2 more with an Affinity)")
    return "\n".join(lines)


def _later_life_rows(saga: Saga, record: Record) -> list[Row]:
    """Later Life's own spends, then each training package, each Virtue's
    own xp and the free Virtue scores, under headings."""
    character = _character(record)
    rows = xp_rows(saga, character, "later_life", later.later_life_targets(character))
    for taken in packages.taken(character):
        rows.append(
            Row(
                label
                := f"Training package: {escape(taken.name)} ({taken.years} years)",
                heading=True,
                cells=[label],
            )
        )
        for entry in cx.entries(character, "package"):
            if entry.note == taken.note:
                row = xp_row(saga, character, entry, None)
                row.delete = lambda note=taken.note: wf.drop_package(character, note)
                rows.append(row)
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    for vf_id in access.virtue_xp(character):
        own = [x for x in cx.entries(character, "virtue") if x.note == vf_id]
        if own:
            heading = f"{escape(by_id[vf_id].name)} xp"
            rows.append(Row(heading, heading=True, cells=[heading]))
            targets = later.virtue_targets(character, vf_id)
            rows += [xp_row(saga, character, x, targets) for x in own]
    free = cx.entries(character, "free")
    if free:
        rows.append(
            Row("Free Virtue scores", heading=True, cells=["Free Virtue scores"])
        )
        rows += [xp_row(saga, character, x, None) for x in free]
    return rows


def _virtue_xp_action(saga: Saga, character: Character, vf_id: str) -> Action:
    name = catalog.load_virtue_flaw_catalog_by_id()[vf_id].name
    return Action(
        f"Spend {name} xp",
        lambda: wf.spend_xp(
            saga,
            character,
            "virtue",
            later.virtue_targets(character, vf_id),
            note=vf_id,
            title=f"Spend {name} xp",
        ),
    )


def _later_life_actions(saga: Saga, record: Record) -> list[Action]:
    character = _character(record)
    actions = [
        _virtue_xp_action(saga, character, vf_id)
        for vf_id in access.virtue_xp(character)
    ]
    if later.free_scores_missing(character):
        actions.append(
            Action(
                "Record free Virtue scores", lambda: wf.record_free_scores(character)
            )
        )
    if packages.offered(saga, character):
        actions.append(
            Action("Take a training package", lambda: wf.training_package(character))
        )
    return actions


PANELS[("character", "later_life")] = Panel(
    _later_life_budget,
    _later_life_actions,
    xp_list(
        "later_life",
        lambda saga, c: later.later_life_targets(c),
        rows=_later_life_rows,
    ),
)


#: The spells' columns, under the xp rows.
SPELL_NAME = 38


def spell_rows(saga: Saga, character: Character, step: str, heading: str) -> list[Row]:
    """A heading, then the spells learned at `step`: each with its level
    and the magus's Lab Total for it; Delete forgets one."""
    found = cx.entries(character, step)
    rows = [Row(heading, heading=True, cells=[heading, "", "", "Level", "Lab Total"])]
    for entry in found:
        spell = spl.find_spell(saga, entry.target)

        def forget(entry: CreationXp = entry) -> Command:
            return wf.forget_spell(saga, character, entry)

        if spell is None:
            rows.append(
                Row(
                    f"{pad(entry.target, SPELL_NAME)} (missing)  level {entry.xp}",
                    delete=forget,
                    cells=[
                        f"{escape(entry.target)} (missing)",
                        "",
                        "",
                        str(entry.xp),
                        "",
                    ],
                )
            )
            continue
        cap = magus.spell_cap(saga, character, spell)
        over = " [$text-error](over its Lab Total)[/]" if entry.xp > cap else ""
        rows.append(
            Row(
                f"{pad(spell.name, SPELL_NAME)}{spl.shorthand(spell):<9}"
                f"level {entry.xp:>3}  Lab Total {cap}{over}",
                spl.detail_text(saga, spell)
                + f"\n\n[b]Learned at level:[/] {entry.xp}"
                + f"\n[b]{escape(character.name)}'s Lab Total for it (aura 3):[/] {cap}",
                delete=forget,
                cells=[
                    f"{escape(spell.name)} ({spl.shorthand(spell)})",
                    "",
                    "",
                    str(entry.xp),
                    f"{cap}{over}",
                ],
            )
        )
    if not found:
        empty = "[dim](no spells yet: Learn a spell)[/]"
        rows.append(Row(empty, heading=True, cells=[empty]))
    return rows


def _learn_spell(saga: Saga, record: Record, step: str) -> Action:
    return Action(
        "Learn a spell", lambda: wf.learn_spell(saga, _character(record), step)
    )


# -- Apprenticeship --


def _apprenticeship_budget(saga: Saga, record: Record) -> str:
    character = _character(record)
    budget = magus.xp_budget(character)
    spent = cx.spent(character, "apprenticeship")
    levels = magus.level_budget(character)
    learned = cx.spent(character, magus.SPELLS_STEP)
    return "\n".join(
        [
            f"Apprenticeship: {budget} xp for Arts and Abilities, "
            f"[b]{spent} spent, {budget - spent} left[/]",
            f"Spells: {levels} levels, {learned} learned (each at most its Lab "
            "Total with aura 3)",
        ]
    )


def _apprenticeship_rows(saga: Saga, record: Record) -> list[Row]:
    character = _character(record)
    return [
        *xp_rows(saga, character, "apprenticeship", magus.targets(character)),
        *spell_rows(saga, character, magus.SPELLS_STEP, "Spells"),
    ]


PANELS[("character", "apprenticeship")] = Panel(
    _apprenticeship_budget,
    lambda saga, record: [_learn_spell(saga, record, magus.SPELLS_STEP)],
    xp_list(
        "apprenticeship",
        lambda saga, c: magus.targets(c),
        rows=_apprenticeship_rows,
    ),
)


# -- Years past Gauntlet and pre-play aging --


def _aging_actions(saga: Saga, character: Character) -> list[Action]:
    """Roll pre-play aging (while due), and the Aging form for a
    Longevity Ritual."""
    actions = []
    if magus.aging_due(saga, character):
        actions.append(
            Action(
                "Roll pre-play aging", lambda: wf.roll_pre_play_aging(saga, character)
            )
        )
    if (cc.age(saga, character) or 0) > cc.aging_age(character):
        actions.append(
            Action(
                "Edit Aging (Longevity Ritual)",
                _description_edit(saga, character, "Aging"),
            )
        )
    return actions


def _gauntlet_budget(saga: Saga, record: Record) -> str:
    character = _character(record)
    conditions = character.creation_conditions
    years = magus.years_past_gauntlet(saga, character)
    points = magus.gauntlet_points(saga, character)
    spent = magus.gauntlet_spent(character)
    lines = [
        f"Gauntlet at {magus.gauntlet_age(character)}: {years} years past it, "
        f"{magus.POINTS_A_YEAR} points a year",
        f"Lab seasons: {conditions.lab_seasons} (cost "
        f"{magus.lab_season_cost(conditions.lab_seasons)} points)",
        f"Points: {points}, [b]{spent} spent, {points - spent} left[/] (1 xp or 1 "
        "spell level each)",
        f"Working conditions: aura {conditions.aura:+d}, lab quality "
        f"{conditions.lab_quality:+d}, Living Conditions "
        f"{conditions.living_conditions:+d}",
    ]
    due = magus.aging_due(saga, character)
    if due:
        lines.append(f"Pre-play aging: {due} roll(s) to make")
    return "\n".join(lines)


def _gauntlet_rows(saga: Saga, record: Record) -> list[Row]:
    character = _character(record)
    return [
        *xp_rows(saga, character, "gauntlet", magus.gauntlet_targets(character)),
        *spell_rows(saga, character, magus.GAUNTLET_SPELLS, "Spells"),
    ]


def _gauntlet_actions(saga: Saga, record: Record) -> list[Action]:
    character = _character(record)
    return [
        Action("Years and conditions", lambda: wf.gauntlet_conditions(character)),
        _learn_spell(saga, record, magus.GAUNTLET_SPELLS),
        *_aging_actions(saga, character),
    ]


PANELS[("character", "gauntlet")] = Panel(
    _gauntlet_budget,
    _gauntlet_actions,
    xp_list(
        "gauntlet",
        lambda saga, c: magus.gauntlet_targets(c),
        rows=_gauntlet_rows,
        add_label="Spend points on xp",
    ),
)


# -- Finishing Touches and the review --


def _finish_budget(saga: Saga, record: Record) -> str:
    character = _character(record)
    traits = ", ".join(
        f"{escape(t.name)} {t.score:+d}" for t in character.personality_traits
    )
    reputations = ", ".join(
        f"{escape(t.name)} {t.score:+d}" for t in character.reputations
    )
    b = character.background
    rows: list[tuple[str, object]] = [
        ("Personality Traits", traits or "(none)"),
        ("Reputations", reputations or "(none)"),
        ("Confidence", f"{b.confidence_score}, {b.confidence_points} points"),
    ]
    return "\n".join([aligned(rows), "Review:", *review_lines(saga, record)])


def _add_trait(traits: list[Any], section: str) -> Start:
    def start() -> Command:
        add = tf.trait_ops(traits, section).add
        assert add is not None
        return add()

    return start


def _finish_actions(saga: Saga, record: Record) -> list[Action]:
    character = _character(record)
    actions = [
        Action(
            "Add a Personality Trait",
            _add_trait(character.personality_traits, "section-personality-traits"),
        ),
        Action(
            "Add a Reputation",
            _add_trait(character.reputations, "section-reputations"),
        ),
        Action("Edit Confidence", lambda: cf.character_info_form(saga, character)),
    ]
    if character.type != "magus":
        actions += _aging_actions(saga, character)
    return actions


PANELS[("character", "finish")] = Panel(_finish_budget, _finish_actions)


# -- a covenant's Baseline: Power Level, Build Points, season, aura, income --


def _situation_name(covenant: Covenant) -> str:
    """The Covenant Situation its Boons and Hooks came from, if any."""
    used = cov_rules.situation_in_use(covenant)
    if used is None:
        return "(none)"
    found = next(
        (s for s in catalog.load_covenant_situation_catalog() if s.id == used[0]),
        None,
    )
    return escape(found.name) if found is not None else escape(used[0])


def _power_budget(saga: Saga, record: Record) -> str:
    covenant = _covenant(record)
    power = cov.POWER_BY_NAME.get(covenant.power_level)
    founded = covenant.year_founded
    boons = catalog.load_covenant_boon_hook_catalog_by_id()
    aura = cov_rules.covenant_effective_aura(covenant, boons)
    rows: list[tuple[str, object]] = [
        ("Power Level", covenant.power_level or "(not chosen)"),
        (
            "Year Founded",
            f"{founded} ({saga.current_year - founded} years ago)"
            if founded is not None
            else "(not set)",
        ),
        ("Season", covenant.covenant_season),
        ("Situation", _situation_name(covenant)),
        (
            "Base covenant",
            base.name
            if (base := templates.BASE_BY_KEY.get(covenant.base_covenant))
            else "(none)",
        ),
        ("Aura", f"{escape(covenant.aura_realm)} {aura}"),
    ]
    if power is not None:
        top = f"{power.most}" if power.most is not None else "no top"
        cap = power.max_level if power.max_level is not None else "none"
        budget = covenant.build_points_budget
        rows += [
            ("Range", f"{power.least} to {top} Build Points"),
            (
                "Build Points (storyguide)",
                budget if budget is not None else "(not set)",
            ),
            ("Highest text or effect level", cap),
            ("Magi without a laboratory", covenant.magi_without_lab),
        ]
    baseline = (
        "Free for every covenant: aura 3, one Typical source of income (or "
        "two Lesser), a standard laboratory per magus, about a grog and two "
        "covenfolk per magus."
    )
    return f"{aligned(rows)}\n{baseline}"


#: The income list's columns.
INCOME_NAME = 40
INCOME_HEADER = f"  {'Source of income':<{INCOME_NAME}}{'Type':<11}{'Pounds':>7}"
INCOME_COLUMNS = ["Source of income", "Type", "Pounds", "Hooks"]


def _income_pounds(source: IncomeSource) -> int:
    return (
        source.income
        if source.income is not None
        else INCOME_TYPE_DEFAULTS[source.type]
    )


def _remove_income(covenant: Covenant, source: IncomeSource) -> Start:
    sources = covenant.economics.income_sources

    def start() -> Command:
        return Confirm(
            f"Delete {escape(source.name or 'this source of income')}?",
            lambda: sources.remove(source),
        )

    return start


def _income_rows(saga: Saga, record: Record) -> list[Row]:
    """The covenant's sources of income: Edit changes one, Delete deletes
    it."""
    covenant = _covenant(record)
    rows = []
    for source in covenant.economics.income_sources:
        flags = [
            name
            for name, on in (
                ("Contested", source.contested),
                ("Dwindling", source.dwindling),
            )
            if on
        ]
        details = [
            f"[b]{escape(source.name or '(unnamed)')}[/]",
            f"[b]Type:[/] {source.type}    [b]Pounds a year:[/] {_income_pounds(source)}",
        ]
        if flags:
            details.append(f"[b]Hooks:[/] {', '.join(flags)}")
        if source.description:
            details += ["", escape(source.description)]
        rows.append(
            Row(
                f"{pad(source.name or '(unnamed)', INCOME_NAME)}{source.type:<11}"
                f"{_income_pounds(source):>7}"
                + (f"  [dim]{', '.join(flags)}[/]" if flags else ""),
                "\n".join(details),
                edit=lambda s=source: covf.income_form(covenant, s),
                delete=_remove_income(covenant, source),
                cells=[
                    escape(source.name or "(unnamed)"),
                    source.type,
                    str(_income_pounds(source)),
                    f"[dim]{', '.join(flags)}[/]" if flags else "",
                ],
            )
        )
    return rows


def _power_actions(saga: Saga, record: Record) -> list[Action]:
    covenant = _covenant(record)
    return [
        Action("Choose Power Level", lambda: wf.power_level(covenant)),
        Action("Edit covenant (season, aura)", lambda: covf.covenant_form(covenant)),
        Action("Set starting income", lambda: wf.starting_income(saga, covenant)),
        Action(
            "Use a Covenant Situation", lambda: wf.covenant_situation(saga, covenant)
        ),
        Action("Use a base covenant", lambda: wf.base_covenant(saga, covenant)),
    ]


PANELS[("covenant", "power")] = Panel(
    _power_budget,
    _power_actions,
    StepList(
        INCOME_HEADER,
        _income_rows,
        add=lambda saga, record: covf.income_form(_covenant(record), None),
        add_label="Add a source of income",
        delete_label="Delete",
        hint="Its sources of income: Set starting income makes them by the rules.",
        columns=INCOME_COLUMNS,
    ),
)


# -- a covenant's Resources: what the Build Points bought --


#: The Resources list's columns.
BP_NAME = 56
BP_HEADER = f"  {'What':<{BP_NAME}}{'Points':>7}"
BP_COLUMNS = ["What", "Points", "Note"]


def _bp_label(text: str, points: object, note: str = "") -> str:
    tail = f"  [dim]{escape(note)}[/]" if note else ""
    return f"{pad(text, BP_NAME)}{points!s:>7}{tail}"


def _bp_row(text: str, points: object, note: str = "", **verbs: Any) -> Row:
    """A Resources row: what was bought, its Build Points and a note."""
    return Row(
        _bp_label(text, points, note),
        cells=[escape(text), str(points), f"[dim]{escape(note)}[/]" if note else ""],
        **verbs,
    )


def tally(saga: Saga, covenant: Covenant) -> str:
    """Build Points by category, with how many things each bought."""
    found = cov.costs(saga, covenant)
    totals = cov.category_totals(found)
    rows = []
    for category in cov.CATEGORIES:
        lines = [c for c in found if c.category == category]
        if not lines:
            continue
        count = len({id(c.item) for c in lines if c.item is not None}) or len(lines)
        rows.append(f"  {category:<20}{totals.get(category, 0):>7}{count:>6}")
    if not rows:
        return (
            "  (nothing bought yet: Buy something adds a book, vis, an enchanted "
            "item or a specialist)"
        )
    return "\n".join([f"  {'Category':<20}{'Points':>7}{'Items':>6}", *rows])


def _build_points_budget(saga: Saga, record: Record) -> str:
    covenant = _covenant(record)
    spent = cov.spent(saga, covenant)
    budget = covenant.build_points_budget
    if budget is None:
        head = f"Build Points spent: {spent} (set the budget on the Baseline step)"
    else:
        head = f"Build Points: {budget}, [b]{spent} spent, {budget - spent} left[/]"
    lines = [head]
    base = templates.BASE_BY_KEY.get(covenant.base_covenant)
    if base is not None:
        lines.append(f"From the {base.name}:")
        lines += [
            f"  {a.what}: {a.chosen} of {a.levels} levels chosen"
            for a in templates.allowances(saga, covenant)
        ]
        books, vis = templates.placeholders(saga, covenant)
        if books or vis:
            lines.append(
                f"  Placeholders to fill in: {len(books)} book(s), {len(vis)} vis "
                "(Edit on the row)"
            )
    return "\n".join(lines) + f"\n\n{tally(saga, covenant)}"


def _possession_entry(
    saga: Saga, covenant: Covenant, possession: Possession
) -> pos.PossessionEntry | None:
    return next(
        (
            e
            for e in pos.entries_for_kind(
                saga,
                covenant,
                possession.kind,
                catalog.load_lab_virtue_flaw_catalog_by_id(),
            )
            if e.record is possession
        ),
        None,
    )


def _inhabitant_entry(
    saga: Saga, covenant: Covenant, person: Inhabitant
) -> inh.InhabitantEntry | None:
    return next(
        (
            e
            for e in inh.entries_for_kind(saga, covenant, person.kind)
            if e.record is person
        ),
        None,
    )


def _book_ops(saga: Saga, covenant: Covenant, book: Book) -> tuple[Start, Start]:
    owner = bk.owner_value("covenant", covenant.id)
    return (
        lambda: library_forms.book_form(saga, book, owner),
        lambda: library_forms.delete_book(saga, book),
    )


def _device_ops(saga: Saga, device: EnchantedDevice) -> tuple[Start, Start]:
    def replaced(edited: EnchantedDevice) -> None:
        devices = saga.enchanted_devices
        devices[devices.index(device)] = edited

    return (
        lambda: device_forms.device_form(saga, device, replaced),
        lambda: Confirm(
            device_forms.remove_question(device, None),
            lambda: device_forms.remove_target(saga, device, None),
        ),
    )


def _resource_ops(
    saga: Saga, covenant: Covenant, item: Any
) -> tuple[Start | None, Start | None]:
    """What Edit and Delete do to a priced record, by its type: the sheet's
    own form and delete for it. A laboratory is set up on its own
    worksheet."""
    if isinstance(item, Book):
        return _book_ops(saga, covenant, item)
    if isinstance(item, Possession):
        entry = _possession_entry(saga, covenant, item)
        if entry is None:
            return None, None
        return (
            lambda: posf.covenant_possession_form(saga, covenant, item.kind, entry),
            lambda: posf.remove_possession(covenant, item.kind, entry),
        )
    if isinstance(item, EnchantedDevice):
        return _device_ops(saga, item)
    if isinstance(item, Inhabitant):
        person = _inhabitant_entry(saga, covenant, item)
        if person is None:
            return None, None
        return (
            lambda: inhf.inhabitant_form(covenant, item.kind, person),
            lambda: inhf.remove_inhabitant(covenant, item.kind, person),
        )
    return None, None


def _cost_details(saga: Saga, cost: cov.Cost) -> str:
    item = cost.item
    if isinstance(item, Book):
        return bk.detail_text(saga, item)
    tail = (
        "Set it up on the laboratory's own worksheet."
        if isinstance(item, Laboratory)
        else "Edit changes it, Delete deletes it."
        if item is not None
        else "Bought as a pool of levels: each text is listed below it, where "
        "Edit changes it and Delete deletes it."
        if cost.category in cov.POOL_CATEGORIES
        else "Worked out from what the covenant has."
    )
    category = f" ({escape(cost.category)})" if cost.category else ""
    return (
        f"[b]{escape(cost.label)}[/]\n{cost.points} Build Points{category}\n\n"
        f"[dim]{tail}[/]"
    )


def _book_label(book: Book) -> str:
    name = book.name or "(untitled)"
    return name if name.startswith(book.type) else f"{book.type}: {name}"


def _pooled_text_row(saga: Saga, covenant: Covenant, book: Book) -> Row:
    """A Lab Text or Casting Tablet, under its pool's row: it has no Build
    Points of its own (the pool has them), but Edit and Delete act on
    it."""
    level = bk.level_of(book, saga)
    note = f"level {level}" if level else "set its level"
    edit, delete = _book_ops(saga, covenant, book)
    return _bp_row(
        f"  {_book_label(book)}",
        "",
        note,
        details=bk.detail_text(saga, book),
        edit=edit,
        delete=delete,
    )


def _build_points_rows(saga: Saga, record: Record) -> list[Row]:
    """Everything the Build Points bought, under its category, each with
    its points; a book with no level or Quality yet shows 0. Edit and
    Delete act on the record a row prices. Lab Texts and Casting Tablets
    are priced as a pool, so each text gets its own row under the pool's."""
    covenant = _covenant(record)
    found = cov.costs(saga, covenant)
    priced = {id(c.item) for c in found if c.item is not None}
    library = bk.books_owned_by(saga, "covenant", covenant.id)
    unpriced = [b for b in library if id(b) not in priced and not bk.pooled(b.type)]
    rows: list[Row] = []
    for category in (*cov.CATEGORIES, ""):
        lines = [c for c in found if c.category == category]
        texts = [b for b in library if cov.POOL_CATEGORIES.get(b.type) == category]
        if not lines and not texts:
            continue
        rows.append(Row(category or "Other", heading=True, cells=[category or "Other"]))
        for cost in lines:
            edit, delete = _resource_ops(saga, covenant, cost.item)
            rows.append(
                _bp_row(
                    cost.label,
                    cost.points,
                    details=_cost_details(saga, cost),
                    edit=edit,
                    delete=delete,
                )
            )
        rows += [_pooled_text_row(saga, covenant, book) for book in texts]
    if unpriced:
        rows.append(Row("Not priced yet", heading=True, cells=["Not priced yet"]))
        for book in unpriced:
            edit, delete = _book_ops(saga, covenant, book)
            rows.append(
                _bp_row(
                    _book_label(book),
                    0,
                    "set its level or Quality",
                    details=bk.detail_text(saga, book),
                    edit=edit,
                    delete=delete,
                )
            )
    return rows


SAGA_BOOK = "A book from the saga's books"


def resource_adds(saga: Saga, covenant: Covenant) -> list[tuple[str, Start]]:
    """What Build Points buy on the Resources step: (label, its first
    step); the saga's own books only while there are any."""
    owner = bk.owner_value("covenant", covenant.id)
    adds: list[tuple[str, Start]] = []
    if bk.unassigned_books(saga):
        adds.append((SAGA_BOOK, lambda: wf.saga_book(saga, covenant)))
    adds += [
        ("A new book", lambda: library_forms.book_form(saga, None, owner)),
        (
            "A vis source",
            lambda: posf.covenant_possession_form(saga, covenant, "vis_source", None),
        ),
        (
            "A vis stock",
            lambda: posf.covenant_possession_form(saga, covenant, "vis_store", None),
        ),
        (
            "An enchanted item",
            lambda: device_forms.device_form(
                saga,
                None,
                saga.enchanted_devices.append,
                holder=f"covenant:{covenant.id}",
            ),
        ),
        (
            "A specialist, craftsperson, teacher or guard",
            lambda: wf.buy_specialist(saga, covenant),
        ),
    ]
    return adds


def _buy_something(saga: Saga, record: Record) -> Choose:
    """Add on Resources: what to buy, then its form."""
    covenant = _covenant(record)
    return Choose(
        "Buy with Build Points",
        lambda: [
            Choice(escape(label), start)
            for label, start in resource_adds(saga, covenant)
        ],
        lambda start: start(),
    )


PANELS[("covenant", "build_points")] = Panel(
    _build_points_budget,
    list=StepList(
        BP_HEADER,
        _build_points_rows,
        add=_buy_something,
        add_label="Buy something",
        delete_label="Delete",
        hint="Choose a row to see what it is and what it costs.",
        columns=BP_COLUMNS,
    ),
)


# -- a covenant's Boons & Hooks --


def _boons_hooks_budget(saga: Saga, record: Record) -> str:
    covenant = _covenant(record)
    boons_catalog = catalog.load_covenant_boon_hook_catalog_by_id()
    boons = covenant_boon_points(covenant, boons_catalog)
    hooks = covenant_hook_points(covenant, boons_catalog)
    return aligned([("Boon points", f"{boons:g}"), ("Hook points", f"{hooks:g}")])


#: The Boons and Hooks list's columns.
BH_NAME = 56
BH_HEADER = f"  {'Boon or Hook':<{BH_NAME}}{'Points':>7}"
BH_COLUMNS = ["Boon or Hook", "Points", "Note"]


def _boons_hooks_rows(saga: Saga, record: Record) -> list[Row]:
    """The covenant's Boons, then its Hooks, each with its points and
    rules; a Resource Hook not yet tied to its source says so. Edit
    changes one (a Resource Hook also names its source), Delete removes
    it."""
    covenant = _covenant(record)
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    rows: list[Row] = []
    for kind, heading in (("Boon", "Boons"), ("Hook", "Hooks")):
        found = [
            (index, bh, by_id[bh.vf_id])
            for index, bh in enumerate(covenant.boons_hooks)
            if bh.vf_id in by_id and by_id[bh.vf_id].type == kind
        ]
        if not found:
            continue
        rows.append(Row(heading, heading=True, cells=[heading]))
        for index, bh, definition in found:
            points = boon_hook_points(bh, definition)
            name = catalog.describe_boon_hook(bh, by_id)
            label = f"{pad(name, BH_NAME)}{points:>7g}"
            note = ""
            details = boon_hook_info_text(covenant, index)
            if bh.vf_id in cov_rules.RESOURCE_HOOKS:
                source = cov_rules.linked_source(covenant, bh)
                if source is None:
                    note = "[$text-warning]needs its source[/]"
                    label += f"  {note}"
                    about = (
                        "(not yet: Edit names it, once the vis or income source exists)"
                    )
                else:
                    about = escape(source.name or "unnamed")
                details = f"[b]About:[/] {about}\n{details}"
            rows.append(
                Row(
                    label,
                    details,
                    edit=lambda i=index: covf.edit_boon_hook(covenant, i),
                    delete=lambda i=index: covf.remove_boon_hook(covenant, i),
                    cells=[escape(name), f"{points:g}", note],
                )
            )
    return rows


PANELS[("covenant", "boons_hooks")] = Panel(
    _boons_hooks_budget,
    lambda saga, record: [
        Action(
            "Add a Hook", lambda: covf.add_boon_hook(saga, _covenant(record), "Hook")
        )
    ],
    StepList(
        BH_HEADER,
        _boons_hooks_rows,
        add=lambda saga, record: covf.add_boon_hook(saga, _covenant(record), "Boon"),
        add_label="Add a Boon",
        delete_label="Remove",
        hint="Choose a Boon or Hook to read its rules.",
        columns=BH_COLUMNS,
    ),
)


def _review_budget(saga: Saga, record: Record) -> str:
    lines = ["Review:", *review_lines(saga, record)]
    if isinstance(record, Covenant):
        lines += ["", "Build Points:", tally(saga, record)]
        lines += ["", f"[dim]{escape(cov.baseline_covenfolk_note(saga, record))}[/]"]
    return "\n".join(lines)


PANELS[("covenant", "finish")] = Panel(_review_budget)


# -- a New Laboratory --


def _setup_budget(saga: Saga, record: Record) -> str:
    lab = _laboratory(record)
    owner = saga.character(lab.owner_id)
    c = lab.characteristics
    rows: list[tuple[str, object]] = [
        ("Owner (builder)", escape(owner.name) if owner else "(none)"),
        ("Size", f"{c.size:+d}"),
        ("Refinement", f"{c.refinement:+d}"),
        ("Starting laboratory", "yes" if lab.starting else "no"),
    ]
    if lab.starting:
        rows.append(("Build Points", cov.lab_points(lab)))
    return aligned(rows)


def toggle_starting(lab: Laboratory) -> Act:
    """Whether the lab is one of its covenant's starting labs (paid for
    from the covenant's Build Points)."""

    def apply() -> None:
        lab.starting = not lab.starting

    return Act(apply)


def _setup_actions(saga: Saga, record: Record) -> list[Action]:
    lab = _laboratory(record)
    return [
        Action("Edit identity (owner)", lambda: labf.identity_form(saga, lab)),
        Action("Edit Characteristics", lambda: labf.characteristics_form(lab)),
        Action("Starting lab: yes/no", lambda: toggle_starting(lab)),
    ]


def _lab_virtue_rows(saga: Saga, record: Record) -> list[Row]:
    """The laboratory's Virtues, then its Flaws, each with its rules;
    Delete removes one."""
    lab = _laboratory(record)
    by_id = catalog.load_lab_virtue_flaw_catalog_by_id()
    rows: list[Row] = []
    for side, heading in (("Virtue", "Virtues"), ("Flaw", "Flaws")):
        taken = [
            (index, instance, definition)
            for index, instance in enumerate(lab.virtues_flaws)
            if (definition := by_id.get(instance.vf_id)) is not None
            and definition.type == side
        ]
        if not taken:
            continue
        rows.append(Row(heading, heading=True, cells=[heading]))
        for index, instance, definition in taken:
            name = catalog.describe_virtue_flaw(instance, by_id)
            rows.append(
                Row(
                    f"{pad(name, VF_NAME)}"
                    f"{definition.tier:<{VF_TIER}}{escape(definition.category)}",
                    lab_rules.vf_info_text(lab, index),
                    delete=_remove_virtue_flaw(saga, lab, instance),
                    cells=[escape(name), definition.tier, escape(definition.category)],
                )
            )
    return rows


PANELS[("laboratory", "setup")] = Panel(
    _setup_budget,
    _setup_actions,
    StepList(
        VF_HEADER,
        _lab_virtue_rows,
        columns=VF_COLUMNS,
        add=lambda saga, record: _add_virtue_flaw(saga, record, None),
        add_label="Add a Virtue or Flaw",
        edit_label=None,
        delete_label="Remove",
        hint="Choose a Virtue or Flaw to read its rules.",
    ),
)
PANELS[("laboratory", "finish")] = Panel(_review_budget)

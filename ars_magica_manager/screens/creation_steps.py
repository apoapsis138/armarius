"""The Creation Worksheet's step panels: each step's
budget text and buttons, registered in creation_worksheet.PANELS. The
buttons open the sheet's own dialogs through the workspace, so a step edits
the record the same way the sheet does."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from functools import partial
from typing import TYPE_CHECKING

from .. import catalog, creation, sourcebooks
from .. import sheet_text as st
from .. import spells as spl
from ..arts import ART_DESCRIPTIONS, ARTS
from ..markup import aligned, escape
from ..models import (
    ArtScore,
    Character,
    CreationXp,
    Saga,
    VirtueFlawInstance,
)
from ..rules import creation as rules
from ..rules import creation_access as access
from ..rules import creation_character as cc
from ..rules import creation_characteristics as cch
from ..rules import creation_later as later
from ..rules import creation_magus as magus
from ..rules import creation_packages as packages
from ..rules import creation_virtues as cv
from ..rules import creation_xp as cx
from ..rules import scores
from ..rules import xp as xp_rules
from .creation_worksheet import (
    PANELS,
    Record,
    StepAction,
    StepList,
    StepPanel,
    StepRow,
)
from .pickers import RemovalPickerScreen

if TYPE_CHECKING:
    from .workspace.screen import WorkspaceScreen


def _character(record: Record) -> Character:
    assert isinstance(record, Character)
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


def _add_type_virtues(workspace: WorkspaceScreen, record: Record) -> None:
    character = _character(record)
    for vf_id in cc.missing_type_virtues(character):
        character.virtues_flaws.append(VirtueFlawInstance(vf_id))
    workspace._commit("section-vf-virtues", "section-vf-flaws")


def _choose_mythic_status(workspace: WorkspaceScreen, record: Record) -> None:
    """Pick the character's one Mythic Companion status Virtue (from the
    books in play), replacing any other."""
    character = _character(record)
    books = sourcebooks.saga_books(workspace.saga)
    statuses = sorted(
        (
            entry
            for entry in catalog.load_virtue_flaw_catalog()
            if entry.id in cc.mythic_status_ids()
            and sourcebooks.in_play(entry.source, books)
        ),
        key=lambda entry: entry.name,
    )

    def handle_index(index: int | None) -> None:
        if index is None:
            return
        chosen = cc.mythic_status_ids()
        character.virtues_flaws = [
            vf for vf in character.virtues_flaws if vf.vf_id not in chosen
        ]
        character.virtues_flaws.append(VirtueFlawInstance(statuses[index].id))
        workspace._commit("section-vf-virtues", "section-vf-flaws")

    workspace.app.push_screen(
        RemovalPickerScreen(
            "Choose the Mythic Companion status Virtue",
            [escape(entry.name) for entry in statuses],
        ),
        handle_index,
    )


def _house_virtue_name(option: dict) -> str:
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    return catalog.describe_virtue_flaw(
        VirtueFlawInstance(option["vf_id"], dict(option.get("params") or {})), by_id
    )


def _add_house_virtue(workspace: WorkspaceScreen, record: Record) -> None:
    """Add the House's free Virtue; a House with a choice asks which."""
    character = _character(record)
    house = catalog.load_house_catalog_by_id().get(character.hermetic.house or "")
    if house is None or not house.virtues:
        return

    def add(index: int | None) -> None:
        if index is None:
            return
        option = house.virtues[index]
        character.virtues_flaws.append(
            VirtueFlawInstance(option["vf_id"], dict(option.get("params") or {}))
        )
        workspace._commit("section-vf-virtues", "section-vf-flaws")

    if len(house.virtues) == 1:
        add(0)
        return
    workspace.app.push_screen(
        RemovalPickerScreen(
            f"House {escape(house.name)}'s free Virtue",
            [escape(_house_virtue_name(o)) for o in house.virtues],
        ),
        add,
    )


def _concept_actions(saga: Saga, record: Record) -> list[StepAction]:
    character = _character(record)
    actions = [
        StepAction("Edit type", lambda ws, r: ws._edit_character_info()),
        StepAction("Edit Year Born", lambda ws, r: ws._edit_biographical_detail()),
    ]
    if character.type == "magus":
        actions.append(
            StepAction("Edit House", lambda ws, r: ws._edit_hermetic_background())
        )
        missing = cc.missing_type_virtues(character)
        if missing:
            by_id = catalog.load_virtue_flaw_catalog_by_id()
            names = " and ".join(by_id[vf_id].name for vf_id in missing)
            actions.append(StepAction(f"Add {names}", _add_type_virtues))
        house = catalog.load_house_catalog_by_id().get(character.hermetic.house or "")
        if (
            house is not None
            and house.virtues
            and not any(cv.held_option(character, o) for o in house.virtues)
        ):
            actions.append(StepAction("Add the House Virtue", _add_house_virtue))
    if character.type == "mythic companion":
        actions.append(StepAction("Choose status Virtue", _choose_mythic_status))
    return actions


PANELS[("character", "concept")] = StepPanel(_concept_budget, _concept_actions)


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
_VF_NAME = 44
_VF_TIER = 8
VF_HEADER = f"  {'Virtue or Flaw':<{_VF_NAME}}{'Tier':<{_VF_TIER}}Type"


def _virtue_rows(saga: Saga, record: Record) -> list[StepRow]:
    """The character's Virtues, then its Flaws, each with its book text."""
    character = _character(record)
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    rows: list[StepRow] = []
    for side, heading in (("Virtue", "Virtues"), ("Flaw", "Flaws")):
        taken = [
            (index, vf, definition)
            for index, vf in enumerate(character.virtues_flaws)
            if (definition := by_id.get(vf.vf_id)) is not None
            and definition.side == side
        ]
        if not taken:
            continue
        rows.append(StepRow(heading, heading=True))
        for index, vf, definition in taken:
            name = catalog.describe_virtue_flaw(vf, by_id)
            rows.append(
                StepRow(
                    f"{pad(name, _VF_NAME)}{definition.tier:<{_VF_TIER}}"
                    f"{escape(definition.category_label)}",
                    st.vf_info_text(character.virtues_flaws, index),
                    delete=partial(_remove_virtue_flaw, character, vf),
                )
            )
    return rows


def _remove_virtue_flaw(
    character: Character, vf: VirtueFlawInstance, workspace: WorkspaceScreen
) -> None:
    if vf in character.virtues_flaws:
        workspace._remove_virtue_flaw_from(character, character.virtues_flaws.index(vf))


def _virtues_actions(saga: Saga, record: Record) -> list[StepAction]:
    character = _character(record)
    return [
        StepAction(
            "Add a Flaw", lambda ws, r: ws._add_virtue_flaw_to(character, "Flaw")
        ),
    ]


PANELS[("character", "virtues_flaws")] = StepPanel(
    _virtues_budget,
    _virtues_actions,
    StepList(
        VF_HEADER,
        _virtue_rows,
        add=lambda ws, r: ws._add_virtue_flaw_to(_character(r)),
        add_label="Add a Virtue (F2 in the picker: Flaws)",
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


def _fill_grog_array(workspace: WorkspaceScreen, record: Record) -> None:
    """Set the Characteristics from one of the Grogs book's arrays, in
    order; the user then moves the scores where they belong."""
    character = _character(record)

    def handle_index(index: int | None) -> None:
        if index is None:
            return
        for (key, _), score in zip(
            cch.CHARACTERISTICS, cch.GROG_ARRAYS[index], strict=True
        ):
            setattr(character.characteristics, key, score)
        workspace._commit("section-char-characteristics")

    workspace.app.push_screen(
        RemovalPickerScreen(
            "Fill from a Grogs array (Int, Per, Str, Sta, Pre, Com, Dex, Qik)",
            [" ".join(f"{n:+d}" for n in array) for array in cch.GROG_ARRAYS],
        ),
        handle_index,
    )


def _characteristics_actions(saga: Saga, record: Record) -> list[StepAction]:
    character = _character(record)
    actions = [
        StepAction("Edit Characteristics", lambda ws, r: ws._edit_characteristics())
    ]
    if cch.grog_arrays_offered(saga, character):
        actions.append(StepAction("Fill from a Grogs array", _fill_grog_array))
    return actions


PANELS[("character", "characteristics")] = StepPanel(
    _characteristics_budget, _characteristics_actions
)


# -- the xp steps --


def pad(text: str, width: int) -> str:
    """`text` escaped for markup and padded to `width` columns (cut with an
    ellipsis if it's longer), counting the text as shown."""
    if len(text) >= width:
        text = text[: width - 2] + "…"
    return escape(text) + " " * (width - len(text))


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
_XP_NAME = 30
XP_HEADER = (
    f"  {'Ability or Art':<{_XP_NAME}}{'Spent':>6}{'Gained':>8}{'Score':>7}   Specialty"
)


def _target_score(character: Character, target: str) -> tuple[xp_rules.Progress, str]:
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
    progress, specialty = _target_score(character, entry.target)
    gained = creation.gained_xp(entry)
    gained_text = f"{gained:>8}"
    if gained != entry.xp:
        gained_text = f"[$text-success]{gained_text}[/]"
    return (
        f"{pad(entry.target + suffix, _XP_NAME)}{entry.xp:>6}{gained_text}"
        f"{progress.score:>7}   {escape(specialty)}"
    )


def xp_details(saga: Saga, character: Character, target: str) -> str:
    """The details of an Art or Ability xp was spent on: its score and xp,
    any Affinity and the creation cap, every worksheet spend on it, and
    what it is."""
    progress, _ = _target_score(character, target)
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
) -> StepRow:
    """A row for an xp spend: e changes it (with `targets` to choose from;
    None: it can't be changed, only taken back), d takes it back."""
    return StepRow(
        xp_label(character, entry),
        xp_details(saga, character, entry.target),
        edit=(
            None
            if targets is None
            else lambda ws: ws._change_creation_entry(character, entry, targets)
        ),
        delete=lambda ws: ws._refund_creation_entry(character, entry),
    )


def xp_rows(
    saga: Saga, character: Character, step: str, targets: Sequence[str]
) -> list[StepRow]:
    return [xp_row(saga, character, x, targets) for x in cx.entries(character, step)]


def xp_list(
    step: str,
    targets: Callable[[Saga, Character], Sequence[str]],
    rows: Callable[[Saga, Record], list[StepRow]] | None = None,
    add_label: str = "Spend xp",
) -> StepList:
    """An xp step's list: a spends the step's pool xp, e changes the chosen
    spend, d takes it back."""
    return StepList(
        XP_HEADER,
        rows
        or (
            lambda saga, record: xp_rows(
                saga, _character(record), step, targets(saga, _character(record))
            )
        ),
        add=lambda ws, record: ws._spend_creation_xp(
            _character(record), step, targets(ws.saga, _character(record))
        ),
        add_label=add_label,
        edit_label="Change its xp",
        delete_label="Take it back",
        hint="Choose a row to see what the xp bought.",
    )


# -- Early Childhood --


def _childhood_budget(saga: Saga, record: Record) -> str:
    character = _character(record)
    native = next(
        (x for x in cx.entries(character, "childhood") if x.note == cx.NATIVE),
        None,
    )
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


def _childhood_rows(saga: Saga, record: Record) -> list[StepRow]:
    """The childhood's spends; the Native Language's row changes the
    language."""
    character = _character(record)
    targets = cx.childhood_targets()
    rows = []
    for entry in cx.entries(character, "childhood"):
        row = xp_row(saga, character, entry, targets)
        if entry.note == cx.NATIVE:
            row.label = xp_label(character, entry, " (native)")
            row.edit = lambda ws: ws._set_native_language(character)
        rows.append(row)
    return rows


def _childhood_actions(saga: Saga, record: Record) -> list[StepAction]:
    character = _character(record)
    return [
        StepAction("Native Language", lambda ws, r: ws._set_native_language(character)),
        StepAction(
            "Use a sample childhood",
            lambda ws, r: ws._apply_sample_childhood(character),
        ),
    ]


PANELS[("character", "childhood")] = StepPanel(
    _childhood_budget,
    _childhood_actions,
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


def _later_life_rows(saga: Saga, record: Record) -> list[StepRow]:
    """Later Life's own spends, then each training package, each Virtue's
    own xp and the free Virtue scores, under headings."""
    character = _character(record)
    rows = xp_rows(saga, character, "later_life", later.later_life_targets(character))
    for taken in packages.taken(character):
        rows.append(
            StepRow(
                f"Training package: {escape(taken.name)} ({taken.years} years)",
                heading=True,
            )
        )
        for entry in cx.entries(character, "package"):
            if entry.note == taken.note:
                row = xp_row(saga, character, entry, None)
                row.delete = partial(_drop_package, character, taken.note)
                rows.append(row)
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    for vf_id in access.virtue_xp(character):
        own = [x for x in cx.entries(character, "virtue") if x.note == vf_id]
        if own:
            rows.append(StepRow(f"{escape(by_id[vf_id].name)} xp", heading=True))
            targets = later.virtue_targets(character, vf_id)
            rows += [xp_row(saga, character, x, targets) for x in own]
    free = cx.entries(character, "free")
    if free:
        rows.append(StepRow("Free Virtue scores", heading=True))
        rows += [xp_row(saga, character, x, None) for x in free]
    return rows


def _drop_package(character: Character, note: str, workspace: WorkspaceScreen) -> None:
    workspace._drop_training_package(character, note)


def _later_life_actions(saga: Saga, record: Record) -> list[StepAction]:
    character = _character(record)
    actions = []
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    for vf_id in access.virtue_xp(character):
        name = by_id[vf_id].name
        actions.append(
            StepAction(
                f"Spend {name} xp",
                lambda ws, r, v=vf_id, n=name: ws._spend_creation_xp(
                    character,
                    "virtue",
                    later.virtue_targets(character, v),
                    note=v,
                    title=f"Spend {n} xp",
                ),
            )
        )
    if later.free_scores_missing(character):
        actions.append(
            StepAction(
                "Record free Virtue scores",
                lambda ws, r: ws._record_free_scores(character),
            )
        )
    if packages.offered(saga, character):
        actions.append(
            StepAction(
                "Take a training package",
                lambda ws, r: ws._take_training_package(character),
            )
        )
    return actions


PANELS[("character", "later_life")] = StepPanel(
    _later_life_budget,
    _later_life_actions,
    xp_list(
        "later_life",
        lambda saga, c: later.later_life_targets(c),
        rows=_later_life_rows,
    ),
)


#: The spells' columns, under the xp rows.
_SPELL_NAME = 38


def spell_rows(
    saga: Saga, character: Character, step: str, title: str
) -> list[StepRow]:
    """A heading, then the spells learned at `step`: each with its level
    and the magus's Lab Total for it; d forgets one."""
    found = cx.entries(character, step)
    rows = [StepRow(title, heading=True)]
    for entry in found:
        spell = spl.find_spell(saga, entry.target)
        forget = partial(_forget_spell, character, entry)
        if spell is None:
            rows.append(
                StepRow(
                    f"{pad(entry.target, _SPELL_NAME)} (missing)  level {entry.xp}",
                    delete=forget,
                )
            )
            continue
        cap = magus.spell_cap(saga, character, spell)
        over = " [$text-error](over its Lab Total)[/]" if entry.xp > cap else ""
        rows.append(
            StepRow(
                f"{pad(spell.name, _SPELL_NAME)}{spl.shorthand(spell):<9}"
                f"level {entry.xp:>3}  Lab Total {cap}{over}",
                spl.detail_text(saga, spell)
                + f"\n\n[b]Learned at level:[/] {entry.xp}"
                + f"\n[b]{escape(character.name)}'s Lab Total for it (aura 3):[/] {cap}",
                delete=forget,
            )
        )
    if not found:
        rows.append(StepRow("[dim](no spells yet: Learn a spell)[/]", heading=True))
    return rows


def _forget_spell(
    character: Character, entry: CreationXp, workspace: WorkspaceScreen
) -> None:
    workspace._forget_creation_spell(character, entry)


def _learn_spell(step: str) -> StepAction:
    return StepAction(
        "Learn a spell",
        lambda ws, r: ws._learn_creation_spell(_character(r), step),
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


def _apprenticeship_rows(saga: Saga, record: Record) -> list[StepRow]:
    character = _character(record)
    return [
        *xp_rows(saga, character, "apprenticeship", magus.targets(character)),
        *spell_rows(saga, character, magus.SPELLS_STEP, "Spells"),
    ]


PANELS[("character", "apprenticeship")] = StepPanel(
    _apprenticeship_budget,
    lambda saga, record: [_learn_spell(magus.SPELLS_STEP)],
    xp_list(
        "apprenticeship",
        lambda saga, c: magus.targets(c),
        rows=_apprenticeship_rows,
    ),
)


# -- Years past Gauntlet and pre-play aging --


def _aging_actions(saga: Saga, character: Character) -> list[StepAction]:
    """Roll pre-play aging (while due), and the Aging dialog for a
    Longevity Ritual."""
    actions = []
    if magus.aging_due(saga, character):
        actions.append(
            StepAction(
                "Roll pre-play aging",
                lambda ws, r: ws._roll_pre_play_aging(character),
            )
        )
    if (cc.age(saga, character) or 0) > cc.aging_age(character):
        actions.append(
            StepAction("Edit Aging (Longevity Ritual)", lambda ws, r: ws._edit_aging())
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


def _gauntlet_rows(saga: Saga, record: Record) -> list[StepRow]:
    character = _character(record)
    return [
        *xp_rows(saga, character, "gauntlet", magus.gauntlet_targets(character)),
        *spell_rows(saga, character, magus.GAUNTLET_SPELLS, "Spells"),
    ]


def _gauntlet_actions(saga: Saga, record: Record) -> list[StepAction]:
    character = _character(record)
    return [
        StepAction(
            "Years and conditions",
            lambda ws, r: ws._edit_gauntlet_conditions(character),
        ),
        _learn_spell(magus.GAUNTLET_SPELLS),
        *_aging_actions(saga, character),
    ]


PANELS[("character", "gauntlet")] = StepPanel(
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


def review_lines(saga: Saga, record: Record) -> list[str]:
    """Each step with its open checks: "Concept: 1 warning"."""
    lines = []
    for step in rules.steps_for(record):
        found = rules.checks(saga, record, step.key)
        open_checks = [c for c in found if c.status != "pass"]
        if open_checks:
            lines.append(f"  {step.title}: {rules.summary(open_checks)}")
    return lines or ["  every check passes"]


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


def _finish_actions(saga: Saga, record: Record) -> list[StepAction]:
    character = _character(record)
    actions = [
        StepAction("Add a Personality Trait", lambda ws, r: ws._add_character_trait()),
        StepAction("Add a Reputation", lambda ws, r: ws._add_character_reputation()),
        StepAction("Edit Confidence", lambda ws, r: ws._edit_character_info()),
    ]
    if character.type != "magus":
        actions += _aging_actions(saga, character)
    return actions


PANELS[("character", "finish")] = StepPanel(_finish_budget, _finish_actions)

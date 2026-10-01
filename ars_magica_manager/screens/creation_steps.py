"""The Creation Worksheet's step panels (STORY-1303 to 1313): each step's
budget text and buttons, registered in creation_worksheet.PANELS. The
buttons open the sheet's own dialogs through the workspace, so a step edits
the record the same way the sheet does."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .. import catalog, sourcebooks
from .. import spells as spl
from ..covenants import covenant_boon_points, covenant_hook_points
from ..markup import aligned, escape
from ..models import Character, Covenant, Laboratory, Saga, VirtueFlawInstance
from ..rules import creation as rules
from ..rules import creation_access as access
from ..rules import creation_character as cc
from ..rules import creation_characteristics as cch
from ..rules import creation_covenant as cov
from ..rules import creation_later as later
from ..rules import creation_magus as magus
from ..rules import creation_packages as packages
from ..rules import creation_virtues as cv
from ..rules import creation_xp as cx
from .creation_worksheet import PANELS, Record, StepAction, StepPanel
from .pickers import RemovalPickerScreen

if TYPE_CHECKING:
    from .workspace.screen import WorkspaceScreen


def _character(record: Record) -> Character:
    assert isinstance(record, Character)
    return record


# -- Concept: type, House and age (STORY-1303) --


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


# -- Virtues and Flaws (STORY-1304) --


def _virtues_budget(saga: Saga, record: Record) -> str:
    character = _character(record)
    t = cv.tally(character)
    fewest, most = cv.virtue_allowance(character, t.flaw_points)
    allowed = f"{most}" if fewest == most else f"{fewest}-{most}"
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    taken = [catalog.describe_virtue_flaw(vf, by_id) for vf in character.virtues_flaws]
    rows: list[tuple[str, object]] = [
        ("Virtue points", f"{t.virtue_points} (allowed {allowed})"),
        (
            "Flaw points",
            f"{t.flaw_points} of {cv.max_flaw_points(character)}, "
            f"{t.minor_flaws} of {cv.max_minor_flaws(character)} Minor Flaws",
        ),
        ("Taken", escape(", ".join(taken)) if taken else "(none)"),
    ]
    house = cv.house_benefit(character)
    if house.held:
        rows.append(("Free from the House", escape(", ".join(house.held))))
    if house.missing:
        rows.append(("House still gives", escape("; ".join(house.missing))))
    return aligned(rows)


def _virtues_actions(saga: Saga, record: Record) -> list[StepAction]:
    character = _character(record)
    actions = [
        StepAction("Add a Virtue", lambda ws, r: ws._add_virtue_flaw_to(character)),
        StepAction(
            "Add a Flaw", lambda ws, r: ws._add_virtue_flaw_to(character, "Flaw")
        ),
    ]
    if character.virtues_flaws:
        actions.append(
            StepAction(
                "Remove one", lambda ws, r: ws._remove_virtue_flaw_from(character)
            )
        )
    return actions


PANELS[("character", "virtues_flaws")] = StepPanel(_virtues_budget, _virtues_actions)


# -- Characteristics (STORY-1305) --


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


# -- the xp steps (STORY-1306 to 1310) --


def xp_lines(character: Character, step: str) -> str:
    """What a step's xp went on, one line each."""
    found = cx.entries(character, step)
    if not found:
        return "  (nothing spent yet)"
    return "\n".join(f"  {escape(x.target)}: {x.xp} xp" for x in found)


# -- Early Childhood (STORY-1306) --


def _childhood_budget(saga: Saga, record: Record) -> str:
    character = _character(record)
    native = next(
        (x for x in cx.entries(character, "childhood") if x.note == cx.NATIVE),
        None,
    )
    others = cx.spent(character, "childhood") - (native.xp if native else 0)
    head = aligned(
        [
            (
                "Native Language",
                f"{escape(native.target)} ({native.xp} xp)" if native else "(not set)",
            ),
            ("Other childhood xp", f"{others} of {cx.CHILDHOOD_XP}"),
        ]
    )
    return f"{head}\n{xp_lines(character, 'childhood')}"


def _childhood_actions(saga: Saga, record: Record) -> list[StepAction]:
    character = _character(record)
    targets = cx.childhood_targets()
    actions = [
        StepAction("Native Language", lambda ws, r: ws._set_native_language(character)),
        StepAction(
            "Spend xp",
            lambda ws, r: ws._spend_creation_xp(character, "childhood", targets),
        ),
        StepAction(
            "Use a sample childhood",
            lambda ws, r: ws._apply_sample_childhood(character),
        ),
    ]
    if any(x.note != cx.NATIVE for x in cx.entries(character, "childhood")):
        actions += [
            StepAction(
                "Change one",
                lambda ws, r: ws._change_creation_xp(
                    character, "childhood", targets, note=""
                ),
            ),
            StepAction(
                "Take back one",
                lambda ws, r: ws._refund_creation_xp(character, "childhood", note=""),
            ),
        ]
    return actions


PANELS[("character", "childhood")] = StepPanel(_childhood_budget, _childhood_actions)


def _change_and_take_back(
    character: Character, step: str, targets: list[str], what: str = "one"
) -> list[StepAction]:
    """The Change / Take back buttons, once a step has xp spent."""
    if not cx.entries(character, step):
        return []
    return [
        StepAction(
            f"Change {what}",
            lambda ws, r: ws._change_creation_xp(character, step, targets),
        ),
        StepAction(
            f"Take back {what}",
            lambda ws, r: ws._refund_creation_xp(character, step),
        ),
    ]


# -- Later Life (STORY-1307) --


def _later_life_budget(saga: Saga, record: Record) -> str:
    character = _character(record)
    years = later.bought_years(saga, character)
    ends = later.later_life_ends(saga, character)
    until = "apprenticeship" if character.type == "magus" else "now"
    lines = [
        f"Later Life: age 5 to {ends if ends is not None else '?'} ({until}), "
        f"{years} years at {later.xp_a_year(character)} xp = "
        f"{later.later_life_budget(saga, character)} xp, "
        f"{cx.spent(character, 'later_life')} spent",
        xp_lines(character, "later_life"),
    ]
    for taken in packages.taken(character):
        lines.append(f"Package: {escape(taken.name)} ({taken.years} years)")
        lines += [
            f"  {escape(x.target)}: {x.xp} xp"
            for x in cx.entries(character, "package")
            if x.note == taken.note
        ]
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    for vf_id, rule in access.virtue_xp(character).items():
        own = [x for x in cx.entries(character, "virtue") if x.note == vf_id]
        lines.append(
            f"{escape(by_id[vf_id].name)}: {rule.xp} xp, {sum(x.xp for x in own)} spent"
        )
        lines += [f"  {escape(x.target)}: {x.xp} xp" for x in own]
    free = cx.entries(character, "free")
    if free or later.free_score_abilities(character):
        lines.append("Free Virtue scores:")
        lines.append(xp_lines(character, "free"))
    cap = access.ability_cap(cc.age(saga, character))
    lines.append(f"Ability cap at this age: {cap}")
    return "\n".join(lines)


def _later_life_actions(saga: Saga, record: Record) -> list[StepAction]:
    character = _character(record)
    targets = later.later_life_targets(character)
    actions = [
        StepAction(
            "Spend xp",
            lambda ws, r: ws._spend_creation_xp(character, "later_life", targets),
        ),
        *_change_and_take_back(character, "later_life", targets),
    ]
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
    if cx.entries(character, "virtue"):
        every = sorted(
            {
                t
                for v in access.virtue_xp(character)
                for t in later.virtue_targets(character, v)
            }
        )
        actions += _change_and_take_back(character, "virtue", every, "Virtue xp")
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
    if packages.taken(character):
        actions.append(
            StepAction(
                "Drop a package", lambda ws, r: ws._drop_training_package(character)
            )
        )
    return actions


PANELS[("character", "later_life")] = StepPanel(_later_life_budget, _later_life_actions)


def spell_lines(saga: Saga, character: Character, step: str) -> str:
    """The spells learned at a step, each with its creation cap."""
    found = cx.entries(character, step)
    if not found:
        return "  (no spells yet)"
    lines = []
    for entry in found:
        spell = spl.find_spell(saga, entry.target)
        if spell is None:
            lines.append(f"  {escape(entry.target)} (missing), level {entry.xp}")
            continue
        cap = magus.spell_cap(saga, character, spell)
        rdt = ", ".join(
            f"{label} {escape(value)}"
            for label, value in (
                ("R:", spell.range),
                ("D:", spell.duration),
                ("T:", spell.target),
            )
            if value
        )
        lines.append(
            f"  {escape(spell.name)} ({spl.shorthand(spell)}), level {entry.xp}, "
            f"Lab Total {cap}" + (f"\n      {rdt}" if rdt else "")
        )
    return "\n".join(lines)


def _spell_actions(character: Character, step: str) -> list[StepAction]:
    actions = [
        StepAction(
            "Learn a spell", lambda ws, r: ws._learn_creation_spell(character, step)
        )
    ]
    if cx.entries(character, step):
        actions += [
            StepAction(
                "Spell details",
                lambda ws, r: ws._show_creation_spell(character, step),
            ),
            StepAction(
                "Forget a spell",
                lambda ws, r: ws._forget_creation_spell(character, step),
            ),
        ]
    return actions


# -- Apprenticeship (STORY-1309) --


def _apprenticeship_budget(saga: Saga, record: Record) -> str:
    character = _character(record)
    return "\n".join(
        [
            f"Apprenticeship: {magus.xp_budget(character)} xp for Arts and "
            f"Abilities, {cx.spent(character, 'apprenticeship')} spent",
            xp_lines(character, "apprenticeship"),
            f"Spells: {magus.level_budget(character)} levels, "
            f"{cx.spent(character, magus.SPELLS_STEP)} learned (each at most "
            "its Lab Total with aura 3)",
            spell_lines(saga, character, magus.SPELLS_STEP),
        ]
    )


def _apprenticeship_actions(saga: Saga, record: Record) -> list[StepAction]:
    character = _character(record)
    targets = magus.targets(character)
    return [
        StepAction(
            "Spend xp",
            lambda ws, r: ws._spend_creation_xp(character, "apprenticeship", targets),
        ),
        *_change_and_take_back(character, "apprenticeship", targets),
        *_spell_actions(character, magus.SPELLS_STEP),
    ]


PANELS[("character", "apprenticeship")] = StepPanel(
    _apprenticeship_budget, _apprenticeship_actions
)


# -- Years past Gauntlet and pre-play aging (STORY-1310) --


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
    if (cc.age(saga, character) or 0) > cc.AGING_AGE:
        actions.append(
            StepAction("Edit Aging (Longevity Ritual)", lambda ws, r: ws._edit_aging())
        )
    return actions


def _gauntlet_budget(saga: Saga, record: Record) -> str:
    character = _character(record)
    conditions = character.creation_conditions
    years = magus.years_past_gauntlet(saga, character)
    lines = [
        f"Gauntlet at {magus.gauntlet_age(character)}: {years} years past it, "
        f"{magus.POINTS_A_YEAR} points a year",
        f"Lab seasons: {conditions.lab_seasons} (cost "
        f"{magus.lab_season_cost(conditions.lab_seasons)} points)",
        f"Points: {magus.gauntlet_points(saga, character)}, "
        f"{magus.gauntlet_spent(character)} spent (1 xp or 1 spell level each)",
        xp_lines(character, "gauntlet"),
        "Spells:",
        spell_lines(saga, character, magus.GAUNTLET_SPELLS),
        f"Working conditions: aura {conditions.aura:+d}, lab quality "
        f"{conditions.lab_quality:+d}, Living Conditions "
        f"{conditions.living_conditions:+d}",
    ]
    due = magus.aging_due(saga, character)
    if due:
        lines.append(f"Pre-play aging: {due} roll(s) to make")
    return "\n".join(lines)


def _gauntlet_actions(saga: Saga, record: Record) -> list[StepAction]:
    character = _character(record)
    targets = magus.gauntlet_targets(character)
    return [
        StepAction(
            "Years and conditions",
            lambda ws, r: ws._edit_gauntlet_conditions(character),
        ),
        StepAction(
            "Spend points on xp",
            lambda ws, r: ws._spend_creation_xp(character, "gauntlet", targets),
        ),
        *_change_and_take_back(character, "gauntlet", targets),
        *_spell_actions(character, magus.GAUNTLET_SPELLS),
        *_aging_actions(saga, character),
    ]


PANELS[("character", "gauntlet")] = StepPanel(_gauntlet_budget, _gauntlet_actions)


# -- Finishing Touches and the review (STORY-1311) --


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


# -- New Covenant (STORY-1312) --


def _covenant(record: Record) -> Covenant:
    assert isinstance(record, Covenant)
    return record


def _power_budget(saga: Saga, record: Record) -> str:
    covenant = _covenant(record)
    power = cov.POWER_BY_NAME.get(covenant.power_level)
    founded = covenant.year_founded
    rows: list[tuple[str, object]] = [
        ("Power Level", covenant.power_level or "(not chosen)"),
        ("Year Founded", founded if founded is not None else "(not set)"),
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
        ]
    baseline = (
        "Free for every covenant: aura 3, one Typical source of income, a "
        "standard laboratory per magus, about a grog and two covenfolk per "
        "magus."
    )
    return f"{aligned(rows)}\n{baseline}"


def _power_actions(saga: Saga, record: Record) -> list[StepAction]:
    covenant = _covenant(record)
    return [
        StepAction(
            "Choose Power Level", lambda ws, r: ws._choose_power_level(covenant)
        ),
        StepAction("Edit covenant", lambda ws, r: ws._edit_covenant()),
    ]


def _build_points_budget(saga: Saga, record: Record) -> str:
    covenant = _covenant(record)
    lines = [f"  {escape(c.label)}: {c.points}" for c in cov.costs(saga, covenant)]
    head = f"Build Points spent: {cov.spent(saga, covenant)}"
    budget = covenant.build_points_budget
    head += f" of {budget}" if budget is not None else " (no budget set yet)"
    return "\n".join(
        [
            head,
            *(lines or ["  (nothing yet: add books, vis, enchanted items, labs)"]),
            "Priced from the covenant's Library, Possessions (vis), Enchanted "
            "Devices, starting laboratories and bought specialists. A grog or "
            "companion with a character sheet costs nothing.",
        ]
    )


def _boons_hooks_budget(saga: Saga, record: Record) -> str:
    covenant = _covenant(record)
    boons_catalog = catalog.load_covenant_boon_hook_catalog_by_id()
    boons = covenant_boon_points(covenant, boons_catalog)
    hooks = covenant_hook_points(covenant, boons_catalog)
    return aligned([("Boon points", f"{boons:g}"), ("Hook points", f"{hooks:g}")])


def _boons_hooks_actions(saga: Saga, record: Record) -> list[StepAction]:
    return [
        StepAction("Add a Boon", lambda ws, r: ws._add_boon_hook("Boon")),
        StepAction("Add a Hook", lambda ws, r: ws._add_boon_hook("Hook")),
        StepAction(
            "Use a Covenant Situation",
            lambda ws, r: ws._use_covenant_situation(_covenant(r)),
        ),
    ]


def _review_budget(saga: Saga, record: Record) -> str:
    return "\n".join(["Review:", *review_lines(saga, record)])


PANELS[("covenant", "power")] = StepPanel(_power_budget, _power_actions)


def _build_points_actions(saga: Saga, record: Record) -> list[StepAction]:
    covenant = _covenant(record)
    return [StepAction("Buy a specialist", lambda ws, r: ws._buy_specialist(covenant))]


PANELS[("covenant", "build_points")] = StepPanel(
    _build_points_budget, _build_points_actions
)
PANELS[("covenant", "boons_hooks")] = StepPanel(
    _boons_hooks_budget, _boons_hooks_actions
)
PANELS[("covenant", "finish")] = StepPanel(_review_budget)


# -- New Laboratory (STORY-1313) --


def _laboratory(record: Record) -> Laboratory:
    assert isinstance(record, Laboratory)
    return record


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


def _setup_actions(saga: Saga, record: Record) -> list[StepAction]:
    lab = _laboratory(record)
    return [
        StepAction("Edit identity (owner)", lambda ws, r: ws._edit_lab_identity()),
        StepAction(
            "Edit Characteristics", lambda ws, r: ws._edit_lab_characteristics()
        ),
        StepAction("Add a Virtue", lambda ws, r: ws._add_virtue_flaw_to(lab)),
        StepAction("Starting lab: yes/no", lambda ws, r: ws._toggle_starting_lab(lab)),
    ]


PANELS[("laboratory", "setup")] = StepPanel(_setup_budget, _setup_actions)
PANELS[("laboratory", "finish")] = StepPanel(_review_budget)

"""The Creation Worksheet's own steps, independent of how they are drawn:
spending a creation step's xp, the Native Language, sample childhoods and
training packages, spells learned at creation, the years past Gauntlet,
a new covenant's Power Level, starting income, Situation, base covenant
and what its Build Points buy, and moving a record to In Play. Each is a
command (commands.py) the worksheet's buttons and rows start; the
worksheet's panels (worksheet.py) say which."""

from __future__ import annotations

import random
from collections.abc import Callable, Sequence
from typing import Any

from .. import books as bk
from .. import catalog, creation, sourcebooks
from .. import covenant_templates as templates
from .. import covenants as cov_rules
from .. import inhabitants as inh
from .. import sheet_text as st
from .. import spells as spl
from ..arts import ART_DESCRIPTIONS, ARTS
from ..commands import (
    Act,
    Choice,
    Choose,
    Command,
    Confirm,
    Form,
    Picked,
    Refuse,
    not_offered,
    notes,
)
from ..form_spec import DialogField, pairs
from ..markup import PROBLEM_GLYPH, TODO_GLYPH, escape
from ..models import (
    CRAFT_FIELDS,
    INCOME_TYPE_DEFAULTS,
    Ability,
    AbilityDef,
    Book,
    Character,
    Covenant,
    CovenantSituationDef,
    CreationConditions,
    CreationXp,
    IncomeSource,
    Laboratory,
    Saga,
    Spell,
    VirtueFlawInstance,
    new_instance_id,
)
from ..rules import creation as rules
from ..rules import creation_access as access
from ..rules import creation_character as cc
from ..rules import creation_characteristics as cch
from ..rules import creation_covenant as cov
from ..rules import creation_later as later
from ..rules import creation_magus as magus
from ..rules import creation_packages as packages
from ..rules import creation_xp as cx
from ..rules import xp as xp_rules
from . import creation as creation_forms
from . import spell as spell_forms
from .familiar import ability_choices, parameter_fields

Record = Character | Covenant | Laboratory

#: How each creation check stands, as a mark (markup).
MARKS: dict[str, str] = {
    "pass": "[$text-success]✔[/]",
    "warn": f"[$text-error]{PROBLEM_GLYPH}[/]",
    "advice": f"[$text-warning]{TODO_GLYPH}[/]",
    "none": "[dim]○[/]",
}


# -- spending a step's xp --


def family_prefix(name: str) -> str:
    """ "Area Lore: " for "Area Lore: {region}"; "" for a plain name."""
    return name.split("{", 1)[0] if "{" in name else ""


#: How much of an Ability's or Art's description the spend form shows.
_SPEND_DESCRIPTION_CHARS = 240


def spend_live(
    saga: Saga,
    character: Character,
    name: str,
    xp: int | None,
    replacing: CreationXp | None,
) -> str:
    """The spend form's live lines for `xp` pool xp on `name`: what it
    gains (half again with an Affinity), the score that buys and the pool
    xp the next score needs, a cap warning, and what the Ability or Art
    is."""
    if not name:
        return "[dim]Choose an Ability or Art.[/]"
    lines = []
    if xp is not None and xp >= 0:
        gained, total = creation.spend_preview(character, name, xp, replacing)
        multiplier = access.xp_multiplier(character, name)
        affinity = " (Affinity x1.5)" if multiplier > 1 else ""
        lines.append(f"{escape(name)}: gains {gained} xp{affinity}")
        is_art = name in ARTS
        factor = xp_rules.ART_FACTOR if is_art else access.ability_factor(name)
        progress = xp_rules.progress(total, factor)
        more = access.xp_giving(progress.next_total - total, multiplier)
        lines.append(f"{st.live_score(total, factor)} ({more} more pool xp)")
        cap = (
            None
            if is_art
            else access.ability_cap_for(character, cc.age(saga, character), name)
        )
        if cap is not None and progress.score > cap:
            lines.append(f"[$text-error]Over the creation cap of {cap}[/]")
    if name in ARTS:
        description = ART_DESCRIPTIONS.get(name, "")
    else:
        definition = st.ability_definition(name)
        description = definition.description if definition else ""
    if description:
        if len(description) > _SPEND_DESCRIPTION_CHARS:
            description = description[: _SPEND_DESCRIPTION_CHARS - 1].rstrip() + "…"
        lines.append(f"[dim]{escape(description)}[/]")
    return "\n".join(lines)


def creation_xp_fields(
    targets: Sequence[str],
    existing: tuple[str, int] | None = None,
    *,
    xp_label: str = "Pool xp",
    character: Character | None = None,
) -> list[DialogField]:
    """xp spent at a creation step: an Ability or Art from `targets` (a
    family, "Area Lore: {region}", asks for its detail), how much pool xp,
    and an Ability's Specialty."""
    families = [t for t in targets if "{" in t]
    target, detail = None, ""
    if existing is not None:
        name = existing[0]
        family = next((f for f in families if name.startswith(family_prefix(f))), None)
        if name in targets:
            target = name
        elif family is not None:
            target, detail = family, name.removeprefix(family_prefix(family))
        else:
            target = name
    options = [(t.replace("{", "(").replace("}", ")"), t) for t in targets]
    if existing is not None and target not in targets:
        options.append((existing[0], existing[0]))
    ability = (
        next((a for a in character.abilities if a.name == existing[0]), None)
        if character is not None and existing is not None
        else None
    )
    specialty = (ability.specialty or "") if ability is not None else ""
    return [
        DialogField(
            "target",
            "Ability or Art",
            "select",
            target,
            options=options,
            required=True,
            allow_blank=True,
            placeholder="(choose one)",
        ),
        DialogField(
            "detail",
            "Which one",
            "text",
            detail,
            placeholder="e.g. the region, language or craft",
            show_if=lambda values: bool(family_prefix(values["target"] or "")),
        ),
        DialogField("xp", xp_label, "int", existing[1] if existing else 5),
        DialogField(
            "specialty",
            "Specialty",
            "text",
            specialty,
            placeholder="(optional) e.g. Swords",
            show_if=lambda values: (
                character is not None
                and bool(values["target"])
                and values["target"] not in ARTS
            ),
        ),
    ]


def creation_xp_target(values: dict[str, Any]) -> str:
    """The Ability or Art the form names, a family's detail filled in."""
    chosen = values["target"] or ""
    prefix = family_prefix(chosen)
    return prefix + (values.get("detail") or "").strip() if prefix else chosen


def creation_xp_problem(values: dict[str, Any]) -> str | None:
    prefix = family_prefix(values["target"] or "")
    if prefix and not (values.get("detail") or "").strip():
        return f"Say which {prefix.rstrip(': ')}."
    if values["xp"] < 1:
        return "xp must be at least 1."
    return None


def creation_xp_form(
    saga: Saga,
    character: Character,
    title: str,
    targets: Sequence[str],
    apply: Callable[[str, int, str], Any],
    *,
    existing: CreationXp | None = None,
) -> Form:
    """Spend (or, given `existing`, change) a step's pool xp; `apply` gets
    (the Ability or Art, the xp, the Specialty or "")."""
    current = (existing.target, existing.xp) if existing is not None else None
    return Form(
        title,
        lambda: creation_xp_fields(targets, current, character=character),
        lambda values: apply(
            creation_xp_target(values),
            values["xp"],
            (values.get("specialty") or "").strip(),
        ),
        validate=creation_xp_problem,
        live=lambda values: spend_live(
            saga, character, creation_xp_target(values), values["xp"], existing
        ),
        save_label="Spend" if existing is None else "Save",
    )


def spend_xp(
    saga: Saga,
    character: Character,
    step: str,
    targets: Sequence[str],
    *,
    note: str = "",
    title: str = "Spend xp",
) -> Form:
    """Spend some of `step`'s pool xp on an Ability or Art (and give an
    Ability its Specialty)."""

    def apply(target: str, xp: int, specialty: str) -> None:
        creation.spend_creation_xp(character, CreationXp(step, target, xp, note))
        creation.set_specialty(character, target, specialty)

    return creation_xp_form(saga, character, title, targets, apply)


def change_xp(
    saga: Saga, character: Character, entry: CreationXp, targets: Sequence[str]
) -> Form:
    """Change what `entry` spent its pool xp on, or how much (the xp it
    gained comes off first, so an Affinity's half again is undone
    exactly)."""

    def apply(target: str, xp: int, specialty: str) -> None:
        creation.change_creation_xp(character, entry, target, xp)
        creation.set_specialty(character, target, specialty)

    return creation_xp_form(
        saga, character, "Change xp", targets, apply, existing=entry
    )


def refund_xp(character: Character, entry: CreationXp) -> Confirm:
    """Take `entry`'s pool xp back: the xp it gained comes off its Ability
    or Art."""
    gained = creation.gained_xp(entry)
    also = f" ({gained} xp comes off it)" if gained != entry.xp else ""
    return Confirm(
        f"Take back the {entry.xp} xp spent on {escape(entry.target)}?{also}",
        lambda: creation.refund_creation_xp(character, entry),
        yes_label="Take back",
    )


# -- Early Childhood and training packages --


def native_entry(character: Character) -> CreationXp | None:
    return next(
        (x for x in cx.entries(character, "childhood") if x.note == cx.NATIVE), None
    )


def native_language(character: Character) -> Form:
    """Choose the Native Language: its 75 childhood xp."""
    native = native_entry(character)
    current = native.target if native else ""

    def apply(values: dict[str, Any]) -> None:
        language = "Living Language: " + values["language"]
        if native is None:
            creation.spend_creation_xp(
                character, CreationXp("childhood", language, cx.NATIVE_XP, cx.NATIVE)
            )
        else:
            creation.change_creation_xp(character, native, language, cx.NATIVE_XP)

    return Form(
        "Native Language",
        lambda: [
            DialogField(
                "language",
                "Language",
                "text",
                current.removeprefix("Living Language: "),
                required=True,
                placeholder="e.g. German",
            )
        ],
        apply,
    )


def with_blanks(
    title: str, rows: cx.XpRows, then: Callable[[list[tuple[str, int]]], Any]
) -> Command:
    """Ask for the names `rows` leave blank ("Area Lore: {area}"), then
    call `then` with the filled-in (Ability, xp)."""
    blanks = cx.template_blanks(rows)
    if not blanks:
        return Act(lambda: then(list(rows)))
    return Form(
        title,
        lambda: creation_forms.blanks_fields(blanks),
        lambda values: then(cx.fill_template(rows, values)),
        save_label="Use",
    )


def use_childhood(character: Character, childhood: cx.Childhood) -> Command:
    """Spend the 45 childhood xp as `childhood` (asking for the names it
    leaves blank), replacing what was spent there (the Native Language
    stays)."""

    def apply(filled: list[tuple[str, int]]) -> None:
        for entry in cx.entries(character, "childhood"):
            if entry.note != cx.NATIVE:
                creation.refund_creation_xp(character, entry)
        for target, xp in filled:
            creation.spend_creation_xp(character, CreationXp("childhood", target, xp))

    return with_blanks(f"{childhood.name} childhood", childhood.xp, apply)


def sample_childhood(saga: Saga, character: Character) -> Choose:
    """Choose one of the sample childhoods to spend the 45 childhood xp
    as (use_childhood)."""
    return Choose(
        "Use a sample childhood (replaces the 45 xp)",
        lambda: [Choice(cx.childhood_label(c), c) for c in cx.childhoods_in_play(saga)],
        lambda childhood: use_childhood(character, childhood),
        empty="(no sample childhoods in play)",
    )


def training_package(character: Character) -> Choose:
    """Pick a Grogs training package and its length, fill its blanks, and
    spend its xp (a Later Life quick build)."""

    def offered() -> list[Choice]:
        return [
            Choice(packages.package_label(package, years), (package, years))
            for package in packages.PACKAGES
            for years, rows in ((5, package.five), (3, package.three))
            if rows
        ]

    def chosen(choice: tuple[packages.Package, int]) -> Command:
        package, years = choice
        note = packages.Taken(
            package.name, years, packages.next_time(character, package.name)
        ).note

        def apply(filled: list[tuple[str, int]]) -> None:
            for target, xp in filled:
                creation.spend_creation_xp(
                    character, CreationXp("package", target, xp, note)
                )

        rows = tuple(packages.package_xp(package, years))
        return with_blanks(f"{package.name} ({years} years)", rows, apply)

    return Choose("Take a training package", offered, chosen)


def drop_package(character: Character, note: str) -> Command:
    """Take back every xp of the package taken as `note`, after asking."""
    taken = next((t for t in packages.taken(character) if t.note == note), None)
    if taken is None:
        return Refuse("Drop a package", "That package isn't taken.")

    def apply() -> None:
        for entry in [x for x in cx.entries(character, "package") if x.note == note]:
            creation.refund_creation_xp(character, entry)

    return Confirm(
        f"Drop the {escape(taken.name)} package ({taken.years} years) and take "
        "back all its xp?",
        apply,
        yes_label="Drop",
    )


def record_free_scores(character: Character) -> Act:
    """The free first 5 xp in each Supernatural Ability a Virtue grants."""

    def apply() -> None:
        for name in later.free_scores_missing(character):
            creation.spend_creation_xp(
                character, CreationXp("free", name, later.FREE_SUPERNATURAL_XP)
            )

    return Act(apply)


# -- Concept and Characteristics --


def add_type_virtues(character: Character) -> Act:
    def apply() -> None:
        for vf_id in cc.missing_type_virtues(character):
            character.virtues_flaws.append(VirtueFlawInstance(vf_id))

    return Act(apply)


def mythic_status(saga: Saga, character: Character) -> Choose:
    """Pick the character's one Mythic Companion status Virtue (from the
    books in play), replacing any other."""
    books = sourcebooks.saga_books(saga)

    def offered() -> list[Choice]:
        statuses = sorted(
            (
                entry
                for entry in catalog.load_virtue_flaw_catalog()
                if entry.id in cc.mythic_status_ids()
                and sourcebooks.in_play(entry.source, books)
            ),
            key=lambda entry: entry.name,
        )
        return [
            Choice(escape(e.name), e.id, escape(e.description or e.summary))
            for e in statuses
        ]

    def chosen(vf_id: str) -> None:
        statuses = cc.mythic_status_ids()
        character.virtues_flaws = [
            vf for vf in character.virtues_flaws if vf.vf_id not in statuses
        ]
        character.virtues_flaws.append(VirtueFlawInstance(vf_id))

    return Choose("Choose the Mythic Companion status Virtue", offered, chosen)


def house_virtue_name(option: dict) -> str:
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    return catalog.describe_virtue_flaw(
        VirtueFlawInstance(option["vf_id"], dict(option.get("params") or {})), by_id
    )


def add_house_virtue(character: Character) -> Command:
    """Add the House's free Virtue; a House with a choice asks which."""
    house = catalog.load_house_catalog_by_id().get(character.hermetic.house or "")
    if house is None or not house.virtues:
        return Refuse("Add the House Virtue", "The House gives no Virtue.")

    def add(option: dict) -> None:
        character.virtues_flaws.append(
            VirtueFlawInstance(option["vf_id"], dict(option.get("params") or {}))
        )

    if len(house.virtues) == 1:
        return Act(lambda: add(house.virtues[0]))
    return Choose(
        f"House {escape(house.name)}'s free Virtue",
        lambda: [Choice(escape(house_virtue_name(o)), o) for o in house.virtues],
        add,
    )


def grog_array(character: Character) -> Choose:
    """Set the Characteristics from one of the Grogs book's arrays, in
    order; the user then moves the scores where they belong."""

    def chosen(array: tuple[int, ...]) -> None:
        for (key, _), score in zip(cch.CHARACTERISTICS, array, strict=True):
            setattr(character.characteristics, key, score)

    return Choose(
        "Fill from a Grogs array (Int, Per, Str, Sta, Pre, Com, Dex, Qik)",
        lambda: [
            Choice(" ".join(f"{n:+d}" for n in array), array)
            for array in cch.GROG_ARRAYS
        ],
        chosen,
    )


# -- spells learned at creation, the years past Gauntlet and aging --


def learn_spell(saga: Saga, character: Character, step: str) -> Choose:
    """Pick a spell to learn at `step` ("apprenticeship_spells" or
    "gauntlet_spells"); a General-level spell asks at what level."""

    def offered() -> list[Choice]:
        found = []
        for choice in spell_forms.spell_choices(
            saga, {k.spell_id for k in character.spells_known}
        ):
            spell = spl.find_spell(saga, choice.value)
            if spell is None:
                continue
            cap = magus.spell_cap(saga, character, spell)
            found.append(
                Choice(
                    choice.label,
                    choice.value,
                    choice.detail
                    + f"\n[b]{escape(character.name)}'s Lab Total for it (aura 3):[/]"
                    f" {cap}",
                    choice.search,
                )
            )
        return found

    def chosen(spell_id: str) -> Command | None:
        spell = spl.find_spell(saga, spell_id)
        if spell is None:
            return None
        if spell.level is not None:
            creation.learn_creation_spell(character, step, spell.id, spell.level)
            return None
        return spell_level_form(character, step, spell)

    return Choose(
        f"A spell {escape(character.name)} learns",
        offered,
        chosen,
        empty="(no spells)",
        others=lambda: spell_forms.spell_choices(
            saga, {k.spell_id for k in character.spells_known}, in_play=False
        ),
    )


def spell_level_form(character: Character, step: str, spell: Spell) -> Form:
    """The level a General-level spell is learned at."""
    return Form(
        f"Learn {escape(spell.name)} at what level?",
        lambda: [DialogField("level", "Level", "int", 5)],
        lambda values: creation.learn_creation_spell(
            character, step, spell.id, values["level"]
        ),
        validate=lambda values: (
            None if values["level"] >= 1 else "Level must be at least 1."
        ),
        save_label="Learn",
    )


def forget_spell(saga: Saga, character: Character, entry: CreationXp) -> Confirm:
    spell = spl.find_spell(saga, entry.target)
    name = escape(spell.name if spell else entry.target)
    return Confirm(
        f"Forget {name}?",
        lambda: creation.forget_creation_spell(character, entry),
        yes_label="Forget",
    )


def gauntlet_conditions_fields(conditions: CreationConditions) -> list[DialogField]:
    return [
        DialogField(
            "lab_seasons",
            "Seasons of lab work",
            "int",
            conditions.lab_seasons,
            hint="Each costs 10 of that year's 30 points (4 a year: all 30).",
        ),
        DialogField("aura", "Aura", "int", conditions.aura),
        DialogField("lab_quality", "Lab quality", "int", conditions.lab_quality),
        DialogField(
            "living_conditions",
            "Living Conditions",
            "int",
            conditions.living_conditions,
            hint="Used for the aging rolls before play.",
        ),
    ]


def gauntlet_conditions_problem(values: dict[str, Any]) -> str | None:
    if values["lab_seasons"] < 0:
        return "Lab seasons can't be negative."
    return None


def gauntlet_conditions(character: Character) -> Form:
    """A magus's years past Gauntlet: the seasons of lab work, and the
    working conditions the storyguide set."""
    conditions = character.creation_conditions

    def apply(values: dict[str, Any]) -> None:
        for key, value in values.items():
            setattr(conditions, key, value)

    return Form(
        "Years past Gauntlet",
        lambda: gauntlet_conditions_fields(conditions),
        apply,
        validate=gauntlet_conditions_problem,
    )


def roll_pre_play_aging(saga: Saga, character: Character) -> Command:
    """The aging rolls a character older than 35 makes before play, after
    asking (they can't be taken back)."""
    due = magus.aging_due(saga, character)
    if not due:
        return Refuse("Roll pre-play aging", "No aging rolls to make.")
    return Confirm(
        f"Roll {due} aging roll(s) for {escape(character.name)}? Each is written "
        "in the Diary and can't be undone.",
        lambda: notes(
            "; ".join(creation.pre_play_aging(saga, character, random.Random()))
        ),
        yes_label="Roll",
    )


# -- a new covenant --


def power_label(power: cov.PowerLevel) -> str:
    top = f"{power.most}" if power.most is not None else "+"
    cap = f"level {power.max_level}" if power.max_level is not None else "any level"
    return f"{power.name} ({power.least}-{top} BP, {cap})"


def power_level_fields(covenant: Covenant) -> list[DialogField]:
    return [
        DialogField(
            "power_level",
            "Power Level",
            "select",
            covenant.power_level or None,
            options=[(power_label(p), p.name) for p in cov.POWER_LEVELS],
            required=True,
            allow_blank=True,
            placeholder="(choose one)",
        ),
        DialogField(
            "build_points_budget",
            "Build Points",
            "optint",
            covenant.build_points_budget,
            hint="Set by the storyguide, within the Power Level's range.",
        ),
        DialogField(
            "magi_without_lab",
            "Magi without a laboratory",
            "int",
            covenant.magi_without_lab,
            hint="Each refunds 50 Build Points. Every other magus has a free "
            "standard lab, entered or not.",
        ),
        DialogField(
            "year_founded",
            "Year Founded",
            "optint",
            covenant.year_founded,
            hint="Medium needs 10 years, High 50, Legendary 100.",
        ),
    ]


def power_level_problem(values: dict[str, Any]) -> str | None:
    power = cov.POWER_BY_NAME.get(values.get("power_level") or "")
    points = values.get("build_points_budget")
    if power is not None and points is not None and not cov.in_band(power, points):
        return f"{power.name} gives {cov.band(power)} Build Points."
    if (values.get("magi_without_lab") or 0) < 0:
        return "Magi without a laboratory can't be negative."
    return None


def power_level(covenant: Covenant) -> Form:
    """A new covenant's Power Level and when it was founded."""

    def apply(values: dict[str, Any]) -> None:
        covenant.power_level = values["power_level"]
        covenant.build_points_budget = values["build_points_budget"]
        covenant.magi_without_lab = values["magi_without_lab"]
        covenant.year_founded = values["year_founded"]

    return Form(
        "Power Level",
        lambda: power_level_fields(covenant),
        apply,
        validate=power_level_problem,
    )


def starting_income(saga: Saga, covenant: Covenant) -> Choose:
    """Start the covenant's income one of the ways the rules allow (one
    Typical source, or two Lesser; what its Poverty or Wealth allows),
    replacing any sources it has after asking."""

    def replace(choice: cov.IncomeChoice) -> None:
        sources = []
        for number, (kind, pounds) in enumerate(choice.sources, start=1):
            name = "Source of income" + (
                f" {number}" if len(choice.sources) > 1 else ""
            )
            sources.append(
                IncomeSource(
                    id=new_instance_id(),
                    name=name,
                    type=kind,
                    income=None if pounds == INCOME_TYPE_DEFAULTS[kind] else pounds,
                )
            )
        covenant.economics.income_sources = sources

    def chosen(choice: cov.IncomeChoice) -> Command | None:
        have = len(covenant.economics.income_sources)
        if not have:
            replace(choice)
            return None
        return Confirm(
            f"Replace the covenant's {have} source(s) of income with "
            f"{escape(choice.label)}?",
            lambda: replace(choice),
            yes_label="Replace",
        )

    return Choose(
        "Start the covenant's income",
        lambda: [
            Choice(escape(c.label), c) for c in cov.income_choices(saga, covenant)
        ],
        chosen,
    )


def covenant_situation(saga: Saga, covenant: Covenant) -> Choose:
    """Add one of the books' Covenant Situations: a ready-made set of Boons
    and Hooks, on top of any the user added. One applied before is
    replaced, after a warning."""
    books = sourcebooks.saga_books(saga)
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    every = catalog.load_covenant_situation_catalog()

    def label(situation: CovenantSituationDef) -> str:
        hooks, boons = cov_rules.situation_points(situation, by_id)
        book = sourcebooks.SOURCEBOOKS.get(situation.source, situation.source)
        return (
            f"{escape(situation.name)}  [dim]{hooks:g} Hook, {boons:g} Boon "
            f"points; {escape(book)}[/]"
        )

    def chosen(situation: CovenantSituationDef) -> Confirm:
        added = cov_rules.situation_instances(situation)
        earlier = cov_rules.situation_in_use(covenant)
        if earlier is not None:
            old_id, count = earlier
            old = next((s for s in every if s.id == old_id), None)
            old_name = escape(old.name) if old is not None else "A Situation"
            message = (
                f"{old_name} is already applied. Using {escape(situation.name)} "
                f"removes the {count} Boons and Hooks it brought and adds "
                f"{len(added)}. {escape(situation.description)} Boons and Hooks "
                "you added yourself stay."
            )
            yes_label = "Replace"
        else:
            message = (
                f"Add {escape(situation.name)}'s {len(added)} Boons and Hooks to "
                f"{escape(covenant.name)}? {escape(situation.description)}"
            )
            if covenant.boons_hooks:
                message += " The ones it already has stay."
            yes_label = "Add"
        if situation.notes:
            message += f"\n\n[dim]{escape(situation.notes)}[/]"
        return Confirm(
            message,
            lambda: cov_rules.use_situation(covenant, added),
            yes_label=yes_label,
        )

    return Choose(
        "Use a Covenant Situation",
        lambda: [
            Choice(label(s), s, escape(s.description), s.description)
            for s in every
            if sourcebooks.in_play(s.source, books)
        ],
        chosen,
        empty="(no Covenant Situations in play)",
    )


def base_covenant(saga: Saga, covenant: Covenant) -> Choose:
    """Start from one of the book's base covenants: its Power Level, Build
    Points and placeholders for its books and vis, after asking (and
    warning when another is in use)."""

    def chosen(base: templates.BaseCovenant) -> Confirm:
        earlier = templates.BASE_BY_KEY.get(covenant.base_covenant)
        books, vis = templates.placeholders(saga, covenant)
        message = (
            f"Start {escape(covenant.name)} from the {base.name}: Power Level "
            f"{base.power_level}, {base.build_points} Build Points, and "
            f"{escape(templates.summary(base))}. Books and vis come as "
            "placeholders whose subject or Art you choose; Lab Text and "
            "enchanted item levels are an allowance to spend."
        )
        if earlier is not None and earlier is not base:
            message = (
                f"{earlier.name} is in use. {message} The {len(books) + len(vis)} "
                "placeholder(s) it left unfilled are removed; what you filled in "
                "stays."
            )
        if base.notes:
            message += "\n\n[dim]" + escape(" ".join(base.notes)) + "[/]"
        return Confirm(
            message, lambda: templates.apply(saga, covenant, base), yes_label="Use it"
        )

    return Choose(
        "Use a base covenant",
        lambda: [
            Choice(
                f"{escape(b.name)}  [dim]{b.build_points} Build Points, "
                f"{b.power_level}[/]",
                b,
                escape(templates.summary(b)),
            )
            for b in templates.BASE_COVENANTS
        ],
        chosen,
    )


def saga_book(saga: Saga, covenant: Covenant) -> Choose:
    """Pick one of the saga's own books a new covenant may buy and copy it
    into the covenant's Library (the saga's copy stays where it is)."""
    power = cov.POWER_BY_NAME.get(covenant.power_level)
    cap = power.max_level if power is not None else None

    def choice(book: Book) -> Choice:
        level = bk.level_of(book, saga)
        return Choice(
            f"{escape(book.name)}  [dim]{escape(book.type)}  L"
            f"{level if level is not None else '-'} Q{book.quality or '-'}  "
            f"{bk.cost(book, saga)} BP[/]",
            book,
            bk.detail_text(saga, book),
            f"{book.type} {bk.subject(book, saga)} {book.author} {book.language}",
        )

    def books(over: bool) -> list[Choice]:
        """The saga's books within a new covenant's limits, or (`over`)
        the others, each marked with why."""
        found = []
        for book in sorted(
            bk.unassigned_books(saga), key=lambda b: (b.type, b.name.lower())
        ):
            refusals = bk.creation_refusals(saga, book, cap)
            if bool(refusals) != over:
                continue
            found.append(
                not_offered(choice(book), " ".join(refusals)) if over else choice(book)
            )
        return found

    def chosen(book: Book) -> list[str]:
        bk.copy_to(saga, book, "covenant", covenant.id)
        return notes(
            f"{escape(book.name)} copied into {escape(covenant.name)}'s Library."
        )

    return Choose(
        "Buy one of the saga's books",
        lambda: books(False),
        chosen,
        empty="(no books a new covenant may buy)",
        others=lambda: books(True),
    )


# -- Buy a Specialist --


def bought_ability(value: Any) -> tuple[str, str]:
    """The (name, category) of a Buy a Specialist form's Ability: an
    Ability chosen from the list, or a name."""
    if isinstance(value, Ability):
        return value.name, value.category
    name = str(value or "")
    definition = st.ability_definition(name)
    return name, definition.category if definition else ""


def choose_ability(saga: Saga, title: str = "Choose an Ability") -> Choose:
    """Choose any Ability from the books in play, naming what a templated
    one ("Craft: {craft}") leaves blank; picked as an Ability."""

    def chosen(entry: AbilityDef) -> Command | Picked:
        if not entry.parameters:
            return Picked(
                Ability(
                    name=entry.name, category=entry.category, xp_table=entry.xp_table
                )
            )
        return Form(
            escape(entry.name),
            lambda: parameter_fields(entry.parameters),
            lambda values: Picked(
                Ability(
                    name=catalog.resolve_ability_name(
                        entry, {p: values[p].lower() for p in entry.parameters}
                    ),
                    category=entry.category,
                    xp_table=entry.xp_table,
                )
            ),
            save_label="Confirm",
        )

    return Choose(
        title,
        lambda: ability_choices(saga, []),
        chosen,
        others=lambda: ability_choices(saga, [], in_play=False),
    )


def specialist_fields(
    saga: Saga, ability_picker: Callable[[Any], Any] | None = None
) -> list[DialogField]:
    """Someone bought with Build Points for a new covenant: an NPC defined
    by the Ability they serve with. A teacher costs Communication +
    Teaching + the highest Ability taught; anyone else their score."""

    def teacher(values: dict[str, Any]) -> bool:
        return bool(values.get("teacher"))

    def craft(values: dict[str, Any]) -> bool:
        return specialist_kind(values) == "craftsperson"

    return [
        DialogField("name", "Name", "text", "", required=True),
        DialogField("teacher", "A teacher", "check", False),
        DialogField(
            "linked_ability",
            "Ability used for the covenant",
            "picker",
            None,
            placeholder="(choose an Ability)",
            picker=ability_picker,
            choose=lambda _current: choose_ability(saga),
            display=lambda value: bought_ability(value)[0],
            hint="A teacher: the highest Ability taught.",
        ),
        DialogField("specialist_score", "Its score", "int", 1),
        DialogField("rare", "A rare craft", "check", False, show_if=craft),
        DialogField(
            "field_of_work",
            "Saves money on",
            "select",
            "None",
            options=pairs(CRAFT_FIELDS),
            show_if=craft,
        ),
        DialogField(
            "teacher_communication", "Communication", "int", 0, show_if=teacher
        ),
        DialogField("teacher_teaching", "Teaching", "int", 1, show_if=teacher),
        DialogField("year_born", "Year Born", "optint", None),
    ]


def specialist_kind(values: dict[str, Any]) -> str:
    """Which covenfolk the specialist joins, from their Ability."""
    name, category = bought_ability(values.get("linked_ability"))
    return inh.bought_kind(name, category, teacher=bool(values.get("teacher")))


def specialist_cost(values: dict[str, Any]) -> int:
    total = values.get("specialist_score") or 0
    if values.get("teacher"):
        total += (values.get("teacher_communication") or 0) + (
            values.get("teacher_teaching") or 0
        )
    return total


def specialist_live(values: dict[str, Any]) -> str:
    if not values.get("linked_ability"):
        return f"Costs {specialist_cost(values)} Build Points"
    return (
        f"Joins the {inh.KIND_TITLES[specialist_kind(values)]}. "
        f"Costs {specialist_cost(values)} Build Points"
    )


def specialist_problem(values: dict[str, Any]) -> str | None:
    if not values.get("linked_ability"):
        return "Choose the Ability they serve the covenant with."
    if values["specialist_score"] < 0:
        return "The score can't be negative."
    return None


def specialist_from(values: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """(the covenfolk kind, an Inhabitant's fields) for the form's values."""
    values = dict(values)
    which = specialist_kind(values)
    name, _ = bought_ability(values["linked_ability"])
    is_teacher = values.pop("teacher")
    rare = values.pop("rare", False)
    field = values.pop("field_of_work", None) or "None"
    values["linked_ability"] = name
    if not is_teacher:
        values["teacher_communication"] = None
        values["teacher_teaching"] = None
    else:
        values["role"] = "Teacher"
    if which == "craftsperson":
        values["rare"] = bool(rare)
        values["field_of_work"] = field
        values["skill_value"] = values["specialist_score"]
    return which, values


def buy_specialist(saga: Saga, covenant: Covenant) -> Form:
    """Buy someone with Build Points: a new line on the Inhabitants, in the
    category their Ability gives them (a craftsperson, the turb or a
    specialist)."""

    def apply(values: dict[str, Any]) -> None:
        kind, fields = specialist_from(values)
        inh.save_entry(covenant, kind, None, fields)

    return Form(
        "Buy a Specialist",
        lambda: specialist_fields(saga),
        apply,
        validate=specialist_problem,
        live=specialist_live,
        save_label="Buy",
    )


# -- Move to In Play --


def move_to_play(saga: Saga, record: Record) -> Command:
    """Show the review of every check, then move the record to In Play
    (with strict creation rules, not while a must is broken)."""
    if not record.in_creation:
        return Refuse("Move to In Play", f"{escape(record.name)} is already In Play.")
    found = rules.checks(saga, record)
    if not rules.can_move_to_play(saga, record):
        return Refuse(
            "Move to In Play",
            f"{escape(record.name)} stays In Creation: it breaks "
            f"{len(rules.broken_musts(found))} creation rule(s) it must follow, "
            "and this saga enforces them strictly.",
        )
    open_checks = [c for c in found if c.status != "pass"]
    review = "\n".join(f"{MARKS[c.status]} {escape(c.label)}" for c in open_checks[:12])
    if len(open_checks) > 12:
        review += f"\n...and {len(open_checks) - 12} more"
    message = (
        f"Move {escape(record.name)} to In Play? Creation checks: "
        f"{rules.summary(found)}."
    )
    if isinstance(record, Covenant):
        note = cov.leftover_note(saga, record)
        if note:
            message += f"\n\n{escape(note)}"
    if review:
        message += f"\n\n{review}"
    return Confirm(
        message,
        lambda: creation.set_in_creation(saga, record, False),
        yes_label="Move to In Play",
    )

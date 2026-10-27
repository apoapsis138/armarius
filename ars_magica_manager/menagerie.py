"""A Menagerie on a covenant's Projects tab (a chapter on the desktop):
the menagerie's site and staff, what it can tend and costs, its owner's
Reputation and its worth as realia; its beasts (More: Tame a Beast) and
the breedings of their pairs (Add: Breed a Pair). The rules are
rules.menagerie's (Hermetic Projects pp. 119-142); the records
models.menagerie's, held on the project.

Pattern: the second kind in the Projects tab's registry (a Strategy, as
hermetic_projects.KIND_TEXT keeps it): the shown project's kind picks the
tab's sections, here a block and two lists of neighbour_lists' KindTab
pieces that each front-end already draws. Taming is not a season of its
own: Tame a Beast plans the tamer's existing taming season (the activity
registry's Strategy), whose progress record the beast's state reads."""

from __future__ import annotations

import random
from collections.abc import Callable
from typing import Any

from . import catalog
from .arts import FORMS
from .commands import Command, Confirm, Form, Refuse, SectionOps, notes
from .form_spec import DialogField, pairs
from .grids import Grid
from .markup import escape
from .models import (
    SEASONS,
    Character,
    Covenant,
    DiaryEntry,
    Neighbour,
    Saga,
    SeasonPlan,
    XpAllocation,
)
from .models.character import Progress
from .models.hermetic_projects import HermeticProject
from .models.menagerie import (
    AIM_LABELS,
    AIMS,
    BEAST_KINDS,
    BOTH,
    DIETS,
    FEMALE,
    MALE,
    MATURITY_YEARS,
    MENAGERIE,
    SEXES,
    TRANSFORMED,
    YOUNG,
    Beast,
    Breeding,
)
from .neighbour_lists import KindBlock, KindList, LedgerEntry
from .references import Fact
from .rules import activities, confidence, dice, lab_seasons, realms, sites
from .rules import hermetic_projects as hp
from .rules import menagerie as mg
from .rules.scores import ability_level
from .rules.season_work.definitive import gift_penalty, kept_points, master_of_creatures
from .seasons.plans import plan_for, set_plan
from .sections import BEASTS_SECTION, BREEDINGS_SECTION, MENAGERIE_SECTION

HP = mg.HP
TAME_BEAST = "Tame a Beast"
BREED_PAIR = "Breed a Pair"
PANEL = "[dim]Choose a project, a beast or a breeding.[/]"
#: The menagerie's kind, in a line (hermetic_projects.KIND_TEXT).
KIND_LINE = "a collection of magical beasts, kept, tamed and bred"
#: Rows of staff on the project's form (lead handler first).
HANDLER_FIELDS = 3
TAME_ANIMAL = "tame_animal"


# -- finding the record --------------------------------------------------------


def covenant_of(saga: Saga, holder: Neighbour) -> Covenant | None:
    return saga.covenant(holder.id)


def shown(saga: Saga, holder: Neighbour) -> HermeticProject | None:
    """The menagerie the tab shows (None when the shown project is a
    tower, or there is none)."""
    covenant = covenant_of(saga, holder)
    project = hp.shown_project(covenant) if covenant is not None else None
    return project if project is not None and project.kind == MENAGERIE else None


def _beast(project: HermeticProject, beast_id: str) -> Beast | None:
    return next((b for b in project.beasts if b.id == beast_id), None)


def _name(saga: Saga, character_id: str) -> str:
    found = saga.character(character_id) if character_id else None
    return found.name if found is not None else ""


def _coloured(words: str, tone: str) -> str:
    return f"[${tone}]{escape(words)}[/]" if tone != "label" else escape(words)


def _plural(count: int, word: str) -> str:
    return f"{count} {word}{'' if count == 1 else 's'}"


# -- the menagerie -------------------------------------------------------------


def site(saga: Saga, covenant: Covenant, project: HermeticProject) -> tuple[str, int]:
    """Where it stands, and the Magic aura there (0 in another realm's):
    its place's, else the covenant's."""
    place = sites.place(saga, project.place_id)
    if place is not None:
        aura, realm = sites.aura_at(place)
        name = place.name
    else:
        boons = catalog.load_covenant_boon_hook_catalog_by_id()
        aura, realm = (
            realms.covenant_effective_aura(covenant, boons),
            covenant.aura_realm,
        )
        name = f"{covenant.name}'s grounds"
    magic = aura if realm == realms.HERMETIC else 0
    words = f"{name}, {realm} aura {aura}" if aura else f"{name}, no aura"
    return words, magic


def progress(project: HermeticProject) -> str:
    """The projects list's Progress: its beasts."""
    return _plural(mg.head_count(project), "beast")


def note(project: HermeticProject) -> str:
    """The projects list's Note: its magical breeds."""
    return _plural(mg.realia_quality(project), "breed")


def staff_text(saga: Saga, project: HermeticProject) -> str:
    people = mg.handlers(saga, project)
    if not people:
        return "none yet"
    return ", ".join(
        f"{c.name} (Animal Handling {ability_level(c, mg.ANIMAL_HANDLING)})"
        if ability_level(c, mg.ANIMAL_HANDLING)
        else c.name
        for c in people
    )


def reputation_text(saga: Saga, project: HermeticProject) -> str:
    owner = saga.character(project.owner_id) if project.owner_id else None
    if owner is None:
        return "no owner named"
    name = project.reputation.strip()
    if not name:
        return f"{owner.name}'s: none named"
    found = next(
        (r for r in owner.reputations if r.name.casefold() == name.casefold()), None
    )
    if found is None:
        return f"{name} 0 ({owner.name}'s, not yet on his sheet)"
    return f"{found.name} {found.score} ({found.deeds} xp)"


def menagerie_facts(saga: Saga, holder: Neighbour) -> list[Fact]:
    covenant = covenant_of(saga, holder)
    project = shown(saga, holder)
    if covenant is None or project is None:
        return []
    where, _aura = site(saga, covenant, project)
    tend = mg.can_tend(saga, project)
    held = mg.load(saga, project)
    breeds = mg.realia_quality(project)
    return [
        Fact("Site", where),
        Fact("Staff", staff_text(saga, project)),
        Fact(
            "Can tend",
            f"{tend} tame herbivores, or {tend // (mg.CARNIVORE_LOAD * mg.WILD_LOAD)} "
            f"wild carnivores (holding {held})",
        ),
        Fact("Upkeep", f"{_plural(mg.upkeep(project), 'Inhabitants point')}"),
        Fact("Reputation", reputation_text(saga, project)),
        Fact(
            "As realia",
            f"{_plural(breeds, 'breed')}: Magic Lore, Quality {breeds}"
            if breeds
            else "no magical breed yet",
        ),
    ]


def warnings(saga: Saga, covenant: Covenant, project: HermeticProject) -> list[str]:
    """What the storyguide should watch: too many beasts for the staff,
    and beasts whose Might the aura can't hold (Acclimation)."""
    year = saga.current_year
    lines: list[str] = []
    tend, held = mg.can_tend(saga, project), mg.load(saga, project)
    if project.beasts and held > tend:
        lines.append(
            f"[$text-warning]The staff can tend {tend} tame herbivores' worth; the "
            f"beasts are {held}' worth ({HP} p. 136).[/]"
        )
    _where, aura = site(saga, covenant, project)
    for beast in project.beasts:
        needed = mg.acclimation(beast, aura, year)
        if needed is None:
            continue
        might = mg.might_now(beast, year)
        need = (
            "no aura will hold it"
            if needed == 0
            else f"it needs an aura of {needed} to live always within"
        )
        lines.append(
            f"[$text-warning]{escape(beast.name)} (Might {might}) lives in a Magic "
            f"aura of {aura}: {need}; watch its Acclimation (RoP: Magic p. 53).[/]"
        )
    return lines


def menagerie_text(saga: Saga, covenant: Covenant, project: HermeticProject) -> str:
    lines = warnings(saga, covenant, project)
    lines.append(
        "[dim]A handler tends 10 tame herbivores per point of Animal Handling, half "
        "as many carnivores, a fifth as many wild ones; Inhabitants points as a "
        "horse (Size +3) is 1, halving or doubling per Size, carnivores double "
        f"({HP} pp. 123, 136).[/]"
    )
    return "\n".join(lines)


def block_text(saga: Saga, holder: Neighbour) -> str:
    covenant = covenant_of(saga, holder)
    project = shown(saga, holder)
    if covenant is None or project is None:
        return "[$label]No menagerie shown.[/]"
    return menagerie_text(saga, covenant, project)


def menagerie_title(saga: Saga, covenant: Covenant | None) -> str:
    project = hp.shown_project(covenant) if covenant is not None else None
    if project is None:
        return "The Menagerie"
    return f"{project.name or '(unnamed)'}: {project.kind}"


# -- the beasts ----------------------------------------------------------------


def _kind_words(beast: Beast) -> str:
    breed = beast.breed or beast.name
    words = breed if beast.breed else beast.kind
    if beast.count > 1:
        words += f", {beast.count} of them"
    if beast.born is not None:
        words += f" (born {beast.born})"
    return words


def beasts_title(saga: Saga, holder: Neighbour) -> str:
    project = shown(saga, holder)
    if project is None:
        return "Beasts"
    rows, heads = len(project.beasts), mg.head_count(project)
    if heads != rows:
        return f"Beasts ({heads}, in {rows} rows)"
    return f"Beasts ({rows})"


def beasts_grid(saga: Saga, holder: Neighbour) -> Grid:
    project = shown(saga, holder)
    beasts = project.beasts if project is not None else []
    year = saga.current_year
    rows: list[list[str]] = []
    styles: dict[tuple[int, int], str] = {}
    for i, beast in enumerate(beasts):
        state = mg.state(saga, beast, year)
        rows.append(
            [
                beast.name or "(unnamed)",
                _kind_words(beast),
                str(mg.might_now(beast, year)) if mg.is_magical(beast) else "–",
                beast.sex,
                state.words,
            ]
        )
        styles[(i, 4)] = f"${state.tone}"
    return Grid(
        ["Beast", "Kind", "Might", "Sex", "State"],
        rows,
        list(range(len(beasts))),
        "No beasts yet: Add one.",
        styles=styles,
        caps=[16, 28, 5, 6],
    )


def _beast_meta(beast: Beast, year: int) -> str:
    might = f"Might {mg.might_now(beast, year)}" if mg.is_magical(beast) else "no Might"
    return f"{_kind_words(beast)}, {might}, Size {beast.size:+d}"


def _beast_body(saga: Saga, beast: Beast, year: int) -> str:
    lines: list[str] = []
    if mg.is_young(beast, year) and mg.is_magical(beast):
        lines.append(
            f"Might {beast.might} when grown; {beast.might} / {beast.maturity} now "
            f"(a {beast.maturity}-year beast, {HP} p. 134)."
        )
    record = mg.taming_record(saga, beast)
    if record is not None and not record.done and record.points:
        lines.append(
            f"{_name(saga, beast.tamer_id)}: {record.points} taming points of "
            f"{mg.taming_might(beast, year)} so far"
            + (
                f", last in {record.last_season} {record.last_year}."
                if record.last_year is not None
                else "."
            )
        )
    for brand in beast.brands:
        lines.append(f"Brand: {brand}")
    if beast.note:
        lines.append(beast.note)
    return "\n".join(escape(line) for line in lines)


def beasts_ledger(saga: Saga, holder: Neighbour) -> list[LedgerEntry]:
    project = shown(saga, holder)
    if project is None:
        return []
    year = saga.current_year
    entries: list[LedgerEntry] = []
    for beast in project.beasts:
        state = mg.state(saga, beast, year)
        entries.append(
            LedgerEntry(
                title=beast.name or "(unnamed)",
                rubric={MALE: "♂", FEMALE: "♀"}.get(beast.sex, "⚥"),
                meta=_beast_meta(beast, year),
                badge=state.words,
                tone=state.tone,
                body=_beast_body(saga, beast, year),
                subtitle=f"{beast.kind} · {_beast_meta(beast, year)}",
            )
        )
    return entries


def beast_info(saga: Saga, holder: Neighbour, index: int) -> str:
    project = shown(saga, holder)
    if project is None or index >= len(project.beasts):
        return ""
    beast = project.beasts[index]
    year = saga.current_year
    state = mg.state(saga, beast, year)
    head = (
        f"{escape(beast.kind)}  ·  {escape(_beast_meta(beast, year))}  ·  "
        f"{escape(beast.sex)}, {beast.diet}  ·  {_coloured(state.words, state.tone)}"
    )
    lines = [head]
    body = _beast_body(saga, beast, year)
    if body:
        lines.append(body)
    creature = saga.creature(beast.creature_id) if beast.creature_id else None
    if creature is not None:
        lines.append(f"In the Bestiary: {escape(creature.name)}.")
    if not beast.cunning:
        lines.append(
            "[dim]Intelligent, not Cunning: it can't be tamed, only befriended "
            f"({HP} p. 135).[/]"
        )
    points = mg.inhabitant_points(beast)
    lines.append(
        f"[dim]Upkeep {points} Inhabitants points ({HP} p. 123); tending as "
        f"{mg.tending_load(saga, beast)} tame herbivores (p. 136).[/]"
    )
    return "\n".join(lines)


# -- the breedings -------------------------------------------------------------


def _breeding_tone(breeding: Breeding) -> str:
    if breeding.botches:
        return "text-error"
    return "text-success" if breeding.young else "text-error"


def breedings_title(saga: Saga, holder: Neighbour) -> str:
    project = shown(saga, holder)
    return f"Breedings ({len(project.breedings) if project is not None else 0})"


def _roll_words(breeding: Breeding) -> str:
    if breeding.botches:
        return f"botch ({breeding.botches})"
    return f"{breeding.total} vs {mg.BREEDING_EASE}"


def _pair_words(breeding: Breeding) -> str:
    aim = {"best": ", for the best", "beast": ", for the beast"}.get(breeding.aim, "")
    return f"{breeding.pair or '(a pair)'}{aim}"


def breedings_grid(saga: Saga, holder: Neighbour) -> Grid:
    project = shown(saga, holder)
    found = project.breedings if project is not None else []
    rows = [
        [
            f"{b.season} {b.year}",
            _pair_words(b),
            _roll_words(b),
            b.result or "–",
        ]
        for b in found
    ]
    styles = {(i, 3): f"${_breeding_tone(b)}" for i, b in enumerate(found)}
    return Grid(
        ["Season", "Pair", "Roll", "Result"],
        rows,
        list(range(len(found))),
        "No breedings yet: Add breeds a pair.",
        styles=styles,
        caps=[12, 30, 12],
    )


def breedings_ledger(saga: Saga, holder: Neighbour) -> list[LedgerEntry]:
    project = shown(saga, holder)
    if project is None:
        return []
    return [
        LedgerEntry(
            title=_pair_words(b),
            rubric="§",
            meta=f"{b.season} {b.year}",
            badge=b.result or "–",
            tone=_breeding_tone(b),
            body=escape(_roll_words(b)),
            note=escape(b.note),
            subtitle=f"{b.season} {b.year}",
        )
        for b in project.breedings
    ]


def breeding_info(saga: Saga, holder: Neighbour, index: int) -> str:
    project = shown(saga, holder)
    if project is None or index >= len(project.breedings):
        return ""
    breeding = project.breedings[index]
    lines = [
        f"{escape(_pair_words(breeding))}  ·  {breeding.season} {breeding.year}  ·  "
        f"{_coloured(breeding.result or '–', _breeding_tone(breeding))}"
    ]
    if breeding.details:
        lines.append(escape(breeding.details))
    if breeding.note:
        lines.append(f"[i]{escape(breeding.note)}[/]")
    return "\n".join(lines)


# -- the project's form: the menagerie's own fields ----------------------------


def _people_options(saga: Saga, covenant: Covenant) -> list[tuple[str, str]]:
    people = [c for c in saga.characters if c.covenant_id == covenant.id]
    return [
        (escape(f"{c.name} ({c.type})"), c.id)
        for c in sorted(people, key=lambda c: c.name.casefold())
    ]


def _is_menagerie(values: dict[str, Any]) -> bool:
    return values.get("kind") == MENAGERIE


def project_fields(
    saga: Saga, covenant: Covenant, project: HermeticProject | None
) -> list[DialogField]:
    """A Menagerie's own fields on the project's form: its handlers, its
    owner and the Reputation it earns him."""
    people = _people_options(saga, covenant)
    handlers = list(project.handler_ids) if project is not None else []
    fields = [
        DialogField(
            f"handler_{i}",
            "Lead handler" if i == 0 else "Handler",
            "select",
            handlers[i] if i < len(handlers) else None,
            options=people,
            allow_blank=True,
            placeholder="(none)",
            show_if=_is_menagerie,
            hint=(
                "Each tends 10 tame herbivores per point of Animal Handling "
                f"({HP} p. 136); the lead handler helps the breeding."
                if i == 0
                else ""
            ),
        )
        for i in range(HANDLER_FIELDS)
    ]
    fields += [
        DialogField(
            "owner_id",
            "Owner",
            "select",
            (project.owner_id if project else "") or None,
            options=people,
            allow_blank=True,
            placeholder="(none)",
            show_if=_is_menagerie,
        ),
        DialogField(
            "reputation",
            "His Reputation",
            "text",
            project.reputation if project else "",
            placeholder="Keeper of Beasts",
            show_if=_is_menagerie,
            hint="The owner's Reputation, built by the storyguide's experience "
            f"points: visitors, beasts caught and sold, years ({HP} p. 138).",
        ),
    ]
    return fields


def write_project(project: HermeticProject, values: dict[str, Any]) -> None:
    """The menagerie's fields, when the project is a Menagerie."""
    if project.kind != MENAGERIE:
        return
    chosen = [values.get(f"handler_{i}") or "" for i in range(HANDLER_FIELDS)]
    project.handler_ids = list(dict.fromkeys(h for h in chosen if h))
    project.owner_id = values.get("owner_id") or ""
    project.reputation = values.get("reputation") or ""


# -- beasts: Add and Edit ------------------------------------------------------


def _creature_fills(saga: Saga) -> Callable[[dict[str, Any]], dict[str, Any]]:
    """Choosing a Bestiary creature fills its Might, Form, Size and
    Cunning."""

    def fills(values: dict[str, Any]) -> dict[str, Any]:
        creature = saga.creature(values.get("creature_id"))
        if creature is None:
            return {}
        filled: dict[str, Any] = {
            "might": max(0, creature.might),
            "size": creature.size,
            "cunning": creature.cunning,
        }
        if creature.might_form in FORMS:
            filled["form"] = creature.might_form
        if not values.get("breed"):
            filled["breed"] = creature.name
        return filled

    return fills


def beast_fields(saga: Saga, beast: Beast | None) -> list[DialogField]:
    creatures = sorted(
        (c for c in saga.creatures if c.realm in ("", "Magic") or c.might),
        key=lambda c: c.name.casefold(),
    )
    return [
        DialogField("name", "Name", "text", beast.name if beast else "", required=True),
        DialogField(
            "kind",
            "Kind",
            "select",
            beast.kind if beast else BEAST_KINDS[0],
            options=pairs(BEAST_KINDS),
            hint=f"A Transformed Animal has no Might and never breeds true ({HP} "
            "p. 124).",
        ),
        DialogField(
            "creature_id",
            "In the Bestiary",
            "select",
            (beast.creature_id if beast else "") or None,
            options=[(escape(c.name), c.id) for c in creatures],
            allow_blank=True,
            placeholder="(not in the Bestiary)",
            fills=_creature_fills(saga),
        ),
        DialogField(
            "animal",
            "Animal",
            "text",
            beast.animal if beast else "",
            placeholder="Goat",
            hint=f"Its kind (lions, horses), which holds several breeds ({HP} p. 131).",
        ),
        DialogField(
            "breed",
            "Breed",
            "text",
            beast.breed if beast else "",
            placeholder="Goat of Virtue",
            hint="A realia counts breeds, not beasts (HP p. 123).",
        ),
        DialogField("might", "Magic Might (grown)", "int", beast.might if beast else 0),
        DialogField(
            "form",
            "Its Form",
            "select",
            beast.form if beast else "Animal",
            options=pairs(FORMS),
        ),
        DialogField("size", "Size", "int", beast.size if beast else 0),
        DialogField(
            "cunning",
            "Cunning (can be tamed)",
            "check",
            beast.cunning if beast else True,
        ),
        DialogField(
            "sex", "Sex", "select", beast.sex if beast else FEMALE, options=pairs(SEXES)
        ),
        DialogField("count", "How many", "int", beast.count if beast else 1),
        DialogField(
            "diet",
            "Diet",
            "select",
            beast.diet if beast else DIETS[0],
            options=pairs(DIETS),
        ),
        DialogField("tamed", "Tamed", "check", beast.tamed if beast else False),
        DialogField(
            "born",
            "Born (year)",
            "optint",
            beast.born if beast else None,
            hint="Blank for a beast grown; a young one's Might is its grown Might / "
            f"its years to grow ({HP} p. 134).",
        ),
        DialogField(
            "maturity",
            "Years to grow",
            "int",
            beast.maturity if beast else MATURITY_YEARS,
        ),
        DialogField(
            "ferocity",
            "Ferocity",
            "int",
            beast.ferocity if beast else 0,
            hint=f"An aggressive beast's, off the Breeding Roll ({HP} p. 140).",
        ),
        DialogField(
            "brands",
            "Brands",
            "area",
            "\n".join(beast.brands) if beast else "",
            hint="One a line. A brand is a device of material 2 x 2 (a palm), 3 (a "
            f"haunch) or 4 (the back) ({HP} p. 130).",
        ),
        DialogField("note", "Note", "text", beast.note if beast else ""),
    ]


def validate_beast(values: dict[str, Any]) -> str | None:
    if (values.get("might") or 0) < 0:
        return "Might is 0 or more."
    if values.get("kind") == TRANSFORMED and (values.get("might") or 0) > 0:
        return f"A Transformed Animal has no Magic Might ({HP} p. 124)."
    if (values.get("count") or 0) < 1:
        return "A row holds at least one beast."
    if (values.get("maturity") or 0) < 1:
        return "A beast takes a year or more to grow."
    if (values.get("ferocity") or 0) < 0:
        return "Ferocity is 0 or more."
    return None


def _write_beast(beast: Beast, values: dict[str, Any]) -> None:
    beast.name = values["name"]
    beast.kind = values.get("kind") or BEAST_KINDS[0]
    beast.creature_id = values.get("creature_id") or ""
    beast.animal = values.get("animal") or ""
    beast.breed = values.get("breed") or ""
    beast.might = values.get("might") or 0
    beast.form = values.get("form") or "Animal"
    beast.size = values.get("size") or 0
    beast.cunning = bool(values.get("cunning"))
    beast.sex = values.get("sex") or FEMALE
    beast.count = values.get("count") or 1
    beast.diet = values.get("diet") or DIETS[0]
    beast.tamed = bool(values.get("tamed"))
    beast.born = values.get("born")
    beast.maturity = values.get("maturity") or MATURITY_YEARS
    beast.ferocity = values.get("ferocity") or 0
    beast.brands = [
        line.strip()
        for line in (values.get("brands") or "").splitlines()
        if line.strip()
    ]
    beast.note = values.get("note") or ""


def beast_form(saga: Saga, project: HermeticProject, beast: Beast | None) -> Form:
    def apply(values: dict[str, Any]) -> None:
        if beast is not None:
            _write_beast(beast, values)
            return
        made = Beast()
        _write_beast(made, values)
        project.beasts.append(made)

    return Form(
        "Edit Beast" if beast is not None else "Add Beast",
        lambda: beast_fields(saga, beast),
        apply,
        validate=validate_beast,
        help_id=BEASTS_SECTION,
    )


def beasts_ops(saga: Saga, holder: Neighbour) -> SectionOps:
    def project() -> HermeticProject | None:
        return shown(saga, holder)

    def add() -> Command:
        found = project()
        if found is None:
            return Refuse("Add Beast", "Show a menagerie first.")
        return beast_form(saga, found, None)

    def edit(index: int) -> Command:
        found = project()
        if found is None or index >= len(found.beasts):
            return Refuse("Edit Beast", "Choose a beast first.")
        return beast_form(saga, found, found.beasts[index])

    def remove(index: int) -> Command:
        found = project()
        if found is None or index >= len(found.beasts):
            return Refuse("Delete", "Choose a beast first.")
        beast = found.beasts[index]
        return Confirm(
            f"Delete {escape(beast.name or 'this beast')}?",
            lambda: found.beasts.remove(beast),
        )

    def rows() -> list[str]:
        found = project()
        return [b.name or "(unnamed)" for b in found.beasts] if found else []

    return SectionOps(add=add, edit=edit, remove=remove, rows=rows)


# -- breedings: Breed a Pair (Add) and Edit ------------------------------------


def _sires(project: HermeticProject) -> list[Beast]:
    return [b for b in project.beasts if b.sex in (MALE, BOTH)]


def _dams(project: HermeticProject) -> list[Beast]:
    return [b for b in project.beasts if b.sex in (FEMALE, BOTH)]


def _beast_label(beast: Beast, year: int) -> str:
    might = f", Might {mg.might_now(beast, year)}" if mg.is_magical(beast) else ""
    return escape(f"{beast.name}, {beast.breed or beast.kind}{might}")


def _handler_label(character: Character) -> str:
    return escape(
        f"{character.name} (Animal Handling "
        f"{ability_level(character, mg.ANIMAL_HANDLING)}, Magic Lore "
        f"{ability_level(character, mg.MAGIC_LORE)})"
    )


def breed_fields(
    saga: Saga, covenant: Covenant, project: HermeticProject
) -> list[DialogField]:
    year = saga.current_year
    sires, dams = _sires(project), _dams(project)
    handlers = mg.handlers(saga, project)
    first_sire = sires[0] if sires else None
    first_dam = next((d for d in dams if d is not first_sire), None)
    only = (
        mg.only_of_kind(project, first_sire, first_dam)
        if first_sire is not None and first_dam is not None
        else False
    )
    people = [
        (_handler_label(c), c.id)
        for c in sorted(
            [c for c in saga.characters if c.covenant_id == covenant.id],
            key=lambda c: c.name.casefold(),
        )
    ]
    return [
        DialogField(
            "sire",
            "Male",
            "select",
            first_sire.id if first_sire else None,
            options=[(_beast_label(b, year), b.id) for b in sires],
            required=True,
        ),
        DialogField(
            "dam",
            "Female",
            "select",
            first_dam.id if first_dam else None,
            options=[(_beast_label(b, year), b.id) for b in dams],
            required=True,
        ),
        DialogField(
            "aim",
            "Breeding",
            "select",
            YOUNG,
            options=[(AIM_LABELS[a], a) for a in AIMS],
        ),
        DialogField(
            "diet",
            "Diet",
            "select",
            "1",
            options=[
                ("Adequate (+1)", "1"),
                ("Ordinary (0)", "0"),
                ("Inadequate (−2)", "-2"),
            ],
        ),
        DialogField(
            "environment",
            "Environment",
            "select",
            "1",
            options=[
                ("Agreeable (+1)", "1"),
                ("Ordinary (0)", "0"),
                ("Unsatisfactory (−2)", "-2"),
            ],
        ),
        DialogField("similar", "Similar animals near (+1)", "check", False),
        DialogField(
            "only",
            "The only pair of their kind (−3)",
            "check",
            only,
            hint="Ticked when no other beast of their animal, of any breed, is "
            f"kept ({HP} pp. 131, 141).",
        ),
        DialogField(
            "spell",
            "Hermetic spell (magnitudes)",
            "int",
            0,
            hint="+1 per 2 magnitudes to the Breeding Roll, +1 a magnitude to the "
            "young's.",
        ),
        DialogField(
            "ligature",
            "Ligature (0 to +3)",
            "int",
            0,
            hint="To the young's roll only (Art & Academe p. 68).",
        ),
        DialogField(
            "handler",
            "Lead handler",
            "select",
            handlers[0].id if handlers else None,
            options=people,
            allow_blank=True,
            placeholder="(none)",
        ),
        DialogField(
            "young",
            "Young, if they breed",
            "int",
            1,
            hint="As many as suit the kind of beast (HP p. 140).",
        ),
        DialogField("keep", "Add the young to Beasts", "check", True),
        DialogField(
            "season", "Season", "select", saga.current_season, options=pairs(SEASONS)
        ),
        DialogField("year", "Year", "int", year),
    ]


def _pair(
    project: HermeticProject, values: dict[str, Any]
) -> tuple[Beast | None, Beast | None]:
    return _beast(project, values.get("sire") or ""), _beast(
        project, values.get("dam") or ""
    )


def _conditions(saga: Saga, values: dict[str, Any]) -> mg.Conditions:
    return mg.Conditions(
        diet=int(values.get("diet") or 0),
        environment=int(values.get("environment") or 0),
        spell=max(0, values.get("spell") or 0),
        similar=bool(values.get("similar")),
        only_pair=bool(values.get("only")),
        ligature=values.get("ligature") or 0,
        handler=saga.character(values.get("handler")),
    )


def _signed(mods: list[tuple[str, int]]) -> str:
    return " ".join(f"{n:+d} {escape(words)}" for words, n in mods)


def breed_live(saga: Saga, project: HermeticProject) -> Callable[[dict[str, Any]], str]:
    def live(values: dict[str, Any]) -> str:
        sire, dam = _pair(project, values)
        if sire is None or dam is None:
            return "Choose a male and a female."
        if sire is dam and sire.count < 2:
            return "[$text-error]A beast can't be bred with itself.[/]"
        year = values.get("year") or saga.current_year
        conditions = _conditions(saga, values)
        mods = mg.breeding_modifiers(saga, sire, dam, conditions, year)
        total = mg.total_of(mods)
        lines = [
            f"[b]Breeding Roll:[/] stress die {_signed(mods)} = [b]die {total:+d}[/] "
            f"against {mg.BREEDING_EASE}: the die must show "
            f"{max(1, mg.BREEDING_EASE - total)} or more.",
            "Botch: one escapes (1), is sterile (2), is hurt mating (3+).",
        ]
        handler = conditions.handler
        hand = ability_level(handler, mg.ANIMAL_HANDLING) if handler else 0
        lines.append(
            f"Birth: the dam rolls as for a Medium Wound every "
            f"{mg.birth_interval(dam.size)} hours"
            + (f", + {escape(handler.name)}'s {hand}" if handler and hand else "")
            + " (Art & Academe p. 62; HP p. 134); a hatchling rolls Stamina + "
            "Survival + stress die against 9."
        )
        aim = values.get("aim") or YOUNG
        if aim != YOUNG:
            young = mg.offspring_modifiers(dam, aim, conditions)
            table = (
                "botch a Major Flaw; 0 a Minor Flaw; 1-3 weak; 4-12 like its "
                "parents; 13-15 hardy; 16-17 a Minor Virtue or Quality; 18+ a Major one"
                if aim == "best"
                else "botch dies; 0 weaker than its sire; 1-12 like its sire; 13 like "
                "its dam; 14 the sire plus a Minor Virtue of the dam's; 15+ a Major one"
            )
            lines.append(
                f"[b]{escape(AIM_LABELS[aim])}[/]: stress die "
                f"{_signed(young) or '+0'} = die {mg.total_of(young):+d}: {table}."
            )
        if not (mg.is_magical(sire) and mg.is_magical(dam)):
            lines.append(
                "Only one parent magical: a magical young is exceptionally rare "
                f"({HP} p. 134)."
            )
        lines.append(
            f"[dim]Optional rules, {HP} pp. 140-142. Most young take the sire's "
            "Virtues (p. 132).[/]"
        )
        return "\n".join(lines)

    return live


def validate_breeding(
    project: HermeticProject,
) -> Callable[[dict[str, Any]], str | None]:
    def check(values: dict[str, Any]) -> str | None:
        sire, dam = _pair(project, values)
        if sire is None or dam is None:
            return "Choose a male and a female."
        if sire is dam and sire.count < 2:
            return "A beast can't be bred with itself."
        if not 0 <= (values.get("ligature") or 0) <= mg.LIGATURE_CAP:
            return "A ligature gives +1 to +3 (Art & Academe p. 68)."
        if (values.get("spell") or 0) < 0 or (values.get("young") or 0) < 0:
            return "A spell's magnitudes and the young are 0 or more."
        return None

    return check


def _young_beast(
    sire: Beast,
    dam: Beast,
    sex: str,
    year: int,
    number: int,
    result: mg.Inherited | None,
) -> Beast:
    like = dam if result is not None and result.like_dam else sire
    magical = mg.is_magical(sire) and mg.is_magical(dam)
    return Beast(
        name=f"{dam.name}'s young {number}",
        kind=like.kind,
        animal=like.animal,
        breed=like.breed,
        might=like.might if magical else 0,
        form=like.form,
        size=like.size,
        cunning=like.cunning,
        sex=sex,
        diet=like.diet,
        born=year,
        maturity=like.maturity,
        cross_bonus=bool(result is not None and result.like_dam and sex == FEMALE),
        note=f"Born {year} of {sire.name} and {dam.name}"
        + (f": {result.words}." if result is not None else "."),
    )


def breed_form(
    saga: Saga, covenant: Covenant, rng: random.Random | None = None
) -> Command:
    """Breed a Pair (the Breedings list's Add): the Breeding Roll, then
    each young's sex and, for the best or the beast, its offspring roll;
    kept as a breeding, the young added to the beasts (HP pp. 140-142)."""
    project = hp.shown_project(covenant)
    if project is None or project.kind != MENAGERIE:
        return Refuse(BREED_PAIR, "Show a menagerie first.")
    if not _sires(project) or not _dams(project):
        return Refuse(BREED_PAIR, "The menagerie needs a male and a female.")

    def apply(values: dict[str, Any]) -> list[str]:
        roller = rng or random.Random()
        sire, dam = _pair(project, values)
        if sire is None or dam is None:
            return ["Choose a male and a female."]
        season = values.get("season") or saga.current_season
        year = values.get("year") or saga.current_year
        aim = values.get("aim") or YOUNG
        conditions = _conditions(saga, values)
        mods = mg.breeding_modifiers(saga, sire, dam, conditions, year)
        die = dice.stress_die(roller, saga=saga)
        roll = dice.Roll(mg.total_of(mods), die, mg.BREEDING_EASE)
        shown_die = (
            f"a botch ({die.botches})" if die.botched else f"stress die {die.value}"
        )
        details = [
            f"{shown_die.capitalize()} {_signed(mods)} = {roll.total} against "
            f"{mg.BREEDING_EASE}."
        ]
        made: list[Beast] = []
        if die.botched and die.botches:
            result = f"Botch: {mg.breeding_botch(die.botches)}"
        elif not roll.succeeded:
            result = "No young"
        else:
            count = max(0, values.get("young") or 0)
            words: list[str] = []
            for number in range(1, count + 1):
                sex = mg.young_sex(dice.simple_die(roller))
                inherited: mg.Inherited | None = None
                if aim != YOUNG:
                    young_mods = mg.offspring_modifiers(dam, aim, conditions)
                    young_die = dice.stress_die(roller, saga=saga)
                    young_roll = dice.Roll(mg.total_of(young_mods), young_die)
                    inherited = mg.inherited(aim, young_roll.total, young_die.botched)
                    details.append(
                        f"Young {number} ({sex}): "
                        + (
                            f"a botch ({young_die.botches})"
                            if young_die.botched
                            else f"stress die {young_die.value}"
                        )
                        + f" {_signed(young_mods)} = {young_roll.total}: "
                        f"{inherited.words if inherited else ''}."
                    )
                else:
                    details.append(f"Young {number}: {sex}.")
                words.append(sex)
                if inherited is not None and inherited.dies:
                    continue
                made.append(_young_beast(sire, dam, sex, year, number, inherited))
            result = (
                f"{_plural(count, 'young')}: " + ", ".join(words) if count else "Bred"
            )
        pair = f"{sire.name} × {dam.name}"
        project.breedings.append(
            Breeding(
                season=season,
                year=year,
                sire_id=sire.id,
                dam_id=dam.id,
                pair=pair,
                aim=aim,
                total=roll.total,
                botches=die.botches if die.botched else 0,
                young=len(made),
                result=result,
                details=" ".join(details),
            )
        )
        if values.get("keep"):
            project.beasts += made
        return notes(
            " ".join(details),
            f"{pair}: {result}.",
            f"{_plural(len(made), 'young')} added to Beasts; each must survive "
            "its birth (HP p. 134)."
            if made and values.get("keep")
            else "",
        )

    return Form(
        BREED_PAIR,
        lambda: breed_fields(saga, covenant, project),
        apply,
        validate=validate_breeding(project),
        live=breed_live(saga, project),
        save_label="Roll",
        inspector="The Season's Breeding",
        help_id=BREEDINGS_SECTION,
    )


def breeding_fields(saga: Saga, breeding: Breeding) -> list[DialogField]:
    """A breeding as kept: its season, its pair and what came of it."""
    return [
        DialogField("pair", "Pair", "text", breeding.pair, required=True),
        DialogField(
            "aim",
            "Breeding",
            "select",
            breeding.aim,
            options=[(AIM_LABELS[a], a) for a in AIMS],
        ),
        DialogField(
            "season", "Season", "select", breeding.season, options=pairs(SEASONS)
        ),
        DialogField("year", "Year", "int", breeding.year),
        DialogField("total", "Breeding Roll", "int", breeding.total),
        DialogField("result", "Result", "text", breeding.result),
        DialogField("young", "Young born", "int", breeding.young),
        DialogField("details", "The rolls", "area", breeding.details),
        DialogField("note", "Note", "text", breeding.note),
    ]


def edit_breeding_form(saga: Saga, breeding: Breeding) -> Form:
    def apply(values: dict[str, Any]) -> None:
        breeding.pair = values["pair"]
        breeding.aim = values.get("aim") or YOUNG
        breeding.season = values.get("season") or "Spring"
        breeding.year = values["year"]
        breeding.total = values.get("total") or 0
        breeding.result = values.get("result") or ""
        breeding.young = values.get("young") or 0
        breeding.details = values.get("details") or ""
        breeding.note = values.get("note") or ""

    def validate(values: dict[str, Any]) -> str | None:
        if (values.get("young") or 0) < 0:
            return "Young born is 0 or more."
        return None

    return Form(
        "Edit Breeding",
        lambda: breeding_fields(saga, breeding),
        apply,
        validate=validate,
        help_id=BREEDINGS_SECTION,
    )


def breedings_ops(saga: Saga, holder: Neighbour) -> SectionOps:
    def project() -> HermeticProject | None:
        return shown(saga, holder)

    def add() -> Command:
        covenant = covenant_of(saga, holder)
        if covenant is None:
            return Refuse(BREED_PAIR, "Show a menagerie first.")
        return breed_form(saga, covenant)

    def edit(index: int) -> Command:
        found = project()
        if found is None or index >= len(found.breedings):
            return Refuse("Edit Breeding", "Choose a breeding first.")
        return edit_breeding_form(saga, found.breedings[index])

    def remove(index: int) -> Command:
        found = project()
        if found is None or index >= len(found.breedings):
            return Refuse("Delete", "Choose a breeding first.")
        breeding = found.breedings[index]
        return Confirm(
            f"Delete the breeding of {escape(breeding.pair or 'this pair')}?",
            lambda: found.breedings.remove(breeding),
        )

    def rows() -> list[str]:
        found = project()
        return [_pair_words(b) for b in found.breedings] if found else []

    return SectionOps(add=add, edit=edit, remove=remove, rows=rows)


# -- More: Tame a Beast --------------------------------------------------------


def _tamers(
    saga: Saga, covenant: Covenant, project: HermeticProject
) -> list[Character]:
    """Who may tame: the covenant's people, its handlers first."""
    people = [c for c in saga.characters if c.covenant_id == covenant.id]
    first = set(project.handler_ids)
    return sorted(people, key=lambda c: (c.id not in first, c.name.casefold()))


def _method(character: Character) -> str:
    if character.type == "magus":
        return "a Rego lab season"
    if activities.is_planned(character):
        return "a season's taming"
    return "a season, kept now"


def tame_plan(
    saga: Saga, character: Character, beast: Beast, season: str, year: int
) -> SeasonPlan:
    """The tamer's season taming the beast: a magus's in his laboratory
    (Rego + its Form), anyone else's by Animal Handling (DE pp. 384-385)."""
    might = mg.taming_might(beast, year)
    if character.type == "magus":
        return SeasonPlan(
            character_id=character.id,
            year=year,
            season=season,
            activity=lab_seasons.TAMING,
            lab_id=character.assigned_lab_id,
            title=beast.name,
            form=beast.form,
            book_level=might,
        )
    return SeasonPlan(
        character_id=character.id,
        year=year,
        season=season,
        activity=TAME_ANIMAL,
        title=beast.name,
        book_level=might,
        # Its Exposure goes into Animal Handling.
        allocations=[XpAllocation(activities.ability_subject(mg.ANIMAL_HANDLING), 0)],
    )


def unplanned_points(
    saga: Saga, character: Character, beast: Beast, year: int
) -> tuple[int, str]:
    """A grog's season taming the beast (he plans no seasons), as a
    taming season works it out: Int (Magic Lore for a Master of Creatures)
    + Animal Handling + Animal Ken - its Might - the Gift's penalty (DE
    pp. 384-385). The points and how they were found."""
    might = mg.taming_might(beast, year)
    master = master_of_creatures(character)
    if master is not None:
        base, label = ability_level(character, mg.MAGIC_LORE), "Magic Lore"
    else:
        base, label = character.characteristics.intelligence, "Int"
    handling = ability_level(character, mg.ANIMAL_HANDLING)
    ken = ability_level(character, "Animal Ken")
    gift = gift_penalty(character)
    points = max(0, base + handling + ken - might - gift)
    words = (
        f"{label} {base} + Animal Handling {handling}"
        + (f" + Animal Ken {ken}" if ken else "")
        + f" − Might {might}"
        + (f" − the Gift {gift}" if gift else "")
        + f" = {points}"
    )
    return points, words


def _planned_points(
    saga: Saga, character: Character, plan: SeasonPlan
) -> tuple[int, str, list[str]]:
    """A planned taming season's points, its arithmetic and its problems
    (rules.activities.outcome, as the season will be worked out)."""
    worked = activities.outcome(character, plan, saga)
    if worked.problems:
        return 0, "", worked.problems
    work = worked.lab_work
    if work is not None:
        total = int(work.lab_total.total)
        return (
            work.points_gained,
            f"Rego {escape(plan.form)} Lab Total {total} − Might "
            f"{plan.book_level} = {work.points_gained}",
            [],
        )
    supplement = worked.supplement
    if supplement is not None and supplement.progress:
        _kind, _name, _target, points = supplement.progress[0]
        return points, escape(supplement.notes[-1] if supplement.notes else ""), []
    return 0, "", ["Nothing to gain."]


def _so_far(
    saga: Saga, character: Character, beast: Beast, season: str, year: int
) -> int:
    record = next(
        (
            p
            for p in character.progress
            if p.kind == "taming" and p.name == beast.name and not p.done
        ),
        None,
    )
    return kept_points(record, season, year)


def tame_fields(
    saga: Saga, covenant: Covenant, project: HermeticProject, beast: Beast
) -> list[DialogField]:
    tamers = _tamers(saga, covenant, project)
    current = beast.tamer_id if beast.tamer_id in {c.id for c in tamers} else None
    return [
        DialogField(
            "who",
            "Tamed by",
            "select",
            current or (tamers[0].id if tamers else None),
            options=[(escape(f"{c.name}: {_method(c)}"), c.id) for c in tamers],
            required=True,
        ),
        DialogField(
            "season", "Season", "select", saga.current_season, options=pairs(SEASONS)
        ),
        DialogField("year", "Year", "int", saga.current_year),
    ]


def _working(
    saga: Saga, beast: Beast, values: dict[str, Any]
) -> tuple[Character | None, int, str, list[str], str, int]:
    """The chosen tamer's season: who, the points, their arithmetic, what
    stops it, the season and year."""
    character = saga.character(values.get("who"))
    season = values.get("season") or saga.current_season
    year = values.get("year") or saga.current_year
    if character is None:
        return None, 0, "", ["Choose who tames it."], season, year
    if not activities.is_planned(character):
        points, words = unplanned_points(saga, character, beast, year)
        return character, points, words, [], season, year
    plan = tame_plan(saga, character, beast, season, year)
    problems: list[str] = []
    if character.type == "magus" and not character.assigned_lab_id:
        problems.append(f"{character.name} has no laboratory to tame it in.")
    existing = plan_for(saga, character, season, year)
    if existing is not None:
        problems.append(
            f"{character.name} already has a plan for {season} {year}: change it "
            "on his Seasons."
        )
    if problems:
        return character, 0, "", problems, season, year
    points, words, found = _planned_points(saga, character, plan)
    return character, points, words, found, season, year


def tame_live(saga: Saga, beast: Beast) -> Callable[[dict[str, Any]], str]:
    def live(values: dict[str, Any]) -> str:
        character, points, words, problems, season, year = _working(saga, beast, values)
        might = mg.taming_might(beast, year)
        if character is None or problems:
            return "\n".join(f"[$text-error]{escape(p)}[/]" for p in problems)
        before = _so_far(saga, character, beast, season, year)
        after = before + points
        done = after >= might
        lines = [
            f"{words}: [b]{points}[/] taming points." if words else f"{points} points.",
            f"Points so far {before} → [b]{after}[/] of {might}: "
            + ("[$text-success]tamed[/]" if done else "[$text-warning]not yet[/]"),
            "Points last only over consecutive seasons, and stay with their tamer "
            "(DE p. 384).",
        ]
        if mg.is_young(beast, year):
            lines.append(f"Young, so tamed at Might {might} ({HP} p. 134).")
        lines.append(
            "[dim]"
            + (
                f"Plan saves {escape(character.name)}'s season; it is worked out "
                "when the season is played."
                if activities.is_planned(character)
                else f"Plan keeps {escape(character.name)}'s season now: a grog "
                "plans no seasons."
            )
            + f" RoP: Magic pp. 81-82, as {HP} p. 135 gives it; DE pp. 384-385.[/]"
        )
        return "\n".join(lines)

    return live


def tame_form(saga: Saga, covenant: Covenant, index: int | None) -> Command:
    """More's Tame a Beast on the chosen beast: plans the tamer's taming
    season (a magus's in his laboratory), or keeps a grog's season now."""
    project = hp.shown_project(covenant)
    if project is None or project.kind != MENAGERIE:
        return Refuse(TAME_BEAST, "Show a menagerie first.")
    if index is None or not 0 <= index < len(project.beasts):
        return Refuse(TAME_BEAST, "Choose a beast first.")
    beast = project.beasts[index]
    if mg.is_tamed(saga, beast):
        return Refuse(TAME_BEAST, f"{beast.name} is tamed already.")
    if not beast.cunning:
        return Refuse(
            TAME_BEAST,
            f"Only beasts with Cunning can be tamed; {beast.name} is Intelligent "
            f"and must be befriended ({HP} p. 135).",
        )

    def validate(values: dict[str, Any]) -> str | None:
        _who, _points, _words, problems, _season, _year = _working(saga, beast, values)
        return problems[0] if problems else None

    def apply(values: dict[str, Any]) -> list[str]:
        character, points, words, problems, season, year = _working(saga, beast, values)
        if character is None or problems:
            return problems
        beast.tamer_id = character.id
        if activities.is_planned(character):
            set_plan(saga, tame_plan(saga, character, beast, season, year))
            return notes(
                f"{character.name} will spend {season} {year} taming {beast.name}: "
                f"{words}."
            )
        might = mg.taming_might(beast, year)
        record = next(
            (
                p
                for p in character.progress
                if p.kind == "taming" and p.name == beast.name and not p.done
            ),
            None,
        )
        if record is None:
            record = Progress("taming", beast.name, might)
            character.progress.append(record)
        record.points = kept_points(record, season, year) + points
        record.last_season, record.last_year = season, year
        record.target = might
        record.done = record.points >= might
        return notes(
            f"{words}: {record.points} of {might}.",
            f"{beast.name} is tamed." if record.done else "",
        )

    return Form(
        f"{TAME_BEAST}: {escape(beast.name)}",
        lambda: tame_fields(saga, covenant, project, beast),
        apply,
        validate=validate,
        live=tame_live(saga, beast),
        save_label="Plan",
        inspector="Taming",
        help_id=BEASTS_SECTION,
    )


# -- the tab's pieces ----------------------------------------------------------


BEASTS_LIST = KindList(
    BEASTS_SECTION,
    beasts_title,
    beasts_grid,
    beasts_ops,
    beast_info,
    ledger=beasts_ledger,
)
BREEDINGS_LIST = KindList(
    BREEDINGS_SECTION,
    breedings_title,
    breedings_grid,
    breedings_ops,
    breeding_info,
    ledger=breedings_ledger,
)


def menagerie_block(
    saga: Saga,
    covenant: Covenant,
    edit: Callable[[Saga, Neighbour], Command],
    after: str,
) -> KindBlock:
    """The menagerie's facts and warnings, after the projects list; its
    Edit is the project's form (`edit`)."""
    return KindBlock(
        MENAGERIE_SECTION,
        menagerie_title(saga, covenant),
        block_text,
        edit,
        edit_label="Edit Project",
        after=after,
        facts=menagerie_facts,
        facts_inline=True,
    )


# -- the owner's Reputation (p. 138) -------------------------------------------

REPUTATION_AWARD = "Reputation Award"


def award_fields(saga: Saga, project: HermeticProject) -> list[DialogField]:
    return [
        DialogField(
            "visitors", "Visitors this year", "int", 0, hint="A point for ten."
        ),
        *(
            DialogField(
                f"captured_{beast.id}",
                f"Captured this year: {escape(beast.name)} (Might {beast.might})",
                "check",
                False,
            )
            for beast in project.beasts
            if beast.might > 0
        ),
        DialogField(
            "another_year",
            "Another year past its first",
            "check",
            saga.current_year > project.year,
        ),
        DialogField("sold", "Beasts sold to other magi", "int", 0),
    ]


def _award(project: HermeticProject, values: dict[str, Any]) -> int:
    mights = [b.might for b in project.beasts if values.get(f"captured_{b.id}")]
    return mg.reputation_award(
        int(values.get("visitors") or 0),
        mights,
        bool(values.get("another_year")),
        int(values.get("sold") or 0),
    )


def award_form(saga: Saga, covenant: Covenant, _index: int | None = None) -> Command:
    """More's Reputation Award on the menagerie's beasts: the year's
    experience toward its owner's Reputation, from the book's suggestions
    (HP p. 138), which the storyguide may change."""
    project = hp.shown_project(covenant)
    if project is None or project.kind != MENAGERIE:
        return Refuse(REPUTATION_AWARD, "Show a menagerie first.")
    owner = saga.character(project.owner_id) if project.owner_id else None
    if owner is None or not project.reputation.strip():
        return Refuse(
            REPUTATION_AWARD,
            "Name the menagerie's owner and his Reputation first (Edit Project).",
        )

    def live(values: dict[str, Any]) -> str:
        return (
            f"{_award(project, values)} experience toward {escape(owner.name)}'s "
            f"{escape(project.reputation)} (HP p. 138: the storyguide may "
            "fine-tune it)."
        )

    def apply(values: dict[str, Any]) -> list[str]:
        xp = _award(project, values)
        held = confidence.deed_toward(owner, project.reputation.strip(), xp)
        owner.diary.append(
            DiaryEntry(
                saga.current_year,
                saga.current_season,
                f"{REPUTATION_AWARD}: {project.name or 'the menagerie'}",
                f"{xp} experience toward {held.name}, now {held.score}.\n"
                "Rules: Hermetic Projects, Hermetic Relations, p. 138",
            )
        )
        return notes(
            f"{escape(held.name)} {held.score} ({held.deeds} xp toward the next)."
        )

    return Form(
        f"{REPUTATION_AWARD}: {escape(owner.name)}",
        lambda: award_fields(saga, project),
        apply,
        live=live,
        help_id="menagerie-reputation",
    )

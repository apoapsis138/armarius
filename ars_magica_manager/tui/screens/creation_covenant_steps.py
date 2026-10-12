"""The Creation Worksheet's covenant and laboratory steps.

A covenant: Baseline (Power Level, Build Points, season, aura and its
starting income), Resources (what its Build Points bought, by category),
Boons & Hooks, and Review. A laboratory: Setting Up, and Review. Each step
registers its StepPanel in creation_worksheet.PANELS, like the character
steps in creation_steps.
"""

from __future__ import annotations

from collections.abc import Callable
from functools import partial
from typing import TYPE_CHECKING, Any

from ... import books as bk
from ... import catalog
from ... import covenant_templates as templates
from ... import covenants as cov_rules
from ... import inhabitants as inh
from ... import laboratories as lab_rules
from ... import possessions as pos
from ...covenants import boon_hook_points, covenant_boon_points, covenant_hook_points
from ...markup import aligned, escape
from ...models import (
    INCOME_TYPE_DEFAULTS,
    Book,
    Covenant,
    EnchantedDevice,
    IncomeSource,
    Inhabitant,
    Laboratory,
    Possession,
    Saga,
    VirtueFlawInstance,
    new_instance_id,
)
from ...rules import creation_covenant as cov
from .creation_steps import _VF_NAME, _VF_TIER, VF_HEADER, pad, review_lines
from .creation_worksheet import (
    PANELS,
    Record,
    StepAction,
    StepList,
    StepPanel,
    StepRow,
)
from .forms import _enchanted_device_dialog
from .pickers import RemovalPickerScreen, SagaBookPickerScreen
from .prompts import ConfirmScreen, MenuScreen
from .widgets import boon_hook_info_text

if TYPE_CHECKING:
    from .workspace.screen import WorkspaceScreen


def _covenant(record: Record) -> Covenant:
    assert isinstance(record, Covenant)
    return record


# -- Baseline: Power Level, Build Points, season, aura, starting income --


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
_INCOME_NAME = 40
INCOME_HEADER = f"  {'Source of income':<{_INCOME_NAME}}{'Type':<11}{'Pounds':>7}"


def _income_pounds(source: IncomeSource) -> int:
    return (
        source.income
        if source.income is not None
        else INCOME_TYPE_DEFAULTS[source.type]
    )


def _income_rows(saga: Saga, record: Record) -> list[StepRow]:
    """The covenant's sources of income: e edits one, d deletes it."""
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
            StepRow(
                f"{pad(source.name or '(unnamed)', _INCOME_NAME)}{source.type:<11}"
                f"{_income_pounds(source):>7}"
                + (f"  [dim]{', '.join(flags)}[/]" if flags else ""),
                "\n".join(details),
                edit=lambda ws, s=source: ws._income_form(s),
                delete=lambda ws, s=source: ws._confirm_remove_income_source(s),
            )
        )
    return rows


def _set_starting_income(workspace: WorkspaceScreen, record: Record) -> None:
    """Start the covenant's income one of the ways the rules allow (one
    Typical source, or two Lesser; what its Poverty or Wealth allows),
    replacing any sources it has after asking."""
    covenant = _covenant(record)
    choices = cov.income_choices(workspace.saga, covenant)

    def apply(index: int | None) -> None:
        if index is None:
            return
        choice = choices[index]

        def replace(confirmed: bool | None = True) -> None:
            if not confirmed:
                return
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
            workspace._commit("section-eco-income")

        if covenant.economics.income_sources:
            workspace.app.push_screen(
                ConfirmScreen(
                    f"Replace the covenant's {len(covenant.economics.income_sources)} "
                    f"source(s) of income with {escape(choice.label)}?",
                    yes_label="Replace",
                ),
                replace,
            )
        else:
            replace()

    workspace.app.push_screen(
        RemovalPickerScreen(
            "Start the covenant's income", [escape(c.label) for c in choices]
        ),
        apply,
    )


def _use_base_covenant(workspace: WorkspaceScreen, record: Record) -> None:
    """Start from one of the book's base covenants: its Power Level, Build
    Points and placeholders for its books and vis, after asking (and
    warning when another is in use)."""
    covenant = _covenant(record)
    bases = templates.BASE_COVENANTS

    def chosen(index: int | None) -> None:
        if index is None:
            return
        base = bases[index]
        earlier = templates.BASE_BY_KEY.get(covenant.base_covenant)
        books, vis = templates.placeholders(workspace.saga, covenant)
        message = (
            f"Start {escape(covenant.name)} from the {base.name}: Power Level "
            f"{base.power_level}, {base.build_points} Build Points, and "
            f"{escape(templates.summary(base))}. Books and vis come as "
            "placeholders whose subject or Art you choose; Lab Text and "
            "enchanted item levels are an allowance to spend."
        )
        if earlier is not None and earlier is not base:
            message = (
                f"{earlier.name} is in use. {message} The "
                f"{len(books) + len(vis)} placeholder(s) it left unfilled are "
                "removed; what you filled in stays."
            )
        if base.notes:
            message += "\n\n[dim]" + escape(" ".join(base.notes)) + "[/]"

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed:
                templates.apply(workspace.saga, covenant, base)
                workspace._books_changed()
                workspace._commit(
                    "section-cov-info",
                    "section-pos-vis_source",
                    "section-pos-vis_store",
                )

        workspace.app.push_screen(
            ConfirmScreen(
                message,
                yes_label="Use it",
                yes_variant="error" if earlier is not None else "primary",
            ),
            handle_confirmed,
        )

    workspace.app.push_screen(
        RemovalPickerScreen(
            "Use a base covenant",
            [
                f"{escape(b.name)}  [dim]{b.build_points} Build Points, "
                f"{b.power_level}[/]"
                for b in bases
            ],
        ),
        chosen,
    )


def _power_actions(saga: Saga, record: Record) -> list[StepAction]:
    covenant = _covenant(record)
    return [
        StepAction(
            "Choose Power Level", lambda ws, r: ws._choose_power_level(covenant)
        ),
        StepAction("Edit covenant (season, aura)", lambda ws, r: ws._edit_covenant()),
        StepAction("Set starting income", _set_starting_income),
        StepAction(
            "Use a Covenant Situation",
            lambda ws, r: ws._use_covenant_situation(_covenant(r)),
        ),
        StepAction("Use a base covenant", _use_base_covenant),
    ]


# -- Resources: what the Build Points bought --


#: The Resources list's columns.
_BP_NAME = 56
BP_HEADER = f"  {'What':<{_BP_NAME}}{'Points':>7}"


def _bp_label(text: str, points: object, note: str = "") -> str:
    tail = f"  [dim]{escape(note)}[/]" if note else ""
    return f"{pad(text, _BP_NAME)}{points!s:>7}{tail}"


def _tally(saga: Saga, covenant: Covenant) -> str:
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
        return "  (nothing bought yet: a adds a book, vis, an enchanted item or a specialist)"
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
                "(e on the row)"
            )
    return "\n".join(lines) + f"\n\n{_tally(saga, covenant)}"


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


Act = Callable[["WorkspaceScreen"], None] | None


def _resource_ops(saga: Saga, covenant: Covenant, item: Any) -> tuple[Act, Act]:
    """What e and d do to a priced record, by its type: the sheet's own
    form and delete for it. A laboratory is set up on its own worksheet."""
    if isinstance(item, Book):
        return (lambda ws: ws._book_form(item), lambda ws: ws._delete_book(item))
    if isinstance(item, Possession):
        entry = _possession_entry(saga, covenant, item)
        if entry is None:
            return None, None
        return (
            lambda ws: ws._possession_form(item.kind, entry),
            lambda ws: ws._confirm_remove_possession(item.kind, entry),
        )
    if isinstance(item, EnchantedDevice):
        return (
            lambda ws: ws._edit_device(item),
            lambda ws: ws._confirm_remove((item, None)),
        )
    if isinstance(item, Inhabitant):
        person = _inhabitant_entry(saga, covenant, item)
        if person is None:
            return None, None
        return (
            lambda ws: ws._inhabitant_form(item.kind, person, None),
            lambda ws: ws._confirm_remove_inhabitant(item.kind, person),
        )
    return None, None


def _cost_details(saga: Saga, cost: cov.Cost) -> str:
    item = cost.item
    if isinstance(item, Book):
        return bk.detail_text(saga, item)
    tail = (
        "Set it up on the laboratory's own worksheet."
        if isinstance(item, Laboratory)
        else "e changes it, d deletes it."
        if item is not None
        else "Bought as a pool of levels: each text is listed below it, where "
        "e changes it and d deletes it."
        if cost.category in cov.POOL_CATEGORIES
        else "Worked out from what the covenant has."
    )
    category = f" ({escape(cost.category)})" if cost.category else ""
    return (
        f"[b]{escape(cost.label)}[/]\n{cost.points} Build Points{category}\n\n"
        f"[dim]{tail}[/]"
    )


def _pooled_text_row(saga: Saga, book: Book) -> StepRow:
    """A Lab Text or Casting Tablet, under its pool's row: it has no Build
    Points of its own (the pool has them), but e and d act on it."""
    name = book.name or "(untitled)"
    label = name if name.startswith(book.type) else f"{book.type}: {name}"
    level = bk.level_of(book, saga)
    note = f"level {level}" if level else "set its level"
    return StepRow(
        _bp_label(f"  {label}", "", note),
        bk.detail_text(saga, book),
        edit=lambda ws: ws._book_form(book),
        delete=lambda ws: ws._delete_book(book),
    )


def _build_points_rows(saga: Saga, record: Record) -> list[StepRow]:
    """Everything the Build Points bought, under its category, each with
    its points; a book with no level or Quality yet shows 0. e and d edit
    or delete the record a row prices. Lab Texts and Casting Tablets are
    priced as a pool, so each text gets its own row under the pool's."""
    covenant = _covenant(record)
    found = cov.costs(saga, covenant)
    priced = {id(c.item) for c in found if c.item is not None}
    library = bk.books_owned_by(saga, "covenant", covenant.id)
    unpriced = [b for b in library if id(b) not in priced and not bk.pooled(b.type)]
    rows: list[StepRow] = []
    for category in (*cov.CATEGORIES, ""):
        lines = [c for c in found if c.category == category]
        texts = [b for b in library if cov.POOL_CATEGORIES.get(b.type) == category]
        if not lines and not texts:
            continue
        rows.append(StepRow(category or "Other", heading=True))
        for cost in lines:
            edit, delete = _resource_ops(saga, covenant, cost.item)
            rows.append(
                StepRow(
                    _bp_label(cost.label, cost.points),
                    _cost_details(saga, cost),
                    edit=edit,
                    delete=delete,
                )
            )
        rows += [_pooled_text_row(saga, book) for book in texts]
    if unpriced:
        rows.append(StepRow("Not priced yet", heading=True))
        for book in unpriced:
            name = book.name or "(untitled)"
            label = name if name.startswith(book.type) else f"{book.type}: {name}"
            rows.append(
                StepRow(
                    _bp_label(label, 0, "set its level or Quality"),
                    bk.detail_text(saga, book),
                    edit=lambda ws, b=book: ws._book_form(b),
                    delete=lambda ws, b=book: ws._delete_book(b),
                )
            )
    return rows


def _add_covenant_device(workspace: WorkspaceScreen, covenant: Covenant) -> None:
    def handle_result(device: EnchantedDevice | None) -> None:
        if device is not None:
            workspace.saga.enchanted_devices.append(device)
            workspace._commit_devices()

    workspace.app.push_screen(
        _enchanted_device_dialog(
            workspace.saga, None, holder=f"covenant:{covenant.id}"
        ),
        handle_result,
    )


SAGA_BOOK = "A book from the saga's books"


def _buy_saga_book(workspace: WorkspaceScreen, covenant: Covenant) -> None:
    """Pick one of the saga's own books a new covenant may buy and copy it
    into the covenant's Library (the saga's copy stays where it is)."""
    saga = workspace.saga
    power = cov.POWER_BY_NAME.get(covenant.power_level)

    def handle_book(book: Book | None) -> None:
        if book is None:
            return
        bk.copy_to(saga, book, "covenant", covenant.id)
        workspace._books_changed()
        workspace._commit()
        workspace.notify(
            f"{escape(book.name)} copied into {escape(covenant.name)}'s Library."
        )

    workspace.app.push_screen(
        SagaBookPickerScreen(
            saga,
            bk.unassigned_books(saga),
            power.max_level if power is not None else None,
        ),
        handle_book,
    )


#: What a adds on the Resources step: (letter, label, how).
_RESOURCE_ADDS: tuple[
    tuple[str, str, Callable[[WorkspaceScreen, Covenant], None]], ...
] = (
    ("b", SAGA_BOOK, _buy_saga_book),
    ("n", "A new book", lambda ws, c: ws._book_form(None)),
    ("v", "A vis source", lambda ws, c: ws._possession_form("vis_source", None)),
    ("s", "A vis stock", lambda ws, c: ws._possession_form("vis_store", None)),
    ("e", "An enchanted item", _add_covenant_device),
    (
        "p",
        "A specialist, craftsperson, teacher or guard",
        lambda ws, c: ws._buy_specialist(c),
    ),
)


def _add_resource(workspace: WorkspaceScreen, record: Record) -> None:
    """a on Resources: ask what to buy, then open its form."""
    covenant = _covenant(record)
    offered = [
        add
        for add in _RESOURCE_ADDS
        if add[1] != SAGA_BOOK or bk.unassigned_books(workspace.saga)
    ]
    adds = {label: how for _, label, how in offered}

    def handle_choice(choice: str | None) -> None:
        if choice in adds:
            adds[choice](workspace, covenant)

    workspace.app.push_screen(
        MenuScreen(
            "Buy with Build Points",
            [(letter, label, label) for letter, label, _ in offered],
        ),
        handle_choice,
    )


# -- Boons & Hooks --


def _boons_hooks_budget(saga: Saga, record: Record) -> str:
    covenant = _covenant(record)
    boons_catalog = catalog.load_covenant_boon_hook_catalog_by_id()
    boons = covenant_boon_points(covenant, boons_catalog)
    hooks = covenant_hook_points(covenant, boons_catalog)
    return aligned([("Boon points", f"{boons:g}"), ("Hook points", f"{hooks:g}")])


#: The Boons and Hooks list's columns.
_BH_NAME = 56
BH_HEADER = f"  {'Boon or Hook':<{_BH_NAME}}{'Points':>7}"


def _boons_hooks_rows(saga: Saga, record: Record) -> list[StepRow]:
    """The covenant's Boons, then its Hooks, each with its points and
    rules; a Resource Hook not yet tied to its source says so. e edits
    one (a Resource Hook also names its source), d removes it."""
    covenant = _covenant(record)
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    rows: list[StepRow] = []
    for kind, heading in (("Boon", "Boons"), ("Hook", "Hooks")):
        found = [
            (index, bh, by_id[bh.vf_id])
            for index, bh in enumerate(covenant.boons_hooks)
            if bh.vf_id in by_id and by_id[bh.vf_id].type == kind
        ]
        if not found:
            continue
        rows.append(StepRow(heading, heading=True))
        for index, bh, definition in found:
            points = boon_hook_points(bh, definition)
            label = (
                f"{pad(catalog.describe_boon_hook(bh, by_id), _BH_NAME)}{points:>7g}"
            )
            details = boon_hook_info_text(covenant, index)
            if bh.vf_id in cov_rules.RESOURCE_HOOKS:
                source = cov_rules.linked_source(covenant, bh)
                if source is None:
                    label += "  [$text-warning]needs its source[/]"
                    about = (
                        "(not yet: e names it, once the vis or income source exists)"
                    )
                else:
                    about = escape(source.name or "unnamed")
                details = f"[b]About:[/] {about}\n{details}"
            rows.append(
                StepRow(
                    label,
                    details,
                    edit=lambda ws, k=kind, i=index: ws._edit_boon_hook_at(k, i),
                    delete=lambda ws, k=kind, i=index: ws._confirm_remove_boon_hook(
                        k, i
                    ),
                )
            )
    return rows


def _boons_hooks_actions(saga: Saga, record: Record) -> list[StepAction]:
    return [StepAction("Add a Hook", lambda ws, r: ws._add_boon_hook("Hook"))]


def _review_budget(saga: Saga, record: Record) -> str:
    lines = ["Review:", *review_lines(saga, record)]
    if isinstance(record, Covenant):
        lines += ["", "Build Points:", _tally(saga, record)]
        lines += ["", f"[dim]{escape(cov.baseline_covenfolk_note(saga, record))}[/]"]
    return "\n".join(lines)


PANELS[("covenant", "power")] = StepPanel(
    _power_budget,
    _power_actions,
    StepList(
        INCOME_HEADER,
        _income_rows,
        add=lambda ws, r: ws._income_form(None),
        add_label="Add a source of income",
        delete_label="Delete",
        hint="Its sources of income: Set starting income makes them by the rules.",
    ),
)
PANELS[("covenant", "build_points")] = StepPanel(
    _build_points_budget,
    list=StepList(
        BP_HEADER,
        _build_points_rows,
        add=_add_resource,
        add_label="Buy something",
        delete_label="Delete",
        hint="Choose a row to see what it is and what it costs.",
    ),
)
PANELS[("covenant", "boons_hooks")] = StepPanel(
    _boons_hooks_budget,
    _boons_hooks_actions,
    StepList(
        BH_HEADER,
        _boons_hooks_rows,
        add=lambda ws, r: ws._add_boon_hook("Boon"),
        add_label="Add a Boon",
        delete_label="Remove",
        hint="Choose a Boon or Hook to read its rules.",
    ),
)
PANELS[("covenant", "finish")] = StepPanel(_review_budget)


# -- New Laboratory --


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
        StepAction("Starting lab: yes/no", lambda ws, r: ws._toggle_starting_lab(lab)),
    ]


def _lab_virtue_rows(saga: Saga, record: Record) -> list[StepRow]:
    """The laboratory's Virtues, then its Flaws, each with its rules; d
    removes one."""
    lab = _laboratory(record)
    by_id = catalog.load_lab_virtue_flaw_catalog_by_id()
    rows: list[StepRow] = []
    for side, heading in (("Virtue", "Virtues"), ("Flaw", "Flaws")):
        taken = [
            (index, vf, definition)
            for index, vf in enumerate(lab.virtues_flaws)
            if (definition := by_id.get(vf.vf_id)) is not None
            and definition.type == side
        ]
        if not taken:
            continue
        rows.append(StepRow(heading, heading=True))
        for index, vf, definition in taken:
            rows.append(
                StepRow(
                    f"{pad(catalog.describe_virtue_flaw(vf, by_id), _VF_NAME)}"
                    f"{definition.tier:<{_VF_TIER}}{escape(definition.category)}",
                    lab_rules.vf_info_text(lab, index),
                    delete=partial(_remove_virtue_flaw_of, lab, vf),
                )
            )
    return rows


def _remove_virtue_flaw_of(
    lab: Laboratory, vf: VirtueFlawInstance, workspace: WorkspaceScreen
) -> None:
    if vf in lab.virtues_flaws:
        workspace._remove_virtue_flaw_from(lab, lab.virtues_flaws.index(vf))


PANELS[("laboratory", "setup")] = StepPanel(
    _setup_budget,
    _setup_actions,
    StepList(
        VF_HEADER,
        _lab_virtue_rows,
        add=lambda ws, r: ws._add_virtue_flaw_to(_laboratory(r)),
        add_label="Add a Virtue or Flaw",
        edit_label=None,
        delete_label="Remove",
        hint="Choose a Virtue or Flaw to read its rules.",
    ),
)
PANELS[("laboratory", "finish")] = StepPanel(_review_budget)

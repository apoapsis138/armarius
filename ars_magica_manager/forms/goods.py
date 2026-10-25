"""Saga Content's Goods tab, independent of how it is drawn: the list's
rows (the terminal's) and table (the desktop's), the chosen good's
details, Add, Edit and Delete for the saga's own goods (a catalog good is
hidden, not deleted), and More's Add a Purity.

The figures and their pages are goods.py's; this module words them.
"""

from __future__ import annotations

import re
from typing import Any

from .. import catalog
from .. import goods as gd
from .. import saga_content as sc
from ..commands import Confirm, Form, Refuse, SectionOps
from ..form_spec import DialogField, description_field
from ..markup import BULLET, escape, fit
from ..models import COMMODITY, COMMON, GoodDef, GoodPurity, Purity, Saga
from ..models.goods import PRICE_PATTERN
from ..sections import GOODS_SECTION
from ..tables import Table

CG = "C&G"
#: A source's towns, in brackets after its region.
_SHORT = re.compile(r" \([^)]*\)")
COLUMNS = ["Good", "Class", "Sold by", *gd.QUALITIES]
#: The terminal's columns: its group headings name each class, so its
#: rows leave the Class column to the desktop's ledger, and the list fits
#: beside the navigation at 120 columns.
TERMINAL_COLUMNS = ["Good", "Sold by", *gd.QUALITIES]
#: Their widths: Good and Sold by, then each quality's (right-aligned).
WIDTHS = (23, 8)
PRICE_WIDTHS = (11, 10, 10, 10)

WEIGHTS = (
    f"16 ounces = 1 pound = 1/2,240 ton [dim](errata p. 57, correcting {CG} p. 140)[/]"
)

_CLASS_LONG = {
    "bulk": "Bulk good",
    "manufactured": "Manufactured good",
    "luxury": "Luxury good",
}

#: The list's group headings: the catalog's commodities by class (C&G
#: p. 134), its common goods and the saga's own.
_HEADINGS = {
    "bulk": f"Bulk goods  [dim]({CG} pp. 134-137)[/]",
    "manufactured": f"Manufactured goods  [dim]({CG} p. 137)[/]",
    "luxury": f"Luxury goods  [dim]({CG} pp. 137-138)[/]",
    "common": f"Common goods  [dim]the standard price each ({CG} p. 144)[/]",
    "own": "The saga's own",
}


def title(saga: Saga) -> str:
    return f"Goods ({len(gd.listed(saga))})"


def header(saga: Saga, *, two_lines: bool = False) -> str:
    """What the prices mean, over the list."""
    sep = "\n" if two_lines else "  ·  "
    off = (
        "  ·  [$text-error]the catalog is not offered: only the saga's own[/]"
        if gd.CATALOG_KEY in saga.hidden_catalogs
        else ""
    )
    return (
        f"Mythic pounds a tun or ton, by quality [dim]({CG} pp. 140-142)[/]"
        "  ·  common goods each [dim](p. 144)[/]"
        + sep
        + "[b]#[/] none to be had at that quality  ·  [b]*[/] priced by purity"
        "  ·  no Excellent column" + off
    )


def _group(saga: Saga, good: GoodDef) -> str:
    if gd.is_own(saga, good):
        return "own"
    if good.kind == COMMON:
        return "common"
    return good.commodity_class if good.commodity_class in _HEADINGS else "bulk"


def _class(good: GoodDef) -> str:
    if good.kind == COMMON:
        return "Common"
    return gd.CLASSES.get(good.commodity_class, "")


def _shown_prices(good: GoodDef) -> tuple[str, str, str, str]:
    """The four price cells: a commodity's as printed, a common good's
    standard price in pounds, shillings and pence."""
    if good.kind == COMMON and good.pence is not None:
        return ("", gd.coins_range(good.pence), "", "")
    return good.prices


def _price_cell(printed: str, *, short: bool) -> str:
    if printed == gd.UNOBTAINABLE:
        return "[dim]#[/]"
    if short:
        printed = printed.replace(" (fake)", " fake")
    return escape(printed)


def _padded(markup: str, plain: str, width: int, *, right: bool = False) -> str:
    pad = " " * max(0, width - len(plain))
    return pad + markup if right else markup + pad


def table_header() -> str:
    """The terminal list's column titles (after its two-character marker)."""
    return (
        "  "
        + "".join(fit(t, w) for t, w in zip(TERMINAL_COLUMNS[:2], WIDTHS, strict=True))
        + "".join(q.rjust(w) for q, w in zip(gd.QUALITIES, PRICE_WIDTHS, strict=True))
    )


def rows(saga: Saga) -> list[tuple[int | None, str]]:
    """The terminal list's rows: a heading per group, then (index, row)."""
    found: list[tuple[int | None, str]] = []
    group = ""
    listed = gd.listed(saga)
    for n, good in enumerate(listed):
        if _group(saga, good) != group:
            group = _group(saga, good)
            found.append((None, f"[b]{_HEADINGS[group]}[/]"))
        cells = [good.name, good.sold_by]
        line = "".join(escape(fit(c, w)) for c, w in zip(cells, WIDTHS, strict=True))
        for printed, width in zip(_shown_prices(good), PRICE_WIDTHS, strict=True):
            shown = printed.replace(" (fake)", " fake")
            line += _padded(_price_cell(printed, short=True), shown, width, right=True)
        found.append((n, line.rstrip()))
    if not listed:
        found.append(
            (
                None,
                "[dim]None: the catalog is not offered and the saga has no "
                "goods of its own. Add one with a.[/]",
            )
        )
    return found


def table(saga: Saga) -> Table:
    """The desktop's ledger: the same columns, a heading row per group."""
    cells: list[list[str]] = []
    keys: list[int | None] = []
    group = ""
    for n, good in enumerate(gd.listed(saga)):
        if _group(saga, good) != group:
            group = _group(saga, good)
            cells.append([_HEADINGS[group].split("  [dim]")[0]])
            keys.append(None)
        cells.append(
            [
                escape(good.name),
                _class(good),
                escape(good.sold_by),
                *(_price_cell(p, short=False) for p in _shown_prices(good)),
            ]
        )
        keys.append(n)
    return Table(list(COLUMNS), cells, keys, markup=True, stretch=0)


def _class_text(good: GoodDef) -> str:
    if good.kind == COMMON:
        return f"Common good ({CG} p. {good.page or 144})"
    long = _CLASS_LONG.get(good.commodity_class, "Commodity")
    page = f" ({CG} p. {good.class_page})" if good.class_page else ""
    return long + page


def inspector_title(saga: Saga, index: int) -> tuple[str, str]:
    good = gd.listed(saga)[index]
    sold = "each" if good.kind == COMMON else f"sold by the {good.sold_by}"
    own = "  ·  the saga's own" if gd.is_own(saga, good) else ""
    return good.name, f"{_class_text(good).split(' (')[0]}  ·  {sold}{own}"


def _page(good: GoodDef) -> str:
    return f" [dim](p. {good.page})[/]" if good.page else ""


def _purity_lines(saga: Saga, good: GoodDef, purity: Purity, wide: bool) -> list[str]:
    lines: list[str] = []
    pure = purity.pure_price
    entries: list[str] = []
    if pure is not None:
        entries.append(f"pure [b]{gd.number(pure)}[/] a ton")
        for example in purity.examples:
            value = gd.price_value(example.price)
            about = ""
            if value is not None:
                percent = f"{gd.purity_percent(value, pure):.0f}%"
                about = (
                    f" ({percent})"
                    if wide
                    else f" (about {percent} {escape(good.name.lower())})"
                )
            entries.append(f"{example.label} [b]{escape(example.price)}[/]{about}")
        for own in gd.purities_of(saga, good):
            entries.append(
                f"{escape(own.label)}, {gd.number(own.percent)}% "
                f"[b]{gd.number(gd.price_at_purity(pure, own.percent))}[/] "
                "[dim](the saga's)[/]"
            )
    rule = f"[dim](by metal content, {CG} p. 140)[/]" if pure is not None else ""
    if wide:
        if entries:
            lines.append(f"[$label]By purity[/] {rule}: " + "  ·  ".join(entries))
        if purity.note:
            lines.append(f"  [dim]{escape(purity.note)}[/]")
    else:
        lines.append(f"[$label]By purity[/] {rule}".rstrip())
        lines += [f"{BULLET} {e}" for e in entries]
        if purity.note:
            lines.append(f"[dim]{escape(purity.note)}[/]")
        lines.append("")
    return lines


def _common_lines(good: GoodDef, wide: bool) -> list[str]:
    assert good.pence is not None
    low, high = good.pence
    printed = good.prices[1]
    lines = [f"[$label]Standard price:[/] [b]{escape(printed)}[/]{_page(good)}"]
    quality = []
    for label, times in gd.COMMON_MULTIPLIERS:
        if times == 1:
            continue
        low_text = gd.pounds_shillings_pence(low * times)
        text = (
            low_text
            if low == high
            else f"{low_text} to {gd.pounds_shillings_pence(high * times)}"
        )
        quality.append(f"{label} x{gd.number(times)} [b]{text}[/]")
    quality.append("Wondrous x5 or more")
    if wide:
        lines.append(
            "[$label]By quality:[/] "
            + "  ·  ".join(quality)
            + f" [dim]({CG} p. 144)[/]"
        )
    else:
        lines += ["", f"[$label]By quality[/] [dim]({CG} p. 144)[/]"]
        lines += [f"{BULLET} {q}" for q in quality]
        lines.append("")
    lines.append(
        f"[dim]For story flavour, not merchants' or crafters' incomes ({CG} p. 143).[/]"
    )
    return lines


def _commodity_lines(saga: Saga, good: GoodDef, wide: bool) -> list[str]:
    unit = "A tun" if good.sold_by == "tun" else "A ton"
    pairs = list(zip(gd.QUALITIES, good.prices, strict=True))
    lines: list[str] = []
    if wide:
        prices = "  ·  ".join(
            f"{q} [b]{_price_cell(p, short=True) if p else '[dim]blank[/]'}[/]"
            for q, p in pairs
        )
        lines.append(f"[$label]{unit}:[/] {prices}{_page(good)}")
    else:
        lines.append(f"[$label]Price {unit.lower()}, by quality[/]{_page(good)}")
        lines += [
            f"{BULLET} {q}: [b]{_price_cell(p, short=False)}[/]"
            if p
            else f"{BULLET} {q}: [dim]blank in the book[/]"
            for q, p in pairs
        ]
        lines.append("")
    if good.sale:
        lines.append(escape(good.sale))
    if good.per_ounce:
        ounce = "  ·  ".join(
            f"{q} [b]{escape(p)}[/]"
            for q, p in zip(gd.QUALITIES, good.per_ounce, strict=False)
            if p
        )
        lines.append(f"[$label]An ounce:[/] {ounce}")
        lines.append(f"  [dim]{escape(good.per_ounce_note)}[/]")
    if (good.sale or good.per_ounce) and not wide:
        lines.append("")
    if good.purity is not None:
        lines += _purity_lines(saga, good, good.purity, wide)
    return lines


def info(saga: Saga, index: int | None, *, wide: bool) -> str:
    """The details panel (wide: the terminal's) or the desktop Inspector."""
    listed = gd.listed(saga)
    if index is None or not 0 <= index < len(listed):
        return (
            "[dim]Choose a good to see its prices, purities and where it is bought.[/]"
        )
    good = listed[index]
    own = gd.is_own(saga, good)
    lines: list[str] = []
    if wide:
        sold = "each" if good.kind == COMMON else f"sold by the {escape(good.sold_by)}"
        lines.append(
            f"[b]{escape(good.name)}[/]  [dim]{_class_text(good)}  ·  {sold}"
            + ("  ·  the saga's own" if own else "")
            + "[/]"
        )
    if good.kind == COMMON and good.pence is not None:
        lines += _common_lines(good, wide)
    else:
        lines += _commodity_lines(saga, good, wide)
    if good.sources:
        if wide:
            # The towns in brackets are left to the desktop's longer list.
            places = "; ".join(_SHORT.sub("", s) for s in good.sources)
            lines.append(
                f"[$label]Bought in bulk at:[/] {escape(places)}"
                + ("" if own else f" [dim]({CG} pp. 138-140)[/]")
            )
        else:
            lines.append(
                "[$label]Bought in bulk at[/]"
                + ("" if own else f" [dim]({CG} pp. 138-140)[/]")
            )
            lines += [f"{BULLET} {escape(s)}" for s in good.sources]
            lines.append("")
    elif good.kind == COMMODITY and not own:
        lines.append(
            "[dim]No place is listed for it in bulk: most goods are found in "
            f"any large city ({CG} p. 139).[/]"
        )
    if good.note:
        lines.append(f"[i]{escape(good.note)}[/]")
    if good.description:
        lines.append(escape(good.description))
    if good.kind == COMMODITY:
        lines.append(f"[$label]Weights:[/] {WEIGHTS}")
    return "\n".join(lines).strip("\n")


# -- Add, Edit and Delete --


def _read_only(good: GoodDef) -> str:
    return (
        f"{escape(good.name)} is from City & Guild's prices, so it's "
        "read-only. To price it your own way, add a good of the saga's own "
        "(and hide this one with d)."
    )


_PRICE_HINT = (
    'A number, "#" none to be had, "*" priced by purity, or blank (as the '
    f"table prints them, {CG} pp. 141-142)."
)


def fields(existing: GoodDef | None) -> list[DialogField]:
    """A good of the saga's own: a commodity priced a tun or ton by
    quality, or a common good priced each."""
    kind = existing.kind if existing is not None else COMMODITY
    prices = existing.prices if existing is not None else ("", "", "", "")
    pure = (
        existing.purity.pure_price
        if existing is not None and existing.purity is not None
        else None
    )

    def commodity(values: dict[str, Any]) -> bool:
        return values.get("kind") == COMMODITY

    return [
        DialogField(
            "name", "Name", "text", existing.name if existing else "", required=True
        ),
        DialogField(
            "kind",
            "Priced",
            "select",
            kind,
            options=[
                ("a tun or ton, by quality (a commodity)", COMMODITY),
                ("each (a common good)", COMMON),
            ],
        ),
        DialogField(
            "commodity_class",
            "Class",
            "select",
            (existing.commodity_class if existing else "") or "bulk",
            options=[(label, key) for key, label in gd.CLASSES.items()],
            hint=f"Bulk, manufactured or luxury goods ({CG} p. 134).",
            show_if=commodity,
        ),
        DialogField(
            "sold_by",
            "Sold by",
            "text",
            existing.sold_by if existing is not None and kind == COMMODITY else "ton",
            placeholder="e.g. ton, tun, ounce, roll, head",
            show_if=commodity,
        ),
        *(
            DialogField(
                quality.lower(),
                quality,
                "text",
                printed,
                hint=_PRICE_HINT if quality == "Shoddy" else "",
                show_if=commodity,
            )
            for quality, printed in zip(gd.QUALITIES, prices, strict=True)
        ),
        DialogField(
            "pure_price",
            "Pure price, a ton",
            "optfloat",
            pure,
            hint="For a good priced by purity: a purity's price is this times "
            f"its metal content ({CG} p. 140).",
            show_if=commodity,
        ),
        DialogField(
            "pence",
            "Standard price, in pence",
            "optfloat",
            existing.pence[0] if existing is not None and existing.pence else None,
            hint=f"12 pence a shilling, 240 a pound ({CG} p. 143); "
            "the other qualities follow p. 144's multipliers.",
            show_if=lambda values: values.get("kind") == COMMON,
        ),
        DialogField(
            "sources",
            "Bought in bulk at",
            "text",
            "; ".join(existing.sources) if existing else "",
            placeholder="e.g. Cologne; the Low Countries",
            hint="Places, separated by semicolons.",
        ),
        description_field(existing.description if existing else ""),
    ]


def problem(saga: Saga, existing: GoodDef | None, values: dict[str, Any]) -> str | None:
    """What's wrong with a good form's values, if anything."""
    name = (values.get("name") or "").strip()
    if any(
        g.name.casefold() == name.casefold()
        for g in saga.custom_goods
        if g is not existing
    ):
        return f"The saga already has a good named {name}."
    if values.get("kind") == COMMON:
        pence = values.get("pence")
        if pence is None or pence <= 0:
            return "Give the standard price in pence."
        return None
    for quality in gd.QUALITIES:
        printed = (values.get(quality.lower()) or "").strip()
        if not PRICE_PATTERN.match(printed):
            return f"{quality}: {_PRICE_HINT}"
    pure = values.get("pure_price")
    if pure is not None and pure <= 0:
        return "The pure price must be more than 0."
    return None


def _made(saga: Saga, existing: GoodDef | None, values: dict[str, Any]) -> GoodDef:
    name = (values.get("name") or "").strip()
    sources = tuple(
        s.strip() for s in (values.get("sources") or "").split(";") if s.strip()
    )
    ident = existing.id if existing is not None else gd.new_good_id(saga, name)
    description = values.get("description") or ""
    if values.get("kind") == COMMON:
        pence = float(values["pence"])
        return GoodDef(
            id=ident,
            name=name,
            kind=COMMON,
            sold_by="each",
            prices=("", gd.coins(pence), "", ""),
            pence=(pence, pence),
            sources=sources,
            description=description,
        )
    pure = values.get("pure_price")
    prices = tuple((values.get(q.lower()) or "").strip() for q in gd.QUALITIES)
    return GoodDef(
        id=ident,
        name=name,
        kind=COMMODITY,
        commodity_class=values.get("commodity_class") or "bulk",
        sold_by=(values.get("sold_by") or "").strip() or "ton",
        prices=(prices[0], prices[1], prices[2], prices[3]),
        purity=Purity(
            pure_price=float(pure),
            note=f"A purity's price is the pure price times its metal content "
            f"({CG} p. 140).",
        )
        if pure is not None
        else None,
        sources=sources,
        description=description,
    )


def ops(saga: Saga) -> SectionOps:
    """Add, Edit and Delete on the Goods list; a row is the good's index
    in goods.listed. A catalog good can't be edited, and Delete hides it
    (the Catalogs tab's Hidden Entries offers it again)."""

    def form(existing: GoodDef | None) -> Form:
        def apply(values: dict[str, Any]) -> None:
            made = _made(saga, existing, values)
            if existing is None:
                saga.custom_goods.append(made)
            else:
                at = next(i for i, g in enumerate(saga.custom_goods) if g is existing)
                saga.custom_goods[at] = made
                if made.purity is None or made.purity.pure_price is None:
                    saga.good_purities[:] = [
                        p for p in saga.good_purities if p.good_id != made.id
                    ]
            catalog.use_saga(saga)

        return Form(
            "Add a Good" if existing is None else f"Edit {escape(existing.name)}",
            lambda: fields(existing),
            apply,
            validate=lambda values: problem(saga, existing, values),
            save_label="Add" if existing is None else "Save",
            help_id=GOODS_SECTION,
        )

    def edit(index: int) -> Form | Refuse:
        good = gd.listed(saga)[index]
        if not gd.is_own(saga, good):
            return Refuse("Edit a Good", _read_only(good))
        return form(good)

    def remove(index: int) -> Confirm:
        good = gd.listed(saga)[index]
        if gd.is_own(saga, good):

            def delete() -> None:
                saga.custom_goods[:] = [g for g in saga.custom_goods if g is not good]
                saga.good_purities[:] = [
                    p for p in saga.good_purities if p.good_id != good.id
                ]
                catalog.use_saga(saga)

            return Confirm(f"Delete {escape(good.name)}?", delete)
        return Confirm(
            f"Hide {escape(good.name)}?\n\nThe Catalogs tab's Hidden Entries "
            "offers it again.",
            lambda: sc.hide_entry(saga, gd.CATALOG_KEY, good.id),
            yes_label="Hide",
        )

    return SectionOps(
        add=lambda: form(None),
        edit=edit,
        remove=remove,
        rows=lambda: [g.name for g in gd.listed(saga)],
    )


# -- More: Add a Purity --


def purity_fields(saga: Saga, good: GoodDef) -> list[DialogField]:
    """A purity of the saga's own for `good`, and a tick to remove each it
    has already."""
    found = [
        DialogField(
            "label",
            "Purity",
            "text",
            "",
            placeholder="e.g. Coin silver",
            hint="Blank adds none (to only remove one below).",
        ),
        DialogField(
            "percent",
            "Metal content, %",
            "optfloat",
            None,
            hint=f"Of the pure good; its price follows from it ({CG} p. 140).",
        ),
    ]
    found += [
        DialogField(
            f"remove:{p.id}",
            f"Remove {p.label} ({gd.number(p.percent)}%)",
            "check",
            False,
        )
        for p in gd.purities_of(saga, good)
    ]
    return found


def purity_problem(values: dict[str, Any]) -> str | None:
    label = (values.get("label") or "").strip()
    percent = values.get("percent")
    if label and percent is None:
        return "Give its metal content, in percent."
    if percent is not None and not label:
        return "Name the purity."
    if percent is not None and not 0 < percent <= 100:
        return "The metal content is more than 0% and at most 100%."
    return None


def purity_live(good: GoodDef) -> Any:
    def live(values: dict[str, Any]) -> str:
        assert good.purity is not None and good.purity.pure_price is not None
        pure = good.purity.pure_price
        percent = values.get("percent")
        if percent is None or not 0 < percent <= 100:
            return (
                f"[dim]{escape(good.name)}: pure {gd.number(pure)} a ton; a purity "
                f"is priced by its metal content ({CG} p. 140).[/]"
            )
        price = gd.price_at_purity(pure, percent)
        return (
            f"[b]{gd.number(round(price, 2))}[/] a ton  [dim]= pure "
            f"{gd.number(pure)} x {gd.number(percent)}% ({CG} p. 140)[/]"
        )

    return live


def add_purity(saga: Saga, index: int | None) -> Form | Refuse:
    """More's Add a Purity on the chosen good: a purity priced by its metal
    content, kept with the saga."""
    listed = gd.listed(saga)
    if index is None or not 0 <= index < len(listed):
        return Refuse("Add a Purity", "Choose a good first.")
    good = listed[index]
    if not gd.takes_purities(good):
        why = (
            good.purity.note
            if good.purity is not None
            else f"The table doesn't price {good.name} by purity."
        )
        return Refuse("Add a Purity", escape(why))

    def apply(values: dict[str, Any]) -> None:
        removed = {
            key.removeprefix("remove:")
            for key, ticked in values.items()
            if key.startswith("remove:") and ticked
        }
        saga.good_purities[:] = [p for p in saga.good_purities if p.id not in removed]
        label = (values.get("label") or "").strip()
        if label and values.get("percent") is not None:
            saga.good_purities.append(
                GoodPurity(
                    gd.new_purity_id(saga), good.id, label, float(values["percent"])
                )
            )

    return Form(
        f"Add a Purity: {escape(good.name)}",
        lambda: purity_fields(saga, good),
        apply,
        validate=purity_problem,
        live=purity_live(good),
        save_label="Save",
        help_id=GOODS_SECTION,
    )


def offers_purity(saga: Saga, index: int | None) -> bool:
    """Whether Add a Purity can act on row `index` of the Goods list."""
    listed = gd.listed(saga)
    return (
        index is not None
        and 0 <= index < len(listed)
        and (gd.takes_purities(listed[index]))
    )

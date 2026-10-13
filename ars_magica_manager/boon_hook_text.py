"""The text of a covenant's Boons and Hooks, for any front-end: the list
titles with their point totals, a row per attached Boon or Hook, and the
details shown for one, chosen from the covenant or from the catalog.

Also the small title helpers the record sheets share ("Rooms (3)",
"Boons (7 pts)" in the colour of the balance).
"""

from __future__ import annotations

from . import catalog, sourcebooks
from . import covenant_diary as cov_diary
from . import sheet_text as st
from .covenants import (
    UNKNOWN_HOOK_POINTS,
    boon_hook_is_unknown,
    covenant_boon_points,
    covenant_hook_points,
)
from .markup import escape, markdown_inline
from .models import (
    BOON_HOOK_DESCRIPTION,
    Covenant,
    CovenantBoonHookDef,
)


def counted(label: str, count: int) -> str:
    """A list section's title with how many entries it has: "Rooms (3)"."""
    return f"{label} ({count})"


def points_title(label: str, points: float, colour: str | None = None) -> str:
    """A title with the points its list comes to: "Boons (3 pts)", the
    points in the theme `colour` if given (see match_colour)."""
    unit = "pt" if points == 1 else "pts"
    text = f"({points:g} {unit})"
    return f"{label} [{colour}]{text}[/]" if colour else f"{label} {text}"


def match_colour(points: float, other: float) -> str:
    """The colour for the two sides of a balance (Virtues against Flaws):
    $text-success when they match, $text-error when they don't."""
    return "$text-success" if points == other else "$text-error"


def tier_text(entry: CovenantBoonHookDef) -> str:
    """ "Minor Boon (1 pt)", "Major Hook (3 pts)" or "Free Boon"."""
    points = abs(entry.cost)
    if not points:
        return f"{entry.tier} {entry.type}"
    return f"{entry.tier} {entry.type} ({points:g} {'pt' if points == 1 else 'pts'})"


def boon_hook_names(ids: list[str], by_id: dict[str, CovenantBoonHookDef]) -> str:
    """Names of catalog entries, each listed once (Road/Urban exist at both
    tiers), for prerequisite/exclusion notes."""
    return ", ".join(dict.fromkeys(by_id[i].name for i in ids if i in by_id))


def boon_hook_title(covenant: Covenant, kind: str) -> str:
    """ "Boons (7 pts)" / "Hooks (7 pts)": Boons show the points they
    cost, Hooks the points they provide. Both totals share one colour:
    plain while the Boons cost less than the Hooks provide (points still
    to spend), $text-success when they match, $text-error when the Boons
    cost more."""
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    boons = covenant_boon_points(covenant, by_id)
    hooks = covenant_hook_points(covenant, by_id)
    colour = None if boons < hooks else match_colour(boons, hooks)
    if kind == "Boon":
        return points_title("Boons", boons, colour)
    return points_title("Hooks", hooks, colour)


def boon_hook_rows(covenant: Covenant, kind: str) -> list[tuple[int, str]]:
    """The attached Boons or Hooks of `kind` as (index into
    covenant.boons_hooks, display label) pairs, in attach order."""
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    return [
        (
            index,
            escape(catalog.describe_boon_hook(bh, by_id))
            + (
                f" [dim](Unknown, {UNKNOWN_HOOK_POINTS} pts)[/]"
                if boon_hook_is_unknown(bh, by_id[bh.vf_id])
                else ""
            )
            + (
                f" [dim]({cov_diary.pool_short(covenant, bh.id)})[/]"
                if bh.vf_id in cov_diary.POOLS and bh.id
                else ""
            ),
        )
        for index, bh in enumerate(covenant.boons_hooks)
        if bh.vf_id in by_id and by_id[bh.vf_id].type == kind
    ]


def boon_hook_info_text(covenant: Covenant, index: int | None) -> str:
    """The details panel for the attached Boon/Hook at `index` into
    covenant.boons_hooks: its name, type, notes, the user's own
    description (if any), then the official rules text and the book it
    comes from."""
    if index is None:
        return "[dim]Select a Boon or Hook to see its details.[/]"
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    instance = covenant.boons_hooks[index]
    definition = by_id.get(instance.vf_id)
    if definition is None:
        return escape(f"{instance.vf_id} (not in catalog)")

    lines = [f"[b]Name:[/] {escape(catalog.describe_boon_hook(instance, by_id))}"]
    if definition.category:
        lines.append(f"[b]Type:[/] {definition.category}")
    lines.append(f"[b]Tier:[/] {tier_text(definition)}")
    if boon_hook_is_unknown(instance, definition):
        lines.append(
            f"[b]Unknown:[/] Yes (counts {UNKNOWN_HOOK_POINTS} points, as a Major Hook)"
        )
    elif definition.unknown:
        lines.append("[dim]May be Unknown (mark it in its Edit form).[/]")
    lines += _boon_hook_rule_lines(definition, by_id)
    if instance.vf_id in cov_diary.POOLS and instance.id:
        lines += cov_diary.pool_lines(covenant, instance.id)
    # The user's own description leads; the official rules text follows.
    description = instance.params.get(BOON_HOOK_DESCRIPTION, "").strip()
    if description:
        lines += ["", "[b]Description:[/]", markdown_inline(description)]
    lines += ["", "[b]Rules:[/]", escape(definition.description)]
    if definition.source:
        lines += ["", f"[dim]Source: {escape(definition.source)}[/]"]
    return "\n".join(lines)


def _boon_hook_rule_lines(
    definition: CovenantBoonHookDef, by_id: dict[str, CovenantBoonHookDef]
) -> list[str]:
    """A Boon's or Hook's prerequisites, exclusions, effects and how often
    it may be taken, one details-panel line each."""
    lines = []
    if definition.requires:
        lines.append(f"[b]Requires:[/] {boon_hook_names(definition.requires, by_id)}")
    if definition.requires_any:
        lines.append(
            "[b]Requires one of:[/] " + boon_hook_names(definition.requires_any, by_id)
        )
    if definition.excludes:
        lines.append(f"[b]Not with:[/] {boon_hook_names(definition.excludes, by_id)}")
    lines += st.effect_lines(definition.modifiers)
    if definition.max_count:
        lines.append(
            f"[dim]May be taken up to {definition.max_count} times; "
            "the effects stack.[/]"
        )
    elif definition.repeatable:
        lines.append("[dim]May be taken more than once; the effects stack.[/]")
    return lines


def boon_hook_entry_text(
    definition: CovenantBoonHookDef, by_id: dict[str, CovenantBoonHookDef]
) -> str:
    """A catalog Boon or Hook as the picker shows it under the list: its
    type, tier, rules and book."""
    lines = []
    if definition.category:
        lines.append(f"[b]Type:[/] {definition.category}")
    lines.append(f"[b]Tier:[/] {tier_text(definition)}")
    if definition.unknown:
        lines.append("[dim]May be Unknown.[/]")
    lines += _boon_hook_rule_lines(definition, by_id)
    lines += ["", escape(definition.description)]
    lines += ["", f"[dim]Source: {escape(sourcebooks.titles(definition.source))}[/]"]
    return "\n".join(lines)

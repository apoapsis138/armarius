"""A printed sheet (print_layout.Document) as Markdown: the same record,
copy and sheet the PDF prints, as a text file any editor or wiki reads.

Pattern: a second renderer (an interpreter) over the same Document: the
builders don't change, only what draws their blocks. Markdown can't draw
paper, so the Art and Ability symbols and the lines left to pencil in
(spare weapon rows, Equipment lines, empty wound boxes) are left off; the
Characteristics and facts become short tables, Fatigue and Wounds a small
table each with the current level marked, and every table is a GitHub
one. No UI library."""

from __future__ import annotations

from collections.abc import Callable, Sequence

from . import print_layout as pl

#: Marks the Fatigue level the character is at.
NOW = "◀ now"


def _cell(text: str) -> str:
    """Words for a table cell: one line, its bars escaped."""
    return " ".join(text.split()).replace("|", "\\|")


def _styled(text: str, style: str) -> str:
    if not text.strip():
        return text
    marks = {"bold": "**", "italic": "*", "struck": "~~"}.get(style, "")
    return f"{marks}{text}{marks}" if marks else text


def _table(header: Sequence[str], rows: Sequence[Sequence[str]]) -> str:
    """A GitHub table; a header of blanks keeps a table that has none."""
    head = [_cell(h) or " " for h in header]
    lines = [
        "| " + " | ".join(head) + " |",
        "| " + " | ".join("---" for _ in head) + " |",
    ]
    lines += ["| " + " | ".join(_cell(c) for c in row) + " |" for row in rows]
    return "\n".join(lines)


def _title(b: pl.Title) -> str:
    return f"# {b.name}\n\n*{b.subtitle}*" if b.subtitle else f"# {b.name}"


def _heading(b: pl.Heading) -> str:
    return f"{'#' * (b.level + 1)} {b.text}"


def _boxes(b: pl.ScoreBoxes) -> str:
    return _table([label for label, _ in b.items], [[v for _, v in b.items]])


def _facts(b: pl.Facts) -> str:
    return _table(["", ""], [[f"**{label}**", value] for label, value in b.facts])


def _paragraph(b: pl.Paragraph) -> str:
    return _styled(b.text, b.style)


def _table_block(b: pl.Table) -> str:
    groups = dict(b.groups)
    rows: list[list[str]] = []
    for i, row in enumerate(b.rows):
        if i in groups:
            rows.append([f"**{groups[i]}**", *("" for _ in row[1:])])
        rows.append([_styled(c.text, c.style) for c in row])
    return _table([c.title for c in b.columns], rows)


def _entry(b: pl.Entry) -> str:
    note = f" ({b.note})" if b.note else ""
    summary = f": {b.summary}" if b.summary else ""
    return f"- **{b.name}**{note}{summary}"


def _columns(b: pl.Columns) -> str:
    return _join([*b.left, *b.right])


def _condition(b: pl.Condition) -> str:
    fatigue = _table(
        ["Fatigue", "Penalty", "Recovery", ""],
        [[r.name, r.penalty, r.recovery, ""] for r in b.fatigue.rows],
    )
    # The current level is the last one ticked (Fresh when none is).
    ticked = [i for i, r in enumerate(b.fatigue.rows) if r.ticked]
    now = ticked[-1] if ticked else 0
    lines = fatigue.split("\n")
    lines[2 + now] = lines[2 + now][: -len(" |")] + f"{NOW} |"
    wounds = _table(
        ["Wounds", "Range", "Penalty", "Taken"],
        [[r.name, r.range, r.penalty, str(r.ticked)] for r in b.wounds.rows],
    )
    return "\n".join(lines) + "\n\n" + wounds


def _combat(b: pl.CombatSummary) -> str:
    return _table(
        ["Armor Worn", "Soak", "Load", "Encumbrance"],
        [[b.armour or "—", b.soak, b.load, b.encumbrance]],
    )


def _weapons(b: pl.Weapons) -> str:
    rows = [
        [r.name, r.initiative, r.attack, r.defence, r.damage, r.load]
        for r in b.rows
        if r.name
    ]
    if not rows:
        return ""
    return _table(["Weapon", "Init", "Atk", "Dfn", "Dam", "Load"], rows)


def _equipment(b: pl.Equipment) -> str:
    if not b.items:
        return ""
    return "**Equipment:** " + ", ".join(b.items)


def _grimoire(b: pl.GrimoireTitle) -> str:
    return f"## Grimoire\n\n*The formulaic spells of {b.owner}*"


def _spell(b: pl.Spell) -> str:
    lines = [f"#### {b.name} ({b.arts})", "", b.parameters]
    if b.casting:
        lines += ["", f"*{b.casting}*"]
    if b.description:
        lines += ["", b.description]
    return "\n".join(lines)


#: How each kind of block is written; those left off write "".
_WRITERS: dict[type, Callable[..., str]] = {
    pl.Title: _title,
    pl.Heading: _heading,
    pl.ScoreBoxes: _boxes,
    pl.Facts: _facts,
    pl.Paragraph: _paragraph,
    pl.Table: _table_block,
    pl.Entry: _entry,
    pl.Columns: _columns,
    pl.Flow: lambda b: _join(b.blocks),
    pl.Condition: _condition,
    pl.CombatSummary: _combat,
    pl.Weapons: _weapons,
    pl.Equipment: _equipment,
    pl.GrimoireTitle: _grimoire,
    pl.Spell: _spell,
    pl.Blanks: lambda _b: "",
    pl.NewPage: lambda _b: "",
}


def _level(block: pl.Block) -> int:
    """How high a block stands as a heading: a chapter's 1, a section's 2,
    the Grimoire's title 1; anything else heads nothing (99)."""
    if isinstance(block, pl.Heading):
        return block.level
    return 1 if isinstance(block, pl.GrimoireTitle | pl.Title) else 99


def _join(blocks: Sequence[pl.Block]) -> str:
    """The blocks written one after another, a blank line between; a run
    of list entries kept as one list."""
    written = [
        (block, text) for block in blocks if (text := _WRITERS[type(block)](block))
    ]
    # A heading with nothing written under it (Raw Vis's pencil lines
    # alone) is left off too.
    kept = [
        (block, text)
        for k, (block, text) in enumerate(written)
        if not isinstance(block, pl.Heading)
        or (k + 1 < len(written) and _level(written[k + 1][0]) > block.level)
    ]
    out: list[str] = []
    for block, text in kept:
        if out and isinstance(block, pl.Entry) and out[-1].startswith("- "):
            out[-1] += "\n" + text
        else:
            out.append(text)
    return "\n\n".join(out)


def render(doc: pl.Document) -> str:
    """`doc` as Markdown, ending in a newline."""
    return _join(doc.blocks) + "\n"

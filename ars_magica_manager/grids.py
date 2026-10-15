"""A list as columns of plain words, drawn by either front-end: the
desktop as a table (tables.Table), the terminal as a list's padded
lines. Both come from the same cells, so the two can't disagree."""

from __future__ import annotations

from dataclasses import dataclass, field

from .markup import escape, fit
from .tables import Table


@dataclass(frozen=True)
class Grid:
    """A list as columns of plain words, each row chosen by its key (an
    index into what the list shows). `styles` colours a cell, by (row,
    column), with a theme colour or style ("$text-warning", "b"); `caps`
    is the widest each column may be on a padded line."""

    columns: list[str]
    rows: list[list[str]]
    keys: list[int | None]
    empty: str
    styles: dict[tuple[int, int], str] = field(default_factory=dict)
    caps: list[int] = field(default_factory=list)
    stretch: int = 0

    def _styled(self, row: int, column: int, words: str) -> str:
        style = self.styles.get((row, column))
        return f"[{style}]{words}[/]" if style else words

    def table(self) -> Table:
        """The grid as a table, for a front-end that draws columns."""
        return Table(
            self.columns,
            [
                [self._styled(r, c, escape(cell)) for c, cell in enumerate(row)]
                for r, row in enumerate(self.rows)
            ],
            list(self.keys),
            markup=True,
            stretch=self.stretch,
        )

    def row_text(self, key: int) -> str:
        """The row chosen by `key` as markup for a details panel: each
        column's title and its words in full; "" for no such row."""
        if key not in self.keys:
            return ""
        row = self.rows[self.keys.index(key)]
        return "\n".join(
            f"[$label]{escape(title)}:[/] {escape(cell)}"
            for title, cell in zip(self.columns, row)
            if cell.strip()
        )

    def lines(self) -> list[tuple[int | None, str]]:
        """The grid as a list's rows (key, markup): a heading of the
        column titles, then each row padded into columns."""
        if not self.rows:
            return [(None, f"[$label]{escape(self.empty)}[/]")]
        widths = []
        for column, title in enumerate(self.columns):
            width = max([len(title), *(len(row[column]) for row in self.rows)])
            cap = self.caps[column] if column < len(self.caps) else 0
            widths.append(min(width, cap) if cap else width)
        last = len(self.columns) - 1

        def padded(cells: list[str], row: int | None) -> str:
            out = []
            for column, cell in enumerate(cells):
                words = fit(cell, widths[column])
                if column == last:
                    words = words.rstrip()
                shown = escape(words)
                if row is not None and (row, column) in self.styles:
                    plain = shown.rstrip()
                    shown = self._styled(row, column, plain) + " " * (
                        len(shown) - len(plain)
                    )
                out.append(shown)
            return "  ".join(out).rstrip()

        lines: list[tuple[int | None, str]] = [
            (None, f"[$label]  {padded(self.columns, None)}[/]")
        ]
        lines += [
            (key, padded(row, index))
            for index, (key, row) in enumerate(zip(self.keys, self.rows, strict=True))
        ]
        return lines

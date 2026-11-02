"""A list as columns and cells, for a front-end that draws real tables
(the desktop) rather than padding each row into a line of text (the
terminal). The same values fill both: a module's `*_table` function sits
beside its padded `*_rows` and reads the record the same way.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Table:
    """Column titles and a row of cells for each, in the same order.

    A cell is app markup (markup.py) when `markup` is set, else plain
    words. `keys`, when given, is what choosing each row picks (an index
    into the list the table shows); a row whose key is None is a heading
    for the rows after it: its first cell spans the row and it can't be
    chosen. With no `keys`, every row is chosen by its own position.
    `stretch` is the column that takes the room the others leave (the
    longest words, usually the name)."""

    columns: list[str]
    rows: list[list[str]]
    keys: list[int | None] | None = None
    markup: bool = False
    stretch: int = 0
    #: Its last row is a total, set off above by a double rule.
    footed: bool = False

    def key(self, row: int) -> int | None:
        """What choosing row `row` picks."""
        return row if self.keys is None else self.keys[row]

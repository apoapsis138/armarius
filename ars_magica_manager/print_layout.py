"""A record laid out for paper: the blocks of its printed sheet, in order,
and where the pages break between them.

This is the printed sheet's content and order, not its drawing: a front-end
measures each block at its column width, asks `paginate` where the pages
break, and draws them. So the paper is laid out once, here, for every
front-end, as the forms are in form_spec.

The rules the pages keep: nothing is cut by a page edge (a block goes on a
page whole, or on the next). A section may run on to the next page: a
table is split between its rows with its header again at the top of each
part, and two columns side by side each run on. A heading goes on a page
only with the first part of what it heads, and the Combat box only with
Weapons and Equipment. A big part of a sheet (a magus's Arts) starts a
page only when less than about a third of the page is left; the Grimoire
and the story always start one.

The blocks and the paginator are here, with the character's sheet and the
session handouts; print_records holds the other kinds and the registry
of them all (LAYOUTS) that picks a builder and the copy's reader.
"""

from __future__ import annotations

from collections.abc import Callable, Hashable, Sequence
from dataclasses import dataclass, field
from typing import Any

from . import cast_sheet, catalog, recap, viewing
from .arts import ART_ABBREVIATIONS, FORMS, TECHNIQUES
from .models import Character, Saga, ScoredTrait
from .rules import combat, derived
from .rules.breakdown import Breakdown
from .sheets import character as cs
from .viewing import Viewer

# ---------------------------------------------------------------- options

LETTER, A4 = "Letter", "A4"
PAPER_SIZES = (LETTER, A4)
#: Each paper size in points (1/72 inch), portrait.
PAPER_POINTS = {LETTER: (612.0, 792.0), A4: (595.0, 842.0)}

#: Who a copy is for: the table (what the players may read) or the
#: storyguide (everything).
PLAYER_COPY, STORYGUIDE_COPY = "player", "storyguide"
COPIES = (PLAYER_COPY, STORYGUIDE_COPY)
#: A character's sheet: a short one to play from, or the whole record.
PLAY_SHEET, FULL_RECORD = "play", "full"
SHEETS = (PLAY_SHEET, FULL_RECORD)
#: The theme a sheet is printed in: each in its House's colours (a magus,
#: their laboratory and familiar in their House's theme; anything else in
#: Scriptorum), or a theme by name (style.palettes).
HOUSE_COLOURS = "house"


@dataclass(frozen=True)
class PrintOptions:
    """What the person chooses before printing: the paper, whether the
    pages are textured parchment or plain white, who the copy is for, for
    a character a play sheet or the full record, and the theme
    (HOUSE_COLOURS or a theme's name)."""

    paper: str = LETTER
    textured: bool = True
    copy: str = PLAYER_COPY
    sheet: str = FULL_RECORD
    theme: str = HOUSE_COLOURS


#: US Letter on textured parchment, a Player copy of the full record, each
#: in its House's colours.
DEFAULT_OPTIONS = PrintOptions()


def reader_for(copy: str, viewer: Viewer, saga: Saga) -> Viewer:
    """Who a copy is printed for: the Storyguide copy is the viewer's own
    reading, and only for one who reads everything; any other copy is
    what the table reads (a storyguide's Player view), and a player always
    reads as themselves, their own character's private parts and all."""
    if copy == STORYGUIDE_COPY and viewing.reads_everything(viewer, saga):
        return viewer
    if viewer.is_storyguide:
        return viewing.viewer_for(viewer.player, player_view=True, hosts=viewer.hosts)
    return viewer


# ---------------------------------------------------------------- blocks


@dataclass(frozen=True)
class Symbol:
    """A symbol drawn beside a word: an Art's ("art", "Creo"), or an
    Ability's mark ("ability", "Magic Theory", "Arcane")."""

    kind: str
    name: str
    category: str = ""


@dataclass(frozen=True)
class Cell:
    """A table cell: its text, how it is set ("" plain, "italic", "bold"),
    and any symbol before it."""

    text: str
    style: str = ""
    symbol: Symbol | None = None


@dataclass(frozen=True)
class Column:
    """A table column: its title, its share of the width, its alignment
    ("l", "c", "r")."""

    title: str
    width: float
    align: str = "l"


@dataclass(frozen=True)
class Title:
    """The record's name in the title face, and the line under it."""

    name: str
    subtitle: str


@dataclass(frozen=True)
class Heading:
    """A chapter's (level 1) or section's (level 2) heading."""

    text: str
    level: int = 1
    symbol: Symbol | None = None


@dataclass(frozen=True)
class ScoreBoxes:
    """Scores in boxes side by side, a big number over a label: the
    Characteristics."""

    items: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class Facts:
    """Labelled values in a grid, a small label over each value."""

    facts: tuple[tuple[str, str], ...]
    columns: int = 4


@dataclass(frozen=True)
class Paragraph:
    text: str
    style: str = ""
    #: "small" for a note, "" for body text.
    size: str = ""


@dataclass(frozen=True)
class Table:
    """A ruled table. `groups` puts a group's name (an Ability category)
    above the row at its index. A `two_up` table sets its rows in two
    columns side by side, each with the header, the second going on where
    the first ends."""

    columns: tuple[Column, ...]
    rows: tuple[tuple[Cell, ...], ...]
    groups: tuple[tuple[int, str], ...] = ()
    two_up: bool = False

    def group_of(self, row: int) -> str:
        """The name of the group the row at `row` is in ("" for none)."""
        found = ""
        for index, name in self.groups:
            if index > row:
                break
            found = name
        return found


@dataclass(frozen=True)
class Entry:
    """A Virtue or Flaw: its name, its tier and category, a summary. A
    `run_in` one sets all three on one run of text, the name first, to
    save the page."""

    name: str
    note: str
    summary: str
    run_in: bool = False


@dataclass(frozen=True)
class Flow:
    """Blocks set as one stream in two columns of equal height, the first
    going on into the second; a heading never ends a column. Over more
    than a page each page fills both columns, the last balanced."""

    blocks: tuple[Block, ...]


@dataclass(frozen=True)
class Columns:
    """Two runs of blocks side by side; each runs on to the next page where
    the page ends, between its blocks."""

    left: tuple[Block, ...]
    right: tuple[Block, ...]
    #: The left run's share of the width.
    split: float = 0.5


@dataclass(frozen=True)
class FatigueRow:
    name: str
    penalty: str
    recovery: str
    ticked: bool


@dataclass(frozen=True)
class FatigueLevels:
    """Fatigue as the printed sheet sets it: a box, the penalty, how long
    it takes to recover and the level, for each; those spent ticked."""

    rows: tuple[FatigueRow, ...]


@dataclass(frozen=True)
class WoundRow:
    name: str
    #: The damage that gives it, for the character's Size.
    range: str
    #: How many boxes the band has, and how many are ticked.
    boxes: int
    ticked: int
    penalty: str


@dataclass(frozen=True)
class Wounds:
    rows: tuple[WoundRow, ...]


@dataclass(frozen=True)
class Condition:
    """Fatigue Levels beside Wounds, kept together."""

    fatigue: FatigueLevels
    wounds: Wounds


@dataclass(frozen=True)
class CombatSummary:
    """Armour worn and modifiers (to pencil in where blank), and Soak, Load
    and Encumbrance."""

    armour: str
    soak: str
    load: str
    encumbrance: str


@dataclass(frozen=True)
class WeaponRow:
    """A weapon the character has, with its totals before the die; a blank
    row has no name."""

    name: str = ""
    initiative: str = ""
    attack: str = ""
    defence: str = ""
    damage: str = ""
    load: str = ""


#: The Weapons table's totals and the sums that make them.
WEAPON_SUMS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("Init", "Qik + Weap − Enc", ("+", "−", "=")),
    ("Atk", "Dex + Abil + Weap", ("+", "+", "=")),
    ("Dfn", "Qik + Abil + Weap", ("+", "+", "=")),
    ("Dam", "Str + Weap", ("+", "=")),
)


@dataclass(frozen=True)
class Weapons:
    """The weapons the character has, then blank rows to pencil more in,
    with the sums as the printed sheet gives them."""

    rows: tuple[WeaponRow, ...]


@dataclass(frozen=True)
class Equipment:
    """Ruled lines in two columns, the character's gear written on the
    first."""

    items: tuple[str, ...]
    lines: int


@dataclass(frozen=True)
class GrimoireTitle:
    """The Grimoire's own title, centred."""

    owner: str


@dataclass(frozen=True)
class Spell:
    """A spell as the book sets it: its name, arts and level, Range,
    Duration and Target, the Casting Total, and its description when the
    full Grimoire is chosen."""

    name: str
    arts: str
    parameters: str
    casting: str
    description: str = ""


@dataclass(frozen=True)
class Blanks:
    """Ruled lines in two columns, to pencil in what changes in play (raw
    vis not yet gathered, stores)."""

    lines: int = 2


@dataclass(frozen=True)
class Passage:
    """A written Handout's words as its Stationery sets them: `text` in
    the app's markup (handout_markup's blocks), where it stands ("l", "c",
    "r"), whether it is a heading, and for a paragraph opening on an
    illuminated initial, the letter drawn large beside it."""

    text: str
    align: str = "l"
    heading: bool = False
    initial: str = ""


@dataclass(frozen=True)
class Flourish:
    """A short ornamental rule, centred."""


@dataclass(frozen=True)
class Picture:
    """A picture, as large as fits the column: its bytes as shown (None
    for one not to hand, printed as a box naming it), the words it is named
    by, its number among a written Handout's own (0 for none), and whether
    it may fill the rest of the page (a picture Handout) rather than stand
    at a placed picture's height."""

    data: bytes | None
    caption: str
    number: int = 0
    page: bool = False


@dataclass(frozen=True)
class NewPage:
    """The next block starts a page; a `soft` one only when less than
    about a third of the page is left."""

    soft: bool = False


Block = (
    Title
    | Heading
    | ScoreBoxes
    | Facts
    | Paragraph
    | Table
    | Entry
    | Flow
    | Columns
    | Condition
    | CombatSummary
    | Weapons
    | Equipment
    | GrimoireTitle
    | Spell
    | Blanks
    | Passage
    | Flourish
    | Picture
    | NewPage
)


def keeps_with_next(block: Block) -> bool:
    """Whether `block` goes on a page only with the block after it: a
    heading (a written Handout's too) with what it heads, and the Combat
    box with Weapons and Equipment, so those never sit alone on a page."""
    if isinstance(block, Passage):
        return block.heading
    return isinstance(block, Heading | CombatSummary | Weapons)


@dataclass
class Document:
    """A record's printed sheet: its name (the running head), the line the
    foot of each page repeats, and its blocks in order. A written Handout
    names the Stationery its pages are drawn on (handout_layout.STATIONERY;
    "" for the printed sheet's own frame)."""

    title: str
    subtitle: str
    blocks: list[Block] = field(default_factory=list)
    stationery: str = ""


# ---------------------------------------------------------------- pagination


@dataclass(frozen=True)
class Piece:
    """A block as the paginator sees it: how tall it is, the space after
    it, and whether it must go on a page with what follows (a heading).

    A table also gives its header's and each row's height, so it can be
    split between rows; a `two_up` one sets its rows in two columns, and
    gives the rows a group starts at (`breaks`, where a column is best
    split) and the height of a group's name set again atop a column that
    starts inside it (`cont`). Columns side by side give each run's block
    heights (`runs`) and which of those are kept with the next
    (`run_keeps`). A `soft` new page breaks only when little is left."""

    height: float
    gap: float = 0.0
    keep_with_next: bool = False
    new_page: bool = False
    header: float = 0.0
    rows: tuple[float, ...] = ()
    soft: bool = False
    two_up: bool = False
    breaks: tuple[int, ...] = ()
    cont: float = 0.0
    runs: tuple[tuple[float, ...], ...] = ()
    run_keeps: tuple[tuple[bool, ...], ...] = ()
    #: Kept whole, from a new page if need be (a Grimoire's spell), and
    #: split between its rows only when it is longer than a page.
    whole: bool = False


@dataclass(frozen=True)
class Placement:
    """Where a piece goes on its page: `index` into the pieces, the top,
    and for part of a split table the rows (`first` to `last`, exclusive)
    and whether its header is repeated above them. Part of a two-up table
    or of columns side by side gives each column's span (`spans`, first
    and last, exclusive)."""

    index: int
    top: float
    first: int = 0
    last: int = 0
    header: bool = True
    spans: tuple[tuple[int, int], ...] = ()


#: The fewest rows of a table set at the foot of a page: a shorter table
#: moves whole.
MIN_ROWS = 3
#: A soft new page breaks when the page is filled past this share.
SOFT_BREAK = 2 / 3


def column_height(piece: Piece, first: int, last: int) -> float:
    """The height of a two-up table's rows `first` to `last` set as one
    column, with its group's name set again atop it when it starts inside
    a group."""
    if first >= last:
        return 0.0
    again = piece.cont if first not in piece.breaks and first > 0 else 0.0
    return again + sum(piece.rows[first:last])


def balance(piece: Piece, first: int, last: int) -> int:
    """Where a two-up table's rows `first` to `last` are best split between
    its two columns: as even as can be, at the start of a group where that
    costs little."""
    best, best_cost = last, float("inf")
    for split in range(first + 1, last + 1):
        tall = max(
            column_height(piece, first, split), column_height(piece, split, last)
        )
        inside = split < last and split not in piece.breaks
        cost = tall + (2 * piece.cont if inside else 0.0)
        if cost < best_cost:
            best, best_cost = split, cost
    return best


def two_up_height(piece: Piece) -> float:
    """A two-up table's height when it is set whole: its header and the
    taller of its balanced columns."""
    split = balance(piece, 0, len(piece.rows))
    n = len(piece.rows)
    return piece.header + max(
        column_height(piece, 0, split), column_height(piece, split, n)
    )


class _Paginator:
    """Lays pieces onto pages top to bottom, keeping track of the page
    being filled and how far down it is."""

    def __init__(self, pieces: Sequence[Piece], page_height: float) -> None:
        self.pieces = pieces
        self.height = page_height
        self.pages: list[list[Placement]] = [[]]
        self.y = 0.0

    def new_page(self) -> None:
        if self.pages[-1]:
            self.pages.append([])
        self.y = 0.0

    def splits(self, piece: Piece) -> bool:
        """Whether a piece may run on to the next page: columns side by
        side, or a table long enough to leave the fewest rows on each; a
        piece kept whole only when it is longer than a page."""
        if piece.whole:
            return bool(piece.rows) and piece.height > self.height
        return bool(piece.runs) or len(piece.rows) >= 2 * MIN_ROWS

    def first_part(self, piece: Piece) -> float:
        """The room a piece needs to start on this page."""
        if piece.runs:
            start = max(sum(run[:2]) for run in piece.runs)
            return min(piece.height, start)
        if self.splits(piece):
            return min(piece.height, piece.header + sum(piece.rows[:MIN_ROWS]))
        return piece.height

    def run_from(self, i: int) -> list[int]:
        """The piece at `i` with any it is kept with: a heading and the
        piece it heads, Combat & Condition's parts."""
        run = [i]
        while self.pieces[run[-1]].keep_with_next and run[-1] + 1 < len(self.pieces):
            if self.pieces[run[-1] + 1].new_page:
                break
            run.append(run[-1] + 1)
        return run

    def place(self, k: int) -> None:
        piece = self.pieces[k]
        if self.y and self.y + piece.height > self.height:
            self.new_page()
        self.pages[-1].append(Placement(k, self.y))
        self.y += piece.height + piece.gap

    def place_split(self, k: int) -> None:
        """A table that runs on, split between its rows, its header at the
        top of each part."""
        piece = self.pieces[k]
        first = 0
        while first < len(piece.rows):
            room = self.height - self.y - piece.header
            last = first
            while last < len(piece.rows) and piece.rows[last] <= room:
                room -= piece.rows[last]
                last += 1
            if last == first:
                if self.y:
                    self.new_page()
                    continue
                last = first + 1  # a row taller than a page
            left = len(piece.rows) - last
            if 0 < left < MIN_ROWS and last - first - (MIN_ROWS - left) >= MIN_ROWS:
                # Never leave a row or two alone at the top of a page.
                last -= MIN_ROWS - left
            self.pages[-1].append(Placement(k, self.y, first, last))
            self.y += piece.header + sum(piece.rows[first:last])
            first = last
            if first < len(piece.rows):
                self.new_page()
        self.y += piece.gap

    def fill(self, piece: Piece, first: int, room: float) -> int:
        """How far a two-up table's column starting at row `first` goes in
        `room`."""
        last = first
        while last < len(piece.rows) and (
            column_height(piece, first, last + 1) <= room
        ):
            last += 1
        return last

    def place_two_up(self, k: int) -> None:
        """A two-up table that runs on: on each page its first column is
        filled, then its second, and the last page's rows are balanced."""
        piece = self.pieces[k]
        n, first = len(piece.rows), 0
        while first < n:
            room = self.height - self.y - piece.header
            split = balance(piece, first, n)
            tall = max(
                column_height(piece, first, split), column_height(piece, split, n)
            )
            if tall <= room:
                self.pages[-1].append(
                    Placement(k, self.y, spans=((first, split), (split, n)))
                )
                self.y += piece.header + tall
                break
            middle = self.fill(piece, first, room)
            if middle == first:
                if self.y:
                    self.new_page()
                    continue
                middle = first + 1  # a row taller than a page
            last = max(self.fill(piece, middle, room), middle)
            self.pages[-1].append(
                Placement(k, self.y, spans=((first, middle), (middle, last)))
            )
            self.y += piece.header + max(
                column_height(piece, first, middle), column_height(piece, middle, last)
            )
            first = last
            if first < n:
                self.new_page()
        self.y += piece.gap

    def place_runs(self, k: int) -> None:
        """Columns side by side that run on: each column takes the blocks
        that fit, never ending on one kept with the next, and goes on on
        the next page."""
        piece = self.pieces[k]
        at = [0] * len(piece.runs)
        while any(a < len(run) for a, run in zip(at, piece.runs, strict=True)):
            room = self.height - self.y
            ends, used = [], []
            for c, run in enumerate(piece.runs):
                end, tall = at[c], 0.0
                while end < len(run) and tall + run[end] <= room:
                    tall += run[end]
                    end += 1
                while end > at[c] and end < len(run) and piece.run_keeps[c][end - 1]:
                    end -= 1
                    tall -= run[end]
                ends.append(end)
                used.append(tall)
            if ends == at:
                if self.y:
                    self.new_page()
                    continue
                ends = [min(a + 1, len(run)) for a, run in zip(at, piece.runs)]
                used = [sum(run[a:e]) for a, e, run in zip(at, ends, piece.runs)]
            self.pages[-1].append(
                Placement(k, self.y, spans=tuple(zip(at, ends, strict=True)))
            )
            self.y += max(used)
            at = ends
            if any(a < len(run) for a, run in zip(at, piece.runs, strict=True)):
                self.new_page()
        self.y += piece.gap

    def lay_out(self) -> list[list[Placement]]:
        i = 0
        while i < len(self.pieces):
            piece = self.pieces[i]
            if piece.new_page:
                if not piece.soft or self.y > self.height * SOFT_BREAK:
                    self.new_page()
                i += 1
                continue
            run = self.run_from(i)
            need = sum(self.pieces[k].height + self.pieces[k].gap for k in run[:-1])
            need += self.first_part(self.pieces[run[-1]])
            if self.y and self.y + need > self.height:
                self.new_page()
            for k in run:
                piece = self.pieces[k]
                if not self.splits(piece) or self.y + piece.height <= self.height:
                    self.place(k)
                elif piece.runs:
                    self.place_runs(k)
                elif piece.two_up:
                    self.place_two_up(k)
                else:
                    self.place_split(k)
            i = run[-1] + 1
        return [page for page in self.pages if page] or [[]]


def paginate(pieces: Sequence[Piece], page_height: float) -> list[list[Placement]]:
    """The pages, each a list of placements, for `pieces` on pages whose
    printed area is `page_height` tall."""
    return _Paginator(pieces, page_height).lay_out()


# ---------------------------------------------------------------- a character


def signed(n: int) -> str:
    return f"+{n}" if n > 0 else str(n).replace("-", "−")


#: How long each Fatigue level takes to recover, as the printed sheet gives it.
FATIGUE_RECOVERY = {
    "Fresh": "",
    "Winded": "2 min.",
    "Weary": "10 min.",
    "Tired": "30 min.",
    "Dazed": "1 hr.",
    "Unconscious": "2 hr.",
}
#: The wound bands with a box for each wound (the others have one box).
COUNTED_WOUNDS = ("Light", "Medium", "Heavy")
#: Blank rows the Weapons table and Equipment always leave to pencil in.
SPARE_WEAPONS, SPARE_LINES = 2, 2


def condition_block(character: Character) -> Condition:
    return condition_from(cs.fatigue_track(character), cs.wound_track(character))


def condition_from(
    levels: Sequence[tuple[str, int, bool]], bands: Sequence[cs.WoundBand]
) -> Condition:
    """Fatigue Levels beside Wounds, from a character's or familiar's
    Fatigue track (name, penalty, whether it is the current level) and
    wound bands."""
    current = next((i for i, (_, _, now) in enumerate(levels) if now), 0)
    fatigue = tuple(
        FatigueRow(
            name,
            ""
            if name in ("Fresh", "Unconscious")
            else (signed(penalty) if penalty else "0"),
            FATIGUE_RECOVERY.get(name, ""),
            0 < i <= current,
        )
        for i, (name, penalty, _) in enumerate(levels)
    )
    wounds = tuple(
        WoundRow(
            "Incapacitated" if band.name == "Incapacitating" else band.name,
            f"{band.low}–{band.high}" if band.high is not None else f"{band.low}+",
            5 if band.name in COUNTED_WOUNDS else 1,
            band.count,
            signed(band.penalty) if band.penalty else "",
        )
        for band in bands
    )
    return Condition(FatigueLevels(fatigue), Wounds(wounds))


def combat_blocks(character: Character, *, play: bool = False) -> list[Block]:
    """Combat & Condition, as the printed ArM5 sheet sets it out; a play
    sheet leaves fewer blank lines to pencil in."""
    inventory = character.inventory
    load = derived.carried_load(inventory)
    encumbrance = derived.encumbrance(load, character.characteristics.strength)
    soak = int(derived.soak(character).total)

    def total(part: Breakdown | None) -> str:
        return "—" if part is None else signed(int(part.total))

    weapons = []
    for weapon in (item for item in inventory if item.kind == "weapon"):
        totals = combat.combat_totals(character, weapon)
        weapons.append(
            WeaponRow(
                weapon.name,
                total(totals.initiative),
                total(totals.attack),
                total(totals.defence),
                total(totals.damage),
                str(weapon.load or 0),
            )
        )
    gear = tuple(item.name for item in inventory if item.kind != "weapon")
    if play:
        blanks, lines = 1, -(-len(gear) // 2) + 1
    else:
        blanks = max(SPARE_WEAPONS, 5 - len(weapons))
        lines = max(5, -(-len(gear) // 2) + SPARE_LINES)
    return [
        Heading("Combat & Condition"),
        condition_block(character),
        CombatSummary(
            ", ".join(item.name for item in inventory if item.kind == "armor"),
            signed(soak),
            str(load),
            str(encumbrance),
        ),
        Weapons(tuple(weapons) + (WeaponRow(),) * blanks),
        Equipment(gear, lines),
    ]


def fact_pairs(
    facts: Sequence[cs.Fact], reader: Viewer = viewing.STORYGUIDE_VIEWER
) -> tuple[tuple[str, str], ...]:
    """The facts given, as `reader` may read them (an unknown record they
    name taken out), with any missing left off."""
    return tuple(
        (f.label, f.value) for f in viewing.facts(facts, reader) if not f.missing
    )


def abilities_blocks(rows: Sequence[cs.AbilityRow]) -> list[Block]:
    """Abilities (a character's or a familiar's rows) in two columns, by
    category."""
    if not rows:
        return []
    groups, last = [], None
    for index, row in enumerate(rows):
        if row.category != last:
            groups.append((index, row.category))
            last = row.category
    return [
        Heading("Abilities"),
        Table(
            (
                Column("Ability", 0.45),
                Column("Specialty", 0.26),
                Column("Score", 0.13, "c"),
                Column("Exp.", 0.16, "r"),
            ),
            tuple(
                (
                    Cell(row.name, symbol=Symbol("ability", row.name, row.category)),
                    Cell(row.specialty, "italic"),
                    Cell(row.score, "bold"),
                    Cell(f"{row.xp}/{row.next_xp}"),
                )
                for row in rows
            ),
            tuple(groups),
            two_up=True,
        ),
    ]


def stacked[C](
    cards: Sequence[C], same: Callable[[C], Hashable] | None = None
) -> list[tuple[C, int]]:
    """Each card once, with how many times it was taken (Great
    Intelligence twice, a Boon taken twice, is one entry), in the order
    first taken. `same` says which cards are the same one (by default a
    Virtue's or Flaw's name, tier, category and summary)."""

    def alike(card: C) -> Hashable:
        if same is not None:
            return same(card)
        return tuple(getattr(card, k) for k in ("name", "tier", "category", "summary"))

    counts: dict[Hashable, int] = {}
    first: dict[Hashable, C] = {}
    for card in cards:
        key = alike(card)
        counts[key] = counts.get(key, 0) + 1
        first.setdefault(key, card)
    return [(first[key], n) for key, n in counts.items()]


def counted(name: str, times: int) -> str:
    """A name taken `times` times, as paper prints it: "Great
    Intelligence × 2"."""
    return name if times == 1 else f"{name} × {times}"


def _virtues_flaws(character: Character) -> list[Block]:
    return virtue_flaw_columns(
        [
            (
                label,
                cs.virtue_flaw_cards(character, side),
                cs.virtue_flaw_points(character, side),
            )
            for side, label in (("Virtue", "Virtues"), ("Flaw", "Flaws"))
        ]
    )


def virtue_flaw_columns(
    sides: Sequence[tuple[str, Sequence[Any], float | None]],
) -> list[Block]:
    """The Virtues, then the Flaws (each side's title, cards and points), a
    character's or a familiar's, as one stream in two balanced columns,
    each run in on one line of text; one taken more than once is printed
    once, as "Great Intelligence × 2", to save the paper."""
    stream: list[Block] = []
    for label, taken, points in sides:
        cards = stacked(taken)
        if not cards:
            continue
        title = label if points is None else f"{label} · {points:g} points"
        stream.append(Heading(title, 2))
        stream += [
            Entry(
                counted(card.name, n),
                " · ".join(p for p in (card.tier, card.category) if p),
                card.summary,
                run_in=True,
            )
            for card, n in cards
        ]
    return [Flow(tuple(stream))] if stream else []


def _virtue_flaw_names(character: Character) -> list[Block]:
    """The Virtues beside the Flaws, by name only, for a play sheet."""
    sides = []
    for side, label in (("Virtue", "Virtues"), ("Flaw", "Flaws")):
        cards = stacked(cs.virtue_flaw_cards(character, side))
        sides.append(
            (
                Heading(label, 2),
                Paragraph(
                    ", ".join(c.name if n == 1 else f"{c.name} × {n}" for c, n in cards)
                ),
            )
            if cards
            else ()
        )
    if not any(sides):
        return []
    return [Columns(sides[0], sides[1])]


def traits_blocks(
    personality: Sequence[ScoredTrait], reputations: Sequence[ScoredTrait]
) -> list[Block]:
    """Personality Traits, then Reputations, each while there are some."""
    blocks: list[Block] = []
    for title, traits in (
        ("Personality Traits", personality),
        ("Reputations", reputations),
    ):
        if traits:
            blocks += [
                Heading(title, 2),
                Facts(tuple((t.name, signed(t.score)) for t in traits)),
            ]
    return blocks


def _arts_table(
    character: Character, arts: Sequence[str], two_up: bool = False
) -> Table:
    return Table(
        (Column("Art", 0.55), Column("Score", 0.2, "c"), Column("Exp.", 0.25, "r")),
        tuple(
            (
                Cell(row.art, "italic", Symbol("art", row.art)),
                Cell(row.score, "bold"),
                Cell(f"{row.xp}/{row.next_xp}"),
            )
            for row in cs.art_rows(character, arts)
        ),
        two_up=two_up,
    )


def _arts_and_casting(
    saga: Saga, character: Character, *, note: bool = True
) -> list[Block]:
    """The Arts in three columns, the Techniques beside the Forms in two,
    then the Casting Scores (with a note on what they count, unless
    `note` is False)."""
    grid = cs.casting_grid(saga, character)
    blocks: list[Block] = [
        Heading("Hermetic Arts"),
        Columns(
            (_arts_table(character, TECHNIQUES),),
            (_arts_table(character, FORMS, two_up=True),),
            1 / 3,
        ),
        Heading("Casting Scores", 2),
        Table(
            (Column("", 0.17),)
            + tuple(Column(ART_ABBREVIATIONS[f], 0.083, "c") for f in FORMS),
            tuple(
                (Cell(t, "italic", Symbol("art", t)),)
                + tuple(Cell(str(int(grid[(t, f)].total))) for f in FORMS)
                for t in TECHNIQUES
            ),
        ),
    ]
    if note:
        blocks.append(
            Paragraph(
                "Casting Score: Technique + Form + Stamina + aura, before the die, "
                "in the magus's home aura.",
                "italic",
                "small",
            )
        )
    return blocks


def _raw_vis(character: Character, lines: int = 2) -> list[Block]:
    """The magus's raw vis, then lines to pencil in what changes in play
    (`lines` of them alone when there is none yet, else one)."""
    vis = {art: pawns for art, pawns in character.raw_vis.items() if pawns}
    blocks: list[Block] = [Heading("Raw Vis", 2)]
    if vis:
        blocks.append(
            Facts(
                tuple(
                    (art.title(), f"{n} pawn{'' if n == 1 else 's'}")
                    for art, n in vis.items()
                ),
                5,
            )
        )
    return [*blocks, Blanks(1 if vis else lines)]


def _hermetic_magic(saga: Saga, character: Character, reader: Viewer) -> list[Block]:
    """From a new page: the Hermetic Background and Wizard's Sigil, then
    the Arts, Casting Scores, raw vis and research goals."""
    # Soft: the Virtues and Flaws running on from page 2 share its page.
    blocks: list[Block] = [NewPage(soft=True)]
    hermetic = fact_pairs(cs.hermetic_facts(character), reader)
    sigil = character.hermetic.wizards_sigil
    if hermetic or sigil:
        blocks.append(Heading("Hermetic Background"))
    if hermetic:
        blocks.append(Facts(hermetic, 3))
    if sigil:
        blocks.append(Paragraph(f"Wizard's Sigil: {sigil}", "italic"))
    # The Casting Score note and a single pencil line keep Raw Vis on the
    # Arts' page rather than alone on the next.
    blocks += [*_arts_and_casting(saga, character, note=False), *_raw_vis(character, 1)]
    if character.breakthroughs:
        blocks += [
            Heading("Research Goals", 2),
            Table(
                (Column("Goal", 0.6), Column("Kind", 0.2), Column("Points", 0.2, "r")),
                tuple(
                    (Cell(g.name), Cell(g.kind), Cell(f"{g.points} / {g.target}"))
                    for g in character.breakthroughs
                ),
            ),
        ]
    return blocks


def _spell_order(row: cs.SpellRow) -> tuple[int, int, str]:
    """The Grimoire's order: by Form, highest level first, then by name."""
    form = FORMS.index(row.form) if row.form in FORMS else len(FORMS)
    return (form, -(row.level or 0), row.name)


def _casting_total(grid: dict[tuple[str, str], Breakdown], row: cs.SpellRow) -> str:
    """A spell's Casting Total before the die, with its Mastery ("" when
    its Arts aren't on the grid)."""
    score = grid.get((row.technique, row.form))
    return "" if score is None else str(int(score.total) + row.mastery)


def _arts_level(row: cs.SpellRow) -> str:
    level = "Gen." if row.level is None else str(row.level)
    return f"{row.arts} {level}" + (" · Ritual" if row.ritual else "")


def _spell_lines(saga: Saga, character: Character) -> list[Block]:
    """The spells one line each, for a play sheet: name, Arts and level,
    Range, Duration and Target, and Casting Total."""
    rows = sorted(cs.spell_table(saga, character), key=_spell_order)
    if not rows:
        return []
    grid = cs.casting_grid(saga, character)
    return [
        Heading("Spells", 2),
        Table(
            (
                Column("Spell", 0.38),
                Column("Arts & Level", 0.18),
                Column("R / D / T", 0.32),
                Column("Casting", 0.12, "c"),
            ),
            tuple(
                (
                    Cell(row.name, "bold"),
                    Cell(_arts_level(row)),
                    Cell(f"{row.range} / {row.duration} / {row.target}"),
                    Cell(_casting_total(grid, row)),
                )
                for row in rows
            ),
        ),
    ]


def _grimoire(saga: Saga, character: Character) -> list[Block]:
    """The Grimoire, last, from a new page: the spells by Form, each with
    its description; a spell is a block, so it is never split between
    pages."""
    rows = cs.spell_table(saga, character)
    if not rows:
        return []
    grid = cs.casting_grid(saga, character)
    blocks: list[Block] = [NewPage(), GrimoireTitle(character.name)]
    last = None
    for row in sorted(rows, key=_spell_order):
        if row.form != last:
            symbol = Symbol("art", row.form) if row.form in FORMS else None
            blocks.append(Heading(row.form or "Unknown", 2, symbol))
            last = row.form
        total = _casting_total(grid, row)
        casting = f"Casting Total {total} + die" if total else ""
        if row.mastery:
            casting += f" · Mastery {row.mastery}"
        spell = catalog.find_spell(saga, character.spells_known[row.index].spell_id)
        description = spell.description if spell else ""
        blocks.append(
            Spell(
                row.name,
                _arts_level(row),
                f"R: {row.range}, D: {row.duration}, T: {row.target}",
                casting,
                description,
            )
        )
    return blocks


def paragraphs(text: str, style: str = "") -> list[Block]:
    """Words as paragraphs, one for each run of lines a blank line ends."""
    return [
        Paragraph(part.strip(), style) for part in text.split("\n\n") if part.strip()
    ]


def secrets_blocks(record: Any) -> list[Block]:
    """A record's Secrets, each under its title and marked revealed or not:
    whatever the record passed in holds, which for a Player copy is only
    those revealed (viewing.as_read_by)."""
    found = getattr(record, "secrets", None) or []
    if not found:
        return []
    blocks: list[Block] = [Heading("Secrets")]
    for secret in found:
        blocks.append(Heading(secret.title or "Secret", 2))
        blocks += paragraphs(secret.text)
        when = (
            f"Revealed {secret.revealed_season} {secret.revealed_year}".replace(
                "  ", " "
            )
            if secret.revealed
            else "Not revealed to the players"
        )
        blocks.append(Paragraph(when, "italic", "small"))
    return blocks


def _notes_and_goals(character: Character) -> list[Block]:
    """The player's own notes and goals: on a copy whose reader may read
    them (viewing.as_read_by leaves them off otherwise; a shared goal is
    the troupe's)."""
    if not (character.private_notes.strip() or character.goals):
        return []
    blocks: list[Block] = [Heading("Notes & Goals")]
    blocks += paragraphs(character.private_notes)
    blocks += [Paragraph(f"Goal: {g.text}") for g in character.goals if g.text]
    return blocks


def _familiar_box(saga: Saga, character: Character) -> list[Block]:
    """The familiar in short; its own sheet prints from its own page."""
    familiar = saga.familiar_of(character.id)
    if familiar is None:
        return []
    return [
        Heading("Familiar"),
        Facts(
            (
                ("Name", familiar.name),
                ("Species", familiar.species),
                ("Magic Might", str(familiar.magic_might)),
                (
                    "Cords",
                    f"Golden {familiar.golden_cord} · Silver {familiar.silver_cord}"
                    f" · Bronze {familiar.bronze_cord}",
                ),
            )
        ),
        Paragraph(
            f"{familiar.name or 'The familiar'}'s full sheet prints from its own page.",
            "italic",
            "small",
        ),
    ]


def _story(saga: Saga, character: Character, reader: Viewer) -> list[Block]:
    blocks: list[Block] = []
    biography = fact_pairs(cs.biographical_facts(saga, character), reader)
    if biography:
        blocks.append(Facts(biography))
    d = character.description
    if d.physical_description:
        blocks += [Heading("Appearance", 2), Paragraph(d.physical_description)]
    if d.biography:
        blocks.append(Heading("Biography", 2))
        blocks += paragraphs(d.biography)
    if blocks:
        blocks.insert(0, Heading("Description & Biography"))
    blocks += _familiar_box(saga, character)
    books = [
        b
        for b in saga.books
        if b.owner_kind == "character" and b.owner_id == character.id
    ]
    if books:
        blocks += [
            Heading("Books"),
            Table(
                (
                    Column("Title", 0.42),
                    Column("Type", 0.18),
                    Column("Subject", 0.16),
                    Column("Level", 0.12, "c"),
                    Column("Quality", 0.12, "c"),
                ),
                tuple(
                    (
                        Cell(b.name, "italic"),
                        Cell(b.type),
                        Cell(b.art or b.ability),
                        Cell(str(b.level) if b.level else ""),
                        Cell(str(b.quality) if b.quality else ""),
                    )
                    for b in books
                ),
            ),
        ]
    if character.diary:
        blocks += [
            Heading("Diary"),
            Table(
                (
                    Column("Season", 0.18),
                    Column("Activity", 0.22),
                    Column("Entry", 0.60),
                ),
                tuple(
                    (Cell(f"{e.season} {e.year}"), Cell(e.activity or ""), Cell(e.name))
                    for e in character.diary
                ),
            ),
        ]
    blocks += _notes_and_goals(character)
    blocks += secrets_blocks(character)
    return [NewPage(), *blocks] if blocks else []


#: The Characteristics, in the printed sheet's order.
CHARACTERISTICS = (
    "Intelligence",
    "Perception",
    "Strength",
    "Stamina",
    "Presence",
    "Communication",
    "Dexterity",
    "Quickness",
)


def _characteristics(character: Character) -> ScoreBoxes:
    ch = character.characteristics
    return ScoreBoxes(
        tuple((name, signed(getattr(ch, name.lower()))) for name in CHARACTERISTICS)
    )


def character_document(
    saga: Saga,
    character: Character,
    options: PrintOptions = DEFAULT_OPTIONS,
    reader: Viewer = viewing.STORYGUIDE_VIEWER,
) -> Document:
    """A character's printed sheet, the play sheet or the full record as
    `options` chooses, as `reader` may read it."""
    if options.sheet == PLAY_SHEET:
        return play_sheet(saga, character)
    return full_record(saga, character, options, reader)


def play_sheet(saga: Saga, character: Character) -> Document:
    """A character's sheet to play from, about one page (two for a magus):
    the Characteristics, Virtues and Flaws by name, traits, Abilities and
    Combat & Condition; for a magus then the Arts, Casting Scores, raw vis
    and the spells a line each. No story, books or diary."""
    subtitle = cs.subtitle(saga, character)
    blocks: list[Block] = [Title(character.name, subtitle), _characteristics(character)]
    blocks += _virtue_flaw_names(character)
    blocks += traits_blocks(character.personality_traits, character.reputations)
    blocks += abilities_blocks(cs.ability_table(character))
    blocks += combat_blocks(character, play=True)
    if character.type == "magus":
        blocks += [NewPage(soft=True), *_arts_and_casting(saga, character, note=False)]
        blocks += _raw_vis(character, 1)
        blocks += _spell_lines(saga, character)
    return Document(character.name, subtitle, blocks)


def full_record(
    saga: Saga,
    character: Character,
    options: PrintOptions = DEFAULT_OPTIONS,
    reader: Viewer = viewing.STORYGUIDE_VIEWER,
) -> Document:
    """A character's whole printed record. Page 1: who they are, their
    Personality Traits, Abilities and Combat & Condition, which runs on to
    the next page with the Virtues and Flaws. For a magus, from a new page,
    the Hermetic Background and Arts. From a new page their story, books,
    diary, notes and the Secrets the copy's reader may read; last, from a
    new page, the Grimoire, each spell in full and never split."""
    subtitle = cs.subtitle(saga, character)
    a = character.aging
    b = character.background
    blocks: list[Block] = [
        Title(character.name, subtitle),
        _characteristics(character),
        Facts(
            fact_pairs(cs.glance_facts(saga, character), reader)
            + (
                ("Confidence", f"{b.confidence_score} ({b.confidence_points} points)"),
                ("Warping", f"{a.warping_score} ({a.warping_points} points)"),
                ("Decrepitude", f"{a.decrepitude} ({a.decrepitude_points} points)"),
            )
        ),
    ]
    blocks += traits_blocks(character.personality_traits, character.reputations)
    blocks += abilities_blocks(cs.ability_table(character))
    blocks += combat_blocks(character)
    virtues_flaws = _virtues_flaws(character)
    if virtues_flaws:
        blocks += [Heading("Virtues & Flaws"), *virtues_flaws]
    magus = character.type == "magus"
    if magus:
        blocks += _hermetic_magic(saga, character, reader)
    blocks += _story(saga, character, reader)
    if magus:
        blocks += _grimoire(saga, character)
    return Document(character.name, subtitle, blocks)


def cast_document(saga: Saga, title: str, cast: list[Character]) -> Document:
    """The cast at a glance on one page (cast_sheet.py): a table of each
    one's figures, then each one's traits and chosen spells."""
    found = cast_sheet.rows(saga, cast)
    columns = (
        Column("Character", 0.22),
        Column("Weapon", 0.14),
        *(
            Column(t, 0.08 if t in ("Wounds", "Fatigue") else 0.0533, "c")
            for t in cast_sheet.COLUMNS
        ),
    )
    blocks: list[Block] = [
        Title(title, "The cast at a glance"),
        Table(
            columns,
            tuple(
                (Cell(r.name, "bold"), Cell(r.weapon, "italic"), *map(Cell, r.figures))
                for r in found
            ),
        ),
    ]
    for r in found:
        if not (r.traits or r.spells):
            continue
        blocks.append(Heading(r.name, 2))
        if r.traits:
            blocks.append(Paragraph(f"Traits: {r.traits}"))
        if r.spells:
            blocks.append(Paragraph(f"Spells: {r.spells}"))
    return Document(title, saga.name, blocks)


def recap_document(saga: Saga, players: bool = False) -> Document:
    """Previously On (recap.py) for paper, to read aloud."""
    blocks: list[Block] = [
        Title(recap.TITLE, recap.lead(saga, players)),
    ]
    found = recap.parts(saga, players)
    if not found:
        blocks.append(Paragraph("Nothing recorded since."))
    for part in found:
        blocks.append(Heading(part.heading, 2))
        blocks.extend(Paragraph(line) for line in part.lines)
    return Document(recap.TITLE, saga.name, blocks)

"""A record laid out for paper: the blocks of its printed sheet, in order,
and where the pages break between them.

This is the printed sheet's content and order, not its drawing: a front-end
measures each block at its column width, asks `paginate` where the pages
break, and draws them. So the paper is laid out once, here, for every
front-end, as the forms are in form_spec.

The rules the pages keep: nothing is cut by a page edge (a block goes on a
page whole, or on the next); a table that fits on one page is never split,
and one longer than a page is split between its rows with its header again
at the top of each page; a heading goes on a page only with the first part
of what it heads; and the big parts of a sheet (a magus's Arts, Grimoire and
story) each start a page.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field

from . import familiars
from . import spells as spl
from .arts import ART_ABBREVIATIONS, FORMS, TECHNIQUES
from .models import Character, Saga
from .rules import combat, derived
from .sheets import character as cs

# ---------------------------------------------------------------- options

LETTER, A4 = "Letter", "A4"
PAPER_SIZES = (LETTER, A4)
#: Each paper size in points (1/72 inch), portrait.
PAPER_POINTS = {LETTER: (612.0, 792.0), A4: (595.0, 842.0)}


@dataclass(frozen=True)
class PrintOptions:
    """What the person chooses before printing: the paper, whether the
    Grimoire gives each spell's full description or only its parameters,
    and whether the pages are textured parchment or plain white."""

    paper: str = LETTER
    full_spells: bool = False
    textured: bool = True


#: US Letter, spells by their parameters only, on textured parchment.
DEFAULT_OPTIONS = PrintOptions()


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
    above the row at its index."""

    columns: tuple[Column, ...]
    rows: tuple[tuple[Cell, ...], ...]
    groups: tuple[tuple[int, str], ...] = ()


@dataclass(frozen=True)
class Entry:
    """A Virtue or Flaw: its name, its tier and category, a summary."""

    name: str
    note: str
    summary: str


@dataclass(frozen=True)
class Columns:
    """Two runs of blocks side by side, kept together on one page."""

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
class NewPage:
    """The next block starts a page."""


Block = (
    Title
    | Heading
    | ScoreBoxes
    | Facts
    | Paragraph
    | Table
    | Entry
    | Columns
    | Condition
    | CombatSummary
    | Weapons
    | Equipment
    | GrimoireTitle
    | Spell
    | NewPage
)


@dataclass
class Document:
    """A record's printed sheet: its name (the running head), the line the
    foot of each page repeats, and its blocks in order."""

    title: str
    subtitle: str
    blocks: list[Block] = field(default_factory=list)


# ---------------------------------------------------------------- pagination


@dataclass(frozen=True)
class Piece:
    """A block as the paginator sees it: how tall it is, the space after
    it, and whether it must go on a page with what follows (a heading).
    A table also gives its header's and each row's height, so one longer
    than a page can be split between rows."""

    height: float
    gap: float = 0.0
    keep_with_next: bool = False
    new_page: bool = False
    header: float = 0.0
    rows: tuple[float, ...] = ()


@dataclass(frozen=True)
class Placement:
    """Where a piece goes on its page: `index` into the pieces, the top,
    and for part of a split table the rows (`first` to `last`, exclusive)
    and whether its header is repeated above them."""

    index: int
    top: float
    first: int = 0
    last: int = 0
    header: bool = True


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
        """Whether a piece is a table too long for any page, so is split."""
        return bool(piece.rows) and piece.height > self.height

    def first_part(self, piece: Piece) -> float:
        """The room a piece needs to start on this page."""
        if self.splits(piece):
            return piece.header + sum(piece.rows[:3])
        return piece.height

    def run_from(self, i: int) -> list[int]:
        """The piece at `i` with any it is kept with: a heading and the
        piece it heads."""
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
        """A table too long for a page, between its rows, its header at
        the top of each part."""
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
            self.pages[-1].append(Placement(k, self.y, first, last))
            self.y += piece.header + sum(piece.rows[first:last])
            first = last
            if first < len(piece.rows):
                self.new_page()
        self.y += piece.gap

    def lay_out(self) -> list[list[Placement]]:
        i = 0
        while i < len(self.pieces):
            if self.pieces[i].new_page:
                self.new_page()
                i += 1
                continue
            run = self.run_from(i)
            need = sum(self.pieces[k].height + self.pieces[k].gap for k in run[:-1])
            need += self.first_part(self.pieces[run[-1]])
            if self.y and self.y + need > self.height:
                self.new_page()
            for k in run:
                if self.splits(self.pieces[k]):
                    self.place_split(k)
                else:
                    self.place(k)
            i = run[-1] + 1
        return [page for page in self.pages if page] or [[]]


def paginate(pieces: Sequence[Piece], page_height: float) -> list[list[Placement]]:
    """The pages, each a list of placements, for `pieces` on pages whose
    printed area is `page_height` tall."""
    return _Paginator(pieces, page_height).lay_out()


# ---------------------------------------------------------------- a character


def _signed(n: int) -> str:
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
    levels = cs.fatigue_track(character)
    current = next((i for i, (_, _, now) in enumerate(levels) if now), 0)
    fatigue = tuple(
        FatigueRow(
            name,
            ""
            if name in ("Fresh", "Unconscious")
            else (_signed(penalty) if penalty else "0"),
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
            _signed(band.penalty) if band.penalty else "",
        )
        for band in cs.wound_track(character)
    )
    return Condition(FatigueLevels(fatigue), Wounds(wounds))


def combat_blocks(character: Character) -> list[Block]:
    """Combat & Condition, as the printed ArM5 sheet sets it out."""
    inventory = character.inventory
    load = derived.carried_load(inventory)
    encumbrance = derived.encumbrance(load, character.characteristics.strength)
    soak = int(derived.soak(character).total)

    def total(part) -> str:
        return "—" if part is None else _signed(int(part.total))

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
    blanks = max(SPARE_WEAPONS, 5 - len(weapons))
    gear = tuple(item.name for item in inventory if item.kind != "weapon")
    return [
        Heading("Combat & Condition"),
        condition_block(character),
        CombatSummary(
            ", ".join(item.name for item in inventory if item.kind == "armor"),
            _signed(soak),
            str(load),
            str(encumbrance),
        ),
        Weapons(tuple(weapons) + (WeaponRow(),) * blanks),
        Equipment(gear, max(5, -(-len(gear) // 2) + SPARE_LINES)),
    ]


def _facts(facts: Sequence[cs.Fact]) -> tuple[tuple[str, str], ...]:
    return tuple((f.label, f.value) for f in facts if not f.missing)


def _abilities(character: Character) -> list[Block]:
    rows = cs.ability_table(character)
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
                Column("Ability", 0.42),
                Column("Specialty", 0.30),
                Column("Score", 0.10, "c"),
                Column("Experience", 0.18, "r"),
            ),
            tuple(
                (
                    Cell(row.name, symbol=Symbol("ability", row.name, row.category)),
                    Cell(row.specialty, "italic"),
                    Cell(row.score, "bold"),
                    Cell(f"{row.xp} / {row.next_xp}"),
                )
                for row in rows
            ),
            tuple(groups),
        ),
    ]


def stacked(cards: Sequence[cs.VirtueFlawCard]) -> list[tuple[cs.VirtueFlawCard, int]]:
    """Each Virtue or Flaw once, with how many times it was taken (Great
    Intelligence twice is one entry), in the order first taken."""
    counts: dict[tuple[str, str, str, str], int] = {}
    first: dict[tuple[str, str, str, str], cs.VirtueFlawCard] = {}
    for card in cards:
        same = (card.name, card.tier, card.category, card.summary)
        counts[same] = counts.get(same, 0) + 1
        first.setdefault(same, card)
    return [(first[same], n) for same, n in counts.items()]


def _virtues_flaws(character: Character) -> list[Block]:
    """The Virtues beside the Flaws; one taken more than once is printed
    once, as "Great Intelligence × 2", to save the paper."""
    sides = []
    for side, label in (("Virtue", "Virtues"), ("Flaw", "Flaws")):
        cards = stacked(cs.virtue_flaw_cards(character, side))
        points = cs.virtue_flaw_points(character, side)
        sides.append(
            (Heading(f"{label} · {points:g} points", 2),)
            + tuple(
                Entry(
                    card.name if n == 1 else f"{card.name} × {n}",
                    f"{card.tier} · {card.category}",
                    card.summary,
                )
                for card, n in cards
            )
            if cards
            else ()
        )
    if not any(sides):
        return []
    return [Columns(sides[0], sides[1])]


def _traits(character: Character) -> list[Block]:
    blocks: list[Block] = []
    for title, traits in (
        ("Personality Traits", character.personality_traits),
        ("Reputations", character.reputations),
    ):
        if traits:
            blocks += [
                Heading(title, 2),
                Facts(tuple((t.name, _signed(t.score)) for t in traits)),
            ]
    return blocks


def _arts_table(character: Character, arts: Sequence[str]) -> Table:
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
    )


def _hermetic_magic(saga: Saga, character: Character) -> list[Block]:
    grid = cs.casting_grid(saga, character)
    blocks: list[Block] = [
        NewPage(),
        Heading("Hermetic Arts"),
        Columns(
            (_arts_table(character, TECHNIQUES),), (_arts_table(character, FORMS),)
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
        Paragraph(
            "Casting Score: Technique + Form + Stamina + aura, before the die, "
            "in the magus's home aura.",
            "italic",
            "small",
        ),
    ]
    vis = {art: pawns for art, pawns in character.raw_vis.items() if pawns}
    if vis:
        blocks += [
            Heading("Raw Vis", 2),
            Facts(
                tuple(
                    (art.title(), f"{n} pawn{'' if n == 1 else 's'}")
                    for art, n in vis.items()
                ),
                5,
            ),
        ]
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


def _grimoire(saga: Saga, character: Character, options: PrintOptions) -> list[Block]:
    rows = cs.spell_table(saga, character)
    if not rows:
        return []
    grid = cs.casting_grid(saga, character)

    def order(row: cs.SpellRow) -> tuple[int, int, str]:
        form = FORMS.index(row.form) if row.form in FORMS else len(FORMS)
        return (form, -(row.level or 0), row.name)

    blocks: list[Block] = [NewPage(), GrimoireTitle(character.name)]
    last = None
    for row in sorted(rows, key=order):
        if row.form != last:
            symbol = Symbol("art", row.form) if row.form in FORMS else None
            blocks.append(Heading(row.form or "Unknown", 2, symbol))
            last = row.form
        score = grid.get((row.technique, row.form))
        casting = (
            f"Casting Total {int(score.total) + row.mastery} + die"
            if score is not None
            else ""
        )
        if row.mastery:
            casting += f" · Mastery {row.mastery}"
        level = "Gen." if row.level is None else str(row.level)
        description = ""
        if options.full_spells:
            spell = spl.find_spell(saga, character.spells_known[row.index].spell_id)
            description = spell.description if spell else ""
        blocks.append(
            Spell(
                row.name,
                f"{row.arts} {level}" + (" · Ritual" if row.ritual else ""),
                f"R: {row.range}, D: {row.duration}, T: {row.target}",
                casting,
                description,
            )
        )
    return blocks


def _story(saga: Saga, character: Character) -> list[Block]:
    blocks: list[Block] = [NewPage(), Heading("Description & Biography")]
    biography = _facts(cs.biographical_facts(saga, character))
    if biography:
        blocks.append(Facts(biography))
    d = character.description
    if d.physical_description:
        blocks += [Heading("Appearance", 2), Paragraph(d.physical_description)]
    if d.biography:
        blocks.append(Heading("Biography", 2))
        blocks += [
            Paragraph(part.strip())
            for part in d.biography.split("\n\n")
            if part.strip()
        ]
    familiar = familiars.familiar_of(saga, character.id)
    if familiar is not None:
        blocks += [
            Heading("Familiar"),
            Facts(
                (
                    ("Name", familiar.name),
                    ("Species", familiar.species),
                    ("Magic Might", str(familiar.magic_might)),
                    ("Bound", f"{familiar.season_bound} {familiar.year_bound}"),
                    ("Golden Cord", str(familiar.golden_cord)),
                    ("Silver Cord", str(familiar.silver_cord)),
                    ("Bronze Cord", str(familiar.bronze_cord)),
                )
            ),
        ]
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
    return blocks


def character_document(
    saga: Saga, character: Character, options: PrintOptions = DEFAULT_OPTIONS
) -> Document:
    """A character's printed sheet: who they are, their Abilities and
    Combat & Condition; for a magus the Arts and the Grimoire, each from a
    new page; then their story."""
    subtitle = cs.subtitle(saga, character)
    ch = character.characteristics
    a = character.aging
    b = character.background
    blocks: list[Block] = [
        Title(character.name, subtitle),
        ScoreBoxes(
            tuple(
                (name, _signed(getattr(ch, name.lower())))
                for name in (
                    "Intelligence",
                    "Perception",
                    "Strength",
                    "Stamina",
                    "Presence",
                    "Communication",
                    "Dexterity",
                    "Quickness",
                )
            )
        ),
        Facts(
            _facts(cs.glance_facts(saga, character))
            + (
                ("Confidence", f"{b.confidence_score} ({b.confidence_points} points)"),
                ("Warping", f"{a.warping_score} ({a.warping_points} points)"),
                ("Decrepitude", f"{a.decrepitude} ({a.decrepitude_points} points)"),
            )
        ),
    ]
    magus = character.type == "magus"
    if magus:
        hermetic = _facts(cs.hermetic_facts(character))
        if hermetic:
            blocks += [Heading("Hermetic Background", 2), Facts(hermetic, 3)]
        if character.hermetic.wizards_sigil:
            blocks.append(
                Paragraph(
                    f"Wizard's Sigil: {character.hermetic.wizards_sigil}", "italic"
                )
            )
    blocks += _virtues_flaws(character)
    blocks += _traits(character)
    blocks += _abilities(character)
    blocks += combat_blocks(character)
    if magus:
        blocks += _hermetic_magic(saga, character)
        blocks += _grimoire(saga, character, options)
    blocks += _story(saga, character)
    return Document(character.name, subtitle, blocks)


#: Each record kind's printed sheet, by transfer's kind names.
LAYOUTS: dict[str, Callable[..., Document]] = {
    "character": character_document,
}


def document(
    saga: Saga, kind: str, record, options: PrintOptions = DEFAULT_OPTIONS
) -> Document:
    """The printed sheet of `record`, a record of `kind`; KeyError for a
    kind that can't be printed yet."""
    return LAYOUTS[kind](saga, record, options)

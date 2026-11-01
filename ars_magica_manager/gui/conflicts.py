"""The desktop's fight and siege pages, drawn as a manuscript leaf.

A fight's page: its title (each word's first letter gilt), the order of
blows as a ribbon of seals, the two sides under their arms with a card
for each unit (its figures, each fighter's wound boxes and Fatigue), The
Blow worked out line by line, and the chronicle. A siege's page: its
title and the seasons it has run as medallions in the saga's set, the
garrison and the besiegers with gauges bound in cord, the castle's plan
drawn from its walls, and the chronicle.

What they say comes from the core (fights.py, sieges.py, rules.fight,
rules.siege), and what their buttons do from conflicts.COMMANDS, as the
terminal's Conflicts view does.
"""

from __future__ import annotations

import math
from collections.abc import Callable

from PySide6.QtCore import QPointF, QRectF, QSize, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QFontMetricsF,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPaintEvent,
    QPen,
    QRadialGradient,
    QResizeEvent,
)
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from .. import arms as heraldic
from .. import conflicts, fights, medallions, sieges
from ..commands import Command
from ..models import FATIGUE_LEVELS, WALLS, Fight, Saga, Siege
from ..rules import fight as fight_rules
from ..rules import options as rule_options
from ..rules import siege as siege_rules
from . import heraldry, pictures
from . import medallions as drawn
from .style import gilding, illumination
from .style.illumination import gold
from .style.ornaments import gloss_box, ledger_entry
from .style.paper import shade
from .themes import DRAWN, PIGMENTS, Palette
from .widgets import edit_button, scrolling_page

Run = Callable[[Command], None]

#: Each side's arms when it fights under no covenant's.
DEFAULT_ARMS = (
    heraldic.Arms("Azure", "Plain", "Argent", "Tower", "Or"),
    heraldic.Arms("Sable", "Per bend", "Gules", "Wolf", "Argent"),
)
GARRISON_ARMS = heraldic.Arms("Or", "Plain", "Or", "Eagle", "Sable")
BESIEGER_ARMS = heraldic.Arms("Gules", "Per pale", "Argent", "Lion", "Or")
STONE, STONE_DARK = QColor(DRAWN["stone"]), QColor(DRAWN["stone-dark"])


def font(size: float, *, bold: bool = False, italic: bool = False) -> QFont:
    f = QFont(pictures.SERIF)
    f.setPointSizeF(size)
    f.setBold(bold)
    f.setItalic(italic)
    return f


def small_caps(size: float, *, bold: bool = True) -> QFont:
    f = font(size, bold=bold)
    f.setCapitalization(QFont.Capitalization.SmallCaps)
    return f


def display(size: float) -> QFont:
    f = QFont(pictures.DISPLAY)
    f.setPointSizeF(size)
    return f


def _text(g: QPainter, at: QPointF, words: str, f: QFont, colour: str) -> None:
    g.setFont(f)
    g.setPen(QColor(colour))
    g.drawText(at, words)


#: The breach ring's radius, and the gap between it and its label.
RING, RING_GAP = 28, 6


def _beside_ring(mid: QPointF, a: QPointF, b: QPointF, outward: QPointF) -> QRectF:
    """Where a breach's label goes: outside the ring, off the wall's line,
    above or below a North or South wall and left or right of an East or
    West one, on the side `outward` points to."""
    width, height = 120, 18
    if abs(a.y() - b.y()) <= abs(a.x() - b.x()):
        above = outward.y() < 0
        top = mid.y() - RING - RING_GAP - height if above else mid.y() + RING + RING_GAP
        return QRectF(mid.x() - width / 2, top, width, height)
    left = outward.x() < 0
    x = mid.x() - RING - RING_GAP - width if left else mid.x() + RING + RING_GAP
    return QRectF(x, mid.y() - height / 2, width, height)


def _boxed(
    g: QPainter,
    rect: QRectF,
    words: str,
    f: QFont,
    colour: str,
    align: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignCenter,
) -> None:
    g.setFont(f)
    g.setPen(QColor(colour))
    g.drawText(rect, int(align), words)


def _elided(words: str, f: QFont, width: float) -> str:
    return QFontMetricsF(f).elidedText(words, Qt.TextElideMode.ElideRight, width)


def _wrapped(words: str, f: QFont, width: float) -> list[str]:
    """The words in lines no wider than `width`, broken between words (a
    single word too long for a line is cut short)."""
    metrics = QFontMetricsF(f)
    lines: list[str] = []
    line = ""
    for word in words.split():
        trial = f"{line} {word}" if line else word
        if line and metrics.horizontalAdvance(trial) > width:
            lines.append(_elided(line, f, width))
            line = word
        else:
            line = trial
    if line:
        lines.append(_elided(line, f, width))
    return lines


def title_words(
    g: QPainter, words: str, f: QFont, at: QPointF, p: Palette, *, skip_first: bool
) -> None:
    """A title: each capital gilt, as a word's first letter, and the rest
    in the rubric's red, so "on" and "the" stay plain; `skip_first` when
    the first word continues an illuminated initial."""
    metrics = QFontMetricsF(f)
    x = at.x()
    for i, word in enumerate(words.split(" ")):
        if i:
            x += metrics.horizontalAdvance(" ")
        if not word:
            continue
        rest = word
        if not (skip_first and i == 0) and word[0].isupper():
            gilding.gilt_letter(g, word[0], f, QPointF(x, at.y()), p)
            x += metrics.horizontalAdvance(word[0])
            rest = word[1:]
        _text(g, QPointF(x, at.y()), rest, f, p["heading"])
        x += metrics.horizontalAdvance(rest)


def illuminated_title(
    g: QPainter, title: str, subtitle: str, width: float, p: Palette
) -> float:
    """The page's title with its illuminated initial, the line under it
    and the red rule; returns the height used."""
    words = title.strip() or "Untitled"
    illumination.paint_initial(g, QRectF(8, 8, 84, 84), words[0], p)
    f = display(30)
    while (
        QFontMetricsF(f).horizontalAdvance(words[1:]) > width - 130
        and f.pointSizeF() > 16
    ):
        f.setPointSizeF(f.pointSizeF() - 1)
    title_words(g, words[1:], f, QPointF(106, 60), p, skip_first=True)
    _text(g, QPointF(108, 86), subtitle, font(13, italic=True), p["label"])
    g.setPen(QPen(QColor(p["heading"]), 2))
    g.drawLine(QPointF(8, 108), QPointF(width - 8, 108))
    g.setPen(QPen(QColor(p["accent"]), 0.8))
    g.drawLine(QPointF(8, 112), QPointF(width - 8, 112))
    return 120


def _arms_of(saga: Saga, covenant_id: str, fallback: heraldic.Arms) -> heraldic.Arms:
    covenant = saga.covenant(covenant_id) if covenant_id else None
    return (heraldic.arms_of(covenant) if covenant else None) or fallback


def buttons(rows: list[tuple[str, str, Callable[[], None]]], p: Palette) -> QWidget:
    """A row of the app's own quiet buttons."""
    box = QWidget()
    line = QHBoxLayout(box)
    line.setContentsMargins(0, 0, 0, 0)
    line.setSpacing(6)
    for words, concept, act in rows:
        line.addWidget(edit_button(words, p, act, concept))
    line.addStretch(1)
    return box


# -- the fight --


class FightHeader(QWidget):
    """The fight's title and its order of blows, as a ribbon of seals."""

    HEIGHT = 236

    def __init__(self, saga: Saga, fight: Fight, p: Palette) -> None:
        super().__init__()
        self.saga, self.fight, self.p = saga, fight, p
        self.setMinimumHeight(self.HEIGHT)

    def sizeHint(self) -> QSize:
        return QSize(900, self.HEIGHT)

    def paintEvent(self, event: QPaintEvent) -> None:
        g = QPainter(self)
        g.setRenderHint(QPainter.RenderHint.Antialiasing)
        p, fight, w = self.p, self.fight, float(self.width())
        where = f"  ·  {fight.place}" if fight.place else ""
        illuminated_title(
            g,
            fight.name,
            f"{fights.state_text(fight)}  ·  {fight_rules.range_text(fight)}  ·  "
            f"{fight.season} {fight.year}{where}",
            w,
            p,
        )
        self._ribbon(g, QRectF(60, 142, w - 120, 76))
        g.end()

    def _ribbon(self, g: QPainter, rib: QRectF) -> None:
        p = self.p
        path = QPainterPath()
        path.moveTo(rib.left() - 24, rib.top() + 7)
        path.lineTo(rib.left(), rib.top())
        path.lineTo(rib.right(), rib.top())
        path.lineTo(rib.right() + 24, rib.top() + 7)
        path.lineTo(rib.right() + 12, rib.center().y())
        path.lineTo(rib.right() + 24, rib.bottom() - 7)
        path.lineTo(rib.right(), rib.bottom())
        path.lineTo(rib.left(), rib.bottom())
        path.lineTo(rib.left() - 24, rib.bottom() - 7)
        path.lineTo(rib.left() - 12, rib.center().y())
        path.closeSubpath()
        g.fillPath(path, QBrush(shade(p["panel"], 150)))
        g.setPen(QPen(QColor(p["heading"]), 1.4))
        g.setBrush(Qt.BrushStyle.NoBrush)
        g.drawPath(path)
        g.setPen(QPen(shade(p["accent"], 200), 0.7))
        g.drawLine(
            QPointF(rib.left(), rib.top() + 4), QPointF(rib.right(), rib.top() + 4)
        )
        g.drawLine(
            QPointF(rib.left(), rib.bottom() - 4),
            QPointF(rib.right(), rib.bottom() - 4),
        )
        _text(
            g,
            QPointF(rib.left() - 4, rib.top() - 7),
            "ORDER OF BLOWS",
            font(9, bold=True),
            p["label"],
        )
        self._seals(g, rib)

    def _seals(self, g: QPainter, rib: QRectF) -> None:
        p, fight = self.p, self.fight
        every = fight_rules.units(self.saga, fight)
        order = [u for u in fight.order if u in every]
        if not order:
            _boxed(
                g,
                rib,
                "Initiative is rolled at the first blow.",
                font(13, italic=True),
                p["foreground"],
            )
            return
        acting = fight_rules.actor(self.saga, fight) if not fight.over else None
        step = rib.width() / len(order)
        key = medallions.chosen(self.saga)
        for i, unit_id in enumerate(order):
            unit = every[unit_id]
            cx = rib.left() + step * (i + 0.5)
            r = min(28.0, step * 0.2)
            seal = QRectF(cx - step / 2 + 10, rib.center().y() - r, 2 * r, 2 * r)
            now = acting is not None and unit.id == acting.id
            drawn.numbered(
                g,
                key,
                seal.center(),
                r,
                fight.initiative.get(unit_id, 0),
                unit.side,
                fight.season,
                fight.year,
                p,
                now=now,
            )
            down = unit.down()
            name_box = QRectF(
                seal.right() + 8, rib.top(), step - 2 * r - 22, rib.height()
            )
            f = font(11.5, bold=now)
            colour = p["heading"] if now else (p["dim"] if down else p["foreground"])
            _boxed(
                g,
                name_box,
                _elided(unit.name, f, name_box.width()),
                f,
                colour,
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            )
            if now:
                tip = QPainterPath()
                tip.moveTo(seal.center().x() - 7, rib.bottom() + 4)
                tip.lineTo(seal.center().x() + 7, rib.bottom() + 4)
                tip.lineTo(seal.center().x(), rib.bottom() + 14)
                tip.closeSubpath()
                g.fillPath(
                    tip, gold(QRectF(seal.center().x() - 7, rib.bottom(), 14, 14))
                )


#: A unit card's height before its fighters, each fighter's row, and the
#: line of tags (riding, defending, grappling) when it has one.
CARD_TOP, FIGHTER_ROW, TAG_ROW = 56, 26, 24


class FightBody(QWidget):
    """The two sides, The Blow between them, and the chronicle."""

    def __init__(self, saga: Saga, fight: Fight, p: Palette) -> None:
        super().__init__()
        self.saga, self.fight, self.p = saga, fight, p
        self.setMinimumWidth(900)
        self.setMinimumHeight(self._height())

    def _units(self, side: int) -> list[fight_rules.Unit]:
        return [
            u
            for u in fight_rules.units(self.saga, self.fight).values()
            if u.side == side
        ]

    def _card_height(self, unit: fight_rules.Unit) -> float:
        tagged = bool(fight_rules.tags(self.saga, self.fight, unit))
        return CARD_TOP + (TAG_ROW if tagged else 0) + FIGHTER_ROW * len(unit.fighters)

    def _column_height(self, side: int) -> float:
        return 100 + sum(self._card_height(u) + 12 for u in self._units(side))

    def _blow_lines(self) -> list[str]:
        return self.fight.log[-1].lines[-9:] if self.fight.log else []

    def _height(self) -> int:
        sides = max(self._column_height(0), self._column_height(1), 380)
        chronicle = 60 + 22 * min(10, len(self.fight.log))
        return int(sides + chronicle + 20)

    def sizeHint(self) -> QSize:
        return QSize(900, self._height())

    def paintEvent(self, event: QPaintEvent) -> None:
        g = QPainter(self)
        g.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = float(self.width())
        mid = max(320.0, min(420.0, w * 0.3))
        column = (w - mid - 60) / 2
        heights = []
        for side, x in ((0, 10.0), (1, w - 10 - column)):
            heights.append(self._side(g, side, QRectF(x, 0, column, 0)))
        self._blow(g, QRectF(column + 30, 20, mid, 340))
        top = max(*heights, 380) + 10
        self._chronicle(g, QRectF(10, top, w - 20, 0))
        g.end()

    def _side(self, g: QPainter, side: int, area: QRectF) -> float:
        p, fight = self.p, self.fight
        sides = fights.sides(fight)
        record = sides[side] if side < len(sides) else None
        arms = _arms_of(
            self.saga, record.covenant_id if record else "", DEFAULT_ARMS[min(side, 1)]
        )
        heraldry.paint(g, arms, QRectF(area.left(), 10, 58, 68), p["foreground"])
        name = fight_rules.side_name(fight, side)
        f = font(21, bold=True)
        _text(
            g,
            QPointF(area.left() + 72, 42),
            _elided(name, f, area.width() - 80),
            f,
            p["heading"],
        )
        covenant = (
            self.saga.covenant(record.covenant_id)
            if record and record.covenant_id
            else None
        )
        standing = sum(len(u.standing()) for u in self._units(side))
        sub = (f"under the arms of {covenant.name} · " if covenant else "") + (
            f"{standing} standing"
        )
        _text(
            g, QPointF(area.left() + 74, 64), sub, font(11.5, italic=True), p["label"]
        )
        y = 96.0
        acting = (
            fight_rules.actor(self.saga, fight)
            if fight.round and not fight.over
            else None
        )
        for unit in self._units(side):
            height = self._card_height(unit)
            self._card(g, unit, QRectF(area.left(), y, area.width(), height), acting)
            y += height + 12
        if not self._units(side):
            _text(
                g,
                QPointF(area.left(), y + 16),
                "No combatants yet.",
                font(12, italic=True),
                p["dim"],
            )
            y += 30
        return y

    def _card(
        self,
        g: QPainter,
        unit: fight_rules.Unit,
        rect: QRectF,
        acting: fight_rules.Unit | None,
    ) -> None:
        p = self.p
        now = acting is not None and acting.id == unit.id
        ledger_entry(g, rect, p, marked=now)
        down = unit.down()
        f = font(15, bold=True)
        x = rect.left() + 12
        if now:
            paraph = font(17, bold=True)
            _text(g, QPointF(x, rect.top() + 25), "¶", paraph, p["text-error"])
            x += QFontMetricsF(paraph).horizontalAdvance("¶ ")
        _text(
            g,
            QPointF(x, rect.top() + 24),
            _elided(unit.name, f, rect.width() - 120),
            f,
            p["dim"] if down else p["heading"],
        )
        group = unit.group
        kind = (
            ("A trained group" if group.trained else "A group")
            + f" of {len(unit.fighters)}"
            if group is not None
            else ""
        )
        _text(
            g,
            QPointF(rect.left() + 12, rect.top() + 44),
            self._figures(unit),
            font(11.5),
            p["foreground"],
        )
        if kind:
            _text(
                g,
                QPointF(
                    rect.right()
                    - 40
                    - QFontMetricsF(font(10, italic=True)).horizontalAdvance(kind),
                    rect.top() + 22,
                ),
                kind,
                font(10, italic=True),
                p["label"],
            )
        if group is not None:
            self._pennant(g, QPointF(rect.right() - 20, rect.top() + 28))
        y = rect.top() + CARD_TOP
        tags = fight_rules.tags(self.saga, self.fight, unit)
        if tags:
            f = font(11, italic=True)
            _text(
                g,
                QPointF(rect.left() + 12, y + 8),
                _elided("  ·  ".join(tags), f, rect.width() - 24),
                f,
                p["text-accent"],
            )
            y += TAG_ROW
        for i, fighter in enumerate(unit.fighters):
            self._fighter(
                g,
                fighter,
                QRectF(rect.left() + 12, y, rect.width() - 24, FIGHTER_ROW),
                vanguard=group is not None and i == 0,
            )
            y += FIGHTER_ROW
        if down:
            g.setPen(QPen(shade(p["heading"], 160), 2.5))
            g.drawLine(
                rect.topLeft() + QPointF(10, 10), rect.bottomRight() - QPointF(10, 10)
            )

    def _figures(self, unit: fight_rules.Unit) -> str:
        f = unit.vanguard.figures()

        def signed(value: int | None) -> str:
            return "n/a" if value is None else f"{value:+d}"

        line = (
            f"Init {signed(f.init)}   Atk {signed(f.attack)}   Dfn {signed(f.defence)}"
            f"   Dam {signed(f.damage)}   Soak {signed(f.soak)}"
        )
        bonus = unit.bonus()
        if bonus and unit.group is not None:
            line += f"   +{bonus} {unit.group.bonus_to}"
        return line

    def _pennant(self, g: QPainter, at: QPointF) -> None:
        p = self.p
        flag = QPainterPath()
        flag.moveTo(at.x() - 10, at.y() - 16)
        flag.lineTo(at.x() + 6, at.y() - 16)
        flag.lineTo(at.x() + 2, at.y() - 10)
        flag.lineTo(at.x() + 6, at.y() - 4)
        flag.lineTo(at.x() - 10, at.y() - 4)
        flag.closeSubpath()
        g.fillPath(flag, QColor(p["heading"]))
        g.setPen(QPen(QColor(p["foreground"]), 1.3))
        g.drawLine(QPointF(at.x() - 10, at.y() - 18), QPointF(at.x() - 10, at.y() + 6))

    def _fighter(
        self, g: QPainter, fighter: fight_rules.Fighter, row: QRectF, *, vanguard: bool
    ) -> None:
        p = self.p
        down = fighter.down()
        f = font(11.5, italic=down)
        name = fighter.name + ("  (vanguard)" if vanguard else "")
        _boxed(
            g,
            QRectF(row.left(), row.top(), row.width() * 0.4, row.height()),
            _elided(name, f, row.width() * 0.4),
            f,
            p["dim"] if down else p["foreground"],
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
        )
        w = fighter.wounds
        x = row.left() + row.width() * 0.42
        cy = row.center().y()
        bands = (
            ("L", w.light, 3, p["accent"]),
            ("M", w.medium, 2, DRAWN["medium-wound"]),
            ("H", w.heavy, 1, p["heading"]),
            ("I", 1 if w.incapacitated else 0, 1, p["heading"]),
        )
        for letter, count, boxes, colour in bands:
            _text(g, QPointF(x, cy + 4), letter, font(9), p["label"])
            x += 9
            for k in range(max(boxes, count)):
                box = QRectF(x, cy - 5, 10, 10)
                g.setPen(QPen(QColor(colour), 1.1))
                g.setBrush(
                    QBrush(QColor(colour)) if k < count else Qt.BrushStyle.NoBrush
                )
                g.drawRect(box)
                x += 12
            x += 6
        if w.dead:
            _text(g, QPointF(x, cy + 4), "Dead", font(10, bold=True), p["heading"])
            x += 34
        holder = (
            fighter.character if fighter.character is not None else fighter.combatant
        )
        level = (
            FATIGUE_LEVELS.index(holder.fatigue_level)
            if holder.fatigue_level in FATIGUE_LEVELS
            else 0
        )
        fx = row.right() - 5 * 13
        for k in range(len(FATIGUE_LEVELS) - 1):
            pip = QRectF(fx + k * 13, cy - 5, 10, 10)
            g.setPen(QPen(QColor(p["text-accent"]), 1))
            g.setBrush(
                QBrush(QColor(p["text-accent"])) if k < level else Qt.BrushStyle.NoBrush
            )
            g.drawEllipse(pip)
        if fighter.combatant.out:
            _text(
                g,
                QPointF(fx - 70, cy + 4),
                fighter.combatant.out,
                font(10, italic=True),
                p["label"],
            )

    def _blow(self, g: QPainter, rect: QRectF) -> None:
        p, fight = self.p, self.fight
        lines = self._blow_lines()
        height = 170 + 22 * len(lines) + 40
        rect.setHeight(height)
        gloss_box(g, rect, p, "The Blow")
        last = (
            fight.log[-1].text
            if fight.log
            else "No blow struck yet: Next Blow begins the fight."
        )
        g.setFont(font(13.5, bold=True))
        g.setPen(QColor(p["heading"]))
        g.drawText(
            QRectF(rect.left() + 26, rect.top() + 44, rect.width() - 44, 52),
            int(Qt.AlignmentFlag.AlignHCenter | Qt.TextFlag.TextWordWrap),
            last,
        )
        self._swords(g, QPointF(rect.center().x(), rect.top() + 146), 0.55)
        y = rect.top() + 198
        for line in lines:
            g.setFont(font(11.5))
            g.setPen(QColor(p["foreground"]))
            g.drawText(
                QRectF(rect.left() + 26, y - 15, rect.width() - 44, 20),
                int(Qt.AlignmentFlag.AlignLeft),
                _elided(line, font(11.5), rect.width() - 44),
            )
            y += 22

    def _swords(self, g: QPainter, c: QPointF, scale: float) -> None:
        for sign in (-1, 1):
            g.save()
            g.translate(c)
            g.scale(scale, scale)
            g.rotate(sign * 38)
            blade = QPainterPath()
            blade.moveTo(-4, -78)
            blade.lineTo(0, -92)
            blade.lineTo(4, -78)
            blade.lineTo(4, 40)
            blade.lineTo(-4, 40)
            blade.closeSubpath()
            steel = QLinearGradient(-4, 0, 4, 0)
            steel.setColorAt(0, QColor(DRAWN["steel-light"]))
            steel.setColorAt(1, QColor(DRAWN["steel"]))
            g.fillPath(blade, QBrush(steel))
            g.setPen(QPen(QColor(self.p["foreground"]), 1))
            g.setBrush(Qt.BrushStyle.NoBrush)
            g.drawPath(blade)
            g.fillRect(QRectF(-18, 40, 36, 6), gold(QRectF(-18, 40, 36, 6)))
            g.fillRect(QRectF(-3, 46, 6, 22), QBrush(QColor(DRAWN["timber"])))
            g.setBrush(gold(QRectF(-6, 68, 12, 12)))
            g.drawEllipse(QRectF(-6, 68, 12, 12))
            g.restore()

    def _chronicle(self, g: QPainter, area: QRectF) -> None:
        p, fight = self.p, self.fight
        g.setPen(QPen(QColor(p["rule"]), 1))
        g.drawLine(QPointF(area.left(), area.top()), QPointF(area.right(), area.top()))
        heading = "The chronicle"
        _text(
            g,
            QPointF(area.left(), area.top() + 30),
            heading,
            font(16, bold=True),
            p["heading"],
        )
        y = area.top() + 56
        entries = fight.log[-10:]
        if not entries:
            _text(
                g,
                QPointF(area.left() + 4, y),
                "Nothing yet.",
                font(12, italic=True),
                p["dim"],
            )
        for entry in entries:
            g.setBrush(QBrush(QColor(p["heading"])))
            g.setPen(Qt.PenStyle.NoPen)
            g.drawEllipse(QRectF(area.left() + 4, y - 8, 6, 6))
            words = f"{entry.round}.  {entry.text}"
            _text(
                g,
                QPointF(area.left() + 18, y),
                _elided(words, font(12), area.width() - 24),
                font(12),
                p["foreground"],
            )
            y += 22


class FightPage(QWidget):
    """A fight's page: the drawn leaf and the buttons that play it."""

    def __init__(self, saga: Saga, fight: Fight, p: Palette, run: Run) -> None:
        super().__init__()
        self.saga, self.fight, self.p, self.run = saga, fight, p, run
        column = QVBoxLayout(self)
        column.setContentsMargins(18, 12, 12, 8)
        column.setSpacing(8)
        self.header = FightHeader(saga, fight, p)
        self.body = FightBody(saga, fight, p)
        self.buttons = buttons(
            [
                ("Next Blow", "combat", lambda: self.act("next_blow")),
                ("Next Round", "combat", lambda: self.act("next_round")),
                ("Restart", "update", lambda: self.act("restart_fight")),
                ("Combat Options", "combat", lambda: self.act("fight_options")),
                *(
                    [
                        ("Morale", "combat", lambda: self.act("group_morale")),
                        ("Rally", "troupe", lambda: self.act("rally_group")),
                    ]
                    if rule_options.is_on(saga, rule_options.MORALE_DISCIPLINE)
                    else []
                ),
            ],
            p,
        )
        self.setup = buttons(
            [
                ("Add Combatant", "add", lambda: self.act("add_combatant")),
                ("Edit Combatant", "edit", lambda: self.act("edit_combatant")),
                ("Remove Combatant", "delete", lambda: self.act("remove_combatant")),
                ("Form a Group", "troupe", lambda: self.act("form_group")),
                ("Break up a Group", "players", lambda: self.act("break_group")),
                ("Edit Fight", "edit", self.edit),
            ],
            p,
        )
        column.addWidget(
            scrolling_page(p, self.header, self.buttons, self.setup, self.body), 1
        )

    def row(self) -> int:
        return self.saga.fights.index(self.fight)

    def act(self, action: str) -> None:
        self.run(conflicts.command(self.saga, action, self.row()))

    def edit(self) -> None:
        edit = fights.ops(self.saga).edit
        if edit is not None:
            self.run(edit(self.row()))


# -- the siege --


def cord(g: QPainter, y: float, x0: float, x1: float, ink: QColor) -> None:
    """A twisted cord: two inked strands crossing, as a knotwork border."""
    for phase in (0.0, math.pi):
        path = QPainterPath()
        steps = max(2, int((x1 - x0) / 2))
        for k in range(steps + 1):
            x = x0 + (x1 - x0) * k / steps
            pt = QPointF(x, y + 2.6 * math.sin((x - x0) / 5.0 + phase))
            if k:
                path.lineTo(pt)
            else:
                path.moveTo(pt)
        g.setPen(QPen(ink, 1.1))
        g.setBrush(Qt.BrushStyle.NoBrush)
        g.drawPath(path)


def knot(g: QPainter, c: QPointF, ink: QColor) -> None:
    """A small three-looped knot capping a gauge's end."""
    g.setPen(QPen(ink, 1.2))
    g.setBrush(Qt.BrushStyle.NoBrush)
    for k in range(3):
        a = math.radians(k * 120 - 90)
        g.drawEllipse(
            QPointF(c.x() + 4.5 * math.cos(a), c.y() + 4.5 * math.sin(a)), 5, 5
        )
    g.drawEllipse(c, 8, 8)


def gauge(
    g: QPainter,
    area: QRectF,
    label: str,
    value: float,
    colour: str,
    note: str,
    ticks: list[tuple[float, str]],
    p: Palette,
) -> None:
    """A gauge bound in cord, washed in colour to `value` (0 to 1), with
    inked gauge marks and their readings, and a red lozenge at the value."""
    ink = QColor(p["foreground"])
    value = max(0.0, min(1.0, value))
    _text(g, QPointF(area.left(), area.top() + 12), label, small_caps(11.5), p["label"])
    x0, x1 = area.left() + 14, area.right() - 14
    bar = QRectF(x0, area.top() + 22, x1 - x0, 15)
    filled = QRectF(bar.left(), bar.top(), bar.width() * value, bar.height())
    g.fillRect(filled, QBrush(shade(colour, 120)))
    g.save()
    g.setClipRect(filled)
    g.setPen(QPen(shade(colour, 210), 0.8))
    k = bar.left() - bar.height()
    while k < filled.right():
        g.drawLine(QPointF(k, bar.bottom()), QPointF(k + bar.height(), bar.top()))
        k += 5
    g.restore()
    cord(g, bar.top(), x0, x1, ink)
    cord(g, bar.bottom(), x0, x1, ink)
    knot(g, QPointF(x0 - 4, bar.center().y()), ink)
    knot(g, QPointF(x1 + 4, bar.center().y()), ink)
    g.setPen(QPen(ink, 1))
    for i in range(1, 20):
        fx = bar.left() + bar.width() * i / 20
        g.drawLine(QPointF(fx, bar.bottom() + 4), QPointF(fx, bar.bottom() + 7))
    for frac, reading in ticks:
        fx = bar.left() + bar.width() * frac
        g.setPen(QPen(ink, 1.3))
        g.drawLine(QPointF(fx, bar.bottom() + 4), QPointF(fx, bar.bottom() + 12))
        _boxed(
            g,
            QRectF(fx - 40, bar.bottom() + 12, 80, 16),
            reading,
            font(9.5, italic=True),
            p["label"],
        )
    vx = bar.left() + bar.width() * value
    loz = QPainterPath(QPointF(vx, bar.top() - 7))
    loz.lineTo(vx + 6, bar.center().y())
    loz.lineTo(vx, bar.bottom() + 7)
    loz.lineTo(vx - 6, bar.center().y())
    loz.closeSubpath()
    g.fillPath(loz, QColor(p["heading"]))
    g.setPen(QPen(ink, 1))
    g.drawPath(loz)
    _text(
        g,
        QPointF(area.left(), area.top() + 82),
        note,
        font(11, italic=True),
        p["foreground"],
    )


#: A gauge's height on the page.
GAUGE = 96
QUALITY_TICKS = [(i / 3, q) for i, q in enumerate(siege_rules.QUALITIES)]
#: The Garrison gauge's reach, in combat groups, and its readings at the
#: steps where its interval changes.
GARRISON_TOP = 50
#: The siege's chronicle runs the page's width under the garrison's three
#: gauges (its arms, its box of three rows, then the gauges); each line of
#: it is this tall.
CHRONICLE_TOP = 10 + 82 + 26 + 46 * 3 + 20 + 3 * GAUGE + 26
CHRONICLE_LINE = 22
#: Where each wall's reading sits beside it (North, East, South, West).
LABEL_OFFSETS = (QPointF(-30, -20), QPointF(18, 4), QPointF(-30, 50), QPointF(-90, 4))


def holder_name(saga: Saga, siege: Siege) -> str:
    """Who holds the castle: the typed holder, else the linked lord or
    covenant."""
    if siege.holder:
        return siege.holder
    lord = saga.neighbour(siege.castle_id)
    covenant = saga.covenant(siege.covenant_id) if siege.covenant_id else None
    return lord.name if lord else (covenant.name if covenant else "")


def garrison_arms(saga: Saga, siege: Siege) -> heraldic.Arms:
    """The garrison's arms: the lord who holds the castle's, else its
    covenant's, else plain ones."""
    lord = saga.neighbour(siege.castle_id)
    found = heraldic.arms_of(lord) if lord else None
    return found or _arms_of(saga, siege.covenant_id, GARRISON_ARMS)


def besieger_arms(saga: Saga, siege: Siege) -> heraldic.Arms:
    """The besieging lord's arms, else plain ones."""
    lord = saga.neighbour(siege.besieger_id)
    return (heraldic.arms_of(lord) if lord else None) or BESIEGER_ARMS


class SiegeHeader(QWidget):
    """The siege's title, and the seasons it has run as medallions."""

    HEIGHT = 150

    def __init__(self, saga: Saga, siege: Siege, p: Palette) -> None:
        super().__init__()
        self.saga, self.siege, self.p = saga, siege, p
        self.setMinimumHeight(self.HEIGHT)

    def sizeHint(self) -> QSize:
        return QSize(900, self.HEIGHT)

    def seasons(self) -> list[tuple[str, int]]:
        s = self.siege
        return medallions.seasons_between(
            s.season, s.year, siege_rules.seasons_run(s) + 1
        )

    def paintEvent(self, event: QPaintEvent) -> None:
        g = QPainter(self)
        g.setRenderHint(QPainter.RenderHint.Antialiasing)
        p, s, w = self.p, self.siege, float(self.width())
        track = self.seasons()
        room = 86 * len(track)
        besieger, holder = sieges.besieger_name(self.saga, s), holder_name(self.saga, s)
        against = (
            f"{besieger} against {holder}"
            if besieger and holder
            else (besieger or holder)
        )
        sub = "  ·  ".join(
            x
            for x in (
                against,
                f"begun in the {s.season} of {s.year}",
                sieges.state_text(s),
            )
            if x
        )
        illuminated_title(g, s.name, sub, w - room, p)
        key = medallions.chosen(self.saga)
        for i, (season, year) in enumerate(track):
            c = QPointF(w - room + 43 + 86 * i, 50)
            drawn.paint(g, key, c, 30, season, year, p, now=i == len(track) - 1)
            now = i == len(track) - 1
            _boxed(
                g,
                QRectF(c.x() - 43, 84, 86, 18),
                f"{season} {year}",
                small_caps(10, bold=now),
                p["heading"] if now else p["label"],
            )
        g.end()


class SiegeBody(QWidget):
    """The garrison, the castle's plan, the besiegers, and the chronicle."""

    def __init__(self, saga: Saga, siege: Siege, p: Palette) -> None:
        super().__init__()
        self.saga, self.siege, self.p = saga, siege, p
        self.setMinimumWidth(1000)
        self.setMinimumHeight(self._height(1000))

    def _height(self, width: float) -> int:
        rows = len(self._chronicle_rows(width - 20)) or 1
        return int(CHRONICLE_TOP + 32 + CHRONICLE_LINE * rows + 30)

    def _chronicle_rows(self, width: float) -> list[tuple[float, str, bool]]:
        """The chronicle's lines, every event's, wrapped to `width`: (how
        far in, the words, whether it opens an event)."""
        rows: list[tuple[float, str, bool]] = []
        for event in self.siege.events:
            head = _wrapped(f"Day {event.day}: {event.text}", font(12), width - 24)
            rows += [(18, line, i == 0) for i, line in enumerate(head)]
            for working in event.lines:
                rows += [
                    (34 if i == 0 else 46, line, False)
                    for i, line in enumerate(
                        _wrapped(working, font(10.5, italic=True), width - 52)
                    )
                ]
        return rows

    def sizeHint(self) -> QSize:
        return QSize(1000, self._height(max(1000, self.width())))

    def resizeEvent(self, event: QResizeEvent) -> None:
        # The chronicle wraps to the page's width, so its height follows it.
        self.setMinimumHeight(self._height(event.size().width()))
        super().resizeEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:
        g = QPainter(self)
        g.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = float(self.width())
        side = max(300.0, min(360.0, w * 0.26))
        plan = QRectF(side + 30, 10, w - 2 * side - 60, 520)
        self._garrison(g, QRectF(10, 10, side, 0))
        self._plan(g, plan)
        self._besiegers(g, QRectF(w - side - 10, 10, side, 0))
        self._chronicle(g, QRectF(10, CHRONICLE_TOP, w - 20, 0))
        g.end()

    def _force(
        self,
        g: QPainter,
        area: QRectF,
        title: str,
        motto: str,
        arms: heraldic.Arms,
        rows: list[tuple[str, str]],
    ) -> float:
        p = self.p
        heraldry.paint(
            g, arms, QRectF(area.left(), area.top(), 56, 66), p["foreground"]
        )
        f = font(20, bold=True)
        _text(
            g,
            QPointF(area.left() + 68, area.top() + 28),
            _elided(title, f, area.width() - 70),
            f,
            p["heading"],
        )
        _text(
            g,
            QPointF(area.left() + 70, area.top() + 50),
            _elided(motto, font(11, italic=True), area.width() - 72),
            font(11, italic=True),
            p["label"],
        )
        box = QRectF(area.left(), area.top() + 82, area.width(), 26 + 46 * len(rows))
        g.setPen(QPen(QColor(p["rule"]), 1))
        g.setBrush(QBrush(shade(p["surface"], 200)))
        g.drawRoundedRect(box, 8, 8)
        y = box.top() + 28
        for name, figure in rows:
            f = small_caps(13)
            _text(
                g,
                QPointF(box.left() + 14, y),
                _elided(name, f, box.width() - 28),
                f,
                p["heading"],
            )
            _text(
                g,
                QPointF(box.left() + 14, y + 19),
                _elided(figure, font(11), box.width() - 28),
                font(11),
                p["foreground"],
            )
            y += 46
        return box.bottom() + 20

    def _garrison(self, g: QPainter, area: QRectF) -> None:
        s, p = self.siege, self.p
        castle = siege_rules.castle_of(s)
        interval, weight = siege_rules.garrison(s.garrison)
        stationed = ", ".join(
            f"{w} {n}" for w, n in zip(WALLS, s.garrison_walls, strict=True) if n
        )
        rows = [
            (
                "The garrison",
                f"{s.garrison} combat groups · Weight of Numbers +{weight}",
            ),
            ("At the walls", stationed or "not stationed at any wall"),
            (
                "The castle's experts",
                f"counter-miner {s.counter_sapper}, engineer {s.engineer}",
            ),
        ]
        y = self._force(
            g,
            area,
            sieges.castle_name(self.saga, s) or "The Garrison",
            f"held by {holder_name(self.saga, s)}"
            if holder_name(self.saga, s)
            else "the castle's garrison",
            garrison_arms(self.saga, s),
            rows,
        )
        top = GARRISON_TOP
        gauge(
            g,
            QRectF(area.left(), y, area.width(), GAUGE),
            "Garrison",
            s.garrison / top,
            p["text-accent"],
            f"{s.garrison} groups: events every {interval.lower()} at this step",
            [
                (0, "0"),
                *((n / top, str(n)) for n in siege_rules.GARRISON_STEPS),
                (1, f"{top}+"),
            ],
            p,
        )
        gauge(
            g,
            QRectF(area.left(), y + GAUGE, area.width(), GAUGE),
            "Defenses",
            siege_rules.QUALITIES.index(s.defenses) / 3,
            p["text-success"],
            f"{s.defenses}: Defense Bonus +{castle.defense_bonus()}"
            + (", a moat" if s.moat else ""),
            QUALITY_TICKS,
            p,
        )
        gauge(
            g,
            QRectF(area.left(), y + 2 * GAUGE, area.width(), GAUGE),
            "Supplies",
            siege_rules.QUALITIES.index(s.supplies) / 3,
            DRAWN["medium-wound"],
            f"{s.supplies}: Siege Conditions +{castle.supplies_bonus()}, every "
            f"{siege_rules.SUPPLIES[s.supplies][0].lower()}",
            QUALITY_TICKS,
            p,
        )

    def _besiegers(self, g: QPainter, area: QRectF) -> None:
        s, p = self.siege, self.p
        engines = ", ".join(
            f"{n} {k.lower()}{'s' if n > 1 else ''}" for k, n in s.engines.items() if n
        )
        stationed = ", ".join(
            f"{w} {n}" for w, n in zip(WALLS, s.besieger_walls, strict=True) if n
        )
        rows = [
            ("Miners", f"{s.miners} units · sapper {s.sapper}"),
            ("Engines", f"{engines or 'none'} · engine master {s.gunner}"),
            ("Soldiers", f"{s.soldiers} combat groups"),
            (
                "The stockade",
                ("held at " if siege_rules.stockaded(s) else "not held: ")
                + (stationed or "no wall manned"),
            ),
        ]
        y = self._force(
            g,
            area,
            sieges.besieger_name(self.saga, s) or "The Besiegers",
            "the besieging army",
            besieger_arms(self.saga, s),
            rows,
        )
        full = siege_rules.full_wall(s)
        left = siege_rules.walls(s)
        for i, wall in enumerate(WALLS):
            # Four wall gauges in two columns.
            col, row = i % 2, i // 2
            half = (area.width() - 12) / 2
            gauge(
                g,
                QRectF(area.left() + col * (half + 12), y + row * GAUGE, half, GAUGE),
                f"{wall} wall",
                left[i] / full if full else 0,
                p["heading"],
                f"{left[i]} of {full}" + (": breached" if left[i] == 0 else ""),
                [(0, "0"), (1, str(full))],
                p,
            )

    def _plan(self, g: QPainter, plan: QRectF) -> None:
        p = self.p
        g.setPen(QPen(QColor(p["rule"]), 1))
        g.setBrush(QBrush(shade(p["surface"], 220)))
        g.drawRoundedRect(plan, 10, 10)
        cx, cy = plan.center().x(), plan.center().y()
        g.save()
        clip = QPainterPath()
        clip.addRoundedRect(plan, 10, 10)
        g.setClipPath(clip)
        g.setPen(QPen(shade(p["rule"], 110), 1))
        for k in range(5):
            path = QPainterPath()
            for a in range(0, 361, 12):
                rr = 130 + k * 32 + 10 * math.sin(math.radians(a * 3 + k * 40))
                pt = QPointF(
                    cx + rr * 1.25 * math.cos(math.radians(a)),
                    cy + rr * 0.95 * math.sin(math.radians(a)),
                )
                if a:
                    path.lineTo(pt)
                else:
                    path.moveTo(pt)
            g.drawPath(path)
        river = QPainterPath(QPointF(plan.left() + 10, plan.bottom() - 36))
        river.cubicTo(
            QPointF(plan.left() + plan.width() * 0.35, plan.bottom() - 8),
            QPointF(plan.right() - plan.width() * 0.4, plan.bottom() - 80),
            QPointF(plan.right() - 10, plan.bottom() - 28),
        )
        g.setPen(QPen(QColor(DRAWN["river"]), 8))
        g.drawPath(river)
        g.setPen(QPen(QColor(DRAWN["river-light"]), 3))
        g.drawPath(river)
        g.restore()
        self._castle(g, plan)

    def _castle(self, g: QPainter, plan: QRectF) -> None:
        s, p = self.siege, self.p
        ink = QColor(p["foreground"])
        cx, cy = plan.center().x(), plan.center().y()
        half_w = min(plan.width() * 0.3, 190)
        half_h = min(plan.height() * 0.3, 150)
        corners = [
            QPointF(cx - half_w, cy - half_h),
            QPointF(cx + half_w, cy - half_h),
            QPointF(cx + half_w, cy + half_h),
            QPointF(cx - half_w, cy + half_h),
        ]
        full = siege_rules.full_wall(s)
        left = siege_rules.walls(s)
        # North, East, South, West: each between two corners.
        for i, wall in enumerate(WALLS):
            a, b = corners[i], corners[(i + 1) % 4]
            self._wall(g, a, b, left[i], full, wall, LABEL_OFFSETS[i])
        for corner in corners:
            fill = QRadialGradient(corner, 26)
            fill.setColorAt(0, QColor(DRAWN["stone-light"]))
            fill.setColorAt(1, STONE_DARK)
            g.setBrush(QBrush(fill))
            g.setPen(QPen(QColor(DRAWN["timber"]), 1.5))
            g.drawEllipse(corner, 22, 22)
        gate = QPointF(cx, cy + half_h)
        g.setBrush(QBrush(STONE))
        g.setPen(QPen(QColor(DRAWN["timber"]), 1.5))
        g.drawRect(QRectF(gate.x() - 30, gate.y() - 20, 60, 40))
        g.setBrush(QBrush(QColor(DRAWN["timber"])))
        g.drawRect(QRectF(gate.x() - 9, gate.y() - 4, 18, 24))
        keep = QRectF(cx - 46, cy - 44, 92, 82)
        g.setBrush(QBrush(STONE))
        g.drawRect(keep)
        heraldry.paint(
            g,
            garrison_arms(self.saga, self.siege),
            QRectF(cx - 20, keep.top() + 12, 40, 48),
            PIGMENTS["ink"],
        )
        _boxed(
            g,
            QRectF(keep.left() - 20, keep.bottom() + 2, keep.width() + 40, 18),
            "The Keep",
            font(10.5, italic=True),
            p["label"],
        )
        self._mine(g, plan, corners[0])
        self._engines(g, plan, corners)
        self._rose(g, plan, ink)

    def _mine(self, g: QPainter, plan: QRectF, target: QPointF) -> None:
        s, p = self.siege, self.p
        if s.miners > 0:
            mine = QPainterPath(QPointF(plan.left() + 30, plan.top() + 60))
            mine.cubicTo(
                QPointF(plan.left() + 110, plan.top() + 100),
                QPointF(target.x() - 80, target.y() - 40),
                QPointF(target.x() - 26, target.y() - 6),
            )
            g.setPen(QPen(QColor(p["heading"]), 2.6, Qt.PenStyle.DashLine))
            g.setBrush(Qt.BrushStyle.NoBrush)
            g.drawPath(mine)
            _text(
                g,
                QPointF(plan.left() + 20, plan.top() + 44),
                f"the sappers' mine · {s.miners} unit{'s' if s.miners > 1 else ''}",
                font(10.5, italic=True),
                p["heading"],
            )

    def _rose(self, g: QPainter, plan: QRectF, ink: QColor) -> None:
        p = self.p
        rose = QPointF(plan.left() + 52, plan.bottom() - 92)
        for k in range(8):
            ang = math.radians(k * 45 - 90)
            length = 26 if k % 2 == 0 else 14
            tip = rose + QPointF(length * math.cos(ang), length * math.sin(ang))
            side1 = rose + QPointF(5 * math.cos(ang + 1.57), 5 * math.sin(ang + 1.57))
            side2 = rose + QPointF(5 * math.cos(ang - 1.57), 5 * math.sin(ang - 1.57))
            path = QPainterPath(side1)
            path.lineTo(tip)
            path.lineTo(side2)
            path.closeSubpath()
            g.fillPath(path, QColor(p["heading"]) if k == 0 else ink)
        _text(
            g,
            QPointF(rose.x() - 5, rose.y() - 32),
            "N",
            font(10.5, bold=True),
            p["heading"],
        )

    def _wall(
        self,
        g: QPainter,
        a: QPointF,
        b: QPointF,
        left: int,
        full: int,
        name: str,
        offset: QPointF,
    ) -> None:
        p = self.p
        mid = QPointF((a.x() + b.x()) / 2, (a.y() + b.y()) / 2)
        if left <= 0:
            for s, e in (
                (
                    a,
                    QPointF(
                        mid.x() + (a.x() - mid.x()) * 0.25,
                        mid.y() + (a.y() - mid.y()) * 0.25,
                    ),
                ),
                (
                    QPointF(
                        mid.x() + (b.x() - mid.x()) * 0.25,
                        mid.y() + (b.y() - mid.y()) * 0.25,
                    ),
                    b,
                ),
            ):
                self._stones(g, s, e)
            g.setBrush(QBrush(STONE_DARK))
            g.setPen(Qt.PenStyle.NoPen)
            for k in range(12):
                g.drawEllipse(
                    QPointF(
                        mid.x() + 16 * math.sin(k * 2.1),
                        mid.y() + 12 * math.cos(k * 1.7),
                    ),
                    2 + k % 3,
                    2 + k % 2,
                )
            g.setPen(QPen(QColor(p["heading"]), 2.2))
            g.setBrush(Qt.BrushStyle.NoBrush)
            g.drawEllipse(mid, RING, RING)
            _boxed(
                g,
                _beside_ring(mid, a, b, offset),
                f"the {name.lower()} breach",
                font(11, bold=True, italic=True),
                p["heading"],
            )
            return
        self._stones(g, a, b)
        lost = (full - left) / full if full else 0
        cracks = 0 if lost == 0 else 1 if lost < 0.34 else 2 if lost < 0.67 else 3
        g.setPen(QPen(QColor(DRAWN["timber"]), 1.5))
        for k in range(cracks):
            g.drawLine(
                QPointF(mid.x() - 8 + k * 6, mid.y() - 8),
                QPointF(mid.x() - 3 + k * 6, mid.y() + 8),
            )
        _text(
            g, mid + offset, f"{name} {left}/{full}", font(10, italic=True), p["label"]
        )

    def _stones(self, g: QPainter, a: QPointF, b: QPointF) -> None:
        pen = QPen(STONE_DARK, 20, Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap)
        g.setPen(pen)
        g.drawLine(a, b)
        g.setPen(QPen(STONE, 13, Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap))
        g.drawLine(a, b)
        n = int(math.hypot(b.x() - a.x(), b.y() - a.y()) // 18)
        for k in range(1, n):
            t = k / n
            pt = QPointF(a.x() + (b.x() - a.x()) * t, a.y() + (b.y() - a.y()) * t)
            g.fillRect(QRectF(pt.x() - 3, pt.y() - 3, 6, 6), QBrush(STONE_DARK))

    def _engines(self, g: QPainter, plan: QRectF, corners: list[QPointF]) -> None:
        s, p = self.siege, self.p
        count = sum(n for k, n in s.engines.items() if k in siege_rules.WALL_BREAKERS)
        if not count:
            return
        ink = QColor(p["foreground"])
        shown = min(count, 4)
        for i in range(shown):
            at = QPointF(plan.right() - 50, plan.top() + 70 + i * 90)
            g.setPen(QPen(ink, 2))
            g.drawLine(at + QPointF(-14, 0), at + QPointF(0, -24))
            g.drawLine(at + QPointF(14, 0), at + QPointF(0, -24))
            g.drawLine(at + QPointF(-18, 0), at + QPointF(18, 0))
            g.drawLine(at + QPointF(24, -34), at + QPointF(-12, -14))
            g.setBrush(QBrush(ink))
            g.drawRect(QRectF(at.x() - 15, at.y() - 16, 9, 9))
            target = corners[1] if i % 2 == 0 else corners[2]
            arc = QPainterPath(at + QPointF(-18, -34))
            arc.quadTo(
                QPointF((at.x() + target.x()) / 2, min(at.y(), target.y()) - 80), target
            )
            g.setPen(QPen(shade(p["heading"], 150), 1.3, Qt.PenStyle.DotLine))
            g.setBrush(Qt.BrushStyle.NoBrush)
            g.drawPath(arc)
        if count > shown:
            _text(
                g,
                QPointF(plan.right() - 80, plan.top() + 70 + shown * 90),
                f"and {count - shown} more",
                font(10, italic=True),
                p["label"],
            )

    def _chronicle(self, g: QPainter, area: QRectF) -> None:
        s, p = self.siege, self.p
        _text(
            g,
            QPointF(area.left(), area.top() + 6),
            "The chronicle",
            font(16, bold=True),
            p["heading"],
        )
        y = area.top() + 32
        if not s.events:
            _text(
                g,
                QPointF(area.left() + 4, y),
                "No event played yet.",
                font(12, italic=True),
                p["dim"],
            )
        for indent, words, opens in self._chronicle_rows(area.width()):
            if opens:
                g.setBrush(QBrush(QColor(p["heading"])))
                g.setPen(Qt.PenStyle.NoPen)
                g.drawEllipse(QRectF(area.left() + 4, y - 8, 6, 6))
            heading = indent == 18
            f = font(12) if heading else font(10.5, italic=True)
            colour = p["foreground"] if heading else p["label"]
            _text(g, QPointF(area.left() + indent, y), words, f, colour)
            y += CHRONICLE_LINE


class SiegePage(QWidget):
    """A siege's page: the drawn leaf and the buttons that play it."""

    def __init__(self, saga: Saga, siege: Siege, p: Palette, run: Run) -> None:
        super().__init__()
        self.saga, self.siege, self.p, self.run = saga, siege, p, run
        column = QVBoxLayout(self)
        column.setContentsMargins(18, 12, 12, 8)
        column.setSpacing(8)
        self.header = SiegeHeader(saga, siege, p)
        self.body = SiegeBody(saga, siege, p)
        self.buttons = buttons(
            [
                ("Next Siege Event", "combat", lambda: self.act("next_siege_event")),
                ("Siege Actions", "update", lambda: self.act("siege_actions")),
                ("Edit Siege", "edit", self.edit),
            ],
            p,
        )
        column.addWidget(scrolling_page(p, self.header, self.buttons, self.body), 1)

    def row(self) -> int:
        return self.saga.sieges.index(self.siege)

    def act(self, action: str) -> None:
        self.run(conflicts.command(self.saga, action, self.row()))

    def edit(self) -> None:
        edit = sieges.ops(self.saga).edit
        if edit is not None:
            self.run(edit(self.row()))

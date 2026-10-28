"""The desktop version's few movements, kept short (150 to 250 ms),
easing out and never in the way of a click or a key: the inspector's new
item inking in, a chosen row's wash spreading, an XP line growing, a
chapter fading in, the dials winding up, and a wax seal pressed on the
page after Advance Season and when a character is finished.

Every movement goes through `tween` (and a pause through `hold`), which
the chosen player carries out: `Moving` animates, `Still` jumps straight
to the end. Still is used while the Reduce motion setting is on and
whenever ARMARIUS_MOTION is "off" (the tests), so no caller checks the
setting. Until the setting is first changed, it follows Windows' own
"Animation effects".
"""

from __future__ import annotations

import ctypes
import os
import sys
from collections.abc import Callable
from typing import Protocol

from PySide6.QtCore import (
    QEasingCurve,
    QObject,
    QPointF,
    QRectF,
    Qt,
    QTimer,
    QVariantAnimation,
)
from PySide6.QtGui import QPainter, QPaintEvent, QPixmap
from PySide6.QtWidgets import QWidget

from .. import settings

#: Turns every movement off whatever the setting says (the tests set it).
ENV_VAR = "ARMARIUS_MOTION"

#: How long the movements take, in milliseconds.
QUICK = 180
SLOW = 250
#: How long the page takes to change between a record's modes.
MODE_FADE = 450

Step = Callable[[float], None]
Done = Callable[[], None]


class Player(Protocol):
    def tween(
        self,
        owner: QObject,
        step: Step,
        ms: int,
        *,
        name: str,
        start: float,
        end: float,
        done: Done | None,
    ) -> None: ...

    def hold(self, owner: QObject, ms: int, then: Done) -> None: ...


class Still:
    """A player that moves nothing: each movement ends at once."""

    def tween(
        self,
        owner: QObject,
        step: Step,
        ms: int,
        *,
        name: str,
        start: float,
        end: float,
        done: Done | None,
    ) -> None:
        step(end)
        if done is not None:
            done()

    def hold(self, owner: QObject, ms: int, then: Done) -> None:
        then()


class Moving:
    """Moves from `start` to `end` over `ms`, easing out. A movement of
    the same `name` still running on `owner` is stopped first, so a quick
    run of choices never stacks up."""

    def tween(
        self,
        owner: QObject,
        step: Step,
        ms: int,
        *,
        name: str,
        start: float,
        end: float,
        done: Done | None,
    ) -> None:
        running = owner.findChild(
            QVariantAnimation, name, Qt.FindChildOption.FindDirectChildrenOnly
        )
        if running is not None:
            # Stopping deletes it; unnamed, it is not found again meanwhile.
            running.setObjectName("")
            running.stop()
        tween = QVariantAnimation(owner)
        tween.setObjectName(name)
        tween.setStartValue(float(start))
        tween.setEndValue(float(end))
        tween.setDuration(ms)
        tween.setEasingCurve(QEasingCurve.Type.OutCubic)
        tween.valueChanged.connect(lambda value: step(float(value)))
        if done is not None:
            tween.finished.connect(done)
        step(start)
        tween.start(QVariantAnimation.DeletionPolicy.DeleteWhenStopped)

    def hold(self, owner: QObject, ms: int, then: Done) -> None:
        QTimer.singleShot(ms, owner, then)


_player: Player | None = None


def windows_animates() -> bool:
    """Whether Windows' "Animation effects" is on (True elsewhere)."""
    if sys.platform != "win32":
        return True
    on = ctypes.c_int(1)
    # SPI_GETCLIENTAREAANIMATION: the setting Windows calls Animation effects.
    if not ctypes.windll.user32.SystemParametersInfoW(0x1042, 0, ctypes.byref(on), 0):
        return True
    return bool(on.value)


def reduced() -> bool:
    """Whether the Reduce motion setting is on: as set, or until it is,
    on while Windows' Animation effects are off."""
    chosen = settings.load_settings().get("reduce_motion")
    if isinstance(chosen, bool):
        return chosen
    return not windows_animates()


def set_reduced(on: bool) -> None:
    """Turn Reduce motion on or off, and remember it."""
    global _player
    settings.update_settings(reduce_motion=on)
    _player = None


def _chosen() -> Player:
    if os.environ.get(ENV_VAR) == "off" or reduced():
        return Still()
    return Moving()


def player() -> Player:
    global _player
    if _player is None:
        _player = _chosen()
    return _player


def tween(
    owner: QObject,
    step: Step,
    ms: int = QUICK,
    *,
    name: str = "tween",
    start: float = 0.0,
    end: float = 1.0,
    done: Done | None = None,
) -> None:
    """Call `step` with values from `start` to `end` over `ms`, then
    `done`; with no motion, `step(end)` and `done` at once."""
    player().tween(owner, step, ms, name=name, start=start, end=end, done=done)


def hold(owner: QObject, ms: int, then: Done) -> None:
    """Call `then` after `ms` (at once with no motion, as a pause only
    matters to something moving)."""
    player().hold(owner, ms, then)


# -- the movements themselves --


class Cover(QWidget):
    """How a widget looked a moment ago, laid over it and fading away,
    so it seems to change into its new look. It takes no clicks."""

    def __init__(self, host: QWidget, before: QPixmap) -> None:
        super().__init__(host)
        self.before, self.shown = before, 1.0
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setGeometry(host.rect())

    def _fade(self, value: float) -> None:
        self.shown = value
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setOpacity(self.shown)
        painter.drawPixmap(0, 0, self.before)
        painter.end()


def fade_from(host: QWidget, before: QPixmap, ms: int = SLOW) -> Cover:
    """Lay `before` (how `host` looked) over `host` and fade it away."""
    cover = Cover(host, before)
    cover.show()
    cover.raise_()
    tween(
        cover, cover._fade, ms, name="fade", start=1.0, end=0.0, done=cover.deleteLater
    )
    return cover


def slide_in(page: QWidget, rise: int = 8, ms: int = QUICK) -> None:
    """Bring `page` up into its place from `rise` pixels below."""
    home = page.pos()

    def step(value: float) -> None:
        page.move(home.x(), home.y() + round(rise * (1 - value)))

    tween(page, step, ms, name="slide")


def moving() -> bool:
    """Whether movements are shown (for one that is skipped, not just
    ended at once, with no motion)."""
    return not isinstance(player(), Still)


def turn_page(stack: QWidget, change: Callable[[], QWidget | None]) -> None:
    """Change what `stack` shows (`change`, which returns the new page),
    fading from how it looked and sliding the new page up a little."""
    if not moving() or not stack.isVisible():
        change()
        return
    before = stack.grab()
    page = change()
    fade_from(stack, before, QUICK)
    if page is not None:
        slide_in(page)


# -- the seal pressed on the page --

#: How long the seal stays pressed before it fades, in milliseconds.
SEAL_HOLD = 900


class PressedSeal(QWidget):
    """A wax seal pressed on the page's lower right: it drops onto the
    page, settles, stays a moment and fades away. `draw` paints the seal
    centred on a point with a radius. It takes no clicks."""

    RADIUS = 34

    def __init__(
        self, host: QWidget, draw: Callable[[QPainter, QPointF, float], None]
    ) -> None:
        super().__init__(host)
        self.draw = draw
        self.scale, self.shown = 1.25, 0.0
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        side = self.RADIUS * 3
        self.resize(side, side)
        self.move(host.width() - side - 24, host.height() - side - 24)

    def press(self) -> None:
        self.show()
        self.raise_()
        tween(self, self._press, QUICK, name="press", done=self._pressed)

    def _press(self, value: float) -> None:
        self.scale, self.shown = 1.25 - 0.25 * value, value
        self.update()

    def _pressed(self) -> None:
        hold(self, SEAL_HOLD, self._lift)

    def _lift(self) -> None:
        tween(
            self,
            self._fade,
            SLOW,
            name="lift",
            start=1.0,
            end=0.0,
            done=self.deleteLater,
        )

    def _fade(self, value: float) -> None:
        self.shown = value
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        if self.shown <= 0:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setOpacity(self.shown)
        centre = QRectF(self.rect()).center()
        self.draw(painter, centre, self.RADIUS * self.scale)
        painter.end()


def press_seal(
    host: QWidget, draw: Callable[[QPainter, QPointF, float], None]
) -> PressedSeal | None:
    """Press a seal (`draw`) on `host`'s lower right; with no motion,
    none is pressed."""
    if not moving():
        return None
    seal = PressedSeal(host, draw)
    seal.press()
    return seal

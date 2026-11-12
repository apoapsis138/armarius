"""The desktop version's few sounds, kept for the moments that mean
something: a page turned for a chapter (a longer one for a record), a
quill when a form is saved, coins for the Treasury, a chest for the
Inventory, a wax seal for Advance Season and a dull knock when an entry
is refused. Plain button presses stay silent.

`play(cue)` is the one way in. It plays through Windows' own `winsound`,
so nothing new is installed; on any other system, while the Sounds
setting is off, and whenever ARMARIUS_SOUNDS is "off" (the tests) the
player is a silent one that does nothing, so no caller checks.

Bluetooth speakers and headphones let their link sleep when nothing plays
and lose the start of the next sound while it wakes, which for a short page
turn is nearly all of it. So while the app is the active one, the Windows
player holds a silent stream open (AwakeLink); leaving the app lets it go,
so Armarius idle in the background doesn't keep the computer from sleeping.
"""

from __future__ import annotations

import ctypes
import os
import sys
from ctypes import wintypes
from pathlib import Path
from typing import Protocol

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication

from .. import artwork, settings

#: Turns every sound off whatever the setting says (the tests set it).
ENV_VAR = "ARMARIUS_SOUNDS"


class Player(Protocol):
    def play(self, path: Path) -> None: ...


class Silent:
    """A player that plays nothing."""

    def play(self, path: Path) -> None:
        pass


class _WaveFormat(ctypes.Structure):
    _fields_ = [
        ("wFormatTag", wintypes.WORD),
        ("nChannels", wintypes.WORD),
        ("nSamplesPerSec", wintypes.DWORD),
        ("nAvgBytesPerSec", wintypes.DWORD),
        ("nBlockAlign", wintypes.WORD),
        ("wBitsPerSample", wintypes.WORD),
        ("cbSize", wintypes.WORD),
    ]


class _WaveHeader(ctypes.Structure):
    _fields_ = [
        ("lpData", ctypes.c_void_p),
        ("dwBufferLength", wintypes.DWORD),
        ("dwBytesRecorded", wintypes.DWORD),
        ("dwUser", ctypes.c_size_t),
        ("dwFlags", wintypes.DWORD),
        ("dwLoops", wintypes.DWORD),
        ("lpNext", ctypes.c_void_p),
        ("reserved", ctypes.c_size_t),
    ]


#: Linear PCM, for waveOutOpen.
_WAVE_FORMAT_PCM = 1
#: Whichever device the system prefers, for waveOutOpen.
_WAVE_MAPPER = 0xFFFFFFFF
#: This buffer begins and ends a loop, for waveOutWrite.
_WHDR_LOOP = 0x04 | 0x08
_RATE = 8000


class AwakeLink:
    """A silent stream on the audio device, looping for as long as it is
    held. A device that refuses just leaves it unheld: the sounds play as
    they would without it."""
    _winmm: ctypes.CDLL
    _header: _WaveHeader
    def __init__(self) -> None:
        if sys.platform != "win32":
            raise OSError("AwakeLink plays through Windows' own audio")
        self._winmm = ctypes.WinDLL("winmm")
        self._device: wintypes.HANDLE | None = None
        self._silence = ctypes.create_string_buffer(_RATE)
        self._header = _WaveHeader(
            lpData=ctypes.addressof(self._silence),
            dwBufferLength=_RATE,
            dwFlags=_WHDR_LOOP,
            dwLoops=0xFFFFFFFF,
        )

    def hold(self) -> None:
        if self._device is not None:
            return
        size = ctypes.sizeof(_WaveHeader)
        wave = _WaveFormat(_WAVE_FORMAT_PCM, 1, _RATE, _RATE * 2, 2, 16, 0)
        device = wintypes.HANDLE()
        if self._winmm.waveOutOpen(
            ctypes.byref(device), _WAVE_MAPPER, ctypes.byref(wave), None, None, 0
        ):
            return
        self._winmm.waveOutPrepareHeader(device, ctypes.byref(self._header), size)
        self._winmm.waveOutWrite(device, ctypes.byref(self._header), size)
        self._device = device

    def release(self) -> None:
        if self._device is None:
            return
        device, self._device = self._device, None
        size = ctypes.sizeof(_WaveHeader)
        self._winmm.waveOutReset(device)
        self._winmm.waveOutUnprepareHeader(device, ctypes.byref(self._header), size)
        self._winmm.waveOutClose(device)


class Windows:
    """Plays a sound without waiting for it, cutting off one still
    playing (winsound plays one at a time). Holds `link` while the app is
    the active one."""

    def __init__(self, link: AwakeLink | None = None) -> None:
        self.link = link or AwakeLink()
        self._app = QGuiApplication.instance()
        if isinstance(self._app, QGuiApplication):
            self._app.applicationStateChanged.connect(self._follow)
            self._follow(self._app.applicationState())

    def _follow(self, state: Qt.ApplicationState) -> None:
        if state == Qt.ApplicationState.ApplicationActive:
            self.link.hold()
        else:
            self.link.release()

    def close(self) -> None:
        """Let the link go, the sounds having been turned off."""
        if isinstance(self._app, QGuiApplication):
            self._app.applicationStateChanged.disconnect(self._follow)
        self.link.release()

    def play(self, path: Path) -> None:
        if sys.platform == "win32":
            import winsound

            winsound.PlaySound(
                str(path),
                winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT,
            )


_player: Player | None = None


def enabled() -> bool:
    """Whether the Sounds setting is on (it is unless turned off)."""
    return settings.load_settings().get("sounds", True) is not False


def set_enabled(on: bool) -> None:
    """Turn the sounds on or off, and remember it."""
    global _player
    settings.update_settings(sounds=on)
    if isinstance(_player, Windows):
        _player.close()
    _player = None


def _chosen() -> Player:
    if os.environ.get(ENV_VAR) == "off" or not enabled():
        return Silent()
    return Windows() if sys.platform == "win32" else Silent()


def play(cue: str) -> None:
    """Play the sound for `cue` (artwork.SOUNDS); KeyError for one the
    registry lacks."""
    global _player
    path = artwork.SOUNDS[cue]
    if _player is None:
        _player = _chosen()
    _player.play(path)

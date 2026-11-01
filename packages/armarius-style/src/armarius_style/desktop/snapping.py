"""Windows Snap for the window that draws its own title bar.

Windows snaps, and offers Win+arrow and the snap layouts, only for a
window whose style says it can be resized and maximised. A Qt frameless
window drops those styles along with the system's title bar, so they are
put back here (a thick frame, a caption, the minimise and maximise
boxes), and WM_NCCALCSIZE keeps the system from drawing a frame for
them: the window's own paper fills it, and while maximised it fills the
screen's work area, not the band past its edges that Windows adds for a
frame. Elsewhere nothing changes.
"""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QWidget

if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes

    _user32 = ctypes.windll.user32

    GWL_STYLE = -16
    WS_THICKFRAME = 0x00040000
    WS_CAPTION = 0x00C00000
    WS_SYSMENU = 0x00080000
    WS_MINIMIZEBOX = 0x00020000
    WS_MAXIMIZEBOX = 0x00010000
    #: What a resizable, maximisable window's style has, for Snap.
    SNAPPABLE = (
        WS_THICKFRAME | WS_CAPTION | WS_SYSMENU | WS_MINIMIZEBOX | WS_MAXIMIZEBOX
    )
    SWP_FLAGS = 0x0001 | 0x0002 | 0x0004 | 0x0010 | 0x0020  # keep all but the frame
    WM_NCCALCSIZE = 0x0083
    MONITOR_DEFAULTTONEAREST = 2

    _user32.GetWindowLongPtrW.restype = ctypes.c_ssize_t
    _user32.GetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int]
    _user32.SetWindowLongPtrW.restype = ctypes.c_ssize_t
    _user32.SetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_ssize_t]
    _user32.MonitorFromWindow.restype = wintypes.HMONITOR
    _user32.MonitorFromWindow.argtypes = [wintypes.HWND, wintypes.DWORD]

    class _MonitorInfo(ctypes.Structure):
        _fields_ = [
            ("cbSize", wintypes.DWORD),
            ("rcMonitor", wintypes.RECT),
            ("rcWork", wintypes.RECT),
            ("dwFlags", wintypes.DWORD),
        ]

    class _CalcSizeParams(ctypes.Structure):
        _fields_ = [("rgrc", wintypes.RECT * 3), ("lppos", ctypes.c_void_p)]

    def make_snappable(window: QWidget) -> None:
        hwnd = int(window.winId())
        style = _user32.GetWindowLongPtrW(hwnd, GWL_STYLE)
        if style & SNAPPABLE != SNAPPABLE:
            _user32.SetWindowLongPtrW(hwnd, GWL_STYLE, style | SNAPPABLE)
            _user32.SetWindowPos(hwnd, None, 0, 0, 0, 0, SWP_FLAGS)

    def native_event(window: QWidget, event_type: bytes, message: int) -> int | None:
        if event_type != b"windows_generic_MSG":
            return None
        msg = wintypes.MSG.from_address(message)
        if msg.message != WM_NCCALCSIZE or not msg.wParam:
            return None
        if window.isMaximized():
            params = _CalcSizeParams.from_address(msg.lParam)
            info = _MonitorInfo()
            info.cbSize = ctypes.sizeof(_MonitorInfo)
            monitor = _user32.MonitorFromWindow(msg.hWnd, MONITOR_DEFAULTTONEAREST)
            if _user32.GetMonitorInfoW(monitor, ctypes.byref(info)):
                params.rgrc[0] = info.rcWork
        # The whole window is the client area: no system frame drawn.
        return 0

else:

    def make_snappable(window: QWidget) -> None:
        """Give `window` back the styles Windows snaps by (Windows only)."""

    def native_event(window: QWidget, event_type: bytes, message: int) -> int | None:
        """The result for a native message the window answers itself, or
        None to leave it to Qt (Windows only)."""
        return None

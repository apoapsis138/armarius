"""The desktop draws on X11 under GNOME on Linux, where Wayland leaves
GNOME's busy cursor up after focus moves between windows."""

from __future__ import annotations

from ars_magica_manager.gui.app import QT_PLATFORM, X11_FIRST, choose_display

GNOME_WAYLAND = {
    "XDG_CURRENT_DESKTOP": "GNOME",
    "WAYLAND_DISPLAY": "wayland-0",
    "DISPLAY": ":0",
}


def chosen(env: dict[str, str], platform: str = "linux") -> str | None:
    choose_display(env, platform)
    return env.get(QT_PLATFORM)


def test_gnome_on_wayland_draws_on_x11_first() -> None:
    assert chosen(dict(GNOME_WAYLAND)) == X11_FIRST


def test_a_desktop_named_with_gnome_counts() -> None:
    assert chosen({**GNOME_WAYLAND, "XDG_CURRENT_DESKTOP": "ubuntu:GNOME"}) == X11_FIRST


def test_the_users_own_choice_is_kept() -> None:
    assert chosen({**GNOME_WAYLAND, QT_PLATFORM: "wayland"}) == "wayland"


def test_other_desktops_and_systems_are_left_alone() -> None:
    assert chosen({**GNOME_WAYLAND, "XDG_CURRENT_DESKTOP": "KDE"}) is None
    assert chosen(dict(GNOME_WAYLAND), platform="win32") is None


def test_wayland_stays_with_no_x11_to_fall_back_to() -> None:
    no_x11 = {key: value for key, value in GNOME_WAYLAND.items() if key != "DISPLAY"}
    assert chosen(no_x11) is None

"""The performance guard on Footer rebuilds (CONTRIBUTING.md "Performance
rules"): a rebuild of the Footer is counted, never timed, and after each
one it must show exactly the keys the screen has."""

from textual.widgets._footer import FooterKey

from ars_magica_manager.tui.screens.widgets import SplitFooter

#: Footer rebuilds allowed per action (a tab switch, a focus move, an arrow
#: key). A tab switch once rebuilt it 4-6 times.
FOOTER_REBUILDS_PER_ACTION = 1


def footer(app) -> SplitFooter:
    return app.screen.query_one(SplitFooter)


def check_footer_current(app, action: str) -> None:
    """The Footer shows exactly the keys the screen has now (a skipped
    rebuild must never leave it stale)."""
    shown = {
        binding.action: enabled
        for binding, enabled in (
            (b, e) for (_, b, e, _) in app.screen.active_bindings.values()
        )
        if binding.show
    }
    in_footer = {
        key.action: not key.disabled
        for key in app.screen.query(FooterKey)
        if key.action != "command_palette"  # ^p, always shown on the right
    }
    assert in_footer == shown, f"stale Footer after {action}"


def check_footer_rebuilds(app, before: int, action: str) -> None:
    rebuilds = footer(app).rebuilds - before
    assert rebuilds <= FOOTER_REBUILDS_PER_ACTION, (
        f"{action}: the Footer was rebuilt {rebuilds} times"
    )
    check_footer_current(app, action)

"""The terminal Creation Worksheet's Review Interests step: Restore the
defaults among the step's buttons, beside Edit Interests."""

from __future__ import annotations

from support import wait_until
from test_creation_worksheet import _open_worksheet, _press_button, _saga, _text
from textual.widgets import Button, OptionList

from ars_magica_manager import storage
from ars_magica_manager.tui.app import ArsMagicaManagerApp


async def test_review_interests_restores_the_defaults_beside_edit_interests():
    storage.save_saga(_saga("grog"))  # made in code: its interests are chosen
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        screen = await _open_worksheet(pilot, app)
        steps = screen.query_one("#ws-steps", OptionList)
        steps.highlighted = steps.option_count - 2
        assert await wait_until(pilot, lambda: screen.step == "interests")
        assert await wait_until(
            pilot, lambda: "the player's own" in _text(screen, "#ws-budget")
        )

        def labels() -> list[str]:
            buttons = screen.query("#ws-actions Button").results(Button)
            return [str(b.label) for b in buttons]

        assert await wait_until(
            pilot,
            lambda: (
                "Edit Interests" in labels()
                and labels()[labels().index("Edit Interests") + 1 :][:1]
                == ["Restore the defaults"]
            ),
        )
        await _press_button(pilot, screen, "Restore the defaults")
        assert await wait_until(
            pilot,
            lambda: not storage.load_saga("test_saga").characters[0].interests_chosen,
        )
        assert await wait_until(
            pilot, lambda: "These are the defaults" in _text(screen, "#ws-budget")
        )

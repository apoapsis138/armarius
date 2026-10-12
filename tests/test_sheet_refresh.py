"""SheetView's refresh registry: a section's own refreshers,
then those for a family of sections, each once, and a refresher whose tab
isn't built doesn't stop the rest."""

from textual.css.query import NoMatches

from ars_magica_manager.models import Saga
from ars_magica_manager.tui.screens.sheets import SheetView


def test_refreshers_run_once_in_order_and_survive_an_unbuilt_tab():
    view = SheetView(Saga(id="s", name="S"))
    ran: list[str] = []

    def unbuilt() -> None:
        ran.append("unbuilt")
        raise NoMatches("a lazy tab not built yet")

    def shared() -> None:
        ran.append("shared")

    view._on_refresh("section-a", lambda: ran.append("own"))
    view._on_refresh("section-a", unbuilt)
    view._on_refresh("section-a", shared)
    view._on_refresh_matching(lambda s: s.startswith("section-"), shared)
    view._on_refresh_matching(lambda _: True, lambda: ran.append("any"))

    view.refresh_section("section-a")
    assert ran == ["own", "unbuilt", "shared", "any"]

    ran.clear()
    view.refresh_section("section-b")
    assert ran == ["shared", "any"]

    ran.clear()
    view.refresh_section("tab-x")
    assert ran == ["any"]

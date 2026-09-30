"""What the covenant sheet's Boons & Hooks section shows: the two titles'
points and colour, the rows, and the details panel."""

import pytest
from support import strip_markup
from textual.content import Content

from ars_magica_manager.models import (
    BOON_HOOK_DESCRIPTION,
    BOON_HOOK_DETAIL,
    BOON_HOOK_UNKNOWN,
    Covenant,
    VirtueFlawInstance,
)
from ars_magica_manager.screens.widgets import (
    boon_hook_info_text,
    boon_hook_rows,
    boon_hook_title,
)


def _covenant(*ids: str) -> Covenant:
    covenant = Covenant(id="cov1", saga_id="s", name="Keep")
    covenant.boons_hooks = [VirtueFlawInstance(vf_id=i) for i in ids]
    return covenant


def _info(covenant: Covenant, index: int) -> str:
    return strip_markup(boon_hook_info_text(covenant, index))


@pytest.mark.parametrize(
    ("attached", "colour", "plain"),
    [
        # Equal (nothing attached is equal too).
        ((), "$text-success", ("Boons (0 pts)", "Hooks (0 pts)")),
        # Boons (1) < Hooks (3): points still to spend, plain.
        (
            ("covbh_boon_minor_wealth", "covbh_hook_major_castle"),
            None,
            ("Boons (1 pt)", "Hooks (3 pts)"),
        ),
        # Boons (3) > Hooks (1).
        (
            ("covbh_boon_major_wealth", "covbh_hook_minor_rival"),
            "$text-error",
            ("Boons (3 pts)", "Hooks (1 pt)"),
        ),
        (
            ("covbh_boon_major_wealth", "covbh_hook_major_castle"),
            "$text-success",
            ("Boons (3 pts)", "Hooks (3 pts)"),
        ),
    ],
)
def test_the_titles_share_a_colour_set_by_how_the_totals_compare(
    attached, colour, plain
):
    covenant = _covenant(*attached)
    for kind, text in zip(("Boon", "Hook"), plain, strict=True):
        # Only the parenthesised total is coloured.
        label, total = text.split(" ", 1)
        expected = f"{label} [{colour}]{total}[/]" if colour else text
        assert boon_hook_title(covenant, kind) == expected


def test_the_panel_shows_name_type_tier_and_rules_text():
    covenant = _covenant("covbh_boon_minor_edifice", "covbh_hook_major_castle")
    edifice = _info(covenant, 0)
    assert "Name: Edifice" in edifice
    assert "Type: Fortifications" in edifice  # the book's type of Boon/Hook
    assert "Tier: Minor Boon (1 pt)" in edifice
    assert "major building erected to inspire awe" in edifice  # the rules text
    assert "Tier: Major Hook (3 pts)" in _info(covenant, 1)
    assert "Select a Boon or Hook" in boon_hook_info_text(covenant, None)


def test_the_panel_shows_the_type_and_omits_it_for_untyped_entries():
    covenant = _covenant(
        "covbh_boon_free_manor_house",
        "covbh_hook_major_unknown",
        "covbh_hook_minor_weak_aura",
    )
    assert "Type: Fortifications" in _info(covenant, 0)
    assert "Tier: Free Boon" in _info(covenant, 0)  # no cost for a Free Choice
    assert "pt)" not in _info(covenant, 0).split("Rules:")[0]
    assert "Type:" not in _info(covenant, 1)  # Unknown isn't filed under a type
    assert "Tier: Major Hook (3 pts)" in _info(covenant, 1)
    assert "Type: Site" in _info(covenant, 2)


def test_the_panel_shows_prerequisites_exclusions_and_repeatability():
    covenant = _covenant(
        "covbh_boon_minor_shell_keep",
        "covbh_boon_minor_seclusion",
        "covbh_boon_minor_aura",
        "covbh_boon_minor_wealth",
        "covbh_boon_minor_edifice",
        "covbh_boon_major_magical_soldiers",
    )
    assert "Requires: Castle" in _info(covenant, 0)
    assert "Not with: Road, Urban" in _info(covenant, 1)
    aura = _info(covenant, 2)
    assert "May be taken up to 7 times; the effects stack." in aura
    assert "Effect: The covenant's Magic aura +1" in aura
    assert aura.endswith("Source: ArM5; Covenants")
    plain = _info(covenant, 3)
    for absent in ("Requires", "Not with", "May be taken", "Effect:"):
        assert absent not in plain
    # A building Boon: its Buildings surcharge, and it may be repeated.
    assert "Effect: Yearly expenditure: Buildings +2" in _info(covenant, 4)
    assert "May be taken more than once" in _info(covenant, 4)
    assert "Requires one of: Cavalry, Crossbowmen, Criminals" in _info(covenant, 5)


def test_an_unknown_hook_says_so_in_its_row_title_and_panel():
    covenant = _covenant("covbh_hook_minor_rival", "covbh_hook_minor_haunted")
    covenant.boons_hooks[0].params = {BOON_HOOK_UNKNOWN: "yes"}
    rows = [strip_markup(label) for _, label in boon_hook_rows(covenant, "Hook")]
    assert rows == ["Rival (Unknown, 3 pts)", "Haunted"]
    assert strip_markup(boon_hook_title(covenant, "Hook")) == "Hooks (4 pts)"
    assert "Unknown: Yes (counts 3 points, as a Major Hook)" in _info(covenant, 0)
    assert "May be Unknown (mark it in its Edit form)." in _info(covenant, 1)


def test_rows_keep_their_index_into_the_whole_list():
    covenant = _covenant(
        "covbh_boon_minor_aura", "covbh_hook_minor_rival", "covbh_boon_minor_edifice"
    )
    assert [i for i, _ in boon_hook_rows(covenant, "Boon")] == [0, 2]
    assert [i for i, _ in boon_hook_rows(covenant, "Hook")] == [1]


def test_the_detail_is_named_and_its_brackets_stay_literal():
    covenant = _covenant("covbh_boon_minor_edifice")
    covenant.boons_hooks[0].params = {BOON_HOOK_DETAIL: "The [Tower] of Iris"}
    shown = Content.from_markup(boon_hook_info_text(covenant, 0)).plain
    assert "Name: Edifice - The [Tower] of Iris" in shown


def test_the_description_leads_with_emphasis_and_the_rules_text_is_literal():
    covenant = _covenant("covbh_boon_minor_hidden_resources")
    covenant.boons_hooks[0].params = {
        BOON_HOOK_DESCRIPTION: (
            "**Accessible Value:** 250 Build Points\n\n"
            "**Location:** sealed *behind* a wall in [The Tower]"
        )
    }
    content = Content.from_markup(boon_hook_info_text(covenant, 0))
    plain = content.plain
    assert "**" not in plain and "*behind*" not in plain  # markers consumed
    assert "Accessible Value: 250 Build Points" in plain
    assert "[The Tower]" in plain  # brackets still literal
    assert plain.index("Description:") < plain.index("Rules:")
    styled = {(plain[s.start : s.end], str(s.style)) for s in content.spans}
    assert ("Accessible Value:", "b") in styled
    assert ("Location:", "b") in styled
    assert ("behind", "i") in styled
    # The official rules text is NOT interpreted as Markdown.
    rules = plain.index("Rules:")
    assert not any(str(s.style) == "i" and s.start > rules for s in content.spans)

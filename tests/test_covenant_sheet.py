"""The covenant page's figures (covenant_sheet), without a front-end."""

from __future__ import annotations

from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager.models import (
    Book,
    CovenantDiaryEntry,
    IncomeSource,
    Inhabitant,
    ScoredTrait,
    Tribunal,
    VirtueFlawInstance,
)
from ars_magica_manager.sheets import covenant as cvs


def _covenant():
    saga = _sample_saga_with_covenant()
    return saga, saga.covenants[0]


def test_the_subtitle_names_the_tribunal_season_and_founding():
    saga, covenant = _covenant()
    saga.tribunals.append(Tribunal(id="rhine", name="Rhine"))
    covenant.tribunal_id, covenant.year_founded = "rhine", 1137
    assert cvs.subtitle(saga, covenant) == (
        "Rhine Tribunal  ·  Spring covenant  ·  founded 1137  ·  Spring 1220"
    )


def test_the_aura_adds_what_the_boons_give():
    _saga, covenant = _covenant()
    covenant.boons_hooks.append(VirtueFlawInstance("covbh_boon_minor_aura"))
    aura = cvs.aura(covenant)
    assert (aura.covenant, aura.modifier, aura.total) == (3, 1, 4)
    assert aura.modifier_from == "from Boons"


def test_boons_and_hooks_are_cards_with_the_points_they_cost_or_give():
    _saga, covenant = _covenant()
    covenant.boons_hooks += [
        VirtueFlawInstance("covbh_boon_major_wealth"),
        VirtueFlawInstance("covbh_hook_minor_road"),
        VirtueFlawInstance("covbh_hook_minor_rival"),
    ]
    (boon,) = cvs.boon_hook_cards(covenant, "Boon")
    assert (boon.index, boon.name, boon.tier, boon.points) == (0, "Wealth", "Major", 3)
    assert [h.index for h in cvs.boon_hook_cards(covenant, "Hook")] == [1, 2]
    assert cvs.boon_hook_points(covenant) == (3, 2)


def test_a_reputation_the_covenant_doesnt_know_of_is_marked():
    _saga, covenant = _covenant()
    covenant.reputations = [ScoredTrait("Haunted", 2, known=False)]
    assert cvs.reputations(covenant) == [cvs.Reputation(0, "Haunted", 2, False)]


def test_inhabitants_are_tables_by_kind_with_their_details():
    saga, covenant = _covenant()
    covenant.inhabitants.append(
        Inhabitant("i1", "turb", "The watch", quantity=6, responsibility="Walls")
    )
    groups = {g.kind: g for g in cvs.inhabitant_groups(saga, covenant)}
    assert list(groups) == ["magus", "turb"]
    assert groups["magus"].table.columns == ["Name", "House", "Year Born", "Gift"]
    turb = groups["turb"]
    assert turb.title == "Turb (6)"
    assert turb.table.rows == [["The watch", "Walls", "6"]]
    assert "Walls" in turb.details[0]


def test_possessions_list_each_kind_the_covenant_has():
    saga, covenant = _covenant()
    groups = {g.kind: g for g in cvs.possession_groups(saga, covenant)}
    assert groups["vis_store"].table.rows == [["Ignem Vis", "Ignem", "5"]]
    assert groups["sanctum"].table.rows[0][0] == "Leandro's Sanctum"


def test_the_treasury_sets_income_against_expenditure():
    saga, covenant = _covenant()
    covenant.economics.income_sources = [IncomeSource("s1", "Mill", income=40)]
    account = cvs.treasury(saga, covenant)
    assert account.income == 40
    assert account.balance == account.income - account.expenditure
    titles = [g.title for g in account.groups]
    assert titles == ["Sources of Income (1)", "Yearly Expenditure", "Cost Savings"]
    assert account.groups[0].table.rows == [["Mill", "Typical", "40", ""]]


def test_the_library_puts_each_book_on_its_shelf():
    saga, covenant = _covenant()
    saga.books.append(
        Book(
            "b3",
            "Of Winds",
            "Tractatus",
            art="auram",
            quality=8,
            owner_kind="covenant",
            owner_id="cov1",
        )
    )
    shelves = dict(cvs.shelves(saga, covenant))
    assert list(shelves) == ["Summae", "Tractatus", "Laboratory Texts"]
    (winds,) = shelves["Tractatus"]
    assert (winds.subject, winds.art, winds.quality) == ("Auram", "Auram", 8)
    (summa,) = shelves["Summae"]
    assert (summa.subject, summa.art, summa.level) == ("Magic Theory", "", 8)


def test_the_diary_is_newest_first():
    _saga, covenant = _covenant()
    covenant.diary = [
        CovenantDiaryEntry(1219, "Summer", "Bought a mill", pounds=-60),
        CovenantDiaryEntry(1220, "Spring", "Tithe"),
    ]
    cards = cvs.diary_cards(covenant.diary)
    assert [(c.index, c.when) for c in cards] == [
        (1, "Spring 1220"),
        (0, "Summer 1219"),
    ]
    assert cards[1].amounts == "-60 £"

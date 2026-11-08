"""A season's effects say what they do through one table
(seasons.plans.EFFECT_TEXT), in rules.EFFECT_ORDER."""

from __future__ import annotations

import pytest

from ars_magica_manager.models import SeasonPlan
from ars_magica_manager.rules import activities as rules
from ars_magica_manager.seasons import plans


def _outcome(*effects: rules.SeasonEffect) -> rules.Outcome:
    plan = SeasonPlan(character_id="c", season="Spring", year=1220, activity="x")
    return rules.Outcome("c", plan, None, effects=list(effects))


def test_every_text_is_for_a_known_kind() -> None:
    assert set(plans.EFFECT_TEXT) <= set(rules.EFFECT_ORDER)


def test_lines_follow_the_effect_order_not_the_order_worked_out(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(plans.EFFECT_TEXT, rules.GainFaith, lambda e, p: "faith")
    monkeypatch.setitem(plans.EFFECT_TEXT, rules.Warp, lambda e, p: "warp")
    worked = _outcome(rules.Warp(1, 0), rules.GainFaith(2))
    assert plans.effect_lines(worked) == ["faith", "warp"]


def test_kinds_narrow_the_lines(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(plans.EFFECT_TEXT, rules.GainFaith, lambda e, p: "faith")
    monkeypatch.setitem(plans.EFFECT_TEXT, rules.Warp, lambda e, p: "warp")
    worked = _outcome(rules.Warp(1, 0), rules.GainFaith(2))
    assert plans.effect_lines(worked, (rules.Warp,)) == ["warp"]


def test_a_kind_with_no_text_or_an_empty_one_says_nothing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(plans.EFFECT_TEXT, rules.Warp, lambda e, p: "")
    worked = _outcome(rules.Warp(1, 0), rules.FoundChild())
    assert plans.effect_lines(worked) == []

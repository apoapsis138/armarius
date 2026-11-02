"""The saga's settings as cards: what they say, and what changing one does
to the saga."""

from __future__ import annotations

from ars_magica_manager.forms import saga_settings as ssf
from ars_magica_manager.models import Saga
from ars_magica_manager.rules import options as rule_options
from ars_magica_manager.seasons import defaults
from ars_magica_manager.sheets import saga_settings as sss


def _saga(**fields: object) -> Saga:
    return Saga(id="s", name="Test", **fields)  # type: ignore[arg-type]


def test_every_optional_rule_has_a_card_under_a_heading():
    groups = sss.rule_groups(_saga())
    assert [g.heading for g in groups] == list(rule_options.GROUPS)
    keys = [card.key for group in groups for card in group.cards]
    assert sorted(keys) == sorted(o.key for o in rule_options.OPTIONS)


def test_a_card_says_less_than_the_inspector():
    offenders = [
        o.label for o in rule_options.OPTIONS if not 0 < len(o.brief) < len(o.effect)
    ]
    assert offenders == []


def test_the_detail_gives_the_rule_in_full_and_its_source():
    option = rule_options.OPTIONS_BY_KEY["bruises"]
    card = next(
        c for g in sss.rule_groups(_saga()) for c in g.cards if c.key == option.key
    )
    assert option.effect in card.detail
    assert "pp. 131-132" in card.detail
    assert card.book == "Lords of Men"


def test_a_rule_whose_book_is_out_of_play_is_greyed_and_keeps_its_choice():
    saga = _saga(books_in_play=[], rule_options={"bruises": True})
    card = next(c for g in sss.rule_groups(saga) for c in g.cards if c.key == "bruises")
    assert not card.usable and not card.on
    assert "Lords of Men" in card.refused
    ssf.toggle_setting(saga, "simple_dice_only").apply()
    assert saga.rule_options == {"bruises": True, "simple_dice_only": True}


def test_a_switch_flips_a_rule_and_a_saga_flag():
    saga = _saga()
    ssf.toggle_setting(saga, "simple_dice_only").apply()
    assert rule_options.is_on(saga, "simple_dice_only")
    ssf.toggle_setting(saga, "simple_dice_only").apply()
    assert saga.rule_options == {}
    kept = saga.keep_season_records
    ssf.toggle_setting(saga, "keep_season_records").apply()
    assert saga.keep_season_records is not kept


def test_a_chip_shows_the_value_and_its_form_sets_it():
    saga = _saga()
    form = ssf.choice_form(saga, "unplanned_grogs")
    form.apply({"unplanned_grogs": defaults.NOTHING})
    assert saga.unplanned_grogs == defaults.NOTHING
    card = next(c for c in sss.season_cards(saga) if c.key == "unplanned_grogs")
    assert card.choice == "Nothing"


def test_the_templates_card_counts_them_and_its_form_replaces_them():
    saga = _saga()
    entry = {"name": "Fined", "text": "{party} pays"}
    ssf.choice_form(saga, sss.RULING_TEMPLATES).apply({sss.RULING_TEMPLATES: [entry]})
    assert sss.tribunal_cards(saga)[0].choice == "1 template"

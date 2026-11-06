"""The pieces every record of the saga's world shares: detail level,
attitude and its reasons, favours, links, and Reputation's kind and
reach."""

from __future__ import annotations

import random

import pytest
from support import everything_saga

from ars_magica_manager import economics, world
from ars_magica_manager import sheet_text as st
from ars_magica_manager.forms import trait as trait_forms
from ars_magica_manager.models import (
    FULL,
    LINE,
    SKETCH,
    Attitude,
    Character,
    Covenant,
    Creature,
    Favour,
    Link,
    Reason,
    Saga,
    ScoredTrait,
)
from ars_magica_manager.rules import creation as creation_rules
from ars_magica_manager.seasons import advance, plans


def test_old_saves_load_as_full_played_records():
    covenant = Covenant.from_dict({"id": "c", "saga_id": "s", "name": "Old"})
    character = Character.from_dict({"id": "m", "name": "Old", "type": "magus"})
    assert (covenant.detail, covenant.played, covenant.summary) == (FULL, True, "")
    assert covenant.attitudes == covenant.favours == covenant.links == []
    assert (character.detail, character.links) == (FULL, [])
    assert ScoredTrait("Brave", 2) == ScoredTrait("Brave", 2, True, "", "")


@pytest.mark.parametrize(
    ("start", "changes", "score", "word", "colour"),
    [
        (0, [], 0, "Neutral", "label"),
        (-1, [], -1, "Wary", "text-warning"),
        (1, [1], 2, "Friendly", "text-success"),
        (2, [1, 1, 1], 3, "Allied", "text-success"),  # kept within +3
        (0, [-2, -5], -3, "Hostile", "text-error"),  # and -3
    ],
)
def test_an_attitude_is_its_start_plus_its_reasons(start, changes, score, word, colour):
    attitude = Attitude("arnhaven", start, [Reason("x", c) for c in changes])
    assert world.attitude_score(attitude) == score
    assert world.attitude_word(score) == word
    assert world.attitude_colour(score) == colour


def test_no_attitude_counts_as_neutral():
    covenant = Covenant("c", "s", "Fengheld")
    assert world.attitude_toward(covenant, "arnhaven") is None
    assert world.attitude_score(None) == 0
    covenant.attitudes.append(Attitude("arnhaven", -1))
    assert world.attitude_toward(covenant, "arnhaven") is covenant.attitudes[0]


def test_the_seal_and_working_read_as_on_the_mockups():
    attitude = Attitude(
        "arnhaven",
        0,
        [Reason("Took the ford source", -2, 1221, "Spring"), Reason("Apologised", 1)],
    )
    assert world.seal_markup(-1) == "[$text-warning]◉ −1 Wary[/]"
    assert world.seal_markup(0) == "[$label]◉ 0 Neutral[/]"
    assert world.attitude_working(attitude) == (
        "Started at 0; −2 Took the ford source; +1 Apologised"
    )


def test_favours_are_open_until_repaid():
    owed = Favour("Shelter in winter", "Fengheld", "Arnhaven", 1220, "Winter")
    repaid = Favour("A lent book", repaid_year=1222, repaid_season="Summer")
    assert world.favour_is_open(owed) and not world.favour_is_open(repaid)
    assert world.favour_rows([owed, repaid]) == [
        (0, "Fengheld owes Arnhaven: Shelter in winter (since Winter 1220)"),
        (1, "[$label]A lent book, repaid Summer 1222[/]"),
    ]


def test_a_link_is_followed_both_ways():
    saga = everything_saga()
    covenant, magus = saga.covenants[0], saga.characters[0]
    link = Link("characters", magus.id, "its founder")
    covenant.links.append(link)
    assert world.link_target(saga, link) is magus
    assert world.link_label(saga, link) == f"{magus.name}: its founder"
    # The sample creature links to the magus too.
    assert world.links_to(saga, "characters", magus.id) == [
        (covenant, link),
        (saga.creatures[0], saga.creatures[0].links[0]),
    ]
    assert world.links_to(saga, "characters", "nobody") == []
    gone = Link("books", "burnt")
    assert world.link_target(saga, gone) is None
    assert world.link_label(saga, gone) == "[$label](gone)[/]"


def test_a_link_reaches_a_covenants_possession():
    saga = everything_saga()
    possession = saga.covenants[0].possessions[0]
    assert world.link_target(saga, Link("possessions", possession.id)) is possession


def test_player_covenants_are_the_played_ones():
    saga = everything_saga()
    sketch = Covenant("fengheld", saga.id, "Fengheld", detail=SKETCH, played=False)
    saga.covenants.append(sketch)
    assert sketch not in world.player_covenants(saga)
    assert saga.covenants[0] in world.player_covenants(saga)


# -- what a sketch is left out of --


def _sketched(detail: str = SKETCH):
    saga = everything_saga()
    magus = next(c for c in saga.characters if c.type == "magus")
    magus.detail = detail
    return saga, magus


@pytest.mark.parametrize("detail", [LINE, SKETCH])
def test_a_sketch_is_not_planned_for(detail):
    saga, magus = _sketched(detail)
    assert not world.takes_part_in_play(magus)
    assert magus not in plans.unplanned(saga)
    magus.detail = FULL
    assert magus in plans.unplanned(saga)


def test_a_sketch_does_not_age():
    saga, magus = _sketched()
    lines = advance.year_end_aging(saga, random.Random(1))
    assert magus.id not in {line.character_id for line in lines}


def test_a_sketch_covenant_keeps_no_accounts():
    saga = everything_saga()
    covenant = saga.covenants[0]
    covenant.detail = SKETCH
    assert covenant.name not in [name for name, _ in economics.close_all_years(saga)]
    assert covenant.name not in [
        name for name, _ in economics.covenants_in_deficit(saga)
    ]


def test_a_sketch_has_no_creation_budget():
    saga = everything_saga()
    covenant = saga.covenants[0]
    covenant.in_creation = True
    assert creation_rules.checks(saga, covenant)
    covenant.detail = SKETCH
    assert creation_rules.checks(saga, covenant) == []


# -- Reputation's kind and reach --


def test_a_reputations_form_asks_its_kind_and_reach():
    rep = ScoredTrait("Fair dealing", 2, type="Local", reach="the Ahse valley")
    fields = {
        f.key: f for f in trait_forms.scored_trait_fields("", rep, include_reach=True)
    }
    assert (fields["type"].value, fields["reach"].value) == ("Local", "the Ahse valley")
    assert ("Ecclesiastical", "Ecclesiastical") in fields["type"].options
    plain = {f.key for f in trait_forms.scored_trait_fields("")}
    assert plain == {"name", "score"}
    assert trait_forms.trait_from(
        {"name": "Fair dealing", "score": 2, "type": None, "reach": ""}
    ) == ScoredTrait("Fair dealing", 2)


def test_only_reputation_lists_ask_kind_and_reach():
    traits: list[ScoredTrait] = []
    for section in trait_forms.NOUNS:
        form = trait_forms.trait_ops(traits, section).add()
        keys = {f.key for f in form.fields()}  # type: ignore[union-attr]
        assert ("reach" in keys) == (section in trait_forms.REPUTATION_SECTIONS)


def test_a_reputations_row_shows_its_kind_and_reach():
    assert st.trait_rows(
        [ScoredTrait("Brave", 2), ScoredTrait("Fair dealing", 1, type="Local")]
    ) == [(0, "Brave: +2"), (1, "Fair dealing: +1 [$label](Local)[/]")]


def test_characters_and_creatures_keep_their_standing():
    standing = {
        "attitudes": [
            {
                "covenant_id": "home",
                "start": 1,
                "reasons": [{"what": "Aid", "change": 1}],
            }
        ],
        "favours": [{"what": "A safe road", "owed_by": "Hush", "owed_to": "Home"}],
    }
    character = Character.from_dict(
        {"id": "j", "name": "Jorg", "type": "companion"} | standing
    )
    creature = Creature.from_dict({"id": "h", "name": "Hush"} | standing)
    for record in (character, creature):
        assert world.attitude_score(world.attitude_toward(record, "home")) == 2
        assert record.favours[0].what == "A safe road"
    assert (
        Character.from_dict({"id": "o", "name": "Old", "type": "grog"}).attitudes == []
    )


def test_only_the_troupes_own_people_hold_no_standing():
    saga = Saga(id="s", name="S")
    home = Covenant(id="home", saga_id="s", name="Home")
    other = Covenant(id="far", saga_id="s", name="Far", played=False)
    saga.covenants += [home, other]
    ours = Character(id="a", name="Ours", type="grog", covenant_id="home")
    theirs = Character(id="b", name="Theirs", type="grog", covenant_id="far")
    nobody = Character(id="c", name="Nobody's", type="companion")
    assert not world.holds_standing(saga, ours)
    assert world.holds_standing(saga, theirs)
    assert world.holds_standing(saga, nobody)
    assert world.holds_standing(saga, Creature(id="h", name="Hush"))

"""The end of an apprenticeship (Apprentices pp. 44-48, 58-61): the
Gauntlet (a story, passed outright, or rolled), three failures and the
Quaesitores, an apprentice kept too long, losing the Gift, Parma Magica's
final key, and cantations learned in play (a saga option)."""

from __future__ import annotations

import random

from ars_magica_manager import actions
from ars_magica_manager.actions import NodeKind
from ars_magica_manager.commands import Form, Refuse
from ars_magica_manager.forms import gauntlet as gf
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.models import (
    Ability,
    ArtScore,
    Character,
    Characteristics,
    DiaryEntry,
    Saga,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import gauntlet as gt
from ars_magica_manager.rules import penetration
from ars_magica_manager.rules.xp import ability_xp, art_xp

YEAR = 1220


class Faces(random.Random):
    """A d10 that shows the faces given, in order (0-9)."""

    def __init__(self, *faces: int) -> None:
        super().__init__(0)
        self.faces = list(faces)

    def randrange(self, *args, **kwargs):  # type: ignore[override]
        return self.faces.pop(0)


def _saga(*, cantations: bool = False) -> Saga:
    apprentice = Character(id="a", name="Hugo", type="magus")
    apprentice.background.year_born = YEAR - 25
    apprentice.hermetic.age_of_apprenticeship = 10
    apprentice.characteristics = Characteristics(intelligence=2)
    apprentice.abilities = [
        Ability("Magic Theory", xp=ability_xp(3)),
        Ability("Parma Magica", xp=ability_xp(1)),
    ]
    apprentice.arts = {"vim": ArtScore(xp=art_xp(4))}
    apprentice.virtues_flaws = [
        VirtueFlawInstance("vf_the_gift"),
        VirtueFlawInstance("vf_gentle_gift"),
        VirtueFlawInstance("vf_apprentice"),
    ]
    saga = Saga(id="s", name="S", current_year=YEAR, characters=[apprentice])
    if cantations:
        saga.rule_options = {gt.CANTATIONS_IN_PLAY: True}
    return saga


def _ids(character: Character) -> set[str]:
    return {vf.vf_id for vf in character.virtues_flaws}


# -- the rules --


def test_years_served_and_an_apprentice_kept_too_long():
    saga = _saga()
    hugo = saga.character("a")
    assert gt.years_served(saga, hugo) == 15
    assert not gt.kept_too_long(15)
    hugo.background.year_born = YEAR - 33
    assert gt.years_served(saga, hugo) == 23
    assert gt.punishment_pawns(23) == 80
    said = gt.gauntlet_notes(saga, hugo)
    assert "low crime" in said[1] and "80 pawns" in said[1]


def test_after_three_failures_the_quaesitores_set_it():
    saga = _saga()
    hugo = saga.character("a")
    hugo.diary = [DiaryEntry(YEAR - i, "Spring", gt.FAILED) for i in (1, 2, 3)]
    assert gt.failures(hugo) == 3
    assert any("Quaesitor" in line for line in gt.gauntlet_notes(saga, hugo))


def test_the_optional_roll_against_nine():
    saga = _saga()
    hugo = saga.character("a")
    # Intelligence 2 + Magic Theory 3 + 4 = 9: passed.
    assert gt.rolled(saga, hugo, "Magic Theory", Faces(4)).passed
    assert not gt.rolled(saga, hugo, "Magic Theory", Faces(3)).passed
    botched = gt.rolled(saga, hugo, "Magic Theory", Faces(0, 0))
    assert botched.botched and "dire" in botched.line


def test_passing_makes_a_magus_and_gives_parmas_key():
    saga = _saga()
    hugo = saga.character("a")
    hugo.type = "companion"  # type: ignore[assignment]
    # Withheld before: no Parma in his Magic Resistance.
    before = penetration.magic_resistance(hugo, "Vim")
    assert not any("Parma" in line.label for line in before.lines)
    said = gt.pass_gauntlet(hugo)
    assert "Parma Magica 1 now protects him" in said[0]
    assert hugo.type == "magus"
    assert gt.HERMETIC_MAGUS in _ids(hugo) and "vf_apprentice" not in _ids(hugo)
    after = penetration.magic_resistance(hugo, "Vim")
    assert int(after.total) == int(before.total) + 5


def test_losing_the_gift_for_good_or_suppressed():
    hugo = _saga().character("a")
    gt.lose_gift(hugo, gt.SUPPRESSED)
    assert gt.SUPPRESSED_GIFT in _ids(hugo) and "vf_the_gift" in _ids(hugo)
    hugo = _saga().character("a")
    gt.lose_gift(hugo, gt.LOST)
    assert _ids(hugo) == {gt.FAILED_APPRENTICE}


def test_a_cantation_must_be_cast_its_level_in_times():
    assert gt.cantation_problem(5, 4, False) is not None
    assert gt.cantation_problem(5, 5, False) is None
    assert gt.cantation_problem(5, 9, True) == "He knows that spell already."
    assert gt.cantation_cost(5) == 5


# -- the forms --


def test_the_gauntlet_form_records_a_failed_story_then_a_pass():
    saga = _saga()
    hugo = saga.character("a")
    form = gf.gauntlet_form(saga, hugo, Faces())
    assert isinstance(form, Form)
    values = {f.key: f.value for f in form.fields()}
    form.apply({**values, "verdict": gt.FAIL, "test": "steal the owl's egg"})
    assert hugo.diary[-1].name == gt.FAILED
    assert "steal the owl's egg" in hugo.diary[-1].details
    assert "vf_apprentice" in _ids(hugo)
    form.apply({**values, "method": gt.AUTOMATIC})
    assert hugo.diary[-1].name == gt.PASSED
    assert "vf_apprentice" not in _ids(hugo)
    assert isinstance(gf.gauntlet_form(saga, hugo), Refuse)


def test_passing_without_a_story_needs_the_years_served():
    saga = _saga()
    hugo = saga.character("a")
    hugo.background.year_born = YEAR - 20
    form = gf.gauntlet_form(saga, hugo)
    assert isinstance(form, Form) and form.validate is not None
    values = {f.key: f.value for f in form.fields()}
    assert "10 years served" in (
        form.validate({**values, "method": gt.AUTOMATIC}) or ""
    )
    rolled = {**values, "method": gt.ROLLED, "ability": "Magic Theory"}
    assert form.validate(rolled) is None
    assert "Intelligence + Magic Theory +5" in gf.gauntlet_lines(saga, hugo, rolled)[1]


def test_the_lose_the_gift_form_keeps_the_cause():
    saga = _saga()
    hugo = saga.character("a")
    form = gf.lose_gift_form(saga, hugo)
    assert isinstance(form, Form)
    values = {f.key: f.value for f in form.fields()}
    assert "Failed Apprentice" in gf.lose_lines(hugo, {**values, "how": gt.LOST})[0]
    form.apply({**values, "how": gt.LOST, "cause": "a nasty Turbulence"})
    assert hugo.diary[-1].name == "The Gift lost"
    assert isinstance(gf.lose_gift_form(saga, hugo), Refuse)


def test_learning_a_cantation_needs_the_option():
    saga = _saga()
    hugo = saga.character("a")
    assert isinstance(gf.cantation_form(saga, hugo), Refuse)
    saga = _saga(cantations=True)
    hugo = saga.character("a")
    form = gf.cantation_form(saga, hugo)
    assert isinstance(form, Form) and form.validate is not None
    values = {f.key: f.value for f in form.fields()}
    wanted = {**values, "spell_id": "spell_ager_belli", "times": 9}
    assert "at least 10" in (form.validate(wanted) or "")
    wanted["times"] = 10
    assert form.validate(wanted) is None
    assert "10 xp" in gf.cantation_lines(saga, hugo, wanted)[0]
    form.apply(wanted)
    assert [k.spell_id for k in hugo.spells_known] == ["spell_ager_belli"]
    assert all(s.id != "spell_ager_belli" for s in gf.cantation_spells(saga, hugo))
    # No level cap (Apprentices p. 46), but never a Ritual (DE p. 311).
    offered = gf.cantation_spells(saga, hugo)
    assert any((s.level or 0) > 10 for s in offered)
    assert not any(s.ritual for s in offered)


def test_the_commands_are_offered_to_an_apprentice():
    saga = _saga(cantations=True)
    page = menu_forms.page_for(saga, NodeKind.CHARACTER, character_id="a")
    labels = [i.label for i in menu_forms.placed(page, "Abilities")]
    assert {"Turbulence", "The Gauntlet", "Lose the Gift"} <= set(labels)
    assert "Learn a Cantation" in [
        i.label for i in menu_forms.placed(page, "Known Spells")
    ]
    saga.character("a").virtues_flaws = [VirtueFlawInstance("vf_the_gift")]
    assert not actions.available("gauntlet", page)
    # The optional rule is for adult magi too (p. 46).
    grown = menu_forms.page_for(saga, NodeKind.CHARACTER, character_id="a")
    assert "Learn a Cantation" in [
        i.label for i in menu_forms.placed(grown, "Known Spells")
    ]

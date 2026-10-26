"""Turbulence (Apprentices pp. 12, 22-24, 56, 59): incurring and
controlling one, its magnitude and Penetration, Turbulence Prone, the
Aegis, forcing one with Confidence, and a laboratory season's check, which
halves an apprentice's aid when uncontrolled."""

from __future__ import annotations

import random

from ars_magica_manager import actions, seasons
from ars_magica_manager.actions import NodeKind
from ars_magica_manager.commands import Form, Refuse
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.forms import turbulence as tf
from ars_magica_manager.models import (
    Ability,
    ArtScore,
    Character,
    Characteristics,
    Covenant,
    LabCharacteristics,
    Laboratory,
    Saga,
    SeasonPlan,
    Spell,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import lab_seasons
from ars_magica_manager.rules import laboratory_seasons as ls
from ars_magica_manager.rules import turbulence as tb
from ars_magica_manager.rules.breakdown import Line
from ars_magica_manager.rules.xp import ability_xp, art_xp

YEAR = 1220


class Faces(random.Random):
    """A d10 that shows the faces given, in order (0-9)."""

    def __init__(self, *faces: int) -> None:
        super().__init__(0)
        self.faces = list(faces)

    def randrange(self, *args, **kwargs):  # type: ignore[override]
        return self.faces.pop(0)


def _saga() -> Saga:
    covenant = Covenant(id="cov", saga_id="s", name="Keep", aura=2)
    magus = Character(id="m", name="Tiberius", type="magus", covenant_id="cov")
    magus.characteristics = Characteristics(intelligence=2)
    magus.abilities = [Ability("Magic Theory", xp=ability_xp(5))]
    magus.arts = {"creo": ArtScore(xp=art_xp(5)), "ignem": ArtScore(xp=art_xp(5))}
    child = Character(id="e", name="Eleanor", type="companion", covenant_id="cov")
    child.background.year_born = YEAR - 7
    child.characteristics = Characteristics(intelligence=3, stamina=3)
    child.abilities = [Ability("Magic Theory", xp=ability_xp(2))]
    child.virtues_flaws = [VirtueFlawInstance("vf_the_gift")]
    lab = Laboratory(
        id="lab",
        covenant_id="cov",
        name="Tower",
        owner_id="m",
        characteristics=LabCharacteristics(refinement=1),
    )
    saga = Saga(
        id="s",
        name="S",
        current_year=YEAR,
        covenants=[covenant],
        characters=[magus, child],
        laboratories=[lab],
    )
    saga.spells = [Spell("bolt", "Bolt", "Creo", "Ignem", level=10)]
    return saga


# -- the rules --


def test_the_books_example_incurs_and_fails_to_control():
    """Eleanor, 7, Int +3 and Sta +3 at -4 for age, in a Magic aura of 2
    (Apprentices p. 23): 9 - 1 + 2 = 10 beats 6 and 7; 3 against 9 fails,
    a third magnitude effect."""
    saga = _saga()
    eleanor = saga.character("e")
    lines = tb.incurring_lines(saga, eleanor, aura=2)
    assert [(line.label, line.amount) for line in lines] == [
        ("Intelligence", 3),
        ("Age (Aging Chart)", -4),
        ("Magic aura 2", 2),
    ]
    incurring = tb.incur(saga, eleanor, Faces(9, 6), lines)
    assert (incurring.total, incurring.storyguide, incurring.years) == (10, 6, 7)
    assert incurring.incurred
    control = tb.control(saga, eleanor, Faces(4, 9))
    assert (control.player_total, control.warping_total) == (3, 9)
    assert not control.controlled
    assert control.magnitude == 3
    said = tb.result_lines(eleanor, incurring, control)
    assert "uncontrolled: the storyguide chooses the effect" in said[1]
    assert "Magnitude 3 (level 15, half the difference rounded down" in said[2]
    assert said[-1].startswith("No Penetration")


def test_age_must_be_beaten_as_well_as_the_storyguide():
    saga = _saga()
    eleanor = saga.character("e")
    eleanor.background.year_born = YEAR - 12
    lines = tb.incurring_lines(saga, eleanor, aura=0)  # 3 - 1 for age 12
    short = tb.incur(saga, eleanor, Faces(8, 2), lines)
    assert (short.total, short.against) == (10, 12)
    assert not short.incurred
    # A 1 doubles the next face: 2 + 12 = 14 beats 2 and 12.
    beaten = tb.incur(saga, eleanor, Faces(1, 6, 2), lines)
    assert beaten.total == 14 and beaten.incurred


def test_another_realms_aura_and_an_aegis_take_from_the_roll():
    saga = _saga()
    eleanor = saga.character("e")
    lines = tb.incurring_lines(
        saga, eleanor, aura=3, aura_realm="Divine", aegis=15, confidence=1
    )
    assert [(line.label, line.amount) for line in lines][2:] == [
        ("Divine aura 3", -9),
        ("Aegis of the Hearth 15", -7),
        ("Confidence x 1", 3),
    ]


def test_turbulence_prone_cannot_control_a_botchs_turbulence():
    saga = _saga()
    eleanor = saga.character("e")
    eleanor.virtues_flaws.append(VirtueFlawInstance("vf_turbulence_prone"))
    assert tb.uncontrollable(eleanor, tb.PRONE)
    assert tb.uncontrollable(eleanor, tb.BOTCH)
    assert not tb.uncontrollable(eleanor, tb.FORCED)
    control = tb.control(saga, eleanor, Faces(9, 2), cannot_control=True)
    assert control.player_total > control.warping_total and not control.controlled
    assert control.magnitude == (8 - 2) // 2


def test_only_the_storyguides_incurring_die_cannot_botch():
    """Apprentices p. 22 makes only the storyguide's die no-botch: the
    player's incurring die and both control dice are ordinary stress
    dice (p. 23)."""
    saga = _saga()
    eleanor = saga.character("e")
    lines = tb.incurring_lines(saga, eleanor, aura=2)
    # The player's 0, then its botch die 0; the storyguide's 0 rolls none.
    incurring = tb.incur(saga, eleanor, Faces(0, 0, 0), lines)
    assert incurring.botched and incurring.die == 0 and incurring.storyguide == 0
    said = tb.result_lines(eleanor, incurring, None)
    assert "a botch (0)" in said[0] and "botched" in said[1]
    # Stamina's 0 and a botch die 0; Warping's 0 and a botch die 3.
    control = tb.control(saga, eleanor, Faces(0, 0, 0, 3))
    assert control.stamina_botched and not control.warping_botched
    said = tb.result_lines(eleanor, incurring, control)
    assert any("A control die botched (Stamina)" in line for line in said)


def test_penetration_needs_the_ability_and_a_sympathy_multiplies_it():
    saga = _saga()
    eleanor = saga.character("e")
    assert tb.penetration(eleanor) == 0
    eleanor.abilities.append(Ability("Penetration", xp=ability_xp(2)))
    assert tb.penetration(eleanor, 2) == 6


def test_an_affinity_or_puissant_art_is_suggested():
    eleanor = _saga().character("e")
    eleanor.virtues_flaws.append(
        VirtueFlawInstance("vf_affinity_with_art", {"art": "aquam"})
    )
    assert tb.suggested_arts(eleanor) == ["Aquam"]


def test_magnitude_levels():
    assert tb.magnitude_level(3) == "level 15"
    assert tb.magnitude_level(0) == "below level 5"


def test_losing_the_gift_by_the_dice():
    saga = _saga()
    assert tb.gift_botch_dice(21) == 3
    # The stress die shows 0, then three botch dice: 4, 0, 7.
    rolled = tb.gift_roll(saga, Faces(0, 4, 0, 7), 21)
    assert rolled.lost
    assert "loses his Gift" in tb.gift_roll_line(rolled)
    safe = tb.gift_roll(saga, Faces(5), 21)
    assert not safe.lost and "safe" in tb.gift_roll_line(safe)


# -- in the laboratory --


def _assisting(saga: Saga, *, experimenting: bool = False) -> SeasonPlan:
    seasons.set_plan(saga, SeasonPlan("e", YEAR, "Spring", ls.ASSIST, teacher_id="m"))
    seasons.set_plan(
        saga,
        SeasonPlan(
            "m",
            YEAR,
            "Spring",
            lab_seasons.INVENT,
            lab_id="lab",
            spell_id="bolt",
            experimenting=experimenting,
        ),
    )
    found = tb.assist_plan(saga, saga.character("e"))
    assert found is not None
    return found


def _lead_total(saga: Saga) -> int:
    lead, plan = tb.lead_plan(saga, tb.assist_plan(saga, saga.character("e")))  # type: ignore[arg-type,misc]
    _, work = lab_seasons.work(saga, lead, plan)
    assert work is not None
    return int(work.lab_total.total)


def test_an_uncontrolled_lab_turbulence_halves_the_apprentices_aid():
    saga = _saga()
    assisting = _assisting(saga)
    before = _lead_total(saga)
    assisting.turbulence = tb.CONTROLLED
    assert _lead_total(saga) == before
    assisting.turbulence = tb.UNCONTROLLED
    # Eleanor's aid is Int 3 + Magic Theory 2 = 5: halved to 2.
    assert _lead_total(saga) == before - 3


def test_halved_aid_lines_round_down_the_half_kept():
    saga = _saga()
    assisting = _assisting(saga)
    assisting.turbulence = tb.UNCONTROLLED
    lead = tb.lead_plan(saga, assisting)
    assert lead is not None
    lines = tb.halved_aid_lines(
        saga, saga.character("e"), lead[1], [Line("Eleanor (assistant)", amount=7)]
    )
    assert [line.amount for line in lines] == [-4]


def test_what_makes_a_lab_season_stressful():
    assert tb.stressful_reasons(True, 12) == [
        "the parens experiments",
        "12 pawns of vis, more than 10",
    ]
    assert tb.stressful_reasons(False, 10) == []


# -- the form --


def test_the_form_rolls_and_keeps_a_lab_seasons_check():
    saga = _saga()
    assisting = _assisting(saga)
    eleanor = saga.character("e")
    # Incur 9 vs 6 (10 > 6 and 7); control 4 vs 9: uncontrolled.
    form = tf.turbulence_form(saga, eleanor, Faces(9, 6, 4, 9, 5))
    assert isinstance(form, Form)
    values = {f.key: f.value for f in form.fields()}
    assert values["aura"] == 2
    assert tb.LAB in [value for _, value in tf.occasions(saga, eleanor)]
    lab = {**values, "occasion": tb.LAB, "gift_roll": True}
    said = tf.turbulence_lines(saga, eleanor, lab)
    assert said[0].startswith("Incurring: Intelligence +3, Age (Aging Chart) -4")
    assert any("Assisting Tiberius" in line for line in said)
    assert any("botch dice" in line for line in said)
    result = form.apply(lab)
    assert assisting.turbulence == tb.UNCONTROLLED
    assert any("aid to the Lab Total is halved" in line for line in result)
    assert eleanor.diary[-1].name == tf.TITLE
    # Checked once: the laboratory occasion isn't offered again.
    assert tb.LAB not in [value for _, value in tf.occasions(saga, eleanor)]


def test_forcing_spends_confidence_and_the_form_checks_it():
    saga = _saga()
    eleanor = saga.character("e")
    eleanor.background.confidence_score = 1
    eleanor.background.confidence_points = 1
    form = tf.turbulence_form(saga, eleanor, Faces(1, 0, 9, 3, 5))
    assert isinstance(form, Form) and form.validate is not None
    values = {f.key: f.value for f in form.fields()}
    forced = {**values, "occasion": tb.FORCED}
    assert form.validate(forced) is None
    assert "spends 2" in (form.validate({**forced, "confidence_incur": 1}) or "")
    assert "Confidence Score" in (
        form.validate({**forced, "confidence_incur": 2}) or ""
    )
    form.apply(forced)
    assert eleanor.background.confidence_points == 0


def test_only_the_gifted_have_turbulences():
    saga = _saga()
    plain = saga.character("e")
    plain.virtues_flaws = []
    assert isinstance(tf.turbulence_form(saga, plain), Refuse)


def test_turbulence_is_offered_on_a_gifted_characters_record():
    saga = _saga()
    page = menu_forms.page_for(saga, NodeKind.CHARACTER, character_id="e")
    assert actions.available("turbulence", page)
    assert "Turbulence" in [i.label for i in menu_forms.placed(page, "Abilities")]
    saga.books_in_play = ["DE"]
    assert not actions.available("turbulence", page)

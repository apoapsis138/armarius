"""The Mysteries Revised Edition's dream magic (pp. 102-113) and Hermetic
Sacrifice (p. 117, Errata p. 51): a spirit's magic in a dream, the
dreamer's rolls, dream wounds and disturbances, the Greater Dream
Grimoire's guidelines, the Dream parameters, and a sacrifice standing in
for a Ritual's vis; and More's two forms."""

import random
from dataclasses import replace

import pytest

from ars_magica_manager.actions import NodeKind, available
from ars_magica_manager.commands import Form, Refuse
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.forms import tmre_dreams as forms
from ars_magica_manager.models import (
    Ability,
    ArtScore,
    Character,
    Characteristics,
    KnownSpell,
    Possession,
    Saga,
    Spell,
    VirtueFlawInstance,
    Wounds,
)
from ars_magica_manager.rules import casting, casting_virtues, lab_seasons, spell_levels
from ars_magica_manager.rules import tmre_dreams as dr
from ars_magica_manager.rules.xp import ability_xp, art_xp


def _morphea(*vf_ids: str) -> Character:
    """Morphea (TMRE pp. 106-107): Stamina +2, Perdo 20, Imaginem 20,
    Parma Magica 3, a dream maga."""
    return Character(
        id="m",
        name="Morphea",
        type="magus",
        covenant_id="c",
        characteristics=Characteristics(stamina=2, perception=1, intelligence=2),
        arts={
            "perdo": ArtScore(xp=art_xp(20)),
            "imaginem": ArtScore(xp=art_xp(20)),
            "corpus": ArtScore(xp=art_xp(5)),
            "creo": ArtScore(xp=art_xp(10)),
        },
        abilities=[
            Ability("Parma Magica", xp=ability_xp(3)),
            Ability("Concentration", xp=ability_xp(2)),
            Ability("Awareness", xp=ability_xp(3)),
        ],
        virtues_flaws=[VirtueFlawInstance(v) for v in ("vf_dream_magic", *vf_ids)],
    )


# -- a spirit's magic -----------------------------------------------------------


def test_a_spirit_casts_every_form_with_imaginem():
    # The diabolist's Perdo Vim in the memory palace (p. 107): Stamina 2 +
    # Perdo 20 + Imaginem 20 + aura 2 = 44 before the die.
    score = dr.spirit_casting_score(_morphea(), "Perdo", "Vim", aura=2)
    assert score.total == 44
    assert "Imaginem (for Vim)" in [line.label for line in score.lines]


def test_the_body_left_behind_takes_nothing_from_the_spirit():
    morphea = _morphea()
    morphea.wounds = Wounds(medium=1)
    morphea.fatigue_level = "tired"
    morphea.inventory = [Possession(id="a", kind="armor", name="Chain", load=20)]
    body = casting.casting_score(morphea, "Perdo", "Imaginem", aura=2)
    assert {"Encumbrance", "Wounds", "Fatigue"} <= {line.label for line in body.lines}
    score = dr.spirit_casting_score(morphea, "Perdo", "Vim", aura=2)
    assert score.total == 44
    hurt = dr.spirit_casting_score(morphea, "Perdo", "Vim", aura=2, dream_wounds=-3)
    assert hurt.total == 41
    assert ("Dream wounds", -3) in [(line.label, line.amount) for line in hurt.lines]


def test_the_spirits_magic_resistance_is_imaginem_and_parma():
    # Imaginem 20 + 5 x Parma 3 + aura 2 = 37 (p. 107).
    assert dr.spirit_resistance(_morphea(), aura=2).total == 37
    # Parma stretched over body and spirit is 3 less: 20 + 2 = 22.
    assert dr.spirit_resistance(_morphea(), aura=2, split_parma=True).total == 22
    assert "Form scores" in dr.body_note(False)


# -- the dreamer ------------------------------------------------------------------


def test_the_dreamer_notices_and_reshapes():
    morphea = _morphea("vf_hermetic_dream_interpreter")
    assert dr.awareness_base(morphea).total == 1 + 3
    # Int 2 + magus 3 + Dream Magic 3 + Interpreter 3 + other powers at most 3.
    assert dr.reshape_base(morphea, other_powers=5).total == 2 + 3 + 3 + 3 + 3
    peasant = Character(id="p", name="Ivan", type="grog")
    peasant.characteristics = Characteristics(intelligence=1)
    assert dr.reshape_base(peasant).total == 1
    assert dr.reshape_base(peasant, magus=True).total == 4
    assert dr.reshape_magnitude(14) == 14


# -- wounds and disturbances ----------------------------------------------------------


def test_dream_wounds_ease_factors_follow_the_book():
    # Two Medium wounds: Ease Factor 3, then 6 (p. 106).
    morphea = _morphea("vf_strong_willed")
    first = dr.DreamWounds().add("medium")
    assert dr.shock_ease(morphea, first) == 3
    assert dr.shock_ease(morphea, first.add("medium")) == 6
    assert dr.shock_ease(morphea, first.add("incapacitating")) == dr.INCAPACITATING_EASE
    # Stamina 2 + Strong-Willed 3, with the earlier wound's -3 on the second.
    assert dr.shock_base(morphea, dr.DreamWounds()).total == 5
    assert dr.shock_base(morphea, first).total == 2
    assert dr.shock_base(morphea, first, modifiers=1).total == 3
    with pytest.raises(ValueError):
        first.add("bruise")


def test_enduring_constitution_eases_a_dream_wound():
    tough = _morphea("vf_enduring_constitution")
    # A Medium wound's -3 is -2 with Enduring Constitution; +3 for pain.
    assert dr.shock_ease(tough, dr.DreamWounds(medium=1)) == 2
    assert dr.shock_base(tough, dr.DreamWounds()).total == 2 + 3


def test_a_disturbed_body_rolls_concentration():
    morphea = _morphea()
    assert dr.disturbance_base(morphea) == 2 + 2
    assert dr.disturbance_ease("Knocked down") == 9
    assert dr.disturbance_ease("Shaken or jostled") == 6
    with pytest.raises(ValueError):
        dr.disturbance_ease("Tickled")


# -- guidelines and parameters --------------------------------------------------------


def test_substance_guidelines_by_size():
    assert dr.substance_level(-3) == 25  # The Oneiropomp's Treasure, Base 25
    assert dr.substance_level(-8) == 15
    assert dr.substance_level(1, enchantment_levels=10) == 45
    assert dr.substance_level(2) is None


def test_dream_duration_and_target_cost_as_the_book_says():
    # The Lucid Dreamer: Base 15, +1 Dream (p. 104) = 20.
    lucid = spell_levels.spell_level(15, "Personal", "Dream", "Dream")
    assert lucid is not None and lucid.level == 20
    # The Path to Lemnos: Base 20, +1 Touch, +1 Dream = 30.
    path = spell_levels.spell_level(20, "Touch", "Dream", "Dream")
    assert path is not None and path.level == 30
    assert spell_levels.virtue_needed(set(), "Personal", "Dream", "Dream")
    assert not spell_levels.virtue_needed(
        {"vf_dream_magic"}, "Personal", "Dream", "Dream"
    )


def test_dream_target_needs_mentem_as_form_or_requisite():
    # "Dream only applies to Mentem spells" (p. 104); the p. 109 Rego
    # Corpus and Rego Terram spells carry Mentem as a requisite.
    assert dr.dream_target_problem("Muto", "Mentem") == ""
    assert dr.dream_target_problem("Rego", "Corpus", ["Muto", "Mentem"]) == ""
    assert "Mentem" in dr.dream_target_problem("Rego", "Corpus")
    assert "Mentem" in dr.dream_target_problem("Creo", "Ignem")
    ignem = spell_levels.spell_level(
        5, "Touch", "Momentary", "Dream", technique="Creo", form="Ignem"
    )
    assert ignem is not None and any("Dream Target" in n for n in ignem.notes)
    gate = spell_levels.spell_level(
        35,
        "Touch",
        "Momentary",
        "Dream",
        technique="Rego",
        form="Corpus",
        requisites=["Muto", "Mentem"],
    )
    assert gate is not None and gate.level == 40 and not gate.notes
    bare = spell_levels.spell_level(
        35, "Touch", "Momentary", "Dream", technique="Rego", form="Corpus"
    )
    assert bare is not None and any("Dream Target" in n for n in bare.notes)


def test_a_dream_target_spell_without_mentem_is_refused():
    magus = _morphea("vf_dream_magic")
    gate = Spell(
        "s_gate",
        "The Morphean Gate",
        "Rego",
        "Corpus",
        40,
        requisites=["Muto", "Mentem"],
        range="Touch",
        duration="Momentary",
        target="Dream",
    )
    assert lab_seasons._mystery_needed(magus, gate) == ""
    bare = replace(gate, requisites=["Muto"])
    assert "Mentem" in lab_seasons._mystery_needed(magus, bare)


# -- Hermetic Sacrifice -----------------------------------------------------------------


def test_a_sacrifice_stands_in_for_a_rituals_vis():
    magus = _morphea("vf_hermetic_sacrifice")
    vis = dr.ritual_vis_breakdown(magus, 30, (1,))
    assert vis is not None and vis.total == 5
    assert ("Sacrifice", -1) in [(line.label, line.amount) for line in vis.lines]
    # A lion's six never takes it below nothing.
    lion = dr.ritual_vis_breakdown(magus, 20, (6,))
    assert lion is not None and lion.total == 0
    assert ("Sacrifice", -4) in [(line.label, line.amount) for line in lion.lines]


def test_mercurian_magic_halves_before_the_sacrifice():
    magus = _morphea("vf_hermetic_sacrifice", "vf_mercurian_magic")
    vis = dr.ritual_vis_breakdown(magus, 40, (2,))
    # 8 pawns, halved to 4, less 2.
    assert vis is not None and vis.total == 2
    rigid = _morphea("vf_rigid_magic")
    assert dr.ritual_vis_breakdown(rigid, 20) is None


def test_what_spoils_a_sacrifice():
    magus = _morphea("vf_hermetic_sacrifice")
    assert dr.sacrifice_problem(magus, 3, pure=True, made_by_magic=False) == ""
    assert "pure" in dr.sacrifice_problem(magus, 3, pure=False, made_by_magic=False)
    assert "never" in dr.sacrifice_problem(magus, 3, pure=True, made_by_magic=True)
    assert "1 to 6" in dr.sacrifice_problem(magus, 7, pure=True, made_by_magic=False)
    assert "doesn't know" in dr.sacrifice_problem(
        _morphea(), 1, pure=True, made_by_magic=False
    )


def test_the_casting_reminders_name_both_mysteries():
    found = casting_virtues.reminders(_morphea("vf_hermetic_sacrifice"))
    assert any(r.startswith("Dream Magic:") for r in found)
    assert any(r.startswith("Hermetic Sacrifice:") for r in found)


# -- the forms -----------------------------------------------------------------------------


def _saga(*characters: Character) -> Saga:
    return Saga(id="s", name="S", characters=list(characters))


def test_the_dream_working_form_casts_and_rolls():
    morphea = _morphea()
    saga = _saga(morphea)
    form = forms.dream_form(saga, morphea)
    assert isinstance(form, Form) and form.live and form.validate
    values = {
        "roll": forms.SPELL,
        "spell": forms.SPONTANEOUS,
        "technique": "Creo",
        "form": "Ignem",
        "aura": 0,
    }
    live = form.live(values)
    assert "Casting Score [b]32[/]" in live and "Imaginem (for Ignem)" in live
    assert "Magic Resistance in the dream [b]35[/]" in live
    lines = form.apply({**values, "die": 8})
    assert "Casting Total 20 (no Fatigue lost in a dream)." in lines
    assert morphea.diary[-1].name.startswith("Dream: a Spontaneous Creo Ignem")
    assert form.validate({**values, "aura": 11})
    assert form.validate({**values, "dream_wounds": 2})


def test_the_dream_working_form_casts_a_known_spell():
    morphea = _morphea()
    spell = Spell("sp1", "Dream Fire", "Creo", "Ignem", level=20)
    saga = _saga(morphea)
    saga.spells = [spell]
    morphea.spells_known = [KnownSpell("sp1", mastery_score=1)]
    form = forms.dream_form(saga, morphea)
    assert isinstance(form, Form) and form.live
    values = {"roll": forms.SPELL, "spell": "sp1"}
    assert "against level [b]20[/]" in form.live(values)
    # Creo 10 + Imaginem 20 + Stamina 2 + Mastery 1 = 33.
    assert "Casting Total 33: cast." in form.apply({**values, "die": 0})


def test_the_dream_working_form_for_the_dreamer_and_wounds():
    morphea = _morphea("vf_strong_willed")
    ivan = Character(id="p", name="Ivan", type="grog")
    ivan.characteristics = Characteristics(perception=2, intelligence=1)
    saga = _saga(morphea, ivan)
    form = forms.dream_form(saga, morphea)
    assert isinstance(form, Form) and form.live and form.validate
    aware = {"roll": forms.AWARE, "dreamer": "p"}
    assert "against [b]9[/]" in form.live(aware)
    assert "Ivan notices the travelers" in form.apply({**aware, "die": 7})[1]
    reshape = {"roll": forms.RESHAPE, "dreamer": "p", "magus_power": False}
    said = form.apply({**reshape, "die": 9})[1]
    assert "10 against 9" in said and "magnitude: 10" in said
    wound = {"roll": forms.WOUND, "wound": "medium", "earlier_medium": 1}
    assert "against [b]6[/]" in form.live(wound)
    assert "stays in the dream" in form.apply({**wound, "die": 4})[1]
    assert "wakes him" in form.apply({**wound, "die": 3})[1]
    shaken = {"roll": forms.DISTURBED, "disturbance": "Knocked down"}
    assert "he wakes" in form.apply({**shaken, "die": 4})[1]
    assert form.validate({**wound, "earlier_light": -1})


def test_the_dreamer_is_chosen_and_a_magus_dreamer_counts_his_power():
    # The rolls are the dreamer's (TMRE p. 105): the form names nobody to
    # start with, and the magus's +3 follows the dreamer, not the traveler.
    morphea = _morphea()
    ivan = Character(id="p", name="Ivan", type="grog")
    ivan.characteristics = Characteristics(intelligence=1)
    saga = _saga(morphea, ivan)
    fields = {f.key: f for f in forms.dream_fields(saga, morphea)}
    assert fields["dreamer"].value is None and fields["magus_power"].value is False
    form = forms.dream_form(saga, morphea)
    assert isinstance(form, Form)
    grog = form.apply({"roll": forms.RESHAPE, "dreamer": "p", "die": 5})[1]
    own = form.apply({"roll": forms.RESHAPE, "dreamer": morphea.id, "die": 5})[1]
    assert "6 against 9" in grog
    assert "against 9" in own and "6 against 9" not in own


def test_the_dream_working_form_rolls_its_own_die():
    morphea = _morphea()
    saga = _saga(morphea)
    form = forms.dream_form(saga, morphea, random.Random(3))
    assert isinstance(form, Form)
    lines = form.apply({"roll": forms.AWARE})
    assert "Die" in lines[0]


def test_the_sacrifice_form():
    magus = _morphea("vf_hermetic_sacrifice")
    rite = Spell("r1", "Summon Mercury", "Rego", "Vim", level=30, ritual=True)
    saga = _saga(magus)
    saga.spells = [rite]
    magus.spells_known = [KnownSpell("r1")]
    form = forms.sacrifice_form(saga, magus)
    assert isinstance(form, Form) and form.live and form.validate
    values = {
        "spell": "r1",
        "deity": "Mercury",
        "beast": "a white ram",
        "worth": 2,
        "pure": True,
        "made_by_magic": False,
    }
    assert form.validate(values) is None
    assert "still needs: [b]4[/]" in form.live(values)
    assert form.validate({**values, "deity": ""})
    assert form.validate({**values, "pure": False})
    typed = {**values, "spell": forms.TYPED_LEVEL, "level": None}
    assert form.validate(typed)
    assert "still needs: [b]8[/]" in form.live({**typed, "level": 50})
    # The rest is paid from the magus's own vis, of the Ritual's Technique.
    assert "needs 4 pawn(s) of Rego; there are 0" in form.validate(
        {**values, "pay_from": "character"}
    )
    magus.raw_vis = {"rego": 5}
    lines = form.apply({**values, "pay_from": "character"})
    assert "The level 30 Ritual still needs 4 pawn(s) of vis." in lines
    assert "4 pawn(s) of Rego paid from their own raw vis." in lines
    assert magus.raw_vis == {"rego": 1}
    assert magus.diary[-1].name == "Sacrifice to Mercury"
    assert isinstance(forms.sacrifice_form(saga, _morphea()), Refuse)


def test_more_offers_the_dream_forms_only_to_their_initiates():
    magus = _morphea("vf_hermetic_sacrifice")
    saga = _saga(magus)
    assert isinstance(forms.dream_form(saga, magus), Form)
    page = menu_forms.page_for(saga, NodeKind.CHARACTER, character_id="m")
    spells = replace(page, section="section-known-spells")
    assert available("dream_working", spells)
    assert available("hermetic_sacrifice", spells)
    assert {"dream_working", "hermetic_sacrifice"} <= {
        i.action for i in menu_forms.placed(page, "Magic Outside the Lab")
    }
    magus.virtues_flaws = []
    assert not available("dream_working", spells)
    assert not available("hermetic_sacrifice", spells)
    assert isinstance(forms.dream_form(saga, magus), Refuse)

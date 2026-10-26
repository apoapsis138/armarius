"""Art & Academe's complexion (pp. 40-41), its lasting consequences of
serious damage (p. 43) and Dies Irae's Great Pestilence (pp. 86-98), all
under the Art & Academe medicine option."""

import random

from ars_magica_manager import health
from ars_magica_manager.forms import character as character_forms
from ars_magica_manager.models import (
    Ability,
    ArtScore,
    Character,
    Characteristics,
    Covenant,
    Description,
    Disease,
    Saga,
)
from ars_magica_manager.rules import complexion, disease, harm, serious_damage
from ars_magica_manager.rules.xp import ability_xp, art_xp
from ars_magica_manager.sheets import character as sheet


class Dice(random.Random):
    """A d10 that shows the faces given, in turn (0-9)."""

    def __init__(self, *faces: int) -> None:
        super().__init__(0)
        self.faces = list(faces)

    def randrange(self, *args, **kwargs) -> int:  # type: ignore[override]
        return self.faces.pop(0)


def _saga(*characters: Character, on: bool = True) -> Saga:
    saga = Saga(
        id="s",
        name="S",
        characters=list(characters),
        covenants=[Covenant(id="cov", saga_id="s", name="C")],
    )
    saga.books_in_play = ["A&A"]
    saga.rule_options = {disease.OPTION: True} if on else {}
    return saga


def _person(stamina: int = 0, kind: str = "companion", **kw) -> Character:
    return Character(
        id="p",
        name="Pia",
        type=kind,
        covenant_id="cov",
        characteristics=Characteristics(stamina=stamina),
        **kw,
    )


# -- complexion --


def test_four_simple_and_eight_compound_complexions():
    assert len(complexion.CHOICES) == 12
    assert complexion.mixes("sanguine", "melancholic")
    # The active quality never features twice (A&A p. 40).
    assert not complexion.mixes("sanguine", "choleric")
    assert not complexion.mixes("melancholic", "phlegmatic")
    assert complexion.label("choleric-phlegmatic") == "Choleric, then phlegmatic"
    assert complexion.parts("sanguine-choleric") == ()


def test_a_minor_aspect_is_a_third_complexion_of_a_compound_one():
    assert complexion.problem("sanguine-melancholic", "phlegmatic") is None
    assert complexion.problem("sanguine-melancholic", "sanguine")
    assert complexion.problem("sanguine", "melancholic")
    assert complexion.problem("", "") is None


def test_the_principal_humour_sets_the_season_and_the_diet():
    phlegmatic = Description(complexion="phlegmatic-sanguine")
    assert complexion.waxes(phlegmatic, "Winter")
    assert not complexion.waxes(phlegmatic, "Spring")
    # The phlegmatic man eats venison, leeks, garlic and wine (A&A p. 41).
    assert "heating and drying" in complexion.diet(phlegmatic)
    line = complexion.text(phlegmatic, "Winter")
    assert "cold and moist" in line and "Winter (now)" in line
    assert complexion.text(Description()) == ""


def test_the_biographical_form_asks_for_complexion_with_the_option():
    c = _person()
    labels = [
        f.key for f in character_forms.biographical_fields(c.background, c.description)
    ]
    assert "complexion" not in labels
    fields = character_forms.biographical_fields(
        c.background, c.description, academe=True
    )
    assert {"complexion", "complexion_minor"} <= {f.key for f in fields}
    # Once recorded it stays on the form whatever the option.
    c.description.complexion = "choleric"
    assert "complexion" in [
        f.key for f in character_forms.biographical_fields(c.background, c.description)
    ]


def test_saving_the_form_keeps_or_clears_the_complexion():
    c = _person()
    c.description = Description(complexion="sanguine-melancholic")
    character_forms.apply_biographical(c, {"hair": "Red"})
    assert c.description.complexion == "sanguine-melancholic"  # not on the form
    assert c.description.hair == "Red"
    character_forms.apply_biographical(
        c, {"complexion": "choleric", "complexion_minor": "phlegmatic"}
    )
    assert (c.description.complexion, c.description.complexion_minor) == (
        "choleric",
        "",
    )  # a simple complexion has no touch of a third
    assert character_forms.biographical_problem(
        {"complexion": "choleric", "complexion_minor": "phlegmatic"}
    )


def test_the_sheet_shows_a_recorded_complexion():
    c = _person()
    saga = _saga(c)
    assert "Complexion" not in sheet.biographical_left_text(saga, c)
    c.description.complexion = "melancholic-sanguine"
    assert "Complexion: Melancholic, then sanguine" in sheet.biographical_left_text(
        saga, c
    )
    assert ("Complexion", "Melancholic, then sanguine") in [
        (f.label, f.value) for f in sheet.biographical_facts(saga, c)
    ]


def test_a_disease_of_ones_own_humour_is_ill_suited_to_the_temperament():
    patient = _person(stamina=-5)
    patient.description.complexion = "phlegmatic"
    saga = _saga(patient)
    done = harm.apply(saga, patient, harm.DISEASE, {"aa_disease": "Coryza"}, Dice(3, 3))
    assert any("ill-suited to the temperament" in line for line in done.lines)
    other = _person(stamina=-5)
    other.description.complexion = "choleric"
    done = harm.apply(
        _saga(other), other, harm.DISEASE, {"aa_disease": "Coryza"}, Dice(3)
    )
    assert not any("ill-suited" in line for line in done.lines)


def test_every_book_disease_has_its_humours():
    found = {d.name: d.humours for d in disease.CATALOG}
    assert found["The Ague"] == ("phlegmatic",)
    assert found["Stones"] == ("choleric", "phlegmatic")
    assert all(
        found[d.name] for d in disease.CATALOG if d.name != disease.SAP_THE_LIFE.name
    )


# -- lasting consequences of serious damage --


def test_a_failed_stamina_roll_leaves_a_minor_flaw_fitting_the_place():
    c = _person(stamina=1)
    saga = _saga(c)
    failed = serious_damage.roll(saga, c, "limbs", Dice(4))  # 1 + 4 = 5 < 6
    assert "lasting complication" in failed[0] and "Lame" in failed[0]
    held = serious_damage.roll(saga, c, "head", Dice(5))  # 1 + 5 = 6
    assert "no lasting complication" in held[0]
    botched = serious_damage.roll(saga, c, "head", Dice(0, 0))
    assert "botched" in botched[0] and "Missing Eye" in botched[0]
    assert serious_damage.roll(_saga(c, on=False), c, "head", Dice(4)) == []


def test_an_injury_dealing_an_incapacitating_wound_rolls_for_it(monkeypatch):
    c = _person()
    monkeypatch.setattr(harm, "damage", lambda *a, **k: (30, 5, "incapacitating"))
    done = harm.apply(_saga(c), c, harm.INJURY, {"location": "head"}, Dice(2))
    assert c.wounds.incapacitated
    assert "Missing Ear" in done.lines[-1]
    monkeypatch.setattr(harm, "damage", lambda *a, **k: (30, 5, "heavy"))
    done = harm.apply(_saga(c), c, harm.INJURY, {}, Dice(2))
    assert not any("lasting" in line for line in done.lines)


def test_take_harm_asks_where_the_injury_struck_with_the_option():
    keys = [f.key for f in health.harm_fields(_saga())]
    assert "location" in keys
    assert "location" not in [f.key for f in health.harm_fields(_saga(on=False))]


# -- the Great Pestilence's miasmas --


def test_the_great_pestilence_is_a_critical_phlegmatic_disease_rolled_daily():
    found = disease.CATALOG_BY_NAME["The Great (Form) Pestilence"]
    assert (found.level, found.severity, found.stable, found.improve) == (
        "Critical",
        21,
        12,
        18,
    )
    # Its Severity: Critical 15 + Stable 12 (+3) + Improve 18 (+3), Day +0.
    assert disease.severity_of("Critical", disease.DAY, 12, 18) == 21
    record = disease.from_def(found)
    record.level = "Major"
    assert "rolls daily" in disease.describe(record)


def test_a_corpus_miasma_infects_without_a_roll_but_not_through_parma():
    grog = _person(stamina=3)
    done = harm.apply(
        _saga(grog),
        grog,
        harm.DISEASE,
        {"aa_disease": disease.CORPUS_PESTILENCE.name},
        Dice(9),
    )
    assert [d.level for d in grog.wounds.diseases] == ["Critical"]
    assert "no Disease Avoidance" in done.lines[0]
    magus = _person(kind="magus")
    magus.abilities.append(Ability("Parma Magica", xp=ability_xp(1)))
    magus.arts["Corpus"] = ArtScore(xp=art_xp(0))
    done = harm.apply(
        _saga(magus),
        magus,
        harm.DISEASE,
        {"aa_disease": disease.CORPUS_PESTILENCE.name},
        Dice(9),
    )
    assert magus.wounds.diseases == []
    assert "Magic Resistance stops" in done.lines[0]
    # Not magi alone: all others with Magic Resistance are immune too
    # (Dies Irae p. 94), here a grog's True Faith (DE p. 419).
    faithful = _person()
    faithful.background.true_faith_score = 1
    done = harm.apply(
        _saga(faithful),
        faithful,
        harm.DISEASE,
        {"aa_disease": disease.CORPUS_PESTILENCE.name},
        Dice(9),
    )
    assert faithful.wounds.diseases == []
    assert "Magic Resistance stops" in done.lines[0]


def test_a_daily_disease_rolls_seven_times_a_week(monkeypatch):
    patient = _person(stamina=0)
    record = disease.from_def(disease.FORM_PESTILENCE)
    record.level = "Major"
    patient.wounds.diseases = [record]
    rolled: list[Disease] = []

    def counting(saga, character, d, living, rng):
        rolled.append(d)
        return "held"

    monkeypatch.setattr(disease, "roll", counting)
    disease.season(_saga(patient), patient, 0, Dice())
    assert len(rolled) == disease.WEEKS * disease.DAYS_A_WEEK

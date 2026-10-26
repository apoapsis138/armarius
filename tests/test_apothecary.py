"""Art & Academe's apothecary and experimental philosophy: the store's
Labor Points and drains, preserving and searching (pp. 63-66), formulae
researched and concocted (pp. 69-78), ligatures (pp. 68-69)."""

import random
from dataclasses import asdict, replace

import pytest

from ars_magica_manager import seasons
from ars_magica_manager.actions import NodeKind, available
from ars_magica_manager.commands import Form, Refuse
from ars_magica_manager.forms import apothecary as forms
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.forms import season as season_forms
from ars_magica_manager.models import (
    Ability,
    Character,
    Characteristics,
    Formula,
    Saga,
    SeasonPlan,
    XpAllocation,
)
from ars_magica_manager.rules import apothecary as ap
from ars_magica_manager.rules import philosophy as ph
from ars_magica_manager.rules import supplement_work as sw
from ars_magica_manager.rules.xp import ability_xp
from ars_magica_manager.seasons.lab_apply import year_end_business


def _martin(**abilities: int) -> Character:
    """Martin the Alchemist (A&A p. 71): Intelligence +2, Philosophiae 5
    in Reagents."""
    martin = Character(id="m", name="Martin", type="companion", covenant_id="cov")
    martin.characteristics = Characteristics(intelligence=2, perception=1, dexterity=1)
    martin.abilities = [
        Ability("Philosophiae", xp=ability_xp(5), specialty="Reagents"),
        *(Ability(name, xp=ability_xp(score)) for name, score in abilities.items()),
    ]
    return martin


def _saga(*characters: Character) -> Saga:
    return Saga(id="s", name="S", characters=list(characters))


def _plan(activity: str, subject: str = "ability:Philosophiae", **kw) -> SeasonPlan:
    return SeasonPlan("m", 1220, "Spring", activity, [XpAllocation(subject)], **kw)


def _run(saga: Saga, plan: SeasonPlan) -> Character:
    seasons.set_plan(saga, plan)
    seasons.apply(saga, seasons.resolve(saga, random.Random(1)))
    found = saga.character(plan.character_id)
    assert found is not None
    return found


# -- formulae ------------------------------------------------------------------


@pytest.mark.parametrize(
    ("base", "magnitudes", "level"),
    [
        (3, 1, 4),  # Chromatic Flames
        (2, 3, 5),  # tomorrow's weather: Basic, the near future
        (5, 1, 10),  # Will N wage war?
        (4, 3, 15),  # Greek Fire
        (3, 4, 15),  # Soporific Sponge
        (10, 2, 20),  # Ointment for Congealing Blood
    ],
)
def test_a_formulas_level_rises_as_a_spells(base, magnitudes, level):
    assert ph.formula_level(base, magnitudes) == level


def test_the_parameters_magnitudes():
    assert ph.parameter_magnitudes(ph.THERIAC, "Mighty") == 4
    assert ph.parameter_magnitudes(ph.REAGENT, "Substantial") == 2
    assert ph.parameter_magnitudes(ph.INCEPTION, "Thorough") == 3


def test_martins_lab_total():
    total = ph.lab_total(_martin(), ph.REAGENT, 4)
    # Int 2 + Philosophiae 5 + 1 for Reagents + 4: 12, as the book's example.
    assert total.total == 12
    assert "Philosophic Bonuses +4" in total.line()
    capped = ph.lab_total(_martin(), ph.REAGENT, 9)
    assert (capped.counted, capped.total) == (5, 13)
    assert "of 9: no more than the Ability" in capped.line()
    # No specialty in theriacs, no Medicine.
    assert ph.lab_total(_martin(), ph.THERIAC, 3).total == 2


def test_concocting_martins_cement_and_berengers():
    # Martin: 12 against level 5, done in a season; three doses with the text.
    assert ph.concoction(12, 5, lab_text=False).points == 7
    assert ph.concoction(12, 5, lab_text=True).doses == 3
    # Berenger: Lab Total 8, two doses with the text, two seasons without.
    assert ph.concoction(8, 5, lab_text=True).doses == 2
    assert ph.concoction(8, 5, lab_text=False).points == 3
    assert ph.seasons_to_concoct(8, 5) == 2
    assert "earns no points" in ph.concoction(5, 5, lab_text=False).problem
    assert ph.concoction(5, 5, lab_text=True).doses == 1
    assert "doesn't reach" in ph.concoction(4, 5, lab_text=True).problem
    assert ph.seasons_to_concoct(5, 5) is None


def test_ingredients_cost_the_level_times_the_doses_over_five():
    assert ph.labor_cost(ph.REAGENT, 5, 3) == 3
    assert ph.labor_cost(ph.THERIAC, 12, 3) == 8  # 7.2, rounded up
    assert ph.labor_cost(ph.INCEPTION, 15, 4) == 0


def test_poisons_without_a_formula():
    assert not ph.poison_needs_formula("Light", 6)
    assert ph.poison_needs_formula("Light", 9)
    assert ph.poison_needs_formula("Medium", 3)
    assert ph.POISON_EASE[10] == 12 and ph.POTENCY_WOUND["Strong"] == "Heavy"


def test_a_formula_from_a_save_is_checked():
    with pytest.raises(ValueError, match="unknown kind"):
        Formula.from_dict({"name": "X", "kind": "potion"})
    with pytest.raises(ValueError, match="whole number"):
        Formula.from_dict({"name": "X", "kind": "reagent", "level": -1})
    martin = _martin()
    martin.formula_designs = [Formula("Cement", "reagent", 5, lab_text=True)]
    again = Character.from_dict(asdict(martin))
    assert again.formula_designs == martin.formula_designs
    old = asdict(martin)
    del old["formula_designs"]
    assert Character.from_dict(old).formula_designs == []


# -- the seasons ---------------------------------------------------------------


def test_researching_a_formula_puts_the_xp_into_it_and_records_its_design():
    saga = _saga(_martin())
    before = saga.characters[0].abilities[0].xp
    martin = _run(saga, _plan("research_formula", title="Cement", book_level=5))
    assert martin.formulas == ["Cement"]
    assert martin.formula_designs == [Formula("Cement", "reagent", 5)]
    # The 5 xp went into the formula, not Philosophiae (A&A p. 70).
    assert martin.abilities[0].xp == before


def test_a_formula_is_researched_in_its_academic_ability():
    saga = _saga(_martin(**{"Craft: Smith": 3}))
    plan = _plan("research_formula", "ability:Craft: Smith", title="Cement")
    assert (
        "Artes Liberales (an inception)"
        in sw.problems(saga, saga.characters[0], plan)[0]
    )
    assert sw.problems(saga, saga.characters[0], _plan("research_formula")) == [
        "Name it (the pilgrimage, the animal, the work, the formula)."
    ]


def test_concocting_cement_then_making_doses_from_the_text():
    martin = _martin(**{"Profession: Apothecary": 2})
    martin.formulas = ["Cement"]
    martin.formula_designs = [Formula("Cement", "reagent", 5)]
    martin.labor_points = 10
    saga = _saga(martin)
    concoct = _plan("produce_remedies", title="Cement", other_modifier=4)
    work = sw.work(saga, martin, concoct, None)
    assert work.notes[0].startswith("Lab Total: Intelligence +2 + Philosophiae 5")
    martin = _run(saga, concoct)
    assert martin.formula_designs[0].lab_text
    assert [(p.name, p.quantity) for p in martin.inventory] == [("Cement (reagent)", 1)]
    assert martin.labor_points == 9  # level 5 x 1 dose / 5
    assert any(e.name == "Finished: Cement" for e in martin.diary)
    again = _run(saga, concoct)
    assert [(p.name, p.quantity) for p in again.inventory] == [("Cement (reagent)", 4)]
    assert again.labor_points == 6  # 5 x 3 / 5
    fewer = sw.work(saga, again, replace(concoct, extra_vis=2), None)
    assert fewer.products == [("Cement (reagent)", 2)]


def test_a_first_concoction_over_several_seasons():
    martin = _martin()
    martin.formulas = ["Greek Fire"]
    martin.formula_designs = [Formula("Greek Fire", "reagent", 15)]
    saga = _saga(martin)
    # Lab Total 2 + 5 + 1 + 5 (capped) = 13: short of 15.
    plan = _plan("produce_remedies", title="Greek Fire", other_modifier=9)
    assert "doesn't reach the formula's level 15" in sw.problems(saga, martin, plan)[0]
    martin.formula_designs[0].level = 10
    work = sw.work(saga, martin, plan, None)
    assert work.progress == [("concoction", "Greek Fire", 10, 3)]
    assert not work.lab_texts and not work.products
    # No store of his own: the ingredients come from an apothecary's.
    assert work.labor_points == 0


def test_concocting_needs_the_formula_learned():
    martin = _martin()
    martin.formula_designs = [Formula("Cement", "reagent", 5)]
    saga = _saga(martin)
    plan = _plan("produce_remedies", title="Cement")
    assert "hasn't learned the formula Cement" in sw.problems(saga, martin, plan)[0]
    blank = _plan("produce_remedies")
    assert sw.problems(saga, martin, blank) == [
        "Choose the formula, or type the product's level."
    ]


def test_an_inception_costs_no_ingredients():
    francis = _martin(**{"Artes Liberales": 6, "Profession: Apothecary": 1})
    francis.formulas = ["Is N in good health?"]
    francis.formula_designs = [Formula("Is N in good health?", "inception", 3)]
    francis.formula_designs[0].lab_text = True
    work = sw.work(
        _saga(francis),
        francis,
        _plan(
            "produce_remedies", "ability:Artes Liberales", title="Is N in good health?"
        ),
        None,
    )
    assert work.products == [("Is N in good health? (inception)", 2)]  # 8 / 5
    assert work.labor_points == 0


# -- the store -----------------------------------------------------------------


def _physician_and_apothecary() -> Saga:
    physician = Character(id="p", name="Galen", type="companion", covenant_id="cov")
    physician.abilities = [Ability("Medicine", xp=ability_xp(4))]
    client = Character(id="k", name="Hugh", type="companion", covenant_id="cov")
    client.aging.regimen, client.aging.regimen_by = 1, "p"
    apothecary = _martin(**{"Profession: Apothecary": 3})
    return _saga(physician, client, apothecary)


def test_the_store_supplies_a_physicians_regimens():
    saga = _physician_and_apothecary()
    apothecary = saga.character("m")
    assert apothecary is not None
    assert [c.name for c in ap.physicians_supplied(saga, apothecary)] == ["Galen"]
    assert ap.regimen_drain(saga, apothecary) == 3
    lines = year_end_business(saga)
    assert apothecary.labor_points == -39  # 36 + 3 for the regimen
    assert any(line.name == "Martin" for line in lines)
    assert "regimens supplied -3" in apothecary.diary[-1].details


def test_a_physician_with_his_own_store_supplies_himself():
    saga = _physician_and_apothecary()
    physician = saga.character("p")
    assert physician is not None
    physician.abilities.append(Ability("Profession: Apothecary", xp=ability_xp(1)))
    assert ap.supplier(saga, physician) is physician


def test_preserving_and_searching():
    assert ap.kept_for(14) == "Years"
    assert ap.kept_for(2) == ""
    search = ap.Search(area_lore=2, assistants=1, terrain=ap.BARREN, winter=True)
    assert search.ease() == 11
    assert replace(search, spell=True).ease() == 8
    # Made by four: five points in a month (A&A p. 66).
    assert ap.found_points(13, 9) == 5
    assert ap.found_points(8, 9) == 0


# -- the forms -----------------------------------------------------------------


def test_the_ligature_form():
    scholar = _martin(**{"Medicine": 3, "Profession: Apothecary": 1})
    saga = _saga(scholar)
    form = forms.ligature_form(saga, scholar)
    assert isinstance(form, Form) and form.live and form.validate
    values = {"ability": "Medicine", "purpose": "Hugh's surgery", "own_store": True}
    assert form.validate({**values, "purpose": ""})
    assert "a stress die + [b]5[/]" in form.live(values)
    # Int 2 + Medicine 3 + 10 = 15: +2.
    lines = form.apply({**values, "die": 10})
    assert "15: +2 to the roll it was made for." in lines
    assert scholar.labor_points == -1
    assert scholar.diary[-1].name == "Ligature: Hugh's surgery"
    botch = form.apply({**values, "die": 0, "botched": True, "own_store": False})
    assert any("Botched, unknown to him" in line for line in botch)
    assert scholar.labor_points == -1
    assert "below 9" in form.apply({**values, "die": 1, "own_store": False})[1]
    nobody = Character(id="n", name="Nobody", type="companion")
    assert isinstance(forms.ligature_form(saga, nobody), Refuse)


def test_the_store_form():
    apothecary = _martin(**{"Profession: Apothecary": 3, "Leadership": 1})
    saga = _saga(apothecary)
    form = forms.store_form(saga, apothecary)
    assert isinstance(form, Form) and form.live and form.validate
    search = {"roll": forms.SEARCH, "ingredient": "henbane", "assistants": 2}
    assert "at most 1 assistants" in str(form.validate(search))
    search["assistants"] = 1
    assert form.validate(search) is None
    # Per 1 + Profession 3 = 4, against 9 - 1 = 8.
    assert "against [b]8[/]" in form.live(search)
    found = form.apply({**search, "die": 7})
    assert "11 against 8: 4 Labor Point(s)' worth" in found[1]
    assert apothecary.diary[-1].name == "Searched for: henbane"
    preserve = {"roll": forms.PRESERVE, "ingredient": "a dragon's scale"}
    preserve["duration"] = "Decades"
    assert form.validate({**preserve, "simple_die": 11})
    # Dex 1 + Profession 3 + 10 = 14 against 15: keeps years.
    kept = form.apply({**preserve, "simple_die": 10})
    assert "14 against 15: it keeps only years." in kept[1]
    assert isinstance(forms.store_form(saga, _martin()), Refuse)


def test_more_offers_the_ligature_and_the_store():
    saga = _saga(_martin(**{"Profession: Apothecary": 1}))
    page = menu_forms.page_for(saga, NodeKind.CHARACTER, character_id="m")
    assert available("make_ligature", page)
    assert available("apothecary_store", replace(page, section="section-char-season"))
    assert "apothecary_store" in {
        i.action for i in menu_forms.placed(page, "This Season")
    }
    saga.characters[0].abilities = []
    assert not available("make_ligature", page)
    assert not available(
        "apothecary_store", replace(page, section="section-char-season")
    )


def test_the_season_form_asks_for_the_formula_and_its_level():
    martin = _martin()
    martin.formulas = ["Cement"]
    saga = _saga(martin)
    fields = {f.key: f for f in season_forms.season_plan_fields(saga, martin, None)}
    assert [v for _, v in fields["formula_name"].options] == ["Cement"]
    shown = fields["formula_level"].show_if
    assert shown is not None and shown({"activity": "research_formula"})
    values = {"formula_name": "Cement", "philosophic_bonus": 4, "doses": None}
    assert season_forms._supplement_title("produce_remedies", values) == "Cement"
    assert season_forms._supplement_level("research_formula", {"formula_level": 5}) == 5
    found = season_forms._supplement_plan_values(martin, "produce_remedies", values)
    assert (found["other_modifier"], found["extra_vis"]) == (4, 0)

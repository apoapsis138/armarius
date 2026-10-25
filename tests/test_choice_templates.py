"""Choice templates: the Definitive Edition's Quick and Easy Virtues and
Flaws for a grog, four kinds of companion and a magus, the limits of each
type the choices are held to, and using one (the Virtues and Flaws on a
character left In Creation)."""

import pytest

from ars_magica_manager import catalog, creation
from ars_magica_manager import choice_templates as ct
from ars_magica_manager.forms import choice_templates as choice_forms
from ars_magica_manager.forms import creation as creation_forms
from ars_magica_manager.models import Saga, VirtueFlawInstance

VFS = catalog.load_virtue_flaw_catalog_by_id()
MAJOR = "vf_dark_secret"
MINOR_PERSONALITY = "vf_reckless"

#: A valid set of picks for each recipe (its first version).
PICKS = {
    "ct_quick_martial": {"slot_0_1": "single weapon", "flaw": MAJOR},
    "ct_quick_learned": {
        "slot_0_1": "medicine",
        "slot_0_2": "philosophiae",
        "flaw": MAJOR,
    },
    "ct_quick_social": {
        "slot_0_0": "vf_gossip",
        "slot_0_1": "charm",
        "slot_0_2": "guile",
        "flaw": MAJOR,
    },
    "ct_quick_magical": {"slot_0_0": "vf_second_sight", "flaw": MAJOR},
    "ct_quick_grog": {"flaw": MINOR_PERSONALITY},
    "ct_quick_magus": {
        "slot_0_1": "auram",
        "slot_0_2": "Fire",
        "slot_0_3": "creo",
        "slot_0_4": "ignem",
        "flaw": MAJOR,
    },
}


def _vf(vf_id, **params) -> VirtueFlawInstance:
    return VirtueFlawInstance(vf_id, params)


def _chosen(template_id, **values):
    template = ct.find(template_id)
    form_values = {**PICKS[template_id], **values}
    return ct.chosen(template, choice_forms.choices_from(template, form_values))


def _problem(template_id, **values):
    return ct.limit_problem(ct.find(template_id), _chosen(template_id, **values))


def test_the_templates_name_only_what_the_catalogs_hold():
    templates = ct.load_catalog()
    quick = [t for t in templates if t.kind == "quick" and t.book == "DE"]
    assert [t.id for t in quick] == list(PICKS)
    assert all(t.book == "DE" and t.page == 46 for t in quick)
    abilities = {a.name for a in catalog.load_ability_catalog()}
    for template in templates:
        assert template.type in ct.LIMITS
        for vf_id in template.statuses:
            assert vf_id in VFS
        for i in range(len(ct.variants(template))):
            for slot in ct.slots(template, i):
                for vf_id in [
                    slot.get("vf_id"),
                    slot.get("default"),
                    *slot.get("vf_ids", []),
                ]:
                    assert vf_id is None or vf_id in VFS, (template.id, vf_id)
                if slot["kind"] == "ability":
                    assert set(ct.ability_options(slot)) <= abilities
        for name, _ in ct.ability_rows(template, {"area": "Rhine"}):
            assert name in abilities or name.split(": ")[0] + ": " in {
                a.split("{")[0] for a in abilities
            }, (template.id, name)


@pytest.mark.parametrize("template_id", list(PICKS))
def test_each_recipe_balances_and_keeps_to_its_types_limits(template_id):
    template = ct.find(template_id)
    chosen = _chosen(template_id)
    assert ct.limit_problem(template, chosen) is None
    points = {"grog": "1 Virtue point, 1 Flaw point (of 3)"}.get(
        template.type, "3 Virtue points, 3 Flaw points (of 10)"
    )
    if template.type == "magus":
        points = "4 Virtue points, 4 Flaw points (of 10)"
    assert ct.tally_line(template, chosen) == points


def test_the_recipes_give_the_books_virtues():
    assert _chosen("ct_quick_martial")[:4] == [
        _vf("vf_covenfolk"),
        _vf("vf_warrior"),
        _vf("vf_puissant_ability", ability="single weapon"),
        _vf("vf_affinity_with_ability", ability="single weapon"),
    ]
    learned_one = _chosen("ct_quick_learned", variant="1", slot_1_1="medicine")
    assert learned_one[1:4] == [
        _vf("vf_educated"),
        _vf("vf_puissant_ability", ability="medicine"),
        _vf("vf_affinity_with_ability", ability="medicine"),
    ]
    assert _chosen("ct_quick_magical")[1:4] == [
        _vf("vf_second_sight"),
        _vf("vf_puissant_ability", ability="second sight"),
        _vf("vf_affinity_with_ability", ability="second sight"),
    ]
    specialist = _chosen("ct_quick_grog", variant="3", slot_3_0="Craft: Blacksmith")
    assert specialist == [
        _vf("vf_covenfolk"),
        _vf("vf_puissant_ability", ability="craft: blacksmith"),
        _vf(MINOR_PERSONALITY),
    ]
    assert _chosen("ct_quick_magus") == [
        _vf("vf_hermetic_magus"),
        _vf("vf_the_gift"),
        _vf("vf_deficient_form", form="auram"),
        _vf("vf_minor_magical_focus", focus="fire"),
        _vf("vf_puissant_art", art="creo"),
        _vf("vf_affinity_with_art", art="creo"),
        _vf("vf_puissant_art", art="ignem"),
        _vf(MAJOR),
    ]


def test_the_choices_keep_to_each_types_limits():
    assert "Flaw points" in _problem("ct_quick_martial", flaw="")
    assert "more often" in _problem("ct_quick_learned", slot_0_2="medicine")
    assert "4 Virtue points" in _problem("ct_quick_martial", status="vf_knight")
    gift_less = [*_chosen("ct_quick_martial"), _vf("vf_minor_magical_focus")]
    assert "need The Gift" in ct.limit_problem(ct.find("ct_quick_martial"), gift_less)
    # A grog's limits are the Grogs templates' own.
    assert "Major" in _problem("ct_quick_grog", flaw="vf_dark_secret")


def test_the_offered_flaws_statuses_and_virtues():
    martial, grog, magus = (
        ct.find(i) for i in ("ct_quick_martial", "ct_quick_grog", "ct_quick_magus")
    )
    assert all(f.tier == "Major" for f in ct.flaw_options(None, martial))
    assert {f.tier for f in ct.flaw_options(None, grog)} == {"Minor"}
    assert MINOR_PERSONALITY in {f.id for f in ct.flaw_options(None, grog)}
    assert ct.status_options(None, martial)[0].id == "vf_covenfolk"
    assert [s.id for s in ct.status_options(None, magus)] == ["vf_hermetic_magus"]
    assert ct.ability_options(ct.slots(martial, 0)[1]) == [
        "Bows",
        "Great Weapon",
        "Single Weapon",
        "Thrown Weapon",
    ]
    magical = {v.id for v in ct.supernatural_options(None)}
    assert {"vf_second_sight", "vf_animal_ken"} <= magical
    assert "vf_entrancement" not in magical  # Major


def test_the_form_reads_back_the_choices():
    saga = Saga(id="s", name="S", current_year=1220)
    learned = ct.find("ct_quick_learned")
    fields = {f.key: f for f in choice_forms.template_fields(saga, learned)}
    assert set(fields) == {
        "variant",
        "slot_0_1",
        "slot_0_2",
        "slot_1_1",
        "flaw",
        "status",
    }
    assert fields["status"].value == "vf_covenfolk"
    assert fields["flaw"].label == "Major Flaw"
    assert ("Medicine", "medicine") in fields["slot_0_1"].options
    choices = choice_forms.choices_from(
        learned, {"variant": "1", "slot_1_1": "medicine", "flaw": MAJOR}
    )
    assert (choices.variant, choices.flaw, choices.picks) == (
        1,
        MAJOR,
        ["", "medicine"],
    )
    magus = {
        f.key: f for f in choice_forms.template_fields(saga, ct.find("ct_quick_magus"))
    }
    assert magus["slot_0_2"].kind == "text"
    assert ("Creo", "creo") in magus["slot_0_3"].options
    assert magus["status"].value == "vf_hermetic_magus"


@pytest.mark.parametrize(
    "kind, template_id",
    [
        ("companion", "ct_quick_martial"),
        ("grog", "ct_quick_grog"),
        ("magus", "ct_quick_magus"),
    ],
)
def test_new_character_offers_each_type_its_recipes(kind, template_id):
    saga = Saga(id="s", name="S", current_year=1220)
    fields = {
        f.key: f for f in creation_forms.character_create_fields(saga, None, kind)
    }
    for other in ("magus", "companion", "grog", "mythic companion"):
        values = {v for _, v in fields[creation_forms.template_key(other)].options}
        assert (template_id in values) == (other == kind)
    live = creation_forms.character_create_live(
        {"type": kind, creation_forms.template_key(kind): template_id}
    )
    assert "page 46" in live and "Its choices come next" in live


def test_new_character_with_a_recipe_asks_its_choices_then_makes_the_character():
    saga = Saga(id="s", name="S", current_year=1220)
    covenant = creation.add_covenant(saga, "Fengheld", "")
    values = {"name": "Ulla", "type": "magus", "covenant_id": covenant.id}
    values[creation_forms.template_key("magus")] = "ct_quick_magus"
    form = creation_forms.new_character_form(saga, covenant.id, "magus")
    choices_form = form.apply(values)
    assert choices_form.help_id == "quick-virtues-flaws"
    assert not saga.characters  # nothing made until the choices are used
    choices_form.apply(PICKS["ct_quick_magus"])
    (ulla,) = saga.characters
    assert (ulla.type, ulla.in_creation, ulla.covenant_id) == (
        "magus",
        True,
        covenant.id,
    )
    assert _vf("vf_the_gift") in ulla.virtues_flaws
    assert not ulla.abilities and not ulla.creation_xp
    assert "Magus (DE quick)" in ulla.description.biography


# -- the Mythic Companions --

MYTHIC = [t for t in ct.load_catalog() if t.kind == "mythic"]
#: Flaws of the player's own that pay for each kind's required Virtues.
FLAWS = [
    _vf("vf_dark_secret"),
    _vf("vf_reckless"),
    _vf("vf_clumsy"),
]


def _mythic_values(template, **values):
    """The form's own starting values, each required select at a different
    choice (two Holy Powers can't be the same) and each required text
    filled in."""
    fields = choice_forms.template_fields(Saga(id="s", name="S"), template)
    found = {f.key: f.value for f in fields if f.kind != "info"}
    for k, f in enumerate(fields):
        if f.kind == "select" and not found.get(f.key) and f.options:
            found[f.key] = f.options[k % len(f.options)][1]
        elif f.kind == "text" and f.required:
            found[f.key] = "Rhine"
    return {**found, **values}


def test_every_status_virtue_has_its_mythic_companion_template():
    assert [ct.option_label(t) for t in MYTHIC] == [
        "Devil Child (DE)",
        "Faerie Doctor (DE)",
        "Spirit Votary (DE)",
        "Nephilim (DE)",
        "Zahid (RoP:D)",
        "Perfectus (RoP:D)",
        "Kabbalist (RoP:D)",
        "Diabolist (RoP:I)",
        "Summoner (RoP:I)",
        "Blood of Heroes (HoH:TL)",
        "Maestro (A&A)",
    ]
    from ars_magica_manager.rules import creation_character as cc

    given = {s["vf_id"] for t in MYTHIC for s in ct.slots(t, 0) if s["kind"] == "fixed"}
    assert cc.mythic_status_ids() <= given
    assert VFS["vf_perfectus_mythic"].tier == "Free"
    assert VFS["vf_perfectus"].category == "Social Status"  # the DE's, kept


@pytest.mark.parametrize("template", MYTHIC, ids=lambda t: t.id)
def test_each_mythic_template_keeps_to_the_limits_once_its_flaws_pay(template):
    values = _mythic_values(template)
    for n, flaw in enumerate(FLAWS[: template.more_flaws]):
        values[f"flaw_{n}"] = flaw
    chosen = ct.chosen(template, choice_forms.choices_from(template, values))
    assert ct.limit_problem(template, chosen) is None, ct.tally_line(template, chosen)
    statuses = [vf.vf_id for vf in chosen if vf.vf_id in ct.cc.mythic_status_ids()]
    assert len(statuses) == 1


def test_the_book_flaw_can_be_substituted_and_more_virtues_must_be_paid_for():
    doctor = ct.find("ct_mc_faerie_doctor")
    values = _mythic_values(doctor)
    assert values["slot_0_4"] == "vf_dutybound"
    swapped = ct.chosen(
        doctor, choice_forms.choices_from(doctor, {**values, "slot_0_4": "vf_reckless"})
    )
    assert _vf("vf_reckless") in swapped and _vf("vf_dutybound") not in swapped
    greedy = {**values, "virtue_0": _vf("vf_tough")}
    problem = ct.limit_problem(
        doctor, ct.chosen(doctor, choice_forms.choices_from(doctor, greedy))
    )
    assert "allow 5" in problem
    gifted = {**values, "virtue_0": _vf("vf_the_gift")}
    assert "no Gift" in ct.limit_problem(
        doctor, ct.chosen(doctor, choice_forms.choices_from(doctor, gifted))
    )


def test_a_mythic_template_puts_the_books_minimum_abilities_on_the_worksheet():
    saga = Saga(id="s", name="S", current_year=1220)
    covenant = creation.add_covenant(saga, "Fengheld", "")
    votary = ct.find("ct_mc_spirit_votary")
    values = {"name": "Ulla", "type": "mythic companion", "covenant_id": covenant.id}
    values[creation_forms.template_key("mythic companion")] = votary.id
    choices_form = creation_forms.new_character_form(
        saga, covenant.id, "mythic companion"
    ).apply(values)
    assert choices_form.help_id == "mythic-companion-templates"
    choices_form.apply(_mythic_values(votary, blank_area="Black Forest"))
    (ulla,) = saga.characters
    assert ulla.type == "mythic companion" and ulla.in_creation
    assert {a.name for a in ulla.abilities} == {
        "Area Lore: Black Forest",
        "Magic Lore",
        "Penetration",
        "Second Sight",
    }
    assert _vf("vf_spiritual_pact", spirit="rhine") in ulla.virtues_flaws

    unticked = ct.find("ct_mc_zahid")
    choices = choice_forms.choices_from(
        unticked, _mythic_values(unticked, abilities=False)
    )
    zahid = creation.add_character(saga, "Z", "mythic companion", covenant.id)
    ct.apply(saga, zahid, unticked, choices)
    assert not zahid.abilities and not zahid.creation_xp


# -- the supplements' ready-made companions --

SAMPLES = [t for t in ct.load_catalog() if t.kind == "sample"]


def _sample_values(template, **values):
    found = _mythic_values(template)
    for blank in ct.blanks(template):
        found[f"blank_{blank}"] = "Rhine"
    return {**found, **values}


def test_each_sample_names_only_what_the_catalogs_hold_and_keeps_to_its_limits():
    assert len(SAMPLES) >= 20
    families = {
        a.name.split("{")[0] for a in catalog.load_ability_catalog() if "{" in a.name
    }
    names = {a.name for a in catalog.load_ability_catalog()}
    for template in SAMPLES:
        assert template.type in ("companion", "mythic companion")
        assert template.age > 0 and template.characteristics
        rows = ct.ability_rows(template)
        for name, _ in rows:
            assert name in names or any(name.startswith(f) for f in families), (
                template.id,
                name,
            )
        assert template.native in {name for name, _ in rows}, template.id
        values = _sample_values(template)
        chosen = ct.chosen(template, choice_forms.choices_from(template, values))
        assert ct.limit_problem(template, chosen) is None, (
            template.id,
            ct.limit_problem(template, chosen),
        )


def test_a_sample_starts_in_creation_with_the_books_character():
    saga = Saga(id="s", name="S", current_year=1220)
    covenant = creation.add_covenant(saga, "Fengheld", "")
    banco = next(t for t in SAMPLES if t.id.startswith("ct_banco"))
    values = {"name": "Banco", "type": "companion", "covenant_id": covenant.id}
    values[creation_forms.template_key("companion")] = banco.id
    choices_form = creation_forms.new_character_form(
        saga, covenant.id, "companion"
    ).apply(values)
    assert choices_form.help_id == "companion-sample-templates"
    choices_form.apply(_sample_values(banco, vf_0=False))
    (made,) = saga.characters
    assert made.in_creation and made.type == "companion"
    assert made.background.year_born == 1220 - banco.age
    assert made.characteristics.intelligence == banco.characteristics["intelligence"]
    first = banco.virtues_flaws[0]
    assert VirtueFlawInstance(first["vf_id"], first.get("params", {})) not in (
        made.virtues_flaws
    )
    specialties = {a.name: a.specialty for a in made.abilities}
    for ability in banco.abilities:
        if ability.get("specialty") and "{" not in ability["name"]:
            assert specialties[ability["name"]] == ability["specialty"]
    assert [(t.name, t.score) for t in made.personality_traits] == [
        tuple(t) for t in banco.traits
    ]


# -- a Grogs template played as a companion --


def test_a_grogs_template_can_be_played_as_a_companion_with_a_story_flaw():
    saga = Saga(id="s", name="S", current_year=1220)
    covenant = creation.add_covenant(saga, "Fengheld", "")
    fields = {
        f.key: f
        for f in creation_forms.character_create_fields(saga, None, "companion")
    }
    offered = {
        v: label
        for label, v in fields[creation_forms.template_key("companion")].options
    }
    assert offered["ctg:gt_bull"] == "The Bull (Grogs, as a companion)"
    grog = {
        f.key: f for f in creation_forms.character_create_fields(saga, None, "grog")
    }
    assert not any(
        v.startswith("ctg:")
        for _, v in grog[creation_forms.template_key("grog")].options
    )
    values = {"name": "Madoc", "type": "companion", "covenant_id": covenant.id}
    values[creation_forms.template_key("companion")] = "ctg:gt_animal_trainer"
    step = creation_forms.new_character_form(saga, covenant.id, "companion").apply(
        values
    )
    assert "Story Flaw" in step.validate({})
    story = {"flaw_0": _vf("vf_dark_secret")}  # a Major Flaw: no grog may take it
    assert step.validate(story) is None
    assert "of 10" in step.live(story)
    assert step.apply(story) is None  # Madoc's list leaves nothing blank
    (madoc,) = saga.characters
    assert madoc.type == "companion" and madoc.in_creation
    assert _vf("vf_dark_secret") in madoc.virtues_flaws
    assert ("Loyal", 1) not in [(t.name, t.score) for t in madoc.personality_traits]
    assert "Played as a companion" in madoc.description.biography

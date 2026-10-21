"""Grogs' Chapter 7 Grog Templates: the catalog, the grog limits the
choices are held to, and using one (the book's Ability list for the age
as Creation Worksheet xp, the grog left In Creation)."""

import pytest

from ars_magica_manager import catalog, creation
from ars_magica_manager import grog_templates as gt
from ars_magica_manager.forms import creation as creation_forms
from ars_magica_manager.forms import grog_templates as grog_forms
from ars_magica_manager.models import Saga, VirtueFlawInstance
from ars_magica_manager.rules import creation_access as access
from ars_magica_manager.rules import creation_xp as cx
from ars_magica_manager.rules.xp import ability_xp, score_from_xp

TEMPLATES = catalog.load_grog_template_catalog()
VFS = catalog.load_virtue_flaw_catalog_by_id()

#: Every (template, version, age) the catalog offers.
CASES = [
    (t, vi, ai)
    for t in TEMPLATES
    for vi, variant in enumerate(gt.variants(t))
    for ai in range(len(variant.ages))
]


def _book_choices(template, vi=0, ai=0, **changes) -> gt.Choices:
    variant = gt.variants(template)[vi]
    choices = gt.Choices(
        variant=vi,
        age=ai,
        status=variant.statuses[0],
        virtues_flaws=[gt.instance(e) for e in variant.virtues_flaws],
        characteristics=True,
        traits=[tuple(trait) for trait in template.traits],
    )
    for key, value in changes.items():
        setattr(choices, key, value)
    return choices


def _vf(vf_id, **params) -> VirtueFlawInstance:
    return VirtueFlawInstance(vf_id, params)


def test_the_book_has_nineteen_human_grog_templates():
    assert len(TEMPLATES) == 19
    assert len({t.id for t in TEMPLATES}) == 19
    names = {t.name for t in TEMPLATES}
    assert {"The Advisor", "The Street Thug", "Time-Lost Witness"} <= names
    # Horses & Hounds is its own story: animal grogs need more than a template.
    assert not any("Hound" in t.name for t in TEMPLATES)


@pytest.mark.parametrize("template", TEMPLATES, ids=lambda t: t.id)
def test_a_template_names_only_what_the_catalogs_hold(template):
    for variant in gt.variants(template):
        assert variant.ages, template.id
        for status in variant.statuses:
            assert "Social Status" in (
                VFS[status].category,
                *VFS[status].extra_categories,
            )
        entries = [*variant.virtues_flaws, *gt._pool_entries(template)]
        for entry in entries:
            definition = VFS[entry["vf_id"]]
            assert set(entry["params"]) <= set(definition.parameters), entry
            # The book's own and suggested ones are all a grog may take.
            assert definition.tier == "Minor", entry
            assert not catalog.needs_the_gift(definition), entry
        for age in variant.ages:
            names = [row["name"] for row in age["abilities"]]
            assert age["native"] in names, (template.id, age["age"])
            for name in names:
                assert access.ability_def(name) is not None, name
    assert template.page and template.concept


@pytest.mark.parametrize(
    ("template", "vi", "ai"),
    CASES,
    ids=[f"{t.id}-{vi}-{ai}" for t, vi, ai in CASES],
)
def test_using_a_template_gives_the_books_scores_on_the_worksheet(template, vi, ai):
    saga = Saga(id="s", name="S", current_year=1220)
    grog = creation.add_character(saga, "Ulla", "grog", None)
    choices = _book_choices(template, vi, ai)
    names = {blank: f"The {blank.title()}" for blank in gt.blanks(template, choices)}
    gt.apply(saga, grog, template, choices, names)

    assert grog.in_creation
    age = gt.variants(template)[vi].ages[ai]
    assert grog.background.year_born == 1220 - age["age"]
    shown = {a.name: (score_from_xp(a.xp, 5), a.specialty) for a in grog.abilities}
    for row in gt._rows(template, choices):
        name = cx.fill_template(((row["name"], 0),), names)[0][0]
        assert shown[name] == (row["score"], row.get("specialty")), name
    assert not any("{" in a.name for a in grog.abilities)
    # Every xp is on the worksheet, the Native Language as Early Childhood's 75.
    assert sum(creation.gained_xp(x) for x in grog.creation_xp) == sum(
        a.xp for a in grog.abilities
    )
    natives = [x for x in grog.creation_xp if x.note == cx.NATIVE]
    assert [(x.step, x.xp) for x in natives] == [("childhood", 75)]
    assert {x.step for x in grog.creation_xp} <= {
        "childhood",
        "virtue",
        "free",
        "later_life",
    }
    assert template.name in grog.description.biography
    assert any(t.name.startswith("Loyal") for t in grog.personality_traits)


def test_xp_goes_on_step_by_step():
    """The Advisor at 20: the Native Language, Educated's 50 on Latin and
    Artes Liberales, 45 of Early Childhood on what a child may learn, and
    the rest as Later Life, which matches its 15 years at 15 xp."""
    saga = Saga(id="s", name="S", current_year=1220)
    grog = creation.add_character(saga, "Ulla", "grog", None)
    advisor = gt.find("gt_advisor")
    gt.apply(saga, grog, advisor, _book_choices(advisor), {"language": "French"})

    def spent(step):
        return sum(x.xp for x in cx.entries(grog, step))

    assert spent("childhood") == 75 + 45
    virtue = cx.entries(grog, "virtue")
    assert {x.note for x in virtue} == {"vf_educated"}
    assert {x.target for x in virtue} <= {"Dead Language: Latin", "Artes Liberales"}
    assert spent("virtue") == 50
    assert spent("later_life") == 15 * 15
    assert grog.characteristics.intelligence == 3
    assert grog.characteristics.strength == -1


def test_a_supernatural_virtues_free_score_is_recorded():
    """The Ferryman's Premonitions and Second Sight start with their free
    5 xp; the rest of their xp is Later Life."""
    saga = Saga(id="s", name="S", current_year=1220)
    grog = creation.add_character(saga, "Ulla", "grog", None)
    ferryman = gt.find("gt_role_bound_ferryman")
    gt.apply(saga, grog, ferryman, _book_choices(ferryman), {"covenant": "Fengheld"})
    free = {x.target: x.xp for x in cx.entries(grog, "free")}
    assert free == {"Premonitions": 5, "Second Sight": 5}
    assert "Organization Lore: Fengheld" in {a.name for a in grog.abilities}
    assert [(t.name, t.score) for t in grog.personality_traits] == [
        ("Loyal to the Covenant", 3),
        ("Taciturn", 2),
        ("Reliable", 1),
    ]


def test_an_affinity_needs_less_xp_for_the_same_score():
    saga = Saga(id="s", name="S", current_year=1220)
    grog = creation.add_character(saga, "Ulla", "grog", None)
    almogavar = gt.find("gt_almogavars")
    affinity = _vf("vf_affinity_with_ability", ability="single weapon")
    choices = _book_choices(almogavar, virtue_flaws=None)
    choices.virtues_flaws = [affinity, _vf("vf_proud")]
    gt.apply(saga, grog, almogavar, choices, {"area": "Aragon", "language": "Catalan"})
    weapon = next(a for a in grog.abilities if a.name == "Single Weapon")
    assert weapon.xp >= ability_xp(4)
    spent = sum(x.xp for x in grog.creation_xp if x.target == "Single Weapon")
    assert spent < ability_xp(4)


def test_loyal_and_brave_are_added_when_the_book_lacks_them():
    saga = Saga(id="s", name="S", current_year=1220)
    grog = creation.add_character(saga, "Ulla", "grog", None)
    almogavar = gt.find("gt_almogavars")
    gt.apply(
        saga, grog, almogavar, _book_choices(almogavar), {"area": "A", "language": "B"}
    )
    assert [(t.name, t.score) for t in grog.personality_traits] == [
        ("Loyal", 1),
        ("Brave", 1),
    ]


def test_the_book_details_and_differences_go_in_the_biography():
    saga = Saga(id="s", name="S", current_year=1220)
    grog = creation.add_character(saga, "Ulla", "grog", None)
    confessor = gt.find("gt_confessor")
    gt.apply(
        saga,
        grog,
        confessor,
        _book_choices(confessor, 1, 2),
        {"area": "X", "language": "Y"},
    )
    text = grog.description.biography
    assert "The Confessor, Islamic at age 55" in text
    assert "Vow (celibacy)" in text
    assert "Where this differs from the book" in text
    assert "Theology: Islam" in {a.name for a in grog.abilities}
    assert grog.background.year_born == 1220 - 55


# -- the grog limits --


@pytest.mark.parametrize(
    ("chosen", "problem"),
    [
        ([_vf("vf_covenfolk"), _vf("vf_magical_air")], "no Major"),
        ([_vf("vf_covenfolk"), _vf("vf_the_gift")], "The Gift"),
        (
            [
                _vf("vf_covenfolk"),
                _vf("vf_tough"),
                _vf("vf_vulnerable_to_folk_tradition"),
            ],
            "Hermetic",
        ),
        (
            [
                _vf("vf_covenfolk"),
                _vf("vf_clumsy"),
                _vf("vf_carefree"),
                _vf("vf_gullible"),
                _vf("vf_jinxed"),
            ],
            "at most 3 Minor Flaws",
        ),
        ([_vf("vf_covenfolk"), _vf("vf_tough"), _vf("vf_large")], "2 Virtue points"),
        ([_vf("vf_clumsy")], "one Social Status"),
        ([_vf("vf_custos"), _vf("vf_outcast"), _vf("vf_clumsy")], "one Social Status"),
    ],
)
def test_the_choices_keep_to_a_grogs_limits(chosen, problem):
    assert problem in (gt.limit_problem(chosen) or "")


def test_fewer_virtues_than_flaws_is_allowed_for_now():
    chosen = [
        _vf("vf_covenfolk"),
        _vf("vf_clumsy"),
        _vf("vf_tough"),
        _vf("vf_carefree"),
    ]
    assert gt.limit_problem(chosen) is None
    assert gt.tally_line(chosen) == "1 Virtue point, 2 Flaw points (2 of 3 Minor Flaws)"


def test_an_inoffensive_or_offensive_virtue_is_no_hermetic_for_the_worksheet():
    """Offensive to Animals is Hermetic or General: the Failed
    Apprentice's own set passes the worksheet's Gift check."""
    from ars_magica_manager.rules import creation_virtues as cv

    saga = Saga(id="s", name="S", current_year=1220)
    grog = creation.add_character(saga, "Ulla", "grog", None)
    failed = gt.find("gt_failed_apprentice")
    choices = _book_choices(failed)
    assert gt.limit_problem(choices.all_virtues_flaws()) is None
    gt.apply(
        saga, grog, failed, choices, {"area": "A", "language": "B", "covenant": "C"}
    )
    assert cv.tally(grog).hermetic == 0


# -- offered, and the choices form --


def test_the_templates_are_offered_only_while_grogs_is_in_play():
    saga = Saga(id="s", name="S", current_year=1220)
    assert len(gt.templates(saga)) == 19
    grog_field = next(
        f
        for f in creation_forms.character_create_fields(saga, None, "grog")
        if f.key == creation_forms.template_key("grog")
    )
    assert ("The Advisor (Grogs)", "gt_advisor") in grog_field.options
    saga.books_in_play = []
    assert gt.templates(saga) == []
    grog_field = next(
        f
        for f in creation_forms.character_create_fields(saga, None, "grog")
        if f.key == creation_forms.template_key("grog")
    )
    assert not any(value.startswith("gt_") for _, value in grog_field.options)


def test_the_form_starts_with_the_books_set_and_reads_back_the_choices():
    saga = Saga(id="s", name="S", current_year=1220)
    bull = gt.find("gt_bull")
    fields = {f.key: f for f in grog_forms.template_fields(saga, bull)}
    assert fields["status_0"].options[0] == ("Covenfolk", "vf_covenfolk")
    stigmatic = next(n for n, e in enumerate(bull.pool) if "one_of" in e)
    values = {
        "age_0": "1",
        "status_0": "vf_turb_trained",
        "pool_0": True,  # Large
        f"pool_{stigmatic}": "1",  # Faerie Stigmatic
        "flaw_0": _vf("vf_wrathful"),
    }
    choices = grog_forms.choices_from(bull, values)
    assert (choices.age, choices.status) == (1, "vf_turb_trained")
    assert choices.virtues_flaws == [
        _vf("vf_large"),
        _vf("vf_realm_stigmatic", realm="faerie"),
        _vf("vf_wrathful"),
    ]
    assert "Offensive Fighter" in fields["flaw_0"].hint

    advisor = gt.find("gt_advisor")
    keys = {f.key for f in grog_forms.template_fields(saga, advisor)}
    assert {"characteristics", "trait_0"} <= keys
    unticked = grog_forms.choices_from(
        advisor, {"vf_0_3": False, "trait_0": "Wry Humor"}
    )
    assert _vf("vf_small_frame") not in unticked.virtues_flaws
    assert ("Wry Humor", 1) in unticked.traits


def test_new_character_with_a_grogs_template_asks_its_choices_then_blanks():
    saga = Saga(id="s", name="S", current_year=1220)
    covenant = creation.add_covenant(saga, "Fengheld", "")
    values = {"name": "Ulla", "type": "grog", "covenant_id": covenant.id}
    values[creation_forms.template_key("grog")] = "gt_refugee_librarian"
    form = creation_forms.new_character_form(saga, covenant.id, "grog")
    choices_form = form.apply(values)
    assert choices_form.help_id == "grog-templates"
    blanks_form = choices_form.apply({"age_0": "1"})
    fields = {f.key: f.value for f in blanks_form.fields()}
    assert fields["covenant"] == "Fengheld"
    assert not saga.characters
    blanks_form.apply({**fields, "language": "German", "former_covenant": "Calebais"})
    (ulla,) = [c for c in saga.characters if c.name == "Ulla"]
    assert ulla.in_creation and ulla.covenant_id == covenant.id
    assert "Organization Lore: Calebais" in {a.name for a in ulla.abilities}

"""The census of Art & Academe's and City & Guild's Virtues, Flaws and
Abilities against the catalogs, and the two books' ready-made characters.

Nearly every entry these two books print was reprinted in the Definitive
Edition, so the catalog already has them (as DE entries, the DE winning
where the wording differs); the census adds only what the DE left out.
"""

from ars_magica_manager import catalog, sourcebooks
from ars_magica_manager import choice_templates as ct
from ars_magica_manager.forms import choice_templates as choice_forms
from ars_magica_manager.models import Character, Saga, VirtueFlawInstance
from ars_magica_manager.rules import creation_access

#: Each book's Virtues and Flaws, by catalog id, with the printed page.
ART_AND_ACADEME = {
    "vf_aristotelian_training": 12,
    "vf_academic_concentration_subject": 12,
    "vf_herbalism": 55,
    "vf_physician_of_salerno": 55,
    "vf_magister_in_medicina": 56,
    "vf_surgical_empiricus": 56,
    "vf_leprosy": 49,
    "vf_baccalaureus": 90,
    "vf_beadle": 91,
    "vf_cathedral_school_master": 91,
    "vf_doctor_in_faculty": 91,
    "vf_jurist": 91,
    "vf_lupus_the_wolf": 91,
    "vf_magister_in_artibus": 91,
    "vf_nuntius": 91,
    "vf_prestigious_student": 91,
    "vf_simple_student": 92,
    "vf_university_grammar_teacher": 92,
    "vf_failed_student": 92,
    "vf_poor_disputer": 92,
    "vf_rector_proctor": 92,
    "vf_university_dean": 92,
    "vf_artistic_renown": 133,
    "vf_hermetic_inclination_in_form": 134,
    "vf_life_linked_art": 134,
    "vf_maestro": 134,
    "vf_prolific_artist": 134,
    "vf_fickle_nature": 134,
    "vf_fluctuating_fortune": 134,
    "vf_gullible": 134,
    "vf_unruly_air": 134,
}
CITY_AND_GUILD = {
    "vf_leprosy": 27,
    "vf_town_magistrate": 29,
    "vf_failed_master": 52,
    "vf_failed_journeyman": 52,
    "vf_laborer": 53,
    "vf_craftsman": 53,
    "vf_male_guild_sponsor": 53,
    "vf_guild_apprentice": 53,
    "vf_journeyman": 53,
    "vf_guild_master": 53,
    "vf_senior_master": 53,
    "vf_guild_dean": 53,
    "vf_eye_of_hephaestus": 71,
    "vf_touched_by_realm": 71,
    "vf_crafters_healing": 71,
    "vf_capo": 108,
    "vf_factor": 108,
    "vf_merchant_adventurer": 108,
    "vf_partner": 109,
    "vf_perfect_eye_for_commodity": 109,
    "vf_educated_vernacular": 109,
    "vf_bigamist": 109,
    "vf_employed_by_company": 109,
    "vf_many_marriageable_daughters": 109,
    "vf_unhappily_married": 109,
}


def test_every_virtue_and_flaw_of_the_two_books_is_in_the_catalog():
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    missing = sorted(
        vf_id for vf_id in {**ART_AND_ACADEME, **CITY_AND_GUILD} if vf_id not in by_id
    )
    assert not missing, f"not in the catalog: {missing}"


def test_where_the_supplement_and_the_de_disagree_the_catalog_follows_the_de():
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    # A&A p. 92 prints Failed Student as a Story Flaw; DE p. 136: General.
    assert (by_id["vf_failed_student"].category, by_id["vf_failed_student"].tier) == (
        "General",
        "Minor",
    )
    # C&G p. 71 prints Crafter's Healing as Major; DE p. 83: Minor.
    assert by_id["vf_crafters_healing"].tier == "Minor"
    # C&G p. 53 prints Male Guild Sponsor as a General Virtue; DE p. 103:
    # Social Status.
    assert by_id["vf_male_guild_sponsor"].category == "Social Status"
    # A&A p. 134's Gullible is a Personality Flaw; DE p. 140: General.
    assert by_id["vf_gullible"].category == "General"
    # Leprosy's Living Condition penalty (A&A p. 49, C&G p. 27, DE p. 143).
    [modifier] = by_id["vf_leprosy"].modifiers
    assert (modifier.applies_to, modifier.amount) == ("living_conditions", -2)


def test_the_herbalism_ability_loads_with_its_book_and_page():
    herbalism = catalog.load_ability_catalog_by_id()["ab_herbalism"]
    assert (herbalism.name, herbalism.category) == ("Herbalism", "General")
    assert herbalism.source == "A&A"
    assert "A&A p. 55" in herbalism.description
    # Medicine's specialties (A&A p. 54) for the ground Herbalism covers,
    # therapy (disease recovery) among them; not regimens (p. 55).
    specialties = herbalism.description.split("Specialties: ")[1]
    for name in ("diagnosis", "prognosis", "therapy", "theriacs", "a specific disease"):
        assert name in specialties, name
    assert "regimen" not in specialties
    assert sourcebooks.in_play(herbalism.source, ["A&A"])
    assert not sourcebooks.in_play(herbalism.source, [])
    assert creation_access.ability_category("Herbalism") == "General"


def test_the_herbalism_virtue_names_an_ability_the_catalog_has():
    virtue = catalog.load_virtue_flaw_catalog_by_id()["vf_herbalism"]
    assert virtue.source == "A&A" and "Herbalism" in virtue.summary
    names = {entry.name for entry in catalog.load_ability_catalog()}
    assert "Herbalism" in names
    holder = Character(id="h", name="H", type="companion")
    holder.virtues_flaws.append(VirtueFlawInstance(vf_id=virtue.id))
    assert creation_access.may_learn(holder, "Herbalism")


#: The two books' ready-made characters, by template id: book, page and
#: the name the Template list shows ("Role - Name").
SAMPLES = {
    "ct_leonardo_fibonacci": ("A&A", 15, "Mathematician of Pisa - Leonardo Fibonacci"),
    "ct_gilles_de_corbeil": (
        "A&A",
        51,
        "Physician to the King of France - Gilles de Corbeil",
    ),
    "ct_brother_julian": ("A&A", 85, "Dominican Friar - Brother Julian"),
    "ct_gilpatrick": ("A&A", 98, "Bachelor of Arts at Paris - Gilpatrick"),
    "ct_brogo_the_dwarf": ("A&A", 122, "Wandering Trouvère - Brogo the Dwarf"),
    "ct_julian_apprentice_carpenter": ("C&G", 44, "Apprentice Carpenter - Julian"),
    "ct_obano_journeyman_swordsmith": ("C&G", 47, "Journeyman Swordsmith - Obano"),
    "ct_doolin_guild_master_clothier": ("C&G", 48, "Guild Master Clothier - Doolin"),
    "ct_banco": ("C&G", 51, "Dean of the Goldsmiths' Guild - Banco"),
}


def test_the_two_books_characters_are_templates_named_by_role_then_name():
    for template_id, (book, page, name) in SAMPLES.items():
        template = ct.find(template_id)
        assert template is not None, template_id
        assert (template.book, template.page, template.kind) == (book, page, "sample")
        assert template.name == name
        assert template in ct.templates(None, "companion")
        assert template not in ct.templates(
            Saga(id="s", name="S", books_in_play=[]), "companion"
        )


def test_each_character_keeps_to_a_companions_limits_with_every_virtue_ticked():
    for template_id in SAMPLES:
        template = ct.find(template_id)
        assert template is not None
        values = {f"blank_{b}": "Rhine" for b in ct.blanks(template)}
        chosen = ct.chosen(template, choice_forms.choices_from(template, values))
        assert ct.limit_problem(template, chosen) is None, template_id


def test_brogo_takes_enchanting_music_as_the_virtue_and_its_ability():
    brogo = ct.find("ct_brogo_the_dwarf")
    assert brogo is not None
    enchanting = next(
        vf for vf in brogo.virtues_flaws if vf["vf_id"] == "vf_enchanting_ability"
    )
    assert enchanting["params"] == {"ability": "music"}
    names = [a["name"] for a in brogo.abilities]
    assert "Enchanting: Music" in names
    assert {"vf_curse_of_venus", "vf_dwarf", "vf_proud_major"} <= {
        vf["vf_id"] for vf in brogo.virtues_flaws
    }

"""The census of Lords of Men's and The Church's Virtues, Flaws and
Abilities against the catalogs, and The Church's ready-made characters.

The Definitive Edition reprints nearly every Virtue and Flaw the two books
print (the clergy's, the Templars', the household offices'), so the
catalog has them as DE entries, the DE winning where the wording differs;
the census adds only what the DE left out: Lords of Men's Siege Weapon
Ability, and The Church's sample characters as choice templates.
"""

from dataclasses import asdict, replace

from ars_magica_manager import catalog, sourcebooks
from ars_magica_manager import choice_templates as ct
from ars_magica_manager.forms import choice_templates as choice_forms
from ars_magica_manager.models import Character, VirtueFlawInstance
from ars_magica_manager.rules import creation_access

#: Each book's Virtues and Flaws, by catalog id, with the printed page.
LORDS_OF_MEN = {
    "vf_paid_rights": 27,
    "vf_oath_of_fealty": 31,
    "vf_knightly_demands": 31,
    "vf_knight": 31,
    "vf_landed_noble": 31,
    "vf_great_noble": 31,
    "vf_master_of_kennels": 61,
    "vf_falconer": 61,
    "vf_marshal": 61,
}
THE_CHURCH = {
    "vf_senior_clergy": 25,
    "vf_priest": 26,
    "vf_clerk": 26,
    "vf_religious": 26,
    "vf_license_of_absence": 26,
    "vf_commanding_aura": 26,
    "vf_dark_secret": 27,
    "vf_regular": 27,
    "vf_monastic_vows": 27,
    "vf_brother_knight": 123,
    "vf_brother_chaplain": 123,
    "vf_brother_sergeant": 124,
    "vf_templar_confrere_or_consoeur": 124,
    "vf_templar_servant": 124,
    "vf_templar_specialist": 124,
    "vf_templar_administrator": 125,
    "vf_templar_commander": 125,
    "vf_templar_office_holder": 125,
    "vf_templar_prestige": 125,
}
#: The Church's ready-made characters, by choice-template id, with the page.
SAMPLES = {
    "ct_mystic_nun": 81,
    "ct_anne_holy_hermit": 82,
    "ct_imposter": 82,
    "ct_templar_commander": 126,
    "ct_templar_brother_priest": 127,
    "ct_francis_of_assisi": 131,
    "ct_brother_elias": 133,
}


def test_every_virtue_and_flaw_of_the_two_books_is_in_the_catalog():
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    missing = sorted(
        vf_id for vf_id in {**LORDS_OF_MEN, **THE_CHURCH} if vf_id not in by_id
    )
    assert not missing, f"not in the catalog: {missing}"


def test_where_the_church_and_the_de_disagree_the_catalog_follows_the_de():
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    # The Church p. 125 printed Reputation 3; DE p. 112 and the Errata
    # (p. 78) make it 4.
    assert "Reputation 4" in by_id["vf_templar_prestige"].summary
    # The Church's Templar Commander is the DE's (p. 111): Major Social
    # Status.
    commander = by_id["vf_templar_commander"]
    assert (commander.category, commander.tier) == ("Social Status", "Major")
    # Brother Knight, Brother Sergeant and Brother Chaplain are the DE's
    # crusading-order versions (p. 73): The Church's Brother-Priest is the
    # DE's Brother Chaplain, so only the DE's is in the catalog.
    for status in ("vf_brother_knight", "vf_brother_sergeant", "vf_brother_chaplain"):
        assert by_id[status].source == "DE", status
    assert "vf_brother_priest" not in by_id
    # License of Absence frees one more season (The Church p. 26).
    [season] = by_id["vf_license_of_absence"].modifiers
    assert (season.applies_to, season.amount) == ("working_seasons", -1)


def test_the_siege_weapon_ability_loads_with_its_book_and_page():
    siege = catalog.load_ability_catalog_by_id()["ab_siege_weapon"]
    assert (siege.name, siege.category, siege.source) == (
        "Siege Weapon",
        "Martial",
        "LoM",
    )
    assert "p. 114" in siege.description
    assert sourcebooks.in_play(siege.source, ["LoM"])
    assert not sourcebooks.in_play(siege.source, [])
    assert creation_access.ability_category("Siege Weapon") == "Martial"


def test_the_churchs_samples_are_choice_templates_with_their_pages():
    for template_id, page in SAMPLES.items():
        template = ct.find(template_id)
        assert template is not None, template_id
        assert (template.book, template.page, template.kind) == ("TC", page, "sample")
        assert template.type == "companion"


def test_each_new_sample_keeps_to_a_companions_limits_with_every_virtue_ticked():
    for template_id in (
        "ct_templar_commander",
        "ct_templar_brother_priest",
        "ct_francis_of_assisi",
        "ct_brother_elias",
    ):
        template = ct.find(template_id)
        assert template is not None
        values = {f"blank_{b}": "Rhine" for b in ct.blanks(template)}
        chosen = ct.chosen(template, choice_forms.choices_from(template, values))
        assert ct.limit_problem(template, chosen) is None, template_id


def test_the_commander_takes_the_de_status_and_balances_without_temporal_influence():
    commander = ct.find("ct_templar_commander")
    assert commander is not None
    assert commander.statuses == ["vf_templar_commander"]
    ids = [vf["vf_id"] for vf in commander.virtues_flaws]
    assert "vf_temporal_influence" not in ids and "vf_brother_knight" not in ids
    assert ids.count("vf_greedy_major") == 1
    assert set(ct.blanks(commander)) == {"area", "language", "second_language"}


def test_the_templar_rank_template_offers_every_rank_as_a_social_status():
    rank = ct.find("ct_templar_rank")
    assert rank is not None and rank.book == "TC"
    offered = [s.id for s in ct.status_options(None, rank)]
    assert offered == rank.statuses
    assert "vf_brother_chaplain" in offered and "vf_templar_commander" in offered
    # Each standing balances with two Minor Flaws of the player's own.
    for variant in range(len(ct.variants(rank))):
        values = {
            "variant": str(variant),
            "status": "vf_brother_sergeant",
            "flaw_0": VirtueFlawInstance("vf_mentor"),
            "flaw_1": VirtueFlawInstance("vf_fear"),
        }
        chosen = ct.chosen(rank, choice_forms.choices_from(rank, values))
        assert ct.limit_problem(rank, chosen) is None, (variant, chosen)
    renowned = ct.chosen(
        rank,
        choice_forms.choices_from(
            rank, {"variant": "1", "status": "vf_brother_knight"}
        ),
    )
    assert [vf.vf_id for vf in renowned] == ["vf_brother_knight", "vf_templar_prestige"]
    # Office Holder is a second Social Status, which a companion here can't
    # take with the rank.
    office = [
        *renowned,
        VirtueFlawInstance("vf_templar_office_holder"),
        *(VirtueFlawInstance(i) for i in ("vf_mentor", "vf_fear", "vf_lame")),
    ]
    assert "Social Status" in (ct.limit_problem(rank, office) or "")


def test_a_saved_brother_priest_loads_as_the_de_brother_chaplain():
    saved = Character(id="c", name="Hugh", type="companion")
    saved.virtues_flaws = [VirtueFlawInstance("vf_brother_priest")]
    data = asdict(saved)
    loaded = Character.from_dict(data)
    assert [vf.vf_id for vf in loaded.virtues_flaws] == ["vf_brother_chaplain"]


def test_the_templar_brother_priest_sample_takes_the_brother_chaplain():
    priest = ct.find("ct_templar_brother_priest")
    assert priest is not None and priest.statuses == ["vf_brother_chaplain"]


#: The Church's other printed characters, by template id: page, type and
#: the name the Template list shows.
MORE_SAMPLES = {
    "ct_anchoress": (83, "grog", "Anchoress"),
    "ct_beguine": (83, "grog", "Beguine"),
    "ct_priests_wife": (84, "grog", "Priest's Wife"),
    "ct_father_tino_of_gradara": (
        97,
        "mythic companion",
        "Diabolist Abbot - Father Tino of Gradara",
    ),
    "ct_clare_of_assisi": (
        137,
        "companion",
        "Leader of the Poor Sisters - Clare of Assisi",
    ),
    "ct_franciscan_nun": (142, "grog", "Franciscan Nun"),
    "ct_franciscan_friar": (142, "grog", "Franciscan Friar"),
}


def test_the_churchs_other_characters_are_templates_with_their_pages():
    for template_id, (page, kind, name) in MORE_SAMPLES.items():
        template = ct.find(template_id)
        assert template is not None, template_id
        assert (template.book, template.page, template.kind) == ("TC", page, "sample")
        assert (template.type, template.name) == (kind, name), template_id


def test_the_churchs_grog_templates_keep_to_a_grogs_limits():
    for template_id, (_page, kind, _name) in MORE_SAMPLES.items():
        if kind != "grog":
            continue
        template = ct.find(template_id)
        assert template is not None
        values = {f"blank_{b}": "Rhine" for b in ct.blanks(template)}
        chosen = ct.chosen(template, choice_forms.choices_from(template, values))
        assert ct.limit_problem(template, chosen) is None, template_id
        assert template in ct.templates(None, "grog")


def test_the_storyguides_characters_are_kept_as_printed():
    # Tino prints 13 points of Flaws (a Mythic Companion takes 10) and
    # Clare 10 of Virtues to 9 of Flaws: both are the storyguide's, so the
    # Template list says so and their limits aren't checked.
    for template_id in ("ct_father_tino_of_gradara", "ct_clare_of_assisi"):
        template = ct.find(template_id)
        assert template is not None and template.storyguide
        chosen = ct.chosen(template, choice_forms.choices_from(template, {}))
        assert ct.limit_problem(template, chosen) is None
        assert ct.option_label(template).endswith("(TC, for the storyguide)")
    tino = ct.find("ct_father_tino_of_gradara")
    assert tino is not None
    unchecked = replace(tino, storyguide=False)
    chosen = ct.chosen(unchecked, choice_forms.choices_from(unchecked, {}))
    assert "Flaws" in (ct.limit_problem(unchecked, chosen) or "")

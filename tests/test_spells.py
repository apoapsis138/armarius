import build_spell_catalog as build
import pytest

from ars_magica_manager import catalog
from ars_magica_manager import sheet_text as st
from ars_magica_manager import spells as sp
from ars_magica_manager.arts import FORMS, TECHNIQUES
from ars_magica_manager.models import (
    SPELL_SOURCES,
    Character,
    KnownSpell,
    Saga,
    Spell,
)


def _spell(**kwargs) -> Spell:
    fields = {"id": "x", "name": "X", "technique": "Creo", "form": "Ignem"}
    return Spell(**(fields | kwargs))


# ------------------------------------------------------------------ figures


@pytest.mark.parametrize(
    ("level", "expected"), [(1, 1), (5, 1), (10, 2), (12, 3), (20, 4), (None, None)]
)
def test_magnitude(level, expected):
    assert sp.magnitude(_spell(level=level)) == expected


def test_shorthand_places_requisites_after_the_art_they_qualify():
    assert sp.shorthand(_spell(level=20)) == "CrIg 20"
    muto = _spell(technique="Muto", form="Terram", level=15, requisites=["Rego"])
    assert sp.shorthand(muto) == "Mu(Re)Te 15"
    rego = _spell(technique="Rego", form="Corpus", level=10, requisites=["Mentem"])
    assert sp.shorthand(rego) == "ReCo(Me) 10"
    both = _spell(
        technique="Perdo", form="Animal", level=20, requisites=["Rego", "Corpus", "Vim"]
    )
    assert sp.shorthand(both) == "Pe(Re)An(Co/Vi) 20"
    assert sp.shorthand(_spell(technique="Rego", form="Vim")) == "ReVi Gen"


def test_ritual_vis_cost_and_casting_time():
    formulaic = _spell(level=20)
    assert (sp.vis_cost(formulaic), sp.casting_time(formulaic)) == (0, "1 round")
    ritual = _spell(level=20, ritual=True)
    assert (sp.vis_cost(ritual), sp.casting_time(ritual)) == (4, "60 minutes")
    general = _spell(ritual=True)  # the Aegis of the Hearth
    assert sp.vis_cost(general) is None
    assert sp.casting_time(general) == "15 minutes per magnitude"


# ------------------------------------------------------- Range/Duration/Target


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        (
            "R: Voice, D: Mom, T: Ind",
            ("Voice", "Momentary", "Individual", False, []),
        ),
        (
            "R: Touch, D: Year, T: Bound, Ritual",
            ("Touch", "Year", "Boundary", True, []),
        ),
        (
            "R: Touch, D: Moon, T: Group, Ritual; Req: Rego",
            ("Touch", "Moon", "Group", True, ["Rego"]),
        ),
        (
            "R: Eye, D: Mom, T: Ind Req: Perdo, Corpus",
            ("Eye", "Momentary", "Individual", False, ["Perdo", "Corpus"]),
        ),
        (
            "R: Per, D: Conc, T: Part; Requisites: Auram",
            ("Personal", "Concentration", "Part", False, ["Auram"]),
        ),
        (
            "R: Arc, D: Diam, T: Str, Requisite: Rego, InAn 45",
            ("Arcane Connection", "Diameter", "Structure", False, ["Rego"]),
        ),
        (
            "R: Sight, D: Sun & Year, T: Vision.",
            ("Sight", "Sun & Year", "Vision", False, []),
        ),
    ],
)
def test_parse_rdt_reads_every_spelling_on_the_page(line, expected):
    parsed = sp.parse_rdt(line)
    assert (
        parsed["range"],
        parsed["duration"],
        parsed["target"],
        parsed["ritual"],
        parsed["requisites"],
    ) == expected


def test_parse_rdt_ignores_other_lines():
    assert sp.parse_rdt("A 2-foot jet of fire flies from your palms.") is None


def test_parse_requisites_accepts_names_and_abbreviations():
    assert sp.parse_requisites("Au/Im, and Terram") == ["Auram", "Imaginem", "Terram"]
    assert sp.parse_requisites("Rego (for the motion)") == ["Rego"]


def test_catalog_page_link_without_an_href_value_reads_as_empty():
    page = build._Flatten()
    page.feed("<table><tr><td><a href>Pilum of Fire</a></td></tr></table>")
    assert page.events == [("cell", "Pilum of Fire", [("", "Pilum of Fire")])]


# ------------------------------------------------------------ where they live


def test_find_spell_looks_in_the_catalog_then_the_saga_then_the_magi():
    saga = Saga(
        id="s",
        name="S",
        spells=[_spell(id="saga_spell", name="House Rule")],
        characters=[
            Character(
                id="c",
                name="Leandro",
                type="magus",
                invented_spells=[_spell(id="inv_spell", name="Leandro's Light")],
            )
        ],
    )
    assert sp.find_spell(saga, "spell_pilum_of_fire").name == "Pilum of Fire"
    assert sp.find_spell(saga, "saga_spell").name == "House Rule"
    assert sp.find_spell(saga, "inv_spell").name == "Leandro's Light"
    assert sp.find_spell(saga, "nope") is None
    assert sp.find_spell(saga, None) is None
    ids = sp.all_spell_ids(saga)
    assert {"spell_pilum_of_fire", "saga_spell", "inv_spell"} <= ids


# ------------------------------------------------------------------ the catalog


def test_the_catalog_loads_with_valid_arts_and_unique_ids():
    spells = catalog.load_spell_catalog()
    assert len(spells) > 400
    assert len({s.id for s in spells}) == len(spells)
    for spell in spells:
        assert spell.technique in TECHNIQUES, spell.name
        assert spell.form in FORMS, spell.name
        assert all(r in TECHNIQUES or r in FORMS for r in spell.requisites)
        assert spell.source in SPELL_SOURCES, spell.name
        if not spell.details_missing:
            assert spell.range and spell.duration and spell.target, spell.name


def test_the_catalog_has_the_well_known_spells_right():
    by_id = catalog.load_spell_catalog_by_id()
    pilum = by_id["spell_pilum_of_fire"]
    assert (sp.shorthand(pilum), pilum.range, pilum.base_level) == (
        "CrIg 20",
        "Voice",
        10,
    )
    aegis = by_id["spell_aegis_of_the_hearth"]
    assert (aegis.level, aegis.ritual, aegis.target) == (None, True, "Boundary")
    healing = by_id["spell_the_chirurgeon_s_healing_touch"]
    assert (healing.level, healing.ritual) == (20, True)
    assert by_id["spell_eyes_of_the_cat"].requisites == ["Animal"]
    assert {s.source for s in by_id.values()} >= {"ArM5", "HoHTL", "TMRE"}


# --------------------------------------------------------------- the builder

_PAGE = """
<table>
<tr><th>Form \\ Technique</th><th>Creo</th><th>Intellego</th><th>Muto</th>
<th>Perdo</th><th>Rego</th></tr>
<tr><th>Ignem</th>
<td><a href="#Pilum_of_Fire">Pilum of Fire 20</a><br>
<a href="#Ball_of_Flame">Ball of FlameBall of Flame 35</a></td>
<td><a href="#Exactly_to_Warm">Excatly To Warm 5</a></td>
<td></td><td><a href="#Lost_Spell">The Lost Spell 15</a></td>
<td><a href="#Ward_Against_Heat">Ward Against Heat Gen</a></td></tr>
</table>
<div class="mw-heading mw-heading2"><h2 id="Ignem_Spells">Ignem Spells</h2></div>
<div class="mw-heading mw-heading3"><h3 id="Creo_Ignem">Creo Ignem Spells</h3></div>
<div class="mw-heading mw-heading4"><h4 id="Pilum_of_Fire">Pilum of Fire</h4></div>
<p>R: Voice, D: Mom, T: Ind</p>
<p>A jet of fire flies from your palms.</p>
<p>(Base 10, +2 Voice)</p>
<p>A variant Potent Spell is given in TMRE.</p>
<p>Level 25</p>
<div class="mw-heading mw-heading4"><h4 id="Level_55">Level 55</h4></div>
<div class="mw-heading mw-heading4"><h4 id="x1">Ball of Flame (CrIg 35)</h4></div>
<p>R: Voice, D: Mom, T: Ind, Ritual; Req: Rego</p>
<p>A great ball of flame.</p>
<p>Source: HoHS.</p>
<div class="mw-heading mw-heading4"><h4 id="Unlisted">The Unlisted Flame</h4></div>
<p>R: Touch, D: Sun, T: Ind</p>
<p>Not in the index.</p>
<p>(Base 3, +1 Touch, +2 Sun)</p>
<div class="mw-heading mw-heading3"><h3 id="Intellego_Ignem">Intellego Ignem</h3></div>
<div class="mw-heading mw-heading4"><h4 id="x2">Exactly To Warm</h4></div>
<p>R: Per, D: Conc, T: Ind</p>
<p>Senses warmth.</p>
<div class="mw-heading mw-heading3"><h3 id="Rego_Ignem">Rego Ignem Spells</h3></div>
<div class="mw-heading mw-heading4"><h4 id="Ward_Against_Heat">Ward Against Heat</h4></div>
<p>R: Touch, D: Sun, T: Ind</p>
<p>(As ward guideline)</p>
<p>Protects from fire.</p>
"""


def test_the_builder_matches_the_index_to_the_page_and_ignores_variant_levels():
    spells, report = build.parse_page(_PAGE)
    by_name = {s["name"]: s for s in spells}
    assert set(by_name) == {
        "Pilum of Fire",
        "Ball of Flame",
        "The Unlisted Flame",
        "Exactly To Warm",
        "Ward Against Heat",
        "The Lost Spell",
    }
    pilum = by_name["Pilum of Fire"]
    assert (pilum["level"], pilum["base_level"], pilum["source"]) == (20, 10, "ArM5")
    assert "variant Potent Spell" in pilum["description"]
    ball = by_name["Ball of Flame"]  # a doubled index name and a "(CrIg 35)" tag
    assert (ball["level"], ball["ritual"], ball["requisites"], ball["source"]) == (
        35,
        True,
        ["Rego"],
        "HoHS",
    )
    # Matched to the index despite its typo; the heading's spelling wins.
    assert (
        by_name["Exactly To Warm"]["technique"],
        by_name["Exactly To Warm"]["level"],
    ) == (
        "Intellego",
        5,
    )
    assert by_name["Ward Against Heat"]["level"] is None  # General
    # Not in the index: level from its Base line (3 -> 4 -> 5 -> 10).
    assert by_name["The Unlisted Flame"]["level"] == 10
    assert report["not_in_index"] == ["The Unlisted Flame"]
    # In the index with no section: kept, details missing, Arts from the grid.
    lost = by_name["The Lost Spell"]
    assert (lost["technique"], lost["form"], lost["level"]) == ("Perdo", "Ignem", 15)
    assert lost["details_missing"] is True
    assert report["details_missing"] == ["The Lost Spell"]
    assert len({s["id"] for s in spells}) == len(spells)


# ------------------------------------------------------------ the list view


def _saga_with_own_spell() -> tuple[Saga, Spell]:
    own = _spell(
        id="saga_candle", name="Candle of Truth", technique="Intellego", level=5
    )
    return Saga(id="s", name="S", spells=[own]), own


def test_filters_narrow_the_list_and_combine():
    saga, own = _saga_with_own_spell()
    everything = sp.all_spells(saga)
    assert everything[-1] is own
    names = lambda **f: [s.name for s in sp.filter_spells(saga, everything, **f)]
    assert names(text="pilum") == ["Pilum of Fire"]
    assert names(text="FIRE pilum") == ["Pilum of Fire"]  # every word, any case
    assert names(source=sp.OWN_SOURCE) == ["Candle of Truth"]
    assert "Candle of Truth" not in names(source="ArM5")
    rituals = sp.filter_spells(saga, everything, ritual=True)
    assert rituals and all(s.ritual for s in rituals)
    # A Form also matches a requisite: Eyes of the Cat is MuCo(An).
    assert "Eyes of the Cat" in names(form="Animal")
    ranged = sp.filter_spells(saga, everything, min_level=30, max_level=30)
    assert {s.level for s in ranged} == {30, None}  # General passes any range
    both = names(technique="Creo", form="Ignem", max_level=20)
    assert "Pilum of Fire" in both and "Ball of Abysmal Flame" not in both


def test_rows_line_up_with_the_header_and_mark_the_saga_own():
    saga, own = _saga_with_own_spell()
    header = sp.table_header()
    pilum = catalog.load_spell_catalog_by_id()["spell_pilum_of_fire"]
    row = sp.row_label(saga, pilum)
    assert header.index("Arts") - 2 == row.index("CrIg")
    assert header.index("Source") - 2 == row.index("ArM5")
    assert "Voice/Mom/Ind" in row
    assert sp.row_label(saga, own).rstrip().endswith("Saga")
    aegis = catalog.load_spell_catalog_by_id()["spell_aegis_of_the_hearth"]
    assert "  Gen  " in sp.row_label(saga, aegis)


def test_details_panel_shows_the_figures_and_where_the_spell_is_from():
    saga, own = _saga_with_own_spell()
    healing = catalog.load_spell_catalog_by_id()["spell_the_chirurgeon_s_healing_touch"]
    text = sp.detail_text(saga, healing)
    assert "CrCo 20" in text and "Ritual" in text
    assert "Level:[/] 20 (magnitude 4)" in text
    assert "Vis:[/] 4 pawn(s)" in text and "60 minutes" in text
    assert "catalog spell, read-only" in text
    assert "press e to edit it" in sp.detail_text(saga, own)
    aegis = catalog.load_spell_catalog_by_id()["spell_aegis_of_the_hearth"]
    assert "General (cast at any level)" in sp.detail_text(saga, aegis)


# ---------------------------------------------------------------- CSV import


def test_the_example_csv_imports_cleanly():
    result = sp.parse_spells_csv(sp.EXAMPLE_CSV)
    assert result.skipped == [] and result.unused_columns == []
    palm, ward = result.spells
    assert (sp.shorthand(palm), palm.range, palm.duration, palm.ritual) == (
        "CrIg 5",
        "Touch",
        "Diameter",
        False,
    )
    assert (sp.shorthand(ward), ward.ritual, ward.target, ward.source) == (
        "ReVi(Me) Gen",
        True,
        "Boundary",
        "House rule",
    )
    assert all(s.id == "" for s in result.spells)  # ids come on import


def test_spell_rows_accept_abbreviations_and_report_bad_rows():
    text = (
        "Name,Technique,Form,Level,Requisites,Range,Duration,Target,Ritual,Shelf\n"
        "Short,cr,ig,10,re,Per,Mom,Ind,,3\n"
        ",Creo,Ignem,5,,,,,,\n"
        "Bad Art,Creo,Fire,5,,,,,,\n"
        "Bad Level,Creo,Ignem,high,,,,,,\n"
        "Bad Req,Creo,Ignem,5,Rego Magic,,,,,\n"
        "Bad Ritual,Creo,Ignem,5,,,,,maybe,\n"
        "Zero,Creo,Ignem,0,,,,,,\n"
    )
    result = sp.parse_spells_csv(text)
    (short,) = result.spells
    assert (short.technique, short.form, short.requisites) == (
        "Creo",
        "Ignem",
        ["Rego"],
    )
    assert (short.range, short.duration, short.target) == (
        "Personal",
        "Momentary",
        "Individual",
    )
    assert result.unused_columns == ["shelf"]
    assert result.skipped == [
        "Row 3: no name.",
        "Row 4 (Bad Art): unknown Form 'Fire'.",
        "Row 5 (Bad Level): Level 'high' isn't a number or Gen.",
        "Row 6 (Bad Req): requisites 'Rego Magic' aren't all Arts.",
        "Row 7 (Bad Ritual): Ritual 'maybe' isn't yes or no.",
        "Row 8 (Zero): a Level below 1.",
    ]


def test_a_spell_csv_needs_name_technique_and_form_columns():
    with pytest.raises(ValueError, match="no technique, form column"):
        sp.parse_spells_csv("name,level\nX,5\n")


def test_the_spell_import_preview():
    result = sp.parse_spells_csv(
        sp.EXAMPLE_CSV
        + "Palm of Warming Flame,Creo,Ignem,5,,,,,,,,\nOops,Creo,Nope,5\n"
    )
    preview = sp.spell_import_preview(result, "mine.csv", {"Pilum of Fire"})
    assert preview.startswith(
        "Import 3 spells from [b]mine.csv[/] into the saga's own spells?"
    )
    assert "1 has the same name as another spell" in preview
    assert "1 General-level" in preview
    assert "1 row(s) will be skipped" in preview


def test_spell_names_match_in_any_case_and_spacing():
    assert sp.name_key("  Palm of  Warming Flame") == "palm of warming flame"
    assert sp.name_key("Hermes’ Portal") == sp.name_key("hermes' portal")


def test_add_own_spell_uses_a_saga_prefixed_id():
    saga = Saga(id="s", name="S")
    spell = sp.add_own_spell(saga, "Pilum of Fire", "Creo", "Ignem")
    again = sp.add_own_spell(saga, "Pilum of Fire", "Creo", "Ignem")
    assert (spell.id, again.id) == ("saga_pilum_of_fire", "saga_pilum_of_fire_2")
    assert saga.spells == [spell, again]
    assert (spell.technique, spell.form) == ("Creo", "Ignem")


def test_add_imported_spells_gives_each_a_unique_own_id():
    saga = Saga(id="s", name="S")
    spells = [_spell(id="", name="Glow"), _spell(id="", name="Glow")]
    sp.add_imported_spells(saga, spells)
    assert [s.id for s in saga.spells] == ["saga_glow", "saga_glow_2"]


def test_known_spell_rows_show_catalog_and_own_spells_mastery_and_lost_ids():
    saga = Saga(id="s", name="S", spells=[_spell(id="own1", name="Own Spell")])
    magus = Character(id="m", name="M", type="magus")
    magus.spells_known = [
        KnownSpell(spell_id="spell_aegis_of_the_hearth"),
        KnownSpell(spell_id="own1", mastery_score=2),
        KnownSpell(spell_id="gone"),
    ]
    rows = st.known_spell_rows(saga, magus)
    assert [index for index, _ in rows] == [0, 1, 2]
    aegis, own, gone = (label for _, label in rows)
    assert "Aegis of the Hearth" in aegis and "Ritual" in aegis
    assert "Own Spell" in own and own.endswith("  [b]Mastery 2[/]")
    assert gone == "gone (unknown spell)"

"""The character Virtue/Flaw catalog, reviewed against
reference/virtues-and-flaws-reference.md, and the repeat rules it drives."""

import re
from collections import Counter

import pytest

from ars_magica_manager import catalog, sourcebooks
from ars_magica_manager import sheet_text as st
from ars_magica_manager.models import (
    VIRTUE_FLAW_AUDIENCES,
    VirtueFlawDef,
    VirtueFlawInstance,
)

#: The sources an entry may name (the DE and the open-content books read for
#: the review, plus the books the index says also print it).
KNOWN_BOOKS = {
    # The DE and the open-content books
    *("DE", "HoH:TL", "HoH:MC", "TMRE", "App", "RoP:M", "RoP:F", "RoP:D"),
    *("RoP:I", "C&G", "LoM", "TC", "GotF", "L&L", "AtD", "TCI", "A&A"),
    *("F&F", "Grogs"),
    # Sanctuary of Ice, the Greater Alps pack's book
    "SoI",
    # Secrets in Sand, Blood and Sand's free web supplement
    "SiS",
    # Books only the index was read for
    *("AnM", "Ant", "BCoC", "TC&TC", "Gr", "HMRE", "HP", "HoH:S"),
    *("LoH", "MoH", "RM", "TSE", "ToME"),
    # The hedge traditions' books
    *("AM", "BS&S", "LotN", "TtA"),
}


def by_id() -> dict[str, VirtueFlawDef]:
    return catalog.load_virtue_flaw_catalog_by_id()


def test_catalog_counts_after_adding_the_supplements():
    # 625 DE entries, the 2 the catalog had lost, 33 Major versions of
    # "Major or Minor" DE entries, and 440 open-content supplement entries
    # (423 definitions, 17 of them at both tiers), plus 13 Virtues from
    # Faith & Flame (11 definitions, 2 of them at both tiers), plus 2 from
    # The Sundered Eagle, plus Hedge Magic RE's 101 hedge Virtues and Flaws,
    # plus the other books' hedge traditions' 115, plus Ancient Magic's 6
    # integration Virtues, plus the 3 Grogs entries the DE doesn't have,
    # plus Realms of Power: The Divine's Perfectus Mythic Companion Virtue,
    # plus Secrets in Sand's 2 Virtues and 2 Flaws, plus The Cradle and the
    # Crescent's Jinni, plus Legends of Hermes's 3 realm-insight Virtues,
    # plus The Sundered Eagle's Mythic Blood (Gigantes) and 7 Maledictions,
    # plus Magi of Hermes's Hermetic Metamorphosis, The Cradle and the
    # Crescent's four Solomonic breakthrough Virtues and Societates's Miles,
    # less The Church's Brother-Priest, which is the DE's Brother Chaplain.
    entries = catalog.load_virtue_flaw_catalog()
    assert len(entries) == 1373
    counts = Counter(e.type for e in entries)
    assert counts == {"Virtue": 807, "Flaw": 479, "Quality": 67, "Inferiority": 20}
    assert sum(e.source == "DE" for e in entries) == 660


def test_every_entry_names_known_source_books():
    for e in catalog.load_virtue_flaw_catalog():
        books = e.source.split("; ")
        assert books and set(books) <= KNOWN_BOOKS, (e.id, e.source)


def test_secrets_in_sand_adds_the_islamic_tradition_s_entries():
    vfs = by_id()
    expected = {
        "vf_islamic_magic": ("Islamic Magic", "Virtue", "Minor", 1),
        "vf_interfaith_magic": ("Interfaith Magic", "Virtue", "Major", 3),
        "vf_poorly_meshed_hermetic_islamic_magic": (
            "Poorly-Meshed Hermetic-Islamic Magic",
            "Flaw",
            "Minor",
            -1,
        ),
        "vf_the_faerie_problem": ("The Faerie Problem", "Flaw", "Minor", -1),
    }
    for vf_id, (name, kind, tier, cost) in expected.items():
        e = vfs[vf_id]
        assert (e.name, e.type, e.tier, e.cost) == (name, kind, tier, cost)
        assert e.category == "Hermetic" and e.source == "SiS"
        assert e.summary and e.description
    assert {e.id for e in vfs.values() if e.source == "SiS"} == set(expected)


def test_the_jinni_free_virtue_is_for_spirits_of_its_book():
    jinni = by_id()["vf_jinni"]
    assert (jinni.name, jinni.type, jinni.tier, jinni.cost) == (
        "Jinni",
        "Virtue",
        "Free",
        0,
    )
    assert jinni.source == "TC&TC" and jinni.summary and jinni.description
    assert set(jinni.audience) == {"faerie", "magic being"}
    assert sourcebooks.in_play(jinni.source, ["TC&TC"])
    assert not sourcebooks.in_play(jinni.source, [])


def test_the_wrongly_filed_entries_are_fixed():
    vfs = by_id()
    assert vfs["vf_folk_magic"].type == "Virtue"
    assert vfs["vf_folk_magic"].cost == 1
    assert vfs["vf_vulnerable_to_folk_tradition"].type == "Flaw"
    assert vfs["vf_vulnerable_to_folk_tradition"].cost == -1
    assert vfs["vf_role_bound"].name == "Bound to {role}"


def test_the_entries_swallowed_into_others_are_split_out():
    vfs = by_id()
    assert vfs["vf_hunchback"].type == "Flaw"
    assert vfs["vf_prestigious_student"].type == "Virtue"
    assert "Hunchback" not in vfs["vf_humble"].description
    assert "Prestigious Student" not in vfs["vf_premonitions"].description
    assert "Based on the material" not in vfs["vf_wrathful"].description
    assert not vfs["vf_withstand_casting"].description.endswith("Flaws")
    assert "A candle flame (Ignem)" in vfs["vf_study_bonus"].description
    assert "an additional head" in vfs["vf_form_monstrosity"].description


def test_major_or_minor_entries_have_a_major_version():
    vfs = by_id()
    for base in ("vf_ambitious", "vf_pious", "vf_outsider", "vf_potent_magic"):
        minor, major = vfs[base], vfs[base + "_major"]
        assert (minor.tier, major.tier) == ("Minor", "Major")
        assert minor.name == major.name
        assert abs(major.cost) == 3


def test_a_second_printed_type_is_kept():
    vfs = by_id()
    assert vfs["vf_demonic_blood"].category_label == "Supernatural, Tainted"
    assert vfs["vf_adept_laboratory_student"].category_label == "Hermetic"


@pytest.mark.parametrize(
    ("vf_id", "max_count", "per_parameter", "parameters"),
    [
        ("vf_affinity_with_ability", None, 1, ["ability"]),
        ("vf_affinity_with_art", 2, 1, ["art"]),
        ("vf_puissant_art", 2, 1, ["art"]),
        ("vf_great_characteristic", None, 2, ["characteristic"]),
        ("vf_poor_characteristic", None, 2, ["characteristic"]),
        ("vf_weak_characteristics", 2, 1, []),
        ("vf_improved_characteristics", None, 1, []),
        ("vf_performance_magic", None, 1, ["ability"]),
        ("vf_greater_power", None, None, ["power"]),
        ("vf_folk_magic", 4, 1, ["category"]),
    ],
)
def test_repeatable_entries(vf_id, max_count, per_parameter, parameters):
    e = by_id()[vf_id]
    assert e.repeatable
    assert e.max_count == max_count
    assert e.max_per_parameter == per_parameter
    assert e.parameters == parameters


def test_decided_not_repeatable():
    vfs = by_id()
    # True Faith is taken once; its Score rises by other means. Beloved
    # Rival's "both" is its Minor and Major entries, not two copies.
    for vf_id in ("vf_true_faith", "vf_beloved_rival", "vf_beloved_rival_major"):
        assert not vfs[vf_id].repeatable, vf_id


def test_non_human_entries_name_their_audience():
    entries = catalog.load_virtue_flaw_catalog()
    for e in entries:
        assert set(e.audience) <= set(VIRTUE_FLAW_AUDIENCES), e.id
        if e.type in ("Quality", "Inferiority"):
            assert e.audience, e.id
    assert by_id()["vf_affinity_with_art"].audience == []


def test_placeholder_names_match_parameters():
    for e in catalog.load_virtue_flaw_catalog():
        for placeholder in re.findall(r"\{(\w+)\}", e.name):
            assert placeholder in e.parameters, e.id


def _vf(**overrides) -> VirtueFlawDef:
    fields = {
        "id": "vf_test",
        "name": "Test",
        "type": "Virtue",
        "category": "General",
        "tier": "Minor",
        "cost": 1,
    }
    fields.update(overrides)
    return VirtueFlawDef(**fields)


@pytest.mark.parametrize(
    "overrides",
    [
        {"max_count": 2},  # a max needs repeatable
        {"type": "Flaw"},  # a Flaw's cost is <= 0
        {"type": "Quality", "cost": -1},  # a Quality's is >= 0
        {"type": "Boon"},
        {"audience": ["dragon"]},
        {"repeatable": True, "max_per_parameter": 0},
    ],
)
def test_bad_entries_fail_at_load(overrides):
    with pytest.raises(ValueError):
        _vf(**overrides)


def test_offerable_hides_a_taken_entry_unless_repeatable():
    once = _vf()
    twice = _vf(id="vf_twice", repeatable=True, max_count=2)
    free = _vf(id="vf_free", repeatable=True)
    one = [VirtueFlawInstance("vf_test"), VirtueFlawInstance("vf_twice")]
    assert not catalog.virtue_flaw_offerable(once, one)
    assert catalog.virtue_flaw_offerable(twice, one)
    assert not catalog.virtue_flaw_offerable(
        twice, one + [VirtueFlawInstance("vf_twice")]
    )
    assert catalog.virtue_flaw_offerable(free, [VirtueFlawInstance("vf_free")] * 5)
    assert catalog.virtue_flaw_offerable(once, [])


def test_repeat_refusal_per_parameter():
    art = by_id()["vf_affinity_with_art"]
    creo = VirtueFlawInstance("vf_affinity_with_art", {"art": "creo"})
    assert catalog.virtue_flaw_repeat_refusal(art, [], {"art": "creo"}) == ""
    assert catalog.virtue_flaw_repeat_refusal(art, [creo], {"art": "rego"}) == ""
    refusal = catalog.virtue_flaw_repeat_refusal(art, [creo], {"art": "creo"})
    assert "Affinity with Creo" in refusal
    rego = VirtueFlawInstance("vf_affinity_with_art", {"art": "rego"})
    assert "at most 2 times" in catalog.virtue_flaw_repeat_refusal(
        art, [creo, rego], {"art": "ignem"}
    )
    great = by_id()["vf_great_characteristic"]
    strength = VirtueFlawInstance("vf_great_characteristic", {"characteristic": "str"})
    params = {"characteristic": "str"}
    assert catalog.virtue_flaw_repeat_refusal(great, [strength], params) == ""
    assert catalog.virtue_flaw_repeat_refusal(great, [strength] * 2, params)
    power = by_id()["vf_greater_power"]
    flight = VirtueFlawInstance("vf_greater_power", {"power": "flight"})
    assert (
        catalog.virtue_flaw_repeat_refusal(power, [flight] * 3, {"power": "flight"})
        == ""
    )


def test_repeat_refusal_for_an_entry_taken_once():
    humble = by_id()["vf_humble"]
    refusal = catalog.virtue_flaw_repeat_refusal(
        humble, [VirtueFlawInstance("vf_humble")], {}
    )
    assert refusal == "Humble may only be taken once."


def test_a_parameter_without_a_placeholder_follows_the_name():
    vfs = by_id()
    label = catalog.describe_virtue_flaw(
        VirtueFlawInstance("vf_deficient_technique", {"technique": "creo"}), vfs
    )
    assert label == "Deficient Technique (Creo)"
    label = catalog.describe_virtue_flaw(
        VirtueFlawInstance("vf_affinity_with_art", {"art": "creo"}), vfs
    )
    assert label == "Affinity with Creo"


def test_qualities_list_with_virtues_and_inferiorities_with_flaws():
    quality = next(e for e in catalog.load_virtue_flaw_catalog() if e.type == "Quality")
    inferiority = next(
        e for e in catalog.load_virtue_flaw_catalog() if e.type == "Inferiority"
    )
    instances = [VirtueFlawInstance(quality.id), VirtueFlawInstance(inferiority.id)]
    assert [i for i, _ in st.vf_rows(instances, "Virtue")] == [0]
    assert [i for i, _ in st.vf_rows(instances, "Flaw")] == [1]
    assert st.vf_points(instances, "Virtue") == abs(quality.cost)
    assert st.vf_points(instances, "Flaw") == abs(inferiority.cost)


@pytest.mark.parametrize(
    ("vf_id", "text"),
    [
        ("vf_humble", ""),
        (
            "vf_affinity_with_art",
            "May be taken up to 2 times, for a different Art each time.",
        ),
        (
            "vf_great_characteristic",
            "May be taken more than once, at most 2 times for the same Characteristic.",
        ),
        ("vf_improved_characteristics", "May be taken more than once."),
        ("vf_greater_power", "May be taken more than once."),
    ],
)
def test_repeat_text(vf_id, text):
    assert st.vf_repeat_text(by_id()[vf_id]) == text


def test_details_panel_shows_types_repeats_and_source():
    instances = [VirtueFlawInstance("vf_affinity_with_art", {"art": "creo"})]
    text = st.vf_info_text(instances, 0)
    assert "May be taken up to 2 times" in text
    assert text.rstrip().endswith("Source: DE[/]")
    demonic = st.vf_info_text([VirtueFlawInstance("vf_demonic_blood")], 0)
    assert "Supernatural, Tainted" in demonic

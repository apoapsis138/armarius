"""The lab sheet's list rows and details-panel text (laboratories.py)."""

from support import strip_markup

from ars_magica_manager import catalog
from ars_magica_manager import laboratories as lab_text
from ars_magica_manager.models import (
    LAB_SPECIALIZATIONS,
    DiaryEntry,
    LabCharacteristics,
    LabFeature,
    Laboratory,
    LabSpecialtyEntry,
    LabSpecialtyGrant,
    NamedDescription,
    VirtueFlawInstance,
)


def _lab(*vf_ids: str, **characteristics: int) -> Laboratory:
    return Laboratory(
        id="lab1",
        covenant_id=None,
        name="Tower",
        characteristics=LabCharacteristics(**characteristics),
        virtues_flaws=[VirtueFlawInstance(vf_id=i) for i in vf_ids],
    )


def test_vf_rows_split_virtues_from_flaws_keeping_true_indexes():
    lab = _lab("labvf_lesser_focus", "labvf_greater_feature")
    assert lab_text.vf_rows(lab, "Virtue") == [(1, "Greater Feature (Major)")]
    assert lab_text.vf_rows(lab, "Flaw") == [(0, "Lesser Focus (Minor)")]


def test_vf_info_text_shows_category_tier_points_and_characteristics():
    lab = _lab("labvf_greater_feature", "labvf_superior_construction")
    text = strip_markup(lab_text.vf_info_text(lab, 0))
    assert text.splitlines()[:4] == [
        "Name: Greater Feature",
        "Category: Structure",
        "Tier: Major Virtue (3 pts)",
        "Characteristics: Aesthetics +2",
    ]
    assert "Rules:" in text
    free = strip_markup(lab_text.vf_info_text(lab, 1))
    assert "Tier: Free Virtue (Free)" in free
    assert "Characteristics: Safety +1, Aesthetics +1" in free
    assert "Select a Virtue or Flaw" in lab_text.vf_info_text(lab, None)


def test_vf_warnings_flag_over_capacity_and_a_second_focus():
    assert lab_text.vf_warnings(_lab()) == ""
    # Greater Feature costs 3; Size + Refinement is 0 -> over by 3.
    over = lab_text.vf_warnings(_lab("labvf_greater_feature"))
    assert over == (
        "[$text-error]✘ Over capacity by 3 "
        "(Virtues less Flaws may total Size + Refinement = 0).[/]"
    )
    # ...but not once Size makes room for it.
    assert lab_text.vf_warnings(_lab("labvf_greater_feature", size=3)) == ""
    # Two Focus Flaws (net -4 points: well inside capacity).
    two = lab_text.vf_warnings(_lab("labvf_lesser_focus", "labvf_greater_focus"))
    assert (
        two == "[$text-error]✘ 2 Focus Flaws: a laboratory may only have one Focus.[/]"
    )


def test_named_info_text_renders_emphasis_and_escapes_the_name():
    rooms = [NamedDescription(name="[Vault]", description="**Cold**")]
    assert lab_text.named_rows(rooms) == [(0, "\\[Vault]")]
    assert (
        lab_text.named_info_text(rooms, 0, "a Room") == "[b]\\[Vault][/]\n\n[b]Cold[/b]"
    )
    empty = [NamedDescription(name="Hall")]
    assert "(no description)" in lab_text.named_info_text(empty, 0, "a Room")
    assert "Select a Room" in lab_text.named_info_text(rooms, None, "a Room")


def test_raw_vis_rows_are_sorted_by_art():
    lab = _lab()
    lab.raw_vis = {"vim": 3, "aquam": 1}
    assert lab_text.raw_vis_rows(lab) == [
        (0, "Aquam: 1 pawn(s)"),
        (1, "Vim: 3 pawn(s)"),
    ]


def test_diary_rows_line_up_the_names_and_dash_a_missing_activity():
    diary = [
        DiaryEntry(year=1220, season="Spring", name="Built"),
        DiaryEntry(year=1221, season="Winter", name="Pilum", activity="Invent Spell"),
    ]
    assert lab_text.diary_rows(diary) == [
        (0, "1220 Spring  -             Built"),
        (1, "1221 Winter  Invent Spell  Pilum"),
    ]
    assert lab_text.diary_rows([]) == []


def test_diary_info_text_shows_date_activity_and_details():
    diary = [DiaryEntry(year=1220, season="Autumn", name="Moved in", details="*Boxes*")]
    assert lab_text.diary_info_text(diary, 0).splitlines() == [
        "[b]Moved in[/]",
        "[b]Date:[/] Autumn 1220",
        "[b]Activity:[/] (not set)",
        "",
        "[i]Boxes[/i]",
    ]


# -- Specializations (STORY-307) --


def _with(*entries: tuple[str, int], dropped: tuple[str, ...] = ()) -> Laboratory:
    lab = _lab()
    lab.specialties = [LabSpecialtyEntry(n, p, "Notes") for n, p in entries]
    lab.dropped_specializations = list(dropped)
    return lab


def test_old_free_text_specialties_migrate_to_entries():
    lab = Laboratory.from_dict(
        {
            "id": "lab1",
            "covenant_id": None,
            "name": "Tower",
            "specialties": ["Terram +1", "ignem", "Vis Extraction -2", "Big windows"],
        }
    )
    assert lab.specialties == [
        LabSpecialtyEntry("Terram", 1, "(from old notes)"),
        LabSpecialtyEntry("Ignem", 1, "(from old notes)"),
        LabSpecialtyEntry("Vis Extraction", -2, "(from old notes)"),
        LabSpecialtyEntry("", 0, "Big windows"),
    ]
    assert lab.dropped_specializations == []
    assert lab.sanctum_marked is False
    # ...and the text that named nothing asks to be fixed.
    assert strip_markup(lab_text.specialty_entry_rows(lab)[3][1]) == (
        "☞ needs a Specialization  Big windows"
    )


def test_scores_sum_every_source_and_keep_where_they_came_from():
    lab = _lab()
    lab.specialties = [
        LabSpecialtyEntry("Terram", 1, "Subterranean"),
        LabSpecialtyEntry("Terram", 2, "Old notes"),
        LabSpecialtyEntry("Spells", 1, ""),
    ]
    scores = {s.name: s for s in lab_text.specialization_scores(lab)}
    assert scores["Terram"].points == 3
    assert scores["Terram"].sources == (("Subterranean", 1), ("Old notes", 2))
    assert scores["Spells"].sources == (("(no source given)", 1),)
    # Activities come before Arts.
    assert list(scores) == ["Spells", "Terram"]


def test_grid_rows_group_and_dim_what_does_not_count():
    lab = _with(("Items", 1), ("Ignem", 2), ("Perdo", -1), dropped=("Ignem",))
    assert lab_text.specialization_rows(lab) == [
        (None, "Activity (1 of 2)"),
        (LAB_SPECIALIZATIONS.index("Items"), "Items  +1"),
        (None, "Art (0 of 4)"),
        (LAB_SPECIALIZATIONS.index("Perdo"), "[dim]Perdo  -1[/]"),
        (LAB_SPECIALIZATIONS.index("Ignem"), "[dim strike]Ignem  +2[/]"),
    ]
    assert lab_text.counted_specializations(lab) == {"Items"}


def test_toggle_refuses_a_zero_score_and_turning_on_over_a_cap():
    lab = _with(("Creo", 1), ("Rego", 1), ("Muto", 1), ("Vim", 0), dropped=("Muto",))
    assert lab_text.toggle_specialization(lab, "Vim") == (
        "Vim scores 0 or less, so it doesn't count either way."
    )
    assert lab_text.toggle_specialization(lab, "Muto") == (
        "Can't turn Muto on: 2 Technique Specializations already count, "
        "the most a laboratory can have. Turn one off first."
    )
    assert lab.dropped_specializations == ["Muto"]
    assert lab_text.toggle_specialization(lab, "Rego") is None
    assert lab_text.toggle_specialization(lab, "Muto") is None
    assert lab.dropped_specializations == ["Rego"]


def test_caps_allow_four_arts_and_two_activities():
    lab = _with(
        ("Spells", 1), ("Items", 1), ("Texts", 1),
        ("Creo", 1), ("Ignem", 1), ("Aquam", 1), ("Vim", 1), ("Corpus", 1),
        dropped=("Texts", "Corpus"),
    )  # fmt: skip
    headers = [label for i, label in lab_text.specialization_rows(lab) if i is None]
    assert headers == ["Activity (2 of 2)", "Art (4 of 4)"]
    assert lab_text.toggle_specialization(lab, "Texts") is not None
    assert lab_text.toggle_specialization(lab, "Corpus") is not None
    # Over a cap (e.g. an old save) shows in the theme's error colour.
    lab.dropped_specializations = []
    headers = [label for i, label in lab_text.specialization_rows(lab) if i is None]
    assert headers == [
        "Activity [$text-error](3 of 2)[/]",
        "Art [$text-error](5 of 4)[/]",
    ]
    # An empty lab still shows both headers.
    assert lab_text.specialization_rows(_lab()) == [
        (None, "Activity (0 of 2)"),
        (None, "Art (0 of 4)"),
    ]


def test_reconcile_turns_off_newcomers_over_a_cap_and_forgets_stale_names():
    lab = _with(("Spells", 1), ("Items", 1), dropped=("Longevity Rituals",))
    before = lab_text.counted_specializations(lab)
    lab.specialties.append(LabSpecialtyEntry("Texts", 1))
    lab_text.reconcile_dropped(lab, before)
    # Texts is new and there's no room; Longevity Rituals has no points now.
    assert lab.dropped_specializations == ["Texts"]
    # Room for a newcomer: it stays on.
    lab.specialties.append(LabSpecialtyEntry("Creo", 2))
    lab_text.reconcile_dropped(lab, before)
    assert "Creo" in lab_text.counted_specializations(lab)
    # One that already counted stays on even if a newcomer comes first.
    lab = _with(("Items", 1), ("Spells", 1))
    before = {"Spells", "Teaching"}
    lab.specialties.insert(0, LabSpecialtyEntry("Teaching", 1))
    lab_text.reconcile_dropped(lab, before)
    assert lab.dropped_specializations == ["Items"]


def test_specialization_info_text_lists_sources_and_status():
    lab = _with(("Terram", 1), ("Terram", 1), dropped=("Terram",))
    text = strip_markup(
        lab_text.specialization_info_text(lab, LAB_SPECIALIZATIONS.index("Terram"))
    )
    assert text.splitlines() == [
        "Terram +2: turned off (Space turns it back on)",
        "",
        "Sources:",
        "  +1  Notes",
        "  +1  Notes",
    ]
    assert (
        lab_text.specialization_info_text(lab, None) == lab_text.ATTRIBUTES_PANEL_HINT
    )
    # A Technique's panel says how many Techniques count.
    lab = _with(("Creo", 1))
    text = strip_markup(
        lab_text.specialization_info_text(lab, LAB_SPECIALIZATIONS.index("Creo"))
    )
    assert text.splitlines()[-1] == "Techniques counting: (1 of 2)"


def test_specialty_entry_and_raw_vis_panels():
    lab = _with(("Terram", 1))
    lab.specialties.append(LabSpecialtyEntry("", 0, "Big windows"))
    assert strip_markup(lab_text.specialty_entry_info_text(lab, 0)).splitlines() == [
        "Terram +1",
        "Source: Notes",
        "",
        "Counts towards Terram in Specializations.",
    ]
    assert "edit it (e)" in lab_text.specialty_entry_info_text(lab, 1)
    lab.raw_vis = {"vim": 1, "aquam": 3}
    assert lab_text.raw_vis_info_text(lab, 0) == "[b]Aquam vis[/]\n3 pawns"
    assert lab_text.raw_vis_info_text(lab, 1) == "[b]Vim vis[/]\n1 pawn"


# -- Features (STORY-308) --


def test_vf_points_count_each_side_on_its_own():
    lab = _lab("labvf_greater_feature", "labvf_gallery", "labvf_cramped", "labvf_empty")
    assert lab_text.vf_points(lab, "Virtue") == 4  # Major 3 + Minor 1
    assert lab_text.vf_points(lab, "Flaw") == 1  # Minor 1 + Free 0


def test_features_title_counts_features_against_feature_virtues():
    lab = _lab("labvf_lesser_feature", "labvf_greater_feature")
    assert lab_text.features_title(lab) == "Features (0 of 2)"
    lab.features = [LabFeature("f", "Cauldron")]
    assert lab_text.features_title(lab) == "Features (1 of 2)"


def test_feature_catalog_has_all_36_and_expands_any_technique():
    features = catalog.load_lab_feature_catalog()
    assert len(features) == 36
    altar = catalog.load_lab_feature_catalog_by_id()["labfeat_altar"]
    assert altar.specializations == (
        "Creo",
        "Intellego",
        "Muto",
        "Perdo",
        "Rego",
        "Vim",
    )
    assert lab_text.feature_options(None) == LAB_SPECIALIZATIONS


def test_old_free_text_features_match_the_catalog_and_take_free_virtues():
    lab = Laboratory.from_dict(
        {
            "id": "lab1",
            "covenant_id": None,
            "name": "Tower",
            "virtues_flaws": [
                {"vf_id": "labvf_lesser_feature"},
                {"vf_id": "labvf_subterranean"},
                {"vf_id": "labvf_greater_feature"},
            ],
            "features": [
                "Large Brass Cauldron",
                "Big windows",
                "Summoning circle of salt",
                "Hanging gardens",
            ],
        }
    )
    lesser, _, greater = lab.virtues_flaws
    assert all(vf.id for vf in lab.virtues_flaws)
    assert [(f.name, f.feature_id, f.virtue_id) for f in lab.features] == [
        ("Large Brass Cauldron", "labfeat_cauldron", lesser.id),
        ("Big windows", "labfeat_window", greater.id),
        ("Summoning circle of salt", "labfeat_summoning_circle", None),
        ("Hanging gardens", None, None),
    ]
    rows = [strip_markup(label) for _, label in lab_text.feature_rows(lab)]
    assert rows == [
        "Large Brass Cauldron  (Cauldron, Lesser)  ☞ 1 point to allocate",
        "Big windows  (Window, Greater)  ☞ 3 points to allocate",
        "Summoning circle of salt  (Summoning Circle)  ☞ needs a Feature Virtue",
        "Hanging gardens  (Custom)  ☞ needs a Feature Virtue",
    ]


def _feature_lab(*vf_ids: str, **feature: object) -> Laboratory:
    lab = _lab()
    lab.virtues_flaws = [
        VirtueFlawInstance(v, id=f"v{n}") for n, v in enumerate(vf_ids)
    ]
    lab.features = [LabFeature(**{"id": "f", "name": "Cauldron", **feature})]
    return lab


def test_focus_needs_the_matching_flaw_and_no_other_focus():
    lab = _feature_lab("labvf_lesser_feature", "labvf_greater_focus", virtue_id="v0")
    feature = lab.features[0]
    assert not lab_text.can_focus(lab, feature, "labvf_lesser_feature")
    assert lab_text.can_focus(lab, feature, "labvf_greater_feature")
    lab.features.append(LabFeature("g", "Other", focus=True))
    assert not lab_text.can_focus(lab, feature, "labvf_greater_feature")
    assert lab_text.can_focus(lab, lab.features[1], "labvf_greater_feature")


def test_feature_points_and_focus_feed_the_specializations():
    lab = _feature_lab(
        "labvf_greater_feature",
        "labvf_greater_focus",
        feature_id="labfeat_cauldron",
        virtue_id="v0",
        allocations=[LabSpecialtyGrant("Ignem", 2), LabSpecialtyGrant("Aquam", 1)],
        focus=True,
        focus_allocations=[LabSpecialtyGrant("Ignem", 3)],
    )
    lab.specialties = [LabSpecialtyEntry("Ignem", -1, "Hearth")]
    ignem = next(s for s in lab_text.specialization_scores(lab) if s.name == "Ignem")
    assert ignem.points == 4
    assert ignem.sources == (
        ("Cauldron (Feature)", 2),
        ("Cauldron (Focus)", 3),
        ("Hearth", -1),
    )
    assert lab_text.feature_problems(lab, lab.features[0]) == [
        "1 Focus point to allocate"
    ]
    text = strip_markup(lab_text.feature_info_text(lab, 0))
    assert text.splitlines()[:6] == [
        "Cauldron",
        "Type: Cauldron",
        "Virtue: Greater Feature (3 points)",
        "Offers: Experimentation, Longevity Rituals, Vis Extraction, Muto, Aquam, "
        "Herbam, Ignem",
        "Points: Ignem +2, Aquam +1",
        "Focus: Ignem +3 (Greater Focus: -2 General Quality on activities it "
        "doesn't aid)",
    ]
    assert "1 Focus point to allocate." in text
    # The V&F panel says what each carries.
    assert "Feature: Cauldron" in strip_markup(lab_text.vf_info_text(lab, 0))
    assert "Focus of: Cauldron" in strip_markup(lab_text.vf_info_text(lab, 1))


def test_prune_drops_a_feature_whose_virtue_went_and_a_focus_without_a_flaw():
    lab = _feature_lab(
        "labvf_lesser_feature",
        "labvf_lesser_focus",
        virtue_id="v0",
        focus=True,
        focus_allocations=[LabSpecialtyGrant("Ignem", 2)],
    )
    lab.features.append(LabFeature("u", "Unlinked"))
    del lab.virtues_flaws[1]  # the Focus Flaw
    lab_text.prune_features(lab)
    assert (lab.features[0].focus, lab.features[0].focus_allocations) == (False, [])
    del lab.virtues_flaws[0]  # the Feature Virtue
    lab_text.prune_features(lab)
    assert [f.name for f in lab.features] == ["Unlinked"]


def test_free_feature_virtues_and_point_grants():
    lab = _feature_lab("labvf_lesser_feature", "labvf_lesser_feature", virtue_id="v0")
    feature = lab.features[0]
    assert [vf.id for vf in lab_text.free_feature_virtues(lab)] == ["v1"]
    assert [vf.id for vf in lab_text.free_feature_virtues(lab, feature)] == ["v0", "v1"]
    grants = lab_text.grants_from_points(["Ignem", "Aquam", "Ignem"])
    assert grants == [LabSpecialtyGrant("Ignem", 2), LabSpecialtyGrant("Aquam", 1)]
    assert lab_text.points_from_grants(grants) == ["Ignem", "Ignem", "Aquam"]

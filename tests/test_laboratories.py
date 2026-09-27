"""The lab sheet's list rows and details-panel text (laboratories.py)."""

from support import strip_markup

from ars_magica_manager import laboratories as lab_text
from ars_magica_manager.models import (
    LAB_SPECIALIZATIONS,
    DiaryEntry,
    LabCharacteristics,
    Laboratory,
    LabSpecialtyEntry,
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
        "[$text-error]Over capacity by 3 "
        "(Virtues less Flaws may total Size + Refinement = 0).[/]"
    )
    # ...but not once Size makes room for it.
    assert lab_text.vf_warnings(_lab("labvf_greater_feature", size=3)) == ""
    # Two Focus Flaws (net -4 points: well inside capacity).
    two = lab_text.vf_warnings(_lab("labvf_lesser_focus", "labvf_greater_focus"))
    assert two == "[$text-error]2 Focus Flaws: a laboratory may only have one Focus.[/]"


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
        "needs a Specialization  Big windows"
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
        (None, "Activity"),
        (LAB_SPECIALIZATIONS.index("Items"), "Items  +1"),
        (None, "Art"),
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
    assert lab_text.caps_text(lab) == "Activity 2/2, Art 4/4 (Techniques 1/2)"
    assert lab_text.toggle_specialization(lab, "Texts") is not None
    assert lab_text.toggle_specialization(lab, "Corpus") is not None
    # Over a cap (e.g. an old save) shows in the theme's error colour.
    lab.dropped_specializations = []
    assert lab_text.caps_text(lab) == (
        "[$text-error]Activity 3/2[/], [$text-error]Art 5/4[/] (Techniques 1/2)"
    )


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


def test_specialization_info_text_lists_sources_status_and_caps():
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
        "",
        "Counting: Activity 0/2, Art 0/4 (Techniques 0/2)",
    ]
    assert "Space turns it off or on" in lab_text.specialization_info_text(lab, None)

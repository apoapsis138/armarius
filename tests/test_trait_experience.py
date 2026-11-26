"""A Personality Trait that gains experience: it grows like an Ability (DE
p. 241's Hubris, "building like an Ability"), keeps only the experience
toward its next point, and the sheet shows that experience in a quiet
column the way the Abilities list does."""

from __future__ import annotations

from ars_magica_manager import sheet_text as st
from ars_magica_manager.forms import trait as trait_forms
from ars_magica_manager.markup import plain
from ars_magica_manager.models import ScoredTrait


def _shown(traits: list[ScoredTrait], **options: bool) -> list[str]:
    return [plain(label).rstrip() for _, label in st.trait_rows(traits, **options)]


def test_a_trait_that_gains_experience_shows_an_ability_style_total() -> None:
    # Score 2 is 15 xp as an Ability (5 + 10); 3 toward 3, which is at 30.
    trait = ScoredTrait("Hubris", 2, deeds=3, gains_xp=True)
    progress = trait.progress
    assert progress is not None
    assert (progress.score, progress.total, progress.next_total) == (2, 18, 30)


def test_an_ordinary_trait_has_no_experience() -> None:
    assert ScoredTrait("Brave", 2, deeds=3).progress is None


def test_the_list_shows_experience_in_a_right_aligned_column() -> None:
    shown = _shown(
        [
            ScoredTrait("Hubris (Arrogant)", 2, deeds=3, gains_xp=True),
            ScoredTrait("Brave", 1),
            ScoredTrait("Winter", 0, deeds=4, gains_xp=True),
        ]
    )
    assert [line.split()[-1] for line in shown] == ["18/30", "+1", "4/5"]
    # The experience lines up on its right edge; a trait without any shows none.
    assert len(shown[0]) == len(shown[2])
    assert shown[1] == "Brave: +1"


def test_a_list_with_no_experience_looks_as_before() -> None:
    assert _shown([ScoredTrait("Brave", 1), ScoredTrait("Loyal", -2)]) == [
        "Brave: +1",
        "Loyal: -2",
    ]


def test_the_statblock_line_leaves_the_experience_out() -> None:
    traits = [ScoredTrait("Hubris", 2, deeds=3, gains_xp=True)]
    assert _shown(traits, with_xp=False) == ["Hubris: +2"]


def test_ticking_experience_on_again_brings_back_what_it_had() -> None:
    # Brave 2 with 3 toward 3, its box unticked: ticking it shows 15 + 3.
    kept = ScoredTrait("Brave", 2, deeds=3)
    tick = trait_forms.xp_fields(kept)[0]
    assert tick.fills is not None
    assert tick.fills({"gains_xp": True, "score": 2}) == {"xp": 18}
    # A score typed afresh starts from that score alone.
    assert tick.fills({"gains_xp": True, "score": 3}) == {"xp": 30}
    # Unticking shows the score the XP buys.
    assert tick.fills({"gains_xp": False, "xp": 31}) == {"score": 3}


def test_experience_kept_while_unticked_belongs_to_its_score() -> None:
    kept = ScoredTrait("Brave", 2, deeds=3)
    unticked = {"name": "Brave", "gains_xp": False}
    same = trait_forms.trait_from({**unticked, "score": 2}, kept)
    assert same.deeds == 3
    # A new score typed by hand leaves the old score's experience behind.
    lowered = trait_forms.trait_from({**unticked, "score": 0}, kept)
    assert lowered.deeds == 0


def test_a_trait_pushed_below_0_opens_with_its_box_unticked() -> None:
    # A broken faerie bargain or a grog's punishment can take a trait below
    # 0; its form must still save (a rename, say) without a blank XP.
    pushed = ScoredTrait("Winter", -1, gains_xp=True)
    tick, _ = trait_forms.xp_fields(pushed)
    assert tick.value is False

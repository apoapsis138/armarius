"""End of Session: Confidence awards and Reputation deeds (DE pp. 29, 386)."""

from ars_magica_manager import session_end
from ars_magica_manager.models import Character, Saga, ScoredTrait
from ars_magica_manager.rules import confidence


def test_ten_deeds_take_a_reputation_from_one_to_two():
    fame = ScoredTrait("Dragon-slayer", 1)
    assert confidence.add_deeds(fame, 9) == 0 and fame.score == 1
    assert confidence.add_deeds(fame, 1) == 1 and fame.score == 2
    shame = ScoredTrait("Drunkard", -1)
    confidence.add_deeds(shame, 10)
    assert shame.score == -2


def test_a_session_awards_confidence_and_counts_deeds():
    hero = Character(
        id="h",
        name="Hero",
        type="companion",
        reputations=[ScoredTrait("Brave", 1)],
    )
    saga = Saga(id="s", name="S", characters=[hero])
    values = {"played": True, "personal_goal": True, "bonus": True, "deeds_0": 10}
    lines = session_end.end_session(saga, hero, values)
    assert hero.background.confidence_points == 2
    assert hero.reputations[0].score == 2
    assert lines[0].startswith("2 Confidence Point(s)")
    assert hero.diary[-1].name == "End of session"
    idle = session_end.end_session(saga, hero, {"played": False, "bonus": True})
    assert idle[0].startswith("0 Confidence Point(s)")

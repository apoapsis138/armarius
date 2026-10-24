"""One reading of Reputations for every rule (DE pp. 28-29; Covenants p. 40;
Art & Academe p. 100)."""

from ars_magica_manager.models import ScoredTrait
from ars_magica_manager.rules import reputations


def test_a_bad_reputation_by_its_score():
    # The troupe types a bad Reputation with a negative score.
    assert reputations.is_bad(ScoredTrait("Drunkard", -2))
    assert not reputations.is_bad(ScoredTrait("Bad Academic Reputation", 1))


def test_academic_reputations_net_of_the_bad():
    traits = [
        ScoredTrait("Good Academic Reputation", 3),
        ScoredTrait("Learned", 2, type="Academic"),
        ScoredTrait("Plagiarist", -1, type="Academic"),
        ScoredTrait("Drunkard", -2),  # not academic: doesn't count
    ]
    assert reputations.academic_scores(traits) == (5, 1)
    assert reputations.net_academic(traits) == 4
    assert reputations.highest_good(traits) == 3

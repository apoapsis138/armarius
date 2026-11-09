"""What changed: a character against a kept copy, in plain words, after
Advance Season and since the last played Session."""

from ars_magica_manager import commands, what_changed
from ars_magica_manager.forms import sessions as session_forms
from ars_magica_manager.models import (
    Ability,
    ArtScore,
    Book,
    Character,
    Player,
    Saga,
    ScoredTrait,
    Session,
)
from ars_magica_manager.rules import xp as xp_rules


def _magus() -> tuple[Saga, Character]:
    saga = Saga(id="s", name="Saga")
    saga.players = [Player("ana", "Ana")]
    magus = Character(id="m", name="Aelfric", type="magus")
    magus.background.player_ids = ["ana"]
    magus.arts["creo"] = ArtScore(xp=xp_rules.art_xp(12))
    magus.abilities.append(Ability("Magic Theory", xp=xp_rules.ability_xp(5)))
    magus.personality_traits.append(ScoredTrait("Brave", 1))
    saga.characters = [magus]
    return saga, magus


def test_a_copy_reads_back_the_scores_that_moved():
    saga, magus = _magus()
    kept = what_changed.keep(saga, magus)
    magus.arts["creo"].xp = xp_rules.art_xp(13)
    magus.abilities[0].xp = xp_rules.ability_xp(6)
    magus.aging.warping_points = 2
    magus.personality_traits[0].score = 2
    magus.background.confidence_points = 1
    saga.books.append(
        Book("b", "On Fire", "Summa", owner_kind="character", owner_id="m")
    )
    assert what_changed.changes(saga, kept, magus) == [
        "Creo 12 to 13",
        "Magic Theory 5 to 6",
        "Warping Points 0 to 2",
        "Confidence Points 0 to 1",
        "Brave +1 to +2",
        "gained the book On Fire",
    ]


def test_nothing_changed_says_so():
    saga, magus = _magus()
    kept = what_changed.keep(saga, magus)
    assert what_changed.text(saga, kept, magus) == "Nothing changed."


def test_marking_a_session_played_keeps_a_copy_for_since_the_last_session():
    saga, magus = _magus()
    saga.players = []  # Solo: the form has one step.
    ops = session_forms.session_ops(saga)
    form = ops.add()
    assert isinstance(form, commands.Form)
    values = {f.key: f.value for f in form.fields()}
    form.apply({**values, "real_date": "2026-11-14", "played": True})
    [session] = saga.sessions
    assert set(session.kept) == {"m"}
    magus.arts["creo"].xp = xp_rules.art_xp(13)
    shown = session_forms.since_last_session(saga, magus)
    [info] = shown.fields()
    assert "Creo 12 to 13" in str(info.value)


def test_only_the_latest_two_played_sessions_keep_their_copies():
    saga, _ = _magus()
    saga.players = []
    saga.sessions = [
        Session("a", real_date="2026-10-01", played=True, kept={"m": {}}),
        Session("b", real_date="2026-10-08", played=True, kept={"m": {}}),
    ]
    form = session_forms.session_ops(saga).add()
    values = {f.key: f.value for f in form.fields()}
    form.apply({**values, "real_date": "2026-10-15", "played": True})
    kept = {s.id: bool(s.kept) for s in saga.sessions}
    assert kept["a"] is False and kept["b"] is True

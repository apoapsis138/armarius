"""A record's Secrets: a list of secrets, kept apart from what the players
see, moved there from older saves (one untitled secret), edited one by
one through the same forms, revealed one by one, split by paragraph, and
left out of a player's download unless revealed."""

from __future__ import annotations

from dataclasses import asdict

import pytest
from support import everything_saga

from ars_magica_manager import saga_index, transfer, viewing
from ars_magica_manager.commands import Confirm, Form
from ars_magica_manager.forms import creature as creature_forms
from ars_magica_manager.forms import neighbour as neighbour_forms
from ars_magica_manager.forms import reveal
from ars_magica_manager.forms import secrets as secret_forms
from ars_magica_manager.forms import tribunal as tribunal_forms
from ars_magica_manager.forms import world as world_forms
from ars_magica_manager.models import (
    Character,
    Covenant,
    Creature,
    Neighbour,
    Secret,
    Tribunal,
    as_secrets,
    read_secrets,
)
from ars_magica_manager.models.common import split_secrets
from ars_magica_manager.sections import SECRETS_SECTION


def _texts(secrets: list[Secret]) -> list[str]:
    return [s.text for s in secrets]


def test_secrets_are_what_follows_a_heading_of_their_own():
    assert split_secrets("Seen.\n\nSecrets\nHidden.\n\nMore.") == (
        "Seen.",
        "Hidden.\n\nMore.",
    )
    assert split_secrets("Secrets\nAll of it.") == ("", "All of it.")
    assert split_secrets("Seen.\n\n**Secrets:**\nHidden.") == ("Seen.", "Hidden.")
    # Only a line of its own after a blank line is the heading.
    for text in ("Secrets are fun.", "Seen.\nSecrets\nNot a heading."):
        assert split_secrets(text) == (text, "")


def test_older_saves_have_their_secrets_moved_out_on_loading():
    neighbour = Neighbour.from_dict(
        {"id": "n", "name": "N", "summary": "A lord.\n\nSecrets\nIn debt."}
    )
    character = Character.from_dict(
        {
            "id": "c",
            "name": "C",
            "type": "magus",
            "summary": "A magus.\n\nSecrets\nA diabolist.",
        }
    )
    tribunal = Tribunal.from_dict(
        {
            "id": "t",
            "name": "T",
            "summary": "Now.\n\nSecrets\nA plot.",
            "history": "Then.\n\nSecrets\nWhat comes.",
        }
    )
    creature = Creature.from_dict(
        {"id": "r", "name": "R", "notes": "A wolf.\n\nSecrets\nA man."}
    )
    assert (neighbour.summary, _texts(neighbour.secrets)) == ("A lord.", ["In debt."])
    assert (character.summary, _texts(character.secrets)) == (
        "A magus.",
        ["A diabolist."],
    )
    assert (tribunal.summary, tribunal.history) == ("Now.", "Then.")
    assert _texts(tribunal.secrets) == ["A plot.\n\nWhat comes."]
    assert (creature.notes, _texts(creature.secrets)) == ("A wolf.", ["A man."])


def test_an_older_saves_words_become_one_untitled_secret():
    [secret] = read_secrets("The aegis has a gap.\n\nThe founder lives.")
    assert (secret.title, secret.revealed) == ("", False)
    assert read_secrets("") == [] and read_secrets(None) == []
    with pytest.raises(ValueError):
        read_secrets(12, "Cologne")
    with pytest.raises(ValueError):
        read_secrets([{"title": 3}], "Cologne")


def test_a_covenants_secrets_lose_the_line_that_pointed_at_them():
    covenant = Covenant.from_dict(
        {
            "id": "c",
            "saga_id": "s",
            "name": "C",
            "notes": "Founded 1100.\n\nWhat the players do not know.\n\nSecrets\nCursed.",
            "secrets": "Already known.",
        }
    )
    assert covenant.notes == "Founded 1100."
    assert _texts(covenant.secrets) == ["Already known.\n\nCursed."]


def test_a_saved_list_loads_as_it_was_saved():
    first = Neighbour(
        id="n", name="N", secrets=[Secret("Debt", "In debt.", 1221, "Summer")]
    )
    again = Neighbour.from_dict(asdict(first))
    assert again.secrets == first.secrets and again.secrets[0].revealed


def test_moving_secrets_out_is_done_once():
    first = Neighbour.from_dict(
        {"id": "n", "name": "N", "summary": "A lord.\n\nSecrets\nIn debt."}
    )
    again = Neighbour.from_dict(asdict(first))
    assert (again.summary, _texts(again.secrets)) == ("A lord.", ["In debt."])


def test_every_record_with_secrets_adds_edits_and_deletes_them_through_one_form():
    saga = everything_saga()
    gottfried = saga.neighbour("gottfried")
    assert gottfried is not None
    creature, tribunal = saga.creatures[0], saga.tribunals[0]
    covenant = saga.covenants[0]
    for ops, record in (
        (neighbour_forms.neighbour_ops(saga, gottfried), gottfried),
        (creature_forms.creature_ops(saga, creature), creature),
        (tribunal_forms.tribunal_ops(saga, tribunal), tribunal),
        (world_forms.record_ops(saga, covenant), covenant),
    ):
        record.secrets = []
        section = ops[SECRETS_SECTION]
        assert section.add is not None and section.edit is not None
        form = section.add()
        assert isinstance(form, Form)
        assert [f.key for f in form.fields()] == ["title", "text"]
        form.apply({"title": "Debt", "text": "Told."})
        assert record.secrets == [Secret("Debt", "Told.")]
        edit = section.edit(0)
        assert isinstance(edit, Form)
        edit.apply({"title": "Debts", "text": "Told twice."})
        assert record.secrets == [Secret("Debts", "Told twice.")]
        assert section.rows() == ["Debts"]


def test_the_storyguides_list_says_whether_each_is_revealed_in_words():
    record = Neighbour(
        id="n",
        name="N",
        secrets=[Secret("Debt", "x", 1221, "Summer"), Secret("", "A long hidden plot")],
    )
    [(_, first), (_, second)] = secret_forms.secret_rows(record)
    assert first.startswith("Debt") and first.endswith("Revealed Summer 1221")
    assert second.startswith("A long hidden plot") and second.endswith("Not revealed")


def test_a_record_without_secrets_says_so():
    assert secret_forms.NONE_YET in secret_forms.secrets_text(
        Neighbour(id="n", name="N")
    )
    shown = secret_forms.secrets_text(
        Neighbour(id="n", name="N", secrets=as_secrets("*Cursed*"))
    )
    assert "[i]Cursed[/i]" in shown


def test_split_breaks_a_secret_by_paragraph_after_showing_the_parts():
    record = Neighbour(
        id="n",
        name="N",
        secrets=[Secret("Old", "One.\n\nTwo.\n\nThree.", 1221, "Spring")],
    )
    assert secret_forms.splits(record, 0) and not secret_forms.splits(record, 1)
    step = secret_forms.split(record, 0)
    assert isinstance(step, Confirm)
    assert "1. One." in step.question and "3. Three." in step.question
    step.apply()
    assert _texts(record.secrets) == ["One.", "Two.", "Three."]
    assert [s.title for s in record.secrets] == ["Old", "", ""]
    assert all(s.revealed for s in record.secrets)


def test_revealing_one_secret_dates_it_and_writes_the_diary_hiding_takes_it_back():
    saga = everything_saga()
    gottfried = saga.neighbour("gottfried")
    assert gottfried is not None
    gottfried.secrets = [Secret("Debt", "In debt to the Jews of Cologne.")]
    troupe = [c for c in saga.covenants if c.played]
    before = [len(c.diary) for c in troupe]
    step = reveal.reveal_secret(saga, gottfried, 0)
    assert isinstance(step, Confirm)
    step.apply()
    secret = gottfried.secrets[0]
    assert (secret.revealed_year, secret.revealed_season) == (
        saga.current_year,
        saga.current_season,
    )
    assert [len(c.diary) for c in troupe] == [n + 1 for n in before]
    assert troupe[0].diary[-1].name == f"Revealed: {gottfried.name}: Debt"
    step = reveal.conceal_secret(saga, gottfried, 0)
    assert isinstance(step, Confirm)
    step.apply()
    assert not secret.revealed and [len(c.diary) for c in troupe] == before


def test_the_players_see_only_the_revealed_secrets_in_known():
    record = Neighbour(
        id="n",
        name="N",
        secrets=[Secret("Debt", "In debt.", 1221, "Summer"), Secret("Plot", "A plot.")],
    )
    viewing.use(viewing.TABLE_VIEWER)
    assert secret_forms.shown(record) and secret_forms.tab_title(record) == "Known"
    known = secret_forms.known_text(record)
    assert "Debt" in known and "Plot" not in known
    assert not secret_forms.shown(
        Neighbour(id="m", name="M", secrets=[Secret("P", "x")])
    )


def test_the_storyguides_find_searches_every_secret():
    saga = everything_saga()
    gottfried = saga.neighbour("gottfried")
    assert gottfried is not None
    gottfried.secrets = [Secret("Debt", "x"), Secret("", "A werewolf by night.")]
    found = saga_index.search(saga_index.entries(saga), "werewolf")
    assert [m.entry.name for m in found] == [gottfried.name]


def test_a_players_download_carries_only_the_revealed_secrets():
    saga = everything_saga()
    covenant = saga.covenants[0]
    covenant.secrets = [
        Secret("Gap", "The aegis has a gap."),
        Secret("Spring", "A vis spring.", 1221, "Summer"),
    ]
    for character in saga.characters:
        character.secrets = as_secrets("Owes a debt.")
    data = transfer.export_data(saga, covenant, with_members=True)
    assert len(data["saga"]["covenants"][0]["secrets"]) == 2
    kept = transfer.without_secrets(data)
    assert [s["title"] for s in kept["saga"]["covenants"][0]["secrets"]] == ["Spring"]
    assert all(r["secrets"] == [] for r in kept["saga"]["characters"])
    # The storyguide's own export is untouched.
    assert len(data["saga"]["covenants"][0]["secrets"]) == 2

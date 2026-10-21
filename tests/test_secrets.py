"""A record's Secrets: kept apart from what the players see, moved there
from older saves, edited through one form, and left out of a player's
download."""

from __future__ import annotations

from dataclasses import asdict

from support import everything_saga

from ars_magica_manager import transfer
from ars_magica_manager.forms import creature as creature_forms
from ars_magica_manager.forms import neighbour as neighbour_forms
from ars_magica_manager.forms import tribunal as tribunal_forms
from ars_magica_manager.forms import world as world_forms
from ars_magica_manager.forms.secrets import NONE_YET, secrets_text
from ars_magica_manager.models import (
    Character,
    Covenant,
    Creature,
    Neighbour,
    Tribunal,
)
from ars_magica_manager.models.common import split_secrets
from ars_magica_manager.sections import SECRETS_SECTION


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
    assert (neighbour.summary, neighbour.secrets) == ("A lord.", "In debt.")
    assert (character.summary, character.secrets) == ("A magus.", "A diabolist.")
    assert (tribunal.summary, tribunal.history) == ("Now.", "Then.")
    assert tribunal.secrets == "A plot.\n\nWhat comes."
    assert (creature.notes, creature.secrets) == ("A wolf.", "A man.")


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
    assert covenant.secrets == "Already known.\n\nCursed."


def test_moving_secrets_out_is_done_once():
    first = Neighbour.from_dict(
        {"id": "n", "name": "N", "summary": "A lord.\n\nSecrets\nIn debt."}
    )
    again = Neighbour.from_dict(asdict(first))
    assert (again.summary, again.secrets) == ("A lord.", "In debt.")


def test_every_record_with_secrets_edits_them_through_one_form():
    saga = everything_saga()
    gottfried = saga.neighbour("gottfried")
    creature, tribunal = saga.creatures[0], saga.tribunals[0]
    covenant = saga.covenants[0]
    for ops, record in (
        (neighbour_forms.neighbour_ops(saga, gottfried), gottfried),
        (creature_forms.creature_ops(saga, creature), creature),
        (tribunal_forms.tribunal_ops(saga, tribunal), tribunal),
        (world_forms.record_ops(saga, covenant), covenant),
    ):
        edit = ops[SECRETS_SECTION].edit
        assert edit is not None
        form = edit(0)
        (field,) = form.fields()
        assert field.key == "secrets" and field.value == record.secrets
        form.apply({"secrets": "Told."})
        assert record.secrets == "Told."


def test_a_record_without_secrets_says_so():
    assert NONE_YET in secrets_text(Neighbour(id="n", name="N"))
    assert secrets_text(Neighbour(id="n", name="N", secrets="*Cursed*")) == (
        "[i]Cursed[/i]"
    )


def test_a_players_download_leaves_out_the_secrets():
    saga = everything_saga()
    covenant = saga.covenants[0]
    covenant.secrets = "The aegis has a gap."
    for character in saga.characters:
        character.secrets = "Owes a debt."
    data = transfer.export_data(saga, covenant, with_members=True)
    assert data["saga"]["covenants"][0]["secrets"] == "The aegis has a gap."
    kept = transfer.without_secrets(data)
    records = [r for k in ("covenants", "characters") for r in kept["saga"][k]]
    assert records and all(r["secrets"] == "" for r in records)
    # The storyguide's own export is untouched.
    assert data["saga"]["covenants"][0]["secrets"] == "The aegis has a gap."

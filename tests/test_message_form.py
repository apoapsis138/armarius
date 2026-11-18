"""The Message composer (forms/message.py): one commands.Form the desktop's
Chronicle pane and the terminal draw. It says in words who will read the
Message before it is sent, offers only people at the Session to whisper
to and only records the writer may open to link, and sends words, never
anything else."""

from __future__ import annotations

from typing import Any

from ars_magica_manager import chronicle, commands, references, viewing
from ars_magica_manager.forms import message
from ars_magica_manager.models import Neighbour, Player, Saga, Session

HOST = viewing.HOST


def _saga() -> tuple[Saga, Session]:
    """Ana and Ben are at the Session, Dai is Away; the players know the
    abbey but not the diabolist."""
    saga = Saga(id="fengheld", name="Fengheld")
    saga.players = [Player("ana", "Ana"), Player("ben", "Ben"), Player("dai", "Dai")]
    hidden = Neighbour(id="diabolist", name="Brother Wido")
    hidden.known = False
    saga.neighbours = [Neighbour(id="abbey", name="St Gall"), hidden]
    session = Session("s1", coming=["ana", "ben"], away=["dai"])
    saga.sessions = [session]
    return saga, session


Sent = tuple[str, tuple[str, ...], tuple[references.Ref, ...]]


def _form(who: str) -> tuple[commands.Form, list[Sent]]:
    saga, session = _saga()
    sent: list[Sent] = []

    def send(
        words: str, to: tuple[str, ...], links: tuple[references.Ref, ...]
    ) -> str | None:
        sent.append((words, to, links))
        return None

    return message.message_form(saga, session, who, send), sent


def _field(form: commands.Form, key: str) -> Any:
    return next(f for f in form.fields() if f.key == key)


def _answer(form: commands.Form, values: dict[str, Any]) -> list[str]:
    fields = {f.key: f.value for f in form.fields() if f.kind != "info"}
    fields.update(values)
    problem = form.validate(fields) if form.validate else None
    assert problem is None, problem
    return list(form.apply(fields) or [])


def _choices(command: Any) -> list[str]:
    assert isinstance(command, commands.Choose)
    return [c.value for c in command.choices()]


def test_a_message_goes_to_the_table_unless_someone_is_chosen() -> None:
    form, sent = _form("ana")

    _answer(form, {"words": "We ride at dawn."})

    assert sent == [("We ride at dawn.", (), ())]


def test_the_composer_says_who_will_read_it_in_words() -> None:
    form, _sent = _form("ana")
    to = _field(form, "to")

    assert to.display([]) == "The Table: everyone at the Session"
    assert to.display(["ben"]) == "A Whisper to Ben, which the storyguide also sees"
    assert to.display([HOST]) == "A Whisper to the storyguide"


def test_only_people_at_the_session_can_be_whispered_to() -> None:
    form, _sent = _form("ana")

    assert _choices(_field(form, "to").items.entry(None)) == [HOST, "ben"]


def test_a_whisper_sends_those_chosen() -> None:
    form, sent = _form("ana")

    _answer(form, {"words": "Bring rope.", "to": ["ben"]})

    assert sent == [("Bring rope.", ("ben",), ())]


def test_only_records_the_writer_may_open_can_be_linked() -> None:
    as_ana, _ = _form("ana")
    as_storyguide, _ = _form(HOST)

    offered = _choices(_field(as_ana, "links").items.entry(None))
    assert "neighbours:abbey" in offered
    assert "neighbours:diabolist" not in offered
    assert "neighbours:diabolist" in _choices(
        _field(as_storyguide, "links").items.entry(None)
    )


def test_linking_a_record_writes_its_name_into_the_words() -> None:
    form, sent = _form("ana")
    links = _field(form, "links")

    filled = links.fills({"words": "Meet at", "links": ["neighbours:abbey"]})
    assert filled == {"words": "Meet at St Gall"}

    _answer(form, {"words": "Meet at St Gall", "links": ["neighbours:abbey"]})
    assert sent[0][2] == (references.Ref("neighbours", "abbey", "St Gall"),)


def test_an_emoji_is_refused_before_sending() -> None:
    form, sent = _form("ana")
    values = {"words": f"Huzzah {chr(0x1F389)}", "to": [], "links": []}

    problem = form.validate(values) if form.validate else None

    assert problem is not None and "Emoji" in problem
    assert sent == []


def test_on_the_hosts_own_copy_a_message_is_written_to_the_chronicle() -> None:
    saga, session = _saga()
    assert isinstance(message.message_here(saga, session), commands.Refuse)
    book = chronicle.begin(saga, session, by=HOST)

    form = message.message_here(saga, session)
    assert isinstance(form, commands.Form)
    _answer(form, {"words": "Night falls."})

    book.refresh()
    entry = book.entries[-1]
    assert entry.kind == chronicle.MESSAGE and entry.author == HOST

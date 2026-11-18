"""Table rolls go to the Chronicle (table_rolls.py; ADR 0018 as amended):
while a Session is Under way, a rolling form whose roll the story calls
for in the moment takes its dice from the host, and its roll is written
to the Chronicle with every face it drew and the form's own result line.

Pattern: Decorator, twice. The recording die source wraps the host's
source of chance and keeps each face; the form decorator wraps a Form,
adding who sees the roll and writing the entry, and changes no rule."""

from __future__ import annotations

import random
from typing import Any

import pytest

from ars_magica_manager import chronicle, table_rolls, viewing
from ars_magica_manager.commands import Form, notes
from ars_magica_manager.form_spec import DialogField, shown
from ars_magica_manager.models import Casting, Character, Player, Saga, Session
from ars_magica_manager.rules import dice
from tests.test_chronicle import Faces

HOST = viewing.HOST


def _saga() -> Saga:
    """Ana plays Aelfric tonight; the host runs the Session."""
    saga = Saga(id="fengheld", name="Fengheld")
    saga.players = [Player("ana", "Ana")]
    saga.characters = [Character(id="aelfric", name="Aelfric", type="magus")]
    saga.sessions = [
        Session(
            "s1",
            coming=["ana"],
            castings=[Casting(player_id="ana", character_id="aelfric")],
        )
    ]
    return saga


def _begun() -> tuple[Saga, Session, chronicle.Chronicle]:
    saga = _saga()
    session = saga.sessions[0]
    return saga, session, chronicle.begin(saga, session, by=HOST)


def _rolling_form(rng: random.Random | None = None, *, fail: bool = False) -> Form:
    """A form that rolls a stress die at Save, unless one is typed."""
    source = rng or table_rolls.dice()

    def fields() -> list[DialogField]:
        return [
            DialogField("ease", "Ease Factor", "int", 6),
            DialogField("die", "Stress die", "optint", None, hint="Blank: rolled."),
        ]

    def apply(values: dict[str, Any]) -> list[str]:
        typed = values.get("die")
        die = typed if typed is not None else dice.stress_die(source, 1).value
        if fail:
            raise ValueError("The form refused the save.")
        verdict = "it holds" if die >= values["ease"] else "it fails"
        return notes(f"die {die} against {values['ease']}: [b]{verdict}[/b].")

    return Form("Roll: Aelfric", fields, apply, save_label="Roll")


def _wrapped(saga: Saga, form: Form | None = None) -> Form:
    return table_rolls.form(
        form or _rolling_form(), saga, character_id="aelfric", typed=("die",)
    )


def _shown(form: Form, values: dict[str, Any] | None = None) -> list[str]:
    return [f.key for f in form.fields() if shown(f, values or {})]


def _form_rolls(book: chronicle.Chronicle) -> list[chronicle.Entry]:
    return [e for e in book.entries if e.kind == chronicle.FORM_ROLL]


@pytest.fixture
def faces() -> Any:
    """The host's dice show 3, then 7, ..."""

    def use(*shown: int) -> None:
        table_rolls.host_source = lambda: Faces(*shown)

    yield use
    table_rolls.host_source = table_rolls.system_source


# -- the recording die source --


def test_the_recording_source_gives_the_faces_its_source_would() -> None:
    plain = random.Random(2291)
    recorded = table_rolls.RecordingDice(random.Random(2291))

    thrown = [recorded.randrange(10) for _ in range(8)] + [recorded.randint(1, 6)]

    assert thrown == [plain.randrange(10) for _ in range(8)] + [plain.randint(1, 6)]
    assert recorded.faces == thrown


def test_the_recording_source_records_every_stress_doubling_and_botch_die() -> None:
    recorded = table_rolls.RecordingDice(Faces(1, 1, 4, 0, 0))

    first = dice.stress_die(recorded, 1)
    second = dice.stress_die(recorded, 1)

    assert first.value == 16  # 1, 1 double twice: 4 x 4 (DE p. 7)
    assert second.botched
    assert recorded.faces == [1, 1, 4, 0, 0]


def test_any_draw_through_the_recording_source_is_recorded() -> None:
    recorded = table_rolls.RecordingDice(random.Random(7))

    recorded.choice(["a", "b", "c"])

    assert len(recorded.faces) == 1


# -- outside a Session --


def test_outside_a_session_the_form_is_unchanged_but_for_its_dice_line() -> None:
    saga = _saga()
    inner = _rolling_form()

    shown = table_rolls.form(inner, saga, character_id="aelfric")

    assert shown.title == inner.title and shown.fields is inner.fields


def test_outside_a_session_the_form_rolls_its_own_dice() -> None:
    saga = _saga()

    lines = _wrapped(saga).apply({"ease": 0, "die": None})

    assert lines and "it holds" in lines[0]


# -- the form, while Under way --


def test_under_way_the_storyguide_sees_who_sees_it_blind_first() -> None:
    saga, _session, _book = _begun()

    fields = {f.key: f for f in _wrapped(saga).fields()}

    pick = fields[table_rolls.VISIBILITY]
    assert pick.value == chronicle.BLIND
    assert [v for _l, v in pick.options] == [
        chronicle.PUBLIC,
        chronicle.PRIVATE,
        chronicle.BLIND,
    ]


def test_under_way_a_player_rolls_public_and_never_blind() -> None:
    saga, _session, _book = _begun()
    viewing.use(viewing.viewer_for(saga.players[0]))

    pick = next(f for f in _wrapped(saga).fields() if f.key == table_rolls.VISIBILITY)

    assert pick.value == chronicle.PUBLIC
    assert chronicle.BLIND not in [v for _l, v in pick.options]


def test_under_way_the_typed_die_is_hidden() -> None:
    saga, _session, _book = _begun()

    assert _shown(_wrapped(saga)) == ["ease", table_rolls.VISIBILITY]


def test_a_saved_form_roll_is_written_with_its_faces_and_result_line(
    faces: Any,
) -> None:
    saga, _session, book = _begun()
    faces(1, 4)

    lines = _wrapped(saga).apply({"ease": 6, table_rolls.VISIBILITY: chronicle.PUBLIC})

    [entry] = _form_rolls(book)
    assert lines == ["die 8 against 6: [b]it holds[/b].", "Stress die 1, 4 → 4 × 2 = 8"]
    assert entry.author == HOST
    assert entry.audience == chronicle.table()
    assert entry.body["form"] == "Roll: Aelfric"
    assert entry.body["character_id"] == "aelfric"
    assert entry.body["character_name"] == "Aelfric"
    assert entry.body["faces"] == [1, 4]
    assert entry.body["lines"] == ["die 8 against 6: it holds."]
    assert not entry.body["cancelled"]


def test_the_form_never_sees_the_visibility_pick(faces: Any) -> None:
    saga, _session, _book = _begun()
    faces(5)
    seen: list[dict[str, Any]] = []

    def apply(values: dict[str, Any]) -> list[str]:
        seen.append(dict(values))
        return []

    inner = Form("Roll", list, apply)
    table_rolls.form(inner, saga).apply({table_rolls.VISIBILITY: chronicle.PUBLIC})

    assert seen == [{}]


def test_a_form_roll_line_shows_its_dice_and_result() -> None:
    saga, _session, book = _begun()
    table_rolls.host_source = lambda: Faces(1, 4)
    try:
        _wrapped(saga).apply({"ease": 6, table_rolls.VISIBILITY: chronicle.PUBLIC})
    finally:
        table_rolls.host_source = table_rolls.system_source

    [entry] = _form_rolls(book)

    assert chronicle.line(entry, {}) == (
        "Roll: Aelfric, Aelfric: Stress die 1, 4 → 4 × 2 = 8; "
        "die 8 against 6: it holds."
    )


def test_a_form_roll_line_names_its_whole_dice_and_loose_faces() -> None:
    body = {
        "form": "Hunting",
        "character_name": "",
        "faces": [0, 0, 7, 12],
        "dice": [
            {"stress": True, "faces": [0], "botch_faces": [0]},
            {"stress": False, "faces": [7], "botch_faces": []},
            {"face": 12},
        ],
        "lines": ["The quarry gets away."],
    }

    assert chronicle.form_roll_line(body) == (
        "Hunting: Stress die 0; 1 botch die 0: botch, 1 zero; Simple die 7; "
        "other dice 12; The quarry gets away."
    )


def test_a_form_roll_written_before_whole_dice_keeps_its_old_line() -> None:
    body = {"form": "Hunting", "faces": [3, 7], "lines": ["It works."]}

    assert chronicle.form_roll_line(body) == "Hunting: dice 3 7; It works."


def test_nothing_is_written_when_no_die_is_drawn() -> None:
    saga, _session, book = _begun()
    quiet = Form("Roll", list, lambda _values: notes("No roll needed."))

    table_rolls.form(quiet, saga).apply({table_rolls.VISIBILITY: chronicle.PUBLIC})

    assert _form_rolls(book) == []


def test_a_blind_form_roll_is_the_storyguides_with_a_line_for_its_player(
    faces: Any,
) -> None:
    saga, _session, book = _begun()
    faces(7)

    _wrapped(saga).apply({"ease": 6, table_rolls.VISIBILITY: chronicle.BLIND})

    [entry] = _form_rolls(book)
    told = book.entries[-1]
    assert entry.audience == chronicle.storyguide_only()
    assert told.kind == chronicle.ROLLED
    assert told.audience == chronicle.chosen("ana")
    assert told.body["roll"] == entry.number


def test_a_private_form_roll_is_seen_by_its_roller() -> None:
    saga, _session, book = _begun()
    viewing.use(viewing.viewer_for(saga.players[0]))

    _wrapped(saga).apply({"ease": 6, table_rolls.VISIBILITY: chronicle.PRIVATE})

    [entry] = _form_rolls(book)
    assert entry.audience == chronicle.chosen("ana")
    assert entry.author == "ana"


def test_a_player_cannot_roll_a_form_blind() -> None:
    saga, _session, book = _begun()
    viewing.use(viewing.viewer_for(saga.players[0]))

    lines = _wrapped(saga).apply({"ease": 6, table_rolls.VISIBILITY: chronicle.BLIND})

    assert lines == ["Only the Session's storyguide rolls Blind."]
    assert _form_rolls(book) == []


def test_a_form_that_fails_after_drawing_leaves_its_dice(faces: Any) -> None:
    saga, _session, book = _begun()
    faces(9)

    with pytest.raises(ValueError, match="refused the save"):
        _wrapped(saga, _rolling_form(fail=True)).apply(
            {"ease": 6, table_rolls.VISIBILITY: chronicle.PUBLIC}
        )

    [entry] = _form_rolls(book)
    assert entry.body["faces"] == [9]
    assert entry.body["cancelled"]
    assert entry.body["lines"] == []
    assert chronicle.line(entry, {}) == (
        "Roll: Aelfric, Aelfric: Stress die 9; drawn, then cancelled."
    )


def test_the_form_draws_from_its_own_source_again_after_the_save(
    faces: Any,
) -> None:
    saga, _session, book = _begun()
    faces(2)
    form = _wrapped(saga)
    form.apply({"ease": 6, table_rolls.VISIBILITY: chronicle.PUBLIC})

    chronicle.end(saga, saga.sessions[0], by=HOST)
    form.apply({"ease": 6, table_rolls.VISIBILITY: chronicle.PUBLIC})

    assert len(_form_rolls(book)) == 1


def test_the_storyguide_strikes_a_form_roll(faces: Any) -> None:
    saga, session, book = _begun()
    faces(4)
    _wrapped(saga).apply({"ease": 6, table_rolls.VISIBILITY: chronicle.PUBLIC})
    [entry] = _form_rolls(book)

    chronicle.strike(book, session, entry.number, "Wrong trait", by=HOST, saga=saga)

    assert chronicle.voided(book) == {entry.number: "Wrong trait"}
    assert chronicle.line(entry, chronicle.voided(book)).startswith(
        "STRUCK (Wrong trait): Roll: Aelfric"
    )


def test_confidence_is_not_spent_on_a_form_roll(faces: Any) -> None:
    saga, session, book = _begun()
    faces(4)
    _wrapped(saga).apply({"ease": 6, table_rolls.VISIBILITY: chronicle.PUBLIC})
    [entry] = _form_rolls(book)

    problem = chronicle.why_not_spend(book, saga, session, entry.number, 1, HOST)

    assert problem == "There is no such roll."


def test_a_blind_form_roll_calls_the_storyguides_attention(faces: Any) -> None:
    saga, session, book = _begun()
    faces(4)
    _wrapped(saga).apply({"ease": 6, table_rolls.VISIBILITY: chronicle.BLIND})
    [entry] = _form_rolls(book)

    assert chronicle.calls_attention(entry, HOST, session, saga)
    assert not chronicle.calls_attention(entry, "ana", session, saga)


# -- at a Remote seat --


class _FakeSeat:
    """A seat's roll that draws each die from the 'host': records what it
    was asked, and gives the host's faces."""

    def __init__(self, *faces: int) -> None:
        self.asked: list[table_rolls.Opening] = []
        self.host_faces = list(faces)
        self.finished: list[list[str]] = []
        self.cancelled = 0

    def open(self, opening: table_rolls.Opening) -> table_rolls.FormRoll:
        self.asked.append(opening)
        seat = self

        class Roll:
            def __init__(self) -> None:
                self.dice = Faces(*seat.host_faces)

            def finish(self, lines: list[str]) -> str | None:
                seat.finished.append(lines)
                return None

            def cancel(self) -> None:
                seat.cancelled += 1

        return Roll()


class _Untouchable(random.Random):
    def randrange(self, *_args: object, **_kwargs: object) -> int:  # type: ignore[override]
        raise AssertionError("The seat's own source of chance was used.")


def test_at_a_seat_each_die_comes_from_the_host() -> None:
    saga, _session, book = _begun()
    viewing.use(viewing.viewer_for(saga.players[0]))
    seat = _FakeSeat(1, 4)
    table_rolls.use_seat(seat.open)
    try:
        form = _wrapped(saga, _rolling_form())
        table_rolls.plain_source = _Untouchable
        lines = form.apply({"ease": 6, table_rolls.VISIBILITY: chronicle.PUBLIC})
    finally:
        table_rolls.use_seat(None)
        table_rolls.plain_source = random.Random

    assert lines == ["die 8 against 6: [b]it holds[/b].", "Stress die 1, 4 → 4 × 2 = 8"]
    assert seat.asked == [
        table_rolls.Opening("Roll: Aelfric", "aelfric", chronicle.PUBLIC)
    ]
    # The host can't group a seat's faces, so the seat says its dice.
    assert seat.finished == [
        ["die 8 against 6: it holds.", "Stress die 1, 4 → 4 × 2 = 8"]
    ]
    assert _form_rolls(book) == []  # the host writes it, not the seat


def test_at_a_seat_a_form_that_fails_after_drawing_is_cancelled() -> None:
    saga, _session, _book = _begun()
    seat = _FakeSeat(3)
    table_rolls.use_seat(seat.open)
    try:
        with pytest.raises(ValueError):
            _wrapped(saga, _rolling_form(fail=True)).apply(
                {"ease": 6, table_rolls.VISIBILITY: chronicle.PUBLIC}
            )
    finally:
        table_rolls.use_seat(None)

    assert seat.cancelled == 1
    assert seat.finished == []


def test_at_a_seat_the_hosts_refusal_is_shown() -> None:
    saga, _session, _book = _begun()

    class Refusing(_FakeSeat):
        def open(self, opening: table_rolls.Opening) -> table_rolls.FormRoll:
            roll = super().open(opening)
            roll.finish = lambda _lines: "The host can't be reached just now."  # type: ignore[method-assign]
            return roll

    seat = Refusing(5)
    table_rolls.use_seat(seat.open)
    try:
        lines = _wrapped(saga).apply(
            {"ease": 0, table_rolls.VISIBILITY: chronicle.PUBLIC}
        )
    finally:
        table_rolls.use_seat(None)

    assert (
        lines[-1]
        == "The roll isn't in the Chronicle: The host can't be reached just now."
    )


# -- the host's side of a seat's form roll --


def test_the_host_writes_a_seats_form_roll_with_the_faces_it_drew() -> None:
    saga, session, book = _begun()
    roll = table_rolls.HostRoll(
        saga,
        session,
        table_rolls.Opening("Cast a Power", "aelfric", chronicle.PUBLIC),
        by="ana",
        source=Faces(6, 0),
    )

    assert [roll.dice.randrange(10), roll.dice.randrange(10)] == [6, 0]
    assert roll.finish(["Cast: succeeds."]) is None

    book.refresh()
    [entry] = _form_rolls(book)
    assert entry.author == "ana"
    assert entry.body["faces"] == [6, 0]
    assert entry.body["lines"] == ["Cast: succeeds."]


def test_the_host_refuses_a_seats_blind_form_roll() -> None:
    saga, session, _book = _begun()

    with pytest.raises(ValueError, match="Blind"):
        table_rolls.HostRoll(
            saga,
            session,
            table_rolls.Opening("Cast a Power", "aelfric", chronicle.BLIND),
            by="ana",
        )


# -- a Table roll made outside a form --


def test_a_roll_outside_a_form_is_written_with_its_lines(faces: Any) -> None:
    saga, _session, book = _begun()
    faces(6)

    with table_rolls.drawing(saga, "Roll a Table: [b]Wolves[/b]") as drawn:
        drawn.lines = [f"the d10 shows {dice.simple_die(drawn.dice)}: wolves."]

    [entry] = _form_rolls(book)
    assert entry.audience == chronicle.storyguide_only()  # the storyguide's: Blind
    assert entry.body["form"] == "Roll a Table: Wolves"
    assert entry.body["lines"] == ["the d10 shows 6: wolves."]
    assert drawn.refused is None


def test_a_players_roll_outside_a_form_is_public(faces: Any) -> None:
    saga, _session, book = _begun()
    viewing.use(viewing.viewer_for(saga.players[0]))
    faces(6)

    with table_rolls.drawing(saga, "Impress", character_id="aelfric") as drawn:
        dice.stress_die(drawn.dice)

    [entry] = _form_rolls(book)
    assert entry.audience == chronicle.table()


def test_a_roll_outside_a_form_that_fails_leaves_its_dice(faces: Any) -> None:
    saga, _session, book = _begun()
    faces(2)

    with (
        pytest.raises(RuntimeError),
        table_rolls.drawing(saga, "Debate") as drawn,
    ):
        drawn.dice.randrange(10)
        raise RuntimeError("the debate broke")

    [entry] = _form_rolls(book)
    assert entry.body["cancelled"]


def test_outside_a_session_a_roll_outside_a_form_writes_nothing() -> None:
    saga = _saga()

    with table_rolls.drawing(saga, "Roll a Table") as drawn:
        face = drawn.dice.randrange(10)

    assert 0 <= face <= 9
    assert drawn.refused is None


# -- whole dice (STORY-2348) --


def test_the_recording_source_keeps_whole_dice_with_their_doublings_and_botch_dice() -> (
    None
):
    """DE p. 7: a 1 re-rolls and doubles; a first 0 rolls the botch dice."""
    recorded = table_rolls.RecordingDice(Faces(1, 1, 5, 0, 3, 0, 8))

    dice.stress_die(recorded, 2)  # 1, 1, 5: 5 x 4 = 20
    dice.stress_die(recorded, 2)  # 0; botch dice 3, 0
    dice.simple_die(recorded)  # 8

    assert recorded.dice == [
        {"stress": True, "faces": [1, 1, 5], "botch_faces": []},
        {"stress": True, "faces": [0], "botch_faces": [3, 0]},
        {"stress": False, "faces": [8], "botch_faces": []},
    ]
    assert recorded.faces == [1, 1, 5, 0, 3, 0, 8]


def test_a_form_roll_keeps_its_whole_dice_and_loose_faces(faces: Any) -> None:
    saga, _session, book = _begun()
    faces(1, 4, 9)

    def apply(_values: dict[str, Any]) -> list[str]:
        rng = table_rolls.dice()
        dice.stress_die(rng, 1)  # 1, 4: 4 x 2 = 8
        rng.randrange(10)  # a face drawn outside the die helpers
        return notes("Done.")

    table_rolls.form(Form("Roll", list, apply), saga).apply(
        {table_rolls.VISIBILITY: chronicle.PUBLIC}
    )

    [entry] = _form_rolls(book)
    assert entry.body["dice"] == [
        {"stress": True, "faces": [1, 4], "botch_faces": []},
        {"face": 9},
    ]
    assert entry.body["faces"] == [1, 4, 9]


def test_a_form_that_asks_to_keep_its_roll_posts_the_rolls_result(faces: Any) -> None:
    """Health and Disputations end in a Keep question: the entry carries
    the question's result lines, not just the dice."""
    from ars_magica_manager.commands import Confirm

    saga, _session, book = _begun()
    faces(6)

    def apply(_values: dict[str, Any]) -> Confirm:
        die = dice.stress_die(table_rolls.dice(), 1).value
        return Confirm(
            f"Soak [b]{die}[/b].\n\nNo wound.", lambda: None, roll_result=True
        )

    table_rolls.form(Form("Take Harm", list, apply), saga).apply(
        {table_rolls.VISIBILITY: chronicle.PUBLIC}
    )

    [entry] = _form_rolls(book)
    assert entry.body["lines"] == ["Soak 6.", "No wound."]


def test_a_question_not_marked_as_the_rolls_result_posts_nothing(faces: Any) -> None:
    """Only a question a form marks as its roll's result is the roll's
    result: any other ("Overwrite it?") leaves the entry with its dice."""
    from ars_magica_manager.commands import Confirm

    saga, _session, book = _begun()
    faces(6)

    def apply(_values: dict[str, Any]) -> Confirm:
        dice.stress_die(table_rolls.dice(), 1)
        return Confirm("Overwrite the old note?", lambda: None)

    table_rolls.form(Form("Take Harm", list, apply), saga).apply(
        {table_rolls.VISIBILITY: chronicle.PUBLIC}
    )

    [entry] = _form_rolls(book)
    assert entry.body["lines"] == []
    assert entry.body["faces"] == [6]


# -- the dice line on a Table roll form's own result (STORY-2348, part 2) --


def test_outside_a_session_a_table_roll_forms_result_shows_its_dice() -> None:
    saga = _saga()
    table_rolls.plain_source = lambda: Faces(1, 1, 5)
    try:
        shown = _wrapped(saga).apply({"ease": 6})
    finally:
        table_rolls.plain_source = random.Random

    assert shown[-1] == "Stress die 1, 1, 5 → 5 × 4 = 20"


def test_under_way_the_result_shows_its_dice_and_the_chronicle_keeps_them_once(
    faces: Any,
) -> None:
    saga, _session, book = _begun()
    faces(0, 0)

    shown = _wrapped(saga).apply({"ease": 6, table_rolls.VISIBILITY: chronicle.PUBLIC})

    assert shown[-1] == "Stress die 0; 1 botch die 0: botch, 1 zero"
    [entry] = _form_rolls(book)
    assert chronicle.line(entry, {}) == (
        "Roll: Aelfric, Aelfric: Stress die 0; 1 botch die 0: botch, 1 zero; "
        "die 0 against 6: it fails."
    )


def test_a_typed_die_adds_no_dice_line() -> None:
    shown = _wrapped(_saga()).apply({"ease": 6, "die": 7})

    assert shown == ["die 7 against 6: [b]it holds[/b]."]


def test_a_roll_outside_a_form_says_its_dice_in_or_out_of_a_session(
    faces: Any,
) -> None:
    table_rolls.plain_source = lambda: Faces(1, 3)
    try:
        with table_rolls.drawing(_saga(), "Impress") as outside:
            dice.stress_die(outside.dice, 1)
    finally:
        table_rolls.plain_source = random.Random
    saga, _session, book = _begun()
    faces(0, 4)
    with table_rolls.drawing(saga, "Impress") as inside:
        dice.stress_die(inside.dice, 1)
        inside.lines = ["Not impressed."]

    assert outside.said == "Stress die 1, 3 → 3 × 2 = 6"
    assert inside.said == "Stress die 0; 1 botch die 4: no zeros"
    [entry] = _form_rolls(book)
    assert entry.body["dice"] == [{"stress": True, "faces": [0], "botch_faces": [4]}]


def test_a_form_saved_inside_another_leaves_the_outer_watch_running() -> None:
    saga = _saga()
    inner = _wrapped(saga)

    def apply(_values: dict[str, Any]) -> list[str]:
        inner.apply({"ease": 6, "die": 7})  # typed: draws nothing
        dice.stress_die(table_rolls.dice(), 1)
        return notes("Done.")

    table_rolls.plain_source = lambda: Faces(1, 3)
    try:
        shown = table_rolls.form(Form("Outer", list, apply), saga).apply({})
    finally:
        table_rolls.plain_source = random.Random

    assert shown == ["Done.", "Stress die 1, 3 → 3 × 2 = 6"]


def test_a_seat_roll_that_already_says_its_dice_doesnt_say_them_twice() -> None:
    saga, _session, _book = _begun()
    viewing.use(viewing.viewer_for(saga.players[0]))
    seat = _FakeSeat(6)
    table_rolls.use_seat(seat.open)
    try:
        with table_rolls.drawing(saga, "Impress") as drawn:
            dice.stress_die(drawn.dice, 1)
            drawn.lines = [f"Impress Udo: {drawn.said}, +5 = 11 vs 6."]
    finally:
        table_rolls.use_seat(None)

    assert seat.finished == [["Impress Udo: Stress die 6, +5 = 11 vs 6."]]


def test_an_unmarked_question_gets_no_dice_line(faces: Any) -> None:
    from ars_magica_manager.commands import Confirm

    saga, _session, _book = _begun()
    faces(6)

    def apply(_values: dict[str, Any]) -> Confirm:
        dice.stress_die(table_rolls.dice(), 1)
        return Confirm("Overwrite the old note?", lambda: None)

    asked = table_rolls.form(Form("Take Harm", list, apply), saga).apply(
        {table_rolls.VISIBILITY: chronicle.PUBLIC}
    )

    assert isinstance(asked, Confirm)
    assert asked.question == "Overwrite the old note?"

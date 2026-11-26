"""The desktop's Chronicle pane (gui/chronicle_pane.py), the Virtual
Tabletop preview: docked on the right while a Session is Under way, a card
per entry the reader may see, collapsing to a strip that counts what came
and pulses once for a Blind result (not with Reduce motion)."""

from __future__ import annotations

import os
import random

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from chronicle_support import evening_with_damage, line_of, whole, written
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication, QLabel, QToolButton, QWidget

from ars_magica_manager import (
    chronicle,
    commands,
    references,
    settings,
    storage,
    viewing,
    virtual_tabletop,
)
from ars_magica_manager.gui import motion, pictures, sounds
from ars_magica_manager.gui.chronicle_pane import (
    ChroniclePane,
    DiceRow,
    Die,
    remembered_collapsed,
)
from ars_magica_manager.gui.style.liveries import THEMES
from ars_magica_manager.gui.themes import SCRIPTORUM
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.models import (
    Ability,
    Casting,
    Character,
    Characteristics,
    Neighbour,
    Player,
    Saga,
    Session,
)
from ars_magica_manager.remote import events

HOST = viewing.HOST


class Faces(random.Random):
    def __init__(self, *faces: int) -> None:
        super().__init__()
        self.faces = list(faces)

    def randrange(self, *_args: object, **_kwargs: object) -> int:  # type: ignore[override]
        return self.faces.pop(0)


@pytest.fixture(scope="module")
def app() -> QApplication:
    application = QApplication.instance() or QApplication([])
    assert isinstance(application, QApplication)
    assert pictures.register_fonts() == []
    return application


@pytest.fixture(autouse=True)
def quiet(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    played: list[str] = []
    monkeypatch.setattr(sounds, "play", played.append)
    return played


def _saga() -> Saga:
    saga = Saga(id="fengheld", name="Fengheld")
    saga.players = [Player("ana", "Ana")]
    saga.characters = [Character(id="aelfric", name="Aelfric", type="magus")]
    saga.sessions = [
        Session("s1", castings=[Casting(player_id="ana", character_id="aelfric")])
    ]
    return saga


def _pane(
    who: str = HOST,
) -> tuple[ChroniclePane, Saga, Session, chronicle.Chronicle, list[commands.Command]]:
    saga = _saga()
    session = saga.sessions[0]
    book = chronicle.begin(saga, session, by=HOST)
    ran: list[commands.Command] = []
    pane = ChroniclePane(SCRIPTORUM, ran.append)
    pane.attach(saga, session, book, who)
    return pane, saga, session, book, ran


def _roll(
    saga: Saga,
    session: Session,
    book: chronicle.Chronicle,
    *faces: int,
    **asked: object,
) -> None:
    request = chronicle.RollRequest(**asked)  # type: ignore[arg-type]
    chronicle.free_roll(book, saga, session, request, by=HOST, rng=Faces(*faces))


@pytest.mark.usefixtures("app")
def test_a_roll_is_a_card_of_who_what_the_dice_and_the_outcome(
    quiet: list[str],
) -> None:
    pane, saga, session, book, _ran = _pane()

    _roll(
        saga,
        session,
        book,
        1,
        1,
        5,
        modifier=9,
        ease_factor=12,
        character_id="aelfric",
        for_what="Climb the wall",
    )

    assert pane.lines()[-1] == (
        "Aelfric (Climb the wall): Stress die 1, 1, 5 → 5 × 4 = 20, +9 = 29 "
        "vs 12: succeeds by 17"
    )
    card = pane.card_list()[-1]
    assert _text(card, "who") == "Aelfric" and _text(card, "what") == "Climb the wall"
    assert [d.face for d in card.findChildren(Die, "die")] == [1, 1, 5]
    assert [t.text() for t in card.findChildren(QLabel, "doubled")] == ["×2", "×4"]
    assert "die 5 × 4 = 20 + 9" in _text(card, "verdict")
    assert _text(card, "total") == "29"
    assert "vs 12: succeeds by 17" in _text(card, "verdict")  # as the line says
    assert quiet == ["tock"]


def _text(card: QWidget, name: str) -> str:
    found = card.findChild(QLabel, name)
    assert isinstance(found, QLabel), name
    return found.text()


@pytest.mark.usefixtures("app")
def test_a_players_roll_names_the_player_in_smaller_type() -> None:
    pane, saga, session, book, _ran = _pane()

    chronicle.free_roll(
        book,
        saga,
        session,
        chronicle.RollRequest(character_id="aelfric"),
        by="ana",
        rng=Faces(4),
    )

    assert _text(pane.card_list()[-1], "player") == "Ana"


@pytest.mark.usefixtures("app")
def test_botch_dice_show_as_tiles_of_their_own() -> None:
    pane, saga, session, book, _ran = _pane()

    _roll(saga, session, book, 0, 3, 0, botch_dice=2)

    card = pane.card_list()[-1]
    assert [d.face for d in card.findChildren(Die, "botch")] == [3, 0]
    assert "botch, 1 zero" in _text(card, "verdict")


@pytest.mark.usefixtures("app")
def test_the_pane_shows_only_what_its_reader_may_see() -> None:
    pane, saga, session, book, _ran = _pane("ana")

    _roll(saga, session, book, 5, character_id="aelfric", visibility=chronicle.BLIND)

    assert pane.lines()[-1] == "Aelfric: the storyguide rolled."
    assert not pane.feed.findChildren(Die, "die")


@pytest.mark.usefixtures("app")
def test_the_storyguide_sees_a_blind_roll_once() -> None:
    pane, saga, session, book, _ran = _pane()

    _roll(saga, session, book, 5, character_id="aelfric", visibility=chronicle.BLIND)

    assert [c.line for c in pane.card_list()][1:] == [
        "Aelfric: Stress die 5, +0 = 5 [Blind]"
    ]


@pytest.mark.usefixtures("app")
def test_a_struck_roll_is_struck_through_with_the_reason_beneath() -> None:
    pane, saga, session, book, _ran = _pane()
    _roll(saga, session, book, 5)

    chronicle.strike(book, session, 2, "Wrong grog", by=HOST)

    card = pane.card_list()[-1]
    dice = card.findChild(DiceRow, "dice")
    assert isinstance(dice, DiceRow) and dice.struck
    assert _text(card, "reason") == "Struck: Wrong grog"
    assert card.line.startswith("STRUCK (Wrong grog)")


@pytest.mark.usefixtures("app")
def test_collapsed_it_counts_what_came_and_never_opens_itself(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(motion, "moving", lambda: True)
    pane, saga, session, book, _ran = _pane("ana")
    pane.set_collapsed(True)

    _roll(saga, session, book, 5)
    _roll(saga, session, book, 6, character_id="aelfric", visibility=chronicle.BLIND)

    assert pane.collapsed and pane.unseen == 2
    assert pane.pulses == 1  # the Blind line for Ana, not the public roll
    assert pane.strip.count == 2
    pane.strip.click()
    assert not pane.collapsed and pane.unseen == 0


@pytest.mark.usefixtures("app")
def test_a_blind_answer_to_a_roll_request_pulses_the_storyguides_strip(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An answer is gathered on its request's card rather than drawn as one
    of its own, but a Blind answer's number is still for the storyguide."""
    monkeypatch.setattr(motion, "moving", lambda: True)
    pane, saga, session, book, _ran = _pane()
    call = chronicle.RollCall(("aelfric",), "Perception", visibility=chronicle.BLIND)
    request = chronicle.request_rolls(book, saga, session, call, by=HOST)
    pane.set_collapsed(True)

    chronicle.answer(book, saga, session, request.number, "aelfric", by="ana")

    assert pane.pulses == 1


@pytest.mark.usefixtures("app")
def test_no_pulse_with_reduce_motion(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(motion, "moving", lambda: False)
    pane, saga, session, book, _ran = _pane("ana")
    pane.set_collapsed(True)

    _roll(saga, session, book, 6, character_id="aelfric", visibility=chronicle.BLIND)

    assert pane.pulses == 0 and pane.unseen == 1


@pytest.mark.usefixtures("app")
def test_open_or_collapsed_is_remembered() -> None:
    pane, *_rest = _pane()

    pane.set_collapsed(True)

    again = ChroniclePane(SCRIPTORUM, lambda _c: None)
    assert remembered_collapsed() is True
    assert not again.collapsed  # the window decides when to restore it


@pytest.mark.usefixtures("app")
def test_free_roll_runs_the_cores_form() -> None:
    pane, *_rest, ran = _pane()

    pane.roll_button.click()

    assert isinstance(ran[0], commands.Form) and ran[0].title == "Free Roll"


@pytest.mark.usefixtures("app")
def test_begin_session_opens_the_pane_in_the_saga_window() -> None:
    virtual_tabletop.set_on(True)
    saga = _saga()
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    assert not window.chronicle_pane.isVisibleTo(window)
    assert window.saga is not None

    chronicle.begin(window.saga, window.saga.sessions[0], by=HOST)
    window.redraw()

    assert window.chronicle_pane.isVisibleTo(window)
    assert not window.chronicle_pane.collapsed
    assert window.chronicle_button.isVisibleTo(window)
    window.chronicle_button.click()
    assert window.chronicle_pane.collapsed
    window.close()


@pytest.mark.usefixtures("app")
def test_no_pane_with_the_preview_off() -> None:
    saga = _saga()
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    assert window.saga is not None
    chronicle.begin(window.saga, window.saga.sessions[0], by=HOST)

    window.redraw()

    assert not window.chronicle_pane.isVisibleTo(window)
    assert not window.chronicle_button.isVisibleTo(window)
    window.close()


# -- found in review --


@pytest.mark.usefixtures("app")
def test_the_sessions_storyguide_strikes_a_roll_from_its_dice() -> None:
    pane, saga, session, book, ran = _pane()
    _roll(saga, session, book, 5)
    dice = pane.card_list()[-1].findChild(DiceRow, "dice")
    assert isinstance(dice, DiceRow) and dice.can_strike
    menu = dice.menu()
    assert [a.text() for a in menu.actions()] == ["Strike this roll…"]

    dice.strike_mark.click()

    form = ran[-1]
    assert isinstance(form, commands.Form) and form.title == "Strike Roll 2"
    form.apply({"reason": "Wrong grog"})
    assert chronicle.voided(book) == {2: "Wrong grog"}
    again = pane.card_list()[-1].findChild(DiceRow, "dice")
    assert isinstance(again, DiceRow) and not again.can_strike


@pytest.mark.usefixtures("app")
def test_a_player_has_no_void_and_rolls_only_with_a_character_tonight() -> None:
    pane, saga, session, book, _ran = _pane("ana")
    _roll(saga, session, book, 5)

    dice = pane.card_list()[-1].findChild(DiceRow, "dice")
    assert isinstance(dice, DiceRow) and not dice.can_strike
    assert pane.roll_button.isEnabled()
    pane.attach(saga, session, book, "")  # the table: no one in particular
    assert not pane.roll_button.isEnabled()


@pytest.mark.usefixtures("app")
def test_a_session_already_under_way_comes_back_as_it_was_left() -> None:
    virtual_tabletop.set_on(True)
    saga = _saga()
    chronicle.begin(saga, saga.sessions[0], by=HOST)
    storage.save_saga(saga)
    settings.update_settings(chronicle_pane_collapsed=True)
    chronicle.forget_open()

    window = MainWindow(saga_ids=[saga.id])

    assert window.chronicle_pane.isVisibleTo(window)
    assert window.chronicle_pane.collapsed
    window.close()


@pytest.mark.usefixtures("app")
def test_a_damaged_chronicle_hides_the_pane_and_the_page_still_works(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    virtual_tabletop.set_on(True)
    saga = _saga()
    book = chronicle.begin(saga, saga.sessions[0], by=HOST)
    book.path.write_text("not json\n{}\n", encoding="utf-8")
    storage.save_saga(saga)
    chronicle.forget_open()
    told: list[str] = []
    monkeypatch.setattr(MainWindow, "tell", lambda _w, title, _why: told.append(title))

    window = MainWindow(saga_ids=[saga.id])
    window.redraw()

    assert not window.chronicle_pane.isVisibleTo(window)
    assert told and told[-1] == "Chronicle"
    window.close()


@pytest.mark.usefixtures("app")
def test_entries_caught_up_together_each_draw_one_card() -> None:
    """Another process (the listener for a seat) wrote a Strike and then a
    Message: caught up at once, the Strike redraws the cards, already
    holding the Message, and the Message isn't drawn a second time."""
    pane, saga, session, book, _ran = _pane()
    _roll(saga, session, book, 5)
    other = chronicle.Chronicle(book.path, [])
    other.refresh()
    chronicle.strike(other, session, 2, "Typo", by=HOST, saga=saga)
    chronicle.message(other, saga, session, "Evening.", by="ana")

    book.refresh()

    assert pane.lines().count("Ana: Evening.") == 1


def _cards(who: str, extra: str) -> list[str]:
    """The pane's cards, as `who` reads an evening with one entry of each
    kind and then its damaged variants: all of them (`extra` "all"), only
    those still whole ("whole"), or all of them told one by one as they
    come ("told")."""
    saga, session, book, variants = evening_with_damage()
    written(saga, session, book, variants if extra == "all" else whole(variants))
    if extra != "told":
        pane = ChroniclePane(SCRIPTORUM, lambda _command: None)
        pane.attach(saga, session, chronicle.read(saga, session), who)
        return pane.lines()
    written(saga, session, book, [])
    book = chronicle.read(saga, session)
    pane = ChroniclePane(SCRIPTORUM, lambda _command: None)
    pane.attach(saga, session, book, who)
    with book.path.open("a", encoding="utf-8") as out:
        out.write("".join(f"{line_of(e)}\n" for e in variants))
    book.refresh()
    return pane.lines()


@pytest.mark.usefixtures("app")
@pytest.mark.parametrize("who", [HOST, "ana"])
def test_the_pane_passes_over_a_damaged_entry_of_any_kind(who: str) -> None:
    """Drawn whole or told as it comes, a damaged entry of any kind draws
    no card and breaks none: the cards are those of the whole entries."""
    expected = _cards(who, "whole")

    assert _cards(who, "all") == expected
    assert _cards(who, "told") == expected


@pytest.mark.usefixtures("app")
def test_the_pane_follows_the_theme(monkeypatch: pytest.MonkeyPatch) -> None:
    pane, saga, session, book, _ran = _pane()
    _roll(saga, session, book, 5)
    dark = next(t for t in THEMES if t.name != THEMES[0].name)

    pane.set_palette(dark.palette)

    assert pane.p is dark.palette and pane.strip.p is dark.palette
    dice = pane.card_list()[-1].findChild(DiceRow, "dice")
    assert isinstance(dice, DiceRow) and dice.p is dark.palette


# -- found in review of the design pass --


@pytest.mark.usefixtures("app")
def test_the_smaller_name_is_the_player_of_the_character_tonight() -> None:
    pane, saga, session, book, _ran = _pane()

    _roll(saga, session, book, 5, character_id="aelfric")  # rolled by the host

    assert _text(pane.card_list()[-1], "player") == "Ana"


@pytest.mark.usefixtures("app")
def test_many_botch_dice_go_on_a_line_of_their_own() -> None:
    pane, saga, session, book, _ran = _pane()

    _roll(saga, session, book, 0, 1, 2, 3, 4, 5, 6, 7, botch_dice=7)

    card = pane.card_list()[-1]
    assert len(card.findChildren(Die, "botch")) == 7
    assert card.sizeHint().width() <= 340


@pytest.mark.usefixtures("app")
def test_a_reader_who_scrolled_up_keeps_their_place() -> None:
    pane, saga, session, book, _ran = _pane()
    pane._scrolled(0)  # as if they scrolled to the top of a long feed
    pane.follow = False

    _roll(saga, session, book, 5)

    assert not pane.follow


@pytest.mark.usefixtures("app")
def test_a_roll_from_the_pane_is_not_a_saga_save(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    virtual_tabletop.set_on(True)
    saga = _saga()
    chronicle.begin(saga, saga.sessions[0], by=HOST)
    storage.save_saga(saga)
    chronicle.forget_open()
    window = MainWindow(saga_ids=[saga.id])
    saved: list[bool] = []
    monkeypatch.setattr(MainWindow, "save_saga", lambda _w: saved.append(True))
    monkeypatch.setattr(MainWindow, "_answer", lambda _w, step: {})

    window.chronicle_pane.roll_button.click()

    assert saved == []
    assert window.chronicle_pane.lines()[-1].startswith("Storyguide: Stress die")
    window.close()


# -- for a reader who can't tell the colours apart --


def _luminance(colour: str) -> float:
    def channel(value: int) -> float:
        c = value / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    found = QColor(colour)
    return (
        0.2126 * channel(found.red())
        + 0.7152 * channel(found.green())
        + 0.0722 * channel(found.blue())
    )


def _contrast(one: str, other: str) -> float:
    high, low = sorted((_luminance(one), _luminance(other)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def test_the_dice_are_inked_dark_enough_in_every_theme() -> None:
    """WCAG: 4.5:1 for the numeral, 3:1 for the die's outline; both are
    drawn in the theme's ink."""
    weak = [
        t.name
        for t in THEMES
        if _contrast(t.palette["foreground"], t.palette["background"]) < 4.5
    ]
    assert not weak, weak


@pytest.mark.usefixtures("app")
def test_a_zero_die_shows_by_its_shape_not_colour_alone() -> None:
    pane, saga, session, book, _ran = _pane()

    _roll(saga, session, book, 0, 3, 0, botch_dice=2)

    card = pane.card_list()[-1]
    dice = card.findChildren(Die)
    assert [(d.face, d.marked) for d in dice] == [(0, True), (3, False), (0, True)]
    assert "botch" in _text(card, "verdict")


@pytest.mark.usefixtures("app")
def test_an_exploding_one_shows_by_its_shape_not_colour_alone() -> None:
    pane, saga, session, book, _ran = _pane()

    _roll(saga, session, book, 1, 1, 5)

    dice = pane.card_list()[-1].findChildren(Die, "die")
    assert [(d.face, d.doubled) for d in dice] == [(1, True), (1, True), (5, False)]
    assert len({d.colour for d in dice}) == 1  # the same ink: only the rim differs


@pytest.mark.usefixtures("app")
def test_a_sheet_roll_shows_how_it_was_made_and_takes_confidence() -> None:
    pane, saga, session, book, ran = _pane("ana")
    aelfric = saga.characters[0]
    aelfric.characteristics = Characteristics(dexterity=2)
    aelfric.abilities = [Ability("Athletics", xp=30)]
    aelfric.background.confidence_score = 1
    aelfric.background.confidence_points = 2
    request = chronicle.RollRequest(
        character_id="aelfric", sheet=chronicle.SheetRoll("Dexterity", "Athletics")
    )
    chronicle.free_roll(book, saga, session, request, by="ana", rng=Faces(5))
    card = pane.card_list()[-1]

    assert _text(card, "terms") == "Dexterity +2, Athletics +3"
    dice = card.findChild(DiceRow, "dice")
    assert isinstance(dice, DiceRow) and dice.can_spend and not dice.can_strike
    assert [a.text() for a in dice.menu().actions()] == [
        "Spend Confidence…",
        "Strike this roll…",
    ]

    dice.confidence_mark.click()

    form = ran[-1]
    assert isinstance(form, commands.Form)
    assert form.title == "Spend Confidence on Roll 2"
    assert form.apply({"points": 1}) == []
    assert book.entries[-1].kind == chronicle.CONFIDENCE
    again = pane.card_list()[-2].findChild(DiceRow, "dice")
    assert isinstance(again, DiceRow) and not again.can_spend  # the Score is 1


def _labels(card: QWidget, name: str) -> list[str]:
    return [w.text() for w in card.findChildren(QLabel, name)]


@pytest.mark.usefixtures("app")
def test_a_roll_request_gathers_its_answers_on_one_card() -> None:
    pane, _saga_shown, _session, book, ran = _pane()
    assert pane.request_button.isVisibleTo(pane)

    pane.request_rolls()
    form = ran[-1]
    assert isinstance(form, commands.Form) and form.title == "Roll Request"
    assert (
        form.apply(
            {
                "roll:aelfric": True,
                "characteristic": "Perception",
                "ability": "",
                "die": "simple",
                "ease_factor": 6,
                "hide_ease": True,
                "for_what": "Spot the ambush",
                "visibility": chronicle.PUBLIC,
                "hand_to": "",
            }
        )
        == []
    )
    card = pane.card_list()[-1]
    assert _labels(card, "result") == ["…"]
    assert _labels(card, "kept") == ["Ease Factor 6, kept from the players."]

    answer = card.findChild(QToolButton, "answer")
    assert isinstance(answer, QToolButton)
    answer.click()

    card = next(c for c in pane.card_list() if c.line.startswith("Roll request"))
    assert len(chronicle.answers(book, 2)) == 1
    assert _labels(card, "result")[0] != "…"
    assert card.findChild(QToolButton, "answer") is None
    outcome = card.findChild(QToolButton, "outcome")
    assert isinstance(outcome, QToolButton)


@pytest.mark.usefixtures("app")
def test_a_player_answers_for_their_own_character_and_asks_for_nothing() -> None:
    pane, saga, session, book, _ran = _pane("ana")
    assert not pane.request_button.isVisibleTo(pane)
    chronicle.request_rolls(
        book,
        saga,
        session,
        chronicle.RollCall(
            characters=("aelfric",),
            characteristic="Perception",
            visibility=chronicle.PUBLIC,
        ),
        by=HOST,
    )
    card = pane.card_list()[-1]

    answer = card.findChild(QToolButton, "answer")
    assert isinstance(answer, QToolButton)
    answer.click()

    roll = chronicle.answers(book, 2)[0]
    assert roll.author == "ana"
    assert card_outcome_hidden(pane)


def card_outcome_hidden(pane: ChroniclePane) -> bool:
    card = next(c for c in pane.card_list() if c.line.startswith("Roll request"))
    return card.findChild(QToolButton, "outcome") is None


# -- Table rolls made from a form --


def _form_roll(
    saga: Saga,
    session: Session,
    book: chronicle.Chronicle,
    *,
    cancelled: bool = False,
    visibility: str = chronicle.PUBLIC,
) -> None:
    chronicle.form_roll(
        book,
        saga,
        session,
        form="Roll: Aelfric",
        character_id="aelfric",
        visibility=visibility,
        faces=[1, 4],
        lines=["die 8 against 6: it holds."],
        by=HOST,
        cancelled=cancelled,
    )


@pytest.mark.usefixtures("app")
def test_a_form_roll_is_a_card_of_the_form_its_dice_and_its_result(
    quiet: list[str],
) -> None:
    pane, saga, session, book, _ran = _pane()

    _form_roll(saga, session, book)

    card = pane.card_list()[-1]
    labels = {w.objectName(): w.text() for w in card.findChildren(QLabel)}
    assert labels["who"] == "Aelfric"
    assert labels["player"] == "Ana"
    assert labels["what"] == "Roll: Aelfric"
    assert labels["result"] == "die 8 against 6: it holds."
    assert [d.face for d in card.findChildren(Die)] == [1, 4]
    assert quiet == ["tock"]


@pytest.mark.usefixtures("app")
def test_lone_botch_dice_draw_no_die_and_loose_faces_stay_out_of_the_line() -> None:
    pane, saga, session, book, _ran = _pane()

    chronicle.form_roll(
        book,
        saga,
        session,
        form="Lab accident",
        character_id="aelfric",
        visibility=chronicle.PUBLIC,
        faces=[4, 0, 7],
        whole_dice=[
            {"stress": False, "faces": [], "botch_faces": [4, 0]},
            {"face": 7},
        ],
        lines=["Something goes wrong."],
        by=HOST,
    )

    card = pane.card_list()[-1]
    assert [d.face for d in card.findChildren(Die, "die")] == [7]
    assert [d.face for d in card.findChildren(Die, "botch")] == [4, 0]
    assert _text(card, "dice-line") == "2 botch dice 4, 0: 1 zero"


@pytest.mark.usefixtures("app")
def test_a_form_rolls_whole_dice_show_their_doublings_and_botch_dice() -> None:
    pane, saga, session, book, _ran = _pane()

    chronicle.form_roll(
        book,
        saga,
        session,
        form="Hunting",
        character_id="aelfric",
        visibility=chronicle.PUBLIC,
        faces=[1, 4, 0, 0],
        whole_dice=[
            {"stress": True, "faces": [1, 4], "botch_faces": []},
            {"stress": True, "faces": [0], "botch_faces": [0]},
        ],
        lines=["The quarry gets away."],
        by=HOST,
    )

    card = pane.card_list()[-1]
    assert [(d.face, d.doubled) for d in card.findChildren(Die, "die")] == [
        (1, True),
        (4, False),
        (0, False),
    ]
    assert [d.face for d in card.findChildren(Die, "botch")] == [0]
    assert [t.text() for t in card.findChildren(QLabel, "doubled")] == ["×2"]
    assert _text(card, "dice-line") == (
        "Stress die 1, 4 → 4 × 2 = 8; Stress die 0; 1 botch die 0: botch, 1 zero"
    )


@pytest.mark.usefixtures("app")
def test_a_cancelled_form_roll_says_so() -> None:
    pane, saga, session, book, _ran = _pane()

    _form_roll(saga, session, book, cancelled=True)

    card = pane.card_list()[-1]
    results = [
        w.text() for w in card.findChildren(QLabel) if w.objectName() == "result"
    ]
    assert results == ["Drawn, then cancelled."]


@pytest.mark.usefixtures("app")
def test_the_storyguide_strikes_a_form_roll_from_its_dice() -> None:
    pane, saga, session, book, ran = _pane()
    _form_roll(saga, session, book)
    dice = pane.card_list()[-1].findChild(DiceRow, "dice")
    assert isinstance(dice, DiceRow) and dice.can_strike

    dice.strike_mark.click()
    form = ran[-1]
    assert isinstance(form, commands.Form)
    form.apply({"reason": "Wrong trait"})

    card = pane.card_list()[-1]
    labels = {w.objectName(): w.text() for w in card.findChildren(QLabel)}
    assert labels["reason"] == "Struck: Wrong trait"


@pytest.mark.usefixtures("app")
def test_a_blind_form_roll_is_marked_blind_for_the_storyguide() -> None:
    pane, saga, session, book, _ran = _pane()

    _form_roll(saga, session, book, visibility=chronicle.BLIND)

    card = pane.card_list()[-1]
    labels = {w.objectName(): w.text() for w in card.findChildren(QLabel)}
    assert labels["visibility"] == "Blind"


@pytest.mark.usefixtures("app")
def test_at_a_seat_a_blind_roll_for_your_character_pulses_the_strip(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A seat is sent each entry as the host frames it, with no Players
    chosen but told which are for it; the line that the storyguide rolled
    for Ana's character calls Ana's collapsed pane."""
    monkeypatch.setattr(motion, "moving", lambda: True)
    saga = _saga()
    session = saga.sessions[0]
    book = chronicle.begin(saga, session, by=HOST)
    _roll(saga, session, book, 6, character_id="aelfric", visibility=chronicle.BLIND)
    held = chronicle.SeatChronicle()
    pane = ChroniclePane(SCRIPTORUM, lambda _c: None)
    pane.attach(saga, session, held, "ana")
    pane.set_collapsed(True)

    found = chronicle.feed(saga, "ana", session.id, 0)
    assert found is not None
    for entry in found.entries:
        held.take(*events.entry_of(events.frame(session.id, entry).body))

    assert [e.kind for e in held.entries] == ["begin", "rolled"]
    assert pane.pulses == 1


# -- Messages and Whispers --


def _messages_pane(
    who: str,
) -> tuple[ChroniclePane, Saga, Session, chronicle.Chronicle, list[commands.Command]]:
    """Ana and Ben at the Session; the players know the abbey."""
    saga = _saga()
    saga.players.append(Player("ben", "Ben"))
    saga.neighbours = [Neighbour(id="abbey", name="St Gall")]
    session = saga.sessions[0]
    book = chronicle.begin(saga, session, by=HOST)
    ran: list[commands.Command] = []
    pane = ChroniclePane(SCRIPTORUM, ran.append)
    pane.attach(saga, session, book, who)
    return pane, saga, session, book, ran


@pytest.mark.usefixtures("app")
def test_message_runs_the_cores_composer() -> None:
    pane, *_rest, ran = _messages_pane("ana")

    assert pane.message_button.isEnabled()
    pane.message_button.click()

    assert isinstance(ran[0], commands.Form) and ran[0].title == "Message"


@pytest.mark.usefixtures("app")
def test_a_message_is_a_card_of_who_and_the_words_with_its_links() -> None:
    pane, saga, session, book, _ran = _messages_pane("ben")
    link = references.Ref("neighbours", "abbey", "St Gall")
    chronicle.message(book, saga, session, "To St Gall!", links=(link,), by="ana")

    card = pane.card_list()[-1]
    assert card.line == "Ana: To St Gall!"
    words = card.findChild(QLabel, "message-words")
    assert words is not None and "St Gall" in words.text()
    assert 'href="' in words.text()
    followed: list[references.Ref] = []
    pane.open_record = followed.append
    words.linkActivated.emit(words.text().split('href="')[1].split('"')[0])
    assert followed == [link]


@pytest.mark.usefixtures("app")
def test_a_whisper_to_you_pulses_the_strip_and_a_message_to_all_does_not(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(motion, "moving", lambda: True)
    pane, saga, session, book, _ran = _messages_pane("ben")
    pane.set_collapsed(True)

    chronicle.message(book, saga, session, "Hello all.", by="ana")
    chronicle.message(book, saga, session, "Psst.", to=("ben",), by="ana")

    assert pane.unseen == 2 and pane.pulses == 1


@pytest.mark.usefixtures("app")
def test_a_messages_line_breaks_show_on_its_card() -> None:
    pane, saga, session, book, _ran = _messages_pane("ben")
    chronicle.message(book, saga, session, "First,\nsecond.", by="ana")

    words = pane.card_list()[-1].findChild(QLabel, "message-words")

    assert words is not None and "First,<br>second." in words.text()

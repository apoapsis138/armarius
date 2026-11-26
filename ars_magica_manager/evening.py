"""The evening's account: what a played Session's Chronicle tells, kept on
the Session (ADR 0020). End Session folds the Chronicle into a line for
each Scene set, Roll request, roll, Confidence spend, outcome note and
Show, in order, each under the Scene it fell in and keeping who may read
it. A Struck roll and its Strike, a Show withdrawn, and every Message and
Whisper leave no line; the Chronicle's file keeps them all.

Pattern: a plain function folds the entries; each entry kind says its own
line (Kind.account, a Strategy held in the kind registry), so a new kind
needs no new branch here.
"""

from __future__ import annotations

from . import chronicle
from .models import AccountLine, Saga, Session


def account_of(book: chronicle.HasEntries) -> list[AccountLine]:
    """The account `book` tells: each entry's line by its kind, under the
    Scene playing when it was written ("" outside one), and how many
    Scenes had been set by then."""
    struck = chronicle.voided(book)
    scene, play = "", 0
    found: list[AccountLine] = []
    for entry in book.entries:
        spec = chronicle.kind_of(entry)
        if spec is None:
            continue
        if entry.kind == chronicle.SCENE_SET:
            scene, play = str(entry.body["title"]), play + 1
        if spec.strikable and entry.number in struck:
            continue
        text = spec.account(entry, book)
        if text is not None:
            found.append(
                AccountLine(
                    entry.kind,
                    text,
                    entry.audience.to,
                    list(entry.audience.players),
                    scene,
                    play=play,
                )
            )
        if entry.kind == chronicle.SCENE_ENDED:
            scene = ""
    return found


def keep(session: Session, book: chronicle.HasEntries) -> None:
    """Write `book`'s account onto `session` (End Session, or a Session
    played before accounts were kept)."""
    session.account = account_of(book)
    session.account_kept = True


def fold_older(saga: Saga) -> None:
    """Each Session played before accounts were kept gets one, folded once
    from its Chronicle's file as the host opens the saga (the next save
    keeps it). One whose Chronicle can't be read is tried again next time."""
    for session in saga.sessions:
        if session.account_kept or not session.played or session.under_way:
            continue
        if not chronicle.has_chronicle(saga, session):
            continue
        try:
            book = chronicle.read(saga, session)
        except OSError, ValueError:
            continue
        keep(session, book)


def reads(line: AccountLine, who: str, session: Session, saga: Saga | None) -> bool:
    """Whether `who` (a Player's id, or chronicle.person's) may read `line`:
    its entry's Audience, as chronicle.sees decides for the entry itself."""
    if line.audience == chronicle.TABLE:
        return True
    if who == chronicle.storyguide_of(session, saga):
        return True
    return line.audience == chronicle.CHOSEN and who in line.players


def for_reader(saga: Saga, session: Session, who: str) -> list[AccountLine]:
    """`session`'s account as `who` may read it (Protection Proxy): a
    Blind line for the Session's storyguide alone, a Private one for its
    Players and the storyguide."""
    return [line for line in session.account if reads(line, who, session, saga)]


def as_sent(saga: Saga, session: Session, who: str) -> list[AccountLine]:
    """`session`'s account as it leaves the host for `who` (their seat,
    their export): the lines they may read, naming no other Player's id."""
    return [
        AccountLine(
            line.kind,
            line.text,
            line.audience,
            [p for p in line.players if p == who],
            line.scene,
            line.starred,
            line.play,
        )
        for line in for_reader(saga, session, who)
    ]

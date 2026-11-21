"""The aura here now (the Virtual Tabletop preview): while a Scene plays
(scene_play.py), its aura and realm are the default for the rolls an aura
touches, which the roller can change: casting (the Table roll forms that
work out a Casting Score), and Roll from the sheet and Roll requests for a
Supernatural Ability or hedge Art, taken as Magic. A foreign realm's aura
adds a botch die per point of the aura as it is, twice that in a regio of
another realm; Lab Totals are seasonal, and a mundane Ability takes none.

Whoever may not know the aura has none here: the Session's storyguide reads
it from the Scene, anyone else from the banner only when the table was
told it, so a kept aura never fills in a player's form.

Rules: Ars Magica Definitive Edition, Chapter Twelve: Realms, Realm
Interaction, p. 411 (the modifier on Casting Scores and supernatural
Abilities, most Magical in origin; one extra botch die per point of the
unmultiplied aura of a foreign realm; the Divine never hampered); Regiones,
p. 422 (twice the botch dice in a regio of another realm); Appendix D,
p. 545. Errata pp. 19 and 37 agree (both already in the Definitive
Edition).

Pattern: a plain function the forms ask, as they ask table_rules for the
default visibility."""

from __future__ import annotations

from dataclasses import dataclass

from . import chronicle, host_table, record_links, scene_play, scenes, table_rules
from .models import Character, Saga, Session
from .rules import realms

SOURCE = (
    "Ars Magica Definitive Edition, Chapter Twelve: Realms, Realm Interaction, "
    "p. 411; Regiones, p. 422; Appendix D, p. 545"
)


@dataclass(frozen=True)
class AuraHere:
    """The playing Scene's aura: its score, its realm, and whether it is a
    regio's."""

    aura: int
    realm: str
    in_regio: bool = False


def aura_here(
    saga: Saga, session: Session, who: str, book: chronicle.HasEntries | None
) -> AuraHere | None:
    """The aura of the Scene playing at `session`, as `who` may know it:
    the Session's storyguide always, anyone else when the table was told
    it; None with no Scene playing, or an aura with no realm."""
    banner = scene_play.banner_playing(book.entries) if book is not None else None
    if banner is None:
        return None
    if who == table_rules.storyguide_of(session, saga):
        use = next((u for u in session.scenes if u.id == banner.body.get("use")), None)
        scene = scenes.find(saga, use.scene_id) if use is not None else None
        if scene is not None:
            if not scene.realm:
                return None
            regio = bool(scene.place_id and scene.place_level)
            return AuraHere(scene.aura, scene.realm, regio)
    realm = banner.body.get("aura_realm")
    score = banner.body.get("aura_score")
    if not isinstance(realm, str) or not realm or not isinstance(score, int):
        return None
    return AuraHere(score, realm, banner.body.get("regio") is True)


def book_of(
    session: Session, book: chronicle.HasEntries | None
) -> chronicle.HasEntries | None:
    """`book`, unless it is another Session's (a Remote seat holds only
    the one its host feeds it, which may still be an earlier one)."""
    if isinstance(book, chronicle.SeatChronicle) and book.session_id != session.id:
        return None
    return book


def held(saga: Saga, session: Session) -> chronicle.HasEntries | None:
    """`session`'s Chronicle as this copy holds it (book_of)."""
    return book_of(session, host_table.here(saga, session, chronicle.here()).held())


def present_ids(session: Session, book: chronicle.HasEntries | None) -> set[str] | None:
    """The characters present in the Scene playing, by id; None while none
    plays, or where who is present isn't known (a player's copy of the
    saga holds no Scenes)."""
    use = scene_play.playing(session, book)
    if use is None:
        return None
    return {
        ref.partition(":")[2]
        for ref in use.present
        if ref.startswith(record_links.CHARACTERS + ":")
    }


def for_character(
    saga: Saga,
    session: Session,
    who: str,
    book: chronicle.HasEntries | None,
    character_id: str,
) -> AuraHere | None:
    """The aura `character_id` acts in, as `who` may know it: the playing
    Scene's while the character is present there (or who is present isn't
    known), else None."""
    found = aura_here(saga, session, who, book)
    if found is None:
        return None
    present = present_ids(session, book)
    return found if present is None or character_id in present else None


def aura_now(saga: Saga, character: Character) -> tuple[int, str]:
    """The aura (score, realm) a casting form starts on for `character`:
    the playing Scene's while he is present there, else where he is
    (realms.present_aura)."""
    session = chronicle.under_way(saga)
    found = (
        for_character(
            saga, session, chronicle.here(), held(saga, session), character.id
        )
        if session is not None
        else None
    )
    if found is None:
        return realms.present_aura(saga, character)
    return found.aura, found.realm

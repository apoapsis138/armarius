"""A character's faith and what it lets him do: the Religion chapter's
registry of faiths, one Faith for each religion (its icon, whether the
Church's sections are his, the actions it offers), and who may take each
of those actions.

- Anyone of the faith may invoke a saint, the Virgin or his patron: no
  Ability or Virtue is needed (Realms of Power: The Divine p. 87; The
  Church p. 13). A saint may be threatened only after he has refused an
  invocation (RoP: The Divine pp. 87-88).
- Devotions belong to Christians (The Church pp. 12-13): Devotion Points
  are offered to one who holds a Devotion, or is Pious enough to begin
  one (a positive Pious trait, or the Pious Flaw). The patron saint,
  which anyone may have, Pious or not, is its own action (p. 13).
- Indulgences, vigils and fasts are any Christian's (The Church pp.
  11-12); so are petitions and the canon courts, which hear laymen and
  clergy alike (pp. 36, 46).
- A mystic path needs a positive Pious trait and a tie to the Divine
  (The Church p. 21); one already on a path may always see it.
- God's aid may be asked by any Christian, Jew or Muslim who can spend a
  Confidence Point, or a Faith Point with True Faith: not a grog, nor one
  with Low Self-Esteem (RoP: The Divine p. 41). Holy influence is for one
  with spiritual authority, a priest or a rabbi among them (pp. 38,
  124-125).
- Any clergyman may perform an exorcism (The Church p. 34): one in
  orders, or with a clergy Social Status other than Religious.
- Holy Orders are the clergy's: one with a clerical Social Status (Clerk,
  Priest, Religious, Senior Clergy, Mendicant Friar; The Church p. 26; DE
  p. 97), or a grade or ordination already recorded. The orders are men's
  (The Church pp. 34-35), but the sheet records no sex, so that is left
  to the troupe.
- A Muslim seeks a holy forbear's baraka at his shrine, as a saint
  is invoked, and never threatens one; he may make the Hajj (RoP: The
  Divine pp. 103-108; rules.baraka).
- A Mazdean invokes a yazata as a Christian invokes a saint, and never
  threatens one (The Cradle and the Crescent p. 85).
- The books give pagans no rite of their own like the saints': a pagan's
  faith is in a magic spirit (the Spirit Votary, DE p. 58) or in faerie
  (RoP: Faerie p. 134), which the Abilities' and Hermetic chapters
  already offer.

A blank religion counts as Christian (models.religion)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from ..models import Character
from ..models.religion import CHRISTIAN, JEWISH, MAZDEAN, MUSLIM, OTHER, PAGAN
from . import clergy, devotion, holy_influence, mysticism
from .theban_customs import pious

SOURCE = (
    "Realms of Power: The Divine pp. 38-42, 87-88, 103-108, 124-125; The "
    "Church pp. 11-13, 21, 26, 34-36, 46; DE pp. 58, 97"
)

#: The faith actions, by their menu names (actions.MORE_MENU).
INVOKE_SAINT = "invoke_saint"
THREATEN_SAINT = "threaten_saint"
DEVOTION_POINTS = "devotion_points"
PATRON_SAINT = "patron_saint"
ACT_OF_PIETY = "act_of_piety"
MYSTIC_PATH = "mystic_path"
SPIRITUAL_PATH = "spiritual_path"
MONISTIC_REVELATION = "monistic_revelation"
GODS_AID = "gods_aid"
INVOKE_BARAKA = "invoke_baraka"
HAJJ = "hajj"
HOLY_INFLUENCE = "holy_influence"


@dataclass(frozen=True)
class Faith:
    """A religion as the Religion chapter shows it: its icon (an
    artwork concept), whether the Church's sections (Holy Orders,
    Ordinations, Petitions, the Canon Court) are his, the actions it may
    offer (each still asks `may`), and a line on it."""

    name: str
    icon: str
    church: bool
    actions: tuple[str, ...]
    note: str


_ABRAHAMIC = (GODS_AID, HOLY_INFLUENCE)

FAITHS: dict[str, Faith] = {
    CHRISTIAN: Faith(
        CHRISTIAN,
        "church",
        True,
        (
            INVOKE_SAINT,
            THREATEN_SAINT,
            PATRON_SAINT,
            DEVOTION_POINTS,
            ACT_OF_PIETY,
            MYSTIC_PATH,
            SPIRITUAL_PATH,
            MONISTIC_REVELATION,
            *_ABRAHAMIC,
        ),
        "The saints hear any Christian; Devotions, the mystic paths and "
        "the Church are his (RoP: The Divine pp. 71-100; The Church).",
    ),
    MUSLIM: Faith(
        MUSLIM,
        "crescent",
        False,
        (INVOKE_BARAKA, HAJJ, *_ABRAHAMIC),
        "A Muslim seeks a holy forbear's baraka at his shrine (the Qur'an "
        "anywhere), makes the Hajj, and may ask God's aid (RoP: The Divine "
        "pp. 41, 103-108).",
    ),
    JEWISH: Faith(
        JEWISH,
        "star_of_david",
        False,
        _ABRAHAMIC,
        "A Jew may ask God's aid; a rabbi leads his community and tempers "
        "its aura (RoP: The Divine pp. 41, 124-125).",
    ),
    MAZDEAN: Faith(
        MAZDEAN,
        "sacred_fire",
        False,
        (INVOKE_SAINT,),
        "One ritually pure invokes a yazata as a Christian invokes a saint, "
        "and never threatens one (The Cradle and the Crescent p. 85).",
    ),
    PAGAN: Faith(
        PAGAN,
        "sacred_tree",
        False,
        (),
        "The books give pagans no rite like the saints': his faith is in a "
        "magic spirit (a Spirit Votary, DE p. 58) or in faerie (RoP: Faerie "
        "p. 134), dealt with in his Abilities.",
    ),
    OTHER: Faith(
        OTHER,
        "other_faith",
        False,
        (),
        "The books give no rites for his faith.",
    ),
}


def religion(character: Character) -> str:
    """His religion, a blank one counting as Christian."""
    return character.background.religion or CHRISTIAN


def faith(character: Character) -> Faith:
    return FAITHS.get(religion(character), FAITHS[OTHER])


def _has(character: Character, vf_id: str) -> bool:
    return any(vf.vf_id == vf_id for vf in character.virtues_flaws)


def may_spend_for_aid(character: Character) -> bool:
    """Whether he can ever ask God's aid: True Faith, or one who may spend
    Confidence (not a grog, nor Low Self-Esteem; p. 41)."""
    return _has(character, holy_influence.TRUE_FAITH) or not (
        character.type == "grog" or _has(character, holy_influence.LOW_SELF_ESTEEM)
    )


def may_hold_orders(character: Character) -> bool:
    """A clerical Social Status, or a grade or ordination recorded."""
    career = character.church
    return (
        clergy.in_orders(career)
        or bool(career.ordinations)
        or any(vf.vf_id in clergy.CLERICAL for vf in character.virtues_flaws)
    )


def church_career(character: Character) -> bool:
    """Whether he has a Church career on his sheet: orders, or a petition
    or canon case; his Religion chapter stays on whatever his interests."""
    return clergy.has_church_tab(character) or may_hold_orders(character)


def may_keep_devotions(character: Character) -> bool:
    """A Devotion held, or a positive Pious trait (or the Pious Flaw) to
    begin one (The Church pp. 12-13)."""
    return (
        bool(devotion.devotions(character)) or devotion.creation_points(character) > 0
    )


#: The clergy's own Social Statuses: a Religious (a monk or nun) is not
#: one unless ordained (The Church p. 26).
_CLERGY = clergy.CLERICAL - {clergy.RELIGIOUS}


def may_exorcise(character: Character) -> bool:
    """Any clergyman may perform an exorcism (The Church p. 34): one in
    orders, or with the clergy's Social Status."""
    return clergy.in_orders(character.church) or any(
        vf.vf_id in _CLERGY for vf in character.virtues_flaws
    )


def may_walk_a_path(character: Character) -> bool:
    """On a path already, or Pious and tied to the Divine (TC p. 21)."""
    return bool(mysticism.path(character)) or (
        pious(character) > 0 and bool(mysticism.divine_ties(character))
    )


#: Each action's own check, beyond its faith offering it.
_CHECKS: dict[str, Callable[[Character], bool]] = {
    THREATEN_SAINT: lambda c: bool(devotion.refused(c)),
    DEVOTION_POINTS: may_keep_devotions,
    MYSTIC_PATH: may_walk_a_path,
    GODS_AID: may_spend_for_aid,
    HOLY_INFLUENCE: holy_influence.has_standing,
}


def may(character: Character, action: str) -> bool:
    """Whether his faith offers `action` and he may take it: a person (not
    an animal) of a faith listing it, who passes its check, if it has one.
    The books in play, and a path's own steps (Spiritual Path on a
    contemplative's, Monistic Revelation after an Ascent), are the
    caller's to ask."""
    if character.animal is not None or action not in faith(character).actions:
        return False
    check = _CHECKS.get(action)
    return check is None or check(character)

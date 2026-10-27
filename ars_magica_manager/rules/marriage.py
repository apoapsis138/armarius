"""Marriage, the dowry, and what follows.

- **What makes a marriage** (Lords of Men p. 10): the Church asks only a
  spoken intent to marry and a dowry, and prefers a priest and two
  witnesses. The bride must consent: the sacrament needs her free part
  (also C&G p. 113). In many places her father must consent too, though
  in no Christian land does he choose her husband.
- **Canon crimes** (The Church p. 37): marriage between close kin, and
  bigamy. Since 1215 only those sharing a great-great-grandparent are too
  close (LoM pp. 81-82). A marriage blessing is a petition at Ease Factor
  3, and annulling a marriage of common folk one at 9 (The Church p. 47).
- **A noble dowry** (LoM p. 11): in some places an equal share of the
  land her parents own, split between their children; in the French
  sphere the eldest son and his patrimony are kept out of the division
  (both: the land is his patrimony less, the children the eldest son
  less).
  The book gives statements that make it smaller when true and larger
  when not, and no figures: the app works out the share and counts the
  statements; the troupe settles the sum. An heiress may bring a dower
  from the groom's family to her father instead.
- **A merchant's dowry** (City & Guild p. 113, with the errata p. 57,
  which corrects two of its statements to "a groom from a wealthier
  family" and "is not a virgin"): her father's Social Status the same as
  the groom's, or one higher, pays 10 times his yearly profit divided by
  his children (married daughters left out), as Mythic Pounds; two levels
  higher, he raises the groom instead, who becomes a Poor member of the
  Social Status just below the father's, losing any surplus Labor Points.
  A daughter who will inherit the business is likely to bring no dowry,
  and perhaps a dower.
- **A villein's daughter** (LoM p. 81): the serfs of different lords need
  their lord's leave to marry, bought with merchet, higher for a large
  dowry and when the bride moves to her husband's lord's manor.
- **The dowry after** (LoM p. 11): in Italy and much of France the husband
  manages it but may not spend it, may be sued for mismanaging it, and
  gives it back to her family if they separate; in Italy it goes to her
  children or back to her parents if she dies first; for France the books
  don't say, and the troupe decides. In parts of France he may keep much of
  it. In England all she has becomes his.
- **Paid how** (the one statement the two lists word differently): a
  noble's dowry is smaller paid in land or money rather than other rights
  (LoM p. 11); a merchant's is larger paid in assets rather than money (C&G
  p. 113), and land is an asset. Each kind of bride has her own statement.
- **A wife's own land** (Definitive Edition p. 512): a woman who rules a
  fief by inheritance keeps her authority in it while married, except in
  England, where her rights become her husband's. When she dies her eldest
  son keeps it where the eldest takes all; where land is divided, her
  lands go to one of her sons. Land a father has added to his ancestral
  lands may be given as a dowry, which is an inheritance before his death.
- **A widow** (DE p. 513): keeps the profit, not the income, of a third of
  her husband's land until she remarries; one landed at her marriage with
  no adult sons likely has her own lands returned to her outright. Lords
  of Men p. 11 says a third of his estate, likely lost on remarrying: the
  Definitive Edition wins.
- **Parting** (DE p. 148, Unhappily Married): separation, not divorce, is
  permitted in many places for infidelity; the wife's dowry must often be
  returned, in part or full, and among nobles this can start a feud.

Pattern: the dowry is worked out by the bride's family (noble, merchant,
villein), each its own function in a dict: Strategy reduced to a dict of
functions. The statements are a table both kinds read.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from ..models.marriage import (
    ENDED,
    ENGLAND,
    FRANCE,
    FRANCE_MANAGES,
    HUSBAND_DIED,
    ITALY,
    LOWER,
    MARRIED,
    MERCHANT,
    MERCHANT_ASSETS_POINT,
    NEIGHBOUR_REF,
    NOBLE,
    NOBLE_RIGHTS_POINT,
    ONE_HIGHER,
    PARTED,
    SAME_STATUS,
    TWO_HIGHER,
    VILLEIN,
    WIFE_DIED,
    Marriage,
)
from ..models.saga import Saga

SOURCE = (
    "Lords of Men pp. 10-11, 81-82; City & Guild p. 113 (errata p. 57); "
    "Definitive Edition pp. 148, 512-513; The Church pp. 37, 47"
)

#: A merchant's dowry is ten years' profit, shared between his children
#: (C&G p. 113).
MERCHANT_YEARS = 10


@dataclass(frozen=True)
class Point:
    """A statement about the bride that makes her dowry larger when true
    (and smaller when not), and which kinds of family the books give it
    for."""

    key: str
    label: str
    noble: bool = True
    merchant: bool = True


#: The statements, worded the way that makes a dowry larger (LoM p. 11
#: words them the other way; C&G p. 113 this way, as the errata p. 57
#: corrects it).
POINTS: tuple[Point, ...] = (
    Point("wealthier", "The groom's family is wealthier"),
    Point("many", "One of many acceptable brides"),
    Point("not_virgin", "Not a virgin"),
    Point("close_age", "Less than ten years younger than the groom"),
    Point("no_bequest", "Will receive nothing after (bequests to daughters barred)"),
    Point("few_siblings", "Fewer siblings than most"),
    Point("brothers", "Mostly brothers"),
    Point("hard_heir", "Will find it hard to get money from the heir later"),
    Point(
        NOBLE_RIGHTS_POINT,
        "Paid in other rights, not land or money",
        merchant=False,
    ),
    Point(
        MERCHANT_ASSETS_POINT,
        "Paid in assets (land or goods), not money",
        noble=False,
    ),
    Point("instalments", "Paid in instalments", noble=False),
    Point("show", "Her parents would seem richer than they are", noble=False),
)

FAMILY_LABELS: dict[str, str] = {
    NOBLE: "Noble: a share of the land (LoM p. 11)",
    MERCHANT: "Merchant: 10 x a year's profit / children (C&G p. 113)",
    VILLEIN: "Peasant: merchet to the lord (LoM p. 81)",
}

CUSTOM_LABELS: dict[str, str] = {
    ITALY: "Italy: he manages it, can't spend it",
    FRANCE_MANAGES: "Much of France: he manages it, can't spend it",
    FRANCE: "Parts of France: he may keep much of it",
    ENGLAND: "England: all hers becomes his",
    "other": "Another custom: the troupe's",
}
#: What the custom does with the dowry while they are married (LoM p. 11).
CUSTOM_KEEPS: dict[str, str] = {
    ITALY: "he may invest and manage it but not spend it, and may be sued for "
    "mismanaging it",
    FRANCE_MANAGES: "he may invest and manage it but not spend it, and may be "
    "sued for mismanaging it",
    FRANCE: "he may keep much of it",
    ENGLAND: "everything she has becomes his",
    "other": "as the troupe's custom says (Lords of Men gives Italy, France "
    "and England)",
}

STANDING_LABELS: dict[str, str] = {
    SAME_STATUS: "The same as the groom's",
    ONE_HIGHER: "One level higher",
    TWO_HIGHER: "Two levels higher",
    LOWER: "Lower than the groom's",
}

#: The widow's portion (DE p. 513).
WIDOWS_PORTION = (
    "the profit (not the income) of a third of his land until she remarries"
)
WIDOW_LANDED = (
    "landed at her marriage and with no adult sons, she likely has her own "
    "lands returned to her outright"
)
CHURCH_NEEDS = "intent and dowry; a priest and two witnesses preferred"
BLESSING = "A blessing is a petition at Ease Factor 3 (The Church p. 47)."


def points_for(family: str) -> tuple[Point, ...]:
    """The statements the books give for a bride of `family` (none for a
    villein's daughter)."""
    if family == NOBLE:
        return tuple(p for p in POINTS if p.noble)
    if family == MERCHANT:
        return tuple(p for p in POINTS if p.merchant)
    return ()


def larger_and_smaller(marriage: Marriage) -> tuple[int, int]:
    """How many of her family's statements make the dowry larger (true of
    her) and how many smaller (not)."""
    shown = points_for(marriage.family)
    larger = sum(1 for p in shown if p.key in marriage.points)
    return larger, len(shown) - larger


def noble_sharing(marriage: Marriage) -> int:
    """The children her parents' land is divided between: all of them, or,
    with a patrimony kept out (the French sphere), all but the eldest son,
    who takes it (LoM p. 11)."""
    sharing = marriage.children - (1 if marriage.patrimony else 0)
    return max(1, sharing)


def noble_share(marriage: Marriage) -> float:
    """An equal share of her parents' land between their children, the
    eldest son and his patrimony kept out, in manors (LoM p. 11)."""
    lands = max(0, marriage.lands - marriage.patrimony)
    return lands / noble_sharing(marriage)


def merchant_coin(marriage: Marriage) -> int:
    """10 times her father's yearly profit, divided by his children
    (married daughters left out), in Mythic Pounds, rounded down (C&G
    p. 113)."""
    return MERCHANT_YEARS * marriage.profit // max(1, marriage.children)


def _adjusted(marriage: Marriage) -> str:
    larger, smaller = larger_and_smaller(marriage)
    return (
        f"then larger for {larger} of the book's points and smaller for "
        f"{smaller}: the troupe settles the figure"
    )


def _noble(marriage: Marriage) -> list[str]:
    if marriage.heiress:
        return [
            "[b]No dowry:[/] she is the heiress; the groom's family may pay her "
            "father or guardian a dower instead (LoM p. 11)."
        ]
    kept = (
        f" less the eldest son's patrimony of {marriage.patrimony}"
        if marriage.patrimony
        else ""
    )
    sharing = noble_sharing(marriage)
    between = (
        f"{sharing} (her parents' {marriage.children} children less the eldest son)"
        if marriage.patrimony
        else str(sharing)
    )
    return [
        f"A share of the land: {marriage.lands} manors{kept} / "
        f"{between} = [b]{noble_share(marriage):g} manors[/], "
        f"{_adjusted(marriage)} (LoM p. 11)."
    ]


def _merchant(marriage: Marriage) -> list[str]:
    if marriage.heiress:
        return [
            "[b]No dowry, likely:[/] she will inherit the business; the groom "
            "may even pay her family a dower (C&G p. 113)."
        ]
    if marriage.standing == TWO_HIGHER:
        return [
            "[b]No coin:[/] her father, two levels above the groom, raises him "
            "instead: the groom becomes a Poor member of the Social Status just "
            "below her father's, and loses any surplus Labor Points (C&G p. 113)."
        ]
    if marriage.standing == LOWER:
        return [
            "Her father stands below the groom: the books give no dowry for "
            "this; the troupe decides."
        ]
    return [
        f"In coin and goods: 10 x {marriage.profit} pounds' profit / "
        f"{max(1, marriage.children)} children = "
        f"[b]{merchant_coin(marriage)} Mythic Pounds[/], {_adjusted(marriage)} "
        "(C&G p. 113, errata p. 57)."
    ]


def _villein(_marriage: Marriage) -> list[str]:
    return [
        "A villein's daughter: no figure in the books. Serfs of different lords "
        "need their lord's leave, bought with merchet, more for a large dowry "
        "or when she moves to her husband's lord's manor (LoM p. 81); the "
        "manor court keeps it."
    ]


#: How each kind of family's dowry is worked out.
DOWRY: dict[str, Callable[[Marriage], list[str]]] = {
    NOBLE: _noble,
    MERCHANT: _merchant,
    VILLEIN: _villein,
}


def dowry_lines(marriage: Marriage) -> list[str]:
    """The dowry worked out for `marriage`'s bride (markup)."""
    return DOWRY.get(marriage.family, _villein)(marriage)


def warnings(marriage: Marriage) -> list[str]:
    """What stands against the marriage (markup)."""
    found = []
    if not marriage.her_consent:
        found.append(
            "[$text-error]Without her consent there is no sacrament: a man is not "
            "her husband unless she consents (LoM p. 10; C&G p. 113).[/]"
        )
    if not marriage.father_consent:
        found.append(
            "[$text-warning]Her father has not consented: in many places that "
            "stops it, though no Christian father may choose her husband for her "
            "(LoM p. 10).[/]"
        )
    if marriage.kin:
        found.append(
            "[$text-error]Close kin (sharing a great-great-grandparent, since "
            "1215) or bigamy: a canon crime (The Church p. 37; LoM p. 82).[/]"
        )
    return found


def what_follows(marriage: Marriage, bride: str, groom: str) -> str:
    """What the marriage brings while it stands and when it ends, for a
    bride and groom so named (markup)."""
    parts = []
    if marriage.heiress and marriage.family == NOBLE:
        parts.append(
            f"{bride} keeps her inheritance in her own right while married (DE "
            "p. 512)"
            + (
                ": not in England, where her rights become her husband's"
                if marriage.custom == ENGLAND
                else "; not in England"
            )
        )
    elif marriage.custom in CUSTOM_KEEPS:
        parts.append(f"her dowry: {CUSTOM_KEEPS[marriage.custom]} (LoM p. 11)")
    parts.append(
        f"if {groom} dies first she keeps {WIDOWS_PORTION} (DE p. 513), and "
        "Settle an Inheritance reads this marriage"
    )
    if marriage.custom in (ITALY, FRANCE_MANAGES, FRANCE, "other"):
        parts.append(
            "if they part, a dowry goes back to her family, in part or whole (DE "
            "p. 148; LoM p. 11)"
        )
    return "; ".join(parts) + "."


def ending_text(marriage: Marriage, how: str, bride: str, groom: str) -> str:
    """What follows when the marriage ends `how` (markup)."""
    if how == HUSBAND_DIED:
        text = f"{bride} keeps {WIDOWS_PORTION} (DE p. 513)"
        if marriage.heiress:
            text += f"; {WIDOW_LANDED}"
        return text + f". {groom}'s lands go by his own custom."
    if how == WIFE_DIED:
        dowry = {
            ITALY: "her dowry goes to her children, or back to her parents (in "
            "Italy, LoM p. 11)",
            FRANCE_MANAGES: "the books don't say where her dowry goes when she "
            "dies first in France (LoM p. 11 says it only of Italy): the troupe "
            "decides",
            FRANCE: f"{groom} may keep much of her dowry (LoM p. 11)",
            ENGLAND: f"all she had is already {groom}'s (LoM p. 11)",
        }.get(marriage.custom, "her dowry goes as the troupe's custom says")
        text = dowry[0].upper() + dowry[1:]
        if marriage.heiress:
            text += (
                ". Her own fief passes to her eldest son where the eldest takes "
                "all, or to one of her sons where land is divided (DE p. 512)"
            )
        return text + "."
    if how == PARTED:
        return (
            "Separation, not divorce: her dowry goes back to her family, in part "
            "or whole (DE p. 148; LoM p. 11), and among nobles this can start a "
            "feud. Annulling a marriage of common folk is a petition at Ease "
            "Factor 9 (The Church p. 47)."
        )
    return ""


def is_standing(marriage: Marriage) -> bool:
    """Whether the marriage (or betrothal) hasn't ended."""
    return not marriage.ended


def leaves_widow(saga: Saga, lord_id: str) -> bool:
    """Whether the lord `lord_id` leaves a widow: the last marriage naming
    him as the groom stands married, or ended with his death."""
    his = [m for m in saga.marriages if m.groom_ref == NEIGHBOUR_REF + lord_id]
    if not his:
        return False
    last = his[-1]
    return (last.state == MARRIED and not last.ended) or (
        last.state == ENDED and last.ended == HUSBAND_DIED
    )

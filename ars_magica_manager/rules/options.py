"""Optional rules: saga settings that change how the Rules Engine works,
every one off until the troupe turns it on. The options come
from the rules review's decisions (rules reference section 22); each later
story adds the options its rules use.

A supplement's own rules have no switch here: they apply when its book is
in play (Saga.books_in_play, see sourcebooks). An option that comes from a
supplement names its book: it is offered, and can be on, only while that
book is in play.
"""

from __future__ import annotations

from dataclasses import dataclass

from .. import sourcebooks
from ..models import Saga

SOURCE = (
    "Ars Magica Definitive Edition, Chapter Sixteen: Sagas, Rules Questions "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Sixteen:"
    "_Sagas#Rules_Questions)"
)


#: Covenants' extended rules for the Quality of books (book_kinds.CRAFT).
EXTENDED_BOOK_QUALITY = "extended_book_quality"


@dataclass(frozen=True)
class RuleOption:
    key: str
    label: str
    #: What turning it on does, in a line.
    effect: str
    #: The rule it changes, as cited in the rules reference.
    source: str
    #: The sourcebook it comes from ("" for the core book): offered, and
    #: on, only while the saga has that book in play.
    book: str = ""


OPTIONS: tuple[RuleOption, ...] = (
    RuleOption(
        key="simple_dice_only",
        label="Simple dice only",
        effect=(
            "Every stress die is replaced by a simple die: no exploding 1s "
            "and no botches, so skill counts for more."
        ),
        source=SOURCE,
    ),
    RuleOption(
        key="dominion_magic_resistance",
        label="Dominion Magic Resistance",
        effect=(
            "Every Christian, Jew and Muslim has Magic Resistance of 5 x the "
            "local Dominion aura."
        ),
        source=SOURCE,
    ),
    RuleOption(
        key="harsher_infernal_vis",
        label="Harsher Infernal vis",
        effect=(
            "Infernal vis in casting uses Realms of Power: The Infernal's vis "
            "sordida: +3 botch dice per pawn instead of doubling the botch dice."
        ),
        source=(
            "Realms of Power: The Infernal, Chapter One: The Infernal Realm, "
            "Infernal Vis (https://www.redcap.org/page/Realms_of_Power:_The_Infernal"
            "_Chapter_One:_The_Infernal_Realm#Infernal_Vis)"
        ),
        book="RoP:I",
    ),
    RuleOption(
        key="income_per_magus",
        label="Starting income by number of magi",
        effect=(
            "A new covenant's starting income assumes six magi: a Typical "
            "source gains or loses 15 pounds a year for each magus over or "
            "under six, a Lesser source 6."
        ),
        source=(
            "Ars Magica Definitive Edition, Chapter Six: Covenants, Covenant "
            "Finances, Baseline (https://www.redcap.org/page/Ars_Magica_"
            "Definitive_Edition,_Chapter_Six:_Covenants#Baseline_2)"
        ),
    ),
    RuleOption(
        key="strict_creation",
        label="Enforce creation rules strictly",
        effect=(
            "A covenant, laboratory or character In Creation can't move to "
            "In Play while it breaks a creation rule the book says it must "
            "follow (advice never stops it)."
        ),
        source=(
            "Ars Magica Definitive Edition, Chapter Three: Characters, "
            "Detailed Character Creation Summary (https://www.redcap.org/page/"
            "Ars_Magica_Definitive_Edition,_Chapter_Three:_Characters"
            "#Detailed_Character_Creation_Summary)"
        ),
    ),
    RuleOption(
        key=EXTENDED_BOOK_QUALITY,
        label="Extended book Quality",
        effect=(
            "A book's Quality is built from parts: the author gives "
            "Communication + 3 instead of + 6, and a skilled scribe, binder "
            "and illuminator, resonant materials, clarification and glossing "
            "each add to it."
        ),
        source=(
            "Covenants, Chapter Seven: Library, Extended Suggestions on the "
            "Quality of Books (https://www.redcap.org/page/Covenants_Chapter"
            "_Seven:_Library)"
        ),
        book="Covenants",
    ),
)

OPTIONS_BY_KEY: dict[str, RuleOption] = {option.key: option for option in OPTIONS}


def offered(saga: Saga | None) -> list[RuleOption]:
    """The options `saga` can turn on: those whose book is in play."""
    books = sourcebooks.saga_books(saga)
    return [o for o in OPTIONS if sourcebooks.in_play(o.book, books)]


def is_on(saga: Saga | None, key: str) -> bool:
    """Whether optional rule `key` applies to the saga: turned on, and its
    book in play (never, for no saga; a key the app doesn't know is an
    error). Taking the book out of play keeps the choice for when it
    comes back."""
    option = OPTIONS_BY_KEY.get(key)
    if option is None:
        raise KeyError(f"Unknown rule option {key!r}")
    return (
        saga is not None
        and bool(saga.rule_options.get(key, False))
        and sourcebooks.in_play(option.book, sourcebooks.saga_books(saga))
    )


def summary(saga: Saga) -> str:
    """The options a saga has turned on, for its summary: "none" or their
    labels."""
    on = [option.label for option in OPTIONS if is_on(saga, option.key)]
    return ", ".join(on) if on else "none (the book's standard rules)"


def normalized(rule_options: dict[str, bool]) -> dict[str, bool]:
    """Only the options that are on and still exist: a save keeps just
    what the troupe turned on, so an option's default stays off."""
    return {
        key: True for key, on in rule_options.items() if on and key in OPTIONS_BY_KEY
    }

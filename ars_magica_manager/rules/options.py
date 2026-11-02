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

#: Where the core book suggests house rules: the two options citing it are
#: house rules it offers as examples, not rules of the game.
SOURCE = (
    "Ars Magica Definitive Edition, Chapter Sixteen: Sagas, Rules Questions "
    "(house rules), p. 524"
)


#: Any Range, Duration or Target for a spell being invented (Other...),
#: not only those a Virtue or breakthrough opens (spell_parameters).
ANY_SPELL_PARAMETER = "any_spell_parameter"

#: Covenants' extended rules for the Quality of books (book_kinds.CRAFT).
EXTENDED_BOOK_QUALITY = "extended_book_quality"

#: A realia collection's +1 and an expert correspondence's level both
#: raise a library's research on one subject (the book doesn't say).
RESEARCH_AIDS_STACK = "research_aids_stack"

#: A magus still in apprenticeship has the Apprentices' year-by-year
#: model's xp and spell levels for the years so far.
STANDARD_APPRENTICESHIP = "standard_apprenticeship"

#: Copying Lab Texts by magic (Transforming Mythic Europe pp. 103-104): an
#: imperfect copy is hazardous rather than useless; or none may be copied.
HAZARDOUS_LAB_TEXTS = "hazardous_lab_texts"
NO_MAGICAL_LAB_TEXTS = "no_magical_lab_texts"

#: Charter Strength (Transforming Mythic Europe p. 36): a charter's two
#: scores, drafted by each side's notaries, and loopholes sought in it.
CHARTER_STRENGTH = "charter_strength"

#: Rules for a Large Library (Transforming Mythic Europe p. 105): each
#: subject's books summed as one Level and Quality, studied as one.
LARGE_LIBRARY = "large_library"
MORALE_DISCIPLINE = "morale_discipline"


#: The headings of Saga Settings' optional rules, in order.
DICE = "Dice and Combat"
MAGI = "Magi and Characters"
REALMS = "Realms and Auras"
LIBRARY = "Books and the Library"
COVENANTS = "Covenants and Charters"
GROUPS = (DICE, MAGI, REALMS, LIBRARY, COVENANTS)


@dataclass(frozen=True)
class RuleOption:
    key: str
    label: str
    #: What it does in a few words, for its card on Saga Settings.
    brief: str
    #: The heading it comes under on Saga Settings.
    group: str
    #: What turning it on does, in full.
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
        brief="Simple dice replace stress dice: no explosions, no botches.",
        group=DICE,
        effect=(
            "Every stress die is replaced by a simple die: no exploding 1s "
            "and no botches, so skill counts for more."
        ),
        source=SOURCE,
    ),
    RuleOption(
        key="dominion_magic_resistance",
        label="Dominion Magic Resistance",
        brief="The faithful resist magic in a Dominion aura.",
        group=REALMS,
        effect=(
            "Every Christian, Jew and Muslim has Magic Resistance of 5 x the "
            "local Dominion aura."
        ),
        source=SOURCE,
    ),
    RuleOption(
        key="harsher_infernal_vis",
        label="Harsher Infernal vis",
        brief="Infernal vis in casting adds more botch dice.",
        group=REALMS,
        effect=(
            "Infernal vis in casting uses Realms of Power: The Infernal's vis "
            "sordida: +3 botch dice per pawn instead of doubling the botch dice."
        ),
        source=(
            "Realms of Power: The Infernal, Chapter One: The Infernal Realm, "
            "Infernal Vis, pp. 18-19"
        ),
        book="RoP:I",
    ),
    RuleOption(
        key="income_per_magus",
        label="Starting income by number of magi",
        brief="A new covenant's income rises or falls with its number of magi.",
        group=COVENANTS,
        effect=(
            "A new covenant's starting income assumes six magi: its main "
            "source gains or loses 15 pounds a year for each magus over or "
            "under six, only 6 when its one source is Lesser."
        ),
        source=(
            "Ars Magica Definitive Edition, Chapter Six: Covenants, Covenant "
            "Finances, Baseline, p. 189"
        ),
    ),
    RuleOption(
        key="strict_creation",
        label="Enforce creation rules strictly",
        brief="A record that breaks a creation rule stays In Creation.",
        group=MAGI,
        effect=(
            "A covenant, laboratory or character In Creation can't move to "
            "In Play while it breaks a creation rule the book says it must "
            "follow (advice never stops it)."
        ),
        source=(
            "Ars Magica Definitive Edition, Chapter Three: Characters, "
            "Detailed Character Creation Summary, p. 44"
        ),
    ),
    RuleOption(
        key=ANY_SPELL_PARAMETER,
        label="Any spell parameter",
        brief="Invent Spell can take any Range, Duration or Target.",
        group=MAGI,
        effect=(
            "Invent Spell offers Other...: any Range, Duration or Target, its "
            "magnitudes typed, not only those a Virtue, a breakthrough or a "
            "known spell opens to the magus."
        ),
        source=(
            "Ars Magica Definitive Edition, Chapter Nine: Spells, Changing "
            "Ranges, Durations, and Targets, p. 302"
        ),
    ),
    RuleOption(
        key=EXTENDED_BOOK_QUALITY,
        label="Extended book Quality",
        brief="A book's Quality is built up from its makers and materials.",
        group=LIBRARY,
        effect=(
            "A book's Quality is built from parts: the author gives "
            "Communication + 3 instead of + 6, and a skilled scribe, binder "
            "and illuminator, resonant materials, clarification and glossing "
            "each add to it."
        ),
        source=(
            "Covenants, Chapter Seven: Library, Extended Suggestions on the "
            "Quality of Books, pp. 87-90"
        ),
        book="Covenants",
    ),
    RuleOption(
        key=RESEARCH_AIDS_STACK,
        label="Research aids stack",
        brief="Realia and expert correspondence both add to research.",
        group=LIBRARY,
        effect=(
            "A realia collection's +1 and an expert correspondence's level "
            "both add to a library's research on the same subject; off, the "
            "two together add one."
        ),
        source=(
            "Covenants, Chapter Seven: Library, Other Opus Types, p. 90, and "
            "Realia, p. 102 (a house rule: the book doesn't say)"
        ),
        book="Covenants",
    ),
    RuleOption(
        key="bruises",
        label="Bruises",
        brief="Non-lethal blows leave bruises instead of costing Fatigue.",
        group=DICE,
        effect=(
            "Non-lethal blows deal bruises instead of costing Fatigue: a "
            "bruise's penalty works as a wound's, it heals within hours, and "
            "a Heavy or worse one leaves a residual wound."
        ),
        source="Lords of Men, Chapter Nine: Non-Lethal Combat, pp. 131-132",
        book="LoM",
    ),
    RuleOption(
        key="art_academe_medicine",
        label="Art & Academe medicine",
        brief="A disease is its own record, with stages and its own treatment.",
        group=MAGI,
        effect=(
            "A disease is its own record instead of a wound: it has a stage "
            "(Minor, Serious, Major, Critical), a Severity and its own Ease "
            "Factors, its Disease Penalty adds to the Wound Penalty, and it "
            "rolls to recover at its interval, twice a day in a Crisis. A "
            "physician's Medicine helps only when his Prognosis Total beats "
            "the Severity, and the patient's surroundings are Recovery "
            "Modifiers. An injury heals with first aid and palliative care "
            "(half a chirurgeon's Chirurgy each, together at most the "
            "nurse's Chirurgy) instead of the medic's whole Chirurgy, and a "
            "chirurgeon can operate on a disease or intervene when a wound "
            "worsens, at a lasting cost."
        ),
        source="Art & Academe, Chapter Three: Medicine, pp. 45-62",
        book="A&A",
    ),
    RuleOption(
        key="dominion_growth",
        label="Dominion growth",
        brief="A church's aura grows with its years of worship.",
        group=REALMS,
        effect=(
            "A church's aura grows with the years of worship (3, then 4 after "
            "a year, 5 after a decade), fades once worship stops, and rises "
            "by 1 for each Faith Point above 5 in its greatest relic."
        ),
        source=(
            "Realms of Power: The Divine, Chapter Two: Heaven and Earth, "
            "Creating a Dominion Aura, pp. 11-12"
        ),
        book="RoP:D",
    ),
    RuleOption(
        key="aura_change",
        label="Auras change",
        brief="Each winter a Magic aura may strengthen or weaken.",
        group=REALMS,
        effect=(
            "Each winter a Magic aura's yearly modifier (its tethers, the "
            "magic worked there, vis spent and extracted, auras around it) "
            "may strengthen or weaken it on the books' tables; an Infernal "
            "aura inside a stronger aura erodes by 1 after as many years as "
            "its strength unless something keeps it."
        ),
        source=(
            "Realms of Power: Magic, Chapter Two: Magic Auras, pp. 7-12; "
            "Realms of Power: The Infernal, Chapter One: Infernal Auras in "
            "Play, pp. 10-12"
        ),
        book="RoP:M",
    ),
    # Young characters (Apprentices).
    RuleOption(
        key=STANDARD_APPRENTICESHIP,
        label="Standard apprenticeship model",
        brief="A magus part way through apprenticeship has experience by the year.",
        group=MAGI,
        effect=(
            "A magus created part way through his apprenticeship has, for "
            "each year of it so far, 19 xp for the first 12 years and 6 xp "
            "and 40 spell levels for each of the last 3 (a Skilled Parens 5 "
            "xp and 10 levels more, a Weak one as much less), either "
            "spendable on the other, instead of the full 240 xp and 120 "
            "levels; a finished magus keeps the 240."
        ),
        source=(
            "Apprentices, Chapter Two: Creating Young Characters, Abilities, "
            "p. 14, and A Standard Apprenticeship, pp. 15-16"
        ),
        book="App",
    ),
    # An apprentice's cantations (Apprentices).
    RuleOption(
        key="cantations_in_play",
        label="Learning cantations in play",
        brief="A spontaneous spell cast often enough can be learned as formulaic.",
        group=MAGI,
        effect=(
            "A spontaneous spell cast in play at least as many times as its "
            "level may be bought as a formulaic spell with that adventure's "
            "experience, one point a level (More, Learn a Cantation, on Known "
            "Spells); for magi as well as apprentices."
        ),
        source=(
            "Apprentices, Chapter Four: Pueritia, Optional Rule: Learning "
            "Cantations in Play, p. 46"
        ),
        book="App",
    ),
    # Copying Lab Texts by magic (Transforming Mythic Europe).
    RuleOption(
        key=HAZARDOUS_LAB_TEXTS,
        label="Hazardous Laboratory Texts",
        brief="A Lab Text badly copied by magic is risky rather than useless.",
        group=LIBRARY,
        effect=(
            "A Lab Text copied by magic below the Finesse Total that copies it "
            "flawlessly isn't useless: each use makes an extra Experimentation "
            "roll, its risk modifier half the pages spoiled in ten."
        ),
        source=(
            "Transforming Mythic Europe, Optional Rule: Hazardous Laboratory "
            "Texts, p. 103"
        ),
        book="TME",
    ),
    RuleOption(
        key=NO_MAGICAL_LAB_TEXTS,
        label="No magical copying of Lab Texts",
        brief="Every Lab Text is copied by hand.",
        group=LIBRARY,
        effect=(
            "Lab Texts are too sensitive to scribal errors to copy with Rego "
            "craft magic: each is written by hand."
        ),
        source=(
            "Transforming Mythic Europe, Optional Rule: No Magical Copying of "
            "Laboratory Texts, p. 104"
        ),
        book="TME",
    ),
    RuleOption(
        key=LARGE_LIBRARY,
        label="Rules for a Large Library",
        brief="A library's holding of a subject is one Level and Quality.",
        group=LIBRARY,
        effect=(
            "Each subject of a covenant's library has one Level and Quality, "
            "its best summa raised by the other books near it; Read a book "
            "can study the library's whole holding of a subject: Quality + 3 "
            "below its Level, its Quality for Quality more seasons at it."
        ),
        source="Transforming Mythic Europe, Rules for a Large Library, p. 105",
        book="TME",
    ),
    # Lords of Men's optional combat rules.
    RuleOption(
        key=MORALE_DISCIPLINE,
        label="Morale and Discipline for combat groups",
        brief="Combat groups can break, until their leader rallies them.",
        group=DICE,
        effect=(
            "Combat groups make Discipline and Morale rolls on the leader's "
            "Presence + Leadership; failing, they are disordered (a trained "
            "group fights as untrained, then only half an untrained group's "
            "attacks hit) or routed, until the leader rallies them; a battle "
            "event's fight shows its army's disorder."
        ),
        source="Lords of Men, Morale and Discipline, pp. 134-135",
        book="LoM",
    ),
    # Charter Strength (Transforming Mythic Europe).
    RuleOption(
        key=CHARTER_STRENGTH,
        label="Charter Strength",
        brief="A charter has two scores, and loopholes can be sought in it.",
        group=COVENANTS,
        effect=(
            "A charter between a lord and a town or covenant has two scores, "
            "the lord's and the other side's, rolled by each side's notaries "
            "when it is drafted; a season's search may find a loophole in it."
        ),
        source="Transforming Mythic Europe, Optional Rule: Charter Strength, p. 36",
        book="TME",
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

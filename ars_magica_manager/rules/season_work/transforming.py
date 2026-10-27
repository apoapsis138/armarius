"""Transforming Mythic Europe's season of copying books by magic (pp.
100-103). The rules are rules.tme_books's.

The magus casts The First Furrow Guides the Second and The Copyist's
Puissant Quill page after page over the season (he must know both),
copying the book the plan names as many times as it says. Magic neither
reads nor understands, so he needs no language, Magic Theory or Realm
Lore to copy it uncorrupted. His Finesse Total sets the copy's Quality on
the book's table; a total too low for a readable book stops the plan.
The copies lose the original's resonances and are loose sheets, unless he
binds them with Binding the Mundane Codex (a Finesse Total of 6), which
gives the sound binding's +1. A Lab Text must be copied flawlessly: a
total below what its levels need may leave a botched page that corrupts
it (Hazardous Lab Texts, a saga option, makes that an extra
Experimentation roll instead), and the No Magical Copying of Lab Texts
option forbids it.

Or a copying device does it (the Superb Scrinium, pp. 101-103): one he,
his covenant or one of its laboratories holds, with The First Furrow
Guides the Second instilled, so he needs not the spells. Each text takes
an activation of it (and of the device's Binding the Mundane Codex to
bind it), so the copies are capped at their uses a day for the season's
days. His Finesse Total still sets the Quality.
"""

from __future__ import annotations

import random

from ... import catalog
from ...models import Book, Character, EnchantedDevice, Saga, SeasonPlan
from .. import activity_groups as groups
from .. import book_seasons, enchantment, library, options
from .. import tme_books as tb
from .base import MAGI, SimpleActivity, SupplementWork, register, source

COPYING = source(tb.COPY_SOURCE, "TME")
STORY = "933-C"

COPY_BY_MAGIC = "copy_books_by_magic"
#: The kinds of book the spells copy.
COPYABLE: tuple[str, ...] = (
    "Art Summa",
    "Ability Summa",
    "Tractatus",
    "Lab Text",
    "Casting Tablet",
)
LAB_TEXTS: tuple[str, ...] = ("Lab Text", "Casting Tablet")


def knows(saga: Saga, character: Character, name: str) -> bool:
    """Whether the magus knows a spell of this name."""
    for known in character.spells_known:
        spell = catalog.find_spell(saga, known.spell_id)
        if spell is not None and spell.name.casefold() == name.casefold():
            return True
    return False


def copies(plan: SeasonPlan) -> int:
    """How many copies the plan makes (its book_level; blank is one)."""
    return max(1, plan.book_level or 1)


def _book(saga: Saga, plan: SeasonPlan) -> Book | None:
    return next((b for b in saga.books if b.id == plan.book_id), None)


def copy_devices(saga: Saga, character: Character) -> list[EnchantedDevice]:
    """The copying devices the magus can use: his own, and his covenant's
    and its laboratories', each with The First Furrow Guides the Second."""
    held = enchantment.held_by(saga, "character", character.id)
    if character.covenant_id:
        held += enchantment.covenant_devices(
            saga, character.covenant_id, every_lab=True
        )
    return [d for d in held if tb.copies_books(d)]


def _device(
    saga: Saga, character: Character, plan: SeasonPlan
) -> EnchantedDevice | None:
    if not plan.device_id:
        return None
    return next(
        (d for d in copy_devices(saga, character) if d.id == plan.device_id), None
    )


def _bound_by_device(device: EnchantedDevice | None, plan: SeasonPlan) -> bool:
    return bool(plan.quick and device is not None and tb.binds_books(device))


def _levels(saga: Saga, book: Book, plan: SeasonPlan) -> int:
    """The levels of Lab Text copied this season, all the copies together."""
    return max(1, book_seasons.text_level(book, saga)) * copies(plan)


def _problems(saga: Saga, character: Character, plan: SeasonPlan) -> list[str]:
    book = _book(saga, plan)
    if book is None or book.type not in COPYABLE:
        return ["Choose the summa, tractatus or Lab Text to copy."]
    if not library.can_read(saga, character, book):
        return [f"{character.name} can't get at {book.name}."]
    device = _device(saga, character, plan)
    if plan.device_id and device is None:
        return [
            f"Choose a copying device {character.name} can use: one with "
            f"{tb.DEVICE_COPY_EFFECT} instilled (TME p. 102)."
        ]
    missing = [name for name in tb.COPY_SPELLS if not knows(saga, character, name)]
    if missing and device is None:
        return [
            f"Copying by magic needs {' and '.join(missing)} (TME p. 100); "
            f"{character.name} doesn't know {'them' if len(missing) > 1 else 'it'}."
        ]
    if device is not None:
        bound = _bound_by_device(device, plan)
        most = tb.device_season_books(device, bound=bound)
        if most is not None and copies(plan) > most:
            a_day = tb.device_books_a_day(device, bound=bound)
            return [
                f"{device.name} copies at most {a_day} book(s) a day, one a use of "
                f"its {tb.DEVICE_COPY_EFFECT}"
                + (f" and {tb.DEVICE_BIND_EFFECT}" if bound else "")
                + f": {most} in a season (TME p. 102)."
            ]
    if (
        plan.quick
        and not _bound_by_device(device, plan)
        and not knows(saga, character, tb.BINDING_SPELL)
    ):
        return [
            f"Binding the copies needs {tb.BINDING_SPELL} (Covenants p. 97; TME "
            "p. 103)."
        ]
    total = tb.finesse_total(character)
    if plan.quick and not tb.can_bind(total):
        return [
            f"Binding the copies needs a Finesse Total of {tb.BINDING_FINESSE}; "
            f"{character.name}'s is {total} (TME p. 103)."
        ]
    if book.type in LAB_TEXTS:
        if options.is_on(saga, options.NO_MAGICAL_LAB_TEXTS):
            return [
                "This saga's option No Magical Copying of Lab Texts: each is "
                "written by hand (TME p. 104)."
            ]
        return []
    outcome = tb.copy_outcome(book.quality or 0, total)
    if not outcome.readable:
        return [
            f"A Finesse Total of {total} ({outcome.table_total} at the Quill's "
            f"Ease Factor {outcome.ease}) spoils eight pages in ten: no readable "
            "book (TME p. 100)."
        ]
    return []


def _copy(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    """The copies, at the Quality the table gives, and what they lose."""
    book = _book(saga, plan)
    if book is None:
        return
    total = tb.finesse_total(character)
    bound = plan.quick
    count = copies(plan)
    device = _device(saga, character, plan)
    if device is not None:
        a_day = tb.device_books_a_day(device, bound=_bound_by_device(device, plan))
        result.notes.append(
            f"Copied by {device.name}"
            + (f", {a_day} book(s) a day at most" if a_day is not None else "")
            + f": each text takes a use of its {tb.DEVICE_COPY_EFFECT} (TME p. 102)."
        )
    if book.type in LAB_TEXTS:
        result.books.extend(
            tb.magic_copy(book, None, "character", character.id, bound=bound)
            for _ in range(count)
        )
        result.notes.append(_lab_text_note(saga, book, plan, total))
    else:
        outcome = tb.copy_outcome(book.quality or 0, total)
        result.books.extend(
            tb.magic_copy(book, outcome.quality, "character", character.id, bound=bound)
            for _ in range(count)
        )
        pages = tb.book_pages(book)
        result.notes.append(
            f"{count} cop{'y' if count == 1 else 'ies'} of {book.name} by magic "
            f"(about {pages} pages each): Finesse Total {total}, "
            f"{outcome.table_total} at the Quill's Ease Factor {outcome.ease}, "
            f"spoils {outcome.spoiled} page(s) in ten; Quality {outcome.quality} "
            f"(the original's {book.quality or 0}) (TME pp. 100-101)."
        )
        if pages:
            result.notes.append(
                f"A mundane scribe, at {tb.SCRIBE_PAGES_PER_DAY} pages a day, takes "
                f"{tb.scribe_days(pages)} days a copy, and as many again to tidy "
                "and illuminate it (TME p. 101)."
            )
    lost = [key for key in book.craft if key in tb.LOST_CRAFT[:3]]
    if lost:
        result.notes.append(
            "The original's resonances and clarification aren't copied; rebinding "
            "with new resonant materials can replace them (TME p. 101)."
        )
    result.notes.append(
        f"Bound by {tb.BINDING_SPELL}: the sound binding's +1 under the extended "
        "Quality rules (TME p. 103)."
        if bound
        else "Left as loose sheets: bind them before they are damaged (TME p. 101)."
    )


def _lab_text_note(saga: Saga, book: Book, plan: SeasonPlan, total: int) -> str:
    levels = _levels(saga, book, plan)
    needed = tb.lab_text_needed(levels)
    copied = f"{copies(plan)} copy(ies) of {book.name}, {levels} level(s) in all"
    if needed is None:
        return (
            f"{copied}: more than a year's worth ({tb.LAB_TEXT_YEAR:,} levels, "
            "Finesse Total 17); no book gives the Finesse Total that copies so "
            "much flawlessly, so the troupe decides (TME p. 103; DE p. 307)."
        )
    if total >= needed:
        return (
            f"{copied}: a Finesse Total of {total} copies them flawlessly "
            f"({needed} needed, TME p. 103)."
        )
    spoiled = tb.spoiled_pages(total)
    if options.is_on(saga, options.HAZARDOUS_LAB_TEXTS):
        return (
            f"{copied}: a Finesse Total of {total} is below the {needed} that "
            f"copies them flawlessly; each use of a copy makes an extra "
            f"Experimentation roll at risk +{tb.hazard_risk(spoiled)} "
            "(Hazardous Laboratory Texts, TME p. 103)."
        )
    return (
        f"{copied}: a Finesse Total of {total} is below the {needed} that copies "
        "them flawlessly: a botched page may have corrupted a copy, found only "
        "when it is used, wasting that season (TME p. 103)."
    )


register(
    SimpleActivity(
        COPY_BY_MAGIC,
        "Copy books by magic",
        "A season casting Rego craft magic page by page: copies of a summa, "
        "tractatus or Lab Text at the Quality the Finesse Total gives, without "
        "the original's resonances, loose or bound by magic.",
        COPYING,
        STORY,
        hint="Exposure (2 xp), as other book work, in Finesse or Profession: Scribe.",
        who=MAGI,
        group=groups.WRITING,
    ),
    _copy,
    _problems,
)

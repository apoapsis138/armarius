"""The book form, independent of how it is drawn: its fields, what it
shows as it is filled in, the book it builds, and a book list's Add, Edit
and Delete (commands.SectionOps); and the covenant library's research
bonuses form.

The form's Spell is a "picker" field: the front-end's own chooser when it
gives a `spell_picker` (the terminal's searchable spell chooser), else a
searchable list of every spell there is."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

from . import book_kinds, catalog, sourcebooks, spell_forms
from . import book_value as bv
from . import books as bk
from . import spells as spl
from .arts import ARTS, FORMS, TECHNIQUES
from .commands import Choose, Confirm, Form, Picked, SectionOps
from .form_spec import DialogField, attr, description_field, pairs
from .markup import escape, problem
from .models import (
    BOOK_TYPES,
    DEVICE_TYPES,
    LAB_TEXT_KINDS,
    TEXT_ENCHANTMENT,
    TEXT_LONGEVITY,
    TEXT_OTHER,
    TEXT_SPELL,
    TRACTATUS_SUBJECTS,
    Book,
    Covenant,
    Saga,
)

#: The Codex select's value for binding the book into a new codex.
NEW_CODEX = "__new__"
#: The Epitome select's value for enchanting the book as a new device.
NEW_EPITOME = "__new_epitome__"


def _ability_template_prefix(name: str) -> str | None:
    """ "Area Lore: " for a templated catalog name like "Area Lore: {region}"."""
    return name.split("{", 1)[0] if "{" in name else None


def _book_ability_choice(ability: str, names: list[str]) -> tuple[str, str]:
    """(Ability select value, Ability detail) for a book's stored ability: a
    catalog name as is, or a templated family plus the filled-in blank."""
    if not ability or ability in names:
        return ability, ""
    for name in names:
        prefix = _ability_template_prefix(name)
        if prefix and ability.startswith(prefix):
            return name, ability[len(prefix) :]
    return ability, ""  # not in the catalog: kept as its own option


class _BookShows:
    """When the book form's fields show: which follows the Type (and a
    Tractatus's Subject) live, and a Lab Text's Kind too."""

    def __init__(self, saga: Saga, book: Book | None) -> None:
        self.saga = saga
        self.book = book

    def book_type(self, values: dict[str, Any]) -> str:
        return values.get("type") or ""

    def art_book(self, values: dict[str, Any]) -> bool:
        return bk.is_art_book(self.book_type(values), values.get("subject_kind") or "")

    def ability_book(self, values: dict[str, Any]) -> bool:
        return bk.is_ability_book(
            self.book_type(values), values.get("subject_kind") or ""
        )

    def templated(self, values: dict[str, Any]) -> bool:
        return self.ability_book(values) and "{" in (values.get("ability") or "")

    def lab_text(self, values: dict[str, Any]) -> bool:
        return self.book_type(values) == "Lab Text"

    def text_kind(self, values: dict[str, Any]) -> str:
        return (values.get("text_kind") or TEXT_SPELL) if self.lab_text(values) else ""

    def of_spell(self, values: dict[str, Any]) -> bool:
        return bk.records_spell(self.book_type(values), self.text_kind(values))

    def needs_level(self, values: dict[str, Any]) -> bool:
        kind = self.book_type(values)
        if kind not in bk.SPELL_TYPES:
            return bk.has_level(kind)
        if not self.of_spell(values):
            return True  # an enchantment's, a ritual's: the text's own
        spell = spl.find_spell(self.saga, values.get("spell_id"))
        if spell is None:
            # No spell chosen: ask for the spell first -- unless this is a book
            # whose typed spell is unknown, which keeps its own Level.
            return bool(attr(self.book, "spell_name", ""))
        return spell.level is None


def _book_identity_fields(
    book: Book | None, default_type: str, shows: _BookShows
) -> list[DialogField]:
    """Name, Type and a Lab Text's Kind."""
    return [
        DialogField("name", "Name", "text", attr(book, "name", ""), required=True),
        DialogField(
            "type",
            "Type",
            "select",
            attr(book, "type", default_type),
            options=pairs(BOOK_TYPES),
            required=True,
            allow_blank=True,
            placeholder="(choose a Type)",
        ),
        DialogField(
            "text_kind",
            "Kind",
            "select",
            attr(book, "text_kind", "") or TEXT_SPELL,
            options=pairs(LAB_TEXT_KINDS),
            show_if=shows.lab_text,
        ),
    ]


def _book_subject_fields(
    saga: Saga,
    book: Book | None,
    shows: _BookShows,
    spell_picker: Callable[[Any], Any] | None = None,
) -> list[DialogField]:
    """What the book is about: its Art, Ability or spell, or a Lab Text's own
    Technique and Form."""
    ability_names = [a.name for a in catalog.load_ability_catalog()]
    ability, ability_detail = _book_ability_choice(
        attr(book, "ability", ""), ability_names
    )
    ability_options = pairs(ability_names)
    if ability and ability not in ability_names:
        ability_options.insert(0, (ability, ability))

    # A Lab Text / Casting Tablet takes its spell's Level; only a General (or
    # not yet chosen) spell needs the book's own.
    linked = bk.book_spell(saga, book) if book is not None else None
    spell_id = linked.id if linked is not None else None

    def spell_display(chosen_id: str) -> str:
        spell = spl.find_spell(saga, chosen_id)
        if spell is None:
            return chosen_id
        return f"{spell.name}  ({spl.shorthand(spell)})"

    return [
        DialogField(
            "subject_kind",
            "Subject",
            "select",
            attr(book, "subject_kind", ""),
            options=pairs(TRACTATUS_SUBJECTS),
            required=True,
            allow_blank=True,
            placeholder="(Art or Ability)",
            show_if=lambda v: shows.book_type(v) == "Tractatus",
        ),
        DialogField(
            "art",
            "Art",
            "select",
            attr(book, "art", ""),
            options=pairs(ARTS),
            required=True,
            allow_blank=True,
            placeholder="(choose an Art)",
            show_if=shows.art_book,
        ),
        DialogField(
            "ability",
            "Ability",
            "select",
            ability,
            options=ability_options,
            required=True,
            allow_blank=True,
            placeholder="(choose an Ability)",
            show_if=shows.ability_book,
        ),
        DialogField(
            "ability_detail",
            "Ability detail",
            "text",
            ability_detail,
            placeholder="fills the {blank}, e.g. Rhine Tribunal",
            show_if=shows.templated,
        ),
        _spell_field(saga, book, spell_id, spell_display, shows, spell_picker),
        DialogField(
            "technique",
            "Technique",
            "select",
            attr(book, "technique", ""),
            options=pairs(TECHNIQUES),
            allow_blank=True,
            placeholder="(not recorded)",
            show_if=lambda v: shows.text_kind(v) in (TEXT_ENCHANTMENT, TEXT_OTHER),
        ),
        DialogField(
            "form",
            "Form",
            "select",
            attr(book, "form", ""),
            options=pairs(FORMS),
            allow_blank=True,
            placeholder="(not recorded)",
            show_if=lambda v: shows.text_kind(v) in (TEXT_ENCHANTMENT, TEXT_OTHER),
        ),
    ]


def _spell_field(
    saga: Saga,
    book: Book | None,
    spell_id: str | None,
    spell_display: Callable[[str], str],
    shows: _BookShows,
    spell_picker: Callable[[Any], Any] | None,
) -> DialogField:
    """The spell a Lab Text or Casting Tablet records, chosen from every
    spell there is: by the front-end's own `spell_picker` when it has one,
    else by a searchable list (spell_forms.spell_choices)."""
    unknown = spell_id is None and attr(book, "spell_name", "")

    def choose(_current: Any) -> Choose:
        return Choose(
            "Choose the spell",
            lambda: spell_forms.spell_choices(saga, set()),
            Picked,
            empty="(no spells)",
            others=lambda: spell_forms.spell_choices(saga, set(), in_play=False),
        )

    return DialogField(
        "spell_id",
        "Spell",
        "picker",
        spell_id,
        placeholder=(
            f"Unknown: {attr(book, 'spell_name', '')} -- choose the spell..."
            if unknown
            else "(choose the spell...)"
        ),
        picker=spell_picker,
        choose=choose,
        display=spell_display,
        show_if=shows.of_spell,
    )


def _book_level_fields(book: Book | None, shows: _BookShows) -> list[DialogField]:
    """Level and Quality, for the types that have them."""
    return [
        DialogField(
            "level",
            "Level",
            "optint",
            attr(book, "level", None),
            required=True,
            hint="",
            show_if=shows.needs_level,
        ),
        DialogField(
            "quality",
            "Quality",
            "optint",
            attr(book, "quality", None),
            required=True,
            show_if=lambda v: bk.has_quality(shows.book_type(v)),
        ),
    ]


def _book_kind_fields(
    saga: Saga, book: Book | None, shows: _BookShows
) -> list[DialogField]:
    """What kind of work and copy it is (book_kinds): a tractatus can be a
    commentary on a summa; any book can be an exemplar, flap-bound..."""
    summae = [
        (b.name or "(untitled)", b.id)
        for b in saga.books
        if b.type in bk.SUMMA_TYPES and b is not book
    ]

    def commentary(values: dict[str, Any]) -> bool:
        return (
            shows.book_type(values) == "Tractatus"
            and values.get("opus") == book_kinds.COMMENTARY
        )

    books = sourcebooks.saga_books(saga)
    opus = book_kinds.offered(book_kinds.OPUS_TYPES, books, attr(book, "opus", ""))
    forms = book_kinds.offered(
        book_kinds.PHYSICAL_FORMS, books, attr(book, "physical_form", "")
    )
    # What a book out of play adds is left off, unless this book uses it.
    hidden: set[str] = set()
    if not opus:
        hidden |= {"opus", "commentary_on"}
    if not forms:
        hidden.add("physical_form")
    if not (
        sourcebooks.in_play(book_kinds.EPITOME_BOOK, books)
        or attr(book, "device_id", None)
    ):
        hidden.add("epitome")
    if not (
        sourcebooks.in_play(book_kinds.GLOSS.book, books)
        or attr(book, "glossed", False)
    ):
        hidden.add("glossed")
    fields = [
        DialogField(
            "opus",
            "Opus",
            "select",
            attr(book, "opus", "") or None,
            options=[(k.name, k.name) for k in opus],
            allow_blank=True,
            placeholder="(an ordinary tractatus)",
            hint=" ".join(f"{k.name}: {k.summary}" for k in opus),
            show_if=lambda v: shows.book_type(v) == "Tractatus",
        ),
        DialogField(
            "commentary_on",
            "Commentary on",
            "select",
            attr(book, "commentary_on", None),
            options=summae,
            allow_blank=True,
            placeholder="(its summa isn't in the saga)",
            show_if=commentary,
        ),
        DialogField(
            "epitome",
            "Epitome",
            "select",
            attr(book, "device_id", None),
            options=[(d.name, d.id) for d in saga.enchanted_devices]
            + [("(enchant it: a new invested device)", NEW_EPITOME)],
            allow_blank=True,
            placeholder="(not enchanted)",
            hint="A book enchanted as an item: material level 2, size x4; the "
            "Book shape gives +6 changing thoughts or images, +4 numerology, "
            "+3 divination.",
        ),
        DialogField(
            "glossed",
            "Glossed (+1)",
            "check",
            bool(attr(book, "glossed", False)),
            hint="Annotated by a reader at least half as skilled as its Level, "
            "with better Communication than the author (a Read season can do "
            "it); +1 once.",
            show_if=lambda v: bk.has_quality(shows.book_type(v)),
        ),
        DialogField(
            "physical_form",
            "Physical form",
            "select",
            attr(book, "physical_form", "") or None,
            options=[
                (f"{k.name} ({k.quality:+d} Quality)" if k.quality else k.name, k.name)
                for k in forms
            ],
            allow_blank=True,
            placeholder="(an ordinary bound book)",
        ),
        *_craft_fields(saga, book, shows),
    ]
    return [f for f in fields if f.key not in hidden]


#: The book form's craftsmanship checkboxes (book_kinds.CRAFT keys), by
#: field key; resonant materials are a choice of their own.
_CRAFT_CHECKS: dict[str, str] = {
    "craft_scribe": "scribe",
    "craft_binder": "binder",
    "craft_illuminator": "illuminator",
    "craft_clarified": "clarified",
}


def _craft_fields(
    saga: Saga, book: Book | None, shows: _BookShows
) -> list[DialogField]:
    """Under the extended book Quality rule: who made the book, and how
    (book_kinds.CRAFT), each adding to its Quality."""
    if not bk.extended_quality(saga):
        return []
    craft = list(attr(book, "craft", []) or [])

    def has_quality(values: dict[str, Any]) -> bool:
        return bk.has_quality(shows.book_type(values))

    fields = [
        DialogField(
            key,
            book_kinds.CRAFT[part].name + f" (+{book_kinds.CRAFT[part].quality})",
            "check",
            part in craft,
            hint="A professional with a Profession score of 6 or more."
            if key == "craft_scribe"
            else "",
            show_if=has_quality,
        )
        for key, part in _CRAFT_CHECKS.items()
        if part != "clarified"
    ]
    resonance = next((p for p in book_kinds.RESONANCE if p in craft), None)
    fields.append(
        DialogField(
            "craft_resonance",
            "Resonant materials",
            "select",
            resonance,
            options=[
                (f"{book_kinds.CRAFT[p].name} +{book_kinds.CRAFT[p].quality}", p)
                for p in book_kinds.RESONANCE
            ],
            allow_blank=True,
            placeholder="(none)",
            show_if=has_quality,
        )
    )
    fields += [
        DialogField(
            key,
            book_kinds.CRAFT[part].name + f" (+{book_kinds.CRAFT[part].quality})",
            "check",
            part in craft,
            hint="Enchanted to express its resonances: needs resonant "
            "materials and an author with the Art at 15.",
            show_if=has_quality,
        )
        for key, part in _CRAFT_CHECKS.items()
        if part == "clarified"
    ]
    return fields


def _lab_text_fields(book: Book | None, shows: _BookShows) -> list[DialogField]:
    """An enchantment's effect and device, or a Longevity Ritual's subject."""
    return [
        DialogField(
            "effect_rdt",
            "Range / Duration / Target",
            "text",
            attr(book, "effect_rdt", ""),
            placeholder="Touch / Sun / Individual",
            show_if=lambda v: shows.text_kind(v) == TEXT_ENCHANTMENT,
        ),
        DialogField(
            "device_type",
            "Device",
            "select",
            attr(book, "device_type", ""),
            options=pairs((*DEVICE_TYPES, "Talisman")),
            allow_blank=True,
            placeholder="(not recorded)",
            show_if=lambda v: shows.text_kind(v) == TEXT_ENCHANTMENT,
        ),
        DialogField(
            "shape_material",
            "Shape and material",
            "text",
            attr(book, "shape_material", ""),
            show_if=lambda v: shows.text_kind(v) == TEXT_ENCHANTMENT,
        ),
        DialogField(
            "ritual_subject",
            "Ritual's subject",
            "text",
            attr(book, "ritual_subject", ""),
            show_if=lambda v: shows.text_kind(v) == TEXT_LONGEVITY,
        ),
        DialogField(
            "ritual_extra_vis",
            "Extra vis (each time)",
            "int",
            attr(book, "ritual_extra_vis", 0),
            hint="Pawns beyond age / 5 the ritual was first made with: spent "
            "again whenever it is performed.",
            show_if=lambda v: shows.text_kind(v) == TEXT_LONGEVITY,
        ),
    ]


def _book_authorship_fields(
    saga: Saga, book: Book | None, shows: _BookShows
) -> list[DialogField]:
    """Language, author and when it was written."""
    return [
        DialogField("language", "Language", "text", attr(book, "language", "Latin")),
        DialogField("author", "Author", "text", attr(book, "author", "")),
        DialogField(
            "author_id",
            "Author's sheet",
            "select",
            attr(book, "author_id", None),
            options=[(c.name, c.id) for c in saga.characters if c.type == "magus"],
            allow_blank=True,
            placeholder="(not a magus of this saga)",
            hint="Links the text to its author: the Sigil shown, and whose "
            "texts a reader has decoded.",
            show_if=shows.lab_text,
        ),
        DialogField(
            "raw",
            "Raw (author's shorthand)",
            "check",
            bool(attr(book, "raw", False)),
            hint="Only the author, and whoever has decoded his texts, can use "
            "it until he rewrites it.",
            show_if=shows.lab_text,
        ),
        DialogField(
            "year_published",
            "Year Published",
            "optint",
            attr(book, "year_published", None),
        ),
    ]


def _book_ownership_fields(
    saga: Saga, book: Book | None, default_owner: str
) -> list[DialogField]:
    """Who keeps the book, and the codex it is bound in."""
    codex = bk.codex_of(saga, book) if book is not None else None

    def codex_fills(values: dict[str, Any]) -> dict[str, Any]:
        """Joining a codex: the book goes where the codex is kept."""
        chosen = next((c for c in saga.codices if c.id == values.get("codex")), None)
        if chosen is None:
            return {}
        mates = [b for b in saga.books if b.codex_id == chosen.id]
        fills: dict[str, Any] = {
            "palimpsest": chosen.palimpsest,
            "encyclopedia": chosen.encyclopedia,
            "collection": chosen.collection or None,
            "florilegium_bonus": str(chosen.florilegium_bonus),
        }
        if mates:
            fills["owner"] = (
                ""
                if bk.is_unassigned(saga, mates[0])
                else bk.owner_value(mates[0].owner_kind, mates[0].owner_id)
            )
        return fills

    if book is None:
        owner = default_owner
    elif bk.is_unassigned(saga, book):
        owner = ""
    else:
        owner = bk.owner_value(book.owner_kind, book.owner_id)
    books = sourcebooks.saga_books(saga)
    collections = book_kinds.offered(
        book_kinds.COLLECTIONS, books, codex.collection if codex is not None else ""
    )
    # What a book out of play adds is left off, unless this codex uses it.
    hidden: set[str] = set()
    if not collections:
        hidden |= {"collection", "florilegium_bonus"}
    if not (
        sourcebooks.in_play(book_kinds.PALIMPSEST_BOOK, books)
        or (codex is not None and codex.palimpsest)
    ):
        hidden.add("palimpsest")
    if not (
        sourcebooks.in_play(book_kinds.ENCYCLOPEDIA_BOOK, books)
        or (codex is not None and codex.encyclopedia)
    ):
        hidden.add("encyclopedia")
    fields = [
        DialogField(
            "owner",
            "Owner",
            "select",
            owner,
            options=bk.owner_options(saga),
            hint="The books bound in its codex move with it.",
        ),
        DialogField(
            "codex",
            "Codex",
            "select",
            book.codex_id if book is not None and codex is not None else None,
            options=[(c.name, c.id) for c in saga.codices]
            + [("(a new codex)", NEW_CODEX)],
            allow_blank=True,
            placeholder="(bound on its own)",
            hint="Bound with other books: each is studied on its own, one "
            "reader a season for the whole codex.",
            fills=codex_fills,
        ),
        DialogField(
            "codex_name",
            "New codex's name",
            "text",
            attr(book, "name", ""),
            show_if=lambda v: v.get("codex") == NEW_CODEX,
        ),
        DialogField(
            "palimpsest",
            "Palimpsest",
            "check",
            bool(codex is not None and codex.palimpsest),
            hint="Written over a scraped text: each text in the codex is read "
            "at -3 Quality.",
            show_if=lambda v: bool(v.get("codex")),
        ),
        DialogField(
            "encyclopedia",
            "Encyclopedia",
            "check",
            bool(codex is not None and codex.encyclopedia),
            hint="A series of tractatus that also aids research: +1 per "
            "tractatus on the subject.",
            show_if=lambda v: bool(v.get("codex")),
        ),
        DialogField(
            "collection",
            "Collection",
            "select",
            (codex.collection or None) if codex is not None else None,
            options=[(k.name, k.name) for k in collections],
            allow_blank=True,
            placeholder="(neither)",
            hint=" ".join(f"{k.name}: {k.summary}" for k in collections),
            show_if=lambda v: bool(v.get("codex")),
        ),
        DialogField(
            "florilegium_bonus",
            "Florilegium bonus",
            "select",
            str(codex.florilegium_bonus if codex is not None else 1),
            options=[
                ("+1", "1"),
                ("+2 (edited by an authority, from a peerless collection)", "2"),
            ],
            show_if=lambda v: (
                bool(v.get("codex")) and v.get("collection") == book_kinds.FLORILEGIUM
            ),
        ),
    ]
    return [f for f in fields if f.key not in hidden]


def book_fields(
    saga: Saga,
    book: Book | None,
    default_owner: str,
    default_type: str = "",
    *,
    spell_picker: Callable[[Any], Any] | None = None,
) -> list[DialogField]:
    """The add/edit form for a book. Which of Art/Ability/Spell, Level and
    Quality are shown follows the Type (and a Tractatus's Subject) live; a
    Lab Text's follow its Kind too: a spell's text names the
    spell, any other its own Technique, Form and Level, with an
    enchantment's effect and device or a Longevity Ritual's subject. A new
    book starts as `default_type` (the Lab Texts list adds Lab Texts).
    `spell_picker`: the front-end's spell chooser, for the Spell field."""
    shows = _BookShows(saga, book)
    return [
        *_book_identity_fields(book, default_type, shows),
        *_book_subject_fields(saga, book, shows, spell_picker),
        *_book_level_fields(book, shows),
        *_book_kind_fields(saga, book, shows),
        *_lab_text_fields(book, shows),
        *_book_authorship_fields(saga, book, shows),
        *_book_ownership_fields(saga, book, default_owner),
        description_field(attr(book, "description", "")),
    ]


def _bind_from_values(book: Book, values: dict[str, Any], saga: Saga) -> None:
    """The form's Codex and Owner: bind the book (into a new codex, an
    existing one, or on its own), then give it -- and so its whole codex --
    the chosen owner."""
    chosen = values.get("codex") or None
    if chosen == NEW_CODEX:
        codex = bk.new_codex(saga, values.get("codex_name") or book.name)
    else:
        codex = next((c for c in saga.codices if c.id == chosen), None)
    book.codex_id = codex.id if codex is not None else None
    if codex is not None:
        # A field the form left off (its book out of play) keeps the codex's.
        if "palimpsest" in values:
            codex.palimpsest = bool(values["palimpsest"])
        if "encyclopedia" in values:
            codex.encyclopedia = bool(values["encyclopedia"])
        if "collection" in values:
            codex.collection = values["collection"] or ""
            codex.florilegium_bonus = int(values.get("florilegium_bonus") or 1)
    kind, owner_id = bk.parse_owner_value(values.get("owner"))
    bk.set_owner(saga, book, kind, owner_id)
    bk.prune_codices(saga)


def book_from_values(book: Book, values: dict[str, Any], saga: Saga) -> None:
    """Write a book form's result onto `book`. Fields the chosen Type doesn't
    use (hidden in the form, so absent from `values`) are cleared."""
    book.name = values["name"]
    book.type = values["type"]
    book.language = values.get("language", "")
    book.author = values.get("author", "")
    book.year_published = values.get("year_published")
    book.description = values.get("description", "")
    _bind_from_values(book, values, saga)
    book.subject_kind = values.get("subject_kind") or ""
    book.art = values.get("art") or ""
    ability = values.get("ability") or ""
    prefix = _ability_template_prefix(ability)
    if prefix is not None:
        ability = prefix + values.get("ability_detail", "")
    book.ability = ability
    lab_text = book.type == "Lab Text"
    book.text_kind = (values.get("text_kind") or TEXT_SPELL) if lab_text else ""
    of_spell = bk.needs_spell(book)
    book.spell_id = values.get("spell_id") if of_spell else None
    if not of_spell:
        book.spell_name = ""
    book.technique = values.get("technique") or ""
    book.form = values.get("form") or ""
    if book.text_kind == TEXT_LONGEVITY:
        # A Longevity Ritual is always Creo Corpus.
        book.technique, book.form = "Creo", "Corpus"
    book.effect_rdt = values.get("effect_rdt") or ""
    book.device_type = values.get("device_type") or ""
    book.shape_material = values.get("shape_material") or ""
    book.ritual_subject = values.get("ritual_subject") or ""
    book.ritual_extra_vis = max(0, values.get("ritual_extra_vis") or 0)
    book.author_id = (values.get("author_id") or None) if lab_text else None
    book.raw = bool(values.get("raw")) if lab_text else False
    author = saga.character(book.author_id)
    if author is not None and not book.author:
        book.author = author.name
    book.level = values.get("level")
    spell = spl.find_spell(saga, book.spell_id)
    if spell is not None:
        # A copy for display without the saga; level_of() reads the spell.
        book.spell_name = spell.name
        if spell.level is not None:
            book.level = spell.level
    book.quality = values.get("quality")
    _kinds_from_values(book, values, saga)


def _kinds_from_values(book: Book, values: dict[str, Any], saga: Saga) -> None:
    """The form's opus type, physical form and (under the extended book
    Quality rule) craftsmanship, onto `book`."""
    book.opus = (values.get("opus") or "") if book.type == "Tractatus" else ""
    commentary = book.opus == book_kinds.COMMENTARY
    book.commentary_on = (values.get("commentary_on") or None) if commentary else None
    book.physical_form = values.get("physical_form") or ""
    book.glossed = bool(values.get("glossed")) and bk.has_quality(book.type)
    epitome = values.get("epitome") or None
    if epitome == NEW_EPITOME:
        bk.enchant_as_epitome(saga, book)
    else:
        book.device_id = epitome
    if bk.extended_quality(saga):
        craft = [part for key, part in _CRAFT_CHECKS.items() if values.get(key)]
        if values.get("craft_resonance"):
            craft.append(values["craft_resonance"])
        book.craft = craft if bk.has_quality(book.type) else []


def book_live(values: dict[str, Any], saga: Saga, editing: Book | None = None) -> str:
    """The form's live line. For a covenant still In Creation: the Build
    Point cost (a Lab Text's or Casting Tablet's from its spell's level) and
    any covenant-creation limit the values go over (a warning, not an
    error). Otherwise Build Points don't matter: only the
    Level a spell gives the book."""
    owner_kind, owner_id = bk.parse_owner_value(values.get("owner"))
    probe = Book(
        id="",
        name="",
        type=values.get("type") or "Other",
        owner_kind=owner_kind,
        owner_id=owner_id,
    )
    probe.text_kind = values.get("text_kind") or ""
    probe.spell_id = values.get("spell_id") if bk.needs_spell(probe) else None
    spell = spl.find_spell(saga, probe.spell_id)
    from_spell = (
        f"Level {spell.level}, from the spell"
        if spell is not None and spell.level is not None
        else ""
    )
    if not bk.priced(saga, probe):
        return f"[dim]{from_spell}[/]" if from_spell else ""
    if not values.get("type"):
        return "[dim]Cost: choose a Type.[/]"
    probe.level = values.get("level") if bk.has_level(probe.type) else None
    probe.quality = values.get("quality") if bk.has_quality(probe.type) else None
    if bk.pooled(probe.type):
        # Bought as a pool: what the covenant's pool comes to with this one
        # (in place of `editing`, the book being edited).
        others = [
            b
            for b in bk.books_owned_by(saga, "covenant", probe.owner_id or "")
            if b is not editing
        ]
        level = bk.level_of(probe, saga) or 0
        pool = bk.pool([*others, probe], probe.type, saga)
        lines = [
            f"[b]Cost:[/] part of the {probe.type} pool, which with these "
            f"{level} levels comes to {bk.pool_text(pool)}"
        ]
    else:
        lines = [f"[b]Cost:[/] {bk.cost(probe, saga)} Build Points"]
    if from_spell:
        lines[0] += f"  [dim]({from_spell})[/]"
    lines += [problem(escape(w)) for w in bk.limit_warnings(probe)]
    return "\n".join(lines)


def research_fields(saga: Saga, covenant: Covenant) -> list[DialogField]:
    """The covenant library's research bonus per subject: a drop-down for
    each Art or Ability it has a book on, with what it holds as a guide."""
    options = [(label, str(level)) for level, label in bv.RESEARCH_LEVELS]
    fields: list[DialogField] = []
    for i, (subject, books) in enumerate(bv.library_subjects(saga, covenant).items()):
        fields.append(
            DialogField(
                f"research_{i}",
                subject,
                "select",
                str(covenant.library_research.get(subject, 0)),
                options=options,
                hint=bv.guide_text(saga, covenant, subject, books),
            )
        )
        fields.append(
            DialogField(
                f"pictorial_{i}",
                "  Pictorial works (+1)",
                "check",
                subject in covenant.pictorial_works,
            )
        )
    return fields


def research_from_values(
    saga: Saga, covenant: Covenant, values: dict[str, Any]
) -> None:
    """Write the research form's levels onto the covenant (None dropped).
    Its fields are numbered in library_subjects' order."""
    levels = dict(covenant.library_research)
    for i, subject in enumerate(bv.library_subjects(saga, covenant)):
        level = int(values.get(f"research_{i}") or 0)
        if level:
            levels[subject] = level
        else:
            levels.pop(subject, None)
    covenant.library_research = levels
    covenant.pictorial_works = [
        subject
        for i, subject in enumerate(bv.library_subjects(saga, covenant))
        if values.get(f"pictorial_{i}")
    ]


# A book list's Add, Edit and Delete


def book_title(book: Book | None) -> str:
    return "Add a Book" if book is None else f"Edit {escape(book.name or 'this book')}"


def book_form(
    saga: Saga,
    book: Book | None,
    default_owner: str,
    default_type: str = "",
    *,
    spell_picker: Callable[[Any], Any] | None = None,
) -> Form:
    """Add (`book` None) or edit a book; a new one is kept by
    `default_owner` (books.owner_value) unless the form says otherwise."""

    def apply(values: dict[str, Any]) -> None:
        target = book
        if target is None:
            target = bk.add_book(saga, values["name"], values["type"])
        book_from_values(target, values, saga)

    return Form(
        book_title(book),
        lambda: book_fields(
            saga, book, default_owner, default_type, spell_picker=spell_picker
        ),
        apply,
        validate=bk.form_problem,
        live=lambda values: book_live(values, saga, book),
    )


def delete_book(saga: Saga, book: Book) -> Confirm:
    """Delete `book`, after confirming (a codex it leaves empty goes too)."""

    def apply() -> None:
        if book in saga.books:
            saga.books.remove(book)
            bk.prune_codices(saga)

    return Confirm(f"Delete {escape(book.name or 'this book')}?", apply)


def change_owner_fields(saga: Saga, books: Sequence[Book]) -> list[DialogField]:
    """The new owner, then a tick for each of `books` to give them."""
    return [
        DialogField(
            "owner",
            "New owner",
            "select",
            None,
            options=bk.owner_options(saga),
            required=True,
            allow_blank=True,
            placeholder="(choose one)",
        ),
        *(
            DialogField(f"book_{index}", book.name or "(untitled)", "check", False)
            for index, book in enumerate(books)
        ),
    ]


def change_owner(saga: Saga, books: Sequence[Book]) -> Form:
    """Give several of `books` one new owner (the only edit that makes
    sense for many at once), confirming first."""

    def ticked(values: dict[str, Any]) -> list[Book]:
        return [b for i, b in enumerate(books) if values.get(f"book_{i}")]

    def apply(values: dict[str, Any]) -> Confirm:
        chosen = ticked(values)
        owner = values["owner"]
        label = next(lbl for lbl, value in bk.owner_options(saga) if value == owner)
        plural = "s" if len(chosen) != 1 else ""

        def move() -> None:
            kind, owner_id = bk.parse_owner_value(owner)
            for book in chosen:
                bk.set_owner(saga, book, kind, owner_id)

        return Confirm(
            f"Changing ownership of {len(chosen)} book{plural} to "
            f"[b]{escape(label)}[/]. Continue?",
            move,
            yes_label="Change",
        )

    return Form(
        "Change the owner of several books",
        lambda: change_owner_fields(saga, books),
        apply,
        validate=lambda values: None if ticked(values) else "Tick at least one book.",
        live=lambda values: f"{len(ticked(values))} of {len(books)} books ticked",
        save_label="Change",
    )


def book_ops(
    saga: Saga,
    books: Callable[[], Sequence[Book]],
    default_owner: str,
    default_type: str = "",
    *,
    listed: bool = True,
) -> SectionOps:
    """A book list's Add, Edit and Delete, by the row's index in `books()`
    (the books as the section lists them). A list that shows no books
    (`listed` False: the library's Summary) only adds."""
    if not listed:
        return SectionOps(
            add=lambda: book_form(saga, None, default_owner, default_type)
        )
    return SectionOps(
        add=lambda: book_form(saga, None, default_owner, default_type),
        edit=lambda index: book_form(saga, books()[index], default_owner, default_type),
        remove=lambda index: delete_book(saga, books()[index]),
        rows=lambda: [b.name or "(untitled)" for b in books()],
    )

"""The book form: its fields, what it shows as it is filled in, and the
book it builds."""

from __future__ import annotations

from typing import Any

from ... import books as bk
from ... import catalog
from ... import spells as spl
from ...arts import ARTS, FORMS, TECHNIQUES
from ...markup import escape, problem
from ...models import (
    BOOK_TYPES,
    DEVICE_TYPES,
    LAB_TEXT_KINDS,
    TEXT_ENCHANTMENT,
    TEXT_LONGEVITY,
    TEXT_OTHER,
    TEXT_SPELL,
    TRACTATUS_SUBJECTS,
    Book,
    Saga,
)
from ..fields import DialogField, _attr, _description_field, _pairs
from ..pickers import SpellChooserScreen


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


def _book_fields(
    saga: Saga, book: Book | None, default_owner: str, default_type: str = ""
) -> list[DialogField]:
    """The add/edit form for a book. Which of Art/Ability/Spell, Level and
    Quality are shown follows the Type (and a Tractatus's Subject) live; a
    Lab Text's follow its Kind too: a spell's text names the
    spell, any other its own Technique, Form and Level, with an
    enchantment's effect and device or a Longevity Ritual's subject. A new
    book starts as `default_type` (the Lab Texts list adds Lab Texts)."""

    ability_names = [a.name for a in catalog.load_ability_catalog()]
    ability, ability_detail = _book_ability_choice(
        _attr(book, "ability", ""), ability_names
    )
    ability_options = _pairs(ability_names)
    if ability and ability not in ability_names:
        ability_options.insert(0, (ability, ability))

    def book_type(values: dict[str, Any]) -> str:
        return values.get("type") or ""

    def art_book(values: dict[str, Any]) -> bool:
        return bk.is_art_book(book_type(values), values.get("subject_kind") or "")

    def ability_book(values: dict[str, Any]) -> bool:
        return bk.is_ability_book(book_type(values), values.get("subject_kind") or "")

    def templated(values: dict[str, Any]) -> bool:
        return ability_book(values) and "{" in (values.get("ability") or "")

    # A Lab Text / Casting Tablet takes its spell's Level; only a General (or
    # not yet chosen) spell needs the book's own.
    linked = bk.book_spell(saga, book) if book is not None else None
    spell_id = linked.id if linked is not None else None

    def spell_display(chosen_id: str) -> str:
        spell = spl.find_spell(saga, chosen_id)
        if spell is None:
            return chosen_id
        return f"{spell.name}  ({spl.shorthand(spell)})"

    def lab_text(values: dict[str, Any]) -> bool:
        return book_type(values) == "Lab Text"

    def text_kind(values: dict[str, Any]) -> str:
        return (values.get("text_kind") or TEXT_SPELL) if lab_text(values) else ""

    def of_spell(values: dict[str, Any]) -> bool:
        return bk.records_spell(book_type(values), text_kind(values))

    def needs_level(values: dict[str, Any]) -> bool:
        kind = book_type(values)
        if kind not in bk.SPELL_TYPES:
            return bk.has_level(kind)
        if not of_spell(values):
            return True  # an enchantment's, a ritual's: the text's own
        spell = spl.find_spell(saga, values.get("spell_id"))
        if spell is None:
            # No spell chosen: ask for the spell first -- unless this is a book
            # whose typed spell is unknown, which keeps its own Level.
            return bool(_attr(book, "spell_name", ""))
        return spell.level is None

    if book is None:
        owner = default_owner
    elif bk.is_unassigned(saga, book):
        owner = ""
    else:
        owner = bk.owner_value(book.owner_kind, book.owner_id)
    return [
        DialogField("name", "Name", "text", _attr(book, "name", ""), required=True),
        DialogField(
            "type",
            "Type",
            "select",
            _attr(book, "type", default_type),
            options=_pairs(BOOK_TYPES),
            required=True,
            allow_blank=True,
            placeholder="(choose a Type)",
        ),
        DialogField(
            "text_kind",
            "Kind",
            "select",
            _attr(book, "text_kind", "") or TEXT_SPELL,
            options=_pairs(LAB_TEXT_KINDS),
            show_if=lab_text,
        ),
        DialogField(
            "subject_kind",
            "Subject",
            "select",
            _attr(book, "subject_kind", ""),
            options=_pairs(TRACTATUS_SUBJECTS),
            required=True,
            allow_blank=True,
            placeholder="(Art or Ability)",
            show_if=lambda v: book_type(v) == "Tractatus",
        ),
        DialogField(
            "art",
            "Art",
            "select",
            _attr(book, "art", ""),
            options=_pairs(ARTS),
            required=True,
            allow_blank=True,
            placeholder="(choose an Art)",
            show_if=art_book,
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
            show_if=ability_book,
        ),
        DialogField(
            "ability_detail",
            "Ability detail",
            "text",
            ability_detail,
            placeholder="fills the {blank}, e.g. Rhine Tribunal",
            show_if=templated,
        ),
        DialogField(
            "spell_id",
            "Spell",
            "picker",
            spell_id,
            placeholder=(
                f"Unknown: {_attr(book, 'spell_name', '')} -- choose the spell..."
                if spell_id is None and _attr(book, "spell_name", "")
                else "(choose the spell...)"
            ),
            picker=lambda _current: SpellChooserScreen(saga),
            display=spell_display,
            show_if=of_spell,
        ),
        DialogField(
            "technique",
            "Technique",
            "select",
            _attr(book, "technique", ""),
            options=_pairs(TECHNIQUES),
            allow_blank=True,
            placeholder="(not recorded)",
            show_if=lambda v: text_kind(v) in (TEXT_ENCHANTMENT, TEXT_OTHER),
        ),
        DialogField(
            "form",
            "Form",
            "select",
            _attr(book, "form", ""),
            options=_pairs(FORMS),
            allow_blank=True,
            placeholder="(not recorded)",
            show_if=lambda v: text_kind(v) in (TEXT_ENCHANTMENT, TEXT_OTHER),
        ),
        DialogField(
            "level",
            "Level",
            "optint",
            _attr(book, "level", None),
            required=True,
            hint="",
            show_if=needs_level,
        ),
        DialogField(
            "quality",
            "Quality",
            "optint",
            _attr(book, "quality", None),
            required=True,
            show_if=lambda v: bk.has_quality(book_type(v)),
        ),
        DialogField(
            "effect_rdt",
            "Range / Duration / Target",
            "text",
            _attr(book, "effect_rdt", ""),
            placeholder="Touch / Sun / Individual",
            show_if=lambda v: text_kind(v) == TEXT_ENCHANTMENT,
        ),
        DialogField(
            "device_type",
            "Device",
            "select",
            _attr(book, "device_type", ""),
            options=_pairs((*DEVICE_TYPES, "Talisman")),
            allow_blank=True,
            placeholder="(not recorded)",
            show_if=lambda v: text_kind(v) == TEXT_ENCHANTMENT,
        ),
        DialogField(
            "shape_material",
            "Shape and material",
            "text",
            _attr(book, "shape_material", ""),
            show_if=lambda v: text_kind(v) == TEXT_ENCHANTMENT,
        ),
        DialogField(
            "ritual_subject",
            "Ritual's subject",
            "text",
            _attr(book, "ritual_subject", ""),
            show_if=lambda v: text_kind(v) == TEXT_LONGEVITY,
        ),
        DialogField(
            "ritual_extra_vis",
            "Extra vis (each time)",
            "int",
            _attr(book, "ritual_extra_vis", 0),
            hint="Pawns beyond age / 5 the ritual was first made with: spent "
            "again whenever it is performed.",
            show_if=lambda v: text_kind(v) == TEXT_LONGEVITY,
        ),
        DialogField("language", "Language", "text", _attr(book, "language", "Latin")),
        DialogField("author", "Author", "text", _attr(book, "author", "")),
        DialogField(
            "author_id",
            "Author's sheet",
            "select",
            _attr(book, "author_id", None),
            options=[(c.name, c.id) for c in saga.characters if c.type == "magus"],
            allow_blank=True,
            placeholder="(not a magus of this saga)",
            hint="Links the text to its author: the Sigil shown, and whose "
            "texts a reader has decoded.",
            show_if=lab_text,
        ),
        DialogField(
            "raw",
            "Raw (author's shorthand)",
            "check",
            bool(_attr(book, "raw", False)),
            hint="Only the author, and whoever has decoded his texts, can use "
            "it until he rewrites it.",
            show_if=lab_text,
        ),
        DialogField(
            "year_published",
            "Year Published",
            "optint",
            _attr(book, "year_published", None),
        ),
        DialogField("owner", "Owner", "select", owner, options=bk.owner_options(saga)),
        _description_field(_attr(book, "description", "")),
    ]


def _book_from_values(book: Book, values: dict[str, Any], saga: Saga) -> None:
    """Write a book form's result onto `book`. Fields the chosen Type doesn't
    use (hidden in the form, so absent from `values`) are cleared."""
    book.name = values["name"]
    book.type = values["type"]
    book.language = values.get("language", "")
    book.author = values.get("author", "")
    book.year_published = values.get("year_published")
    book.description = values.get("description", "")
    book.owner_kind, book.owner_id = bk.parse_owner_value(values.get("owner"))
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


def _book_live(values: dict[str, Any], saga: Saga, editing: Book | None = None) -> str:
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

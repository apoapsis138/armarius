"""The book form, as the terminal draws it: the core's (library_forms.py),
with the searchable spell chooser for its Spell."""

from __future__ import annotations

from .... import library_forms
from ....form_spec import DialogField
from ....library_forms import book_from_values as _book_from_values
from ....library_forms import book_live as _book_live
from ....library_forms import research_fields as _research_fields
from ....library_forms import research_from_values as _research_from_values
from ....models import Book, Saga
from ..pickers import SpellChooserScreen

__all__ = [
    "_book_fields",
    "_book_from_values",
    "_book_live",
    "_research_fields",
    "_research_from_values",
]


def _book_fields(
    saga: Saga, book: Book | None, default_owner: str, default_type: str = ""
) -> list[DialogField]:
    """library_forms.book_fields, its Spell chosen with SpellChooserScreen."""
    return library_forms.book_fields(
        saga,
        book,
        default_owner,
        default_type,
        spell_picker=lambda _current: SpellChooserScreen(saga),
    )

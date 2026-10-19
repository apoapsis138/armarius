"""The Create forms: a saga (and its rule options), a covenant, a character
(from a template), a laboratory and a familiar. Their fields are the
core's (creation_forms.py); this module draws the New Character form."""

from __future__ import annotations

from typing import Any

from ....forms import creation as creation_forms
from ....forms.creation import RULE_OPTION_PREFIX, saga_rule_options, template_key
from ....forms.creation import covenant_create_fields as _covenant_create_fields
from ....forms.creation import familiar_create_fields as _familiar_create_fields
from ....forms.creation import laboratory_create_fields as _laboratory_create_fields
from ....forms.creation import saga_fields as _saga_fields
from ....models import Saga
from ..fields import FieldsDialog

__all__ = [
    "RULE_OPTION_PREFIX",
    "_character_create_dialog",
    "_covenant_create_fields",
    "_familiar_create_fields",
    "_laboratory_create_fields",
    "_saga_fields",
    "saga_rule_options",
    "template_key",
]


def _character_create_dialog(
    saga: Saga, covenant_id: str | None
) -> FieldsDialog[dict[str, Any]]:
    """Create a New Character, describing the chosen Template as it is
    picked."""
    return FieldsDialog(
        "Create a New Character",
        creation_forms.character_create_fields(saga, covenant_id),
        live=creation_forms.character_create_live,
        save_label="Create",
    )

"""A laboratory's forms: its details, characteristics and features. The
fields and what they build are the core's (laboratory_forms.py), shared
with the desktop."""

from __future__ import annotations

from typing import Any

from ....form_spec import DialogField
from ....forms import laboratory as lf
from ....models import LabCharacteristics, LabFeature, Laboratory, Saga
from ..fields import FieldsDialog

NEW_FEATURE_VIRTUE = lf.NEW_FEATURE_VIRTUE


def _lab_identity_fields(saga: Saga, lab: Laboratory) -> list[DialogField]:
    return lf.identity_fields(saga, lab)


def _lab_characteristics_fields(
    characteristics: LabCharacteristics,
) -> list[DialogField]:
    return lf.characteristics_fields(characteristics)


def _lab_feature_type_dialog(
    lab: Laboratory, feature: LabFeature | None = None
) -> FieldsDialog[tuple[str | None, str]]:
    """First step of adding or editing a Feature: which Feature it is (from
    the catalog, or Custom) and the Feature Virtue it's built on. Gives
    (catalog id or None for Custom, a VirtueFlawInstance id or
    NEW_FEATURE_VIRTUE + a catalog id)."""
    return FieldsDialog(
        "Add a Feature" if feature is None else "Edit a Feature",
        lf.feature_type_fields(lab, feature),
        save_label="Next",
        build=lf.feature_type_from,
    )


def _lab_feature_dialog(
    lab: Laboratory,
    feature_id: str | None,
    virtue_vf_id: str,
    feature: LabFeature | None = None,
) -> FieldsDialog[dict[str, Any]]:
    """Second step: the Feature's name, points and Focus
    (laboratory_forms.feature_details)."""
    details = lf.feature_details(lab, feature_id, virtue_vf_id, feature)
    return FieldsDialog(
        "Add a Feature" if feature is None else "Edit a Feature",
        details.fields,
        save_label="Add" if feature is None else "Save",
        build=details.build,
    )

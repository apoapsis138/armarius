"""Ruined covenants: a place marked as a fallen covenant's site
(places.RUINED) shows a ruin, and Found a Covenant Here raises a new
covenant on it.

The rules support reviving one: the Definitive Edition's Winter Ruins
Covenant Situation is a fallen covenant its new magi have been sent to
rebuild. Founding one makes a covenant In Creation named for the ruin,
sited on its place (so it takes the place's aura), with Winter Ruins's
Boons and Hooks if asked; the place is then claimed by it and no longer
a ruin.

A ruin with a regio is founded on its surface or in one of its levels.
In a level, the covenant takes the Regio Boon (Minor: entered in several
ways; Major: only with a native guide); on the surface, the regio on its
site is the Regio Hook (Minor, or Major when its folk come out and make
trouble), with the Non-magical Regio Hook too when the regio isn't
Magical.

Pattern: Command: New Covenant's own steps, started with a prefilled
form and finished with what a ruin adds."""

from __future__ import annotations

from typing import Any

from . import catalog, creation, places
from . import covenants as cov_rules
from .commands import Form
from .form_spec import DialogField
from .forms import tribunal as tribunal_forms
from .forms.creation import covenant_create_fields
from .markup import escape
from .models import Neighbour, Saga, VirtueFlawInstance, new_instance_id
from .rules import sites

#: The Covenant Situation of a covenant raised on a ruin.
WINTER_RUINS = "situation_de_winter_ruins"

#: A covenant in a regio: its Regio Boon, by tier.
REGIO_BOONS = {"minor": "covbh_boon_minor_regio", "major": "covbh_boon_major_regio"}

#: A regio on the covenant's site that it isn't in: the Regio Hook, by
#: tier, and the Hook added when that regio isn't Magical.
REGIO_HOOKS = {"minor": "covbh_hook_minor_regio", "major": "covbh_hook_major_regio"}
NON_MAGICAL_REGIO = "covbh_hook_minor_non_magical_regio"


def _site_fields(ruin: Neighbour) -> list[DialogField]:
    """Where on a ruin with a regio the covenant stands, and the Regio
    Boon or Hook that brings."""
    shown = sites.levels(ruin)
    if not shown:
        return []
    options = [
        (
            escape(
                f"{places.level_name(ruin, level)} ({places.aura_text(ruin, level)})"
            ),
            str(level),
        )
        for level in range(len(shown) + 1)
    ]
    return [
        DialogField(
            "site",
            "Site",
            "select",
            "0",
            options=options,
            hint="The surface, or one of the ruin's regio levels: the "
            "covenant takes its aura.",
            fills=lambda values: {
                "aura_realm": sites.aura_at(ruin, int(values.get("site") or 0))[1]
            },
        ),
        DialogField(
            "regio_boon",
            "Regio Boon",
            "select",
            "minor",
            options=[
                ("Minor: entered in several ways", "minor"),
                ("Major: entered only with a native guide", "major"),
            ],
            show_if=lambda values: (values.get("site") or "0") != "0",
        ),
        DialogField(
            "regio_hook",
            "Regio Hook",
            "select",
            "minor",
            options=[
                ("Minor: a regio on the site", "minor"),
                ("Major: its folk come out and make trouble", "major"),
            ],
            hint="The covenant isn't in the ruin's regio; a regio that isn't "
            "Magical adds the Non-magical Regio Hook.",
            show_if=lambda values: (values.get("site") or "0") == "0",
        ),
    ]


def _regio_boons_hooks(ruin: Neighbour, values: dict[str, Any]) -> list[str]:
    """The Regio Boon or Hooks the covenant's site brings, by catalog id."""
    shown = sites.levels(ruin)
    if not shown:
        return []
    level = int(values.get("site") or 0)
    if level:
        return [REGIO_BOONS[values.get("regio_boon") or "minor"]]
    taken = [REGIO_HOOKS[values.get("regio_hook") or "minor"]]
    if any(sites.aura_at(ruin, i)[1] != "Magic" for i in range(1, len(shown) + 1)):
        taken.append(NON_MAGICAL_REGIO)
    return taken


def found_fields(saga: Saga, ruin: Neighbour) -> list[DialogField]:
    """New Covenant's fields, named for the ruin and in its aura's realm,
    and whether to take Winter Ruins."""
    fields = []
    for field in covenant_create_fields():
        if field.key == "name":
            field.value = ruin.name
        elif field.key == "aura_realm":
            field.value = sites.aura_at(ruin)[1]
        fields.append(field)
    fields.extend(_site_fields(ruin))
    if saga.tribunals:
        fields.append(tribunal_forms.tribunal_field(saga, None))
        fields.extend(tribunal_forms.package_fields(saga, None))
    fields.append(
        DialogField(
            "winter_ruins",
            "Take Winter Ruins",
            "check",
            True,
            hint="The Covenant Situation of a fallen covenant rebuilt: its "
            "Boons and Hooks are added.",
        )
    )
    return fields


def found(saga: Saga, ruin: Neighbour, values: dict[str, Any]) -> None:
    """Raise the covenant `values` describe on `ruin`."""
    covenant = creation.add_covenant(
        saga,
        values["name"],
        values.get("notes", ""),
        season=values.get("season") or "Spring",
        aura_realm=values.get("aura_realm") or "Magic",
    )
    covenant.tribunal_id = values.get("tribunal_id")
    tribunal_forms.save_package_fields(saga, covenant, values)
    covenant.place_id = ruin.id
    covenant.place_level = int(values.get("site") or 0)
    covenant.boons_hooks.extend(
        VirtueFlawInstance(vf_id=vf_id, id=new_instance_id())
        for vf_id in _regio_boons_hooks(ruin, values)
    )
    if values.get("winter_ruins"):
        situation = next(
            (
                s
                for s in catalog.load_covenant_situation_catalog()
                if s.id == WINTER_RUINS
            ),
            None,
        )
        if situation is not None:
            cov_rules.use_situation(covenant, cov_rules.situation_instances(situation))
    ruin.details[places.RUINED] = False
    ruin.details["claimed_by"] = covenant.id
    ruin.details["status"] = "Claimed"
    places.sync(saga)


def found_form(saga: Saga, ruin: Neighbour) -> Form:
    """Found a Covenant Here, on a ruined covenant's site."""
    return Form(
        f"Found a Covenant at {escape(ruin.name)}",
        lambda: found_fields(saga, ruin),
        lambda values: found(saga, ruin, values),
        save_label="Found",
    )

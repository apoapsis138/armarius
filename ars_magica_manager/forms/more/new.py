"""New: the records an action makes."""

from __future__ import annotations

from ... import deeds
from ...actions import NodeKind
from .. import creation as creation_forms
from .. import creature as creature_forms
from .. import neighbour as neighbour_forms
from .. import tribunal as tribunal_forms
from ..menu_refresh import makes
from ..menu_steps import covenant_id, default_magus
from .entry import MoreAction
from .rules import binds_familiar

#: This area's actions, in the order More lists them.
ENTRIES: tuple[MoreAction, ...] = (
    MoreAction(
        "create_covenant",
        "v",
        "New Covenant",
        step=lambda page: creation_forms.new_covenant_form(page.saga),
        refresh=makes("covenants"),
        menu="new",
        places=((NodeKind.SAGA, "Covenants"),),
    ),
    MoreAction(
        "create_character",
        "c",
        "New Character",
        step=lambda page: creation_forms.new_character_form(
            page.saga, covenant_id(page)
        ),
        refresh=makes("characters"),
        menu="new",
        places=(
            (NodeKind.SAGA, "Unassigned Characters"),
            # A player's own characters, on The Troupe.
            (NodeKind.SAGA, "Your Characters"),
            (NodeKind.COVENANT, "People"),
            (NodeKind.CHARACTER_GROUP, "People"),
        ),
    ),
    MoreAction(
        "create_laboratory",
        "l",
        "New Laboratory",
        step=lambda page: creation_forms.new_laboratory_form(
            page.saga, covenant_id(page)
        ),
        refresh=makes("laboratories"),
        menu="new",
        places=(
            (NodeKind.SAGA, "Unassigned Laboratories"),
            (NodeKind.COVENANT, "Laboratories"),
        ),
    ),
    MoreAction(
        "create_familiar",
        "f",
        "Bind Familiar",
        step=lambda page: creation_forms.bind_familiar_form(
            page.saga, default_magus(page)
        ),
        refresh=makes("familiars"),
        menu="new",
        places=(
            (NodeKind.CHARACTER, "Familiar"),
            (NodeKind.LABORATORY, deeds.SEASON_WORK),
        ),
        on_record=binds_familiar,
    ),
    MoreAction(
        "create_tribunal",
        "t",
        "New Tribunal",
        step=lambda page: tribunal_forms.new_tribunal_form(page.saga),
        refresh=makes("tribunals"),
        menu="new",
        places=((NodeKind.SAGA, "Tribunals"),),
    ),
    MoreAction(
        "create_neighbour",
        "b",
        "New Neighbour",
        step=lambda page: neighbour_forms.new_neighbour(page.saga),
        refresh=makes("neighbours"),
        menu="new",
        places=((NodeKind.SAGA, "Neighbours"),),
    ),
    MoreAction(
        "create_creature",
        "r",
        "New Creature",
        step=lambda page: creature_forms.new_creature_form(page.saga),
        refresh=makes("creatures"),
        menu="new",
        places=((NodeKind.SAGA, "Creatures"), (NodeKind.BESTIARY, "Creatures")),
    ),
)

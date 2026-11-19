"""When each action is offered: `available` asks the generic gates (who
may act, Player view, the books in play, a character's interests, a record
In Creation), then the action's own rule about the record on show or the
section focus is in.
"""

from __future__ import annotations

from collections.abc import Callable
from functools import partial
from typing import Any

from ... import (
    action_books,
    arms,
    catalog,
    chronicle,
    connections,
    deeds,
    giving,
    guest_stays,
    hosting,
    merges,
    mobile_covenants,
    places,
    seasons,
    selling,
    sourcebooks,
    storyguides,
    theban_customs,
    threats,
    traditions,
    viewing,
    virtual_tabletop,
    world,
)
from ... import book_value as bv
from ... import devotion as devotion_forms
from ... import familiars as fam
from ... import goods as gd
from ... import house_rules as hr
from ... import inhabitants as inh
from ... import lab_texts as lt
from ... import mystery_cults as cults_core
from ... import mystic_paths as mystic_forms
from ... import sessions as ss
from ... import spells as spl
from ...actions import (
    CREATE_PLACES,
    MORE_SECTIONS,
    RECORD_SECTION,
    SECTION_VERBS,
    ActionFacts,
    NodeKind,
    silver_purse,
)
from ...forms import acclaim as acclaim_forms
from ...forms import careers, go_to, message, sheet_roll, take_up
from ...forms import certamen_duel as certamen_forms
from ...forms import charter as charter_forms
from ...forms import hubris as hubris_forms
from ...forms import notes_goals as goal_forms
from ...forms import secrets as secret_forms
from ...forms import threshold as threshold_forms
from ...forms import tmre_divination as tmre_divination_forms
from ...forms import tmre_dreams as tmre_dream_forms
from ...forms import tmre_spirits as tmre_spirit_forms
from ...forms import tunnel as tunnel_forms
from ...models import (
    FULL,
    LINE,
    TEXT_LONGEVITY,
    Agent,
    Character,
    Covenant,
    Familiar,
    Laboratory,
    Neighbour,
    Saga,
    Session,
)
from ...models.hermetic_projects import BURNING_CITY, INTANGIBLE_ASSASSIN, LIVING_CORPSE
from ...rules import (
    activities,
    apothecary,
    casting,
    faiths,
    galdor,
    hedge_casting,
    house_magic,
    merchants,
    mobile,
    options,
    philosophy,
)
from ...rules import agents as agent_rules
from ...rules import faerie_dealings as faerie_dealing_rules
from ...rules import gauntlet as gauntlet_rules
from ...rules import goetic as goetic_rules
from ...rules import hermetic_projects as project_rules
from ...rules import sin as sin_rules
from ...rules import theban_customs as byzantine
from ...rules import tmre_alchemy as tmre_alchemy_rules
from ...sections import (
    AGENTS_SECTION,
    AHEAD_SECTION,
    CASES_SECTION,
    CHARTER_LORDS_SECTION,
    CHARTER_SECTION,
    CLAUSES_SECTION,
    CONNECTIONS_SECTION,
    COV_AHEAD_SECTION,
    COV_CHARTER_LORDS_SECTION,
    DEVICE_SECTIONS,
    FAITH_SECTION,
    GOODS_SECTION,
    GUESTS_SECTION,
    HOUSE_RULES_SECTION,
    LAB_TEXTS_SECTION,
    LIBRARY_SECTIONS,
    NEIGHBOUR_INFO_SECTION,
    NOTES_SECTION,
    ORDERS_SECTION,
    SECRETS_SECTION,
    SESSIONS_SECTION,
    STAGED_SECTION,
    WHEREABOUTS_SECTION,
)


def available(action: str, facts: ActionFacts) -> bool:
    """Whether `action` can run where the user is: what enables add / edit /
    delete and decides what More and New offer."""
    if not facts.player_may(action):
        return False
    if not viewing.offers(action):
        return False
    if not action_books.book_allows(action, facts.saga):
        return False
    if action in deeds.DEEDS and _drafting(facts):
        return False
    character = facts.selected_character
    if character is not None and deeds.hidden(deeds.interests_off(character), action):
        return False
    if action in CREATE_PLACES and facts.selected_kind not in CREATE_PLACES[action]:
        return False
    if action == "edit" and facts.selected_kind == NodeKind.SAGA:
        return True
    rule = _RECORD_RULES.get(action)
    if rule is not None:
        return rule(facts)
    in_section = _SECTION_RULES.get(action)
    if in_section is None:
        return True
    return in_section(facts, facts.active_section() or "")


def _drafting(facts: ActionFacts) -> bool:
    """Whether the record on show is In Creation: its deeds wait until it
    is In Play."""
    record = facts.creation_record()
    return record is not None and record.in_creation


# -- the actions that depend on the record on show --


def _on_saga(facts: ActionFacts) -> bool:
    return facts.selected_kind == NodeKind.SAGA


def _exports_saga(facts: ActionFacts) -> bool:
    return _on_saga(facts) and facts.can_send_files()


def _exports_cult(facts: ActionFacts) -> bool:
    return _exports_saga(facts) and bool(facts.saga.custom_cults)


def _hosts(facts: ActionFacts) -> bool:
    """Host for Players: on the saga, in the storyguide's own window, while
    it isn't hosting yet."""
    return _on_saga(facts) and not hosting.is_hosted_copy() and not hosting.HOST.running


def _stops_hosting(facts: ActionFacts) -> bool:
    return _on_saga(facts) and hosting.HOST.running


def _in_full_creation(facts: ActionFacts, *, worksheet: bool) -> bool:
    """Toggle Mode, or (`worksheet`) the creation worksheet: on a full
    record with an In Creation / In Play mode, the worksheet only while it
    is In Creation."""
    record = facts.creation_record()
    return (
        record is not None
        and facts.on_record()
        and getattr(record, "detail", FULL) == FULL
        and (not worksheet or record.in_creation)
    )


def _changes_detail(facts: ActionFacts, *, up: bool) -> bool:
    """Promote (`up`) or Demote: a character or covenant whose level of
    detail has a step that way."""
    record = facts.creation_record()
    if not isinstance(record, (Character, Covenant)) or not facts.on_record():
        return False
    step = world.promoted if up else world.demoted
    return step(record.detail) is not None


def _on_covenfolk(facts: ActionFacts) -> bool:
    """Reward or Punish and Pension: on a grog who serves a covenant, from
    his record or his Personality Traits."""
    record = facts.creation_record()
    return (
        isinstance(record, Character)
        and record.type == "grog"
        and record.animal is None
        and facts.saga.covenant(record.covenant_id) is not None
        and facts.active_section()
        in (None, RECORD_SECTION[NodeKind.CHARACTER], "section-personality-traits")
    )


def _commands_beast(facts: ActionFacts) -> bool:
    """Command the Beast: on a tamed animal's Personality Traits."""
    record = facts.creation_record()
    return (
        isinstance(record, Character)
        and record.animal is not None
        and facts.active_section() in (None, "section-personality-traits")
    )


def _gives(facts: ActionFacts) -> bool:
    found = facts.to_give()
    return found is not None and giving.blocked(facts.saga, *found) is None


def _gives_silver(facts: ActionFacts) -> bool:
    purse = silver_purse(facts)
    return (
        purse is not None and giving.blocked(facts.saga, giving.SILVER, purse) is None
    )


def _experiments(facts: ActionFacts) -> bool:
    """Experiment on a Script: a Mystagogue of one of the saga's cults with
    a degree open to an experiment."""
    character = facts.selected_character
    return (
        facts.selected_kind == NodeKind.CHARACTER
        and facts.on_record()
        and character is not None
        and bool(cults_core.experiments_for(facts.saga, character))
    )


def _has_interests(facts: ActionFacts) -> bool:
    """Interests: on a person's full record, the one sheet with Deeds, or
    a full covenant's."""
    covenant = facts.selected_covenant
    if facts.selected_kind == NodeKind.COVENANT:
        return facts.on_record() and covenant is not None and covenant.detail == FULL
    character = facts.selected_character
    return (
        facts.selected_kind == NodeKind.CHARACTER
        and facts.on_record()
        and character is not None
        and character.animal is None
        and character.detail == FULL
    )


def _exports_record(facts: ActionFacts) -> bool:
    return (
        facts.can_send_files()
        and facts.record_to_export() is not None
        and facts.on_record()
    )


def _exports_markdown(facts: ActionFacts) -> bool:
    """A character's, covenant's, laboratory's or familiar's own page: a
    record with a printed sheet."""
    record = facts.record_to_delete()
    return (
        facts.can_send_files()
        and isinstance(record, Character | Covenant | Laboratory | Familiar)
        and facts.on_record()
    )


def _updates_record(facts: ActionFacts) -> bool:
    return facts.record_to_export() is not None and facts.on_record()


def _binds_familiar(facts: ActionFacts) -> bool:
    """A magus without a familiar exists, and on a character, it is one."""
    character = facts.selected_character
    if facts.selected_kind == NodeKind.CHARACTER and (
        character is None or character.type != "magus"
    ):
        return False
    return bool(fam.unbonded_magi(facts.saga))


def _disputes(facts: ActionFacts) -> bool:
    """A character, with another to dispute with."""
    return (
        facts.selected_kind == NodeKind.CHARACTER
        and facts.on_record()
        and facts.selected_character is not None
        and len(facts.saga.characters) > 1
    )


def _makes_ligature(facts: ActionFacts) -> bool:
    """A character with Artes Liberales, Philosophiae or Medicine."""
    character = facts.selected_character
    return (
        facts.selected_kind == NodeKind.CHARACTER
        and facts.on_record()
        and character is not None
        and bool(philosophy.ligature_abilities(character))
    )


def _keeps_byzantine_custom(
    test: Callable[[Saga, Character], bool],
) -> Callable[[ActionFacts], bool]:
    """A Byzantine custom's More command: on a person's record (not an
    animal's), when `test` allows it."""

    def rule(facts: ActionFacts) -> bool:
        character = facts.selected_character
        return (
            facts.selected_kind == NodeKind.CHARACTER
            and facts.on_record()
            and character is not None
            and character.animal is None
            and test(facts.saga, character)
        )

    return rule


def _casts_hedge_magic(facts: ActionFacts) -> bool:
    """A character whose tradition has a way of casting."""
    character = facts.selected_character
    return (
        facts.selected_kind == NodeKind.CHARACTER
        and facts.on_record()
        and character is not None
        and hedge_casting.can_cast(character)
    )


def _sings(wanted: Callable[[Character], bool], facts: ActionFacts) -> bool:
    """A character with the galdor Virtue the action needs."""
    character = facts.selected_character
    return (
        facts.selected_kind == NodeKind.CHARACTER
        and facts.on_record()
        and character is not None
        and wanted(character)
    )


def _joins_traditions(facts: ActionFacts) -> bool:
    """A full or sketched character, with a tradition the saga offers or
    one they belong to."""
    character = facts.selected_character
    return (
        facts.selected_kind == NodeKind.CHARACTER
        and facts.on_record()
        and character is not None
        and character.detail != LINE
        and bool(traditions.offered(facts.saga) or character.traditions)
    )


def _deletes_record(facts: ActionFacts) -> bool:
    return facts.record_to_delete() is not None


def _bears_arms(facts: ActionFacts) -> bool:
    record = facts.record_to_delete()
    return facts.on_record() and record is not None and arms.bears_arms(record)


def _on_ruin(facts: ActionFacts) -> bool:
    return facts.on_record() and places.is_ruin(facts.record_to_delete())


def _merges_doubles(facts: ActionFacts) -> bool:
    """On the saga or the Region, while a faction shares its name with a
    character or creature (merges.py)."""
    return facts.selected_kind in (
        NodeKind.SAGA,
        NodeKind.REGION,
        NodeKind.NEIGHBOUR_GROUP,
    ) and bool(merges.doubles(facts.saga))


def _reveals(facts: ActionFacts, *, known: bool) -> bool:
    """Reveal (a record the players don't know of) or Hide from the
    Players (one they do): on a record of the world the troupe doesn't
    play (viewing.can_be_unknown)."""
    record = facts.record_to_delete()
    return (
        facts.on_record()
        and viewing.can_be_unknown(record)
        and getattr(record, "known", True) == known
    )


def _assigns_storyguide(facts: ActionFacts) -> bool:
    """Its Storyguide: on a record that can have one, with a second
    storyguide, for a storyguide who runs it (storyguides.offered)."""
    return facts.on_record() and storyguides.offered(
        facts.saga, facts.record_to_delete()
    )


def _on_region(facts: ActionFacts) -> bool:
    """On the saga or the Region (the desktop's The Region chapter)."""
    return facts.selected_kind in (
        NodeKind.SAGA,
        NodeKind.REGION,
        NodeKind.NEIGHBOUR_GROUP,
    )


def _on_dormant_threat(facts: ActionFacts) -> bool:
    return facts.on_record() and threats.is_dormant(facts.record_to_delete())


def _on_threat_under_way(facts: ActionFacts) -> bool:
    record = facts.record_to_delete()
    return (
        facts.on_record()
        and threats.is_threat(record)
        and not threats.is_dormant(record)
    )


def _goes_to(facts: ActionFacts) -> bool:
    """Go To: on a record whose page names another record. On a
    character, covenant or laboratory, whose sections have More items of
    their own, only on the record itself or its Connections."""

    record = facts.record_to_delete()
    if record is None or not go_to.has_targets(facts.saga, record):
        return False
    if isinstance(record, connections.SHOWN_ON):
        return facts.on_record() or facts.active_section() == CONNECTIONS_SECTION
    return True


#: When each action that acts on the record on show (or the saga) is
#: offered, one rule per action (Strategy, as a table).

# Sin, tarnish and the Goetic Arts (RoP: The Infernal).


def _on_traits(facts: ActionFacts) -> Character | None:
    """The character on show, from his record or his Personality Traits."""
    character = facts.selected_character
    if (
        facts.selected_kind != NodeKind.CHARACTER
        or character is None
        or facts.active_section()
        not in (None, RECORD_SECTION[NodeKind.CHARACTER], "section-personality-traits")
    ):
        return None
    return character


def _sins(facts: ActionFacts) -> bool:
    """Confidence through Sin: a trait or Flaw with a penchant for a sin."""
    character = _on_traits(facts)
    return character is not None and bool(sin_rules.sinful_traits(character))


def _influences(facts: ActionFacts) -> bool:
    """Infernal Influence: a sinner, or one who knows Infernal Lore."""
    character = _on_traits(facts)
    return character is not None and (
        bool(sin_rules.sinful_traits(character))
        or any(a.name == "Infernal Lore" for a in character.abilities)
    )


def _works_goetia(facts: ActionFacts) -> bool:
    """Ars Goetia: one who holds a Goetic Art, from his record or a
    tradition's chapter."""
    character = facts.selected_character
    section = facts.active_section() or ""
    return (
        facts.selected_kind == NodeKind.CHARACTER
        and character is not None
        and goetic_rules.holds_goetic_art(character)
        and (
            section in ("", RECORD_SECTION[NodeKind.CHARACTER])
            or section.startswith(traditions.SECTION_PREFIX)
        )
    )


# An apprentice's magic and the Gauntlet (Apprentices).


def _apprentices_character(facts: ActionFacts, *sections: str) -> Character | None:
    """The character on show, from his record or one of `sections`."""
    character = facts.selected_character
    section = facts.active_section() or ""
    if (
        facts.selected_kind != NodeKind.CHARACTER
        or character is None
        or section not in ("", RECORD_SECTION[NodeKind.CHARACTER], *sections)
    ):
        return None
    return character


def _turbulent(facts: ActionFacts) -> bool:
    """Turbulence: a Gifted character, from his record or This Season."""
    character = _apprentices_character(facts, "section-char-season")
    return character is not None and gauntlet_rules.gifted(character)


def _faces_gauntlet(facts: ActionFacts) -> bool:
    """The Gauntlet: an apprentice (the Social Status)."""
    character = _apprentices_character(facts)
    return character is not None and gauntlet_rules.apprentice(character)


def _may_lose_gift(facts: ActionFacts) -> bool:
    """Lose the Gift: a Gifted apprentice."""
    character = _apprentices_character(facts)
    return (
        character is not None
        and gauntlet_rules.apprentice(character)
        and gauntlet_rules.gifted(character)
    )


def _learns_cantation(facts: ActionFacts) -> bool:
    """Learn a Cantation: on Known Spells, with the saga option on."""
    character = _apprentices_character(facts, "section-known-spells")
    return (
        character is not None
        and facts.active_section() == "section-known-spells"
        and gauntlet_rules.cantations_in_play(facts.saga)
    )


# Art & Academe's artists and scholars.


def _academe_person(facts: ActionFacts) -> Character | None:
    """A person's record (not an animal's)."""
    character = facts.selected_character
    if (
        facts.selected_kind != NodeKind.CHARACTER
        or not facts.on_record()
        or character is None
        or character.animal is not None
    ):
        return None
    return character


def _makes_art(facts: ActionFacts) -> bool:
    """An Artist's Career: someone with a Craft or Profession."""
    character = _academe_person(facts)
    return character is not None and bool(careers.artist_crafts(character))


def _studies(facts: ActionFacts) -> bool:
    """A Scholar's Career: anyone."""
    return _academe_person(facts) is not None


# Dealing with faeries (RoP: Faerie).


def _faerie_dealer(facts: ActionFacts) -> Character | None:
    """A person on show, from his record or a tradition's chapter."""
    character = facts.selected_character
    section = facts.active_section() or ""
    if (
        facts.selected_kind != NodeKind.CHARACTER
        or character is None
        or character.animal is not None
        or not (
            section in ("", RECORD_SECTION[NodeKind.CHARACTER])
            or section.startswith(traditions.SECTION_PREFIX)
        )
    ):
        return None
    return character


def _bargains_with_faeries(facts: ActionFacts) -> bool:
    """Ars Fabulosa and A Faerie Bargain: one who holds a bargaining
    power."""
    character = _faerie_dealer(facts)
    return character is not None and faerie_dealing_rules.bargains(character)


def _offers_to_faerie(facts: ActionFacts) -> bool:
    """An Offer to Faerie: any person."""
    return _faerie_dealer(facts) is not None


# The lacuna and the pilgrim (HoH:S, The Church).


def _goes_on_pilgrimage(facts: ActionFacts, section: str) -> bool:
    """Pilgrimage: on a person's This Season (any pilgrim, grogs too: The
    Church p. 16)."""
    character = facts.selected_character
    return (
        section == "section-char-season"
        and character is not None
        and character.animal is None
    )


def _casts_in_lacuna(facts: ActionFacts, section: str) -> bool:
    """Cast in a Lacuna: on a magus's Known Spells."""
    character = facts.selected_character
    return (
        section == "section-known-spells"
        and character is not None
        and character.type == "magus"
    )


def _keeps_faith(
    action: str, books: Callable[[Saga, Character], bool]
) -> Callable[[ActionFacts], bool]:
    """A faith's More command (devotion, the saints, the mystic paths, God's
    aid, holy influence): in the Faith section of the character's Religion
    chapter, when `books` finds the saga's books give it and his faith
    offers it to him (rules.faiths.may)."""

    def rule(facts: ActionFacts) -> bool:
        character = facts.selected_character
        return (
            facts.selected_kind == NodeKind.CHARACTER
            and character is not None
            and facts.active_section() == FAITH_SECTION
            and books(facts.saga, character)
            and faiths.may(character, action)
        )

    return rule


def _rop_divine(saga: Saga) -> bool:
    return sourcebooks.in_play("RoP:D", sourcebooks.saga_books(saga))


def _exorcises(facts: ActionFacts) -> bool:
    """Perform an Exorcism: on Holy Orders, for a clergyman."""
    character = facts.selected_character
    return (
        character is not None
        and facts.active_section() == ORDERS_SECTION
        and faiths.may_exorcise(character)
    )


# Mystic paths, God's aid, the Font and the Commanding Aura.


def _walks_in_faith(
    test: Callable[[Saga, Character], bool],
) -> Callable[[ActionFacts], bool]:
    """A holy life's More commands: on a person's record or Personality
    Traits, when `test` finds the saga and the character allow it."""

    def rule(facts: ActionFacts) -> bool:
        character = _on_traits(facts)
        return (
            character is not None
            and character.animal is None
            and test(facts.saga, character)
        )

    return rule


# House Verditius's Hubris and vendettas.


def _is_proud(facts: ActionFacts) -> bool:
    """Hubris: a Verditius with the Flaw or the trait, on his Personality
    Traits."""
    character = _on_traits(facts)
    return character is not None and hubris_forms.offers(facts.saga, character)


# Hermetic spirit magic and theurgy (The Mysteries Revised Edition).


def _works_with_spirits(facts: ActionFacts) -> bool:
    """Spirits and Names: a magus with one of the Mysteries, from his
    record or his Known Spells."""
    character = facts.selected_character
    return (
        facts.selected_kind == NodeKind.CHARACTER
        and character is not None
        and facts.active_section()
        in (None, RECORD_SECTION[NodeKind.CHARACTER], "section-known-spells")
        and tmre_spirit_forms.offers(character)
    )


# Dream magic and Hermetic sacrifice (The Mysteries Revised Edition).


def _on_known_spells(
    offers: Callable[[Saga, Character], bool],
) -> Callable[[ActionFacts], bool]:
    """A Mystery's More command: on the character's record or his Known
    Spells, when `offers` allows it."""

    def rule(facts: ActionFacts) -> bool:
        character = facts.selected_character
        return (
            facts.selected_kind == NodeKind.CHARACTER
            and character is not None
            and facts.active_section()
            in (None, RECORD_SECTION[NodeKind.CHARACTER], "section-known-spells")
            and offers(facts.saga, character)
        )

    return rule


# Divination and Hermetic astrology (The Mysteries Revised Edition).


def _reads_signs(
    offers: Callable[[Saga, Character], bool],
) -> Callable[[ActionFacts], bool]:
    """Divination and Astrology: on a person's record, when `offers`
    allows it."""

    def rule(facts: ActionFacts) -> bool:
        character = facts.selected_character
        return (
            facts.selected_kind == NodeKind.CHARACTER
            and character is not None
            and character.animal is None
            and facts.active_section() in (None, RECORD_SECTION[NodeKind.CHARACTER])
            and offers(facts.saga, character)
        )

    return rule


# House Acclaim and Reputation rolls (HoH:TL, HoH:S, LoH, DE).


def _on_reputations(facts: ActionFacts) -> Character | None:
    """The character on show, from his Reputations."""
    character = facts.selected_character
    if (
        facts.selected_kind != NodeKind.CHARACTER
        or character is None
        or facts.active_section() != "section-reputations"
    ):
        return None
    return character


def _keeps_acclaim(facts: ActionFacts) -> bool:
    """House Acclaim: a magus of Bonisagus or Flambeau, or one holding it."""
    character = _on_reputations(facts)
    return character is not None and acclaim_forms.offers(facts.saga, character)


def _has_reputation(facts: ActionFacts) -> bool:
    """Reputation Roll: anyone with a Reputation."""
    character = _on_reputations(facts)
    return character is not None and bool(character.reputations)


# A covenant's Hermetic Projects (Hermetic Projects).

#: Where Begin Project is offered: the covenant's record and the
#: sections of its Overview tab.
BEGIN_PROJECT_SECTIONS = (
    None,
    RECORD_SECTION[NodeKind.COVENANT],
    "section-cov-description",
    "section-cov-reputations",
    "section-cov-boons",
    "section-cov-hooks",
)


def _staged(kind: str) -> Callable[[ActionFacts], bool]:
    """A staged project's More command: on its project's block, while a
    project of that kind is shown."""

    def rule(facts: ActionFacts) -> bool:
        covenant = facts.selected_covenant
        project = (
            project_rules.shown_project(covenant) if covenant is not None else None
        )
        return (
            project is not None
            and project.kind == kind
            and facts.active_section() == STAGED_SECTION
        )

    return rule


def _begins_project(facts: ActionFacts) -> bool:
    """Begin Project: on a full covenant's record or Overview tab."""
    covenant = facts.selected_covenant
    return (
        facts.selected_kind == NodeKind.COVENANT
        and covenant is not None
        and covenant.detail == FULL
        and facts.active_section() in BEGIN_PROJECT_SECTIONS
    )


def _has_asks(facts: ActionFacts) -> bool:
    """A character asked to teach, or asking (teaching.py)."""
    character = facts.selected_character
    return character is not None and any(
        character.id in (r.student_id, r.teacher_id) for r in facts.saga.teach_requests
    )


_RECORD_RULES: dict[str, Callable[[ActionFacts], bool]] = {
    "teaching_requests": _has_asks,
    "set_date": _on_saga,
    "undo_season": _on_saga,
    "downtime_run": _on_saga,
    "previously_on": _on_saga,
    "export_saga": _exports_saga,
    "export_cult": _exports_cult,
    "export_pack": _exports_saga,
    "host_saga": _hosts,
    "stop_hosting": _stops_hosting,
    "toggle_mode": partial(_in_full_creation, worksheet=False),
    "creation_worksheet": partial(_in_full_creation, worksheet=True),
    "promote": partial(_changes_detail, up=True),
    "demote": partial(_changes_detail, up=False),
    "give": _gives,
    "command_beast": _commands_beast,
    "discipline_grog": _on_covenfolk,
    "grog_pension": _on_covenfolk,
    "edit_traditions": _joins_traditions,
    "disputatio": _disputes,
    "hedge_cast": _casts_hedge_magic,
    "galdor_conjure": partial(_sings, galdor.conjures),
    "galdor_bargain": partial(_sings, galdor.bargains),
    "galdor_bind": partial(_sings, galdor.enchants),
    "give_silver": _gives_silver,
    "export_record": _exports_record,
    "export_markdown": _exports_markdown,
    "edit_interests": _has_interests,
    # Experiment on a Script, on a Mystagogue's record (TMRE p. 18).
    "experiment_script": _experiments,
    "update_record": _updates_record,
    "create_familiar": _binds_familiar,
    "delete_record": _deletes_record,
    "edit_arms": _bears_arms,
    "found_covenant": _on_ruin,
    "begin_story": _on_dormant_threat,
    "merge_doubles": _merges_doubles,
    "reveal": partial(_reveals, known=False),
    "conceal": partial(_reveals, known=True),
    "mark_unknown": _on_region,
    "player_view": _on_saga,
    "assign_storyguide": _assigns_storyguide,
    "delay_threat": _on_threat_under_way,
    "take_up_tale": _on_threat_under_way,
    "go_to": _goes_to,
    # A scholar's ligature (Art & Academe).
    "make_ligature": _makes_ligature,
    # The Theban Tribunal's Byzantine customs (The Sundered Eagle).
    "theban_letter": _keeps_byzantine_custom(lambda _s, _c: True),
    "invoke_oath": _keeps_byzantine_custom(lambda _s, _c: True),
    "make_greek_fire": _keeps_byzantine_custom(lambda _s, _c: True),
    "paint_icon": _keeps_byzantine_custom(
        lambda saga, c: (
            byzantine.icon_problem(c) is None and bool(theban_customs.church_list(saga))
        )
    ),
    "venerate_icon": _keeps_byzantine_custom(
        lambda saga, _c: bool(theban_customs.icon_choices(saga))
    ),
    "mothers_curse": _keeps_byzantine_custom(lambda _s, _c: True),
    # Sin, tarnish and the Goetic Arts (RoP: The Infernal).
    "indulge_sin": _sins,
    "infernal_influence": _influences,
    "ars_goetia": _works_goetia,
    # An apprentice's magic and the Gauntlet (Apprentices).
    "turbulence": _turbulent,
    "gauntlet": _faces_gauntlet,
    "lose_the_gift": _may_lose_gift,
    "learn_cantation": _learns_cantation,
    # Art & Academe's artists and scholars.
    "artist_career": _makes_art,
    "scholar_career": _studies,
    # Dealing with faeries (RoP: Faerie).
    "ars_fabulosa": _bargains_with_faeries,
    "faerie_bargain": _bargains_with_faeries,
    "faerie_offer": _offers_to_faerie,
    # Devotion and the saints (The Church, RoP: The Divine).
    "invoke_saint": _keeps_faith(
        "invoke_saint", lambda s, _c: devotion_forms.invokes(s)
    ),
    "threaten_saint": _keeps_faith(
        "threaten_saint", lambda s, _c: devotion_forms.threatens(s)
    ),
    "patron_saint": _keeps_faith(
        "patron_saint", lambda s, _c: devotion_forms.invokes(s)
    ),
    "devotion_points": _keeps_faith(
        "devotion_points", lambda s, _c: devotion_forms.the_church(s)
    ),
    "act_of_piety": _keeps_faith(
        "act_of_piety", lambda s, _c: devotion_forms.the_church(s)
    ),
    # Holy influence and tempers (RoP: The Divine).
    "holy_influence": _keeps_faith("holy_influence", lambda s, _c: _rop_divine(s)),
    # Mystic paths and God's aid in the Faith section; the Font and the
    # Commanding Aura where they act.
    "mystic_path": _keeps_faith("mystic_path", mystic_forms.offers_path),
    "spiritual_path": _keeps_faith("spiritual_path", mystic_forms.offers_spiritual),
    "monistic_revelation": _keeps_faith(
        "monistic_revelation", mystic_forms.offers_revelation
    ),
    "gods_aid": _keeps_faith("gods_aid", mystic_forms.offers_aid),
    # A Muslim's baraka and the Hajj (RoP: The Divine pp. 103-108).
    "invoke_baraka": _keeps_faith("invoke_baraka", lambda s, _c: _rop_divine(s)),
    "hajj": _keeps_faith("hajj", lambda s, _c: _rop_divine(s)),
    # A clergyman's exorcism, on Holy Orders (The Church p. 34).
    "perform_exorcism": _exorcises,
    "font_of_knowledge": _walks_in_faith(mystic_forms.offers_font),
    "commanding_aura": _walks_in_faith(mystic_forms.offers_aura),
    # House Verditius's Hubris and vendettas.
    "verditius_hubris": _is_proud,
    # Hermetic spirit magic and theurgy (The Mysteries Revised Edition).
    "spirits_and_names": _works_with_spirits,
    # Dream magic and Hermetic sacrifice (The Mysteries Revised Edition).
    "dream_working": _on_known_spells(tmre_dream_forms.offers_dreams),
    "hermetic_sacrifice": _on_known_spells(tmre_dream_forms.offers_sacrifice),
    "certamen_duel": _on_known_spells(certamen_forms.offers),
    # Divination and Hermetic astrology (The Mysteries Revised Edition).
    "tmre_divination": _reads_signs(tmre_divination_forms.offers_divination),
    "tmre_astrology": _reads_signs(tmre_divination_forms.offers_astrology),
    # House Acclaim and Reputation rolls (HoH:TL, HoH:S, LoH, DE).
    "house_acclaim": _keeps_acclaim,
    "reputation_roll": _has_reputation,
    # A covenant's Hermetic Projects: Begin Project on its record and its
    # Overview; a magus's tunnel on his Known Spells.
    "begin_project": _begins_project,
    "open_tunnel": _on_known_spells(tunnel_forms.offers),
    # A covenant's staged project, by its kind.
    "warning_bell": _staged(BURNING_CITY),
    "gather_connection": _staged(INTANGIBLE_ASSASSIN),
    "lower_aegis": _staged(INTANGIBLE_ASSASSIN),
    "death_roll": _staged(LIVING_CORPSE),
}


# -- the actions that depend on the section focus is in --


def _has_verb(action: str) -> Callable[[ActionFacts, str], bool]:
    def rule(_facts: ActionFacts, section: str) -> bool:
        return action in SECTION_VERBS.get(section, ())

    return rule


def _restores(facts: ActionFacts, section: str) -> bool:
    """Offered only while someone has departed (Magi, Companions)."""
    covenant = facts.selected_covenant
    return (
        "restore" in SECTION_VERBS.get(section, ())
        and covenant is not None
        and bool(
            inh.departed_entries_for_kind(
                facts.saga, covenant, section.removeprefix("section-inh-")
            )
        )
    )


def _with_morale_rules(action: str) -> Callable[[ActionFacts, str], bool]:
    """In its section, while the saga plays Morale and Discipline (LoM
    pp. 134-135)."""
    in_section = _in_more_section(action)

    def rule(facts: ActionFacts, section: str) -> bool:
        return in_section(facts, section) and options.is_on(
            facts.saga, options.MORALE_DISCIPLINE
        )

    return rule


def _chosen_secret(facts: ActionFacts, section: str) -> tuple[Any, int] | None:
    """The record on show and its chosen secret's row, in its Secrets list."""
    if section != SECRETS_SECTION:
        return None
    record = facts.record_to_delete()
    row = facts.chosen_row(SECRETS_SECTION)
    found = getattr(record, "secrets", None)
    if not isinstance(found, list) or row is None or not 0 <= row < len(found):
        return None
    return record, row


def _chosen_session(facts: ActionFacts, section: str) -> Session | None:
    """The Session chosen in the Sessions list, while the Virtual Tabletop
    (Preview) is on; None otherwise."""
    if section != SESSIONS_SECTION or not virtual_tabletop.on():
        return None
    row = facts.chosen_row(section)
    shown = ss.in_order(facts.saga)
    return shown[row] if row is not None and 0 <= row < len(shown) else None


def _begins_session(facts: ActionFacts, section: str) -> bool:
    session = _chosen_session(facts, section)
    return session is not None and (
        chronicle.why_not_begin(facts.saga, session, chronicle.here()) is None
    )


def _ends_session(facts: ActionFacts, section: str) -> bool:
    session = _chosen_session(facts, section)
    return session is not None and (
        chronicle.why_not_end(session, chronicle.here(), facts.saga) is None
    )


def _rolls_from_sheet(facts: ActionFacts, section: str) -> bool:
    """Roll, on a character's Abilities and Characteristics, while a
    Session is Under way and whoever uses this copy may roll for them: on
    the host with the Virtual Tabletop (Preview) on, at a Remote seat as
    its host does. One who can't act now is still offered it, and told
    why."""
    character = facts.selected_character
    if section not in (sheet_roll.ABILITIES, sheet_roll.CHARACTERISTICS):
        return False
    if character is None or chronicle.under_way(facts.saga) is None:
        return False
    if viewing.current().hosts and not virtual_tabletop.on():
        return False
    return sheet_roll.why_not_offered(facts.saga, character) is None


def _reads_chronicle(facts: ActionFacts, section: str) -> bool:
    session = _chosen_session(facts, section)
    return session is not None and chronicle.has_chronicle(facts.saga, session)


def _sends_message(facts: ActionFacts, section: str) -> bool:
    """Message, on the Session Under way, for anyone at it."""
    session = _chosen_session(facts, section)
    return session is not None and message.why_not_here(facts.saga, session) is None


def _on_secret(facts: ActionFacts, section: str, *, revealed: bool) -> bool:
    """Reveal the Secret (one not revealed) or Hide the Secret Again (one
    revealed), on the chosen row of a record's Secrets."""
    chosen = _chosen_secret(facts, section)
    return chosen is not None and chosen[0].secrets[chosen[1]].revealed == revealed


def _splits_secret(facts: ActionFacts, section: str) -> bool:
    """Split by Paragraph: on a chosen secret of several paragraphs."""
    chosen = _chosen_secret(facts, section)
    return chosen is not None and secret_forms.splits(*chosen)


def _plans_goal(facts: ActionFacts, section: str) -> bool:
    """Plan the Study Path: on a chosen goal of Notes & Goals naming an Art
    or Ability and a score, for whoever may plan the character's seasons."""
    character = facts.selected_character
    return (
        section == NOTES_SECTION
        and character is not None
        and goal_forms.plans(facts.saga, character, facts.chosen_row(NOTES_SECTION))
    )


def _in_more_section(action: str) -> Callable[[ActionFacts, str], bool]:
    def rule(_facts: ActionFacts, section: str) -> bool:
        return section == MORE_SECTIONS[action]

    return rule


def _improves(_facts: ActionFacts, section: str) -> bool:
    return section == "section-eco-income"


def _acts_on_device(action: str) -> Callable[[ActionFacts, str], bool]:
    def rule(facts: ActionFacts, section: str) -> bool:
        return section in DEVICE_SECTIONS and facts.device_action_enabled(action)

    return rule


def _shares_spell(facts: ActionFacts, section: str) -> bool:
    character = facts.selected_character
    return (
        section == "section-known-spells"
        and character is not None
        and bool(spl.shareable_spells(character))
    )


def _boosts_spell(facts: ActionFacts, section: str) -> bool:
    """On Known Spells, for a magus with a spell he may boost."""
    character = facts.selected_character
    return (
        section == "section-known-spells"
        and character is not None
        and any(
            (spell := catalog.find_spell(facts.saga, k.spell_id)) is not None
            and house_magic.can_boost(
                character, spell, casting.mastery_counts(k.mastery_abilities)
            )
            for k in character.spells_known
        )
    )


def _filters_lab_texts(_facts: ActionFacts, section: str) -> bool:
    return section == LAB_TEXTS_SECTION


def _performs_ritual(facts: ActionFacts, section: str) -> bool:
    lab = facts.selected_laboratory
    return (
        section == LAB_TEXTS_SECTION
        and lab is not None
        and any(
            lt.kind(b) == TEXT_LONGEVITY
            for b in lt.texts_of(facts.saga, "laboratory", lab.id)
        )
    )


def _research_bonuses(facts: ActionFacts, section: str) -> bool:
    """Library research values are Covenants'."""
    covenant = facts.selected_covenant
    return (
        sourcebooks.in_play(bv.SOURCE_BOOK, sourcebooks.saga_books(facts.saga))
        and facts.selected_kind == NodeKind.COVENANT
        and section in LIBRARY_SECTIONS
        and covenant is not None
        and bool(bv.library_subjects(facts.saga, covenant))
    )


def _acts_on_agent(
    test: Callable[[Character, Agent], bool],
) -> Callable[[ActionFacts, str], bool]:
    """A More command on the Agents list, offered only for a chosen agent
    it can act on (Impress only one not yet impressed)."""

    def rule(facts: ActionFacts, section: str) -> bool:
        character = facts.selected_character
        if section != AGENTS_SECTION or character is None:
            return False
        row = facts.chosen_row(section)
        return (
            row is not None
            and 0 <= row < len(character.agents)
            and test(character, character.agents[row])
        )

    return rule


def _adds_purity(facts: ActionFacts, section: str) -> bool:
    """Add a Purity, offered on the Goods list for a chosen good priced by
    purity that has a pure price."""
    if section != GOODS_SECTION:
        return False
    row = facts.chosen_row(section)
    listed = gd.listed(facts.saga)
    return row is not None and 0 <= row < len(listed) and gd.takes_purities(listed[row])


def _moves_to_source(facts: ActionFacts, section: str) -> bool:
    """Move to Source, offered on House Rules once the saga has a source
    of its own and an entry to move."""
    return (
        section == HOUSE_RULES_SECTION
        and bool(facts.saga.sources)
        and bool(hr.all_entries(facts.saga))
    )


def _grog_season(facts: ActionFacts, section: str) -> bool:
    character = facts.selected_character
    return (
        section == "section-char-season"
        and character is not None
        and not activities.is_planned(character)
    )


def _grog_has_plan(facts: ActionFacts) -> bool:
    character = facts.selected_character
    return character is not None and seasons.plan_for(facts.saga, character) is not None


def _works_for_labor(
    test: Callable[[Character], bool],
) -> Callable[[ActionFacts, str], bool]:
    """Labor Points from a Story and Invest Time or Money: on This Season,
    for a character who works for Labor Points (a trader, for most
    investments)."""

    def rule(facts: ActionFacts, section: str) -> bool:
        character = facts.selected_character
        return (
            section == "section-char-season"
            and character is not None
            and character.grog_year is None
            and test(character)
        )

    return rule


def _breaks_clause(facts: ActionFacts, section: str) -> bool:
    """Break a Clause: on the Clauses list, for a chosen clause not yet
    broken."""
    covenant = facts.selected_covenant
    return (
        section == CLAUSES_SECTION
        and covenant is not None
        and charter_forms.can_break(covenant, facts.chosen_row(section))
    )


def _censures_clause(facts: ActionFacts, section: str) -> bool:
    """Censure: on the Clauses list, for a chosen broken clause."""
    covenant = facts.selected_covenant
    return (
        section == CLAUSES_SECTION
        and covenant is not None
        and charter_forms.can_censure(covenant, facts.chosen_row(section))
    )


def _charges_clause(facts: ActionFacts, section: str) -> bool:
    """Charge at Tribunal: on a chosen broken clause of a charter that binds
    under the Peripheral Code, not charged yet."""
    covenant = facts.selected_covenant
    return (
        section == CLAUSES_SECTION
        and covenant is not None
        and charter_forms.can_charge(facts.saga, covenant, facts.chosen_row(section))
    )


def _forgets_template(facts: ActionFacts, section: str) -> bool:
    """Forget a Template: on the charter, while the saga keeps one."""
    return section == CHARTER_SECTION and bool(facts.saga.charter_templates)


def _ends_membership(facts: ActionFacts, section: str) -> bool:
    """End Membership: on the charter, while a magus expelled under it is
    still of the covenant."""
    covenant = facts.selected_covenant
    return (
        section == CHARTER_SECTION
        and covenant is not None
        and charter_forms.can_end_membership(facts.saga, covenant)
    )


def _owes_fee(facts: ActionFacts, section: str) -> bool:
    """Pay the Fee: on the Guests list, for a guest owing this year's."""
    covenant = facts.selected_covenant
    return (
        section == GUESTS_SECTION
        and covenant is not None
        and guest_stays.can_pay(facts.saga, covenant, facts.chosen_row(section))
    )


def _on_ship_row(
    can: Callable[[Covenant, int | None], bool],
) -> Callable[[ActionFacts, str], bool]:
    """Offered on the Ships list, while `can` says so of the chosen ship."""

    def rule(facts: ActionFacts, section: str) -> bool:
        covenant = facts.selected_covenant
        return (
            section == "section-pos-ship"
            and covenant is not None
            and can(covenant, facts.chosen_row(section))
        )

    return rule


def _logs_stop(facts: ActionFacts, section: str) -> bool:
    """Add a Stop: on Whereabouts, and on the top panel of a covenant with
    a Mobile Hook, as a covenant that never moves has no stops to log."""
    covenant = facts.selected_covenant
    if covenant is None:
        return False
    return section == WHEREABOUTS_SECTION or (
        section == "section-cov-info" and mobile.has_mobile_hook(covenant)
    )


def _plans_journey(_facts: ActionFacts, section: str) -> bool:
    """Travel, the calculator: on Ahead, the Seasons page's or a
    covenant's."""
    return section in (AHEAD_SECTION, COV_AHEAD_SECTION)


def _on_charter_lord(facts: ActionFacts, section: str) -> bool:
    """Draft the Charter and Seek a Loophole: on a town's or a covenant's
    charter lords, with a lord chosen, while the saga uses the Charter
    Strength rule (TME p. 36)."""
    return (
        section in (CHARTER_LORDS_SECTION, COV_CHARTER_LORDS_SECTION)
        and facts.chosen_row(section) is not None
        and options.is_on(facts.saga, options.CHARTER_STRENGTH)
    )


def _imports(facts: ActionFacts, section: str) -> bool:
    return facts.selected_kind == NodeKind.SAGA or section in LIBRARY_SECTIONS


#: When each action that depends on the active section is offered. An
#: action in neither table is always offered.
_SECTION_RULES: dict[str, Callable[[ActionFacts, str], bool]] = {
    "reveal_secret": partial(_on_secret, revealed=False),
    "conceal_secret": partial(_on_secret, revealed=True),
    "split_secret": _splits_secret,
    "plan_goal": _plans_goal,
    "add": _has_verb("add"),
    "remove": _has_verb("remove"),
    "edit": _has_verb("edit"),
    "restore": _restores,
    "improve": _improves,
    "instill_effect": _acts_on_device("instill_effect"),
    "use_charge": _acts_on_device("use_charge"),
    "use_effect": _acts_on_device("use_effect"),
    "share_spell": _shares_spell,
    "boost_spell": _boosts_spell,
    "filter_lab_texts": _filters_lab_texts,
    "perform_ritual": _performs_ritual,
    "research_bonuses": _research_bonuses,
    "import_data": _imports,
    "impress_agent": _acts_on_agent(lambda _c, agent: agent_rules.can_impress(agent)),
    "spend_agency_xp": _acts_on_agent(agent_rules.can_spend),
    "set_agent_task": _acts_on_agent(lambda _c, agent: agent_rules.may_be_asked(agent)),
    "resolve_agent_task": _acts_on_agent(
        lambda _c, agent: agent_rules.recruited(agent)
    ),
    "add_purity": _adds_purity,
    "move_to_source": _moves_to_source,
    "plan_journey": _plans_journey,
    "break_clause": _breaks_clause,
    "censure_clause": _censures_clause,
    "charge_clause": _charges_clause,
    "forget_charter_template": _forgets_template,
    "end_membership": _ends_membership,
    "pay_fee": _owes_fee,
    "add_stop": _logs_stop,
    "detach_ship": _on_ship_row(mobile_covenants.can_detach),
    "rejoin_ship": _on_ship_row(mobile_covenants.can_rejoin),
    "labor_story": _works_for_labor(lambda c: bool(merchants.work_abilities(c))),
    "invest_labor": _works_for_labor(merchants.earns_labor),
    # A grog's season of copying, on This Season: planned, then cleared.
    "plan_copying": lambda facts, section: (
        _grog_season(facts, section) and not _grog_has_plan(facts)
    ),
    "clear_copying": lambda facts, section: (
        _grog_season(facts, section) and _grog_has_plan(facts)
    ),
    # A grog's story experience (Grogs p. 67), on This Season.
    "grog_story_xp": _grog_season,
    # A place with a Faerie aura (RoP: Faerie pp. 20-24), on its record.
    "cross_threshold": lambda facts, section: (
        section == NEIGHBOUR_INFO_SECTION
        and isinstance(record := facts.record_to_export(), Neighbour)
        and threshold_forms.offers(facts.saga, record)
    ),
    # A craftsman's sale of his finished goods, on This Season.
    "sell_goods": _works_for_labor(lambda c: bool(selling.crafts(c))),
    **{action: _in_more_section(action) for action in MORE_SECTIONS},
    # A Session's Chronicle, with the Virtual Tabletop (Preview) on: these
    # replace the plain in-section rule above.
    "begin_session": _begins_session,
    "close_session": _ends_session,
    "read_chronicle": _reads_chronicle,
    "send_message": _sends_message,
    "sheet_roll": _rolls_from_sheet,
    # Lords of Men's Morale and Discipline, a saga option.
    "group_morale": _with_morale_rules("group_morale"),
    "rally_group": _with_morale_rules("rally_group"),
    # An apothecary's searching and preserving, on This Season.
    "apothecary_store": _works_for_labor(apothecary.keeps_store),
    # A chosen open story (or, on Needs You, a story or threat).
    "take_up_story": lambda facts, section: (
        section in take_up.LISTS
        and take_up.offered(
            facts.saga, section, facts.chosen_row(section), facts.selected_covenant
        )
    ),
    # The hunt and Area Lore on the road, beside Travel on Ahead.
    "hunt_on_journey": _plans_journey,
    "area_lore_on_journey": _plans_journey,
    # The lacuna and the pilgrim (HoH:S, The Church).
    "cast_in_lacuna": _casts_in_lacuna,
    "pilgrimage": _goes_on_pilgrimage,
    # Philosophic Alchemy's digestions, on This Season.
    "philosophic_alchemy": _works_for_labor(
        lambda c: bool(tmre_alchemy_rules.philosophic_tier(c))
    ),
    # The Great Elixir's test, on Aging & Warping.
    "great_elixir": lambda facts, section: (
        section == "section-aging"
        and facts.selected_character is not None
        and tmre_alchemy_rules.has_great_elixir(facts.selected_character)
    ),
    # Gaining and losing Virtues and Flaws in play (Grogs pp. 61-64).
    "change_virtues_flaws": lambda facts, section: (
        section in ("section-vf-virtues", "section-vf-flaws")
        and facts.selected_kind == NodeKind.CHARACTER
        and facts.selected_character is not None
    ),
    # Shaping the land by magic, on a covenant's Income (TME pp. 54-77).
    "shape_land": lambda facts, section: (
        section == "section-eco-income"
        and facts.selected_kind == NodeKind.COVENANT
        and facts.selected_covenant is not None
        and sourcebooks.in_play("TME", sourcebooks.saga_books(facts.saga))
    ),
    # Charter Strength (TME p. 36), on a charter's chosen lord.
    "draft_charter": _on_charter_lord,
    "seek_loophole": _on_charter_lord,
    # War's End: on the docket, with a case chosen (the form refuses one
    # that isn't a Wizard's War).
    "war_end": lambda facts, section: (
        section == CASES_SECTION and facts.chosen_row(section) is not None
    ),
}

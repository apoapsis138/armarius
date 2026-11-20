"""When each action is offered: `available` asks the generic gates (who
may act, Player view, the books in play, a character's interests, a record
In Creation), then the action's own rule about the record on show or the
section focus is in.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ... import (
    arms,
    catalog,
    chronicle,
    connections,
    giving,
    guest_stays,
    hosting,
    merges,
    places,
    seasons,
    sourcebooks,
    storyguides,
    threats,
    traditions,
    viewing,
    virtual_tabletop,
    world,
)
from ... import book_value as bv
from ... import familiars as fam
from ... import goods as gd
from ... import house_rules as hr
from ... import inhabitants as inh
from ... import lab_texts as lt
from ... import mystery_cults as cults_core
from ... import sessions as ss
from ... import spells as spl
from ...actions import (
    RECORD_SECTION,
    SECTION_VERBS,
    ActionFacts,
    NodeKind,
    silver_purse,
)
from ...forms import acclaim as acclaim_forms
from ...forms import careers, go_to, message, sheet_roll
from ...forms import charter as charter_forms
from ...forms import hubris as hubris_forms
from ...forms import notes_goals as goal_forms
from ...forms import secrets as secret_forms
from ...forms import tmre_spirits as tmre_spirit_forms
from ...models import (
    FULL,
    LINE,
    TEXT_LONGEVITY,
    Agent,
    Character,
    Covenant,
    Familiar,
    Laboratory,
    Saga,
    Session,
)
from ...rules import (
    activities,
    casting,
    faiths,
    hedge_casting,
    house_magic,
    mobile,
    options,
    philosophy,
)
from ...rules import faerie_dealings as faerie_dealing_rules
from ...rules import gauntlet as gauntlet_rules
from ...rules import goetic as goetic_rules
from ...rules import hermetic_projects as project_rules
from ...rules import sin as sin_rules
from ...sections import (
    AGENTS_SECTION,
    AHEAD_SECTION,
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
    NOTES_SECTION,
    ORDERS_SECTION,
    SECRETS_SECTION,
    SESSIONS_SECTION,
    STAGED_SECTION,
    WHEREABOUTS_SECTION,
)


def drafting(facts: ActionFacts) -> bool:
    """Whether the record on show is In Creation: its deeds wait until it
    is In Play."""
    record = facts.creation_record()
    return record is not None and record.in_creation


# -- the actions that depend on the record on show --


def on_saga(facts: ActionFacts) -> bool:
    return facts.selected_kind == NodeKind.SAGA


def exports_saga(facts: ActionFacts) -> bool:
    return on_saga(facts) and facts.can_send_files()


def exports_cult(facts: ActionFacts) -> bool:
    return exports_saga(facts) and bool(facts.saga.custom_cults)


def hosts(facts: ActionFacts) -> bool:
    """Host for Players: on the saga, in the storyguide's own window, while
    it isn't hosting yet."""
    return on_saga(facts) and not hosting.is_hosted_copy() and not hosting.HOST.running


def stops_hosting(facts: ActionFacts) -> bool:
    return on_saga(facts) and hosting.HOST.running


def in_full_creation(facts: ActionFacts, *, worksheet: bool) -> bool:
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


def changes_detail(facts: ActionFacts, *, up: bool) -> bool:
    """Promote (`up`) or Demote: a character or covenant whose level of
    detail has a step that way."""
    record = facts.creation_record()
    if not isinstance(record, (Character, Covenant)) or not facts.on_record():
        return False
    step = world.promoted if up else world.demoted
    return step(record.detail) is not None


def on_covenfolk(facts: ActionFacts) -> bool:
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


def commands_beast(facts: ActionFacts) -> bool:
    """Command the Beast: on a tamed animal's Personality Traits."""
    record = facts.creation_record()
    return (
        isinstance(record, Character)
        and record.animal is not None
        and facts.active_section() in (None, "section-personality-traits")
    )


def gives(facts: ActionFacts) -> bool:
    found = facts.to_give()
    return found is not None and giving.blocked(facts.saga, *found) is None


def gives_silver(facts: ActionFacts) -> bool:
    purse = silver_purse(facts)
    return (
        purse is not None and giving.blocked(facts.saga, giving.SILVER, purse) is None
    )


def experiments(facts: ActionFacts) -> bool:
    """Experiment on a Script: a Mystagogue of one of the saga's cults with
    a degree open to an experiment."""
    character = facts.selected_character
    return (
        facts.selected_kind == NodeKind.CHARACTER
        and facts.on_record()
        and character is not None
        and bool(cults_core.experiments_for(facts.saga, character))
    )


def has_interests(facts: ActionFacts) -> bool:
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


def exports_record(facts: ActionFacts) -> bool:
    return (
        facts.can_send_files()
        and facts.record_to_export() is not None
        and facts.on_record()
    )


def exports_markdown(facts: ActionFacts) -> bool:
    """A character's, covenant's, laboratory's or familiar's own page: a
    record with a printed sheet."""
    record = facts.record_to_delete()
    return (
        facts.can_send_files()
        and isinstance(record, Character | Covenant | Laboratory | Familiar)
        and facts.on_record()
    )


def updates_record(facts: ActionFacts) -> bool:
    return facts.record_to_export() is not None and facts.on_record()


def binds_familiar(facts: ActionFacts) -> bool:
    """A magus without a familiar exists, and on a character, it is one."""
    character = facts.selected_character
    if facts.selected_kind == NodeKind.CHARACTER and (
        character is None or character.type != "magus"
    ):
        return False
    return bool(fam.unbonded_magi(facts.saga))


def disputes(facts: ActionFacts) -> bool:
    """A character, with another to dispute with."""
    return (
        facts.selected_kind == NodeKind.CHARACTER
        and facts.on_record()
        and facts.selected_character is not None
        and len(facts.saga.characters) > 1
    )


def makes_ligature(facts: ActionFacts) -> bool:
    """A character with Artes Liberales, Philosophiae or Medicine."""
    character = facts.selected_character
    return (
        facts.selected_kind == NodeKind.CHARACTER
        and facts.on_record()
        and character is not None
        and bool(philosophy.ligature_abilities(character))
    )


def keeps_byzantine_custom(
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


def casts_hedge_magic(facts: ActionFacts) -> bool:
    """A character whose tradition has a way of casting."""
    character = facts.selected_character
    return (
        facts.selected_kind == NodeKind.CHARACTER
        and facts.on_record()
        and character is not None
        and hedge_casting.can_cast(character)
    )


def sings(wanted: Callable[[Character], bool], facts: ActionFacts) -> bool:
    """A character with the galdor Virtue the action needs."""
    character = facts.selected_character
    return (
        facts.selected_kind == NodeKind.CHARACTER
        and facts.on_record()
        and character is not None
        and wanted(character)
    )


def joins_traditions(facts: ActionFacts) -> bool:
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


def bears_arms(facts: ActionFacts) -> bool:
    record = facts.record_to_delete()
    return facts.on_record() and record is not None and arms.bears_arms(record)


def on_ruin(facts: ActionFacts) -> bool:
    return facts.on_record() and places.is_ruin(facts.record_to_delete())


def merges_doubles(facts: ActionFacts) -> bool:
    """On the saga or the Region, while a faction shares its name with a
    character or creature (merges.py)."""
    return facts.selected_kind in (
        NodeKind.SAGA,
        NodeKind.REGION,
        NodeKind.NEIGHBOUR_GROUP,
    ) and bool(merges.doubles(facts.saga))


def reveals(facts: ActionFacts, *, known: bool) -> bool:
    """Reveal (a record the players don't know of) or Hide from the
    Players (one they do): on a record of the world the troupe doesn't
    play (viewing.can_be_unknown)."""
    record = facts.record_to_delete()
    return (
        facts.on_record()
        and viewing.can_be_unknown(record)
        and getattr(record, "known", True) == known
    )


def assigns_storyguide(facts: ActionFacts) -> bool:
    """Its Storyguide: on a record that can have one, with a second
    storyguide, for a storyguide who runs it (storyguides.offered)."""
    return facts.on_record() and storyguides.offered(
        facts.saga, facts.record_to_delete()
    )


def on_region(facts: ActionFacts) -> bool:
    """On the saga or the Region (the desktop's The Region chapter)."""
    return facts.selected_kind in (
        NodeKind.SAGA,
        NodeKind.REGION,
        NodeKind.NEIGHBOUR_GROUP,
    )


def on_dormant_threat(facts: ActionFacts) -> bool:
    return facts.on_record() and threats.is_dormant(facts.record_to_delete())


def on_threat_under_way(facts: ActionFacts) -> bool:
    record = facts.record_to_delete()
    return (
        facts.on_record()
        and threats.is_threat(record)
        and not threats.is_dormant(record)
    )


def goes_to(facts: ActionFacts) -> bool:
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


def sins(facts: ActionFacts) -> bool:
    """Confidence through Sin: a trait or Flaw with a penchant for a sin."""
    character = _on_traits(facts)
    return character is not None and bool(sin_rules.sinful_traits(character))


def influences(facts: ActionFacts) -> bool:
    """Infernal Influence: a sinner, or one who knows Infernal Lore."""
    character = _on_traits(facts)
    return character is not None and (
        bool(sin_rules.sinful_traits(character))
        or any(a.name == "Infernal Lore" for a in character.abilities)
    )


def works_goetia(facts: ActionFacts) -> bool:
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


def turbulent(facts: ActionFacts) -> bool:
    """Turbulence: a Gifted character, from his record or This Season."""
    character = _apprentices_character(facts, "section-char-season")
    return character is not None and gauntlet_rules.gifted(character)


def faces_gauntlet(facts: ActionFacts) -> bool:
    """The Gauntlet: an apprentice (the Social Status)."""
    character = _apprentices_character(facts)
    return character is not None and gauntlet_rules.apprentice(character)


def may_lose_gift(facts: ActionFacts) -> bool:
    """Lose the Gift: a Gifted apprentice."""
    character = _apprentices_character(facts)
    return (
        character is not None
        and gauntlet_rules.apprentice(character)
        and gauntlet_rules.gifted(character)
    )


def learns_cantation(facts: ActionFacts) -> bool:
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


def makes_art(facts: ActionFacts) -> bool:
    """An Artist's Career: someone with a Craft or Profession."""
    character = _academe_person(facts)
    return character is not None and bool(careers.artist_crafts(character))


def studies(facts: ActionFacts) -> bool:
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


def bargains_with_faeries(facts: ActionFacts) -> bool:
    """Ars Fabulosa and A Faerie Bargain: one who holds a bargaining
    power."""
    character = _faerie_dealer(facts)
    return character is not None and faerie_dealing_rules.bargains(character)


def offers_to_faerie(facts: ActionFacts) -> bool:
    """An Offer to Faerie: any person."""
    return _faerie_dealer(facts) is not None


# The lacuna and the pilgrim (HoH:S, The Church).


def goes_on_pilgrimage(facts: ActionFacts, section: str) -> bool:
    """Pilgrimage: on a person's This Season (any pilgrim, grogs too: The
    Church p. 16)."""
    character = facts.selected_character
    return (
        section == "section-char-season"
        and character is not None
        and character.animal is None
    )


def casts_in_lacuna(facts: ActionFacts, section: str) -> bool:
    """Cast in a Lacuna: on a magus's Known Spells."""
    character = facts.selected_character
    return (
        section == "section-known-spells"
        and character is not None
        and character.type == "magus"
    )


def keeps_faith(
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


def rop_divine(saga: Saga) -> bool:
    return sourcebooks.in_play("RoP:D", sourcebooks.saga_books(saga))


def exorcises(facts: ActionFacts) -> bool:
    """Perform an Exorcism: on Holy Orders, for a clergyman."""
    character = facts.selected_character
    return (
        character is not None
        and facts.active_section() == ORDERS_SECTION
        and faiths.may_exorcise(character)
    )


# Mystic paths, God's aid, the Font and the Commanding Aura.


def walks_in_faith(
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


def is_proud(facts: ActionFacts) -> bool:
    """Hubris: a Verditius with the Flaw or the trait, on his Personality
    Traits."""
    character = _on_traits(facts)
    return character is not None and hubris_forms.offers(facts.saga, character)


# Hermetic spirit magic and theurgy (The Mysteries Revised Edition).


def works_with_spirits(facts: ActionFacts) -> bool:
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


def on_known_spells(
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


def reads_signs(
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


def keeps_acclaim(facts: ActionFacts) -> bool:
    """House Acclaim: a magus of Bonisagus or Flambeau, or one holding it."""
    character = _on_reputations(facts)
    return character is not None and acclaim_forms.offers(facts.saga, character)


def has_reputation(facts: ActionFacts) -> bool:
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


def staged(kind: str) -> Callable[[ActionFacts], bool]:
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


def begins_project(facts: ActionFacts) -> bool:
    """Begin Project: on a full covenant's record or Overview tab."""
    covenant = facts.selected_covenant
    return (
        facts.selected_kind == NodeKind.COVENANT
        and covenant is not None
        and covenant.detail == FULL
        and facts.active_section() in BEGIN_PROJECT_SECTIONS
    )


def has_asks(facts: ActionFacts) -> bool:
    """A character asked to teach, or asking (teaching.py)."""
    character = facts.selected_character
    return character is not None and any(
        character.id in (r.student_id, r.teacher_id) for r in facts.saga.teach_requests
    )


#: The rules of the actions that aren't More's or New's, by the record on
#: show (registry.REGISTRY has the rest).
RECORD_RULES: dict[str, Callable[[ActionFacts], bool]] = {
    "delete_record": _deletes_record,
}


# -- the actions that depend on the section focus is in --


def _has_verb(action: str) -> Callable[[ActionFacts, str], bool]:
    def rule(_facts: ActionFacts, section: str) -> bool:
        return action in SECTION_VERBS.get(section, ())

    return rule


def restores(facts: ActionFacts, section: str) -> bool:
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


def with_morale_rules(its_section: str) -> Callable[[ActionFacts, str], bool]:
    """In `its_section`, while the saga plays Morale and Discipline (LoM
    pp. 134-135)."""

    def rule(facts: ActionFacts, section: str) -> bool:
        return section == its_section and options.is_on(
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


def _session_here(facts: ActionFacts, section: str) -> Session | None:
    """The Session on show on its own page, or chosen in the Sessions
    list; None otherwise."""
    if facts.selected_kind == NodeKind.SESSION:
        return facts.selected_session
    if section != SESSIONS_SECTION:
        return None
    row = facts.chosen_row(section)
    shown = ss.in_order(facts.saga)
    return shown[row] if row is not None and 0 <= row < len(shown) else None


def _chosen_session(facts: ActionFacts, section: str) -> Session | None:
    """_session_here, while the Virtual Tabletop (Preview) is on."""
    return _session_here(facts, section) if virtual_tabletop.on() else None


def opens_session(facts: ActionFacts, section: str) -> bool:
    """Open Session, on a row of the Sessions list."""
    return facts.selected_kind != NodeKind.SESSION and (
        _session_here(facts, section) is not None
    )


def glances_cast(facts: ActionFacts, section: str) -> bool:
    """Cast at a Glance, on a Session's page or its row."""
    return _session_here(facts, section) is not None


def begins_session(facts: ActionFacts, section: str) -> bool:
    session = _chosen_session(facts, section)
    return session is not None and (
        chronicle.why_not_begin(facts.saga, session, chronicle.here()) is None
    )


def ends_session(facts: ActionFacts, section: str) -> bool:
    session = _chosen_session(facts, section)
    return session is not None and (
        chronicle.why_not_end(session, chronicle.here(), facts.saga) is None
    )


def rolls_from_sheet(facts: ActionFacts, section: str) -> bool:
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


def reads_chronicle(facts: ActionFacts, section: str) -> bool:
    session = _chosen_session(facts, section)
    return session is not None and chronicle.has_chronicle(facts.saga, session)


def sends_message(facts: ActionFacts, section: str) -> bool:
    """Message, on the Session Under way, for anyone at it."""
    session = _chosen_session(facts, section)
    return session is not None and message.why_not_here(facts.saga, session) is None


def on_secret(facts: ActionFacts, section: str, *, revealed: bool) -> bool:
    """Reveal the Secret (one not revealed) or Hide the Secret Again (one
    revealed), on the chosen row of a record's Secrets."""
    chosen = _chosen_secret(facts, section)
    return chosen is not None and chosen[0].secrets[chosen[1]].revealed == revealed


def splits_secret(facts: ActionFacts, section: str) -> bool:
    """Split by Paragraph: on a chosen secret of several paragraphs."""
    chosen = _chosen_secret(facts, section)
    return chosen is not None and secret_forms.splits(*chosen)


def plans_goal(facts: ActionFacts, section: str) -> bool:
    """Plan the Study Path: on a chosen goal of Notes & Goals naming an Art
    or Ability and a score, for whoever may plan the character's seasons."""
    character = facts.selected_character
    return (
        section == NOTES_SECTION
        and character is not None
        and goal_forms.plans(facts.saga, character, facts.chosen_row(NOTES_SECTION))
    )


def improves(_facts: ActionFacts, section: str) -> bool:
    return section == "section-eco-income"


def acts_on_device(action: str) -> Callable[[ActionFacts, str], bool]:
    def rule(facts: ActionFacts, section: str) -> bool:
        return section in DEVICE_SECTIONS and facts.device_action_enabled(action)

    return rule


def shares_spell(facts: ActionFacts, section: str) -> bool:
    character = facts.selected_character
    return (
        section == "section-known-spells"
        and character is not None
        and bool(spl.shareable_spells(character))
    )


def boosts_spell(facts: ActionFacts, section: str) -> bool:
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


def performs_ritual(facts: ActionFacts, section: str) -> bool:
    lab = facts.selected_laboratory
    return (
        section == LAB_TEXTS_SECTION
        and lab is not None
        and any(
            lt.kind(b) == TEXT_LONGEVITY
            for b in lt.texts_of(facts.saga, "laboratory", lab.id)
        )
    )


def research_bonuses_rule(facts: ActionFacts, section: str) -> bool:
    """Library research values are Covenants'."""
    covenant = facts.selected_covenant
    return (
        sourcebooks.in_play(bv.SOURCE_BOOK, sourcebooks.saga_books(facts.saga))
        and facts.selected_kind == NodeKind.COVENANT
        and section in LIBRARY_SECTIONS
        and covenant is not None
        and bool(bv.library_subjects(facts.saga, covenant))
    )


def acts_on_agent(
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


def adds_purity(facts: ActionFacts, section: str) -> bool:
    """Add a Purity, offered on the Goods list for a chosen good priced by
    purity that has a pure price."""
    if section != GOODS_SECTION:
        return False
    row = facts.chosen_row(section)
    listed = gd.listed(facts.saga)
    return row is not None and 0 <= row < len(listed) and gd.takes_purities(listed[row])


def moves_to_source(facts: ActionFacts, section: str) -> bool:
    """Move to Source, offered on House Rules once the saga has a source
    of its own and an entry to move."""
    return (
        section == HOUSE_RULES_SECTION
        and bool(facts.saga.sources)
        and bool(hr.all_entries(facts.saga))
    )


def grog_season(facts: ActionFacts, section: str) -> bool:
    character = facts.selected_character
    return (
        section == "section-char-season"
        and character is not None
        and not activities.is_planned(character)
    )


def grog_has_plan(facts: ActionFacts) -> bool:
    character = facts.selected_character
    return character is not None and seasons.plan_for(facts.saga, character) is not None


def works_for_labor(
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


def breaks_clause(facts: ActionFacts, section: str) -> bool:
    """Break a Clause: on the Clauses list, for a chosen clause not yet
    broken."""
    covenant = facts.selected_covenant
    return (
        section == CLAUSES_SECTION
        and covenant is not None
        and charter_forms.can_break(covenant, facts.chosen_row(section))
    )


def censures_clause(facts: ActionFacts, section: str) -> bool:
    """Censure: on the Clauses list, for a chosen broken clause."""
    covenant = facts.selected_covenant
    return (
        section == CLAUSES_SECTION
        and covenant is not None
        and charter_forms.can_censure(covenant, facts.chosen_row(section))
    )


def charges_clause(facts: ActionFacts, section: str) -> bool:
    """Charge at Tribunal: on a chosen broken clause of a charter that binds
    under the Peripheral Code, not charged yet."""
    covenant = facts.selected_covenant
    return (
        section == CLAUSES_SECTION
        and covenant is not None
        and charter_forms.can_charge(facts.saga, covenant, facts.chosen_row(section))
    )


def forgets_template(facts: ActionFacts, section: str) -> bool:
    """Forget a Template: on the charter, while the saga keeps one."""
    return section == CHARTER_SECTION and bool(facts.saga.charter_templates)


def ends_membership(facts: ActionFacts, section: str) -> bool:
    """End Membership: on the charter, while a magus expelled under it is
    still of the covenant."""
    covenant = facts.selected_covenant
    return (
        section == CHARTER_SECTION
        and covenant is not None
        and charter_forms.can_end_membership(facts.saga, covenant)
    )


def owes_fee(facts: ActionFacts, section: str) -> bool:
    """Pay the Fee: on the Guests list, for a guest owing this year's."""
    covenant = facts.selected_covenant
    return (
        section == GUESTS_SECTION
        and covenant is not None
        and guest_stays.can_pay(facts.saga, covenant, facts.chosen_row(section))
    )


def on_ship_row(
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


def logs_stop(facts: ActionFacts, section: str) -> bool:
    """Add a Stop: on Whereabouts, and on the top panel of a covenant with
    a Mobile Hook, as a covenant that never moves has no stops to log."""
    covenant = facts.selected_covenant
    if covenant is None:
        return False
    return section == WHEREABOUTS_SECTION or (
        section == "section-cov-info" and mobile.has_mobile_hook(covenant)
    )


def plans_journey(_facts: ActionFacts, section: str) -> bool:
    """Travel, the calculator: on Ahead, the Seasons page's or a
    covenant's."""
    return section in (AHEAD_SECTION, COV_AHEAD_SECTION)


def on_charter_lord(facts: ActionFacts, section: str) -> bool:
    """Draft the Charter and Seek a Loophole: on a town's or a covenant's
    charter lords, with a lord chosen, while the saga uses the Charter
    Strength rule (TME p. 36)."""
    return (
        section in (CHARTER_LORDS_SECTION, COV_CHARTER_LORDS_SECTION)
        and facts.chosen_row(section) is not None
        and options.is_on(facts.saga, options.CHARTER_STRENGTH)
    )


def imports(facts: ActionFacts, section: str) -> bool:
    return facts.selected_kind == NodeKind.SAGA or section in LIBRARY_SECTIONS


#: The section verbs' rules, by the section focus is in.
SECTION_RULES: dict[str, Callable[[ActionFacts, str], bool]] = {
    "add": _has_verb("add"),
    "remove": _has_verb("remove"),
    "edit": _has_verb("edit"),
    "filter_lab_texts": _filters_lab_texts,
}

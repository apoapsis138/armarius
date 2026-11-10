"""The core's table from a record and a sheet section to the section's Add,
Edit and Delete.

Both front-ends draw what this returns: a section's verbs are built here,
once, so the same key does the same thing in the terminal and on the
desktop. `actions.SECTION_VERBS` says which verbs a section has; this says
what they do.

One builder per kind of record (a plain dict, as a Strategy keyed by the
record's type) returns every section the record's sheet shows that has a
`commands.SectionOps`, keyed by the section's widget id. A section with
only a single Edit form is not in the table.
"""

from __future__ import annotations

from collections.abc import Callable, Collection
from dataclasses import replace
from typing import Any

from . import (
    conflicts,
    creation,
    guest_stays,
    hermetic_projects,
    manors,
    mobile_covenants,
    seat,
    sourcebooks,
    stores,
    town_charter,
    traditions,
)
from .commands import SectionOps
from .forms import ability as ability_forms
from .forms import agents as agent_forms
from .forms import ahead as ahead_forms
from .forms import character as character_forms
from .forms import charter as charter_forms
from .forms import church as church_forms
from .forms import constant_effect as constant_forms
from .forms import covenant as covenant_forms
from .forms import covenant_history, notes_goals
from .forms import covers as cover_forms
from .forms import creature as creature_forms
from .forms import criamon as criamon_forms
from .forms import device as device_forms
from .forms import diary as diary_forms
from .forms import familiar as familiar_forms
from .forms import goods as goods_forms
from .forms import inhabitant as inhabitant_forms
from .forms import lab_item as lab_item_forms
from .forms import laboratory as lab_forms
from .forms import neighbour as neighbour_forms
from .forms import possession as possession_forms
from .forms import power as power_forms
from .forms import religion as religion_forms
from .forms import saga_content as content_forms
from .forms import season as season_forms
from .forms import sessions as session_forms
from .forms import spell as spell_forms
from .forms import stores as store_forms
from .forms import tradition as tradition_forms
from .forms import trait as trait_forms
from .forms import tribunal as tribunal_forms
from .forms import virtue as virtue_forms
from .forms import vis as vis_forms
from .forms import world as world_forms
from .forms.secrets import secrets_ops
from .models import (
    Character,
    Covenant,
    Creature,
    Familiar,
    Laboratory,
    Neighbour,
    Saga,
    Tribunal,
)
from .models.holdings import INHABITANT_KINDS, POSSESSION_KINDS
from .seasons.covenant import SEASON_KINDS
from .sections import (
    AGENTS_SECTION,
    BOOKS_SECTION,
    CHAR_AHEAD_SECTION,
    CONSTANT_EFFECTS_SECTION,
    COV_AHEAD_SECTION,
    COVERS_SECTION,
    DEVICE_SECTIONS,
    GOODS_SECTION,
    HOUSE_RULES_SECTION,
    LAB_ITEMS_SECTION,
    LAB_TRAITS_SECTION,
    LAB_VF_SECTIONS,
    PLAYERS_SECTION,
    POWERS_SECTION,
    SESSIONS_SECTION,
    SOURCES_SECTION,
    SPELL_SECTION,
)

OpsBuilder = Callable[[Saga, Any], dict[str, SectionOps]]

ABILITIES_SECTION = "tab-abilities"
KNOWN_SPELLS_SECTION = "section-known-spells"
RESEARCH_GOALS_SECTION = "section-research-goals"
INVENTORY_SECTION = "section-inventory"
SEASON_SECTION = "section-char-season"
DIARY_SECTION = "tab-diary"
RAW_VIS_SECTIONS = ("section-raw-vis-hermetic", "section-raw-vis-inventory")
BOONS_SECTION = "section-cov-boons"
HOOKS_SECTION = "section-cov-hooks"
COVENANT_REPUTATIONS_SECTION = "section-cov-reputations"
INCOME_SECTION = "section-eco-income"
EXPENDITURE_SECTION = "section-eco-expenditure"
SAVINGS_SECTION = "section-eco-savings"
COVENANT_DIARY_SECTION = "tab-cov-diary"
COVENANT_SEASONS_SECTION = "tab-cov-seasons"
#: Each Boons or Hooks section and the kind it lists.
BOON_HOOK_KINDS = {BOONS_SECTION: "Boon", HOOKS_SECTION: "Hook"}
PERSONALITY_TRAITS_SECTION = "section-personality-traits"
REPUTATIONS_SECTION = "section-reputations"
FAMILIAR_TRAITS_SECTION = "section-fam-personality-traits"
FAMILIAR_REPUTATIONS_SECTION = "section-fam-reputations"
FAMILIAR_WEAPONS_SECTION = "section-fam-natural-weapons"
FAMILIAR_ABILITIES_SECTION = "tab-fam-abilities"
FAMILIAR_POWERS_SECTION = "tab-fam-powers"
LAB_SPECIALTIES_SECTION = "section-lab-specialties"
LAB_FEATURES_SECTION = "section-lab-features"
LAB_RAW_VIS_SECTION = "section-lab-raw-vis"
LAB_DIARY_SECTION = "tab-lab-diary"
LAB_CONNECTIONS_SECTION = "section-lab-connections"
LAB_FEATURE_SECTIONS = (LAB_FEATURES_SECTION, *LAB_VF_SECTIONS)

#: Per kind of record, each Virtues & Flaws section and the side it lists.
VIRTUE_FLAW_SIDES: dict[type, dict[str, str]] = {
    Character: {"section-vf-virtues": "Virtue", "section-vf-flaws": "Flaw"},
    Familiar: {"section-fam-vf-virtues": "Virtue", "section-fam-vf-flaws": "Flaw"},
    Laboratory: dict(zip(LAB_VF_SECTIONS, ("Virtue", "Flaw"), strict=True)),
}


def character_ops(saga: Saga, character: Character) -> dict[str, SectionOps]:
    """The character sheet's sections that have Add, Edit and Delete."""
    books = sourcebooks.saga_books(saga)

    def abilities(only: Collection[str] | None = None) -> SectionOps:
        return ability_forms.ability_ops(
            character.abilities,
            character.virtues_flaws,
            books=books,
            note=lambda name: creation.worksheet_note(character, [name]),
            only=only,
        )

    table = {
        ABILITIES_SECTION: abilities(),
        KNOWN_SPELLS_SECTION: spell_forms.known_spell_ops(saga, character),
        RESEARCH_GOALS_SECTION: character_forms.research_goal_ops(character),
        INVENTORY_SECTION: character_forms.inventory_ops(character, books),
        SEASON_SECTION: season_forms.character_season_ops(saga, character),
        CHAR_AHEAD_SECTION: season_forms.ahead_season_ops(saga, character),
        DIARY_SECTION: diary_forms.entry_ops(
            saga, character.diary, diary_forms.character_activities()
        ),
        **{
            traditions.tradition_section(t.id): abilities(t.abilities)
            for t in traditions.all_traditions()
        },
    }
    for section in RAW_VIS_SECTIONS:
        table[section] = vis_forms.raw_vis_ops(character.raw_vis)
    table[PERSONALITY_TRAITS_SECTION] = trait_forms.trait_ops(
        character.personality_traits, PERSONALITY_TRAITS_SECTION
    )
    table[REPUTATIONS_SECTION] = trait_forms.trait_ops(
        character.reputations, REPUTATIONS_SECTION
    )
    table.update(_virtue_flaw_ops(saga, character))
    table.update(_device_ops(saga, "character", character.id))
    table.update(secrets_ops(character))
    table.update(notes_goals.ops(saga, character))
    table.update(world_forms.standing_ops(saga, character))
    table[CONSTANT_EFFECTS_SECTION] = constant_forms.ops(saga, character)
    table[COVERS_SECTION] = cover_forms.ops(character)
    table[POWERS_SECTION] = power_forms.ops(character)
    table[AGENTS_SECTION] = agent_forms.ops(character)
    table.update(religion_forms.ops(saga, character))
    table.update(church_forms.ops(saga, character))
    table.update(criamon_forms.ops(saga, character))
    for tradition in traditions.all_traditions():
        table[traditions.effects_section(tradition.id)] = tradition_forms.effect_ops(
            character, tradition
        )
        table[traditions.bonds_section(tradition.id)] = tradition_forms.bond_ops(
            saga, character, tradition
        )
        if tradition.pools:
            table[traditions.pools_section(tradition.id)] = tradition_forms.pool_ops(
                character, tradition
            )
    return table


def familiar_ops(saga: Saga, familiar: Familiar) -> dict[str, SectionOps]:
    """The familiar sheet's sections that have Add, Edit and Delete."""
    return {
        FAMILIAR_TRAITS_SECTION: trait_forms.trait_ops(
            familiar.personality_traits, FAMILIAR_TRAITS_SECTION
        ),
        FAMILIAR_REPUTATIONS_SECTION: trait_forms.trait_ops(
            familiar.reputations, FAMILIAR_REPUTATIONS_SECTION
        ),
        FAMILIAR_WEAPONS_SECTION: familiar_forms.natural_weapon_ops(familiar),
        FAMILIAR_ABILITIES_SECTION: familiar_forms.ability_ops(saga, familiar),
        FAMILIAR_POWERS_SECTION: familiar_forms.bond_power_ops(familiar),
        **_virtue_flaw_ops(saga, familiar),
    }


def laboratory_ops(saga: Saga, lab: Laboratory) -> dict[str, SectionOps]:
    """The laboratory sheet's sections that have Add, Edit and Delete."""
    return {
        LAB_SPECIALTIES_SECTION: lab_forms.specialty_ops(saga, lab),
        LAB_FEATURES_SECTION: lab_forms.feature_ops(saga, lab),
        LAB_RAW_VIS_SECTION: vis_forms.raw_vis_ops(lab.raw_vis),
        LAB_DIARY_SECTION: diary_forms.entry_ops(saga, lab.diary),
        LAB_CONNECTIONS_SECTION: lab_forms.connection_ops(lab),
        LAB_TRAITS_SECTION: trait_forms.trait_ops(
            lab.personality_traits, LAB_TRAITS_SECTION
        ),
        LAB_ITEMS_SECTION: lab_item_forms.item_ops(saga, lab),
        **{
            section: lab_forms.named_ops(lab, section)
            for section in lab_forms.NAMED_LISTS
        },
        **_virtue_flaw_ops(saga, lab),
        **_device_ops(saga, "laboratory", lab.id),
    }


def tribunal_ops(saga: Saga, tribunal: Tribunal) -> dict[str, SectionOps]:
    """The Tribunal sheet's sections that have Add, Edit and Delete. Its
    Arguments tab counts into the argument chosen, so the sheet gives
    that one itself."""
    return tribunal_forms.tribunal_ops(saga, tribunal)


def neighbour_ops(saga: Saga, neighbour: Neighbour) -> dict[str, SectionOps]:
    """A Neighbour sheet's sections that have Add, Edit and Delete."""
    return neighbour_forms.neighbour_ops(saga, neighbour)


def creature_ops(saga: Saga, creature: Creature) -> dict[str, SectionOps]:
    """A Creature sheet's sections that have Add, Edit and Delete."""
    return creature_forms.creature_ops(saga, creature)


def saga_ops(saga: Saga, record: Saga) -> dict[str, SectionOps]:
    """The sheets of the saga as a whole: Saga Content, Seasons, Conflicts,
    the Bestiary, the Region and the two stores. Saga Content's Spells list
    counts into the spells it shows now, and its Mystery Cults into the
    cult and degree chosen, so the sheet gives those itself; so does a
    store, filtered (here unfiltered)."""
    return {
        **ahead_forms.seasons_ops(saga),
        **conflicts.ops(saga),
        **creature_forms.bestiary_ops(saga),
        **neighbour_forms.region_ops(saga),
        GOODS_SECTION: goods_forms.ops(saga),
        SOURCES_SECTION: content_forms.source_ops(saga),
        HOUSE_RULES_SECTION: content_forms.house_rule_ops(saga),
        PLAYERS_SECTION: content_forms.player_ops(saga),
        SESSIONS_SECTION: session_forms.session_ops(saga),
        **{
            store.section: store_forms.store_ops(
                saga, store, lambda store=store: stores.shown(saga, store)
            )
            for store in stores.STORES.values()
        },
    }


def covenant_ops(saga: Saga, covenant: Covenant) -> dict[str, SectionOps]:
    """The covenant sheet's sections that have Add, Edit and Delete. An
    inhabitant's Restore (a departed Magus or Companion) is a sheet's own."""
    return {
        **world_forms.covenant_ops(saga, covenant),
        COV_AHEAD_SECTION: ahead_forms.ahead_ops(saga, covenant),
        **town_charter.covenant_charter_ops(saga, covenant),
        **manors.covenant_ops(saga, covenant),
        **covenant_history.covenant_ops(saga, covenant),
        **charter_forms.charter_ops(saga, covenant),
        **guest_stays.section_ops(saga, covenant),
        **mobile_covenants.section_ops(saga, covenant),
        **secrets_ops(covenant),
        **hermetic_projects.covenant_ops(saga, covenant),
        BOONS_SECTION: covenant_forms.boon_hook_ops(saga, covenant, "Boon"),
        HOOKS_SECTION: covenant_forms.boon_hook_ops(saga, covenant, "Hook"),
        COVENANT_REPUTATIONS_SECTION: trait_forms.trait_ops(
            covenant.reputations, COVENANT_REPUTATIONS_SECTION
        ),
        INCOME_SECTION: covenant_forms.income_ops(covenant),
        EXPENDITURE_SECTION: covenant_forms.economics_row_ops(
            saga, covenant, "expenditure"
        ),
        SAVINGS_SECTION: covenant_forms.economics_row_ops(saga, covenant, "savings"),
        COVENANT_DIARY_SECTION: diary_forms.covenant_diary_ops(saga, covenant),
        **{
            f"section-inh-{kind}": inhabitant_forms.inhabitant_ops(saga, covenant, kind)
            for kind in INHABITANT_KINDS
        },
        **{
            f"section-cov-seasons-{kind}": season_forms.covenant_season_ops(
                saga, covenant, kind
            )
            for kind, _ in SEASON_KINDS
        },
        **{
            f"section-pos-{kind}": possession_forms.possession_ops(saga, covenant, kind)
            for kind in POSSESSION_KINDS
        },
        **_device_ops(saga, "covenant", covenant.id),
    }


def _device_ops(saga: Saga, kind: str, holder_id: str) -> dict[str, SectionOps]:
    """The Enchanted Devices section of the sheet of `kind` (DEVICE_SECTIONS)."""
    return {
        section: device_forms.device_ops(saga, kind, holder_id)
        for section, holds in DEVICE_SECTIONS.items()
        if holds == kind
    }


def _virtue_flaw_ops(
    saga: Saga, owner: Character | Familiar | Laboratory
) -> dict[str, SectionOps]:
    return {
        section: virtue_forms.virtue_flaw_ops(saga, owner, side)
        for section, side in VIRTUE_FLAW_SIDES[type(owner)].items()
    }


def table_row(record: object, section: str, row: int) -> int:
    """The core row for `row`, the index a sheet's list gives into the
    record's whole Virtues & Flaws list: the core's rows count within a
    side (Virtues, or Flaws), so a Virtues & Flaws row is found among its
    side's. Every other section's rows are the sheet's own."""
    if isinstance(record, Covenant) and section in BOON_HOOK_KINDS:
        return covenant_forms.attached(record, BOON_HOOK_KINDS[section]).index(row)
    sides = VIRTUE_FLAW_SIDES.get(type(record), {})
    if section not in sides or not isinstance(
        record, (Character, Familiar, Laboratory)
    ):
        return row
    return virtue_forms.side_indices(record, sides[section]).index(row)


def refreshed(record: object, section: str) -> tuple[str, ...]:
    """The sections to redraw after `section`'s verbs run: a device change
    shows in every Enchanted Devices list; a Virtue or Flaw in both lists
    and what they move (a Character's Characteristics, a laboratory's
    Features). Any other section redraws alone."""
    if section in DEVICE_SECTIONS:
        return tuple(DEVICE_SECTIONS)
    if section == SOURCES_SECTION:
        # A source names the books in play, and House Rules and spells cite it.
        return (BOOKS_SECTION, SOURCES_SECTION, HOUSE_RULES_SECTION, SPELL_SECTION)
    if section == HOUSE_RULES_SECTION:
        return (HOUSE_RULES_SECTION, BOOKS_SECTION, SOURCES_SECTION)
    if section in BOON_HOOK_KINDS:
        # A Hook can link a vis source or an income source.
        return (section, INCOME_SECTION, "section-pos-vis_source")
    if section.startswith("section-cov-seasons-"):
        return (COVENANT_SEASONS_SECTION,)
    if section == LAB_FEATURES_SECTION:
        return LAB_FEATURE_SECTIONS
    sides = VIRTUE_FLAW_SIDES.get(type(record), {})
    if section not in sides:
        return (section,)
    if isinstance(record, Laboratory):
        return LAB_FEATURE_SECTIONS
    if isinstance(record, Character):
        return (*sides, "section-char-characteristics")
    return tuple(sides)


BUILDERS: dict[type, OpsBuilder] = {
    Character: character_ops,
    Familiar: familiar_ops,
    Laboratory: laboratory_ops,
    Covenant: covenant_ops,
    Saga: saga_ops,
    Tribunal: tribunal_ops,
    Neighbour: neighbour_ops,
    Creature: creature_ops,
}


def ops_of(saga: Saga, record: object) -> dict[str, SectionOps]:
    """Every section of `record`'s sheet that has Add, Edit and Delete, by
    the section's id (empty for a kind of record the table does not hold).
    A sheet that looks up many sections builds this once. For a record
    whoever sits in this copy may not change (seat.may_change) every
    section keeps its rows but has no verbs: a player's page of another's
    character has no Add, Edit or Delete."""
    build = BUILDERS.get(type(record))
    if build is None:
        return {}
    table = build(saga, record)
    if seat.may_change(saga, record):
        return table
    return {
        section: ops
        if section == seat.PLANS_PART and seat.may_plan(saga, record)
        else replace(ops, add=None, edit=None, remove=None)
        for section, ops in table.items()
    }


def section_ops(saga: Saga, record: object, section: str) -> SectionOps | None:
    """`section`'s Add, Edit and Delete on `record`, or None when the table
    has nothing for that record's kind or that section."""
    return ops_of(saga, record).get(section)

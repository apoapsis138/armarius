"""Helpers shared by several test modules (fixtures live in conftest.py)."""

import re

from ars_magica_manager import catalog
from ars_magica_manager.models import (
    Ability,
    BondPower,
    Book,
    Character,
    Covenant,
    DiaryEntry,
    Familiar,
    IncomeSource,
    Inhabitant,
    KnownSpell,
    Laboratory,
    LabSpecialtyEntry,
    NamedDescription,
    Possession,
    Saga,
    ScoredTrait,
    Spell,
    VirtueFlawInstance,
)


def screen_lines(app) -> list[str]:
    """The screen as rendered, one string per terminal row -- what a text
    dump of the app shows.

    Textual has no public API for this, so it goes through the screen's
    private compositor; this is the one place that does, so a Textual
    upgrade that moves it breaks here, clearly, not deep inside a test."""
    compositor = getattr(app.screen, "_compositor", None)
    render_strips = getattr(compositor, "render_strips", None)
    assert render_strips is not None, (
        "Textual no longer has Screen._compositor.render_strips(): update "
        "support.screen_lines (and CLAUDE.md's text-dump recipe) to the new API"
    )
    return [strip.text for strip in render_strips()]


def strip_markup(markup: str) -> str:
    """`markup` with simple tags like [b], [dim], [$text-error] and [/]
    removed -- enough to check the words and column alignment of a panel's
    text."""
    return re.sub(r"\[/?(?:\$[a-z-]+|[a-z]*)\]", "", markup)


async def wait_until(pilot, condition, timeout: float = 2.0, interval: float = 0.02):
    """Poll `condition()` until it's truthy or `timeout` seconds pass, and
    return its last value.

    A bare `pilot.pause()` (wait-for-idle) has occasionally not been enough
    for a heavy sheet view to finish mounting, or a dialog's result callback
    to land, under load; a fixed extra delay only makes that less likely.
    Polling for the actual condition is fast when things are quick and still
    correct when they aren't.
    """
    elapsed = 0.0
    while not condition() and elapsed < timeout:
        await pilot.pause(interval)
        elapsed += interval
    return condition()


#: Tree node per sheet kind, in the saga built by everything_saga().
NODES: dict[str, tuple[str, ...]] = {
    "saga": ("saga",),
    "covenant": ("covenant", "cov1"),
    "character": ("character", "mag1"),
    "laboratory": ("laboratory", "lab1"),
    "familiar": ("familiar", "fam1"),
    "book_group": ("book_group",),
    "spells": ("spells",),
}


def first_vf(vf_type: str) -> str:
    return next(
        e.id
        for e in catalog.load_virtue_flaw_catalog()
        if e.type == vf_type and not e.parameters
    )


def everything_saga() -> Saga:
    """One of everything, with every list holding at least one entry, so
    edit/remove reach their pickers rather than an "empty" notice."""
    boon = next(
        e.id for e in catalog.load_covenant_boon_hook_catalog() if e.type == "Boon"
    )
    hook = next(
        e.id for e in catalog.load_covenant_boon_hook_catalog() if e.type == "Hook"
    )
    lab_vf = catalog.load_lab_virtue_flaw_catalog()[0].id
    spell_id = next(iter(catalog.load_spell_catalog_by_id()))
    trait = [ScoredTrait("Brave", 2)]
    rep = [ScoredTrait("Wise", 1)]

    covenant = Covenant(id="cov1", saga_id="s", name="Keep")
    covenant.reputations = [ScoredTrait("Fair dealing", 2)]
    covenant.boons_hooks = [VirtueFlawInstance(boon), VirtueFlawInstance(hook)]
    covenant.inhabitants = [
        Inhabitant(id=f"inh-{kind}", kind=kind, name=f"A {kind}")
        for kind in ("specialist", "craftsperson", "turb", "inhabitant")
    ] + [
        Inhabitant(id="inh-horse", kind="horse", name="Horses", quantity=2),
        Inhabitant(id="inh-livestock", kind="livestock", name="Sheep", quantity=5),
    ]
    covenant.possessions = [
        Possession(id=f"pos-{kind}", kind=kind, name=f"A {kind}")
        for kind in ("property", "weapon", "armor", "vis_source", "vis_store", "item")
    ]
    covenant.economics.income_sources = [IncomeSource(id="inc1", name="Mill")]

    magus = Character(id="mag1", name="Leandro", type="magus", covenant_id="cov1")
    magus.abilities = [Ability("Latin", level=4)]
    magus.virtues_flaws = [
        VirtueFlawInstance(first_vf("Virtue")),
        VirtueFlawInstance(first_vf("Flaw")),
    ]
    magus.personality_traits = list(trait)
    magus.reputations = list(rep)
    magus.raw_vis = {"creo": 3}
    magus.spells_known = [KnownSpell(spell_id)]
    magus.inventory = [Possession(id="item1", kind="item", name="Staff")]
    magus.assigned_lab_id = "lab1"
    companion = Character(id="comp1", name="Alys", type="companion", covenant_id="cov1")

    lab = Laboratory(id="lab1", covenant_id="cov1", name="Tower", owner_id="mag1")
    lab.specialties = [LabSpecialtyEntry("Ignem", 1, "Hearth spirit")]
    lab.features = ["Big windows"]
    lab.rooms = [NamedDescription("Study")]
    lab.inventory_items = [NamedDescription("Alembic")]
    lab.raw_vis = {"ignem": 2}
    lab.diary = [DiaryEntry(1220, "Spring", "Built")]
    lab.virtues_flaws = [VirtueFlawInstance(lab_vf)]

    familiar = Familiar(id="fam1", character_id="mag1", name="Corax")
    familiar.virtues_flaws = [VirtueFlawInstance(first_vf("Virtue"))]
    familiar.personality_traits = list(trait)
    familiar.reputations = list(rep)
    familiar.natural_weapons = [Possession(id="nw1", kind="weapon", name="Beak")]
    familiar.abilities = [Ability("Awareness", level=2)]
    familiar.bond_powers = [BondPower(id="bp1", name="Speak")]

    books = [
        Book(
            id="b-cov",
            name="Summa",
            type="Art Summa",
            owner_kind="covenant",
            owner_id="cov1",
        ),
        Book(
            id="b-lab",
            name="Notes",
            type="Other",
            owner_kind="laboratory",
            owner_id="lab1",
        ),
        Book(
            id="b-char",
            name="Diary",
            type="Other",
            owner_kind="character",
            owner_id="mag1",
        ),
        Book(id="b-none", name="Loose", type="Other"),
    ]
    return Saga(
        id="test_saga",
        name="Matrix",
        covenants=[covenant],
        characters=[magus, companion],
        laboratories=[lab],
        familiars=[familiar],
        books=books,
        spells=[
            Spell(id="own1", name="Own Spell", technique="Creo", form="Ignem", level=5)
        ],
    )

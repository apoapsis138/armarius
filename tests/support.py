"""Helpers shared by several test modules (fixtures live in conftest.py)."""

import re

from textual.content import Content
from textual.widgets import OptionList

from ars_magica_manager import catalog
from ars_magica_manager.models import (
    CHARGED,
    Ability,
    BondPower,
    Book,
    Character,
    Covenant,
    DeviceComponent,
    DiaryEntry,
    EnchantedDevice,
    Familiar,
    IncomeSource,
    Inhabitant,
    InstilledEffect,
    KnownSpell,
    LabFeature,
    Laboratory,
    LabSpecialtyEntry,
    LabSpecialtyGrant,
    NamedDescription,
    Possession,
    Saga,
    ScoredTrait,
    Spell,
    VirtueFlawInstance,
)
from ars_magica_manager.rules.xp import ability_xp


def picker_rows(picker) -> list[tuple[str | None, str]]:
    """A searchable picker's rows, in order: each one's item id (None for a
    message row) and its label as shown."""
    option_list = picker.query_one(f"#{picker.LIST_VIEW_ID}", OptionList)
    rows = []
    for index in range(option_list.option_count):
        option = option_list.get_option_at_index(index)
        rows.append((option.id, Content.from_markup(str(option.prompt)).plain))
    return rows


def picker_labels(picker) -> dict[str, str]:
    """A searchable picker's entry labels as shown, by item id."""
    return {item_id: label for item_id, label in picker_rows(picker) if item_id}


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
    """`markup` with simple tags like [b], [dim], [$text-error], [i $label]
    and [/] removed -- enough to check the words and column alignment of a
    panel's text."""
    return re.sub(r"\[/?(?:[a-z]+ )*(?:\$[a-z-]+|[a-z]*)\]", "", markup)


async def wait_until(pilot, condition, timeout: float = 5.0, interval: float = 0.02):
    """Poll `condition()` until it's truthy or `timeout` seconds pass, and
    return its last value.

    A bare `pilot.pause()` (wait-for-idle) has occasionally not been enough
    for a heavy sheet view to finish mounting, or a dialog's result callback
    to land, under load; a fixed extra delay only makes that less likely.
    Polling for the actual condition is fast when things are quick and still
    correct when they aren't. The timeout only matters when the condition
    never holds, so it is generous: under a coverage run with -n 16 a tab
    switch has taken over 2 s to move focus.
    """
    elapsed = 0.0
    while not condition() and elapsed < timeout:
        await pilot.pause(interval)
        elapsed += interval
    return condition()


async def menu(pilot, app, key: str, label: str) -> None:
    """Press a menu key (`m` More or `n` New) and pick `label` -- or, when
    it is the only thing the menu has to offer there, it runs at once."""
    from ars_magica_manager.tui.screens.prompts import MenuScreen

    await pilot.press(key)
    await pilot.pause()
    if isinstance(app.screen, MenuScreen):
        letter = next(letter for letter, _, item in app.screen.items if item == label)
        await pilot.press(letter)
        await pilot.pause()


async def close_worksheet(pilot, app) -> None:
    """A new covenant, laboratory or character opens its Creation
    Worksheet: wait for it, then close it to get back to the workspace."""
    from ars_magica_manager.tui.screens import WorkspaceScreen
    from ars_magica_manager.tui.screens.creation_worksheet import (
        CreationWorksheetScreen,
    )

    assert await wait_until(
        pilot, lambda: isinstance(app.screen, CreationWorksheetScreen)
    )
    await pilot.press("escape")
    assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))


async def build_all_tabs(pilot, view) -> None:
    """Build every tab of a sheet view that's just been opened (tabs are
    built on first visit), for a test that reaches into a tab
    without showing it first."""
    await wait_until(pilot, lambda: view.initial_tab_seen)
    await view.build_all_tabs()
    await pilot.pause()


#: Tree node per sheet kind, in the saga built by everything_saga().
NODES: dict[str, tuple[str, ...]] = {
    "saga": ("saga",),
    "covenant": ("covenant", "cov1"),
    "character": ("character", "mag1"),
    "laboratory": ("laboratory", "lab1"),
    "familiar": ("familiar", "fam1"),
    "book_group": ("book_group",),
    "saga_content": ("saga_content",),
}


def first_vf(vf_type: str) -> str:
    """The first core-book (DE) Virtue or Flaw without parameters, so the
    fixtures don't change as supplement entries join the catalog."""
    return next(
        e.id
        for e in catalog.load_virtue_flaw_catalog()
        if e.type == vf_type and not e.parameters and e.source == "DE"
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
    # A Raw Vis Store is kept somewhere (loading links an unlinked one).
    covenant.possessions[4].location_kind = "covenant"
    covenant.possessions[4].location_id = "cov1"
    covenant.economics.income_sources = [IncomeSource(id="inc1", name="Mill")]

    magus = Character(id="mag1", name="Leandro", type="magus", covenant_id="cov1")
    magus.abilities = [Ability("Latin", xp=ability_xp(4))]
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
    # The Greater Feature Virtue carries Big windows, the lab's Focus.
    lab.features = [
        LabFeature(
            "feat1",
            "Big windows",
            "labfeat_window",
            "labvf1",
            [LabSpecialtyGrant("Intellego", 2), LabSpecialtyGrant("Auram", 1)],
            focus=True,
            focus_allocations=[LabSpecialtyGrant("Imaginem", 4)],
        )
    ]
    lab.rooms = [NamedDescription("Study")]
    lab.inventory_items = [NamedDescription("Alembic")]
    lab.raw_vis = {"ignem": 2}
    lab.diary = [DiaryEntry(1220, "Spring", "Built")]
    lab.virtues_flaws = [
        VirtueFlawInstance(lab_vf, id="labvf1"),
        VirtueFlawInstance("labvf_greater_focus", id="labvf2"),
    ]

    familiar = Familiar(id="fam1", character_id="mag1", name="Corax")
    familiar.virtues_flaws = [VirtueFlawInstance(first_vf("Virtue"))]
    familiar.personality_traits = list(trait)
    familiar.reputations = list(rep)
    familiar.natural_weapons = [Possession(id="nw1", kind="weapon", name="Beak")]
    familiar.abilities = [Ability("Awareness", xp=ability_xp(2))]
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
    devices = [
        EnchantedDevice(
            id="dev-lab",
            name="Wand",
            holder_kind="laboratory",
            holder_id="lab1",
            components=[DeviceComponent("rowan wand", "wood", "small")],
            pawns_opened=4,
            effects=[
                InstilledEffect(
                    id="eff1", name="Pilum", technique="Creo", form="Ignem", level=10
                )
            ],
        ),
        EnchantedDevice(
            id="dev-char",
            name="Ring",
            talisman=True,
            holder_kind="character",
            holder_id="mag1",
            maker_id="mag1",
        ),
        EnchantedDevice(
            id="dev-cov",
            name="Potions",
            type=CHARGED,
            holder_kind="covenant",
            holder_id="cov1",
            lab_total=30,
            effects=[
                InstilledEffect(
                    id="eff2", name="Heal", technique="Creo", form="Corpus", level=20
                )
            ],
        ),
    ]
    return Saga(
        id="test_saga",
        name="Matrix",
        covenants=[covenant],
        characters=[magus, companion],
        laboratories=[lab],
        familiars=[familiar],
        books=books,
        enchanted_devices=devices,
        spells=[
            Spell(id="own1", name="Own Spell", technique="Creo", form="Ignem", level=5)
        ],
    )

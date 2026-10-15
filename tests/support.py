"""Helpers shared by several test modules (fixtures live in conftest.py)."""

import re

from textual.content import Content
from textual.widgets import OptionList

from ars_magica_manager import catalog
from ars_magica_manager.models import (
    CHARGED,
    SKETCH,
    Ability,
    Attitude,
    BondPower,
    Book,
    Case,
    Character,
    Covenant,
    DeviceComponent,
    DiaryEntry,
    EnchantedDevice,
    Familiar,
    Favour,
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
    Reason,
    Ruling,
    Saga,
    ScoredTrait,
    Spell,
    TreasuryEntry,
    Tribunal,
    TribunalDiaryEntry,
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
    "sketch_covenant": ("covenant", "cov_sketch"),
    "tribunal": ("tribunal", "rhine"),
    "theban_tribunal": ("tribunal", "thebes"),
    "normandy_tribunal": ("tribunal", "normandy"),
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

    covenant = Covenant(id="cov1", saga_id="s", name="Keep", tribunal_id="rhine")
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
    # A sketch covenant across the river: one sketch magus, two unnamed,
    # and its attitude toward the player covenant.
    sketch = Covenant(
        id="cov_sketch",
        saga_id="s",
        name="Fengheld",
        tribunal_id="rhine",
        detail=SKETCH,
        played=False,
        summary="Rivals for the ford.",
        unnamed_magi=2,
        what_matters="Vis: the ford, 3 Aquam a year",
        attitudes=[
            Attitude("cov1", -1, [Reason("Claimed the ford", -1, 1219, "Autumn")])
        ],
        favours=[Favour("Hid a grog", "Fengheld", "Keep", 1219, "Spring")],
    )
    rival = Character(
        id="mag_sketch",
        name="Severinus",
        type="magus",
        covenant_id="cov_sketch",
        detail=SKETCH,
        in_creation=False,
    )
    return Saga(
        id="test_saga",
        name="Matrix",
        covenants=[covenant, sketch],
        tribunals=[
            Tribunal(
                id="rhine",
                name="Rhine",
                summary="Gilds and forests.",
                next_year=1228,
                meeting_place="Durenmar",
                praeco_id="mag_sketch",
                package="rhine",
                package_data={
                    "rhine": {
                        "gilds": [
                            {
                                "name": "Hermetic",
                                "members": ["cov1", "cov_sketch"],
                                "dues": "2 pawns a year",
                            }
                        ]
                    }
                },
                proxies={"cov_sketch": 1},
                cases=[
                    Case(
                        "Fengheld v. Keep",
                        brought_by="Fengheld",
                        against="Keep",
                        charge="Depriving a magus of magical power.",
                        filed_year=1219,
                        filed_season="Winter",
                        notice_given=True,
                        penalty="the ford source",
                        evidence="Fengheld's register\nThe miller's account",
                        prosecutor="Severinus",
                    ),
                    Case(
                        "Gild dues",
                        kind="motion",
                        filed_year=1220,
                        filed_season="Spring",
                        penalty="dues of 3 pawns",
                    ),
                    Case(
                        "Oakheart's founding",
                        kind="appeal",
                        filed_year=1212,
                        status="decided",
                        outcome="granted 1214",
                    ),
                ],
                rulings=[
                    Ruling("Gild membership", 1214, "Any covenant may join a gild.")
                ],
                treasury=[
                    TreasuryEntry("silver", 40),
                    TreasuryEntry("vis", 6, art="Vim"),
                    TreasuryEntry("loan", 10, who="Fengheld", due_year=1229),
                    TreasuryEntry("fine", 3, art="Corpus", who="Keep"),
                ],
                diary=[
                    TribunalDiaryEntry(
                        1221, "Summer", "The Tribunal of 1221", "Gild dues set."
                    )
                ],
            ),
            Tribunal(
                id="thebes",
                name="Theban",
                next_year=1225,
                meeting_place="Thebes",
                package="theban",
                package_data={
                    "theban": {
                        "magi": [
                            {"character_id": "mag1", "tokens": 2, "shards": 1},
                            {
                                "character_id": "mag_sketch",
                                "tokens": 0,
                                "shards": 3,
                                "liturgies": 1,
                                "ostracised_until": 1225,
                                "why": "Struck a Theban magus",
                            },
                        ],
                        "archai": [
                            {
                                "office": "Archon of Rites",
                                "holder_id": "mag1",
                                "term_ends": 1225,
                                "duties": "The Tribunal's ceremonies and oaths",
                            },
                            {"office": "Strategos", "holder_id": None},
                        ],
                    }
                },
            ),
            Tribunal(
                id="normandy",
                name="Normandy",
                next_year=1227,
                meeting_place="Confluensis",
                package="normandy",
                package_data={
                    "normandy": {
                        "tenures": [
                            {
                                "source": "The Weeping Oak (3 Herbam)",
                                "holder_id": None,
                                "tenure": "tropaeum",
                                "until": 1220,
                                "notes": "Won at the Tourney",
                            },
                            {
                                "source": "Saint Michael's Spring (2 Aquam)",
                                "holder_id": None,
                                "tenure": "luctatio",
                            },
                        ],
                        "tourney": [
                            {"year": 1220, "team": "Fudarus", "points": 30},
                            {"year": 1220, "team": "Mont Saint Michel", "points": 45},
                            {"year": 1220, "team": "Visitors of Iberia", "points": 30},
                        ],
                    }
                },
            ),
        ],
        characters=[magus, companion, rival],
        laboratories=[lab],
        familiars=[familiar],
        books=books,
        enchanted_devices=devices,
        spells=[
            Spell(id="own1", name="Own Spell", technique="Creo", form="Ignem", level=5)
        ],
    )


async def choose(pilot, app, text: str):
    """Wait for a core Choose's list (ChooseScreen) and choose the first
    entry whose label has `text` (by its label, Show everything's ones too:
    keys can outrun the list filling up under load). Returns the list."""
    from ars_magica_manager.tui.screens.steps import ChooseScreen

    assert await wait_until(pilot, lambda: isinstance(app.screen, ChooseScreen))
    await pilot.pause()
    picker = app.screen
    picker.dismiss(
        next(i for i, c in enumerate(picker._all()) if text in strip_markup(c.label))
    )
    return picker

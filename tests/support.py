from ars_magica_manager.models import as_secrets

"""Helpers shared by several test modules (fixtures live in conftest.py)."""

import re

from textual.content import Content
from textual.widget import Widget
from textual.widgets import OptionList

from ars_magica_manager import catalog, traditions
from ars_magica_manager.models import (
    CHARGED,
    SKETCH,
    Ability,
    Attitude,
    Battle,
    BattleEvent,
    BattleSide,
    BodyVis,
    BondPower,
    Book,
    Breakthrough,
    CalendarEntry,
    Case,
    Character,
    Characteristics,
    Combatant,
    Covenant,
    Creature,
    CreatureAttack,
    CreaturePower,
    DeviceComponent,
    DiaryEntry,
    EnchantedDevice,
    Familiar,
    Favour,
    Fight,
    FightSide,
    IncomeSource,
    Inhabitant,
    InstilledEffect,
    KnownSpell,
    LabFeature,
    Laboratory,
    LabSpecialtyEntry,
    LabSpecialtyGrant,
    Link,
    NamedDescription,
    Neighbour,
    Possession,
    Reason,
    ResearchAttempt,
    Ruling,
    Saga,
    ScoredTrait,
    Siege,
    Spell,
    TreasuryEntry,
    Tribunal,
    TribunalDiaryEntry,
    VirtueFlawInstance,
)
from ars_magica_manager.rules.xp import ability_xp


def offer_only(saga: Saga, *offered: str) -> Saga:
    """Make `saga` offer just the traditions `offered`, every other one
    turned off (a saga offers every tradition of its books by default)."""
    for tradition in traditions.all_traditions():
        if tradition.id not in offered:
            traditions.set_on(saga, tradition.id, False)
    return saga


def literate() -> list[Ability]:
    """Latin 5 and Artes Liberales 1: what reading a Latin book needs (DE
    p. 378)."""
    return [
        Ability("Latin", xp=ability_xp(5)),
        Ability("Artes Liberales", xp=ability_xp(1)),
    ]


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
        "support.screen_lines (and CONTRIBUTING.md's text-dump recipe) to the new API"
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


async def shown[W: Widget](pilot, selector: str, kind: type[W] = Widget) -> W:
    """The current screen's `selector`, once layout has given it a place.

    A new dialog's widgets can be queried a moment before they are mounted
    and laid out. A click then (region 0 x 0) lands on nothing, and setting
    a Select's value then fails on its own parts, not mounted yet."""
    widget = pilot.app.screen.query_one(selector, kind)
    assert await wait_until(pilot, lambda: widget.region.area > 0), (
        f"{selector} was never laid out"
    )
    return widget


async def click_when_shown(pilot, selector: str) -> None:
    """Click `selector` once it is laid out (see `shown`)."""
    await shown(pilot, selector)
    assert await pilot.click(selector), f"clicking {selector} hit nothing"


async def menu(pilot, app, key: str, label: str) -> None:
    """Press a menu key (`m` More or `n` New) and pick `label` -- or, when
    it is the only thing the menu has to offer there, it runs at once."""
    from ars_magica_manager.tui.screens.prompts import MenuScreen

    before = app.screen
    await pilot.press(key)
    await pilot.pause()
    # The menu, or what a lone item opened at once; some items open nothing.
    await wait_until(pilot, lambda: app.screen is not before, timeout=2.0)
    if isinstance(app.screen, MenuScreen):
        menu_screen = app.screen
        letter = next(letter for letter, _, item in menu_screen.items if item == label)
        await pilot.press(letter)
        await pilot.pause()
        await wait_until(pilot, lambda: app.screen is not menu_screen)


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
    "transylvania_tribunal": ("tribunal", "transylvania"),
    "hibernia_tribunal": ("tribunal", "hibernia"),
    "alps_tribunal": ("tribunal", "alps"),
    "region": ("region",),
    "neighbour": ("neighbour", "gottfried"),
    "town": ("neighbour", "soest"),
    "church": ("neighbour", "cologne"),
    "university": ("neighbour", "studium"),
    "faction": ("neighbour", "coven"),
    "threat": ("neighbour", "crown"),
    "place": ("neighbour", "drachenfels"),
    "saga_content": ("saga_content",),
    "armarium": ("armarium",),
    "custodia": ("custodia",),
    "seasons": ("seasons",),
    "bestiary": ("bestiary",),
    "creature": ("creature", "aeolus"),
    "conflicts": ("conflicts",),
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
    magus.abilities = [
        Ability("Latin", xp=ability_xp(4)),
        Ability("Fehu", "Hedge Art", xp=6, xp_table="art"),
    ]
    # An Ex Miscellanea magus who is also a vitki: a tradition's chapter.
    magus.traditions = ["trad_vitkir"]
    magus.virtues_flaws = [
        VirtueFlawInstance(first_vf("Virtue")),
        VirtueFlawInstance(first_vf("Flaw")),
    ]
    magus.personality_traits = list(trait)
    magus.reputations = list(rep)
    magus.raw_vis = {"creo": 3}
    # Research under way: a goal begun, with a season in its log.
    magus.breakthroughs = [
        Breakthrough(
            "Range: Horizon",
            points=3,
            log=[ResearchAttempt(1219, "Winter", "seek", "bolt", 2, 20, 1, 5, 2)],
        )
    ]
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
        calendar=[
            CalendarEntry(
                "Elsbeth leaves for Paris", 1220, "Spring", covenant_id="cov1"
            ),
            CalendarEntry("Midsummer rites", 1219, "Summer", repeats="Each year"),
        ],
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
                                "services": 1,
                                "ostracised_until": 1225,
                                "why": "Struck a Theban magus",
                            },
                        ],
                        "archai": [
                            {
                                "office": "Archon",
                                "holder_id": "mag1",
                                "term_ends": 1225,
                                "duties": "Chairs the Council of Magistrates",
                            },
                            {"office": "Polemarch", "holder_id": None},
                        ],
                        "phylai": {"cov1": "Aegean"},
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
            Tribunal(
                id="transylvania",
                name="Transylvania",
                next_year=1228,
                meeting_place="the Shipka Pass",
                package="transylvania",
                package_data={
                    "transylvania": {
                        "members": [
                            {
                                "character_id": "mag1",
                                "privilege": "coloniae",
                                "office": "Curantis",
                            },
                        ]
                    }
                },
            ),
            Tribunal(
                id="alps",
                name="Greater Alps",
                next_year=1221,
                meeting_place="the Icy North",
                package="alps",
                package_data={
                    "alps": {
                        "ostracised": [
                            {
                                "character_id": "mag1",
                                "year": 1214,
                                "sherds": 30,
                                "voters": 90,
                                "why": "Farmed vis from the aura",
                            },
                        ],
                    }
                },
            ),
            Tribunal(
                id="hibernia",
                name="Hibernia",
                next_year=1227,
                meeting_place="the Hill of Tara",
                package="hibernia",
                package_data={
                    "hibernia": {
                        "ambassadors": [
                            {
                                "id": "amb1",
                                "faction": "The Tuatha Dé",
                                "name": "Fothaid",
                                "confirmed": True,
                            },
                        ],
                        "treaties": [
                            {
                                "title": "The Treaty of the Ford",
                                "parties": "Keep; the river's spirit",
                                "year": 1210,
                                "witness": "Quaesitor Brigid",
                                "ends": "When the ford dries",
                                "terms": "Safe crossing for a pawn a year.",
                            },
                        ],
                    }
                },
            ),
        ],
        neighbours=[
            Neighbour(
                id="gottfried",
                name="Gottfried of Arnsberg",
                kind="lord",
                summary="Count of Arnsberg. Wants the mill rent.",
                secrets=as_secrets("He owes the Archbishop more than he can pay."),
                ruler="Count Gottfried",
                answers_to="cologne",
                attitudes=[
                    Attitude(
                        "cov1",
                        0,
                        [Reason("The mill undercuts his own", -1, 1218, "Autumn")],
                    )
                ],
                favours=[
                    Favour("Safe passage for the wool carts", "Keep", "Gottfried")
                ],
                details={
                    "title": "count",
                    "wealth": "Average",
                    "manors": 50,
                    "seat": "Arnsberg",
                    "castles": [
                        {
                            "name": "Arnsberg",
                            "garrison": "6 knights",
                            "defences": "stone keep",
                            "supplies": "",
                        }
                    ],
                    "gratitude": [
                        {"who": "comp1", "points": 6, "why": "Drove off the wolves"}
                    ],
                },
            ),
            Neighbour(
                id="cologne",
                name="Archbishop of Cologne",
                kind="church",
                detail="Line",
                realm="Divine",
                details={
                    "church": "Archbishop's cathedral",
                    "order": "The secular clergy",
                    "founded": 1180,
                    "relics": [
                        {"name": "The Shrine of the Three Kings", "saint": "The Magi"}
                        | {"faith": 7}
                    ],
                },
            ),
            Neighbour(
                id="coven",
                name="The Black Pool Coven",
                kind="faction",
                attitudes=[Attitude("cov1", 2)],
                details={
                    "faction": "Hedge coven",
                    "decides": "Its leader",
                    "members": 7,
                    "wants": "The Black Pool kept secret",
                    "roster": [],
                },
            ),
            Neighbour(
                id="weavers_peace",
                name="The Weavers' Peace",
                kind="custom",
                summary="No blade is drawn in Soest on a market day.",
                details={"rules": "A fight on a market day costs the town's favour."},
            ),
            Neighbour(
                id="crown",
                name="The Hollow Crown",
                kind="threat",
                links=[Link("creatures", "aeolus", "Carries its messengers")],
                details={
                    "antagonist": "A faerie king without a court",
                    "stages": [
                        {"title": "Cattle go missing", "year": 1219}
                        | {"season": "Spring", "outcome": "Pending"},
                        {"title": "The ford floods", "year": 1220}
                        | {"season": "Winter", "ignored": "The mill is lost"},
                        {"title": "The crowning", "year": 1222, "season": None},
                    ],
                },
            ),
            Neighbour(
                id="studium",
                name="The Studium of Cologne",
                kind="university",
                details={
                    "school": "University",
                    "faculties": [
                        {"faculty": "Arts", "rector": "Master Albert", "chairs": 8},
                        {"faculty": "Theology", "rector": "", "chairs": None},
                    ],
                    "masters": [
                        {"name": "Master Gerard", "licence": "Doctor"}
                        | {"faculty": "Theology", "who": None}
                    ],
                },
            ),
            Neighbour(
                id="soest",
                name="Soest",
                kind="town",
                details={
                    "charter": "Commune",
                    "council": 12,
                    "population": 5000,
                    "guilds": [{"trade": "Weavers", "dean": "Heinrich", "masters": 9}],
                    "fairs": [
                        {
                            "name": "St. Patroclus' fair",
                            "kind": "Fair",
                            "season": "Autumn",
                            "band": "Lesser",
                            "income": None,
                            "covenant_id": "cov1",
                        }
                    ],
                },
            ),
            Neighbour(
                id="siebengebirge",
                name="The Siebengebirge",
                kind="place",
                realm="Magic",
                details={"aura": 2},
            ),
            Neighbour(
                id="drachenfels",
                name="The Drachenfels",
                kind="place",
                realm="Magic",
                place_id="siebengebirge",
                summary="A crag above the Rhine where a dragon died.",
                details={
                    "aura": 5,
                    "tethers": "The dragon's bones",
                    "status": "Visited",
                    "known": "Locally",
                    "claimed_by": "cov1",
                    "levels": [
                        {"name": "The Mist Wood", "realm": "Faerie", "aura": 6}
                        | {"see": "Per + Awareness against 9"}
                        | {"enter": "walk the path backwards at dusk"},
                        {"name": "The Vine Terraces", "realm": "Magic", "aura": 7}
                        | {"see": "Per + Awareness against 9"}
                        | {"enter": "Per + Awareness against 12"},
                    ],
                    "effects": [
                        {"what": "lab_total", "amount": 2, "target": "Herbam"}
                        | {"where": "2", "note": "a lab built in the regio"},
                        {"what": "warping_per_season", "amount": 1, "where": "2"},
                    ],
                    "triggers": [
                        {"name": "Level 2 opens", "when": "Each year"}
                        | {"season": "Summer", "what": "The terraces can be reached"},
                        {"name": "The white stag", "when": "Every N years"}
                        | {"season": "Winter", "year": 1218, "every": 7}
                        | {"what": "It walks the Mist Wood: roll"},
                    ],
                    "tables": [
                        {
                            "name": "Who walks the Mist Wood",
                            "die": "Simple die",
                            "rows": "1-5: No one\n6-9: A white stag\n10: The king",
                        }
                    ],
                    "diary": [
                        {"year": 1218, "season": "Autumn"}
                        | {"text": "Leandro found the path backwards."}
                    ],
                    # A tomb under the crag (Lands of the Nile pp. 40-46).
                    "tomb": True,
                    "tomb_kind": "lesser_royal",
                    "tomb_centuries": 3,
                    "tomb_curses": [
                        {"name": "The Fear of the King", "kind": "Hermetic effect"}
                        | {"art": "CrMe", "level": 25, "uses": 1}
                        | {"condition": "Whoever enters by night"}
                    ],
                    "tomb_wards": [
                        {"name": "Turn the Interloper", "kind": "Ward"}
                        | {"art": "ReCo", "level": 30, "penetration": 0}
                    ],
                    "tomb_traps": [
                        {"name": "The Dead Drop", "harm": "fatal", "ease": 12}
                    ],
                },
            ),
        ],
        creatures=[aeolus()],
        battles=[
            Battle(
                "The ford at Werl",
                sides=[
                    BattleSide(
                        neighbour_id="gottfried", groups=40, deployment=12, baggage=4
                    ),
                    BattleSide("the Count of Mark", groups=20, deployment=10),
                ],
                events=[BattleEvent("mag1", total=9, won=True, losses=2)],
                id="werl",
            )
        ],
        fights=[fray()],
        sieges=[falkenstein()],
        characters=[magus, companion, rival],
        laboratories=[lab],
        familiars=[familiar],
        books=books,
        enchanted_devices=devices,
        spells=[
            Spell(id="own1", name="Own Spell", technique="Creo", form="Ignem", level=5)
        ],
    )


def fray() -> Fight:
    """A fight not yet begun: the magus against two typed bandits."""
    return Fight(
        "The Fray at the Ford",
        place="below the mill",
        year=1220,
        sides=[
            FightSide(
                "The Covenant",
                combatants=[Combatant("Leandro", "character", "mag1", id="c-mag1")],
            ),
            FightSide(
                "Brigands",
                combatants=[
                    Combatant(
                        f"Bandit {n}",
                        init=1,
                        attack=7,
                        defence=5,
                        damage=5,
                        soak=3,
                        ability=3,
                        id=f"c-bandit{n}",
                    )
                    for n in (1, 2)
                ],
            ),
        ],
        id="fray",
    )


def falkenstein() -> Siege:
    """A siege just begun, in stockade, with miners and trebuchets."""
    return Siege(
        "The Siege of Falkenstein",
        castle="Burg Falkenstein",
        holder="Sir Konrad",
        besieger="the Baron of Urach",
        besieger_id="gottfried",
        miners=1,
        engines={"Trebuchet": 2},
        soldiers=4,
        besieger_walls=[1, 1, 1, 0],
        garrison_walls=[2, 2, 2, 2],
        sapper=6,
        gunner=5,
        counter_sapper=5,
        engineer=4,
        id="falkenstein",
    )


def aeolus() -> Creature:
    """Realms of Power: Magic's example magical horse, found at the
    Drachenfels, with every list of a creature's holding an entry."""
    return Creature(
        id="aeolus",
        name="Aeolus",
        realm="Magic",
        might=8,
        might_form="Animal",
        characteristics=Characteristics(presence=2, strength=4, quickness=2),
        size=2,
        season="Summer",
        virtues_flaws=[VirtueFlawInstance("vf_magic_animal")],
        personality_traits=[ScoredTrait("Vain", 3)],
        reputations=[ScoredTrait("Runs with the wind", 1)],
        attacks=[CreatureAttack("Kick", init=4, attack=4, defense=8, damage=5)],
        soak=3,
        fatigue_levels="OK, 0, -1, -3, -5, Unconscious",
        abilities=[Ability("Athletics", xp=ability_xp(5), specialty="running")],
        powers=[
            CreaturePower(
                "From Nag to Charger",
                might_cost=0,
                form="Animal",
                range="Per",
                duration="Sun",
                target="Ind",
                level=15,
            )
        ],
        vis=[BodyVis(2, "Animal", "in head")],
        appearance="A chestnut horse of good breeding.",
        source="Realms of Power: Magic p. 34",
        place_id="drachenfels",
        links=[Link("characters", "mag1", "Has ridden him once")],
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


def quiet(saga):
    """`saga` with the default for an unplanned season set to Nothing, for
    a test of what a season with nothing planned does."""
    saga.unplanned_magi = saga.unplanned_companions = "nothing"
    saga.unplanned_grogs = "nothing"
    return saga

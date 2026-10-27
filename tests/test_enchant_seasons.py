"""Enchanting as lab work: opening, instilling, lesser and
charged enchantments, attuning a talisman and investigating an item, each on
a device recorded on an Inventory tab."""

import random

from support import strip_markup

from ars_magica_manager import seasons
from ars_magica_manager.models import (
    CHARGED,
    INVESTED,
    LESSER,
    Ability,
    ArtScore,
    Book,
    Character,
    Characteristics,
    Covenant,
    EnchantedDevice,
    ExperimentalEffect,
    InstilledEffect,
    KnownSpell,
    Laboratory,
    Saga,
    SeasonPlan,
    Spell,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import activities as rules
from ars_magica_manager.rules import enchant_seasons as es
from ars_magica_manager.rules import enchantment, lab_seasons
from ars_magica_manager.rules.xp import ability_xp, art_xp


def _saga() -> Saga:
    covenant = Covenant(id="cov", saga_id="s", name="Keep")
    magus = Character(id="m", name="Tiberius", type="magus", covenant_id="cov")
    magus.characteristics = Characteristics(intelligence=2)
    magus.abilities = [Ability("Magic Theory", xp=ability_xp(5))]  # vis limit 10
    # CrIg: 10 + 8 + 2 + 5 = 25; InVi: 6 + 5 + 2 + 5 = 18.
    magus.arts = {
        art: ArtScore(xp=art_xp(score))
        for art, score in {"creo": 10, "ignem": 8, "vim": 5, "intellego": 6}.items()
    }
    magus.raw_vis = {"vim": 12, "creo": 5}
    lab = Laboratory(id="lab", covenant_id="cov", name="Tower", owner_id="m")
    staff = EnchantedDevice(
        "staff",
        "Staff",
        INVESTED,
        holder_kind="character",
        holder_id="m",
        capacity_override=6,
        effects=[
            InstilledEffect(
                "fire", "Fire", "Creo", "Ignem", level=15, instilling_progress=0
            )
        ],
    )
    ring = EnchantedDevice(
        "ring",
        "Ring",
        LESSER,
        holder_kind="laboratory",
        holder_id="lab",
        capacity_override=4,
        effects=[InstilledEffect("warm", "Warmth", "Creo", "Ignem", level=5)],
    )
    wand = EnchantedDevice(
        "wand",
        "Wand",
        CHARGED,
        holder_kind="character",
        holder_id="m",
        effects=[InstilledEffect("bolt", "Bolt", "Creo", "Ignem", level=15)],
    )
    box = EnchantedDevice(
        "box",
        "Box",
        INVESTED,
        holder_kind="covenant",
        holder_id="cov",
        pawns_opened=5,
        effects=[
            InstilledEffect("a", "Lid", "Rego", "Terram", level=5, known=False),
            InstilledEffect("b", "Lock", "Rego", "Terram", level=25, known=False),
        ],
    )
    return Saga(
        id="s",
        name="S",
        covenants=[covenant],
        characters=[magus],
        laboratories=[lab],
        enchanted_devices=[staff, ring, wand, box],
    )


def _plan(activity, **kw):
    return SeasonPlan("m", 1220, "Spring", activity, lab_id="lab", **kw)


def _work(saga, plan):
    return lab_seasons.work(saga, saga.character("m"), plan)


def _device(saga, device_id):
    return next(d for d in saga.enchanted_devices if d.id == device_id)


def _run(saga):
    worked = seasons.resolve(saga, random.Random(1))
    seasons.apply(saga, worked)
    return worked


def test_enchanting_is_planned_on_the_laboratory():
    magus = _saga().character("m")
    lab = [a.key for a in rules.activities_for(magus, lab=True)]
    assert all(key in lab for key in es.ACTIVITIES)


def test_opening_an_item_spends_its_capacity_in_vim():
    saga = _saga()
    found, work = _work(saga, _plan(es.OPEN, device_id="staff"))
    assert found == [] and work.vis_cost == {"Vim": 6}
    seasons.plan_lab_work(saga, _plan(es.OPEN, device_id="staff"))
    _run(saga)
    staff = _device(saga, "staff")
    assert (staff.pawns_opened, staff.maker_id) == (6, "m")
    assert saga.character("m").raw_vis == {"vim": 6, "creo": 5}
    found, _ = _work(saga, _plan(es.OPEN, device_id="staff"))
    assert found == ["Staff is already opened."]


def test_opening_is_within_the_vis_limit():
    saga = _saga()
    _device(saga, "staff").capacity_override = 12
    found, _ = _work(saga, _plan(es.OPEN, device_id="staff"))
    assert found == [
        "Opening Staff takes 12 pawns of Vim vis; Tiberius can handle 10 in a "
        "season (twice Magic Theory)."
    ]


def test_instilling_takes_seasons_and_its_vis_in_the_first():
    saga = _saga()
    plan = _plan(es.INSTIL, device_id="staff", effect_id="fire", vis_art="Creo")
    found, _ = _work(saga, plan)
    assert found == ["Staff has to be opened first."]
    _device(saga, "staff").pawns_opened = 6
    found, work = _work(saga, plan)
    assert found == [] and int(work.lab_total.total) == 25
    # 25 - 15 = 10 points a season: 2 seasons; 2 pawns of vis, spent now.
    assert (work.points_gained, work.finished, work.vis_cost) == (
        10,
        False,
        {"Creo": 2},
    )
    added = seasons.plan_lab_work(saga, plan)
    assert [(p.season, p.effect_id) for p in added] == [("Summer", "fire")]
    rows = [
        strip_markup(r) for _, r in seasons.lab_queue_rows(saga, saga.laboratories[0])
    ]
    assert rows[0].startswith("Spring 1220 - Summer 1220  Instil an effect: Fire")
    assert rows[0].endswith("instilled")
    _run(saga)
    effect = _device(saga, "staff").effects[0]
    assert effect.instilling_progress == 10
    assert saga.character("m").raw_vis == {"vim": 12, "creo": 3}
    assert saga.books == []  # no Lab Text until it is instilled
    saga.current_season = "Summer"
    _run(saga)
    assert effect.instilling_progress is None  # finished
    assert saga.character("m").raw_vis == {"vim": 12, "creo": 3}  # no more vis
    # Instilled: its raw Lab Text is in the laboratory, a
    # snapshot of the effect and of the device it went into.
    [text] = saga.books
    assert (text.type, text.text_kind, text.raw) == ("Lab Text", "Enchantment", True)
    staff = _device(saga, "staff")
    assert (text.technique, text.form, text.level) == (
        effect.technique,
        effect.form,
        enchantment.modified_level(staff, effect),
    )
    assert (text.author_id, text.owner_kind) == ("m", "laboratory")
    assert text.device_type == "Invested Device"
    assert text.effect_rdt.count(" / ") == 2


def test_a_lesser_enchantment_needs_twice_the_level():
    saga = _saga()
    plan = _plan(es.LESSER_WORK, device_id="ring", effect_id="warm", vis_art="Creo")
    found, work = _work(saga, plan)
    assert found == [] and work.vis_cost == {"Creo": 1}
    _device(saga, "ring").effects[0].level = 15
    found, _ = _work(saga, plan)
    assert found[0].startswith("Lab Total 25: a lesser enchantment of level 15")


def test_a_charged_item_gets_charges_for_the_excess():
    saga = _saga()
    plan = _plan(es.CHARGED_WORK, device_id="wand", effect_id="bolt")
    found, work = _work(saga, plan)
    assert found == [] and work.charges == 2  # (25 - 15) / 5
    seasons.plan_lab_work(saga, plan)
    _run(saga)
    wand = _device(saga, "wand")
    assert wand.lab_total == 25 and wand.maker_id == "m"
    [text] = saga.books
    assert (text.text_kind, text.device_type) == ("Enchantment", "Charged Item")


# -- working from a Lab Text --


def _text(saga, device_id, effect_id, **fields) -> Book:
    """A general-use Lab Text of that effect, in the covenant's library."""
    device = _device(saga, device_id)
    effect = next(e for e in device.effects if e.id == effect_id)
    values = {
        "id": f"text-{effect_id}",
        "name": f"Lab Text: {effect.name}",
        "type": "Lab Text",
        "text_kind": "Enchantment",
        "technique": effect.technique,
        "form": effect.form,
        "level": enchantment.modified_level(device, effect),
        "device_type": es.text_device_type(device),
        "owner_kind": "covenant",
        "owner_id": saga.covenants[0].id,
    }
    values.update(fields)
    book = Book(**values)
    saga.books.append(book)
    return book


def test_a_lab_text_instils_an_effect_in_one_season():
    saga = _saga()
    _device(saga, "staff").pawns_opened = 6
    text = _text(saga, "staff", "fire")
    plan = _plan(
        es.INSTIL, device_id="staff", effect_id="fire", vis_art="Creo", book_id=text.id
    )
    found, work = _work(saga, plan)
    # Lab Total 25 is at least the level: done this season, vis as usual.
    assert found == [] and work.finished and work.vis_cost == {"Creo": 2}
    assert work.points_gained == work.level
    assert seasons.plan_lab_work(saga, plan) == []  # no later seasons to plan
    _run(saga)
    assert _device(saga, "staff").effects[0].instilling_progress is None
    # No experimenting from a text; and it can't be used below its level.
    found, _ = _work(saga, _plan(**{**_plan_fields(plan), "experimenting": True}))
    assert found == ["There's no experimenting while working from a Lab Text."]


def test_an_effect_instilled_from_a_text_keeps_its_experimental_effects():
    saga = _saga()
    _device(saga, "staff").pawns_opened = 6
    flaw = ExperimentalEffect("side", "minor flaw", "sparks fly", range="Touch")
    text = _text(saga, "staff", "fire", experimental_effects=[flaw])
    plan = _plan(
        es.INSTIL, device_id="staff", effect_id="fire", vis_art="Creo", book_id=text.id
    )
    seasons.plan_lab_work(saga, plan)
    _run(saga)
    effect = _device(saga, "staff").effects[0]
    assert [e.description for e in effect.experimental_effects] == ["sparks fly"]
    assert effect.range == "Touch"
    # The raw text written as it is instilled keeps them too.
    assert saga.books[-1].experimental_effects == effect.experimental_effects
    assert saga.books[-1].experimental_effects[0] is not flaw


def _plan_fields(plan) -> dict:
    return {
        "activity": plan.activity,
        "device_id": plan.device_id,
        "effect_id": plan.effect_id,
        "vis_art": plan.vis_art,
        "book_id": plan.book_id,
    }


def test_text_virtues_apply_to_enchanting_from_a_text():
    saga = _saga()
    magus = saga.character("m")
    plan = _plan(es.CHARGED_WORK, device_id="wand", effect_id="bolt")

    def total(**fields) -> int:
        _, work = _work(saga, _plan(**{**_plan_fields(plan), **fields}))
        return int(work.lab_total.total)

    text = _text(saga, "wand", "bolt", author="Flavia")
    assert total() == 25 and total(book_id=text.id) == 25
    # Inventive Genius: +3 "when not using a Lab Text".
    magus.virtues_flaws = [VirtueFlawInstance("vf_inventive_genius")]
    assert total() == 28 and total(book_id=text.id) == 25
    # Adept Laboratory Student: +6 working from someone else's Lab Text...
    magus.virtues_flaws = [VirtueFlawInstance("vf_adept_laboratory_student")]
    assert total() == 25 and total(book_id=text.id) == 31
    # ...not from his own.
    text.author_id = "m"
    assert total(book_id=text.id) == 25
    text.author_id = None
    magus.virtues_flaws = [VirtueFlawInstance("vf_weak_scholar")]
    assert total(book_id=text.id) == 19


def test_a_lab_text_says_what_shape_and_material_it_is_exact_to():
    saga = _saga()
    text = _text(saga, "wand", "bolt", shape_material="small oak wand")
    plan = _plan(es.CHARGED_WORK, device_id="wand", effect_id="bolt", book_id=text.id)
    _, work = _work(saga, plan)
    assert work.lab_total.notes == [
        "Lab Text: Bolt reproduces the effect in the same shape and material "
        "only: small oak wand."
    ]


def test_a_lab_text_makes_a_lesser_enchantment_at_its_level():
    saga = _saga()
    _device(saga, "ring").effects[0].level = 15
    plan = _plan(es.LESSER_WORK, device_id="ring", effect_id="warm", vis_art="Creo")
    found, _ = _work(saga, plan)
    assert found[0].startswith("Lab Total 25: a lesser enchantment of level 15")
    text = _text(saga, "ring", "warm")
    found, work = _work(
        saga,
        _plan(
            es.LESSER_WORK,
            device_id="ring",
            effect_id="warm",
            vis_art="Creo",
            book_id=text.id,
        ),
    )
    assert found == [] and work.finished  # 25 >= 15, not twice it


def test_a_lab_text_gives_a_charge_per_five_of_the_lab_total():
    saga = _saga()
    text = _text(saga, "wand", "bolt")
    plan = _plan(es.CHARGED_WORK, device_id="wand", effect_id="bolt", book_id=text.id)
    found, work = _work(saga, plan)
    assert found == [] and work.charges == 5  # 25 / 5, not (25 - 15) / 5


def test_a_lab_text_reproduces_its_effect_exactly():
    saga = _saga()
    magus = saga.character("m")
    staff, ring = _device(saga, "staff"), _device(saga, "ring")
    fire, warm = staff.effects[0], ring.effects[0]
    text = _text(saga, "ring", "warm")
    assert es.effect_texts(saga, magus, ring, warm) == [text]
    assert es.text_problem(saga, magus, ring, warm, text) is None
    # Not for another effect, or another kind of device.
    assert "is level" in es.text_problem(saga, magus, staff, fire, text)
    fire_text = _text(saga, "staff", "fire", device_type="Lesser Enchantment")
    assert es.text_problem(saga, magus, staff, fire, fire_text) == (
        "Lab Text: Fire is for a Lesser Enchantment; Staff is a Invested Device."
    )
    # A raw text by someone else has to be decoded first.
    text.raw, text.author = True, "Flavia"
    assert "decode it first" in es.text_problem(saga, magus, ring, warm, text)
    assert es.effect_texts(saga, magus, ring, warm) == []
    # A talisman's text is no use to anyone but its maker.
    text.raw, text.device_type = False, "Talisman"
    ring.talisman = True
    assert es.text_problem(saga, magus, ring, warm, text) == (
        "Lab Text: Warmth is of a talisman's effect: no use to anyone else."
    )
    text.author_id = "m"
    assert es.text_problem(saga, magus, ring, warm, text) is None


def test_attuning_makes_the_talisman():
    saga = _saga()
    staff = _device(saga, "staff")
    staff.pawns_opened, staff.maker_id = 6, "m"
    seasons.plan_lab_work(saga, _plan(es.ATTUNE, device_id="staff"))
    _run(saga)
    assert staff.talisman
    # The talisman adds 5 when its magus instils effects in it.
    _, work = _work(
        saga, _plan(es.INSTIL, device_id="staff", effect_id="fire", vis_art="Creo")
    )
    assert int(work.lab_total.total) == 30
    ring = _device(saga, "ring")
    ring.type, ring.pawns_opened, ring.maker_id = INVESTED, 4, "m"
    found, _ = _work(saga, _plan(es.ATTUNE, device_id="ring"))
    assert found[0].startswith("Tiberius already has a talisman (Staff)")


def test_investigating_finds_powers_weakest_first():
    saga = _saga()
    plan = _plan(es.INVESTIGATE, device_id="box", die=3)
    found, work = _work(saga, plan)
    assert found == [] and int(work.lab_total.total) == 18 and work.level == 5
    seasons.plan_lab_work(saga, plan)
    _run(saga)
    box = _device(saga, "box")
    # A typed die is used for one roll: 18 + 3 finds the level 5 power.
    assert [e.known for e in box.effects] == [True, False]
    assert "found Lid" in saga.character("m").diary[-1].details


async def test_the_lab_work_screen_offers_an_effects_lab_texts():
    from support import wait_until
    from textual.widgets import Select, Tree

    from ars_magica_manager import storage
    from ars_magica_manager.tui.app import ArsMagicaManagerApp
    from ars_magica_manager.tui.screens.invent_spell import InventSpellScreen

    saga = _saga()
    text = _text(saga, "wand", "bolt")
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        await pilot.press("enter")
        await pilot.pause()
        ws = app.screen
        tree = ws.query_one("#nav-tree", Tree)

        def node():
            pending = [tree.root]
            while pending:
                found = pending.pop()
                if found.data == ("laboratory", "lab"):
                    return found
                pending.extend(found.children)
            return None

        assert await wait_until(pilot, lambda: node() is not None)
        tree.select_node(node())
        await wait_until(pilot, lambda: ws._laboratory_sheet_view is not None)
        view = ws._laboratory_sheet_view
        await wait_until(pilot, lambda: view.initial_tab_seen)
        await wait_until(pilot, lambda: ws._active_section() == "tab-lab-planning")
        await pilot.press("e")
        assert await wait_until(
            pilot, lambda: isinstance(app.screen, InventSpellScreen)
        )
        screen = app.screen
        await wait_until(pilot, lambda: bool(screen.query("#inv-activity")))
        screen.set_activity(es.CHARGED_WORK)
        await pilot.pause()
        row = screen.query_one("#inv-effect-text-row")
        assert await wait_until(pilot, lambda: row.display)
        screen.query_one("#inv-device", Select).value = "wand"
        await pilot.pause()
        screen.query_one("#inv-effect", Select).value = "bolt"
        await pilot.pause()
        choice = screen.query_one("#inv-effect-text", Select)
        # Choosing the effect offers the Lab Texts it could be made from.
        assert await wait_until(
            pilot,
            lambda: (
                [value for _, value in choice._options if value == text.id] == [text.id]
            ),
        )
        assert screen.current_plan().book_id is None
        choice.value = text.id
        await pilot.pause()
        plan = screen.current_plan()
        assert plan.book_id == text.id
        found, work = lab_seasons.work(saga, saga.character("m"), plan)
        assert found == [] and work.charges == 5


async def test_the_lab_work_screen_takes_pawns_of_the_other_art():
    from support import wait_until
    from textual.widgets import Input, Select, Tree

    from ars_magica_manager import storage
    from ars_magica_manager.tui.app import ArsMagicaManagerApp
    from ars_magica_manager.tui.screens.invent_spell import InventSpellScreen

    storage.save_saga(_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        await pilot.press("enter")
        await pilot.pause()
        ws = app.screen
        tree = ws.query_one("#nav-tree", Tree)

        def node():
            pending = [tree.root]
            while pending:
                found = pending.pop()
                if found.data == ("laboratory", "lab"):
                    return found
                pending.extend(found.children)
            return None

        assert await wait_until(pilot, lambda: node() is not None)
        tree.select_node(node())
        await wait_until(pilot, lambda: ws._laboratory_sheet_view is not None)
        view = ws._laboratory_sheet_view
        await wait_until(pilot, lambda: view.initial_tab_seen)
        await wait_until(pilot, lambda: ws._active_section() == "tab-lab-planning")
        await pilot.press("e")
        assert await wait_until(
            pilot, lambda: isinstance(app.screen, InventSpellScreen)
        )
        screen = app.screen
        await wait_until(pilot, lambda: bool(screen.query("#inv-activity")))
        screen.set_activity(es.INSTIL)
        await pilot.pause()
        screen.query_one("#inv-device", Select).value = "staff"
        await pilot.pause()
        screen.query_one("#inv-effect", Select).value = "fire"
        await pilot.pause()
        other = screen.query_one("#inv-other-vis", Input)
        assert await wait_until(pilot, lambda: other.display)
        other.value = "1"
        await pilot.pause()
        plan = screen.current_plan()
        assert (plan.vis_art, plan.other_vis) == ("Creo", 1)
        # The box fits on the dialog's row at 120 columns.
        assert other.region.right <= 120 and other.region.width > 0


# -- Effect Expiry, similar spells and Verditius Magic --


def test_effect_expiry_multiplies_the_seasons_points():
    saga = _saga()
    _device(saga, "staff").pawns_opened = 6
    effect = _device(saga, "staff").effects[0]
    effect.expiry = "7 years"
    plan = _plan(es.INSTIL, device_id="staff", effect_id="fire", vis_art="Creo")
    _, work = _work(saga, plan)
    level = enchantment.modified_level(_device(saga, "staff"), effect)
    # Lab Total 25 against the level, the excess times 5 (DE p. 257).
    assert work.points_gained == (25 - level) * 5


def test_a_similar_spell_helps_enchanting():
    saga = _saga()
    saga.spells.append(
        Spell(id="pilum", name="Pilum", technique="Creo", form="Ignem", level=20)
    )
    saga.character("m").spells_known = [KnownSpell("pilum")]
    plan = _plan(
        es.CHARGED_WORK, device_id="wand", effect_id="bolt", similar_spell_id="pilum"
    )
    _, work = _work(saga, plan)
    assert int(work.lab_total.total) == 29  # 25 + magnitude 4


def _verditius(saga, craft="Craft: Jeweler"):
    magus = saga.character("m")
    magus.virtues_flaws.append(VirtueFlawInstance(vf_id="vf_verditius_magic"))
    magus.abilities += [
        Ability("Philosophiae", xp=ability_xp(2)),
        Ability("Craft: Jeweler", xp=ability_xp(3)),
        Ability("Finesse", xp=ability_xp(1)),
    ]
    staff = _device(saga, "staff")
    staff.verditius_runes = True
    staff.verditius_craft = craft
    return magus, staff


def test_verditius_magic_opens_the_item_for_his_craft_fewer_pawns():
    saga = _saga()
    _verditius(saga)
    found, work = _work(saga, _plan(es.OPEN, device_id="staff"))
    # 6 pawns less Craft 3: 3 paid, and it counts as opened in full.
    assert found == [] and work.vis_cost == {"Vim": 3}
    seasons.plan_lab_work(saga, _plan(es.OPEN, device_id="staff"))
    _run(saga)
    assert _device(saga, "staff").pawns_opened == 6
    assert saga.character("m").raw_vis["vim"] == 9


def test_shaped_by_magic_the_saving_is_his_finesse():
    saga = _saga()
    _verditius(saga, craft="")
    _, work = _work(saga, _plan(es.OPEN, device_id="staff"))
    assert work.vis_cost == {"Vim": 5}


def test_the_runes_and_the_makers_craft_add_to_enchanting():
    saga = _saga()
    _, staff = _verditius(saga)
    staff.pawns_opened, staff.maker_id = 6, "m"
    plan = _plan(
        es.INSTIL, device_id="staff", effect_id="fire", vis_art="Creo", shape_bonus=2
    )
    _, work = _work(saga, plan)
    labels = [line.label for line in work.lab_total.lines]
    # 25 + Shape & Material 2 + runes 2 (Philosophiae) + Craft 3.
    assert int(work.lab_total.total) == 32
    assert "Craft: Jeweler (Verditius Magic)" in labels


def test_another_magus_gets_the_runes_but_not_the_craft():
    saga = _saga()
    _, staff = _verditius(saga)
    maker = Character(id="v", name="Valens", type="magus")
    maker.virtues_flaws = [VirtueFlawInstance(vf_id="vf_verditius_magic")]
    maker.abilities = [Ability("Philosophiae", xp=ability_xp(4))]
    saga.characters.append(maker)
    saga.character("m").virtues_flaws = []
    staff.pawns_opened, staff.maker_id = 6, "v"
    plan = _plan(
        es.INSTIL, device_id="staff", effect_id="fire", vis_art="Creo", shape_bonus=1
    )
    _, work = _work(saga, plan)
    # 25 + 1 + the maker's Philosophiae 4 = 30, and no Craft.
    assert int(work.lab_total.total) == 30


def test_instilling_can_be_planned_behind_a_planned_opening():
    from ars_magica_manager.forms.lab_plan import LabPlanForm

    saga = _saga()
    seasons.plan_lab_work(saga, _plan(es.OPEN, device_id="staff"))
    magus, lab = saga.character("m"), saga.laboratories[0]
    form = LabPlanForm(saga, magus, lab, "Summer", 1220, None)
    values = {
        "activity": es.INSTIL,
        "device": "staff",
        "effect": "fire",
        "vis_from": "magus",
    }
    plan = form.plan_of(values)
    assert (plan.season, plan.device_id, plan.effect_id) == ("Summer", "staff", "fire")
    assert form.problem(values) is None
    assert _work(saga, plan)[0] == ["Staff has to be opened first."]


def test_choosing_an_effect_offers_the_device_s_matching_bonuses():
    from ars_magica_manager.forms.lab_plan import LabPlanForm
    from ars_magica_manager.models import ShapeMaterialBonus

    saga = _saga()
    staff = _device(saga, "staff")
    staff.bonuses = [
        ShapeMaterialBonus(4, "fire", "wood"),
        ShapeMaterialBonus(3, "destroy wood", "staff"),
        ShapeMaterialBonus(2, "fire", "talisman", year=1219, season="Spring"),
    ]
    magus, lab = saga.character("m"), saga.laboratories[0]
    staff.effects[0].name = "Gout"
    assert es.suggested_shape_bonus(magus, staff, staff.effects[0]) == 0
    staff.effects[0].description = "A gout of fire from the staff's end."
    assert es.suggested_shape_bonus(magus, staff, staff.effects[0]) == 4
    staff.bonuses.append(ShapeMaterialBonus(5, "flames and fire", "iron"))
    # At most Magic Theory 5 (DE p. 258).
    assert es.suggested_shape_bonus(magus, staff, staff.effects[0]) == 5
    form = LabPlanForm(saga, magus, lab, "Spring", 1220, None)
    effect = next(f for f in form.fields() if f.key == "effect")
    assert effect.fills is not None
    assert effect.fills({"effect": "fire"}) == {"device": "staff", "shape": 5}
    device = next(f for f in form.fields() if f.key == "device")
    assert device.fills is not None
    assert device.fills({"device": "staff", "effect": "fire"}) == {"shape": 5}
    assert device.fills({"device": "staff"}) == {}


def test_opening_a_talisman_gains_the_attunement_chosen():
    """DE p. 259: each season a talisman is opened or instilled, one
    attunement from its shapes and materials."""
    from ars_magica_manager.models import ShapeMaterialBonus

    saga = _saga()
    staff = _device(saga, "staff")
    staff.talisman, staff.maker_id = True, "m"
    staff.bonuses = [ShapeMaterialBonus(4, "control things at a distance", "staff")]
    magus = saga.character("m")
    assert es.attunement_options(saga, magus) == [
        ("Staff: +4 control things at a distance (staff)", "staff:0")
    ]
    plan = _plan(es.OPEN, device_id="staff", attunement="staff:0")
    assert es.attune(staff, plan) is not None
    assert staff.attunements[0].year == 1220 and staff.attunements[0].bonus == 4
    # Once attuned, it isn't offered or gained again.
    assert es.attunement_options(saga, magus) == []
    assert es.attune(staff, plan) is None

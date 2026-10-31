"""Content packs: a part of a saga's world written to a file and read
into another saga, matching what that saga already has by name, or
starting a new saga from one."""

from __future__ import annotations

from pathlib import Path

from support import everything_saga, menu

from ars_magica_manager import packs, storage, threats, transfer
from ars_magica_manager.commands import Refuse
from ars_magica_manager.forms import creation as creation_forms
from ars_magica_manager.forms import saga as saga_forms
from ars_magica_manager.models import Saga


def _rhine_pack(saga: Saga) -> dict:
    rhine = saga.tribunal("rhine")
    assert rhine is not None
    return packs.pack_data(saga, "The Rhine", [rhine], [], [])


def test_a_tribunal_takes_everything_in_it():
    saga = everything_saga()
    keep = saga.covenant("cov1")
    assert keep is not None
    keep.place_id = "drachenfels"
    data = _rhine_pack(saga)
    held = data["saga"]
    assert data["kind"] == transfer.PACK and data["name"] == "The Rhine"
    assert [t["name"] for t in held["tribunals"]] == ["Rhine"]
    assert {c["name"] for c in held["covenants"]} == {"Keep", "Fengheld"}
    members = {c.id for c in saga.covenants if c.tribunal_id == "rhine"}
    assert {c["id"] for c in held["characters"]} >= {
        c.id for c in saga.characters if c.covenant_id in members
    }
    # The places the covenants sit in come along, and whatever is in them.
    # The place Keep sits in comes along, the place round it, and what is
    # in them; a neighbour with an attitude toward Keep too.
    taken = {n["id"] for n in held["neighbours"]}
    assert {"drachenfels", "siebengebirge", "coven"} <= taken
    assert "cologne" not in taken
    assert all(t["meeting"] is None for t in held["tribunals"])
    assert packs.summary(data).startswith("1 Tribunal, 2 covenants, ")


def test_a_pack_imports_into_an_empty_saga_with_its_links():
    saga = everything_saga()
    keep = saga.covenant("cov1")
    assert keep is not None
    keep.place_id = "drachenfels"
    data = _rhine_pack(saga)
    target = Saga(id="dst", name="Target")
    plan = transfer.plan_import(target, data)
    shown = transfer.preview(plan)
    assert shown.startswith("Import Content Pack: The Rhine from ")
    assert "  Tribunal: Rhine" in shown and "  Covenant: Keep" in shown
    transfer.apply(target, plan)
    rhine = target.tribunals[0]
    assert {c.tribunal_id for c in target.covenants} == {rhine.id}
    neighbour_ids = {n.id for n in target.neighbours}
    for record in [*target.covenants, *target.neighbours]:
        assert record.place_id is None or record.place_id in neighbour_ids
        for attitude in getattr(record, "attitudes", []):
            assert target.covenant(attitude.covenant_id) is not None
    placed = next(c for c in target.covenants if c.name == "Keep")
    assert target.neighbour(placed.place_id).name == "The Drachenfels"
    covenant_ids = {c.id for c in target.covenants}
    assert all(e.covenant_id in (None, *covenant_ids) for e in target.calendar)
    assert target.calendar


def test_importing_a_pack_again_adds_nothing_twice():
    saga = everything_saga()
    data = _rhine_pack(saga)
    target = Saga(id="dst", name="Target")
    transfer.apply(target, transfer.plan_import(target, data))
    before = (
        len(target.covenants),
        len(target.characters),
        len(target.neighbours),
        len(target.calendar),
        len(target.tribunals),
        len(target.books),
    )
    again = transfer.plan_import(target, data)
    shown = transfer.preview(again)
    assert "Already here, kept as they are:\n  Covenant Keep" in shown
    assert "  Tribunal Rhine" in shown
    assert "already in the calendar" in shown
    transfer.apply(target, again)
    after = (
        len(target.covenants),
        len(target.characters),
        len(target.neighbours),
        len(target.calendar),
        len(target.tribunals),
        len(target.books),
    )
    assert after == before


def test_a_record_of_the_same_name_takes_the_packs_links():
    saga = everything_saga()
    data = _rhine_pack(saga)
    target = Saga(id="dst", name="Target")
    from ars_magica_manager import creation

    own = creation.add_covenant(target, "Keep")
    plan = transfer.plan_import(target, data)
    assert "Covenant Keep" in plan.already
    transfer.apply(target, plan)
    assert [c.name for c in target.covenants].count("Keep") == 1
    # Keep's characters join the saga's own Keep.
    assert any(c.covenant_id == own.id for c in target.characters)


def test_the_export_form_ticks_records_and_writes_the_pack(tmp_path):
    saga = everything_saga()
    form = packs.export_pack(saga, tmp_path)
    fields = {f.key: f for f in form.fields()}
    rhine = packs.tick("tribunal", [t.id for t in saga.tribunals].index("rhine"))
    keep_key = packs.tick("covenant", [c.id for c in saga.covenants].index("cov1"))
    assert fields[rhine].label == "Tribunal: Rhine"
    assert fields[keep_key].label == "Covenant: Keep"
    values = {k: f.value for k, f in fields.items() if f.kind != "info"}
    assert form.validate is not None
    assert form.validate(values) == (
        "Tick what the pack holds: a Tribunal, a covenant or a neighbour."
    )
    # A covenant of a ticked Tribunal goes with it, so it isn't asked.
    keep = fields[keep_key]
    assert keep.show_if is not None
    assert keep.show_if(values) is True
    values[rhine] = True
    assert keep.show_if(values) is False
    assert form.live is not None and "Holds 1 Tribunal" in form.live(values)
    assert form.validate(values) is None
    said = form.apply(values)
    assert isinstance(said, list) and said[0].startswith("Exported ")
    written = transfer.read(packs._path(values))
    assert written["kind"] == transfer.PACK
    values["file"] = str(tmp_path)
    assert form.validate(values) == "That is a folder: add a file name."


def test_a_new_saga_starts_from_a_pack(tmp_path):
    saga = everything_saga()
    packs.write(storage.exports_dir() / "rhine.amm.json", _rhine_pack(saga))
    # Other exports in the folder are not packs.
    transfer.export_saga_to(storage.exports_dir() / "all.amm.json", saga)
    found = packs.available(storage.exports_dir())
    assert [label.split(":")[0] for label, _path, _data in found] == ["Rhine Tribunal"]
    assert "Tribunal," not in found[0][0]
    fields = {f.key: f for f in creation_forms.saga_fields(None)}
    assert fields["pack"].value == ""
    assert (fields["pack"].options or [])[0] == ("None", "")
    form = saga_forms.new_saga_form()
    values = {f.key: f.value for f in form.fields() if f.kind != "info"}
    values.update(name="Rhine Saga", storyguide="Hedda", pack=found[0][1])
    form.apply(values)
    made = next(
        storage.load_saga(i)
        for i in storage.list_sagas()
        if storage.load_saga(i).name == "Rhine Saga"
    )
    assert {c.name for c in made.covenants} == {"Keep", "Fengheld"}
    assert [t.name for t in made.tribunals] == ["Rhine"]


def test_a_bad_pack_is_refused_on_import(tmp_path):
    from ars_magica_manager.forms import importing as import_forms

    saga = everything_saga()
    path = transfer.export_saga_to(tmp_path / "all.amm.json", saga)
    refused = import_forms.import_file(saga, "pack", path)
    assert isinstance(refused, Refuse)
    assert "choose A Whole Saga in the Import list" in refused.why


async def test_the_terminal_exports_a_pack_from_more():
    from support import wait_until
    from textual.widgets import Checkbox, Tree

    from ars_magica_manager.tui.app import ArsMagicaManagerApp
    from ars_magica_manager.tui.screens import FieldsDialog, WorkspaceScreen

    source = everything_saga()
    source.id = "test_saga"
    storage.save_saga(source)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        await pilot.press("enter")
        assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        workspace = app.screen
        tree = workspace.query_one("#nav-tree", Tree)
        tree.select_node(tree.root)
        assert await wait_until(pilot, lambda: workspace.selected_kind.value == "saga")
        await menu(pilot, app, "m", "Export Pack")
        assert await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
        rhine = [t.id for t in source.tribunals].index("rhine")
        box = app.screen.query_one(f"#fld-{packs.tick('tribunal', rhine)}", Checkbox)
        box.value = True
        assert await wait_until(pilot, lambda: bool(app.screen.query("#btn-save")))
        app.screen.query_one("#btn-save").press()
        target = storage.exports_dir() / packs.file_name(f"{source.name} pack")
        assert await wait_until(pilot, lambda: target.is_file())
        assert transfer.read(target)["kind"] == transfer.PACK


def test_narrowing_a_pack_leaves_out_what_is_unticked():
    saga = everything_saga()
    keep = saga.covenant("cov1")
    assert keep is not None
    keep.place_id = "drachenfels"
    data = _rhine_pack(saga)
    fields = {f.key: f for f in packs.import_fields(data)}
    assert set(fields) == {"people", "places", "world", "code", "history", "bestiary"}
    assert all(f.value is True for f in fields.values())
    assert fields["places"].label.startswith("Places and regiones (")
    # All ticked: the data as it is.
    ticked = {key: True for key in fields}
    assert packs.narrow(data, ticked) is data
    # Nothing but the Tribunal and its covenants.
    bare = packs.narrow(data, {key: False for key in fields})
    held = bare["saga"]
    assert held["characters"] == [] and held["laboratories"] == []
    assert held["neighbours"] == [] and held["calendar"] == []
    assert held["creatures"] == []
    assert all(t["diary"] == [] for t in held["tribunals"])
    assert {c["name"] for c in held["covenants"]} == {"Keep", "Fengheld"}
    # The records left out are named in the links, so the plan can say
    # what became of what pointed at them.
    assert bare["links"][transfer.NEIGHBOUR]["drachenfels"] == "The Drachenfels"
    assert "mag_sketch" in bare["links"][transfer.CHARACTER]
    assert bare["links"][transfer.CREATURE]["aeolus"] == "Aeolus"
    assert data["saga"]["neighbours"], "the pack itself is untouched"
    # Places only: the mundane world stays out, the places come.
    some = packs.narrow(data, {**ticked, "world": False})
    assert all(n["kind"] == "place" for n in some["saga"]["neighbours"])
    assert "Tribunal" in packs.summary(some)


def test_an_import_without_places_drops_the_covenants_place():
    saga = everything_saga()
    keep = saga.covenant("cov1")
    assert keep is not None
    keep.place_id = "drachenfels"
    data = _rhine_pack(saga)
    target = Saga(id="dst", name="Target")
    plan = transfer.plan_import(target, packs.narrow(data, {"places": False}))
    assert "Neighbour The Drachenfels: not in this saga" in transfer.preview(plan)
    transfer.apply(target, plan)
    assert all(c.place_id is None for c in target.covenants)
    assert all(n.kind != "place" for n in target.neighbours)


def test_importing_a_pack_asks_what_to_bring_then_previews(tmp_path):
    from ars_magica_manager.commands import Confirm, Form
    from ars_magica_manager.forms import importing as import_forms

    saga = everything_saga()
    path = packs.write(tmp_path / "rhine.amm.json", _rhine_pack(saga))
    target = Saga(id="dst", name="Target")
    step = import_forms.import_file(target, "pack", path)
    assert isinstance(step, Form) and step.help_id == "import-pack"
    assert step.title == "Import The Rhine" and step.save_label == "Preview"
    values = {f.key: f.value for f in step.fields()}
    assert step.live is not None and step.live(values).startswith("Brings 1 Tribunal")
    values["world"] = False
    confirm = step.apply(values)
    assert isinstance(confirm, Confirm)
    assert "  Covenant: Keep" in confirm.question
    assert "Lord: Gottfried of Arnsberg" not in confirm.question
    confirm.apply()
    assert {c.name for c in target.covenants} == {"Keep", "Fengheld"}
    assert all(n.kind == "place" for n in target.neighbours)


def test_the_new_saga_form_reads_each_pack_once(monkeypatch):
    saga = everything_saga()
    packs.write(storage.exports_dir() / "rhine.amm.json", _rhine_pack(saga))
    packs.write(storage.exports_dir() / "other.amm.json", _rhine_pack(saga))
    reads: list[Path] = []
    real_read = transfer.read

    def counted(path: Path) -> dict:
        reads.append(Path(path))
        return real_read(path)

    monkeypatch.setattr(transfer, "read", counted)
    monkeypatch.setattr(packs, "SHIPPED_DIR", storage.exports_dir() / "none")
    creation_forms.saga_fields(None)
    assert sorted(p.name for p in reads) == ["other.amm.json", "rhine.amm.json"]


def test_an_overlay_adds_to_its_tribunal_and_remembers_the_rest():
    overlay = transfer.read(packs.SHIPPED_DIR / "through_the_aegis.amm.json")
    assert packs.is_overlay(overlay)
    saga = Saga(id="dst", name="Target")
    packs.start_from(saga, packs.SHIPPED_DIR / "provence.amm.json")
    assert "Jardin" not in {c.name for c in saga.covenants}
    packs.apply_overlay(saga, overlay)
    assert "Jardin" in {c.name for c in saga.covenants}
    assert "Didyma" not in {c.name for c in saga.covenants}
    packs.start_from(saga, packs.SHIPPED_DIR / "theban.amm.json")
    assert "Didyma" in {c.name for c in saga.covenants}
    assert saga.overlays == ["TtA"]


def test_an_overlay_is_not_offered_as_a_pack_to_start_from():
    found = packs.available(packs.SHIPPED_DIR)
    assert not any(packs.is_overlay(data) for _label, _path, data in found)


def _magi_of_hermes() -> dict:
    return transfer.read(packs.SHIPPED_DIR / "magi_of_hermes.amm.json")


def test_every_magus_of_hermes_comes_with_every_printed_age():
    data = _magi_of_hermes()
    assert len(data[packs.VARIANTS]) == 15
    assert sum(len(v) for v in data[packs.VARIANTS].values()) == 72
    assert all(v[0]["label"] == "Gauntlet" for v in data[packs.VARIANTS].values())


def test_the_age_chosen_and_the_base_year_set_the_year_of_birth():
    data = _magi_of_hermes()
    saga = Saga(id="dst", name="Target", current_year=1240)
    fields = packs.import_fields(data, saga)
    assert fields[0].key == packs.BASE_YEAR and fields[0].value == 1240
    names = {c["name"]: c["id"] for c in data["saga"]["characters"]}
    key = names["Hugh of Flambeau"]
    versions = data[packs.VARIANTS][key]
    values = {packs.BASE_YEAR: 1240, packs.variant_key(key): "+15"}
    chosen = packs.narrow(data, values)
    (hugh,) = chosen["saga"]["characters"]
    age = next(v["age"] for v in versions if v["label"] == "+15")
    assert hugh["background"]["year_born"] == 1240 - age


def test_marcus_replaces_his_theban_sketch_only_when_this_pack_comes_in():
    saga = Saga(id="dst", name="Target")
    packs.start_from(saga, packs.SHIPPED_DIR / "theban.amm.json")
    sketch = next(c for c in saga.characters if c.name == "Marcus Tauros")
    data = _magi_of_hermes()
    key = next(
        c["id"] for c in data["saga"]["characters"] if c["name"] == "Marcus Tauros"
    )
    chosen = packs.narrow(data, {packs.BASE_YEAR: 1220, packs.variant_key(key): "+30"})
    transfer.apply(saga, transfer.plan_import(saga, chosen))
    packs.after_import(saga, chosen)
    marcus = [c for c in saga.characters if c.name == "Marcus Tauros"]
    assert len(marcus) == 1 and marcus[0].id == sketch.id
    assert any(a.name == "Enigmatic Wisdom" for a in marcus[0].abilities)


def test_a_magus_joins_the_covenant_the_book_ties_them_to_whichever_comes_first():
    data = _magi_of_hermes()
    key = next(
        c["id"]
        for c in data["saga"]["characters"]
        if c["name"].startswith("Conscientia")
    )
    chosen = packs.narrow(data, {packs.BASE_YEAR: 1220, packs.variant_key(key): "+15"})
    saga = Saga(id="dst", name="Target")
    transfer.apply(saga, transfer.plan_import(saga, chosen))
    packs.after_import(saga, chosen)
    conscientia = next(c for c in saga.characters if c.name.startswith("Conscientia"))
    assert conscientia.covenant_id is None
    packs.start_from(saga, packs.SHIPPED_DIR / "rhine.amm.json")
    conscientia = next(c for c in saga.characters if c.name.startswith("Conscientia"))
    durenmar = next(c for c in saga.covenants if c.name == "Durenmar")
    assert conscientia.covenant_id == durenmar.id


def test_legends_of_hermes_imports_with_its_stories_asleep():
    data = transfer.read(packs.SHIPPED_DIR / "legends_of_hermes.amm.json")
    assert not data["saga"]["tribunals"] and not data["saga"]["covenants"]
    target = Saga(id="dst", name="Target")
    transfer.apply(target, transfer.plan_import(target, data))
    held = [n for n in target.neighbours if n.kind == "threat"]
    assert len(held) == 34 and all(threats.is_dormant(n) for n in held)

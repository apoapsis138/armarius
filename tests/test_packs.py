"""Content packs: a part of a saga's world written to a file and read
into another saga, matching what that saga already has by name, or
starting a new saga from one."""

from __future__ import annotations

from pathlib import Path

import pytest
from support import everything_saga, menu

from ars_magica_manager import (
    book_packs,
    catalog,
    character_templates,
    packs,
    storage,
    threats,
    transfer,
)
from ars_magica_manager.book_packs import templates
from ars_magica_manager.commands import Refuse
from ars_magica_manager.forms import creation as creation_forms
from ars_magica_manager.forms import importing as import_forms
from ars_magica_manager.forms import saga as saga_forms
from ars_magica_manager.models import Character, CharacterTemplateDef, Neighbour, Saga


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
    assert [label.split(":")[0] for label, _path, _data in found] == [
        "The Rhine (Rhine Tribunal)"
    ]
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
    monkeypatch.setattr(packs, "STARTERS_DIR", storage.exports_dir() / "none")
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


def test_every_saga_starter_is_a_pack_that_imports_clean_over_its_tribunal():
    """Each saga starter is a plain pack, and comes into a saga started
    from the shipped Rhine pack with nothing skipped, stubbed or dropped."""
    starters = sorted(packs.STARTERS_DIR.glob(f"*{transfer.SUFFIX}"))
    assert starters
    offenders = []
    for path in starters:
        data = transfer.read(path)
        if (
            data.get("kind") != packs.PACK
            or packs.is_overlay(data)
            or packs.is_book_of_magi(data)
        ):
            offenders.append(f"{path.name}: not a plain pack")
            continue
        saga = Saga(id="s", name="S")
        packs.start_from(saga, packs.SHIPPED_DIR / "rhine.amm.json")
        plan = transfer.plan_import(saga, data, pictures=transfer.Pictures(path))
        problems = [
            *plan.skipped,
            *plan.dropped,
            *plan.notes,
            *(f"stub covenant {c.name}" for c in plan.stub_covenants),
        ]
        offenders += [f"{path.name}: {problem}" for problem in problems]
        transfer.apply(saga, plan)
    assert not offenders, "Saga starters that don't import clean:\n" + "\n".join(
        offenders
    )


def test_a_pack_s_introduction_shows_under_it_only_while_it_is_chosen(monkeypatch):
    monkeypatch.setattr(packs, "SHIPPED_DIR", storage.exports_dir() / "none")
    monkeypatch.setattr(packs, "STARTERS_DIR", storage.exports_dir() / "none")
    saga = everything_saga()
    with_one = {**_rhine_pack(saga), transfer.INTRODUCTION: "The Keep.\n\nIts story."}
    packs.write(storage.exports_dir() / "intro.amm.json", with_one)
    packs.write(storage.exports_dir() / "plain.amm.json", _rhine_pack(saga))
    found = packs.available(storage.exports_dir())
    (intro,) = packs.start_intro_fields(found)
    assert intro.kind == "info" and not intro.label
    assert intro.value == "The Keep.\n\nIts story."
    paths = {Path(path).name: path for _label, path, _data in found}
    assert intro.show_if is not None
    assert intro.show_if({"pack": paths["intro.amm.json"]})
    assert not intro.show_if({"pack": paths["plain.amm.json"]})
    assert not intro.show_if({"pack": ""})
    # It sits right under the choice of pack.
    keys = [f.key for f in creation_forms.saga_fields(None)]
    assert keys[keys.index("pack") + 1] == intro.key


def test_export_pack_writes_its_introduction_and_leaves_a_blank_one_out(tmp_path):
    saga = everything_saga()
    form = packs.export_pack(saga, tmp_path)
    fields = {f.key: f for f in form.fields()}
    assert fields["introduction"].kind == "area"
    values = {k: f.value for k, f in fields.items() if f.kind != "info"}
    values[packs.tick("tribunal", [t.id for t in saga.tribunals].index("rhine"))] = True
    values["introduction"] = "  The Keep.\n\nIts story.\n "
    form.apply(values)
    assert transfer.read(packs._path(values))[transfer.INTRODUCTION] == (
        "The Keep.\n\nIts story."
    )
    values["introduction"] = "   "
    form.apply(values)
    assert transfer.INTRODUCTION not in transfer.read(packs._path(values))


def test_a_pack_whose_introduction_is_not_text_is_refused(tmp_path):
    saga = everything_saga()
    path = tmp_path / "bad.amm.json"
    packs.write(path, {**_rhine_pack(saga), transfer.INTRODUCTION: ["not", "text"]})
    with pytest.raises(ValueError, match="introduction of The Rhine isn't text"):
        transfer.read(path)
    assert packs.available(tmp_path) == []


def test_the_dammerstein_starter_has_its_introduction():
    data = transfer.read(packs.STARTERS_DIR / "dammerstein.amm.json")
    assert data[transfer.INTRODUCTION].startswith("Dammërstein, the Stone House\n\n")


def _with_tables(data: dict, name: str, *tables: str) -> dict:
    """`data` with roll tables of these names on its neighbour `name`."""
    for neighbour in data["saga"]["neighbours"]:
        if neighbour["name"] == name:
            neighbour["details"]["tables"] = [
                {"name": t, "die": "d6", "rows": f"1-6: {t}.", "last": "rolled"}
                for t in tables
            ]
    return data


def _tables(saga: Saga, name: str) -> list[dict]:
    (found,) = [n for n in saga.neighbours if n.name == name]
    return found.details.get("tables") or []


def test_a_pack_adds_its_roll_tables_to_a_record_the_saga_already_has():
    lord = "Gottfried of Arnsberg"
    target = everything_saga()
    (own,) = [n for n in target.neighbours if n.name == lord]
    own.details["tables"] = [
        {"name": "Rumours at court", "die": "d6", "rows": "1-6: Ours.", "last": ""}
    ]
    before = {k: v for k, v in own.details.items() if k != "tables"}
    summary = own.summary
    data = _with_tables(
        _rhine_pack(everything_saga()), lord, "rumours at court", "What he wants"
    )
    plan = transfer.plan_import(target, data)
    assert f"Lord {lord}" in plan.already
    assert "  1 roll table to Gottfried of Arnsberg" in transfer.preview(plan)
    transfer.apply(target, plan)
    tables = _tables(target, lord)
    # The saga's own table, whatever the case of its name, is left as it was.
    assert [(t["name"], t["rows"]) for t in tables] == [
        ("Rumours at court", "1-6: Ours."),
        ("What he wants", "1-6: What he wants."),
    ]
    assert tables[1]["last"] == ""
    # Nothing else on the record changed, and a second import adds nothing.
    assert {k: v for k, v in own.details.items() if k != "tables"} == before
    assert own.summary == summary
    again = transfer.plan_import(target, data)
    assert again.new_tables == []
    assert "roll table" not in transfer.preview(again)


def test_a_pack_s_record_the_saga_lacks_comes_with_its_tables():
    data = _with_tables(_rhine_pack(everything_saga()), "The Black Pool Coven", "Omens")
    target = Saga(id="dst", name="Target")
    plan = transfer.plan_import(target, data)
    assert plan.new_tables == []
    transfer.apply(target, plan)
    assert [t["name"] for t in _tables(target, "The Black Pool Coven")] == ["Omens"]


def _starter_on_a_base(tmp_path: Path, monkeypatch, base: str = "base") -> Path:
    """A shipped book pack ("base", the sample Rhine) and a starter built
    on it, which has a table for the base's lord: the starter's path."""
    shipped = tmp_path / "shipped"
    monkeypatch.setattr(packs, "SHIPPED_DIR", shipped)
    packs.write(shipped / "base.amm.json", _rhine_pack(everything_saga()))
    starter = _with_tables(
        _rhine_pack(everything_saga()), "Gottfried of Arnsberg", "His moods"
    )
    starter.update(name="Little Keep", base=base)
    return packs.write(tmp_path / "starters" / "little.amm.json", starter)


def test_a_starter_starts_from_its_base_pack_then_comes_in_over_it(
    tmp_path, monkeypatch
):
    path = _starter_on_a_base(tmp_path, monkeypatch)
    found = packs.available(packs.SHIPPED_DIR, path.parent)
    assert [Path(p).name for _label, p, _data in found] == [
        "base.amm.json",
        "little.amm.json",
    ]
    (line,) = packs.start_base_fields(found)
    assert line.kind == "info" and line.value == (
        "Starts from The Rhine first, then brings Little Keep in over it."
    )
    assert line.show_if is not None and line.show_if({"pack": str(path)})
    assert not line.show_if({"pack": found[0][1]})
    saga = Saga(id="s", name="S")
    said = packs.start_from(saga, path, {})
    assert said[0].startswith("Started from The Rhine")
    assert [t.name for t in saga.tribunals] == ["Rhine"]
    assert [t["name"] for t in _tables(saga, "Gottfried of Arnsberg")] == ["His moods"]
    assert sum(1 for n in saga.neighbours if n.name == "Gottfried of Arnsberg") == 1


def test_the_new_saga_form_reads_a_starter_and_its_base_once(tmp_path, monkeypatch):
    path = _starter_on_a_base(tmp_path, monkeypatch)
    monkeypatch.setattr(packs, "STARTERS_DIR", path.parent)
    monkeypatch.setattr(storage, "exports_dir", lambda: tmp_path / "none")
    reads: list[Path] = []
    real_read = transfer.read

    def counted(at: Path) -> dict:
        reads.append(Path(at))
        return real_read(at)

    monkeypatch.setattr(transfer, "read", counted)
    creation_forms.saga_fields(None)
    assert sorted(p.name for p in reads) == ["base.amm.json", "little.amm.json"]


def test_a_starter_whose_base_pack_is_missing_is_not_offered(tmp_path, monkeypatch):
    from ars_magica_manager.forms import importing as import_forms

    path = _starter_on_a_base(tmp_path, monkeypatch, base="nowhere")
    assert [p for _l, p, _d in packs.available(packs.SHIPPED_DIR, path.parent)] == [
        str(packs.SHIPPED_DIR / "base.amm.json")
    ]
    with pytest.raises(
        ValueError, match="Little Keep is built on the book pack 'nowhere'"
    ):
        packs.base_path(transfer.read(path))
    step = import_forms.import_file(Saga(id="t", name="T"), "pack", path)
    assert isinstance(step, Refuse) and "'nowhere'" in step.why


def test_importing_a_starter_brings_its_base_in_first(tmp_path, monkeypatch):
    from ars_magica_manager.commands import Confirm, Form
    from ars_magica_manager.forms import importing as import_forms

    path = _starter_on_a_base(tmp_path, monkeypatch)
    target = Saga(id="t", name="Elsewhere")
    step = import_forms.import_file(target, "pack", path)
    assert isinstance(step, Form)
    fields = step.fields()
    assert fields[0].key == "base" and fields[0].value is True
    assert fields[0].label == "First bring in the Rhine Tribunal"
    values = {f.key: f.value for f in fields if f.kind != "info"}
    base_people = next(f for f in fields if f.key == "base_people")
    assert base_people.show_if is not None and base_people.show_if(values)
    assert not base_people.show_if({**values, "base": False})
    confirm = step.apply(values)
    assert isinstance(confirm, Confirm)
    first, then = confirm.question.split("Then:")
    assert "Tribunal: Rhine" in first
    assert "1 roll table to Gottfried of Arnsberg" in then
    assert target.tribunals == []  # nothing is added before Import
    confirm.apply()
    assert [t.name for t in target.tribunals] == ["Rhine"]
    assert [t["name"] for t in _tables(target, "Gottfried of Arnsberg")] == [
        "His moods"
    ]


def test_a_starter_imported_without_its_base_warns_and_comes_in_alone(
    tmp_path, monkeypatch
):
    from ars_magica_manager.commands import Confirm, Form
    from ars_magica_manager.forms import importing as import_forms

    path = _starter_on_a_base(tmp_path, monkeypatch)
    target = Saga(id="t", name="Elsewhere")
    step = import_forms.import_file(target, "pack", path)
    assert isinstance(step, Form)
    values = {f.key: f.value for f in step.fields() if f.kind != "info"}
    values["base"] = False
    confirm = step.apply(values)
    assert isinstance(confirm, Confirm) and "Then:" not in confirm.question
    assert "Built on The Rhine, which this saga hasn't" in confirm.question
    confirm.apply()
    assert [t["name"] for t in _tables(target, "Gottfried of Arnsberg")] == [
        "His moods"
    ]


def test_a_saga_that_has_the_base_tribunal_is_not_asked(tmp_path, monkeypatch):
    from ars_magica_manager.forms import importing as import_forms

    path = _starter_on_a_base(tmp_path, monkeypatch)
    target = Saga(id="t", name="Rhine saga")
    packs.start_from(target, packs.SHIPPED_DIR / "base.amm.json")
    step = import_forms.import_file(target, "pack", path)
    keys = {f.key for f in step.fields()} if hasattr(step, "fields") else set()
    assert not any(k == "base" or k.startswith("base_") for k in keys)


def test_the_dammerstein_starter_starts_from_the_rhine_pack():
    found = packs.available(packs.SHIPPED_DIR, packs.STARTERS_DIR)
    index = [Path(p).name for _l, p, _d in found].index("dammerstein.amm.json")
    # The Rhine pack's stories are asked about under the starter too.
    keys = [f.key for f in packs.start_story_fields(found)]
    assert any(k.startswith(f"pack{index}_base_story_") for k in keys)
    saga = Saga(id="s", name="S")
    packs.start_from(saga, packs.STARTERS_DIR / "dammerstein.amm.json")
    assert [t.name for t in saga.tribunals] == ["The Rhine Tribunal"]
    assert "Dammërstein" in {c.name for c in saga.covenants}
    assert len(saga.covenants) > 1
    assert sum(1 for n in saga.neighbours if n.name == "The Black Forest") == 1
    assert saga.books_in_play is None or "GotF" in saga.books_in_play


def test_saga_starters_are_listed_after_the_book_packs():
    found = packs.available(packs.SHIPPED_DIR, packs.STARTERS_DIR)
    folders = [Path(path).parent for _label, path, _data in found]
    first = folders.index(packs.STARTERS_DIR)
    assert set(folders[:first]) == {packs.SHIPPED_DIR}
    assert set(folders[first:]) == {packs.STARTERS_DIR}
    labels = [
        label for label, path, _data in found if Path(path).parent == packs.STARTERS_DIR
    ]
    assert any(label.startswith("Dammërstein (Rhine Tribunal):") for label in labels)


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


def test_the_nile_and_africa_packs_share_their_spirits_when_both_come_in():
    saga = Saga(id="dst", name="Target")
    for name in ("nile", "africa"):
        data = transfer.read(packs.SHIPPED_DIR / f"{name}.amm.json")
        assert not data["saga"]["tribunals"] and not data["saga"]["covenants"]
        transfer.apply(saga, transfer.plan_import(saga, data))
    names = [n.name for n in saga.neighbours]
    assert names.count("The Pact of 1225") == 1
    beings = [c.name for c in saga.creatures]
    for shared in ("The Great Hunger", "The Hope"):
        assert beings.count(shared) == 1
        assert shared not in names
    assert "Er Rif" not in names and "The Rif" in names


def test_a_story_told_differently_is_the_importer_s_choice():
    saga = Saga(id="dst", name="Target")
    packs.start_from(saga, packs.SHIPPED_DIR / "cradle.amm.json")
    crusade = next(n for n in saga.neighbours if n.name == "The Fifth Crusade")
    before = len(crusade.details["stages"])
    data = transfer.read(packs.SHIPPED_DIR / "nile.amm.json")
    story = next(n for n in data["saga"]["neighbours"] if n["name"] == crusade.name)
    fields = {f.key: f for f in packs.import_fields(data, saga)}
    assert fields[packs.take_key(story["id"])].value is False
    kept = packs.narrow(data, {})
    transfer.apply(saga, transfer.plan_import(saga, kept))
    packs.after_import(saga, kept)
    assert len(crusade.details["stages"]) == before
    taken = packs.narrow(data, {packs.take_key(story["id"]): True})
    packs.after_import(saga, taken)
    assert len(crusade.details["stages"]) == len(story["details"]["stages"])


def test_some_people_with_versions_come_in_beside_those_without():
    data = book_packs.data(book_packs.PACKS["antagonists"])
    assert not packs.is_book_of_magi(data)
    everyone = len(data["saga"]["characters"])
    assert len(packs.narrow(data, {})["saga"]["characters"]) == everyone
    fields = {f.key for f in packs.import_fields(data, Saga(id="s", name="S"))}
    key = packs.variant_key("hannelore")
    assert key in fields and "people" in fields
    left = packs.narrow(data, {key: packs.LEAVE_OUT})
    assert len(left["saga"]["characters"]) == everyone - 1
    chosen = packs.narrow(data, {key: "Spoiled Daughter", packs.BASE_YEAR: 1220})
    held = next(c for c in chosen["saga"]["characters"] if c["id"] == "hannelore")
    assert held["background"]["year_born"] == 1204


def test_the_pack_templates_are_what_the_pack_builds():
    b = book_packs.PACKS["antagonists"].assemble()
    assert catalog.load_pack_template_catalog() == [
        CharacterTemplateDef.from_dict(e) for e in templates.entries(b)
    ]


def test_an_antagonist_template_needs_its_book_and_copies_the_record():
    saga = Saga(id="s", name="S", books_in_play=[])
    assert not [
        t for t in character_templates.templates_for("magus", saga) if t.source == "Ant"
    ]
    saga.books_in_play = ["Ant"]
    ingrid = next(
        t
        for t in character_templates.templates_for("magus", saga)
        if t.name.startswith("Antagonist - Ingrid")
    )
    character = Character(id="c", name="N", type="magus")
    character_templates.apply(saga, character, ingrid, {})
    printed = next(
        c
        for c in book_packs.PACKS["antagonists"].assemble().saga.characters
        if c.name == "Ingrid of House Tremere"
    )
    assert character.characteristics == printed.characteristics
    assert {a.name: a.xp for a in character.abilities} == {
        a.name: a.xp for a in printed.abilities
    }
    assert {k: v.xp for k, v in character.arts.items()} == {
        k: v.xp for k, v in printed.arts.items() if v.xp
    }
    assert len(character.spells_known) == len(printed.spells_known)
    assert character.spells_known and saga.spells


def test_the_iceland_pack_holds_vindolanda_with_no_tribunal():
    data = transfer.read(packs.SHIPPED_DIR / "iceland.amm.json")
    assert not data["saga"]["tribunals"]
    vindolanda = next(c for c in data["saga"]["covenants"] if c["name"] == "Vindolanda")
    assert vindolanda["place_id"] and not vindolanda["tribunal_id"]
    stories = [n for n in data["saga"]["neighbours"] if n["kind"] == threats.THREAT]
    assert all(n["details"].get(threats.DORMANT) for n in stories)


def _story_pack() -> dict:
    """A pack of two stories, one the pack has dormant, with a dated stage."""
    return {
        "kind": packs.PACK,
        "saga": {
            "neighbours": [
                {"id": "awake", "name": "Awake", "kind": "threat", "details": {}},
                {
                    "id": "asleep",
                    "name": "Asleep",
                    "kind": "threat",
                    "details": {"dormant": True},
                },
            ]
        },
    }


def test_a_story_the_pack_has_dormant_starts_unticked():
    ticks = {f.key: f.value for f in packs.story_fields(_story_pack())}
    assert ticks == {"story_awake": True, "story_asleep": False}


def test_ticking_a_dormant_story_begins_it_and_unticking_puts_one_to_sleep():
    pack = _story_pack()
    chosen = packs.narrow(pack, {"story_awake": False, "story_asleep": True})
    awake = next(n for n in chosen["saga"]["neighbours"] if n["id"] == "awake")
    assert awake["details"]["dormant"] and chosen[packs.BEGIN_STORIES] == ["asleep"]
    saga = Saga(id="s", name="S")
    saga.neighbours.append(
        Neighbour("asleep", "Asleep", kind="threat", details={"dormant": True})
    )
    packs.after_import(saga, chosen)
    assert not threats.is_dormant(saga.neighbours[0])


def test_the_import_form_hands_what_was_chosen_to_what_follows_the_import():
    saga = Saga(id="s", name="S")
    pack = transfer.read(packs.SHIPPED_DIR / "iceland.amm.json")
    step = import_forms._import_pack(saga, pack)
    step.apply({"story_the_lean_year": True}).apply()
    held = {n.name: threats.is_dormant(n) for n in saga.neighbours}
    assert not held["The Lean Year"] and held["The Storgodar Feud"]

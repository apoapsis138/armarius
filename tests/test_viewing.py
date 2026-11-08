"""Who may read what (viewing.py): the one read check, Known to the
players and Reveal, and what lists, facts, Diary lines, Ahead, threats,
the Atlas and exports show anyone but the storyguide."""

from __future__ import annotations

from ars_magica_manager import (
    ahead,
    atlas,
    diaries,
    help_text,
    sections,
    threats,
    transfer,
    viewing,
)
from ars_magica_manager.book_packs.builder import Builder
from ars_magica_manager.commands import Confirm, Form
from ars_magica_manager.forms import reveal
from ars_magica_manager.models import (
    Character,
    Covenant,
    Creature,
    Neighbour,
    Pin,
    Player,
    Saga,
    as_secrets,
)
from ars_magica_manager.references import Fact, Ref
from ars_magica_manager.tui.screens.widgets import HIDDEN_MARK, KNOWN_MARK, marked_title


def _saga() -> Saga:
    saga = Saga(id="s", name="S", current_year=1220, current_season="Spring")
    saga.covenants += [
        Covenant(id="home", saga_id="s", name="Home", played=True),
        Covenant(id="rival", saga_id="s", name="Rival", played=False),
    ]
    saga.neighbours += [
        Neighbour(id="lord", name="Lord Odo", kind="lord"),
        Neighbour(id="grove", name="The Hidden Grove", kind="place", known=False),
    ]
    saga.characters.append(Character(id="npc", name="Brother Anselm", type="companion"))
    saga.creatures.append(Creature(id="wolf", name="The Grey Wolf", known=False))
    return saga


def _as_table(saga: Saga) -> None:
    viewing.use(viewing.TABLE_VIEWER, saga)


def test_the_storyguide_reads_everything_and_the_table_only_what_is_known():
    saga = _saga()
    grove = saga.neighbour("grove")
    assert viewing.may_read(viewing.STORYGUIDE_VIEWER, grove, sections.SECRETS_SECTION)
    assert not viewing.may_read(viewing.TABLE_VIEWER, grove)
    lord = saga.neighbour("lord")
    assert viewing.may_read(viewing.TABLE_VIEWER, lord)
    assert not viewing.may_read(viewing.TABLE_VIEWER, lord, sections.SECRETS_SECTION)
    # A section not in the table is shown to everyone.
    assert viewing.may_read(viewing.TABLE_VIEWER, lord, "section-nb-info")


def test_a_signed_in_storyguide_reads_everything_and_a_player_does_not():
    guide = Player(id="g", name="Gail", role=viewing.STORYGUIDE)
    player = Player(id="p", name="Pia")
    assert viewing.viewer_for(guide).is_storyguide
    assert viewing.viewer_for(player).kind == viewing.PLAYER
    assert viewing.viewer_for(None).is_storyguide
    assert viewing.viewer_for(None, player_view=True) == viewing.TABLE_VIEWER
    assert viewing.TABLE_VIEWER.label == "Player view"


def test_the_troupes_own_records_are_always_known():
    saga = _saga()
    home = saga.covenant("home")
    assert home is not None
    home.known = False
    pc = Character(id="pc", name="Corvinus", type="magus")
    pc.background.player = "Hedda"
    pc.known = False
    assert viewing.is_known(home) and viewing.is_known(pc)
    assert not viewing.can_be_unknown(home)
    assert viewing.can_be_unknown(saga.covenant("rival"))


def test_every_storyguide_only_part_names_a_section_tab_or_chapter():
    known = {value for value in vars(sections).values() if isinstance(value, str)} | {
        topic_id
        for front_end in (help_text.TUI, help_text.GUI)
        for topic_id in help_text.book(front_end).topics
    }
    unknown = sorted(viewing.STORYGUIDE_ONLY - known)
    assert not unknown, f"STORYGUIDE_ONLY names no part: {', '.join(unknown)}"


def test_lists_leave_out_unknown_records_for_the_table():
    saga = _saga()
    assert len(viewing.shown(saga.neighbours)) == 2
    _as_table(saga)
    assert [n.name for n in viewing.shown(saga.neighbours)] == ["Lord Odo"]
    assert viewing.shown(saga.creatures) == []


def test_a_fact_names_no_unknown_record_and_one_naming_only_them_is_dropped():
    saga = _saga()
    lord, grove = saga.neighbour("lord"), saga.neighbour("grove")
    assert lord is not None and grove is not None
    both = Fact(
        "Members",
        "Lord Odo, The Hidden Grove",
        (Ref("neighbours", "lord", "Lord Odo"), Ref("neighbours", "grove", grove.name)),
    )
    only = Fact("Inside", "The Hidden Grove", (Ref("neighbours", "grove", grove.name),))
    plain = Fact("Ruler", "King Arthur")
    _as_table(saga)
    shown = viewing.facts([both, only, plain])
    assert [(f.label, f.value) for f in shown] == [
        ("Members", "Lord Odo"),
        ("Ruler", "King Arthur"),
    ]
    assert shown[0].refs == (Ref("neighbours", "lord", "Lord Odo"),)


def test_reveal_ticks_it_known_and_writes_a_dated_line_hiding_takes_it_out():
    saga = _saga()
    grove = saga.neighbour("grove")
    home = saga.covenant("home")
    assert grove is not None and home is not None
    step = reveal.reveal(saga, grove)
    assert isinstance(step, Confirm)
    step.apply()
    assert grove.known
    [line] = home.diary
    assert (line.year, line.season, line.name) == (
        1220,
        "Spring",
        "Revealed: The Hidden Grove",
    )
    step = reveal.conceal(saga, grove)
    assert isinstance(step, Confirm)
    step.apply()
    assert not grove.known and home.diary == []


def test_hide_from_the_players_marks_a_whole_list_at_once():
    saga = _saga()
    saga.neighbours.append(Neighbour(id="lord2", name="Lord Bero", kind="lord"))
    form = reveal.mark_unknown(saga)
    assert isinstance(form, Form)
    values = {"which": "lords", "tribunal": None}
    assert form.live is not None and form.live(values).startswith("2 records")
    form.apply(values)
    assert not any(n.known for n in saga.neighbours if n.kind == "lord")


def test_an_app_written_diary_line_about_an_unknown_record_is_the_storyguides():
    saga = _saga()
    home, grove = saga.covenant("home"), saga.neighbour("grove")
    assert home is not None and grove is not None
    diaries.write(
        1220, "Spring", "Omen", "Crows gather.", covenants=[home], neighbours=[grove]
    )
    [line] = home.diary
    assert line.about == ["neighbours:grove"]
    assert viewing.diary_readable(saga, line)
    _as_table(saga)
    assert not viewing.diary_readable(saga, line)
    grove.known = True
    assert viewing.diary_readable(saga, line)


def test_ahead_shows_the_players_only_public_dates():
    saga = _saga()
    found = [
        ahead.Entry(1220, "Summer", "A stage", ahead.THREATS, "The Dark"),
        ahead.Entry(1220, "Summer", "A trigger", ahead.PLACES, "Lord Odo"),
        ahead.Entry(1220, "Summer", "Fair", ahead.NEIGHBOURS, "The Hidden Grove"),
        ahead.Entry(1220, "Summer", "Tribunal", ahead.TRIBUNAL, "Rhine"),
    ]
    assert [e.title for e in ahead.public(saga, found)] == ["Tribunal"]


def test_a_threat_shows_the_players_only_the_stages_come():
    saga = _saga()
    threat = Neighbour(
        id="dark",
        name="The Dark",
        kind="threat",
        details={
            "moves": "A track",
            "position": 1,
            "stages": [
                {"title": "Whispers", "at": 1},
                {"title": "The Fall", "at": 3},
            ],
        },
    )
    saga.neighbours.append(threat)
    assert [r[0] for r in threats.stages_grid(saga, threat).rows] == [
        "Whispers",
        "The Fall",
    ]
    _as_table(saga)
    assert [r[0] for r in threats.stages_grid(saga, threat).rows] == ["Whispers"]
    assert [f.label for f in threats.facts(saga, threat)] == ["Stage reached"]
    assert threats.clock_text(saga, threat) == ""


def test_the_atlas_leaves_unknown_records_off_for_the_table():
    saga = _saga()
    saga.pins += [
        Pin(map_id="m", kind="neighbours", record_id="lord", x=0.1, y=0.1),
        Pin(map_id="m", kind="neighbours", record_id="grove", x=0.5, y=0.5),
    ]
    assert {s.ref.id for s in atlas.shown_pins(saga, "m")} == {"lord", "grove"}
    _as_table(saga)
    assert {s.ref.id for s in atlas.shown_pins(saga, "m")} == {"lord"}


def test_an_export_for_the_table_leaves_out_secrets_and_unknown_records():
    saga = _saga()
    lord = saga.neighbour("lord")
    assert lord is not None
    lord.secrets = as_secrets("A werewolf")
    data = transfer.export_saga_data(saga)
    # The storyguide's: everything but who signs in.
    assert transfer.for_reader(data) == transfer.without_players(data)
    assert transfer.for_reader(data)["saga"]["neighbours"][0]["secrets"]
    _as_table(saga)
    kept = transfer.for_reader(data)["saga"]
    assert [n["id"] for n in kept["neighbours"]] == ["lord"]
    assert kept["neighbours"][0]["secrets"] == []
    assert kept["creatures"] == []
    assert [c["id"] for c in kept["covenants"]] == ["home", "rival"]


def test_a_pack_marks_a_record_secret_and_the_rest_are_known():
    built = Builder("Pack")
    known = Neighbour(id="a", name="A")
    hidden = built.secret(Neighbour(id="b", name="B"))
    assert known.known and not hidden.known


def test_player_view_is_remembered_per_saga():
    assert not viewing.player_view_on("s")
    viewing.set_player_view("s", True)
    assert viewing.player_view_on("s") and not viewing.player_view_on("t")
    viewing.set_player_view("s", False)
    assert not viewing.player_view_on("s")


def test_an_old_save_loads_every_record_known():
    assert Neighbour.from_dict({"id": "x", "name": "X"}).known
    assert Creature.from_dict({"id": "x", "name": "X"}).known


def test_the_terminal_marks_a_records_name_known_or_hidden():
    saga = _saga()
    grove, lord, home = (
        saga.neighbour("grove"),
        saga.neighbour("lord"),
        saga.covenant("home"),
    )
    assert marked_title(grove).endswith(HIDDEN_MARK)
    assert marked_title(lord).endswith(KNOWN_MARK)
    assert marked_title(home) == "Home"
    _as_table(saga)
    assert marked_title(lord) == "Lord Odo"


def test_the_barred_and_looking_actions_name_real_actions_and_do_not_overlap():
    from textual.app import App

    from ars_magica_manager.forms.menu import _COMMANDS
    from ars_magica_manager.tui.screens.workspace.screen import WorkspaceScreen

    def real(name: str) -> bool:
        return (
            name in _COMMANDS
            or hasattr(WorkspaceScreen, f"action_{name}")
            or hasattr(App, f"action_{name}")
            or any(
                b.action == name
                for b in WorkspaceScreen.BINDINGS
                if hasattr(b, "action")
            )
        )

    named = viewing.PLAYER_BARRED_ACTIONS | viewing.LOOKING_ACTIONS
    gone = sorted(n for n in named if not real(n))
    assert not gone, f"no such action: {gone}"
    both = viewing.PLAYER_BARRED_ACTIONS & viewing.LOOKING_ACTIONS
    assert not both, f"barred and looking: {sorted(both)}"

"""More on the saga: its date and seasons, hosting, export and import, its Sessions and the Chronicle."""

from __future__ import annotations

from ... import merges, storage, undo_season
from ...actions import NodeKind
from ...sections import (
    HANDOUTS_SECTION,
    PLAYERS_SECTION,
    SESSION_SCENES_SECTION,
    SESSIONS_SECTION,
)
from .. import downtime, player_handouts, scene_verbs
from .. import handouts as handout_forms
from .. import hosting as hosting_forms
from .. import message as message_forms
from .. import reveal as reveal_forms
from .. import sessions as session_forms
from .. import show as show_forms
from ..menu_refresh import calculator, changes
from ..menu_steps import (
    export_cult,
    export_saga,
    import_command,
    on_session,
    pack_command,
    set_date,
)
from .entry import MoreAction
from .rules import (
    begins_session,
    ends_scene,
    ends_session,
    exports_cult,
    exports_saga,
    glances_cast,
    hosts,
    imports,
    merges_doubles,
    on_region,
    on_saga,
    opens_session,
    opens_show,
    previews_handout,
    reads_chronicle,
    reads_player_handouts,
    sends_message,
    sets_scene,
    shows_at_session,
    shows_handout,
    stops_hosting,
    withdraws_show,
)

#: This area's actions, in the order More lists them.
ENTRIES: tuple[MoreAction, ...] = (
    MoreAction(
        "open_session",
        "o",
        "Open Session",
        step=lambda page: on_session(
            page, lambda _saga, session: session_forms.open_page(session)
        ),
        refresh=calculator(),
        section="section-sessions",
        on_page=False,
        in_section=opens_session,
    ),
    MoreAction(
        "cast_glance",
        "g",
        "Cast at a Glance",
        step=lambda page: on_session(page, session_forms.cast_glance),
        refresh=calculator(),
        section="section-sessions",
        on_page=False,
        in_section=glances_cast,
    ),
    # The Virtual Tabletop (Preview): a Session's Chronicle (chronicle.py).
    MoreAction(
        "begin_session",
        "b",
        "Begin Session",
        step=lambda page: on_session(page, session_forms.begin_session),
        refresh=changes(SESSIONS_SECTION),
        section="section-sessions",
        on_page=False,
        in_section=begins_session,
    ),
    MoreAction(
        "close_session",
        "n",
        "End Session",
        step=lambda page: on_session(page, session_forms.end_session),
        refresh=changes(SESSIONS_SECTION),
        section="section-sessions",
        on_page=False,
        in_section=ends_session,
    ),
    MoreAction(
        "read_chronicle",
        "r",
        "Chronicle",
        step=lambda page: on_session(page, session_forms.read_chronicle),
        refresh=calculator(),
        section="section-sessions",
        on_page=False,
        in_section=reads_chronicle,
    ),
    # A Message or Whisper at the Session Under way (forms/message.py).
    MoreAction(
        "send_message",
        "s",
        "Message",
        step=lambda page: on_session(page, message_forms.message_here),
        refresh=calculator(),
        section="section-sessions",
        on_page=False,
        in_section=sends_message,
    ),
    # A Show to the Table or chosen Players (forms/show.py).
    MoreAction(
        "show_at_session",
        "w",
        "Show",
        step=lambda page: on_session(page, show_forms.show_here),
        # Also reveal changes the record shown, as Reveal does.
        refresh=changes(tree=True),
        section="section-sessions",
        on_page=False,
        in_section=shows_at_session,
    ),
    # Show a written Handout, from the Handouts list in Saga content: its
    # row's own button on the desktop (forms/show.py).
    MoreAction(
        "show_handout",
        "w",
        "Show",
        step=lambda page: show_forms.show_handout(
            page.saga, page.chosen_row(HANDOUTS_SECTION)
        ),
        # The form can show a record instead, and Also reveal changes it.
        refresh=changes(tree=True),
        section=HANDOUTS_SECTION,
        on_page=False,
        in_section=shows_handout,
    ),
    # Preview a written Handout on its Stationery, from the same list: its
    # row's own button on the desktop (forms/handouts.py). It writes nothing.
    MoreAction(
        "preview_handout",
        "p",
        "Preview",
        step=lambda page: handout_forms.preview_handout(
            page.saga, page.chosen_row(HANDOUTS_SECTION)
        ),
        refresh=calculator(),
        section=HANDOUTS_SECTION,
        on_page=False,
        in_section=previews_handout,
    ),
    # Set and end a Scene loaded into the Session (forms/scene_verbs.py).
    MoreAction(
        "set_scene",
        "c",
        "Set Scene",
        step=lambda page: on_session(page, scene_verbs.set_here),
        refresh=changes(SESSION_SCENES_SECTION),
        section="section-sessions",
        on_page=False,
        in_section=sets_scene,
    ),
    MoreAction(
        "end_scene",
        "j",
        "End Scene",
        step=lambda page: on_session(page, scene_verbs.end_here),
        refresh=changes(SESSION_SCENES_SECTION),
        section="section-sessions",
        on_page=False,
        in_section=ends_scene,
    ),
    # What a Player has been Shown, from their row in Players.
    MoreAction(
        "player_handouts",
        "u",
        "Handouts",
        step=lambda page: player_handouts.of_player(page.saga, page.row),
        refresh=calculator(),
        section=PLAYERS_SECTION,
        on_page=False,
        in_section=reads_player_handouts,
    ),
    # Withdraw a Show still out (forms/show.py).
    MoreAction(
        "withdraw_show",
        "x",
        "Withdraw a Show",
        step=lambda page: on_session(page, show_forms.withdraw_here),
        refresh=calculator(),
        section="section-sessions",
        on_page=False,
        in_section=withdraws_show,
    ),
    # A Show's copy, as the Chronicle's Show cards open it.
    MoreAction(
        "open_show",
        "o",
        "Open a Show",
        step=lambda page: on_session(page, show_forms.open_show),
        refresh=calculator(),
        section="section-sessions",
        on_page=False,
        in_section=opens_show,
    ),
    MoreAction(
        "import_data",
        "i",
        "Import",
        step=import_command,
        refresh=changes(tree=True, whole_page=True),
        places=((NodeKind.SAGA, "Saga Management"), (NodeKind.COVENANT, "Library")),
        in_section=imports,
    ),
    MoreAction(
        "export_saga",
        "x",
        "Export Saga",
        step=lambda page: export_saga(page.saga, storage.exports_dir(), page.deliver),
        refresh=calculator(),
        places=((NodeKind.SAGA, "Saga Management"),),
        on_record=exports_saga,
    ),
    MoreAction(
        "export_cult",
        "y",
        "Export a Cult",
        step=lambda page: export_cult(page.saga, storage.exports_dir()),
        refresh=calculator(),
        places=((NodeKind.SAGA, "Saga Management"),),
        on_record=exports_cult,
    ),
    MoreAction(
        "export_pack",
        "k",
        "Export Pack",
        step=pack_command,
        refresh=calculator(),
        places=((NodeKind.SAGA, "Saga Management"),),
        on_record=exports_saga,
    ),
    MoreAction(
        "host_saga",
        "h",
        "Host for Players",
        step=lambda _page: hosting_forms.host_form(),
        refresh=calculator(),
        places=((NodeKind.SAGA, "Saga Management"),),
        on_record=hosts,
    ),
    MoreAction(
        "stop_hosting",
        "h",
        "Stop Hosting",
        step=lambda _page: hosting_forms.stop_hosting(),
        refresh=calculator(),
        places=((NodeKind.SAGA, "Saga Management"),),
        on_record=stops_hosting,
    ),
    MoreAction(
        "set_date",
        "t",
        "Set Date",
        step=lambda page: set_date(page.saga),
        refresh=changes(date=True),
        places=((NodeKind.SAGA, "Seasons"),),
        on_record=on_saga,
    ),
    MoreAction(
        "undo_season",
        "z",
        "Undo Last Season",
        step=lambda page: undo_season.undo_command(page.saga),
        refresh=changes(tree=True, date=True),
        places=((NodeKind.SAGA, "Seasons"),),
        on_record=on_saga,
    ),
    MoreAction(
        "downtime_run",
        "o",
        "Run Downtime",
        step=lambda page: downtime.downtime_form(page.saga, storage.backup_saga),
        refresh=changes(tree=True, date=True),
        places=((NodeKind.SAGA, "Seasons"),),
        on_record=on_saga,
    ),
    MoreAction(
        "previously_on",
        "u",
        "Previously On",
        step=lambda page: session_forms.previously_on(page.saga),
        refresh=calculator(),
        places=((NodeKind.SAGA, "Seasons"),),
        on_record=on_saga,
    ),
    MoreAction(
        "merge_doubles",
        "q",
        merges.TITLE,
        step=lambda page: merges.merge_form(page.saga),
        refresh=changes(tree=True),
        places=((NodeKind.SAGA, "The Region"),),
        on_record=merges_doubles,
    ),
    MoreAction(
        "mark_unknown",
        "k",
        "Hide from the Players",
        step=lambda page: reveal_forms.mark_unknown(page.saga),
        refresh=changes(tree=True),
        places=((NodeKind.SAGA, "The Region"),),
        on_record=on_region,
    ),
)

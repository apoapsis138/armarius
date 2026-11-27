"""More on any record's page: export it, its mode and detail, who knows of it and its storyguide, its secrets and chapters, giving and devices."""

from __future__ import annotations

from functools import partial

from ... import storyguides
from ...actions import ActionFacts
from ...commands import Command, Refuse
from ...models import Character, Familiar
from ...sections import DIARY_SECTION, NEIGHBOUR_INFO_SECTION, STAGES_SECTION
from .. import player_handouts, take_up
from .. import reveal as reveal_forms
from .. import show as show_forms
from .. import virtue as virtue_forms
from ..menu_refresh import INFO_SECTIONS, Refresh, calculator, changes
from ..menu_steps import (
    arms_command,
    begin_command,
    covenant,
    delay_command,
    detail_command,
    export_command,
    found_command,
    markdown_command,
    needs,
    record_command,
    restore,
    take_up_command,
    update_command,
)
from ..page import Page
from .entry import MoreAction
from .rules import (
    acts_on_device,
    assigns_storyguide,
    bears_arms,
    changes_detail,
    exports_markdown,
    exports_record,
    gives,
    goes_to,
    has_interests,
    in_full_creation,
    on_dormant_threat,
    on_ruin,
    on_saga,
    on_secret,
    on_threat_under_way,
    restores,
    reveals,
    shows_record,
    splits_secret,
    updates_record,
)


def _read_in_full(page: Page) -> Command:
    """Read in full on the chosen row of the Virtues and Flaws section focus
    is in (forms/virtue.py)."""
    section = page.active_section() or ""
    owner = page.record_to_delete()
    if not isinstance(owner, Character | Familiar) or (
        section not in virtue_forms.READ_SECTIONS
    ):
        return Refuse(virtue_forms.READ_TITLE, virtue_forms.READ_REFUSED)
    return virtue_forms.read_in_full(owner, page.chosen_row(section))


def _reads_in_full(facts: ActionFacts, section: str) -> bool:
    """Read in full is offered on a long entry chosen in a Virtues and Flaws
    section. The section is checked first, as a sheet can only look up the
    chosen row of a section it has."""
    return section in virtue_forms.READ_SECTIONS and virtue_forms.offers_read_in_full(
        facts.record_to_delete(), section, facts.chosen_row(section)
    )


#: This area's actions, in the order More lists them.
ENTRIES: tuple[MoreAction, ...] = (
    # A long Virtue or Flaw's whole text on a reading page: the inspector's
    # own button on the desktop. It writes nothing.
    MoreAction(
        "read_in_full",
        "f",
        "Read in full",
        step=_read_in_full,
        refresh=calculator(),
        on_page=False,
        in_section=_reads_in_full,
    ),
    MoreAction(
        "restore",
        "r",
        "Restore",
        step=needs(covenant, restore),
        places=(),
        in_section=restores,
    ),
    MoreAction(
        "instill_effect",
        "i",
        "Instill an Effect",
        on_page=False,
        in_section=acts_on_device("instill_effect"),
    ),
    MoreAction(
        "use_charge",
        "c",
        "Use a Charge",
        on_page=False,
        in_section=acts_on_device("use_charge"),
    ),
    MoreAction(
        "use_effect",
        "u",
        "Use an Effect",
        on_page=False,
        in_section=acts_on_device("use_effect"),
    ),
    MoreAction("give", "g", "Give", on_page=False, on_record=gives),
    MoreAction(
        "export_record",
        "x",
        "Export",
        step=export_command,
        refresh=calculator(),
        on_record=exports_record,
    ),
    # The record's sheet as a Markdown file (markdown_sheet).
    MoreAction(
        "export_markdown",
        "j",
        "Export as Markdown",
        step=markdown_command,
        refresh=calculator(),
        on_record=exports_markdown,
    ),
    # A Show of this record at the Session Under way (forms/show.py).
    MoreAction(
        "show_record",
        "h",
        "Show to the Table",
        step=lambda page: show_forms.show_record(page.saga, page.record_to_delete()),
        # Also reveal changes the record, as Reveal does.
        refresh=changes(*INFO_SECTIONS, tree=True),
        on_record=shows_record,
    ),
    # The Handouts of whoever plays this character (forms/player_handouts).
    MoreAction(
        "my_handouts",
        "u",
        "Handouts",
        step=lambda page: player_handouts.mine(page.saga, page.record_to_delete()),
        refresh=calculator(),
        on_record=lambda facts: (
            facts.on_record()
            and player_handouts.offered_on(facts.saga, facts.record_to_delete())
        ),
    ),
    # Which interests' deeds a character's sheet offers (deeds).
    MoreAction(
        "edit_interests",
        "w",
        "Interests",
        refresh=changes("tab-diary"),
        on_record=has_interests,
    ),
    MoreAction(
        "update_record",
        "u",
        "Update from a File",
        step=update_command,
        refresh=changes(tree=True, whole_page=True),
        on_record=updates_record,
    ),
    MoreAction(
        "toggle_mode",
        "m",
        "In Creation / In Play",
        step=record_command,
        refresh=changes("section-creation", tree=True),
        on_record=partial(in_full_creation, worksheet=False),
    ),
    MoreAction(
        "promote",
        "p",
        "Promote",
        step=detail_command("promote"),
        refresh=changes(
            "section-char-info", "section-cov-info", tree=True, reshow=True
        ),
        on_record=partial(changes_detail, up=True),
    ),
    MoreAction(
        "demote",
        "o",
        "Demote",
        step=detail_command("demote"),
        refresh=changes(
            "section-char-info", "section-cov-info", tree=True, reshow=True
        ),
        on_record=partial(changes_detail, up=False),
    ),
    MoreAction(
        "creation_worksheet",
        "w",
        "Creation Worksheet",
        on_record=partial(in_full_creation, worksheet=True),
    ),
    MoreAction(
        "edit_arms",
        "a",
        "Arms",
        step=arms_command,
        refresh=changes(NEIGHBOUR_INFO_SECTION, "section-cov-info"),
        on_page=False,
        on_record=bears_arms,
    ),
    MoreAction(
        "found_covenant",
        "f",
        "Found a Covenant Here",
        step=found_command,
        refresh=Refresh((NEIGHBOUR_INFO_SECTION,), tree=True, made="covenants"),
        on_record=on_ruin,
    ),
    MoreAction(
        "begin_story",
        "b",
        "Begin This Story",
        step=begin_command,
        refresh=changes(NEIGHBOUR_INFO_SECTION, STAGES_SECTION),
        on_record=on_dormant_threat,
    ),
    MoreAction(
        "delay_threat",
        "h",
        "Delay or Hasten",
        step=delay_command,
        refresh=changes(NEIGHBOUR_INFO_SECTION, STAGES_SECTION),
        on_record=on_threat_under_way,
    ),
    # Who may read what (viewing.py): telling the players of a record, or
    # taking it back; many at once on the Region; and the storyguide's
    # own window seen as the players see it.
    MoreAction(
        "reveal",
        "k",
        "Reveal to the Players",
        step=lambda page: reveal_forms.reveal(page.saga, page.record_to_delete()),
        refresh=changes(*INFO_SECTIONS, tree=True),
        on_record=partial(reveals, known=False),
    ),
    MoreAction(
        "conceal",
        "k",
        "Hide from the Players",
        step=lambda page: reveal_forms.conceal(page.saga, page.record_to_delete()),
        refresh=changes(*INFO_SECTIONS, tree=True),
        on_record=partial(reveals, known=True),
    ),
    MoreAction("player_view", "v", "Player View", on_page=False, on_record=on_saga),
    # A record's own storyguide, with more than one (storyguides.py).
    MoreAction(
        "assign_storyguide",
        "y",
        storyguides.TITLE,
        step=lambda page: storyguides.assign_form(page.saga, page.record_to_delete()),
        refresh=changes(*INFO_SECTIONS, tree=True),
        on_record=assigns_storyguide,
    ),
    # One secret of a record's Secrets list, revealed or taken back, or
    # split into a secret for each paragraph.
    MoreAction(
        "reveal_secret",
        "k",
        "Reveal the Secret",
        on_page=False,
        in_section=partial(on_secret, revealed=False),
    ),
    MoreAction(
        "conceal_secret",
        "k",
        "Hide the Secret Again",
        on_page=False,
        in_section=partial(on_secret, revealed=True),
    ),
    MoreAction(
        "split_secret",
        "s",
        "Split by Paragraph",
        on_page=False,
        in_section=splits_secret,
    ),
    # A chapter of what the troupe did: on a threat, or a chosen open story.
    MoreAction(
        "take_up_tale",
        "t",
        "Take Up the Tale",
        step=take_up_command,
        refresh=changes(NEIGHBOUR_INFO_SECTION, DIARY_SECTION),
        on_record=on_threat_under_way,
    ),
    MoreAction(
        "take_up_story",
        "t",
        "Take Up the Tale",
        on_page=False,
        in_section=lambda facts, section: (
            section in take_up.LISTS
            and take_up.offered(
                facts.saga, section, facts.chosen_row(section), facts.selected_covenant
            )
        ),
    ),
    MoreAction("go_to", "g", "Go To", on_page=False, on_record=goes_to),
)

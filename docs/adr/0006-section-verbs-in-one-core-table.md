# A section's Add, Edit and Delete come from one core table

`section_verbs.py` maps a record and one of its sheet's sections to that
section's Add, Edit and Delete (`SectionOps`), through a plain dict of
builders keyed by the record's type (Strategy, with no class needed).
`actions.SECTION_VERBS` says which verbs a section has. Both front-ends read
the table, so a key in the terminal and a button on the desktop do the same
thing, and the terminal's own per-section handlers were removed.

Where the two front-ends had behaved differently, the core's behaviour won:
the Add dialogs became the core's chooser, and Edit or Delete on an empty
list does nothing.

The More menu follows the same rule. `forms/menu.py` holds each action's
first step, and `forms/menu_refresh.py` names what the action changes: the
sections to redraw, whether the tree changes, whether to rebuild the sheet,
and whether it saves at all (a calculator does not). The terminal's
`_run_more` builds the page (including the chosen row and book), runs the
first step and commits what the registry names, so an action with a core
command needs no handler of its own in the terminal. The actions the core has
no command for (most of the records, exports and gifts) keep theirs.

## Consequences

- A list whose rows depend on what its sheet has chosen (a Mystery Cult's
  degrees, the Spells list's filters, a Tribunal's chosen argument) can't be
  answered from the record alone, so the sheet supplies its verbs itself
  (`state_ops`), ahead of the table.
- A section with only a single Edit form is not in the table.
- `tests/test_dispatch_matrix.py` is the golden record of every section's
  keys; a change to the table shows up in its diff.

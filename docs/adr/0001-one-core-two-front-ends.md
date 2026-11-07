# One core, two front-ends; the core imports no UI library

Armarius has a terminal app (Textual) and a desktop app (PySide6). Everything
outside `tui/` and `gui/` is the core, and the core never imports a UI library
or a front-end module; neither front-end imports the other. A front-end only
draws what the core describes: sheets as rows, forms as fields, lists as
cells, and what can be done where. We chose this (Ports and Adapters) so the
rules exist once: the desktop reached parity with the terminal without a
second copy of them, and a third front-end would only have to draw.
`tests/test_core_boundary.py` enforces the line, imports inside functions
included.

## Consequences

- Logic a screen needs that isn't about drawing (parsing a form, choosing
  which verbs a section has) belongs in the core, even when only one
  front-end uses it today.
- Help true of only one front-end is marked `; tui` or `; gui`.

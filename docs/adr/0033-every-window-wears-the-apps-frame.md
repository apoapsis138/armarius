---
status: accepted
---

# Every window wears the app's frame; only the system's file pickers stay native

Every window the desktop opens over the main window (form, list, question, notice, viewer, Settings) is built on one frame-only base, `Window` (`gui/window_frame.py`): the app's drawn title bar, the theme's paper, grips and snapping. The form window, `FormWindow` (`gui/forms.py`), builds on it and adds what only a form has: the error line, Cancel and the action button, and asking before losing unsaved changes. The system's own Open, Save and folder pickers are the one exception.

A first pass (3.53.0) framed the forms and left three viewers (the shown picture, the shown copy and the Handout window) on the system's title bar, which nothing caught. The pickers stay native because Qt's own picker, the only one we could frame, loses Quick Access, OneDrive, search and recent folders.

## Considered options

- **A `framed(content)` wrapper function (a Decorator) in place of a base class:** turned down because the windows already subclass the form window, and a base class keeps every window's frame code in one place; every viewer would have been rebuilt around the wrapper, where a base class is a two-line change per window.
- **Qt's own file picker, framed like the rest:** turned down for what it loses (above).

## Consequences

- A new window subclasses `Window` (or `FormWindow` for a form) and gets the frame, the paper, the heading over the hedera rule (`add_heading`) and the safe `exec` without writing any of it (Template Method).
- A window names the buttons on its bar in its class-level `controls`; one that can maximise also resizes from its edges.
- The code's form window was called `Sheet`, which clashed with the glossary's Sheet (the view a record opens on); it is `FormWindow` now.

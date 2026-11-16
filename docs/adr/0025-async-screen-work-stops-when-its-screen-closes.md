---
status: accepted
---

# Async screen work stops when its screen closes

A terminal screen often fills itself in after it opens: a picker's `on_mount` awaits its list, Help loads a long page in a worker a few sections at a time, and the creation worksheet refreshes after each dialog with `call_after_refresh`. That work waits its turn on the event loop, and the screen can be dismissed while it waits (Esc, Go there, a form's Save, or the app quitting). Textual then removes the screen's widgets, and the work's next `query_one` raises `NoMatches`. Under a loaded parallel test run this happened often enough to make several screen tests flaky, and a user closing a window quickly could see the same crash. Each screen had grown its own answer: the worksheet checked an ad-hoc `_gone()` after every await, Help's `_scroll_to` queried and gave up when nothing was found, and the fields dialog's `_refit` caught `NoMatches` whether it was open or not.

Screens now share one rule, in `tui/screens/closing.py`. `OpenAwareScreen.is_open` says whether a screen is still open: attached to a running app and on its screen stack, so a screen merely covered by a dialog is still open. The app's running flag matters: a quitting app (and every test's end) removes each screen's widgets while the screen is still on the stack. It is the base of every `ModalDialog`, and a screen can override it (a Template Method hook). The `while_open` decorator wraps a screen method, sync or async, that may outlive its screen (an `on_mount`, a worker's coroutine, a refresh queued for later): when the method raises `NoMatches` and its screen is no longer open, the method ends quietly; when the screen is still open, the `NoMatches` is raised, since a missing widget on an open screen is a real bug; any other error is always raised.

## Considered options

- **Cancel the screen's work when it closes, as workers:** every piece would be a worker cancelled on dismiss. Rejected: Help's page loader must not be cancelled midway, since a Markdown widget cancelled during an update can wait for ever; and much of the work is `on_mount` or `call_after_refresh`, not a worker.
- **Check `_gone()` after every await, as the worksheet did:** works, but each new await needs its own check, and a missed one is a flaky test months later. Easy to forget, and hard for a reviewer to spot when it is missing.
- **Catch `NoMatches` wherever it can happen:** simple, but it also hides a widget id that is wrong on a screen that is still open.

## Consequences

- A screen method that queries its widgets after an await, or runs later than it was asked for, is decorated `@while_open`; the screens' `_gone()` and ad-hoc catches are gone.
- Only `NoMatches` is let go, and only once the screen has closed, so a wrong widget id still fails its test.
- A screen that isn't a `ModalDialog` inherits `OpenAwareScreen` to use the decorator.
- A screen is on top of the stack before it has built its widgets, so a test that types into a screen it has just opened waits for the widget first, rather than for the screen alone.
- Work on a closed screen still runs up to its first missing widget; anything it does before that (reading the saga, building rows) is wasted but harmless, as before.

---
status: proposed
---

# The Chronicle lives beside the saga, not in it

While a Session is Under way, its Chronicle is an append-only file of its own in the host's data folder, one per Session, not part of the saga file. At End Session the evening's account is folded into the Session record: its scenes, Roll requests with their "for" lines, rolls with their result and visibility, outcome notes and Shows. Whispers and table talk stay only in the Chronicle's file.

A busy evening writes a line for every roll and message; kept in the saga, each would be a save to merge three ways (ADR 0005) against every player's edits. Kept beside it, the saga changes once, at End Session.

## Considered options

- **The Chronicle inside the saga file:** one file to back up, but every roll becomes a three-way merge and the saga grows with every word said at the table.

## Consequences

- If the host stops mid-evening, the Session stays Under way: on restart its Chronicle is read back and play carries on.
- A backup of a saga includes its Sessions' Chronicle files.
- Whispers are never written into the saga, so an Export or a Content pack cannot carry them.

---
status: accepted
---

# The Chronicle lives beside the saga, not in it

While a Session is Under way, its Chronicle is an append-only file of its own in the host's data folder, one per Session, not part of the saga file: JSON Lines at `chronicles/<saga id>/<session id>.jsonl`, each entry written and flushed as it is made. Every entry has the same envelope: its number within the Session, its time, its kind, its author, its Audience and a body by kind. Nothing in the file is changed or removed: a Strike, a Confidence spend, or any other correction, is a new entry pointing at the one it amends. At End Session the evening's account is folded into the Session record: its scenes, Roll requests with their "for" lines, rolls with their result and visibility, outcome notes and Shows. Messages, Whispers among them, stay only in the Chronicle's file.

A Show outlasts its evening, because what was Shown becomes a Handout each Player shown keeps. Its entry in the Chronicle names the Show, its title and who was shown it; the frozen copy itself (the record as its Players could read it at that moment, with any Secrets the storyguide ticked, or the picture as it then was) is written once, when Shown, to a folder of its own beside the saga, `shows/<saga id>/`, as the Chronicle is, not into the saga file. So each Player's Handouts open it in any later Session without anyone searching that evening's Chronicle, and changing the record or its picture afterwards doesn't change what was Shown. A Withdraw is a new Chronicle entry; from then on the host gives that copy to no seat. Each Player's arrangement of their Handouts (their folders, their own titles, pins) is theirs alone and is kept with the saga.

A busy evening writes a line for every roll and message; kept in the saga, each would be a save to merge three ways (ADR 0005) against every player's edits. Kept beside it, the saga changes once, at End Session.

The host's computer keeps the whole Chronicle, whatever each entry's Audience: Blind rolls and whispers between others are in its file. The host's own app shows only what the host's own Audience allows, and the help says plainly that the file holds everything. Entries are not encrypted against the host, who already holds the saga and rolls the dice (ADR 0018).

## Considered options

- **The Chronicle inside the saga file:** one file to back up, but every roll becomes a three-way merge and the saga grows with every word said at the table.
- **A Show's copy only in its Chronicle entry:** nothing new to keep, but a player would have to find the evening, then the entry, to read a letter again, and a picture is too big for a Chronicle line or an event frame.
- **A Show's copy inside the saga file:** one file to back up, but a picture is binary, and each Show mid-evening would be one more three-way merge.
- **Entries kept encrypted for their Audience:** would hide a Blind roll from a host who is not the Session's storyguide, but needs keys on every seat for a protection the host could defeat by changing its own app.

## Consequences

- If the host stops mid-evening, the Session stays Under way: on restart its Chronicle is read back and play carries on. A last line left half-written is dropped.
- A backup of a saga includes its Sessions' Chronicle files and its Shows' copies.
- Messages and Whispers are never written into the saga, so an Export or a Content pack cannot carry them. Neither carries Shows' copies or Players' Handouts.
- Until the fold at End Session is built, End Session marks the Session Played and closes its Chronicle to writes; the file stays beside the saga, readable from the Session's row.

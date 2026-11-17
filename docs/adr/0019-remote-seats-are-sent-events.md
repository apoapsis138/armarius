---
status: accepted
---

# Remote seats are sent events

Protocol 2 of Remote seats adds the first messages the host starts: when an entry is added to a Session's Chronicle (a roll, a whisper, a scene set, a Show), the host sends each seat in that entry's Audience an event frame, inside the pinned inner TLS of ADR 0009. Events travel on a second connection the seat opens only for them, so the request connection and its one-request-one-answer loop are unchanged: the seat says `events_since(n)` once, and the host then sends every later entry it may see down that connection. Entries are numbered per Session, so a seat that joins late or reconnects asks from the last number it holds and catches up. Who may see an entry is decided at the host before it is sent: an entry a seat may not see is never sent to it, rather than sent and hidden by the client. Event traffic is rate-limited through `remote/limits.py`, as requests already are, and each frame stays within the existing frame cap. A seat still connects out (ADR 0009); only the direction of messages changes. This is the Observer pattern: seats subscribe to the Chronicle and are told of each new entry.

One message spec serves every kind of entry: a generic `chronicle` event carrying the entry's envelope (its number, time, kind, author, Audience and a body by kind), plus `events_since`, rather than a spec per kind. A seat that meets a kind it does not know shows that this version can't show it and asks the player to update.

Seats keep entries in memory only. A seat that restarts asks again from `events_since(0)`; nothing of the Chronicle is written on a player's computer.

## Considered options

- **Seats keep polling snapshots by revision hash:** simple and already built, but a roll would reach the table seconds late, and every poll would carry the whole view to find one new line.
- **Events on the request connection:** one connection, but the seat would have to tell an answer from an event arriving between its request and that answer; a connection of their own keeps both loops simple.
- **A message spec per kind of entry:** the registry would check each body's shape, but every new kind would need a new protocol version, and an older seat would be refused a whole Session for one entry it couldn't read.

## Consequences

- The protocol version rises to 2; a version-1 seat is refused with a message asking it to update.
- `chronicle` and `events_since` are message specs in the existing registry, so the host still sends and takes only listed types; each entry's body is shape-checked by its kind where the host builds it.
- Tests seed a marker in a Private or Blind entry and require it to be absent from every other seat's frames.
- The Remote seats threat model gains host-to-seat events at boundary B2.
- The listener runs as a process of its own (`remote/serve.py`), apart from the Storyguide's window, so the Chronicle the window writes isn't an object the listener holds. The Chronicle file is the one Chronicle: the window and the listener each append under its lock, numbering from the file rather than their own copy, and each catches up by reading what the other wrote (`Chronicle.refresh`), telling its subscribers. The listener looks about once a second for each events connection; the desktop's pane watches the file and refreshes when it changes, with the window's shared-saga tick as a fallback.

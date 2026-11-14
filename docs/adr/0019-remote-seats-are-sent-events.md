---
status: proposed
---

# Remote seats are sent events

Protocol 2 of Remote seats adds the first messages the host starts: when something happens at a Session (a roll, a whisper, a scene set, a Show), the host sends each seat that may see it an event frame, inside the pinned inner TLS of ADR 0009. Events are numbered per Session; a seat that joins late or reconnects asks for `events_since(n)` and catches up. Who may see an event is decided at the host before it is sent: an event a seat may not see is never sent to it, rather than sent and hidden by the client. Event traffic is rate-limited through `remote/limits.py`, as requests already are. A seat still connects out (ADR 0009); only the direction of messages on that connection changes.

## Considered options

- **Seats keep polling snapshots by revision hash:** simple and already built, but a roll would reach the table seconds late, and every poll would carry the whole view to find one new line.

## Consequences

- The protocol version rises to 2; a version-1 seat is refused with a message asking it to update.
- Each new event is a message spec in the existing registry, so the host still sends and takes only listed types.
- Tests seed a marker in a Private or Blind event and require it to be absent from every other seat's frames.
- The Remote seats threat model gains host-to-seat events at boundary B2.

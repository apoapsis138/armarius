---
status: accepted
---

# A remote storyguide runs the saga; the host keeps who may join

In troupe-style play more than one Player holds the Storyguide role. The role lives on the Player record, as it does for a browser sign-in, so one person has one role wherever they sign in, and only the host grants or takes it back. A Remote seat whose Player is a storyguide reads the whole saga (Secrets, unknown records, Roll Tables, threats' stages to come), but never the passcode hashes or the host's Remote seat files (devices, invites, log).

A remote storyguide changes any record, and runs the saga forward: advancing the season (or the game stops whenever the host is away) and putting back a season advanced in error. What stays with the host's own window is who may join and as what: the Players list and their roles, Host for Players (invites, approvals, seats, the log), and deleting the saga. A role change reaches the seat on its next read, within seconds, and is logged.

A season is advanced, or the saga's settings changed, on the storyguide's own full copy, exactly as the host does it, and the whole saga is sent back. The host backs its saga up, then folds the copy in with the three-way merge it already uses for hosted saves (ADR 0005), so a player's edit made meanwhile is kept unless it touched the same field. The host takes the first advance to arrive; one made from an older date is refused before anything changes, naming who advanced.

## Considered options

- **A role per seat (per device):** would let one person be storyguide on one computer and a player on another. Confusing, with no use we know of.
- **Each of Advance Season's questions relayed from the host:** the host would play the season and ask the seat each question in turn. A protocol of its own for the same result the merge already gives.
- **Saga-wide actions host-only:** simpler, but a troupe whose host is away for an evening could not advance the season, and the game would stop.
- **A storyguide limited to their own story arc:** wanted eventually (a storyguide for each story), but it needs the stories to own records first; until then a storyguide reads everything.

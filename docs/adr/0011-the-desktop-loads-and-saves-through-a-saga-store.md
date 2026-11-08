---
status: accepted
---

# The desktop loads and saves through a saga store

The desktop's pages read a saga in memory and the window saves it after each step. For a Joined game that saga is the Player's Seat view, sent by the host, and a save must go back as per-record changes (ADR 0010), never as a file. So the window loads and saves through a saga store with two kinds: the local folder (`storage`, as before) and a Remote seat, which loads the snapshot and, on save, sends each record that changed since the last snapshot as one change. The pages never know which they have (a Remote Proxy). An edit shows at once; a refused change is reported and the page is drawn again from the host.

## Considered options

- A second window for Joined games: two copies of every page to keep in step.
- Sending the whole saga back: impossible by design (the Seat view lacks what is hidden, and the host takes only per-record changes).

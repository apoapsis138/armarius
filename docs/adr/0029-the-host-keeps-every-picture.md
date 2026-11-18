---
status: accepted
---

# The host keeps every Picture

A record shows a Picture: a map's, a character's portrait, and soon a handout's. Each is a file in the save folder, in a folder for its kind, and the saga names it only by file name. In a Joined game the pictures a page needs are fetched from the host by that name and held in memory for the session.

A Joined app that added a map or portrait used to copy the picture into its own computer's folder, so the host never had it, every seat (the one that added it too) showed it as missing, and the Joined computer kept a file the Remote seats threat model says it never writes.

So the host keeps every Picture. A Joined app sends a new one up to the host, which checks it is a picture, names it by its own hash of the bytes and keeps it in the folder for its kind; the record's change then carries that name. The Joined app never writes a picture to its own disk. (The sending comes with STORY-2341 and STORY-2342.)

Each kind of Picture is one entry in a registry (`picture_files.KINDS`): its folder and the most one may be, in an export and between host and seat. A map may be 25 MB, since a hand-drawn regional map is often far larger than a portrait; a portrait 5 MB. A folder that isn't a kind is never read or written. A new kind of record with pictures is one more entry, not more plumbing.

## Considered options

- **Each seat keeps its own copy:** what the Joined app did. Every seat but the one that added it shows the picture as missing, copies drift when a picture is replaced, and a shared or borrowed computer keeps the troupe's pictures.
- **Shrink big pictures on the way in:** a picture library in the core, and a hand-drawn map loses the detail it was drawn with.
- **One cap for every kind (5 MB):** what the host had. Too small for real maps, and large enough for a portrait many times over.
- **One folder for every kind:** possible now that names are hashes, but every existing save, export and zip keeps its maps and portraits apart, and the per-kind folders cost nothing.

## Consequences

- A big map is downloaded again each time someone opens the Joined game. An opt-in picture cache on the seat, named by hash so it can't go stale or be swapped, is a possible later change.
- A picture sent up whose change never comes stays on the host until a tidy (STORY-2343).
- Exports carry maps up to 25 MB; an export with a larger picture leaves it out, as before.

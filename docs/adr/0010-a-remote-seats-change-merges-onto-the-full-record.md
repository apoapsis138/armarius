---
status: accepted
---

# A Remote seat's change is merged onto the full record

A Remote seat holds only its Seat view, so a record it edits lacks whatever is hidden from that Player (unrevealed Secrets, Diary lines about unknown records, a threat's stages to come). Saving the edited record as it stands would erase all of that. So a change carries the record twice, as it was in the Seat view and as the Player left it, and the host three-way merges the difference onto its own full record (the merge of ADR 0005, with the Seat view's record as the base): what the Player never had is unchanged on both of their sides, so the host's stays. Each change is one record, checked by `players.guard_changes` on the host; a seat never uploads the saga. Where the host's record changed in the same place since the Player's snapshot, the later save wins and the overlap is reported to the Player, as ADR 0005 does for hosted copies. Season plans and lab projects, which have no id, are named by their character and season (or character and spell), and a Player may change only those of their own characters, from a Remote seat or a browser.

## Considered options

- Send only the record as edited: erases everything hidden from the Player.
- Send a patch of changed fields: the same outcome, with a second format to keep in step with the models; the two versions reuse the merge the hosted saga already trusts.
- Refuse a change whose record moved on since the snapshot: safe, but turns every overlap at the table into lost work.

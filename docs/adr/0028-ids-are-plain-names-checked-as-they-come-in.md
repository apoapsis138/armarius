---
status: accepted
---

# Ids are plain names, checked as they come in

A saga's id names its file, and a character's id is part of its portrait's file name. Both come from files other people make: a saga file, an export, a content pack, a Remote seat's snapshot. Nothing checked them, so a saga file whose id was `../../somewhere` named a file outside the sagas folder when it was saved, and a hostile character id did the same for the portrait's copy.

So every id coming in must be a **plain id**: lowercase letters, digits, `_` and `-`, starting with a letter or digit, at most 100 characters (`shapes.PLAIN_ID`). The shape check (ADR 0012) checks it before building, in every record, for each id field: a record's `id`, a link ending `_id` and a list of links ending `_ids`; an empty link passes. A saga file, a Remote seat's data and a saga brought in by the headless admin are refused with the field named ("characters[..].id: not a plain id"); nothing repairs them on load. An import gives each record it brings in an id of its own anyway, so it is checked without the id rule (`plain_ids=False`) and re-ids what isn't plain, its links following.

Where an id becomes a path (a saga's file, a portrait's copy), a guard clause refuses a path outside its folder as well, for a record that never passed the check.

It is the validator-at-the-trust-boundary pattern again: one check, at the one place every saga file and network message already passes, rather than one at each caller.

## Considered options

- **`slugify(id) == id`:** what the app makes its own ids with, but the shipped packs have 65 ids with `-`, which `slugify` turns into `_`.
- **Allow capitals (the admin's old `[A-Za-z0-9_-]+`):** safe as a path, but no id the app makes has one, and a second rule beside the shape check's is one to drift.
- **Repair a bad id on load:** a saga's links would have to be rewritten on every open, and a file that names a path outside its folder was made to; refusing it, by field, says so.

## Consequences

- Every saga, backup and export in the maintainer's save folder and every shipped pack already passed the rule when it came in, so no real save is refused.
- `admin saga import` dropped its own safe-id rule; the shape check refuses first.
- A saga id that doesn't match its file's name is still allowed (left for later).

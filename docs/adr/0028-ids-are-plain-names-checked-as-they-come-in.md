---
status: accepted
---

# Ids are plain names, checked as they come in

A saga's id names its file, and a character's id is part of its portrait's file name. Both come from files other people make: a saga file, an export, a content pack, a Remote seat's snapshot. Nothing checked them, so a saga file whose id was `../../somewhere` named a file outside the sagas folder when it was saved, and a hostile character id did the same for the portrait's copy.

So every id coming in must be a **plain id**: lowercase letters, digits, `_` and `-`, starting with a letter or digit, at most 200 characters (`shapes.PLAIN_ID`). The shape check (ADR 0012) checks it before building, in every record: the record's own `id`, and each link to another of the saga's records, named in `shapes.RECORD_LINKS` (`covenant_id`, `character_id`, `owner_id`, `lab_id` and the like); an empty link passes. Other fields ending `_id` aren't checked: they hold catalog keys or keys the app puts together (a lab project's `design:<key>`, `decode:<magus>:<author>`), which never name a file. A saga file, a Remote seat's data and a saga brought in by the headless admin are refused with the field named ("characters[..].id: not a plain id"); nothing repairs them on load. An import gives each record it brings in an id of its own anyway, so it is checked without the id rule (`plain_ids=False`) and re-ids what isn't plain, its links following. An id it keeps as it came, inside a record (a possession's, a Virtue's catalog link), is checked once the import is planned, and refuses the import if it isn't plain.

An id the app makes from a name keeps at most 120 characters of it (`storage.SLUG_LENGTH`), so the ids it builds around one (`labtext_longevity_<id>_<hex>`) stay within 200. A saga's own id may also be one the headless admin's saga import took before this (capitals allowed): still only a name, its file already named for it.

Where an id becomes a path (a saga's file, a portrait's copy), a guard clause refuses a path outside its folder as well, for a record that never passed the check.

It is the validator-at-the-trust-boundary pattern again: one check, at the one place every saga file and network message already passes, rather than one at each caller.

## Considered options

- **`slugify(id) == id`:** what the app makes its own ids with, but the shipped packs have 65 ids with `-`, which `slugify` turns into `_`.
- **Allow capitals (the admin's old `[A-Za-z0-9_-]+`):** safe as a path, but no id the app makes has one, and a second rule beside the shape check's is one to drift. Kept only for a saga's own id, so a hosted saga brought in under the old rule still opens.
- **Check every field ending `_id`:** catches every link without a list to keep, but refused the keys the app puts together itself, so a saga with a spell being invented or a text being decoded would not have opened again (found in review).
- **Repair a bad id on load:** a saga's links would have to be rewritten on every open, and a file that names a path outside its folder was made to; refusing it, by field, says so.

## Consequences

- Every saga, backup and export in the maintainer's save folder and every shipped pack already passed the rule when it came in, so no real save is refused.
- `admin saga import` dropped its own safe-id rule; the shape check refuses first.
- A saga id that doesn't match its file's name is still allowed (left for later).

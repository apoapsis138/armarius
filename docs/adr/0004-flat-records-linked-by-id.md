# Records are flat lists linked by id; a book has one owner

A saga is one human-readable JSON file whose records sit in flat lists
linked by id (`covenant_id`, `owner_id`, `spell_id`), not nested inside each
other. A book has a single owner (a covenant, a laboratory, a character, or
none), and there is no separate Library record: a covenant's Library is the
list of its books and those of its laboratories and characters. Flat records
let a record move between owners by changing one id, and let a hosted
save merge record by record (see ADR 0005).

## Consequences

- Renaming or moving a saved field needs a load-time migration, and so does
  any change to this shape; exports and packs are small sagas of the same
  format, so they run the same migrations.

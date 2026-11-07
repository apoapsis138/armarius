# A hosted save merges three ways, record by record

When the storyguide hosts a saga, each player's copy of the app holds it in
memory, so saving the whole saga from one copy would wipe what another saved
since. Instead each save is a three-way merge (`merge.py`) of the file as
this copy last saw it, as this copy has it now, and as the file has it now:
dicts merge key by key and lists of records merge by id, so two people
changing different things both keep their changes. When both changed the
same value, the later save wins and the place is reported as a conflict,
rather than refusing the save or locking records.

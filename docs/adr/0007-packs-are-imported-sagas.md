# Tribunal books ship as packs imported like any export

Each Tribunal or region book is built in code once (`book_packs/<book>/`,
with the shared `Builder`), written to `data/packs/*.amm.json`, and imported
the same way as a saga export, so it runs the same migrations. Importing
matches records by name rather than adding new ones beside them, so a pack
can be imported again, after a fix, without doubling what the saga holds.
The app has no code per book beyond its builder and its Tribunal's customs.


# Effects are data: one modifier model

Every catalog entry that changes a number (character and laboratory Virtues
and Flaws, covenant Boons and Hooks, user-made entries) carries its effects
as `Modifier`s, checked at load against the registry in `totals.py`, and
`rules.effects.collect()` gathers them from every record involved. Flat
amounts add first, then multipliers multiply; rounding belongs to the rule
that owns the total. Nothing looks an entry up by name to decide what it
does, so a house-ruled or user-made entry works the same as a book's.

## Considered Options

- Per-purpose flags on an entry, with the rule in code.
- One-off maps from an entry's key to a number.
- Code hooks per entry.

All three were rejected because each keeps an entry's effect out of its
data. This is settled; DESIGN.md section 5 describes the model.

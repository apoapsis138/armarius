# Store what is typed, work out the rest

A saga file holds what the user enters, not what follows from it: an Art or
Ability holds its xp and the score is derived (`rules/xp.py`); totals come
from modifiers; a covenant's Economics and Loyalty are worked out from the
covenant. None of these derived figures is saved. A saved score could
disagree with the xp it came from; a derived one can't, and a corrected rule
fixes every old save on load.

## Consequences

- Changing a derived figure means changing what it is derived from (add xp,
  add a modifier), never typing over the result.
- Turning a derived figure into a stored one later needs a save migration,
  so this is costly to reverse.

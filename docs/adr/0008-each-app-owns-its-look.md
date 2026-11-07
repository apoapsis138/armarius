# Armarius and Sortilegus each own a copy of the look

The palettes, fonts, Textual themes and desktop ornaments were briefly a
shared package (`armarius-style`) used by both Armarius and the solo tool,
Sortilegus. That package was dissolved: the look lives in Armarius again
(`style/`, `tui/style.py`, `gui/style/`), and Sortilegus keeps its own copy.
Drift between the two is accepted, so that each app can change its look
without coordinating a shared release (Shared Kernel replaced by Separate
Ways).

## Consequences

- A change to the look here is not carried across to Sortilegus as a matter
  of course.

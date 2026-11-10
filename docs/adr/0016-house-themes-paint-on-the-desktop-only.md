# House themes paint on the desktop only

A theme was a table of colours (`style/palettes.py`) that both front-ends
read. House themes need more than colours: each House family has a form of
its own (frame, corners, rules, heading type) and each House its own mark
and texture. We keep a theme's colours as shared data in the core, and put
the painting in the desktop app's `gui/style/`: each House family is a
Template Method that lays down the steps of drawing a page, and each House
theme fills in its colours, mark and texture. The terminal app never sees
House themes and keeps Scriptorum and Scriptorum Dark.

## Considered Options

- Colours only, shared by both front-ends: cheap, but every House would
  look like Scriptorum recoloured, which loses the families' common forms.
- A theme as a class in the core that knows how to paint: the core would
  need a UI library, which ADR 0001 forbids.

## Consequences

- A House theme carries its own In Creation twin, made from its colours
  (cooled and ruled), as Scriptorum's drafting vellum is.
- Colours that carry meaning (realms, season kinds, loyalty, errors) and
  heraldic arms keep their hues in every theme, adjusted only for contrast.
- Text on a House's texture keeps at least 4.5:1 contrast; a texture that
  fails it is drawn fainter behind text and kept whole in the margins.
- As ADR 0008 has it, House themes are Armarius's own; Sortilegus does
  not get them.

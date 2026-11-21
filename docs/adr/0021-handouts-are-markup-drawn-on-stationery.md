---
status: accepted
---

# Handouts are markup drawn on Stationery, never files

A Handout is the app's own markup plus six handout tags, drawn on a named Stationery (vellum, a sealed letter, a proclamation). No PDF or HTML file comes in. Each front-end draws the Stationery in its own look (ADR 0008). A player who wants a copy on paper prints it, or saves a PDF, from their own desktop, through the same printing code as the app's other PDF exports.

The six tags each start a line: `[heading]`, `[centre]` (centred lines), `[right]` (right-aligned lines), `[initial]` (a paragraph opening on an illuminated initial), `[flourish]` and `[picture n]` (one of the Handout's own pictures, placed). One core parser (`handout_markup.py`) reads the text into blocks, and is the only way a Handout's text reaches a drawing; anything else in brackets comes out as text.

## Considered options

- **PDFs sent to the seats:** every player's machine would need a PDF parser fed by the host, which is the malicious-host actor (E) of the Remote seats threat model.
- **PDFs rasterised on the host:** safe to send, but the storyguide wants styled handouts drawn by the app, not imported PDFs.
- **HTML:** Qt's rich text can fetch outside resources, so a handout could reach the network from a player's machine.

## Consequences

- A handout looks the same on every desktop that draws it, and the terminal app shows its text.
- New Stationery and tags are added in code, drawn in code under the no-generative-art rule.
- A block never holds a file name or an address: a placed picture is a number among the Handout's own pictures, which arrive only through the picture request.

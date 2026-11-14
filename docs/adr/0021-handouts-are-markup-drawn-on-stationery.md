---
status: proposed
---

# Handouts are markup drawn on Stationery, never files

A Handout is the app's own markup plus a few handout tags (a heading, centred and right-aligned lines, an illuminated initial, a flourish, a placed picture), drawn on a named Stationery (vellum, a sealed letter, a proclamation). No PDF or HTML file comes in. Each front-end draws the Stationery in its own look (ADR 0008). A player who wants a copy on paper prints it, or saves a PDF, from their own desktop, through the same printing code as the app's other PDF exports.

## Considered options

- **PDFs sent to the seats:** every player's machine would need a PDF parser fed by the host, which is the malicious-host actor (E) of the Remote seats threat model.
- **PDFs rasterised on the host:** safe to send, but the storyguide wants styled handouts drawn by the app, not imported PDFs.
- **HTML:** Qt's rich text can fetch outside resources, so a handout could reach the network from a player's machine.

## Consequences

- A handout looks the same on every desktop that draws it, and the terminal app shows its text.
- New Stationery and tags are added in code, drawn in code under the no-generative-art rule.

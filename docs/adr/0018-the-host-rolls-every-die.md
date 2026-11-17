---
status: accepted
---

# The host rolls every die

When a hosted saga is played online, every die is rolled on the host. A seat sends only what to roll, never a die or a total: from a sheet, the character, the Characteristic, the Ability (one the character has no score in may be rolled at 0, with three extra botch dice, unless the book forbids it) and whether a Specialty applies, and the host works the modifier out from the sheet, wound and Fatigue penalties included; for a Free roll, stress or simple, the modifier the roller typed, the botch dice, an optional Ease Factor and what it is for. Each request also says who may see it, in terms of the Chronicle's Audience: a Public roll goes to the Table, a Private roll to the roller chosen alone (and so the Session's storyguide), and a Blind roll's number to the Session's storyguide alone, with a line for the roller saying only that it was rolled. The host rolls with `secrets.SystemRandom` through `rules/dice.py`, and one request makes exactly one result, written to the Session's Chronicle; asking again makes a second, recorded roll rather than replacing the first. This is the Command pattern: a roll request is carried out once, and the Chronicle is the list of the commands carried out.

A roll's entry keeps every die face, each doubling of a stress die and each botch die, with the modifier, the total, any Ease Factor and the margin, so it can be read back exactly as it fell. A player rolls only for the characters they play that evening (the Session's castings); the Session's storyguide rolls for any character or none. The host checks both. A roll that should not count is Struck by the storyguide with a reason: the Strike is a new entry pointing at the roll, which stays in the Chronicle. Confidence is spent after the roll, once its result is known, as the rules have it (Definitive Edition p. 29): a new entry pointing at the roll adds +3 a point, never on a botch or on a roll whose number the spender can't see, and the character's Confidence Points fall by what was spent at End Session.

The app's other rolling forms (a Personality Trait roll, Cast a Power, Ars Goetia and the like) are the one exception to "never a die". While a Session is Under way, a form whose roll is a Table roll is handed the host's dice through a recording die source wrapped around `secrets.SystemRandom` (the Decorator pattern), so every face it draws is kept. On the host's own desktop the form rolls there. At a Remote seat the form still works its rule on the seat, as every seat form does, but each die it asks for is drawn from the host one at a time (a Remote Proxy over that die source): the host records every face under the form's name and the roller, the seat sends back only the form's result line, and the host writes the entry with the faces it drew itself. A form cancelled after drawing leaves its dice in the Chronicle as drawn, then cancelled. The form chooses who sees the roll as a Free roll does. Its typed-die fields are hidden while the Session is Under way; outside a Session nothing changes, and rolls the season, the year or a project calls for never go to the Chronicle.

So a seat can't choose its dice or quietly roll again, but a modified seat could misstate a form's modifiers or result line. The posted faces let anyone check the total, and the Session's storyguide can Strike the roll. Rolls from a sheet, Roll requests and Free rolls stay wholly worked on the host.

## Considered options

- **Rolls made on the player's computer:** the seat is not trusted (actors A and F in the Remote seats threat model, `docs/threat-model-remote-seats.md`), so a modified client could send any number it liked.
- **Rolls made on the client and signed:** a signature proves which seat sent a number, not that the number was rolled fairly; it adds keys and checks for no gain.
- **Every rolling form worked on the host:** each form's roll a host command, as a roll from the sheet is. It would close the misstated result line too, but it needs a request and an answer for each of about forty forms, each kept in step with its form; the Remote Proxy gets the same dice for one seam.
- **Rolling forms unavailable at a seat while a Session is Under way:** simplest, but a saga whose host is headless has its storyguide at a seat, who could then use none of them.

## Consequences

- A player who wants to roll real dice may enter them only when the saga option for Entered dice is on, and each such die is marked as entered wherever the roll is shown.
- A roll needs the host to answer; with the host away there is no rolling at the table.
- Rolling follows ADR 0002's spirit: the request is data (what to roll), and the rules turn it into a result in one place.
- Rolls are limited per seat through `remote/limits.py`, apart from other requests, so a seat cannot flood the Chronicle.
- The host's computer holds every roll, Blind ones included (ADR 0020): the Audience decides what each seat is sent and what the host's own app shows, not what the host could read.

---
status: proposed
---

# The host rolls every die

When a hosted saga is played online, every die is rolled on the host. A seat sends only what to roll (the character, the trait, the choices such as a Specialty or Confidence, and the visibility: Public, Private or Blind), never a die or a total. The host rolls with `secrets.SystemRandom` through `rules/dice.py`, and one request makes exactly one result, written to the Session's Chronicle; asking again makes a second, recorded roll rather than replacing the first. A roll that should not count is Voided by the storyguide with a reason, and stays in the Chronicle.

## Considered options

- **Rolls made on the player's computer:** the seat is not trusted (actors A and F in the Remote seats threat model, `docs/threat-model-remote-seats.md`), so a modified client could send any number it liked.
- **Rolls made on the client and signed:** a signature proves which seat sent a number, not that the number was rolled fairly; it adds keys and checks for no gain.

## Consequences

- A player who wants to roll real dice may type them in only when the saga option for Typed dice is on, and each such die is marked as typed wherever the roll is shown.
- A roll needs the host to answer; with the host away there is no rolling at the table.
- Rolling follows ADR 0002's spirit: the request is data (what to roll), and the rules turn it into a result in one place.

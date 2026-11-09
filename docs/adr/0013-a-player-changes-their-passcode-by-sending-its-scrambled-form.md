---
status: accepted
---

# A player changes their passcode by sending its scrambled form

A Remote seat's passcode never crosses the internet: the player's app proves it knows it, bound to the host's pin (ADR 0009). Letting a player change their own passcode from their seat means something about the new one must reach the host. The player's app proves the old passcode as at sign-in, then works out the new one's scrambled form (scrypt, as the saga keeps it) under a fresh salt and sends only that, with the salt. The host stores it as the player's passcode and notes the salt as allowed for Remote seats. The passcode itself still never leaves the player's computer.

The 14-character rule is checked by the player's app, not the host, which never sees the passcode. A modified app could set a shorter one, but only for its own player. The host can't tell, and it isn't a way into anyone else's seat.

A player who has forgotten their passcode asks from the Rejoin window. The request is proven by the device's seat and shows in the storyguide's Requests. The storyguide confirms it's really them by voice, then sets a new passcode and tells them. The reset is out-of-band by design, with no email links or secret questions.

## Considered options

- **Send the new passcode inside the encrypted channel:** simpler, and the host could check its length. But it breaks the promise that a passcode never crosses the internet, made in Help and the threat model.
- **Only the storyguide sets passcodes:** the state before this. Safe, but a player can't change a passcode they've shared or let slip without asking.

---
status: accepted
---

# A seat is told which entries are for it

The host, which keeps each Chronicle entry's whole Audience, tells each Remote seat, entry by entry, whether that entry is for the seat's Player: the `chronicle` event frame of ADR 0019 gains a `for_you` flag, true or false. A seat's collapsed Chronicle pane pulses on that flag alone. Before, a seat was sent only the Audience's kind (Table, Storyguide or Chosen) and guessed: it took any "the storyguide rolled for you" line it was sent as its own, and read a Whisper's recipients' Player ids from its body.

Who an entry is for is part of its kind: each kind's one description in the Chronicle's kind registry (`chronicle.KINDS`) holds a "for whom" rule. A Blind roll's number is for the Session's storyguide; the line that the storyguide rolled is for the player it is for; a Whisper is for each person it is to; a Roll request is for whoever rolls each character offered it, but the storyguide who made it; every other kind is for no one. The host's own pane asks the rule directly (`chronicle.for_whom`), and the host works out each seat's flag through it in one place (`chronicle.stamped`, called by `chronicle.feed`), which every path that hands a seat an entry goes through: live sending and catching up after a drop alike. The flag is kept on the entry a seat holds (`Entry.for_you`), never in the Chronicle file.

This is still ADR 0019's Observer: the host tells each subscribed seat of each new entry, now with one fact worked out for that subscriber. The rule on each kind is a Strategy; the seat's side stays the Adapter that `chronicle.Reader` is, one view over the host's Chronicle and a seat's feed, now with nothing left to guess.

## Considered options

- **Send the Players chosen and let each seat work it out:** one rule, run at both ends, but every seat would learn who else each entry is for, which its card doesn't show.
- **Keep the guess at the seat:** nothing travels, but it breaks the day an entry reaches a seat for more than one reason, and each new kind would need a guess of its own.

## Consequences

- One change a player sees: a Roll request offered to their character pulses their pane.
- The protocol stays at 4: protocols 2 to 4 have never shipped, so this folds into 4 rather than raising it. A seat on the released version (protocol 1) is told to update as before.
- A new kind of entry (a Show, a Handout) must declare its own "for whom" rule (`Kind` has no default for it); a test walks every kind in the registry and checks that the host's reader and a seat's reader pulse for the same people.
- A Whisper sent to seats keeps its recipients' names, which its card shows, and leaves their Player ids (`to`) at the host. Every kind names the keys of its body the host holds back (`Kind.held_back`, required, `()` for none), and `chronicle.stamped` drops them, so the Chronicle file keeps everything and a seat never gets them.
- Player ids still travel where a seat needs them or its card already shows them: every frame's `author` (the writer, whose name the card shows) and each character's `roller` in a Roll request (a seat reads it to know whether it answers). Every seat's saga already lists each Player by id and name. Player ids are identifiers, not secrets: nothing may treat knowing one as proof of who someone is or as leave to do something (the threat model says so).
- The Remote seats threat model's row for host-to-seat events at boundary B2 says what the flag tells a seat.

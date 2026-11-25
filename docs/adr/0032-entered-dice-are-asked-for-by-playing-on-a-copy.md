---
status: accepted
---

# Entered dice are asked for by playing on a copy

When a person rolls a fight's dice at the table and enters them, the app can't know in advance how many dice a blow needs: a stress die's 1 is rolled again and doubled, a first 0 calls for botch dice (DE p. 7), and which rolls happen at all depends on earlier ones. So a blow is played with a source of chance that gives out the faces entered so far (`entered_dice.EnteringDice`) and stops with `NeedDie` at the first die it lacks, saying which die and why. The form asks for that one face and plays again from the start with one more.

Each try is played on a copy of the saga (`copy.deepcopy`), never the saga itself. Once a try needs no more dice, the blow is played once on the real saga with the same faces, and only then does anything change: wounds, Fatigue, the order, the chronicle. Stopping part way, by cancelling a die prompt, leaves the saga exactly as it was.

## Considered options

- **Reorder every rule so its dice come before its changes, and replay on the saga itself:** the spec's first plan. It needs an audit of every rolling module and a rewrite of the fight rules, which tire a charger, wound, split groups and move the order between one roll and the next. A slip leaves a half-made change on a stopped roll.
- **Ask for every face up front:** impossible, since the number of dice depends on the faces.

## Consequences

- The rules stay as they are; they take any source of chance (Strategy), and the recording source (Decorator) wraps the entering one as it wraps any other.
- A try costs a copy of the saga: about 1 ms for a small saga and 43 ms for the largest saved so far, once per die entered.
- Dice-made helpers (`rules.dice`) tell the source each throw's part ("stress die", "a 1: roll again and double", "a 0: botch die 1 of 2"), and a rule may tell it whose roll comes next (`dice.rolling`), so the prompt can say what to throw.
- Only d10s are asked for. A draw that is no die anyone throws, such as a tie broken by chance, is settled the same way every time.
- The same approach can serve the other rolling forms (the rest of "Who rolls the dice") without auditing them first.

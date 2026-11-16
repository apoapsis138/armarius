# Familiar sheet
<!-- help: familiar -->

The familiar sheet holds a magus's familiar, a magical creature bound to
them (DE Chapter 8: Laboratory, Familiars).
<!-- tui -->
A magus has one familiar at a time, bound with Bind Familiar in New (`n`).
<!-- /tui -->
<!-- gui -->
A magus has one familiar at a time. Bind it with the **Bind Familiar** card
on the magus's sheet, or the **Bind Familiar** button beside Planning in
their laboratory's Seasons chapter.
<!-- /gui -->
Binding gives both the magus and the familiar the True Friend Virtue and a
Loyal (Partner) +3 Personality Trait. A familiar made **Bound already** gets
them at once, any other when the binding season is played (DE p. 267).

<!-- tui -->
To remove a familiar, press `d` on its tree node or its Familiar Info panel.
<!-- /tui -->
<!-- gui -->
To remove a familiar, use **Delete** in its page's **Manage** chapter.
<!-- /gui -->
After you confirm, it's deleted and the bond is broken. The magus loses the
True Friend Virtue and Loyal (Partner) Trait the bond gave them, and any
planned seasons of binding or empowering it. The magus's sheet is shown
afterwards.

<!-- tui -->
The Familiar Info panel stays above the tabs whichever tab is open, and the
tabs open with `1` to `5`. On a tab with a list, the details panel at the
bottom shows the chosen row, including the rules text of a Virtue or Flaw.
<!-- /tui -->
<!-- gui -->
The header and the Characteristic cards under it stay on the page whichever
chapter is open. The header shows the familiar's name, its magus, its Size,
Wound Multiplier, Base Soak, Magic Resistance and Magic Might. The rail on
the left lists the chapters:

- Identity & Cords
- Virtues & Flaws
- Combat & Health
- Abilities
- Bond Powers
- Manage, last

Clicking a row or card shows it in the inspector on the right, including
the rules text of a Virtue or Flaw.
<!-- /gui -->
Most of a familiar's figures are typed in as the rules give them, rather
than worked out by the app.

**See also:** [How to bind and keep a familiar](help:guide-familiars)

### Familiar Info
<!-- help: section-fam-info -->

<!-- tui -->
The familiar's Magus Partner, set when it was bound, and what you type with
`e`:
<!-- /tui -->
<!-- gui -->
The familiar's Magus Partner, set when it was bound, and what you type with
the header's **Edit** button:
<!-- /gui -->

- its name and Species / Description
- the season and year it was bound
- its Magic Might Score and current Might Pool
- its Size and Wound Multiplier

<!-- gui -->
The seal in the header shows the Magic Might. Its Characteristics, Base
Soak and Magic Resistance have their own button (see
[Characteristics](help:tab-fam-characteristics)).
<!-- /gui -->

## Identity & Cords
<!-- help: tab-fam-identity -->

<!-- tui -->
The bond between familiar and magus, and who the familiar is: its Virtues
and Flaws, Personality Traits and Reputations.

**You type:** all of it but the Virtues and Flaws, picked from the catalog.

**The app works out:** each Cord's point cost, and the Virtues' and Flaws'
points.
<!-- /tui -->
<!-- gui -->
The bond between familiar and magus, its three Cords, each a card in its
metal, and the familiar's Personality Traits and Reputations.

**You type:** all of these. **The app works out:** each Cord's point cost.
<!-- /gui -->

**See also:** [Abilities](help:tab-fam-abilities),
[Bond Powers](help:tab-fam-powers),
[Character sheet](help:character), [How to bind and keep a familiar](help:guide-familiars)

### Binding & Cords
<!-- help: section-fam-binding -->

The binding's Arts, its initial Lab Total, the target binding level and the
vis spent on it, then the Golden, Silver and Bronze Cords with what each one
<!-- tui -->
does. You type all of these with `e`.
<!-- /tui -->
<!-- gui -->
does. You type all of these with the **Edit** button beside The Bond.
<!-- /gui -->
The app works out each Cord's point cost from its score (DE Chapter 8:
Laboratory, Familiars).

- **Bronze Cord**: a bonus to recovery rolls and against aging, so it comes off the aging roll (DE p. 267).
- **Golden Cord**: takes dice off the botch dice of the magus's casting, a
  hedge power's too, never to none.
- **Silver Cord**: added by [Roll](help:trait-roll) beside Personality
  Traits, on the familiar's sheet and its magus's.

## Roll
<!-- help: trait-roll -->

**Roll** (More beside Personality Traits, on a character or a familiar)
rolls one of three things, each adding the bond's Silver Cord (DE p. 267).

- **A Personality Trait roll**: the trait chosen + the Silver Cord + a
  stress die against the Ease Factor you type.
- **Resisting mental influence**, such as a spell, intimidation or verbal
  trickery. Type the roll's own total as its rules give it. The Silver
  Cord and a stress die are added, against the Ease Factor.
- **The familiar frees a mind overcome**: a stress die + the Silver Cord
  against 9, one try a day. A botch overcomes the familiar's mind too.
  It's offered only where there's a Silver Cord.

Leave the die blank to roll it. The result is shown, not kept.

### Virtues
<!-- help: section-fam-vf-virtues; tui -->

The familiar's Virtues, each with its tier, and their points in the title.
`a` and `e` work as on a character's [Virtues](help:section-vf-virtues).

### Flaws
<!-- help: section-fam-vf-flaws; tui -->

The familiar's Flaws, each with its tier, and their points in the title.
`a` and `e` work as on a character's [Flaws](help:section-vf-flaws).

### Personality Traits
<!-- help: section-fam-personality-traits -->

The familiar's Personality Traits, each a name and a score that you type.
The Loyal (Partner) trait comes from the bond.

### Reputations
<!-- help: section-fam-reputations -->

The familiar's Reputations, typed as a character's
[Reputations](help:section-reputations) are.

## Virtues & Flaws
<!-- help: tab-fam-vf; gui -->

The familiar's Virtues and Flaws, side by side, each a card. Clicking one
shows its effects and rules text in the inspector.

**You type:** nothing; each is picked from the catalog. **The app works
out:** each side's points, in the section titles.

**See also:** [Identity & Cords](help:tab-fam-identity),
[How to bind and keep a familiar](help:guide-familiars)

### Virtues
<!-- help: section-fam-vf-virtues; gui -->

The familiar's Virtues, each with its tier, and their points in the title.
**Add** and **Edit** work as on a character's
[Virtues](help:section-vf-virtues).

### Flaws
<!-- help: section-fam-vf-flaws; gui -->

The familiar's Flaws, each with its tier, and their points in the title.
**Add** and **Edit** work as on a character's [Flaws](help:section-vf-flaws).

## Characteristics
<!-- help: tab-fam-characteristics; tui -->

The familiar's Characteristics and its defences.

**You type:** the eight Characteristics, the Base Soak and the Magic
Resistance.

**The app works out:** nothing here.

**See also:** [Combat & Health tab](help:tab-fam-combat)

### The scores
<!-- help: section-fam-characteristics -->

The eight Characteristics, with Base Soak and Magic Resistance below them.
`e` edits all ten figures in one form.

## Characteristics
<!-- help: tab-fam-characteristics; gui -->

The familiar's eight Characteristics, as cards under the header, and its
defences, Base Soak and Magic Resistance, in the header. The header's
**Characteristics** button types in all ten figures in one form.

Base Soak and Magic Resistance are typed as the creature's statistics give
them. **The app works out:** nothing here.

**See also:** [Combat & Health](help:tab-fam-combat)

## Combat & Health
<!-- help: tab-fam-combat -->

How hurt and tired the familiar is, and how it fights.

**You type:** its wounds, its Fatigue Level and its natural weapons.

**The app works out:** nothing. Unlike a character's Health, a familiar's
Soak and penalties aren't calculated. The penalty of each wound level is
shown beside it as a reminder.

<!-- tui -->
**See also:** [Characteristics tab](help:tab-fam-characteristics),
[Health](help:section-char-health)
<!-- /tui -->
<!-- gui -->
**See also:** [Characteristics](help:tab-fam-characteristics),
[Health](help:section-char-health)
<!-- /gui -->

### Health
<!-- help: section-fam-health -->

<!-- tui -->
The familiar's Light, Medium and Heavy Wounds, whether it's Incapacitated
or Dead, and its Fatigue Level. `e` edits the wounds. The Edit Fatigue
button, or Edit Fatigue in More (`m`), sets the Fatigue Level.

Unlike a character, the familiar has no Soak adjustment here. Its Base Soak
is on the [Characteristics tab](help:tab-fam-characteristics).
<!-- /tui -->
<!-- gui -->
The familiar's Light, Medium and Heavy Wounds, whether it's Incapacitated
or Dead on the Damage Table for its Size, and its Fatigue Level. The
**Wounds** button beside the section edits the wounds, and the **Fatigue**
button sets the Fatigue Level.

Unlike a character, the familiar has no Soak adjustment here. Its Base Soak
is typed in with the header's **Characteristics** button (see
[Characteristics](help:tab-fam-characteristics)).
<!-- /gui -->

### Natural Weapons & Attacks
<!-- help: section-fam-natural-weapons -->

The familiar's attacks, such as a beak or claws, each a weapon with its
Initiative, Attack, Defence and Damage modifiers.
<!-- tui -->
Type them in with `a` or `e`. The details panel shows the chosen attack.
<!-- /tui -->
<!-- gui -->
Type them in with **Add** or **Edit**. Clicking an attack shows it in the
inspector.
<!-- /gui -->

## Abilities
<!-- help: tab-fam-abilities -->

The familiar's Abilities, in one list grouped by category.

<!-- tui -->
**You type:** each Ability's total XP and its Specialty. `a` picks a new
Ability from the catalog.
<!-- /tui -->
<!-- gui -->
**You type:** each Ability's total XP and its Specialty. **Add** picks a
new Ability from the catalog.
<!-- /gui -->

**The app works out:** the score and the XP the next score needs, as for a
character's [Abilities](help:tab-abilities). The familiar shares its
magus's Language scores, so there's no need to add them.

## Bond Powers
<!-- help: tab-fam-powers -->

<!-- tui -->
The powers the magus has given the bond, in one list with a details panel.
<!-- /tui -->
<!-- gui -->
The powers the magus has given the bond, each a card with its Form's
symbol, level, uses a day and Penetration. Clicking one shows it in the
inspector.
<!-- /gui -->

**You type:** each power's name, level, Technique and Form, target and
controller, uses per day, Penetration, vis spent and any cosmetic trait.

**The app works out:** the modified level, when **Work out the modified
level** is ticked. Level is then the effect level, and the app adds:

- its uses per day, priced at the Effect Frequency row at or above the
  count (0 is unlimited, +10)
- a level per 2 points of Penetration
- the modifications ticked, as for an invested device's effect (DE pp.
  256-258, 267-268)

Empowering the bond then needs a Lab Total above that level, gains points
against it, and spends a pawn per 10 levels of it. Unticked, nothing is
worked out. Level is taken as the modified level already, as in older
saves.

**See also:** [Binding & Cords](help:section-fam-binding), [How to bind and keep a familiar](help:guide-familiars)

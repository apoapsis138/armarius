# The Region
<!-- help: region; tui -->

The Region node, under the troupe's covenants in the navigation tree,
holds the saga's world beyond them. Each Tribunal is listed here, with
the covenants the troupe doesn't play under the Tribunal they belong to;
a covenant with no Tribunal sits directly under The Region.

Press `n` (New) here, or on the saga, and choose **New Tribunal** to add
one. A covenant joins a Tribunal through the Tribunal choice in Edit
Covenant.

**See also:** [Tribunal sheet](help:tribunal), [Covenant sheet](help:covenant)

# Tribunal sheet
<!-- help: tribunal -->

A Tribunal is the council of the magi of a region, meeting every seven
years (Ars Magica Definitive Edition, Chapter 2: The Order of Hermes).
Its sheet holds what belongs to the Tribunal itself: its name, how often
and where it next meets, its Praeco and Presiding Quaesitor, and how big
it really is. Everything else is worked out from the covenants that
belong to it.

A Tribunal follows either the core rules or one region's customs, from
that region's sourcebook, never a mix: choose them as **Customs** in Edit
Tribunal (a region's customs are offered while its book is in play).
The customs can add lists of their own to the sheet, a column to the
roster, and change when notice of a case is due. Switching customs keeps
what the old ones recorded, hidden, and switching back shows it again.

- **Core rules**: the Definitive Edition's Tribunal; notice of a case is
  due a season before the meeting.
- **Rhine: Gilds** (Guardians of the Forests): the Rhine's covenants band
  together in gilds, each with its dues; the sheet gains a Gilds list and
  the roster a Gild column. Notice is wanted a year before the meeting.

Older sagas typed a covenant's Tribunal as a name. Each name became a
Tribunal of its own when the saga was first opened by this version, and
covenants that typed the same name share it.

<!-- tui -->
Add a Tribunal with **New Tribunal** in New (`n`). To delete one, press
`d` on its tree node or its top panel: its covenants belong to no
Tribunal afterwards, and nothing else about them changes.
<!-- /tui -->
<!-- gui -->
Add a Tribunal with the **New Tribunal** card under Tribunals in the
saga's World chapter. To delete one, use **Delete** in its page's
**Manage** chapter: its covenants belong to no Tribunal afterwards, and
nothing else about them changes.
<!-- /gui -->

**See also:** [Covenant sheet](help:covenant), [Sketch covenants](help:tab-cov-overview)

## The Tribunal
<!-- help: section-trib-info -->

The facts under the Tribunal's name:

- **Customs**: the core rules, or the region's customs it follows.
- **Meets every**: how many years between its meetings (seven, unless
  its customs say otherwise).
- **Next meeting** and **Meeting place**: when and where it next meets.
- **Praeco** and **Presiding Quaesitor**: chosen from the saga's
  characters, at any detail.
- **Covenants** and **Magi**: how many are recorded here, and of how many
  in all when you have said (most are never written down).
- **Your votes**: the troupe's covenants' votes, proxies included, of
  every vote in the hall.
- **Cases**: how many are on the docket, and how many are against the
  troupe's covenants or their magi.

<!-- tui -->
Press `e` (or Edit) to change them, and to write what the Tribunal is
like in the saga.
<!-- /tui -->
<!-- gui -->
**Edit Tribunal** changes them, and what the Tribunal is like in the saga.
<!-- /gui -->

## Roster tab
<!-- help: tab-trib-roster -->

Every covenant that belongs to the Tribunal, the troupe's first, and the
magi worth keeping an eye on.

### Covenants
<!-- help: section-trib-roster -->

Each covenant of the Tribunal: how much of it is written down, its magi
(named or not), its votes at the next meeting and the proxies it holds,
and its attitude toward the troupe's covenant. When the Tribunal's size
says there are more covenants than are recorded, a last row counts them
and the magi they hold.

A covenant has one vote for each of its magi, and one for each proxy it
carries: the sigil of an absent magus, given for one meeting. Proxies
change at every meeting, so they are kept here rather than on the
covenant.

<!-- tui -->
Press `e` on a covenant to set the proxies it holds. Choose a covenant's
Tribunal in its Edit Covenant to add it here.
<!-- /tui -->
<!-- gui -->
Choose a covenant to read about it beside the list, and **Edit** to set
the proxies it holds. Choose a covenant's Tribunal in its Edit Covenant
to add it here.
<!-- /gui -->

### Magi of Note
<!-- help: section-trib-magi -->

The Tribunal's Praeco and Presiding Quaesitor, the magi of its covenants
the troupe doesn't play, and anyone prosecuting or defending a case on
its docket, with their House, covenant and part in the Tribunal. Edit a
magus on their covenant's sheet or their own.

## Docket tab
<!-- help: tab-trib-docket -->

The cases the Tribunal will hear at its next meeting, and those heard or
withdrawn before.

### Cases
<!-- help: section-trib-cases -->

Each charge, motion or appeal for the next meeting: when it was filed,
when notice of it is due, and what is sought. Under the core rules,
notice is due a season before the meeting; a case whose notice hasn't
been given is flagged, and a case against one of the troupe's covenants
or magi is drawn in red.

<!-- tui -->
`a` adds a case, `e` edits the chosen one and `d` deletes it. More (`m`)
offers **Withdraw**, which takes it off the docket and keeps it among
the past rulings. Choose a case to read all of it under the lists.
<!-- /tui -->
<!-- gui -->
**Add**, **Edit** and **Delete** change the cases; **Withdraw** takes
the chosen one off the docket and keeps it among the past rulings.
Choose a case to read all of it beside the list.
<!-- /gui -->

### Rulings of Past Tribunals
<!-- help: section-trib-past -->

The cases past meetings decided, with their outcome, and those
withdrawn. Edit one to correct it, or set its Status back to open to
return it to the docket.

## Peripheral Code tab
<!-- help: tab-trib-code -->

The rulings of this Tribunal's own Peripheral Code: what each says, the
year it was made, and the case it came from.

### Peripheral Code
<!-- help: section-trib-code -->

Add a ruling, edit it or delete it. A ruling can name one of the
Tribunal's cases as where it came from.

## Treasury tab
<!-- help: tab-trib-treasury -->

What the Tribunal holds in common, and what is owed to it.

### Treasury
<!-- help: section-trib-treasury -->

Each entry is vis, silver, a loan or a fine; Add asks which first. Vis
and silver are taken in (a positive amount) or paid out (a negative
one). A loan is silver or vis lent out of the treasury: it leaves the
treasury until it is marked repaid. A fine, from a case, comes in once it
is marked paid.

The balance above the list adds them up: the silver and vis in hand,
the loans still out and the fines still unpaid.

## Gilds tab
<!-- help: tab-trib-gilds -->

A Rhine Tribunal's gilds: the bands its covenants join, each with its
dues. Only a Tribunal following the Rhine's customs has this tab.

### Gilds
<!-- help: section-trib-gilds -->

Each gild with its member covenants and its dues. Add a gild, edit it
(its name, its dues, and a tick for each covenant of the Tribunal that
belongs to it) or delete it. The roster's Gild column shows the gilds
each covenant belongs to.

## Diary tab
<!-- help: tab-trib-diary -->

The Tribunal's own record of what happened: the minutes of each meeting
and anything else worth writing down.

### Diary
<!-- help: section-trib-diary -->

Entries newest first, each with its year and season. Add one, edit it
or delete it.

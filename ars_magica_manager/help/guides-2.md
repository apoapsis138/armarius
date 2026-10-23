# How the app handles advancement
<!-- help: guide-advancement -->

This guide follows a character's experience from the season it is planned to the moment it lands on their sheet, and what the end of each year does to them. Use it when you want to know where a score comes from, what the app adds by itself when a season is advanced, and when to change a figure by hand.

### Scores come from experience
<!-- help: guide-advancement-scores -->

For each Ability and Art the app keeps only the experience points (xp). The score is always worked out from the xp with the Advancement Table (Ars Magica Definitive Edition, Chapter 3: Characters). The xp is a running total: it never starts again at 0 when a score is reached.

- An Ability needs 5 xp for score 1, 15 for 2, 30 for 3, 50 for 4 and 75 for 5.
- An Art needs 1 xp for score 1, 3 for 2, 6 for 3, 10 for 4 and 15 for 5.

<!-- tui -->
1. Open the character from their covenant's Characters group in the tree and press `2` for the [Abilities tab](help:tab-abilities). Each Ability shows its Score, and its XP as the total so far over the total the next score needs, for example "50/75".
2. For a magus, press `4` for the Hermetic Magic tab. [Magical Arts](help:section-arts) shows each Technique and Form with its Score and XP.
<!-- /tui -->
<!-- gui -->
1. Open the character's sheet (click their card in the covenant's **People** chapter) and choose [Abilities](help:tab-abilities) in the rail. Each Ability shows its Score, and its Experience as the total so far over the total the next score needs, for example "50 / 75 xp".
2. For a magus, choose **Hermetic Magic** in the rail. [Magical Arts](help:section-arts) shows each Technique and Form with its Score and Experience.
<!-- /gui -->

A spell's Mastery is the exception: its score and xp are both typed, and xp gained in a season only ever raises the score.

### Virtues and Flaws the app applies
<!-- help: guide-advancement-virtues -->

These Virtues and Flaws from the catalog are taken into account wherever the app works out a season's xp:

- **Affinity with** an Ability or Art multiplies the xp gained in it by 1.5, rounded up.
- **Puissant** doesn't change the xp. It adds a fixed bonus to the score used (+2 for an Ability, +3 for an Art), shown in brackets after the score.
- **Book Learner**, **Apt Student**, **Independent Study** and **Free Study** add to the Advancement Total of the activity they name; **Poor Student** and **Unimaginative Learner** take from it. Being taught or reading never falls below 1.
- **Good Teacher** raises the Source Quality of the students the character teaches.
- **Linguist** raises the Advancement Total of any Language by a quarter, rounded up. **Savantism** halves every Advancement Total (rounded down) except the favoured Ability's. **Flawless Magic** doubles a spell Mastery's Advancement Total and **Loose Magic** halves it. These multiply the total after its bonuses and before Affinity, and the line above Save names them, for example "Advancement Total 5 (Linguist x1.25)".
- **Secondary Insight**: a season studying a Technique from a book, a teacher or raw vis also gives 1 xp in each of 4 Forms, and a Form gives 1 xp in each of 2 Techniques. Tick them in the plan's **Secondary Insight** grid, which offers only the other kind of Art; with fewer ticked, the lowest-scored make up the rest. No Affinity multiplies these points.
- **Elemental Magic**: a book, teacher or vis for Aquam, Auram, Ignem or Terram also gives half the season's Advancement Total (rounded up) in each of the other three. **Magian Lineage** (Major) does the same for its three connected Abilities, named when the Virtue is taken; a Supernatural one the character can't use yet loses its share. **Hermetic Sorcery** gives half the xp of a season studying a Goetic Art in Rego, and of a supernatural Lore in Vim.
- **Study Bonus** adds 2 to a text's Quality or the vis die when an Art is studied beside its substance (tick **The Art is present** on the plan); **Study Requirement** refuses an Art from books or vis without it.
- **Ability Block** refuses experience in the Abilities it names, or in their category ("Martial"). **Restricted Learning** refuses experience in any Ability but its five (named when the Flaw is taken, else those the character's creation xp went on) and a Virtue's Supernatural Abilities, except from Be taught or Be trained.
- **Master of None**: once an Advancement Total has given xp to an Ability or Art in a year, another that year gives it none; the line above Save says the xp is lost. A plan for an earlier season of the year counts as soon as it is planned. Experience shared by the Virtues above isn't affected.
- **Wealthy** and **License of Absence** each free one of a companion's two working seasons; **Poor** adds one. The covenant's Seasons chapter and the plan's reminder count them.
- **Labor Points** (City & Guild): **Perfect Eye for Commodity** gains 3 x the Wealth Multiplier each Winter and **Bigamist** costs 6 x it (3 x it posing as of lower status: type "lower" when the Flaw is taken). **Necessary Realm Aura** for a Craft or Profession takes 3 off its Labor Points and Workshop Total outside an aura of its realm (Dominion is the Divine). **Independent Craftsman** is a note on a workshop season: take 3 off the Other modifier when working with assistants.
- **Artes Liberales by subject**: **Academic Concentration** adds 3 for its subject and takes 1 for the other six; **Aristotelian Training** adds 1 for grammar, logic and rhetoric. A Laboratory Horoscope counts as astronomy, and a Tribunal debate's Artes Liberales attack as logic and rhetoric.

Other Virtues and Flaws change figures the app shows everywhere, not only in seasons:

- **Scores**: Student of (Realm) adds 2 to that realm's Lore, Dhampir 1 to Faerie Lore, Keen Sense of Smell 2 to Hunt, and a Dwarf, Brownie or Goblin Faerie Blood 1 to every Craft, every Profession or Stealth (with Faerie Legacy, 2 to Stealth, or 2 to the favoured Craft or Profession named when Faerie Legacy is taken). A Sidhe, Nymph, Padfoot, Ettin or Bloodcap Faerie Blood adds a free point of Presence, Communication, Perception, Stamina or Strength at creation, never past +3 (+4 with Faerie Legacy).
- **Soak and penalties**: Improved Soak, Tough Hide, Thick Fur, Spiny and Shell add to Soak, Reduced Soak takes from it. Enduring Constitution makes the Wound and fatigue penalties 1 better (never above 0), Low Tolerance 1 worse.
- **Aging**: see [The end of the year](help:guide-advancement-year-end).
- **Magic**: Flawed Parma Magica halves Parma's part of Magic Resistance against its Form, Limited Magic Resistance drops the Form's part, and Weak Magic halves Penetration. Mute, No Hands, Limited Speech and Limited Gestures set the words or gestures term of every Casting Score; Quiet Magic, Subtle Magic and Deft Form take that much off a penalty. Enfeebled doubles the Fatigue a spell costs, Withstand Casting takes a level off (never below 1) and Vulnerable Casting adds one, and Mythic Blood takes 1 off a Formulaic spell's and 3 off a Ritual's.

A Virtue or Flaw made under House Rules is text only, so adjust its effect by hand.

### Planning the season
<!-- help: guide-advancement-planning -->

<!-- tui -->
1. On the character's sheet, open the Planning tab (`6` for a magus, `5` for anyone else) and press `e` in the [This Season](help:section-char-season) section. This opens [Plan Season](help:plan-season) for the current season. A covenant's [Seasons tab](help:tab-cov-seasons) opens the same form for anyone in its Magi or Companions list.
<!-- /tui -->
<!-- gui -->
1. On the character's sheet, choose **Planning** in the rail and click **Plan** (or **Edit**) in the [This Season](help:section-char-season) section. This opens [Plan Season](help:plan-season) for the current season. A covenant's [Seasons](help:tab-cov-seasons) chapter opens the same form for anyone in its Magi or Companions list.
<!-- /gui -->
2. Choose the **Activity**, then fill in what it asks: **Experience in**, a **Book**, a **Teacher / master**, a **Source Quality**, **Vis from**, a **Stress die (blank: rolled)** or **Months lost (0-3)**.
3. Watch the line above Save. It shows each subject's Advancement Total, the xp gained and how the score and xp will change, for example "Latin: Advancement Total 4, +4 xp (score 3, 34 -> 38 xp)". A plan that breaks a rule shows why, and Save refuses it.
4. Choose **Save**. The This Season section now shows the plan and what it will give.

What each activity gives (Ars Magica Definitive Edition, Chapter 10: Long-Term Events):

- **Work / Exposure**: 2 xp in one subject, or 1 in each of two.
- **Practice**: Source Quality 4 (5 for a spell's Mastery) in one Ability. Arts can't be practised.
- **Read a book**: a summa's Quality, never past its Level; a tractatus's Quality, once per reader. The Quality is the one the book is read at: a palimpsest's -3, a commentary's +1, a florilegium's bonus, an exemplar's -3 and (with Extended book Quality) its craftsmanship all count, as its details panel shows. Only one reader a season for a book, or for any book bound in the same codex. A book whose Level or Quality is still to be set can't be read until it has them. A commentary is read only after a season on its summa: the plan notes it when none is on record. Reading a folio's book also gives 1 xp in Order of Hermes Lore. **Gloss it** glosses the book while reading it (+1 Quality, once): the reader needs a score of at least half its Level and better Communication than its author.
- **Correspondence on** (any season, with Covenants in play): useful correspondence on a theme of the character's research or reading, with at least one letter received that season, adds 1 xp in its subject. One correspondence counts a season.
- **Be taught**: the teacher's Communication + Teaching + 3, plus 6 for one student or 3 for two, never past the teacher's score. The teacher must Teach the same season: saving Be taught plans it for them.
- **Be trained**: the master's score + 3, never past it; Abilities only.
- **Study from vis** (magi): a stress die plus the aura's modifier, using one pawn of the Art's vis for every 5 points of its score (at least one).
- **Adventure**: the storyguide's Source Quality of 5 to 10, split among up to three subjects, at most 5 to each.
- **Lab work** and **Assist in a laboratory** give 2 xp of Exposure in Magic Theory; writing and copying books, and Teach, give Exposure too.
- **Undergo an Initiation** gives no xp: it is the season a Mystery Virtue is initiated. See [How to initiate a character into a Mystery](help:guide-initiation).

The Advancement Total is the Source Quality plus or minus the Virtues and Flaws above. Each full month lost cuts it by a third, then Affinity multiplies it. A character with a Wound Penalty of -3 to -5 gains half the xp, and one at -6 or worse can do nothing productive.

<!-- tui -->
Grogs aren't planned season by season. On a grog's Planning tab, `e` sets up their [yearly update](help:grog-year), applied in Winter.
<!-- /tui -->
<!-- gui -->
Grogs aren't planned season by season. In a grog's Planning chapter, **Yearly Update** sets up their [yearly update](help:grog-year), applied in Winter.
<!-- /gui -->

### Seasons ahead
<!-- help: guide-advancement-ahead -->

A plan for a season ahead is worked out from the character as the seasons planned before it will leave them. The app copies the saga, plays each planned season on the copy as Advance Season would (every plan's outcome first, then each applied), and reads the later season from the copy; the copy is then thrown away, so nothing in the saga changes. So a magus who reads an Ignem summa in Spring and invents an Ignem spell in Summer sees the Summer's Lab Total with the higher Ignem, and a second season on the same summa starts from the xp the first leaves.

- **Where it shows**: the details under [Seasons Ahead](help:section-char-ahead), the line above Save in [Plan Season](help:plan-season) for a season ahead, the laboratory's [Planning tab](help:tab-lab-planning) and its lab work form, and the character's calendar, where each planned season says what it is expected to give.
<!-- tui -->
- **The calendar** is the [Calendar](help:section-char-calendar) section at the bottom of the character's Planning tab.
<!-- /tui -->
<!-- gui -->
- **The calendar** is Seasons, at the top of the character's [Diary](help:tab-diary): a planned season's pill gives its expected result after its activity, and clicking it shows it in the inspector.
<!-- /gui -->
- **A die not rolled yet** (study from vis, an experiment, a search) counts as gaining nothing. The seasons after it say "Counts nothing gained from ...: the die isn't rolled yet." Once the season is played, the later ones are worked out again from what it really gave.
- **Not counted**: the year's end (aging, a grog's year, the covenant's harvests and upkeep), anything the storyguide adds, and seasons nobody planned (the saga's [default](help:advance-unplanned) for them is only filled in when the season is advanced).

### When the season is advanced
<!-- help: guide-advancement-applying -->

<!-- tui -->
1. Press `t` anywhere in the workspace. The [Advance Season](help:advance-season) confirmation lists the plans that will be applied, who has nothing planned and any plan that can't be carried out.
<!-- /tui -->
<!-- gui -->
1. Click **Advance Season** at the top of the window, on any page of the saga. The [Advance Season](help:advance-season) confirmation lists the plans that will be applied, who has nothing planned and any plan that can't be carried out.
<!-- /gui -->
2. Choose Advance and answer any questions it asks.

Every plan's outcome is worked out first, from the saga as it stood, and only then are they all applied: xp gained this season doesn't change this season's other results. Dice left blank on a plan are rolled now. Then, for each character:

- the xp is added to the Ability, Art or Mastery, and the score follows;
<!-- tui -->
- an entry is written on their [Diary tab](help:tab-diary), named for what the season was on with the xp gained, and listing the working and the rule;
<!-- /tui -->
<!-- gui -->
- an entry is written in their [Diary](help:tab-diary) chapter, named for what the season was on with the xp gained, and listing the working and the rule;
<!-- /gui -->
- vis studied is taken from the pool chosen, and a tractatus read is marked as read.

The [Season Summary](help:season-summary) then shows what everyone gained.

### The end of the year
<!-- help: guide-advancement-year-end -->

When Winter is advanced, the app also does the following, each written in the character's Diary:

- **Warping**: +1 Warping Point a year for a Longevity Ritual, and points for living in a strong aura (6 or more) of another realm. A magus gains none from a Magic aura. **Raised from the Dead** adds one a year; **Immortality of the Forest** adds one and makes no aging roll; **Susceptibility to Warping** adds one more in a year that gave any Warping Points, these or an event's.
- **Aging**: everyone aged 35 or more (50 with Strong Faerie Blood or Dhampir), or under a Longevity Ritual, makes an aging roll. The Age is worked out from Year Born, so a character without one never rolls. The roll subtracts the Living Conditions (the covenant's, plus half the Health of a magus's laboratory, plus 1 for Mild Aging, less 1 for Poor Living Conditions or 2 for Leprosy), the Longevity Ritual's modifier and a familiar's bronze cord. Faerie Blood, Magical Blood, Magian Lineage and similar Virtues take 1 off the roll; Strong Faerie Blood and Dhampir take 3.
<!-- tui -->
- The result adds apparent age, Aging Points and Decrepitude. When a Characteristic has more Aging Points than its score (ignoring any minus sign), it falls by 1 (never with Unaging or Demonic Blood), and the Decrepitude score follows from the points. A Crisis is rolled and the survival roll reported for the storyguide (with Mild Aging's +3); a Longevity Ritual sees the character through it and then ends, and the next season is spent recovering. All of this shows in [Aging & Warping](help:section-aging) on the Description tab (`1`).
<!-- /tui -->
<!-- gui -->
- The result adds apparent age, Aging Points and Decrepitude. When a Characteristic has more Aging Points than its score (ignoring any minus sign), it falls by 1 (never with Unaging or Demonic Blood), and the Decrepitude score follows from the points. A Crisis is rolled and the survival roll reported for the storyguide (with Mild Aging's +3); a Longevity Ritual sees the character through it and then ends, and the next season is spent recovering. All of this shows in the [Aging](help:section-aging) section of the Description chapter.
<!-- /gui -->

<!-- tui -->
**Wizard's Twilight**: gaining 2 or more Warping Points from one event takes a magus to the edge of Twilight, which the app rolls at once. It does this for the Warping of an experiment's disaster, and for points typed in **Gain Warping Points now** on the Aging & Warping form.
<!-- /tui -->
<!-- gui -->
**Wizard's Twilight**: gaining 2 or more Warping Points from one event takes a magus to the edge of Twilight, which the app rolls at once. It does this for the Warping of an experiment's disaster, and for points typed in **Gain Warping Points now** on the Aging section's form.
<!-- /gui -->
If the magus enters Twilight, the Diary records how long it lasts and the extra Warping Points; if it lasts a season or more, no season can be planned for them until it ends. The storyguide chooses its effects. A double botch studying vis is only noted in the Diary: add its Warping with Gain Warping Points now.

<!-- tui -->
**Confidence**: the Confidence Score and Confidence Points are typed in the character's top panel (`e`). The app checks the starting values during creation but never changes them in play.
<!-- /tui -->
<!-- gui -->
**Confidence**: the Confidence Score and Confidence Points are typed with **Edit** in the character's header (Edit Character Info). The app checks the starting values during creation but never changes them in play.
<!-- /gui -->

### Changing figures by hand
<!-- help: guide-advancement-by-hand -->

For experience gained outside the planned seasons, or to correct a figure:

<!-- tui -->
1. **An Ability**: on the Abilities tab, highlight it and press `e`. Type the total **XP** (not the xp gained) and the **Specialty**; the score and the total XP the next score needs show as you type. `a` adds a new Ability from the catalog.
2. **The Arts**: on the Hermetic Magic tab, press `e` in Magical Arts. Edit Arts shows all fifteen Arts; type each one's total XP, and its score and the total XP the next score needs are shown beside it as you type.
3. **Mastery**: in [Known Spells](help:section-known-spells), highlight the spell and press `e`.
4. **Aging and Warping**: on the Description tab, press `e` in Aging & Warping to change Decrepitude, the Effects of Aging, the Warping Score and Warping Points.

A change made by hand writes no Diary entry. Press `a` on the Diary tab to record one if you want it kept.
<!-- /tui -->
<!-- gui -->
1. **An Ability**: in the Abilities chapter, click it and then **Edit**. Type the total **XP** (not the xp gained) and the **Specialty**; the score and the total XP the next score needs show as you type. **Add** adds a new Ability from the catalog.
2. **The Arts**: in the Hermetic Magic chapter, click **Edit** beside Magical Arts. Edit Arts shows all fifteen Arts; type each one's total XP, and its score and the total XP the next score needs are shown beside it as you type.
3. **Mastery**: in [Known Spells](help:section-known-spells), click the spell and then **Edit**.
4. **Aging and Warping**: in the Description chapter, click **Edit** beside Aging to change Decrepitude, the Effects of Aging, the Warping Score and Warping Points.

A change made by hand writes no Diary entry. Click **Add** in the Diary chapter to record one if you want it kept.
<!-- /gui -->

### What the app does for you
<!-- help: guide-advancement-app -->

**The app works out:** every score from its xp, each season's Advancement Total and xp, the Virtue and Flaw effects above, the dice left blank, the Winter aging rolls, Decrepitude, yearly Warping and Twilight, and the Diary entries.

**You type:** the season plans, any die rolled at the table, Year Born, Confidence, and any change made outside the seasons.

**See also:** [Plan Season](help:plan-season), [Advance Season](help:advance-season), [Grog's Yearly Update](help:grog-year), [Planning tab](help:tab-planning), [Abilities tab](help:tab-abilities), [Diary tab](help:tab-diary)

# How lab planning works
<!-- help: guide-lab-planning -->

This guide walks through a magus's work in their laboratory: planning it season by season, inventing a spell, comparing Lab Totals, bringing in assistants, using Lab Texts and experimenting, and what happens when the season is advanced. It also covers improving the laboratory itself.

### The laboratory's Planning tab
<!-- help: guide-lab-planning-tab -->

<!-- tui -->
Lab work is planned on the [laboratory sheet](help:laboratory), not the magus's own sheet. The laboratory needs a magus as its owner first: set the owner with `e` on the top panel.

A magus with no laboratory yet starts one from their own sheet: on their Planning tab, plan **Set up a new laboratory** (under Order & covenant). When the season is advanced the laboratory is made in their covenant with them as its owner, and Advance Season offers to plan the second season, which removes the Basic Flaw (see [A new laboratory](help:advance-new-lab)).

To take over a laboratory that has no owner (one left by a magus who died or moved on, or a covenant's spare), plan **Take over the laboratory** (under Order & covenant) on the magus's own Planning tab and choose it in **Laboratory**. When the season is applied the laboratory becomes theirs (any laboratory they had is left without an owner), its Refinement drops to at most their Magic Theory - 3, and the Predecessor may linger. A laboratory that already has a magus as its owner plans the same season on its own Planning tab.

1. In the tree, open the covenant's Laboratories group and choose the laboratory. Press `1` for the [Planning tab](help:tab-lab-planning).
2. The list shows the owner's seasons from the current one on: each planned activity with the seasons it spans and its progress, the free seasons in between, and the first free season after the last plan. A season planned on the owner's own sheet is marked "on (name)'s sheet"; planning lab work there replaces it.
3. Highlight a season. The details panel shows its plan and its Lab Total line by line, or, in red, why it can't be done. A later season's Lab Total counts the seasons planned before it: a season reading an Ignem summa first raises the Ignem in a later invention's total (see [Seasons ahead](help:guide-advancement-ahead)).
4. Press `e` to plan lab work for that season (or reopen the plan there), `a` to start inventing a new spell from a blank design, or `d` to clear the season's plan, with any later seasons scheduled to continue it, after a confirmation.
<!-- /tui -->
<!-- gui -->
Lab work is planned on the [laboratory sheet](help:laboratory), not the magus's own sheet. The laboratory needs a magus as its owner first: set the **Owner** with **Edit** in the laboratory's header.

A magus with no laboratory yet starts one from their own page: in their Planning chapter, plan **Set up a new laboratory** (under Order & covenant). When the season is advanced the laboratory is made in their covenant with them as its owner, and Advance Season offers to plan the second season, which removes the Basic Flaw (see [A new laboratory](help:advance-new-lab)).

To take over a laboratory that has no owner (one left by a magus who died or moved on, or a covenant's spare), plan **Take over the laboratory** (under Order & covenant) in the magus's own Planning chapter and choose it in **Laboratory**. When the season is applied the laboratory becomes theirs (any laboratory they had is left without an owner), its Refinement drops to at most their Magic Theory - 3, and the Predecessor may linger. A laboratory that already has a magus as its owner plans the same season in its own Planning list.

1. On the covenant's page, choose **Laboratories** in the rail and click the laboratory. Choose **Seasons** in its rail: the [Planning](help:tab-lab-planning) list is at the top.
2. The list shows the owner's seasons from the current one on: each planned activity with the seasons it spans and its progress, the free seasons in between, and the first free season after the last plan. A season planned on the owner's own sheet is marked "on (name)'s sheet"; planning lab work there replaces it.
3. Click a season. The inspector on the right shows its plan and its Lab Total line by line, or, in red, why it can't be done. A later season's Lab Total counts the seasons planned before it: a season reading an Ignem summa first raises the Ignem in a later invention's total (see [Seasons ahead](help:guide-advancement-ahead)).
4. Click **Plan** to plan lab work for that season (or reopen the plan there), **New Spell** to start inventing a new spell, or **Clear** to clear the season's plan, with any later seasons scheduled to continue it, after a confirmation.
<!-- /gui -->

### Planning the work
<!-- help: guide-lab-planning-invent -->

<!-- tui -->
`e` and `a` open the [Invent Spell screen](help:invent-spell), titled with the work, the magus, the laboratory and the season. Despite its name it plans every kind of lab work.

1. Choose the **Lab work** (see [Lab work](help:invent-spell-activity)). The screen shows only the fields that work needs.
2. To invent a spell, fill in the [design](help:invent-spell-design). **Start from** picks any spell as the template, the magus's own known spells first for a variant of one of theirs (see [Starting from a spell](help:invent-spell-start)); **New spell** clears the design. Type the Name, Effect, Technique, Form, Requisites, Base level and Ritual, and choose the Range, Duration and Target. The level is worked out below them.
<!-- /tui -->
<!-- gui -->
**Plan** and **New Spell** open the lab work form in place of the list (see [Invent Spell screen](help:invent-spell)), titled with the work, the magus, the laboratory and the season. It plans every kind of lab work.

1. Choose the **Lab work** (see [Lab work](help:invent-spell-activity)). The form shows only the fields that work needs.
2. To invent a spell, fill in the [design](help:invent-spell-design). **Start from** picks any spell as the template, the magus's own known spells first for a variant of one of theirs (see [Starting from a spell](help:invent-spell-start)); **New Spell** asks for it first, or "A new spell (a blank design)". Type the Spell name, Effect, Technique, Form, Requisites, Base level and Ritual, and choose the Range, Duration and Target. The level is worked out in the line under the fields.
<!-- /gui -->
3. To invent from a Lab Text, choose **Invent from a Lab Text** and the **Lab Text**. Texts the magus can't read yet are marked, for example "(can't read: decode first)".
4. For work that pays with vis, choose whose in **Vis**: the laboratory's raw vis, the magus's own or the covenant's vis stores.
5. Under Lab work, tick what applies: **Similar spell known**, a **Magical Focus** or Magic Theory Specialty (shown only if the magus has one), **Days away** and **Other modifiers**. A magus with Potent Magic, Cyclic Magic, Environmental Magic Condition, Planetary or Celestial Magic, or Hermetic Alchemy sees its option too (see [Lab Total](help:invent-spell-total)).

### The Lab Total and when it finishes
<!-- help: guide-lab-planning-total -->

<!-- tui -->
As you type, the [Lab Total](help:invent-spell-total) panel lists every term: Technique and Form (each the lower of the Art and its requisites), Intelligence, Magic Theory, the aura, the laboratory's General Quality, Specializations and Virtues, and the options above. Beside it, [When](help:invent-spell-when) says what the season achieves.
<!-- /tui -->
<!-- gui -->
As you type, the line under the fields gives the [Lab Total](help:invent-spell-total) and every term: Technique and Form (each the lower of the Art and its requisites), Intelligence, Magic Theory, the aura, the laboratory's General Quality, Specializations and Virtues, and the options above. After it, [When](help:invent-spell-when) says what the season achieves.
<!-- /gui -->

- **Inventing a spell**: the Lab Total must be above the spell's level. Each season adds the Lab Total less the level in points, and the spell is invented when the points reach its level. When shows the points so far and the season it is projected to be invented.
- **Inventing from a Lab Text**: one season, if the Lab Total is at least the spell's level.
- **Other work** says what this season produces, such as pawns extracted or the aging-roll modifier.

<!-- tui -->
To compare Lab Totals before choosing, press `2` for the [Lab Totals tab](help:tab-lab-totals). It shows the owner's total for every Technique and Form in this laboratory, the Base Lab Total they share, and what each activity adds.
<!-- /tui -->
<!-- gui -->
To compare Lab Totals before choosing, choose [Lab Totals](help:tab-lab-totals) in the laboratory's rail. It shows the owner's total for every Technique and Form in this laboratory, the Base Lab Total they share, and what each activity adds.
<!-- /gui -->

### Scheduling
<!-- help: guide-lab-planning-schedule -->

1. Choose **Schedule**. It refuses, and says why, if the work can't be done.
2. For work that takes several seasons, such as inventing a spell, the app also plans each following season the work is projected to need, stopping at a season that already has a plan. A message names the last season planned. When each season is advanced, Advance Season asks about [interruptions](help:advance-interrupted) (days away, or the season lost) and works the remaining seasons out again: a season is added when the work fell behind.
<!-- tui -->
3. The Planning tab shows the work as one row spanning its seasons, with its progress, for example "8/15 points".

**Reset** puts back the plan as it was when the screen opened, and **Cancel** leaves without changing anything.
<!-- /tui -->
<!-- gui -->
3. The Planning list shows the work as one row spanning its seasons, with its progress, for example "8/15 points".

**Cancel** leaves without changing anything.
<!-- /gui -->

### Assistants
<!-- help: guide-lab-planning-assistants -->

<!-- tui -->
[Assistants](help:invent-spell-assistants) are named on the Invent Spell screen.

1. Plan the magus's lab work, and choose the helper in **Assistant** (next to Notes). Only characters with The Gift and Magic Theory are offered.
2. Choose **Schedule**: the helper's season is planned as **Assist in a laboratory** with the magus, for each season of the work.
<!-- /tui -->
<!-- gui -->
[Assistants](help:invent-spell-assistants) are named in the lab work form.

1. Plan the magus's lab work, and choose the helper in **Assistant**. Only characters with The Gift and Magic Theory are offered.
2. Choose **Schedule**: the helper's season is planned as **Assist in a laboratory** with the magus, for each season of the work.
<!-- /gui -->
3. The magus's Lab Total now has a line for the helper: their Intelligence plus Magic Theory, for as many helpers as the magus's Leadership allows (at least one). The helper gains 2 xp of Exposure in Magic Theory.

A second helper is planned on their own sheet: Plan Season, **Assist in a laboratory**, with the magus as **Teacher / master**. If the helper already has another plan for the season, Schedule refuses and says so.

### Lab Texts
<!-- help: guide-lab-planning-texts -->

<!-- tui -->
- Inventing a spell writes a Lab Text of it in the laboratory when it is finished. Instilling an effect and a Longevity Ritual write one too. They appear in [Lab Texts](help:section-lab-texts) on the laboratory's Inventory tab (`5`), where `/` filters them.
<!-- /tui -->
<!-- gui -->
- Inventing a spell writes a Lab Text of it in the laboratory when it is finished. Instilling an effect and a Longevity Ritual write one too. They appear in [Lab Texts](help:section-lab-texts) in the laboratory's Stores chapter, where the bar above the list filters them.
<!-- /gui -->
- A magus's own Lab Texts are written raw: only they, and those who have decoded them or been taught to read them, can use them.
<!-- tui -->
- To use another magus's raw texts, plan **Decode another magus's Lab Texts** as lab work. If the reading was settled at the table, set it on the reader's sheet instead: **Lab Texts Read** in [Hermetic Background](help:section-hermetic-background) (Description tab) sets the author, the level read to and whether the magus decoded them or was taught.
<!-- /tui -->
<!-- gui -->
- To use another magus's raw texts, plan **Decode another magus's Lab Texts** as lab work. If the reading was settled at the table, set it on the reader's sheet instead: **Texts Read** in [Hermetic Background](help:section-hermetic-background) (Description chapter) sets the author, the level read to and whether the magus decoded them or was taught.
<!-- /gui -->
- On the author's own sheet, Plan Season offers **Rewrite Lab Texts for general use**, **Copy Lab Texts** and **Teach Lab Text abbreviations**.
- **Casting Tablets** (DE Chapter Eight) let a magus cast a Formulaic or Ritual spell they don't know. A tablet's details show each magus of its covenant casting from it: Stamina + Technique + Form + Aura before the stress die, and what each die gives -- the total minus the level at 0 or more costs 1 Fatigue level, down to -10 two, -20 three, -30 four and a Warping Point; lower, the spell isn't cast, and the caster takes Warping Points equal to its magnitude and loses five levels (a Ritual's Fatigue is long-term). The author fixed the spell's Range, Duration, Target and vis. Reading one needs Artes Liberales 1 and Latin 4. **Write Casting Tablets** makes them of a spell the magus has mastered, and **Copy Lab Texts** copies them too.

### Experimenting
<!-- help: guide-lab-planning-experiment -->

Work that can be done [experimentally](help:invent-spell-experiment) shows an **Experiment** box, **Risk +** and an optional **Research goal**. Inventing from a Lab Text can't be done experimentally. A magus who is Averse to Risk can't experiment, and one who is Prone to Chance must.

- Experimenting adds a simple die and the risk (0 to +3) to the Lab Total. The die is rolled when the season is advanced. Work whose Lab Total is too low without the die can still be planned experimentally, and the plan says so: if the die doesn't lift it, the season goes ahead all the same, the Extraordinary Results chart is still rolled, any vis paid is lost, and the work makes no progress.
- The Extraordinary Results chart is then rolled. Whatever needs the storyguide's word (which of two rolls stands, what a side or modified effect is, what a special result becomes, a Disaster of 5 or more) is asked in Advance Season's [Experiment Results](help:advance-experiment-results) step; the rest is applied by the app and noted in the Diary: Discovery xp, a Disaster's Warping, wounds and laboratory Flaws, a creation destroyed, and the effects the creation keeps (see [Living with an experiment](help:guide-lab-planning-living)).
- With a **Research goal**, the experiment seeks a Discovery (Definitive Edition, Chapter 8, Arcane Discovery; Houses of Hermes: True Lineages calls it original research): the risk goes on the chart roll, not the Lab Total, and is at most +1 for every 5 points of Magic Theory. A Discovery toward the research gives no experience. The goal is chosen from the magus's own goals not yet reached, so add it on their [Research tab](help:tab-research) first. **Risk +** names the chance of a Discovery at each risk the magus may take, and the line above Schedule gives the season's odds as you change it: a Discovery, a harmful result (No Benefit or Complete Failure) and a Disaster. For **Stabilize a Discovery** it gives the chance of stabilizing it instead, at the risk and move of the experiment that made it.
- When the roll is within the risk of 10, Advance Season asks whether to move it there. Taking the move gives a Discovery *as well as* the roll's own result (a side effect or modified effect still stands), unless that result wastes the season. The same move is then made in every later season of that project, and when stabilizing.
- Each spell or enchantment gives one Discovery at most: seeking another with it is refused.
- **Stabilize a Discovery** repeats the experiment: its Lab Total, seasons, vis, risk and move. Any result but a Disaster, No Benefit or Complete Failure stabilizes it, and its magnitude is added to the goal's points; a Discovery rolled then gives nothing. Each attempt gives Warping Points: the magnitude less a simple die. A failed attempt must be tried again the very next season, or the Discovery is lost.
- **Seek an insight** (a season studying a text, relic or teacher) rolls Intelligence + Magic Theory + a stress die against 18, +3 for Inventive Genius. Its research goal is chosen from the magus's goals too.
- Every season spent on a goal goes in its Research Log, with the roll and what came of it: see the magus's [Research tab](help:tab-research), and the laboratory's while the research is under way.

### Living with an experiment
<!-- help: guide-lab-planning-living -->

An experiment's results stay with what it made, "warts and all" (Ars Magica Definitive Edition, Chapter 8: Laboratory, Experimentation):

- **Side effects and modified effects** are kept as the creation's **experimental effects**: on an invented spell (and on anyone's copy learned from it or its Lab Text), on an instilled effect (and on the Lab Text written of it, which reproduces them), on a familiar's bond power or the binding itself, and on a Longevity Ritual. Each shows where the creation's details are shown, with the season it came from; a fatal flaw is marked.
- A side effect's description can be left blank in [Experiment Results](help:advance-experiment-results) and filled in later. Edit a known spell (its Mastery form), an item's effect or a bond power and use **Experimental effects** to add, change or remove one. A new Range, Duration or Target given there changes the creation when the form is saved. The level never changes, and no requisite is added.
- **A special result** becomes what the storyguide makes of it: a story event goes into the laboratory's and the covenant's Diaries as an open Story Event; a spell created as well is learned, with its Lab Text; extra vis is paid from the season's vis.
- **Investigating an item** by experiment: changes reach the power the storyguide names, and a result that would destroy the creation destroys the item, unless one of its own effects protects it with a level above the Lab Total.

**The app's assumptions.** The rules don't size a change of potency. The app takes one step of potency as 5 points of the Lab Total behind the creation, which is 1 point of a Longevity Ritual's modifier: a ritual reduced by a step protects one point less on every aging roll. Where nothing is worked out from the Lab Total (a spell's or an item's power), the change is only recorded and described for the storyguide.

### When the season is advanced
<!-- help: guide-lab-planning-advance -->

<!-- tui -->
Nothing happens to the magus or the laboratory until the season is advanced with `t` (see [Advance Season](help:advance-season)). Then:
<!-- /tui -->
<!-- gui -->
Nothing happens to the magus or the laboratory until the season is advanced with **Advance Season** (see [Advance Season](help:advance-season)). Then:
<!-- /gui -->

- a finished spell joins the magus's Known Spells, its Lab Text goes into the laboratory, and later seasons planned to continue it are removed;
- an unfinished invention keeps its points and carries on into the next free season;
- vis is paid or gained, a connection is fixed, a device is enchanted, and so on;
<!-- tui -->
- the magus gains 2 xp of Exposure in Magic Theory, and entries are written in the magus's Diary and the laboratory's [Diary tab](help:tab-lab-diary).
<!-- /tui -->
<!-- gui -->
- the magus gains 2 xp of Exposure in Magic Theory, and entries are written in the magus's Diary and the laboratory's [Diary](help:tab-lab-diary), in its Seasons chapter.
<!-- /gui -->

### Improving the laboratory
<!-- help: guide-lab-planning-improve -->

<!-- tui -->
- **Seasons of work**: on the Planning tab, `e` offers **Set up the laboratory** (two seasons; a magus with no laboratory plans **Set up a new laboratory** on their own sheet), **Refine the laboratory** (+1 Refinement a season, if Magic Theory is at least the new Refinement + 3), **Take over the laboratory** (a laboratory with no owner is taken over from the magus's own sheet) and **Move the laboratory**. Refining may also gain Highly Organized, or a Hidden Defect on a botch.
- **Virtues and Flaws**: press `3` for the [Virtues & Flaws tab](help:tab-lab-vf) and `a` to pick one from the catalog. What they add shows in the Characteristics and on the Lab Totals tab, and a warning appears when there are more than Size and Refinement allow.
- **Features and Specializations**: press `4` for the [Attributes tab](help:tab-lab-attributes). `a` in [Features](help:section-lab-features) builds a Feature on a Feature Virtue. [Specializations](help:section-lab-specializations) are worked out from them; `Space` turns one off or on within the caps.
- **Magic items**: `a` in [Magic Items](help:section-lab-magic-items), on the same tab, installs an enchanted device kept here, for a Virtue it duplicates or points its level buys (see [How to install a magic item in a laboratory](help:guide-lab-magic-item)).
- **Characteristics**: `e` in the top panel's Characteristics edits the typed values.
<!-- /tui -->
<!-- gui -->
- **Seasons of work**: in the Planning list, **Plan** offers **Set up the laboratory** (two seasons; a magus with no laboratory plans **Set up a new laboratory** on their own sheet), **Refine the laboratory** (+1 Refinement a season, if Magic Theory is at least the new Refinement + 3), **Take over the laboratory** (a laboratory with no owner is taken over from the magus's own sheet) and **Move the laboratory**. Refining may also gain Highly Organized, or a Hidden Defect on a botch.
- **Virtues and Flaws**: choose [Virtues & Flaws](help:tab-lab-vf) in the rail and click **Add** to pick one from the catalog. What they add shows in the Characteristics and in the Lab Totals chapter, and a warning appears when there are more than Size and Refinement allow.
- **Features and Specializations**: choose [Specializations](help:tab-lab-attributes) in the rail. **Add** in [Features](help:section-lab-features) builds a Feature on a Feature Virtue. [Specializations](help:section-lab-specializations) are worked out from them; **Turn Off/On** turns the one clicked off or on within the caps.
- **Magic items**: **Add** in [Magic Items](help:section-lab-magic-items), in the same chapter, installs an enchanted device kept here, for a Virtue it duplicates or points its level buys (see [How to install a magic item in a laboratory](help:guide-lab-magic-item)).
- **Characteristics**: **Edit** beside Characteristics, under the header, edits the typed values.
<!-- /gui -->

### What the app does for you
<!-- help: guide-lab-planning-app -->

**The app works out:** every Lab Total and its terms, the spell's level, the seasons the work needs and the plans for them, progress from season to season, whether each plan can be done, the experiment's results, and what the season does to the magus and the laboratory.

**You type:** the laboratory's owner, the work and its design or choices, any die rolled at the table, and the assistants' plans on their own sheets.

**See also:** [Laboratory sheet](help:laboratory), [Invent Spell screen](help:invent-spell), [Scheduling](help:invent-spell-schedule), [Lab Totals tab](help:tab-lab-totals), [Advance Season](help:advance-season), [How the app handles advancement](help:guide-advancement)

# How the app handles advancement
<!-- help: guide-advancement -->

This guide follows a character's experience from the season it is planned to the moment it lands on their sheet, and what the end of each year does to them. Use it when you want to know where a score comes from, what the app adds by itself when a season is advanced, and when to change a figure by hand.

### Scores come from experience
<!-- help: guide-advancement-scores -->

For each Ability and Art the app keeps only the experience points (xp). The score is always worked out from the xp with the Advancement Table (Ars Magica Definitive Edition, Chapter 3: Characters). The xp is a running total: it never starts again at 0 when a score is reached.

- An Ability needs 5 xp for score 1, 15 for 2, 30 for 3, 50 for 4 and 75 for 5.
- An Art needs 1 xp for score 1, 3 for 2, 6 for 3, 10 for 4 and 15 for 5.

1. Open the character from their covenant's Characters group in the tree and press `2` for the [Abilities tab](help:tab-abilities). Each Ability shows its Score, and its XP as the total so far over the total the next score needs, for example "50/75".
2. For a magus, press `4` for the Hermetic Magic tab. [Magical Arts](help:section-arts) shows each Technique and Form with its Score and XP.

A spell's Mastery is the exception: its score and xp are both typed, and xp gained in a season only ever raises the score.

### Virtues and Flaws the app applies
<!-- help: guide-advancement-virtues -->

These Virtues and Flaws from the catalog are taken into account wherever the app works out a season's xp:

- **Affinity with** an Ability or Art multiplies the xp gained in it by 1.5, rounded up.
- **Puissant** doesn't change the xp. It adds a fixed bonus to the score used (+2 for an Ability, +3 for an Art), shown in brackets after the score.
- **Book Learner**, **Apt Student**, **Independent Study** and **Free Study** add to the Advancement Total of the activity they name; **Poor Student** and **Unimaginative Learner** take from it. Being taught or reading never falls below 1.
- **Good Teacher** raises the Source Quality of the students the character teaches.

A Virtue or Flaw made under House Rules is text only, so adjust its effect by hand.

### Planning the season
<!-- help: guide-advancement-planning -->

1. On the character's sheet, open the Planning tab (`6` for a magus, `5` for anyone else) and press `e` in the [This Season](help:section-char-season) section. This opens [Plan Season](help:plan-season) for the current season. A covenant's [Seasons tab](help:tab-cov-seasons) opens the same form for anyone in its Magi or Companions list.
2. Choose the **Activity**, then fill in what it asks: **Experience in**, a **Book**, a **Teacher / master**, a **Source Quality**, **Vis from**, a **Stress die (blank: rolled)** or **Months lost (0-3)**.
3. Watch the line above Save. It shows each subject's Advancement Total, the xp gained and how the score and xp will change, for example "Latin: Advancement Total 4, +4 xp (score 3, 34 -> 38 xp)". A plan that breaks a rule shows why, and Save refuses it.
4. Save. The This Season section now shows the plan and what it will give.

What each activity gives (Ars Magica Definitive Edition, Chapter 10: Long-Term Events):

- **Work / Exposure**: 2 xp in one subject, or 1 in each of two.
- **Practice**: Source Quality 4 (5 for a spell's Mastery) in one Ability. Arts can't be practised.
- **Read a book**: a summa's Quality, never past its Level; a tractatus's Quality, once per reader. The Quality is the one the book is read at: a palimpsest's -3, a commentary's +1, a florilegium's bonus, an exemplar's -3 and (with Extended book Quality) its craftsmanship all count, as its details panel shows. Only one reader a season for a book, or for any book bound in the same codex. A book whose Level or Quality is still to be set can't be read until it has them. A commentary is read only after a season on its summa: the plan notes it when none is on record. Reading a folio's book also gives 1 xp in Order of Hermes Lore. **Gloss it** glosses the book while reading it (+1 Quality, once): the reader needs a score of at least half its Level and better Communication than its author.
- **Correspondence on** (any season, with Covenants in play): useful correspondence on a theme of the character's research or reading, with at least one letter received that season, adds 1 xp in its subject. One correspondence counts a season.
- **Be taught**: the teacher's Communication + Teaching + 3, plus 6 for one student or 3 for two, never past the teacher's score. The teacher must plan Teach for the same season.
- **Be trained**: the master's score + 3, never past it; Abilities only.
- **Study from vis** (magi): a stress die plus the aura's modifier, using one pawn of the Art's vis for every 5 points of its score (at least one).
- **Adventure**: the storyguide's Source Quality of 5 to 10, split among up to three subjects, at most 5 to each.
- **Lab work** and **Assist in a laboratory** give 2 xp of Exposure in Magic Theory; writing and copying books, and Teach, give Exposure too.

The Advancement Total is the Source Quality plus or minus the Virtues and Flaws above. Each full month lost cuts it by a third, then Affinity multiplies it. A character with a Wound Penalty of -3 to -5 gains half the xp, and one at -6 or worse can do nothing productive.

Grogs aren't planned season by season. On a grog's Planning tab, `e` sets up their [yearly update](help:grog-year), applied in Winter.

### When the season is advanced
<!-- help: guide-advancement-applying -->

1. Press `t` anywhere in the workspace. The [Advance Season](help:advance-season) confirmation lists the plans that will be applied, who has nothing planned and any plan that can't be carried out.
2. Choose Advance and answer any questions it asks.

Every plan's outcome is worked out first, from the saga as it stood, and only then are they all applied: xp gained this season doesn't change this season's other results. Dice left blank on a plan are rolled now. Then, for each character:

- the xp is added to the Ability, Art or Mastery, and the score follows;
- an entry is written on their [Diary tab](help:tab-diary), named for what the season was on with the xp gained, and listing the working and the rule;
- vis studied is taken from the pool chosen, and a tractatus read is marked as read.

The [Season Summary](help:season-summary) then shows what everyone gained.

### The end of the year
<!-- help: guide-advancement-year-end -->

When Winter is advanced, the app also does the following, each written in the character's Diary:

- **Warping**: +1 Warping Point a year for a Longevity Ritual, and points for living in a strong aura (6 or more) of another realm. A magus gains none from a Magic aura.
- **Aging**: everyone aged 35 or more, or under a Longevity Ritual, makes an aging roll. The Age is worked out from Year Born, so a character without one never rolls. The roll subtracts the Living Conditions (the covenant's, plus half the Health of a magus's laboratory), the Longevity Ritual's modifier and a familiar's bronze cord.
- The result adds apparent age, Aging Points and Decrepitude. When a Characteristic has more Aging Points than its score (ignoring any minus sign), it falls by 1, and the Decrepitude score follows from the points. A Crisis is rolled and the survival roll reported for the storyguide; a Longevity Ritual sees the character through it and then ends, and the next season is spent recovering. All of this shows in [Aging & Warping](help:section-aging) on the Description tab (`1`).

**Wizard's Twilight**: gaining 2 or more Warping Points from one event takes a magus to the edge of Twilight, which the app rolls at once. It does this for the Warping of an experiment's disaster, and for points typed in **Gain Warping Points now** on the Aging & Warping form. If the magus enters Twilight, the Diary records how long it lasts and the extra Warping Points; if it lasts a season or more, no season can be planned for them until it ends. The storyguide chooses its effects. A double botch studying vis is only noted in the Diary: add its Warping with Gain Warping Points now.

**Confidence**: the Confidence Score and Confidence Points are typed in the character's top panel (`e`). The app checks the starting values during creation but never changes them in play.

### Changing figures by hand
<!-- help: guide-advancement-by-hand -->

For experience gained outside the planned seasons, or to correct a figure:

1. **An Ability**: on the Abilities tab, highlight it and press `e`. Type the total **XP** (not the xp gained) and the **Specialty**; the score and the total XP the next score needs show as you type. `a` adds a new Ability from the catalog.
2. **The Arts**: on the Hermetic Magic tab, press `e` in Magical Arts. Edit Arts shows all fifteen Arts; type each one's total XP, and its score and the total XP the next score needs are shown beside it as you type.
3. **Mastery**: in [Known Spells](help:section-known-spells), highlight the spell and press `e`.
4. **Aging and Warping**: on the Description tab, press `e` in Aging & Warping to change Decrepitude, the Effects of Aging, the Warping Score and Warping Points.

A change made by hand writes no Diary entry. Press `a` on the Diary tab to record one if you want it kept.

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

Lab work is planned on the [laboratory sheet](help:laboratory), not the magus's own sheet. The laboratory needs a magus as its owner first: set the owner with `e` on the top panel.

1. In the tree, open the covenant's Laboratories group and choose the laboratory. Press `1` for the [Planning tab](help:tab-lab-planning).
2. The list shows the owner's seasons from the current one on: each planned activity with the seasons it spans and its progress, the free seasons in between, and the first free season after the last plan. A season planned on the owner's own sheet is marked "on (name)'s sheet"; planning lab work there replaces it.
3. Highlight a season. The details panel shows its plan and its Lab Total line by line, or, in red, why it can't be done.
4. Press `e` to plan lab work for that season (or reopen the plan there), `a` to start inventing a new spell from a blank design, or `d` to clear the season's plan, with any later seasons scheduled to continue it, after a confirmation.

### Planning the work
<!-- help: guide-lab-planning-invent -->

`e` and `a` open the [Invent Spell screen](help:invent-spell), titled with the work, the magus, the laboratory and the season. Despite its name it plans every kind of lab work.

1. Choose the **Lab work** (see [Lab work](help:invent-spell-activity)). The screen shows only the fields that work needs.
2. To invent a spell, fill in the [design](help:invent-spell-design). **Start from** picks a spell the magus doesn't know as the starting point; **New spell** clears the design. Type the Name, Effect, Technique, Form, Requisites, Base level and Ritual, and choose the Range, Duration and Target. The level is worked out below them.
3. To invent from a Lab Text, choose **Invent from a Lab Text** and the **Lab Text**. Texts the magus can't read yet are marked, for example "(can't read: decode first)".
4. For work that pays with vis, choose whose in **Vis**: the laboratory's raw vis, the magus's own or the covenant's vis stores.
5. Under Lab work, tick what applies: **Similar spell known**, a **Magical Focus** or Magic Theory Specialty (shown only if the magus has one), **Days away** and **Other**.

### The Lab Total and when it finishes
<!-- help: guide-lab-planning-total -->

As you type, the [Lab Total](help:invent-spell-total) panel lists every term: Technique and Form (each the lower of the Art and its requisites), Intelligence, Magic Theory, the aura, the laboratory's General Quality, Specializations and Virtues, and the options above. Beside it, [When](help:invent-spell-when) says what the season achieves.

- **Inventing a spell**: the Lab Total must be above the spell's level. Each season adds the Lab Total less the level in points, and the spell is invented when the points reach its level. When shows the points so far and the season it is projected to be invented.
- **Inventing from a Lab Text**: one season, if the Lab Total is at least the spell's level.
- **Other work** says what this season produces, such as pawns extracted or the aging-roll modifier.

To compare Lab Totals before choosing, press `2` for the [Lab Totals tab](help:tab-lab-totals). It shows the owner's total for every Technique and Form in this laboratory, the Base Lab Total they share, and what each activity adds.

### Scheduling
<!-- help: guide-lab-planning-schedule -->

1. Press **Schedule**. It refuses, and says why, if the work can't be done.
2. For work that takes several seasons, such as inventing a spell, the app also plans each following season the work is projected to need, stopping at a season that already has a plan. A message names the last season planned.
3. The Planning tab shows the work as one row spanning its seasons, with its progress, for example "8/15 points".

**Reset** puts back the plan as it was when the screen opened, and **Cancel** leaves without changing anything.

### Assistants
<!-- help: guide-lab-planning-assistants -->

[Assistants](help:invent-spell-assistants) are planned on the helper's own sheet, not on the Invent Spell screen.

1. Plan the magus's lab work for the current season first.
2. On the helper's Planning tab, press `e`, choose **Assist in a laboratory** and choose the magus as **Teacher / master**. The helper needs The Gift and Magic Theory.
3. The magus's Lab Total now has a line for the helper: their Intelligence plus Magic Theory, for as many helpers as the magus's Leadership allows (at least one). The helper gains 2 xp of Exposure in Magic Theory.

Since Plan Season plans only the current season, assistants are added one season at a time.

### Lab Texts
<!-- help: guide-lab-planning-texts -->

- Inventing a spell writes a Lab Text of it in the laboratory when it is finished. Instilling an effect and a Longevity Ritual write one too. They appear in [Lab Texts](help:section-lab-texts) on the laboratory's Inventory tab (`5`), where `/` filters them.
- A magus's own Lab Texts are written raw: only they, and those who have decoded them or been taught to read them, can use them.
- To use another magus's raw texts, plan **Decode another magus's Lab Texts** as lab work. If the reading was settled at the table, set it on the reader's sheet instead: **Lab Texts Read** in [Hermetic Background](help:section-hermetic-background) (Description tab) sets the author, the level read to and whether the magus decoded them or was taught.
- On the author's own sheet, Plan Season offers **Rewrite Lab Texts for general use**, **Copy Lab Texts** and **Teach Lab Text abbreviations**.
- **Casting Tablets** (DE Chapter Eight) let a magus cast a Formulaic or Ritual spell they don't know. A tablet's details show each magus of its covenant casting from it: Stamina + Technique + Form + Aura before the stress die, and what each die gives -- the total minus the level at 0 or more costs 1 Fatigue level, down to -10 two, -20 three, -30 four and a Warping Point; lower, the spell isn't cast, and the caster takes Warping Points equal to its magnitude and loses five levels (a Ritual's Fatigue is long-term). The author fixed the spell's Range, Duration, Target and vis. Reading one needs Artes Liberales 1 and Latin 4. **Write Casting Tablets** makes them of a spell the magus has mastered, and **Copy Lab Texts** copies them too.

### Experimenting
<!-- help: guide-lab-planning-experiment -->

Work that can be done [experimentally](help:invent-spell-experiment) shows an **Experiment** box, **Risk +** and an optional **Research goal**. Inventing from a Lab Text can't be done experimentally. A magus who is Averse to Risk can't experiment, and one who is Prone to Chance must.

- Experimenting adds a simple die and the risk (0 to +3) to the Lab Total. The die is rolled when the season is advanced.
- The Extraordinary Results chart is then rolled and applied by the app, and noted in the Diary: Discovery xp, a disaster's Warping, wounds and laboratory Flaws, a creation destroyed, or side effects kept.
- When an experiment seeking a Discovery could use the risk to move its roll, Advance Season asks first.

### When the season is advanced
<!-- help: guide-lab-planning-advance -->

Nothing happens to the magus or the laboratory until the season is advanced with `t` (see [Advance Season](help:advance-season)). Then:

- a finished spell joins the magus's Known Spells, its Lab Text goes into the laboratory, and later seasons planned to continue it are removed;
- an unfinished invention keeps its points and carries on into the next free season;
- vis is paid or gained, a connection is fixed, a device is enchanted, and so on;
- the magus gains 2 xp of Exposure in Magic Theory, and entries are written in the magus's Diary and the laboratory's [Diary tab](help:tab-lab-diary).

### Improving the laboratory
<!-- help: guide-lab-planning-improve -->

- **Seasons of work**: on the Planning tab, `e` offers **Set up the laboratory** (two seasons), **Refine the laboratory** (+1 Refinement a season, if Magic Theory is at least the new Refinement + 3), **Take over the laboratory** and **Move the laboratory**. Refining may also gain Highly Organized, or a Hidden Defect on a botch.
- **Virtues and Flaws**: press `3` for the [Virtues & Flaws tab](help:tab-lab-vf) and `a` to pick one from the catalog. What they add shows in the Characteristics and on the Lab Totals tab, and a warning appears when there are more than Size and Refinement allow.
- **Features and Specializations**: press `4` for the [Attributes tab](help:tab-lab-attributes). `a` in [Features](help:section-lab-features) builds a Feature on a Feature Virtue. [Specializations](help:section-lab-specializations) are worked out from them; `Space` turns one off or on within the caps.
- **Characteristics**: `e` in the top panel's Characteristics edits the typed values.

### What the app does for you
<!-- help: guide-lab-planning-app -->

**The app works out:** every Lab Total and its terms, the spell's level, the seasons the work needs and the plans for them, progress from season to season, whether each plan can be done, the experiment's results, and what the season does to the magus and the laboratory.

**You type:** the laboratory's owner, the work and its design or choices, any die rolled at the table, and the assistants' plans on their own sheets.

**See also:** [Laboratory sheet](help:laboratory), [Invent Spell screen](help:invent-spell), [Scheduling](help:invent-spell-schedule), [Lab Totals tab](help:tab-lab-totals), [Advance Season](help:advance-season), [How the app handles advancement](help:guide-advancement)

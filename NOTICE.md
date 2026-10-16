# Licences, credits and trademarks

Armarius, a saga manager for Ars Magica, is an unofficial, fan-made tool. It is not published,
approved or endorsed by Trident, Inc. d/b/a Atlas Games or by Paradox
Interactive AB.

## Licences

**The program** is © 2026 apoapsis and is free software: you can
redistribute it and/or modify it under the terms of the GNU General Public
License, version 3, as published by the Free Software Foundation. It is
distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See [LICENSE](LICENSE) for the full text.

**The Ars Magica rules text** the program contains is adapted from
material licensed under the [Creative Commons Attribution-ShareAlike 4.0
International licence (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/),
which permits adaptations to be shared under the GNU GPL v3. Those
adaptations are also available on their own under CC BY-SA 4.0. They are:

- the catalogs in `data/*_catalog.json` (Virtues & Flaws, laboratory
  Virtues & Flaws and Features, Abilities, Houses, covenant Boons & Hooks,
  spells, weapons & armor);
- rules descriptions written into the code, such as the descriptions of
  the fifteen Arts in `ars_magica_manager/arts.py`;
- the content packs in `data/packs/` and the modules that build them in
  `ars_magica_manager/book_packs/`: summaries, in the program's own words,
  of the Tribunal sourcebooks' open content (*Guardians of the Forests:
  The Rhine Tribunal*, from its [open content on Project: Redcap](https://redcap.org/page/Guardians_of_the_Forest:_The_Rhine_Tribunal_Open_Content)).

### Attribution

Based on the material for Ars Magica, ©1993–2024, licensed by Trident, Inc.
d/b/a Atlas Games®, under Creative Commons Attribution-ShareAlike 4.0
International license 4.0 ("CC-BY-SA 4.0").

Sources: the *Ars Magica Fifth Edition* and *Ars Magica Definitive Edition*
core rules, and the sourcebooks *Covenants*, *Art & Academe*, *Houses of
Hermes: True Lineages*, *Houses of Hermes: Mystery Cults*, *Houses of
Hermes: Societates*, *The Mysteries: Revised Edition* and, for the content
packs, *Guardians of the Forests: The Rhine Tribunal*. Where it is
recorded, each catalog entry's `source` field names its book. The spell
catalog was built from [The Grand
Grimoire](https://www.redcap.org/page/The_Grand_Grimoire) on Project:
Redcap, which collects the Hermetic spells of those books under the same
licence.

**Changes made:** the text has been condensed, reformatted and split into
structured data (names, costs, prerequisites, game effects) for use in the
program; some entries are summarised rather than quoted, and examples and
sidebars are left out.

### Artwork, icons and fonts

**The Technique, Form and House symbols** in
`ars_magica_manager/assets/symbols/` are adapted from the released images
on Atlas Games's [Open Ars Magica](https://atlas-games.com/arsmagica/openars)
page, and **the app icon** in `ars_magica_manager/assets/app/` from its
Order of Hermes sigil. Based on the material for Ars Magica, ©1993–2024,
licensed by Trident, Inc. d/b/a Atlas Games®, under Creative Commons
Attribution-ShareAlike 4.0 International license 4.0 ("CC-BY-SA 4.0").
These adaptations are available under CC BY-SA 4.0 too.

**Changes made:** the symbols were trimmed, centred on a square and traced
from the original black-and-white bitmaps to vector outlines (SVG), drawn
in a single colour that the app tints to its theme. House Guernicus has no
released symbol and shows the Quaesitor symbol. The sigil was scaled down
and made into an icon file, and its light parts are cut out of a block as
the Code of Hermes Ability's mark.

**The Ability marks** are drawn by the app's own code
(`ars_magica_manager/gui/mark_charges.py`) in the style of the Art
symbols; they are part of the app and under its licence.

**The lion** in `ars_magica_manager/assets/charges/` is adapted from
[Lion rampant element](https://commons.wikimedia.org/wiki/File:Lion_rampant_element.svg)
on Wikimedia Commons, by Inductiveload after Jiří Louda, in the public
domain. Its shapes were merged into a silhouette, line work and claws so
the app can paint it in any tincture (`assets/charges/LICENSE.txt`).

**The other drawn charges** in the same folder are adapted the same way
from Wikimedia Commons files, each in the public domain or under CC0:
the lion with its tail knotted (*Lion rampant (tail nowed)*, by
Inductiveload), the eagle (*Meuble héraldique Aigle éployée*), the
fleur-de-lis (*Meuble héraldique Fleur de lis*), the tower (*Meuble
Héraldique Tour ajourée*), the cross (*Pièce héraldique croix dentelée*,
CC0), the crescent (*Coa Illustration Elements Planet Crescent*, after
Fox-Davies and Graham Johnston), the star (*Coa Illustration Elements
Planet Star*) and the tree (*Coa Illustration Elements Plant Pear Tree*,
after Jérôme de Bara). `assets/charges/LICENSE.txt` links each file.

**The icons** in `ars_magica_manager/assets/icons/` are
[Phosphor Icons](https://phosphoricons.com) (Light weight), © 2023
Phosphor Icons, under the MIT licence (`assets/icons/LICENSE.txt`). **The
ruin** in `ars_magica_manager/assets/drawn/` is drawn by the app's own
code (`tools/draw_ruin.py`) after Phosphor's castle turret, its top
broken off and fallen stones at its foot; as a modified Phosphor icon it
is under the same MIT licence.

**The sounds** in `ars_magica_manager/assets/sounds/` are recordings from
[Freesound](https://freesound.org), each dedicated to the public domain
under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/)
(`assets/sounds/LICENSE.txt`). No credit is required; with thanks to
their recordists:

- `page.wav`: [book_page.wav](https://freesound.org/people/fellur/sounds/429724/) by fellur;
- `page-long.wav`: [Page Turn](https://freesound.org/people/davidbain/sounds/136778/) by davidbain;
- `quill.wav`: [Scribble](https://freesound.org/people/Tomoyo%20Ichijouji/sounds/211247/) by Tomoyo Ichijouji;
- `coins.wav`: [Money Bag](https://freesound.org/people/PhilSavlem/sounds/338260/) by PhilSavlem;
- `chest.wav`: [Wooden Chest Open.wav](https://freesound.org/people/The_Frisbee_of_Peace/sounds/573654/) by The_Frisbee_of_Peace;
- `seal.wav`: [Wax seal](https://freesound.org/people/Cerise_Virtuelle/sounds/759526/) by Cerise_Virtuelle;
- `tock.wav`: [wood_knock.wav](https://freesound.org/people/110110010/sounds/66397/) by 110110010.

Changes made: each was converted from Freesound's preview to mono 44.1 kHz
WAV, its silence trimmed, and its level evened with the others.

**The fonts** in `ars_magica_manager/assets/fonts/` are under the SIL Open
Font License, version 1.1, with each font's licence beside it: EB Garamond,
© 2017 The EB Garamond Project Authors; Uncial Antiqua, © 2011 Brian J.
Bonislawsky DBA Astigmatic (AOETI), Reserved Font Name "Uncial Antiqua".

## Trademarks

Ars Magica Open License Logo ©2024 Trident, Inc. The Ars Magica Open
License Logo, Ars Magica, and Mythic Europe are trademarks of Trident,
Inc., and are used with permission.

Order of Hermes, Tremere, Doissetep, and Grimgroth are trademarks of
Paradox Interactive AB and are used with permission.

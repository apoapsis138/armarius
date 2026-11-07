# The Atlas
<!-- help: saga-atlas; gui -->

A chapter of the saga's page, on the desktop only: the saga's maps, each with a pin for the covenants, places, towns, lords and creatures on it. Pick a map from the list at the top right; the chapter opens on the one shown last.

- **Scroll** over the map to zoom in and out, and **drag** it to look around. **Fit** shows the whole map again.
- **Hover** over a pin to see the record in the Inspector: its name, what kind it is and its summary. Where several records share a spot, the pin shows how many, and the Inspector lists them all.
- **Click** a pin to open its record's page; **Back** (its name in the trail) returns to the Atlas, at the same map and place. Where several share the spot, a click lists them to choose from.
- **Show** chooses which kinds of record the map shows: covenants, laboratories, neighbours and places, creatures.
- In [Player view](help:player-view) (the eye in the title bar), for a screen your players can see across the table, the map leaves off the secret pins, every record shown at one, and every record the players don't know of; pins can't be moved or changed then. A secret pin has a dashed ring, so it can be told apart without its colour. A secret pin hides only itself, and an unknown record only itself: a known creature in an unknown grove still shows at the grove's pin, without the grove's name.

A record with no pin of its own on the map is shown at the pin of what it sits in, however far out: a laboratory at its covenant's pin, a covenant built in a forest at the forest's, a regio's creature at its place's. The Inspector says where ("at the Black Forest"). A mobile covenant follows its stop in force, so its pin moves with it as the seasons pass, even past a pin of its own.

**See also:** [Maps](help:atlas-maps), [Pins](help:atlas-pins), [Scale and distance](help:atlas-scale), [How to add a map and place its records](help:guide-atlas)

### Maps
<!-- help: atlas-maps; gui -->

A map is a picture of a region: a PNG, WebP or JPEG you drew or exported, such as a map from a cartography program. It belongs to its Tribunal, or to the saga when it is of a region with no Tribunal. A Tribunal can have several maps (the whole Tribunal, and a city drawn larger), and a record can have a pin on each.

- **New Map** adds one, **Edit Map** changes the map on show, and **Remove Map** takes it and its pins out of the saga (its records stay).
- The picture is copied into the **maps** folder beside the saga files, so moving or deleting your own file later changes nothing. The saga keeps only the copy's name.
- A map with no picture yet shows a **placeholder**: parchment with a grid lettered A to J along the top and numbered 1 to 10 down the side, a compass rose and the map's name. Place your records on it roughly ("Durenmar is about G8"); when your map is drawn, Edit Map adds its picture and the pins stay where they were, ready to be dragged into place. Give the placeholder the shape of the map to come (Placeholder width and height: 3 by 2, or the size in pixels you will export at) so the pins land as near as they can.
- A map whose picture is missing (a saga opened on another computer) shows the same placeholder in the picture's shape, with its pins still on it.
- A pin's place is kept as a share of the map's width and height, so a new export of the same map at another size keeps every pin where it was. When a new picture's proportions differ, the Atlas says so: check the pins.

### The map form
<!-- help: atlas-map-form; gui -->

- **Name**: the map's name, as the list shows it.
- **Tribunal**: the Tribunal it belongs to; blank for the saga's own map of a region with no Tribunal.
- **Picture**: the picture to show, chosen from your files; Delete clears it.
- **Placeholder width** and **Placeholder height**: while there is no picture, the shape of the map to come (3 by 2 when left blank). Give both or neither.
- **Credit**: who drew it, and its licence, shown under the map.

### Pins
<!-- help: atlas-pins; gui -->

The pins belong to the saga. A Tribunal pack may bring its maps with a pin for each of its covenants and places (see [How to start a saga from a sourcebook](help:guide-book-packs)); you add, move and take off pins of your own, and importing the pack again never moves them.

- **Place on Map** lists the covenants, neighbours and creatures with no pin on the map yet. Choose one, then click where it is on the map (Esc stops).
- **Drag** a record's own pin to move it. A record shown at another's pin can't be dragged: place it to give it a pin of its own.
- **Right-click** a pin to open its record, make it **Secret** (left off in Player view) or **take it off the map**. A pack's pin taken off stays off when the pack is imported again; placing the record again brings it back.
- A record's page has **Show on Map** in its **Manage** chapter while it shows on a map: it opens the Atlas on that map, its pin ringed.

### Scale and distance
<!-- help: atlas-scale; gui -->

A drawn map is to no projection, so the Atlas measures it by its own scale bar.

- **Set Scale**: click one end of the map's scale bar, then the other, and say how long the bar is, in **leagues** or **miles**. A league is three miles (Grand Grimoire of Hermetic Spells p. 48; Transforming Mythic Europe p. 108: the Definitive Edition uses leagues for its spells' reach but gives no length). Set it again at any time; a new picture of the same map keeps it.
- **Measure**, once the map has a scale: click a pin or any point, then another. A dashed line joins them, with how far apart they are in leagues and miles, **in a straight line**. Roads and rivers wind, so the way itself is longer. Esc clears it.
- The line under the map says what the scale bar stands for.
- The [Travel](help:travel) calculator uses it: choose From and To that are both on a map with a scale, and it fills in the miles as the crow flies.

### Place on Map
<!-- help: atlas-place; gui -->

The records that can be placed: every covenant, neighbour and creature with no pin of its own on this map. Search by name, or filter by kind. Once one is chosen, the line under the map says where to click.

# How to add a map and place its records
<!-- help: guide-atlas; gui -->

This guide puts a Tribunal's map into the saga and pins its covenants and places on it. Use it when you have drawn or exported a map of your saga's region.

### Adding the map
<!-- help: guide-atlas-map; gui -->

1. Export the map as a PNG, WebP or JPEG from your drawing or cartography program. A map with a scale bar is best. No map drawn yet? Leave Picture blank in step 3: the Atlas draws a placeholder to pin on now, and the picture can be added later.
2. Open the saga's page and its **The Atlas** chapter, and click **New Map**.
3. Type the map's **Name**, choose its **Tribunal** (blank for a region with none), click **Picture** and choose the file, and type a **Credit** line if the map is shared. Choose **Add**.
4. The Atlas shows the new map. Scroll to zoom and drag to look around.

To use a better export later, click **Edit Map** and choose the new picture: the pins keep their places.

### Placing its records
<!-- help: guide-atlas-place; gui -->

1. Click **Place on Map**, and choose a covenant, neighbour or creature.
2. Click where it is on the map. Its pin appears there.
3. Drag a pin to move it, or right-click it to make it secret or take it off the map.

If the map has a scale bar, click **Set Scale**, click the bar's two ends and type its length: Measure then shows distances, and the Travel calculator fills in its miles.

Laboratories, and anything else that sits in a place, need no pins of their own: each shows at the pin of its covenant or place. Before showing the map to your players, turn on [Player view](help:player-view) with the eye in the title bar.

**See also:** [The Atlas](help:saga-atlas), [Pins](help:atlas-pins)

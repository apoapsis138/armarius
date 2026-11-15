# The Atlas
<!-- help: saga-atlas; gui -->

The Atlas is a chapter of the saga's page, on the desktop only. It
holds the saga's maps, each with a pin for the covenants, places,
towns, lords and creatures on it. Pick a map from the list at the top
right. The chapter opens on the one shown last.

- **Scroll** over the map to zoom in and out, and **drag** it to look
  around. **Fit** shows the whole map again.
- **Hover** over a pin to see the record in the Inspector: its name,
  what kind it is and its summary. Where several records share a spot,
  the pin shows how many, and the Inspector lists them all.
- **Click** a pin to open its record's page. **Back**, its name in the
  trail, returns to the Atlas at the same map and place. Where several
  share the spot, a click lists them to choose from.
- **Show** chooses which kinds of record the map shows: covenants,
  laboratories, neighbours and places, creatures.
- **Player view** is for a screen your players can see across the
  table. Turn it on with the eye in the title bar (see
  [Player view](help:player-view)).
  - The map leaves off the secret pins, every record shown at one, and
    every record the players don't know of.
  - Pins can't be moved or changed.
  - A secret pin has a dashed ring, so it can be told apart without its
    colour.
  - A secret pin hides only itself, and an unknown record only itself.
    A known creature in an unknown grove still shows at the grove's pin,
    without the grove's name.

A record with no pin of its own on the map is shown at the pin of what
it sits in, however far out. A laboratory shows at its covenant's pin,
a covenant built in a forest at the forest's, and a regio's creature at
its place's. The Inspector says where ("at the Black Forest"). A mobile
covenant follows its stop in force, so its pin moves with it as the
seasons pass, even past a pin of its own.

**See also:** [Maps](help:atlas-maps), [Pins](help:atlas-pins), [Scale and distance](help:atlas-scale), [How to add a map and place its records](help:guide-atlas)

### Maps
<!-- help: atlas-maps; gui -->

A map is a picture of a region: a PNG, WebP or JPEG you drew or
exported, such as a map from a cartography program. It belongs to its
Tribunal, or to the saga when it's of a region with no Tribunal. A
Tribunal can have several maps, such as the whole Tribunal and a city
drawn larger. A record can have a pin on each.

- **New Map** adds one, and **Edit Map** changes the map on show.
  **Remove Map** takes it and its pins out of the saga, but its records
  stay.
- The picture is copied into the **maps** folder beside the saga files.
  Moving or deleting your own file later changes nothing.
- A map with no picture yet shows a **placeholder**. It's parchment with
  a grid lettered A to J along the top and numbered 1 to 10 down the
  side, a compass rose and the map's name.
  - Place your records on it roughly ("Durenmar is about G8").
  - When your map is drawn, Edit Map adds its picture. The pins stay
    where they were, ready to be dragged into place.
  - Give the placeholder the shape of the map to come, such as 3 by 2
    or the size in pixels you'll export at, so the pins land as near as
    they can (see [The map form](help:atlas-map-form)).
- A map whose picture is missing, such as a saga opened on another
  computer, shows the same placeholder in the picture's shape, with its
  pins still on it.
- A pin's place is kept as a share of the map's width and height. So a
  new export of the same map at another size keeps every pin where it
  was. When a new picture's proportions differ, the Atlas says so. Check
  the pins then.

### The map form
<!-- help: atlas-map-form; gui -->

- **Name**: the map's name, as the list shows it.
- **Tribunal**: the Tribunal it belongs to. Leave it blank for the
  saga's own map of a region with no Tribunal.
- **Picture**: the picture to show, chosen from your files. Delete
  clears it.
- **Placeholder width** and **Placeholder height**: the shape of the
  map to come, while there is no picture. It's 3 by 2 when left blank.
  Give both or neither.
- **Credit**: who drew it, and its licence, shown under the map.

### Pins
<!-- help: atlas-pins; gui -->

The pins belong to the saga. A Tribunal pack may bring its maps with a
pin for each of its covenants and places (see
[How to start a saga from a sourcebook](help:guide-book-packs)). You
add, move and take off pins of your own, and importing the pack again
never moves them.

- **[Place on Map](help:atlas-place)**: choose a record, then click
  where it is on the map. Esc stops.
- **Drag** a record's own pin to move it. A record shown at another's
  pin can't be dragged. Place it to give it a pin of its own.
- **Right-click** a pin to open its record, make it **Secret** or **take
  it off the map**.
- A pack's pin taken off stays off when the pack is imported again.
  Placing the record again brings it back.
- A record's page has **Show on Map** in its **Manage** chapter while it
  shows on a map. It opens the Atlas on that map, with its pin ringed.

### Scale and distance
<!-- help: atlas-scale; gui -->

A drawn map is to no projection, so the Atlas measures it by its own
scale bar.

- **Set Scale**: click one end of the map's scale bar, then the other.
  Then say how long the bar is, in **leagues** or **miles**.
  - A league is three miles (Grand Grimoire of Hermetic Spells p. 48;
    Transforming Mythic Europe p. 108). The Definitive Edition uses
    leagues for its spells' reach, but gives no length.
  - Set it again at any time. A new picture of the same map keeps it.
- **Measure**, once the map has a scale: click a pin or any point, then
  another. A dashed line joins them, with how far apart they are in
  leagues and miles, **in a straight line**. Roads and rivers wind, so
  the way itself is longer. Esc clears it.
- The line under the map says what the scale bar stands for.
- The [Travel](help:travel) calculator uses it. Choose From and To that
  are both on a map with a scale, and it fills in the miles as the crow
  flies.

### Place on Map
<!-- help: atlas-place; gui -->

The records that can be placed: every covenant, neighbour and creature
with no pin of its own on this map. Search by name, or filter by kind.
Once one is chosen, the line under the map says where to click.

# How to add a map and place its records
<!-- help: guide-atlas; gui -->

You've drawn or exported a map of your saga's region, and you'd like its covenants and places pinned where they stand.

### Adding the map
<!-- help: guide-atlas-map; gui -->

1. **Export the map.** Save it as a PNG, WebP or JPEG from your drawing or cartography program. A map with a scale bar is best. No map drawn yet? Leave Picture blank in step 3. The Atlas draws a placeholder to pin on now, and you can add the picture later.
2. **Start a new map.** Open the saga's page and its **The Atlas** chapter, and click **New Map**.
3. **Fill in the form.** Type the map's **Name** and choose its **Tribunal**, or leave it blank for a region with none. Click **Picture** and choose the file, and type a **Credit** line if the map is shared. Choose **Add**.
4. **Look around.** The Atlas shows the new map. Scroll to zoom and drag to look around.

To use a better export later, click **Edit Map** and choose the new picture. The pins keep their places.

### Placing its records
<!-- help: guide-atlas-place; gui -->

1. **Choose a record.** Click **Place on Map**, and choose a covenant, neighbour or creature.
2. **Pin it.** Click where it is on the map, and its pin appears there.
3. **Move or hide a pin.** Drag a pin to move it, or right-click it to make it secret or take it off the map.
4. **Set the scale.** If the map has a scale bar, click **Set Scale**, click the bar's two ends and type its length. Measure then shows distances, and the Travel calculator fills in its miles.

Laboratories, and anything else that sits in a place, need no pins of their own. Each shows at the pin of its covenant or place. Before showing the map to your players, turn on [Player view](help:player-view) with the eye in the title bar.

**See also:** [The Atlas](help:saga-atlas), [Pins](help:atlas-pins)

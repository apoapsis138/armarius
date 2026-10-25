"""Target sizes (DE p. 310; the Forms' base Individuals, pp. 314-372, as
the reference pages gather them, p. 546).

Every Form has a base Individual; each magnitude added for size multiplies
what the spell affects by ten. A Part is as big as an Individual, a Group
has the mass of ten Individuals, a Room holds a hundred, a Structure is ten
Rooms, and a Boundary is a hundred paces across whatever the Form. Size
doesn't matter to Intellego spells or Circle Targets, nor to Mentem and Vim
Individuals. The troupe's rough guess is fine (p. 310), so the app says
what a size reaches and leaves the magnitudes to the player.
"""

from __future__ import annotations

SOURCE = "Ars Magica Definitive Edition, Chapter 9: Targets and Sizes, pp. 310-311, 546"

#: Each Form's base Individual (DE p. 546), and for Aquam and Terram each
#: material's.
BASE_INDIVIDUALS: dict[str, str] = {
    "Animal": "a pony-sized animal, Size +1 or lower",
    "Aquam": "a pool of water five paces across and two deep (natural liquids "
    "two paces across, processed ones one pace, dangerous ones half a pace; "
    "a poison, a single dose)",
    "Auram": "a weather phenomenon within a standard Boundary",
    "Corpus": "an adult human, up to Size +1",
    "Herbam": "a plant one pace in each direction",
    "Ignem": "a large campfire, or the hearthfire of a great hall",
    "Imaginem": "an image, noise or the like of an adult human's size",
    "Terram": "ten cubic paces of sand, dirt, mud or clay; a cubic pace of "
    "stone; a cubic foot of base metal, a tenth of that of precious metal; "
    "a cubic inch of gemstone",
}
#: Forms whose Individual Targets have no size: a Group counts minds or
#: effects instead (DE p. 546).
NO_INDIVIDUAL_SIZE = {"Mentem": "minds", "Vim": "effects"}

#: What the base of each Target holds, in base Individuals of its Form.
TARGET_BASES: dict[str, str] = {
    "Individual": "one base Individual",
    "Part": "a part as big as one base Individual",
    "Group": "the mass of ten base Individuals",
    "Room": "a room holding a hundred base Individuals",
    "Structure": "ten such rooms",
    "Boundary": "the area of a circle a hundred paces across",
}


def _times(magnitudes: int) -> str:
    return "" if magnitudes <= 0 else f"{10**magnitudes:,} times "


def size_text(technique: str, form: str, target: str, magnitudes: int) -> str:
    """What a spell's Target reaches with `magnitudes` added for size, and
    its Form's base Individual; "" when the app can't say (a Target or Form
    it doesn't know)."""
    if technique == "Intellego" or target == "Circle":
        return "Size doesn't change the level of an Intellego spell or a Circle."
    if form in NO_INDIVIDUAL_SIZE and target == "Individual":
        return f"Size doesn't apply to a {form} Individual."
    base = TARGET_BASES.get(target)
    if base is None:
        return ""
    if form in NO_INDIVIDUAL_SIZE and target == "Group":
        return (
            f"A {form} Group's size is its number of {NO_INDIVIDUAL_SIZE[form]}: "
            f"each magnitude added, ten times as many."
        )
    reach = f"{_times(magnitudes)}{base}" if magnitudes > 0 else base
    individual = BASE_INDIVIDUALS.get(form)
    if magnitudes > 0:
        line = (
            f"{target}, with {magnitudes} extra magnitude"
            f"{'s' if magnitudes != 1 else ''} spent on size: up to {reach}."
        )
    else:
        line = f"{target} at its base size: {reach}; each magnitude for size, ten times it."
    if individual and target != "Boundary":
        line += f" A base Individual of {form} is {individual}."
    return line

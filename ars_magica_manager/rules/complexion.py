"""Complexion, the blend of the four humours in a person (Art & Academe,
Chapter Three: Medicine, The Human Body, pp. 37-41), under the Art &
Academe medicine saga option.

- **The four humours** (p. 38): blood (hot and moist, air, spring),
  choler (hot and dry, fire, summer), melancholy (cold and dry, earth,
  autumn) and phlegm (cold and moist, water, winter). Each gives its
  complexion: sanguine, choleric, melancholic and phlegmatic.
- **Compound complexions** (p. 40): most people show two, the principal
  one dominant, sometimes with a minor aspect of a third. The active
  quality (hot or cold) never features twice, so sanguine never mixes
  with choleric, nor melancholic with phlegmatic: four simple and eight
  compound complexions, each of the eight perhaps with a touch of a third.
- **Personality and body** (p. 40): each complexion has its stereotype
  traits and physical qualities; the book gives them as suggestions, not
  as rules, and the app shows them as such.
- **Seasons** (p. 41): each complexion waxes in its humour's season,
  whatever the person's own.
- **Diet** (p. 41): eat foods that counteract the principal humour, with
  the opposite qualities (a phlegmatic man eats heating and drying food).
- **Disease** (pp. 45-46): a disease is an excess of a humour; an
  environment ill-suited to one's temperament calls for a Disease
  Avoidance roll once or twice in the first season there. The book gives
  complexion no modifier to any roll: it is the troupe's guide.

The Definitive Edition has no complexion; nothing here changes its rules.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..models import Description

SOURCE = "Art & Academe, Chapter Three: Medicine, Complexion, pp. 40-41"


@dataclass(frozen=True)
class Humour:
    """A humour and the complexion it gives (A&A p. 38)."""

    complexion: str
    humour: str
    hot: bool
    moist: bool
    element: str
    season: str
    age: str
    #: Its physical qualities and stereotype traits (A&A p. 40).
    body: str
    traits: tuple[str, ...]

    @property
    def qualities(self) -> str:
        return f"{'hot' if self.hot else 'cold'} and {'moist' if self.moist else 'dry'}"


HUMOURS: tuple[Humour, ...] = (
    Humour(
        "sanguine",
        "blood",
        True,
        True,
        "air",
        "Spring",
        "childhood",
        "tall, fleshy, plentiful dark hair, a great full pulse, hot moist skin",
        ("Hopeful", "Friendly", "Amorous", "Restless", "Weak-Willed", "Gluttonous"),
    ),
    Humour(
        "choleric",
        "choler",
        True,
        False,
        "fire",
        "Summer",
        "adolescence",
        "tall, lean, plentiful curly red or blond hair, a swift strong pulse",
        ("Self-Reliant", "Courageous", "Decisive", "Proud", "Hot-Tempered", "Cruel"),
    ),
    Humour(
        "melancholic",
        "melancholy",
        False,
        False,
        "earth",
        "Autumn",
        "adulthood",
        "short, lean, sparse straight brown hair, a slow strong pulse",
        ("Caring", "Loyal", "Creative", "Just", "Pessimistic", "Vengeful"),
    ),
    Humour(
        "phlegmatic",
        "phlegm",
        False,
        True,
        "water",
        "Winter",
        "old age",
        "short, fat, sparse flaxen hair, a slow shallow pulse, cold moist skin",
        ("Calm", "Dependable", "Prudent", "Lazy", "Fearful", "Stubborn"),
    ),
)
BY_NAME = {h.complexion: h for h in HUMOURS}
NAMES: tuple[str, ...] = tuple(h.complexion for h in HUMOURS)

#: The foods that counteract each pair of qualities (A&A p. 41), by the
#: qualities they counteract.
FOODS: dict[tuple[bool, bool], str] = {
    (True, True): "cooling and drying foods (beef, mutton, lentils, olives)",
    (True, False): "cooling and moistening foods (milk, fish, apples, barley, ale)",
    (False, False): "heating and moistening foods (mead, fresh bread, chicken, figs)",
    (False, True): "heating and drying foods (venison, onions, leeks, garlic, wine)",
}


def mixes(first: str, second: str) -> bool:
    """Whether two complexions can blend: never the same, and never two of
    the same active quality (A&A p. 40)."""
    a, b = BY_NAME.get(first), BY_NAME.get(second)
    return a is not None and b is not None and a.hot != b.hot


def compounds() -> list[tuple[str, str]]:
    """The eight compound complexions as (principal, secondary)."""
    return [(a, b) for a in NAMES for b in NAMES if mixes(a, b)]


#: The complexion field's values: the four simple ones, then the eight
#: compounds written "principal-secondary".
CHOICES: tuple[str, ...] = (*NAMES, *(f"{a}-{b}" for a, b in compounds()))


def parts(complexion: str) -> tuple[str, ...]:
    """A complexion value's complexions, the principal first (() for none
    or a value the app doesn't know)."""
    if complexion not in CHOICES:
        return ()
    return tuple(complexion.split("-"))


def label(complexion: str) -> str:
    """ "Sanguine", "Sanguine, then melancholic" ("" for none)."""
    found = parts(complexion)
    if not found:
        return ""
    if len(found) == 1:
        return found[0].title()
    return f"{found[0].title()}, then {found[1]}"


def options() -> list[tuple[str, str]]:
    """The complexion field's (label, value) pairs."""
    return [(label(c), c) for c in CHOICES]


def problem(complexion: str, minor: str) -> str | None:
    """Why a minor aspect can't go with this complexion, or None: only a
    compound complexion takes one, and not one of its own two (A&A p. 40)."""
    if not minor:
        return None
    found = parts(complexion)
    if len(found) != 2:
        return "Only a compound complexion has a minor aspect of a third (A&A p. 40)."
    if minor in found or minor not in BY_NAME:
        return "The minor aspect is a third complexion, not one of its two (A&A p. 40)."
    return None


def principal(description: Description) -> Humour | None:
    found = parts(description.complexion)
    return BY_NAME[found[0]] if found else None


def waxes(description: Description, season: str) -> bool:
    """Whether the season is the principal complexion's own (A&A p. 41)."""
    found = principal(description)
    return found is not None and found.season == season


def diet(description: Description) -> str:
    """What the principal humour calls for at table ("" without one)."""
    found = principal(description)
    return FOODS[(found.hot, found.moist)] if found is not None else ""


def ill_suited(description: Description, humours: tuple[str, ...]) -> bool:
    """Whether a disease of these humours (its complexions' names) is an
    excess of the character's own principal humour (A&A pp. 45-46)."""
    found = principal(description)
    return found is not None and found.complexion in humours


def text(description: Description, season: str = "") -> str:
    """The Biographical Detail's line on the complexion ("" for none):
    the blend, its qualities, the season it waxes, the traits it suggests
    and the diet that keeps it."""
    found = principal(description)
    if found is None:
        return ""
    words = label(description.complexion)
    if description.complexion_minor:
        words += f", a touch {description.complexion_minor}"
    line = (
        f"{words} ({found.qualities}, {found.humour}); waxes in {found.season}"
        + (" (now)" if season and found.season == season else "")
        + f"; suggests {', '.join(found.traits[:4])}; eats {diet(description)}"
        " (A&A pp. 40-41)"
    )
    return line

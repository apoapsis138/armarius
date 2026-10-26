"""More's The Hunt and Area Lore, on a manor or on a journey: the forms,
their inspectors, and what each writes to the Diary -- no UI in here.
The rules and their pages are rules/hunting.py's (Lords of Men pp. 48-60,
City & Guild pp. 82-83).

The Hunt hunts with hounds (the quest, the assembly and the chase, with
its relay and Terrain Bonus) or flies a hawk; Hunt rolls it all, writes
the hunt in the Diary of each character named and of the manor's lord or
covenant, and takes the Long-Term Fatigue the chase cost the hunters. On
a journey the party must first find a hunting spot with Area Lore (C&G
p. 83, Ease Factor 6), and game in a lord's chase, warren or forest is
poached (LoM p. 48).

Area Lore rolls a character's Intelligence + Area Lore against a line
of C&G p. 83's table and writes what he found (or didn't) in his Diary.
"""

from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from .. import bestiary_book, diaries, manors
from ..commands import Command, Form, Refuse, notes
from ..form_spec import DialogField, ListEditor
from ..markup import BULLET, escape, plural
from ..models import Character, Covenant, Neighbour, Saga
from ..rules import harm
from ..rules import hunting as hr
from ..sections import MANORS_SECTION
from . import travel as travel_forms

HUNT_TITLE = "The Hunt"
AREA_LORE_TITLE = "Area Lore"
HOUNDS = "hounds"
HAWKING = "hawking"
KINDS = {
    HOUNDS: f"Hunting with hounds ({hr.LOM} pp. 51-53)",
    HAWKING: f"Hawking ({hr.LOM} pp. 57-58)",
}
#: A household huntsman without a sheet: his Hunt and Area Lore are typed,
#: his Characteristics taken as 0 and his Animal Handling as his Hunt.
HOUSEHOLD_HUNTSMAN = "The household's huntsman"
DEFAULT_HUNT = 5
DEFAULT_AREA_LORE = 3
DEFAULT_FALCONER = 5


@dataclass(frozen=True)
class Ground:
    """Where the hunt or the search is: a manor (its holder and the
    manor) or the road (the covenant on show, if any)."""

    saga: Saga
    holder: Neighbour | None = None
    manor: manors.Manor | None = None
    covenant: Covenant | None = None

    @property
    def on_journey(self) -> bool:
        return self.manor is None

    @property
    def where(self) -> str:
        return self.manor["name"] if self.manor is not None else "on the road"

    @property
    def place(self) -> str:
        """Where, to open a sentence: "At Hagen", "On the road"."""
        return f"At {self.where}" if self.manor is not None else "On the road"


# -- choosing characters --


def _people(saga: Saga, key: str, label: str, title: str, hint: str) -> DialogField:
    name = travel_forms.traveller_name(saga)
    return DialogField(
        key,
        label,
        "picker",
        [],
        display=lambda chosen: "; ".join(name(c) for c in chosen) or "(no one named)",
        items=ListEditor(name, travel_forms.choose_traveller(saga, title), title),
        hint=hint,
    )


def _characters(saga: Saga, ids: Any) -> list[Character]:
    """The characters named, each once."""
    found = (saga.character(i) for i in dict.fromkeys(ids or []))
    return [c for c in found if c is not None]


def _person_options(saga: Saga) -> list[tuple[str, str]]:
    return [
        (escape(c.name), c.id)
        for c in sorted(saga.characters, key=lambda c: c.name)
        if c.name and c.animal is None
    ]


def area_options(saga: Saga) -> list[tuple[str, str]]:
    """Every Area Lore a character of the saga holds, by name."""
    names = sorted({name for c in saga.characters for name, _ in hr.area_lores(c)})
    return [(escape(n), n) for n in names]


def _area_field(saga: Saga) -> DialogField:
    return DialogField(
        "area",
        "Area Lore of",
        "select",
        None,
        options=area_options(saga),
        allow_blank=True,
        placeholder="(each one's best)",
        hint="The region the ground lies in; each roller uses his score in it.",
    )


# -- the quarry --


def quarry_options(saga: Saga) -> list[tuple[str, str]]:
    """The quarry p. 54 names, by the Definitive Edition's beasts and p.
    58's hare, then the saga's own Bestiary (Beasts of Virtue and magical
    beasts are the finest quarry)."""
    found: list[tuple[str, str]] = []
    for key, _seasons, _words, _danger in hr.BOOK_QUARRY:
        book = bestiary_book.by_key(key)
        if book is not None:
            found.append((f"{book.name} (DE p. {book.page})", f"book:{key}"))
    found.append((f"{hr.HARE.name} ({hr.LOM} p. 58)", hr.HARE.key))
    found += [
        (f"{escape(c.name)} (the Bestiary)", f"saga:{c.id}")
        for c in sorted(saga.creatures, key=lambda c: c.name)
        if c.name
    ]
    return found


def quarry_of(saga: Saga, key: str | None) -> hr.Quarry | None:
    if not key:
        return None
    if key == hr.HARE.key:
        return hr.HARE
    kind, _, rest = key.partition(":")
    if kind == "book":
        for book_key, seasons, words, danger in hr.BOOK_QUARRY:
            book = bestiary_book.by_key(book_key)
            if book_key == rest and book is not None:
                return hr.creature_quarry(
                    bestiary_book.build(book),
                    key,
                    seasons=seasons,
                    source=f"DE p. {book.page}; {hr.LOM} p. 54",
                    words=words,
                    dangerous=danger,
                )
    if kind == "saga":
        creature = saga.creature(rest)
        if creature is not None:
            return hr.creature_quarry(
                creature,
                key,
                words="from the saga's Bestiary",
                dangerous=any(a.damage for a in creature.attacks),
            )
    return None


# -- The Hunt's form --


def _help(ground: Ground) -> str:
    """The help page: the Manors tab's, or the Travel calculator's."""
    return travel_forms.HELP_ID if ground.on_journey else MANORS_SECTION


def _hunting_with_hounds(values: dict[str, Any]) -> bool:
    return (values.get("kind") or HOUNDS) == HOUNDS


def _hawking(values: dict[str, Any]) -> bool:
    return values.get("kind") == HAWKING


def hunt_fields(ground: Ground) -> list[DialogField]:
    """The Hunt's form: hounds or hawk; for hounds the quarry, the pack,
    the hunters and huntsmen; for a hawk the hawker, bird and prey."""
    saga = ground.saga

    def no_huntsmen(values: dict[str, Any]) -> bool:
        return (
            not ground.on_journey
            and _hunting_with_hounds(values)
            and not values.get("huntsmen")
        )

    fields = [
        DialogField(
            "kind",
            "Hunt",
            "select",
            HOUNDS,
            options=[(label, key) for key, label in KINDS.items()],
            required=True,
        ),
        DialogField(
            "quarry",
            "Quarry",
            "select",
            f"book:{hr.BOOK_QUARRY[0][0]}",
            options=quarry_options(saga),
            hint=f"The hart is the object of most hunts ({hr.LOM} p. 54).",
            show_if=_hunting_with_hounds,
        ),
        DialogField(
            "native",
            "Native to the ground",
            "check",
            True,
            hint="A beast on its own ground has a Terrain Bonus of +6 (p. 53).",
            show_if=_hunting_with_hounds,
        ),
        DialogField(
            "hound",
            "The pack's best nose",
            "select",
            hr.RUNNING_DOG,
            options=[(h.name, k) for k, h in hr.HOUNDS.items()],
            required=True,
            hint=f"Its Perception + Hunt is the Pursuit Total ({hr.LOM} p. 50).",
            show_if=_hunting_with_hounds,
        ),
        _people(
            saga,
            "hunters",
            "Hunters, who ride",
            "Who Rides",
            "They read the droppings, ride with the hounds and lose Long-Term "
            "Fatigue; each hunter's Diary records the hunt.",
        ),
        _people(
            saga,
            "huntsmen",
            "Huntsmen",
            "Huntsmen",
            "They quest with lymers before dawn and lay the relay"
            + ("; on the road, the hunters do." if ground.on_journey else "."),
        ),
        DialogField(
            "huntsman_hunt",
            "Household huntsman: Hunt",
            "int",
            DEFAULT_HUNT,
            hint="With no huntsman named: his Characteristics taken as 0, his "
            "Animal Handling as his Hunt.",
            show_if=no_huntsmen,
        ),
        DialogField(
            "huntsman_lore",
            "Household huntsman: Area Lore",
            "int",
            DEFAULT_AREA_LORE,
            show_if=no_huntsmen,
        ),
        _area_field(saga),
        DialogField(
            "relay",
            "Lay a relay",
            "check",
            True,
            hint="Fresh couples along the quarry's path (p. 52).",
            show_if=_hunting_with_hounds,
        ),
        DialogField(
            "hours",
            "Hours of daylight",
            "int",
            hr.DAYLIGHT.get(saga.current_season, 12),
            hint="Darkness ends the chase (p. 52).",
            show_if=_hunting_with_hounds,
        ),
        DialogField(
            "hawker",
            "Hawker",
            "select",
            None,
            options=_person_options(saga),
            allow_blank=True,
            placeholder="(the falconer, without a sheet)",
            show_if=_hawking,
        ),
        DialogField(
            "falconer",
            "Falconer's Presence + Animal Handling",
            "int",
            DEFAULT_FALCONER,
            show_if=lambda v: _hawking(v) and not v.get("hawker"),
        ),
        DialogField(
            "bird",
            "Bird",
            "select",
            "gyrfalcon",
            options=[(b.name, k) for k, b in hr.BIRDS.items()],
            required=True,
            show_if=_hawking,
        ),
        DialogField(
            "prey",
            "Prey",
            "select",
            "partridge",
            options=[(p.name, k) for k, p in hr.PREY.items()],
            required=True,
            show_if=_hawking,
        ),
        DialogField(
            "loyal",
            "The bird's Loyal",
            "int",
            0,
            hint="A tamed bird is Loyal +0, raised a season at a time to +3 "
            f"({hr.LOM} p. 51).",
            show_if=_hawking,
        ),
        DialogField(
            "trained",
            "Trained to this prey",
            "check",
            False,
            show_if=lambda v: _hawking(v) and not _stoops(v),
        ),
    ]
    if ground.on_journey:
        fields.append(
            DialogField(
                "reserved",
                "In a lord's chase, warren or forest",
                "check",
                False,
                hint=f"Game elsewhere is anyone's; here it is poaching ({hr.LOM} "
                "pp. 48-49).",
            )
        )
    fields.append(DialogField("note", "Note", "text", ""))
    return fields


def _stoops(values: dict[str, Any]) -> bool:
    bird = hr.BIRDS.get(values.get("bird") or "")
    prey = hr.PREY.get(values.get("prey") or "")
    if bird is None or prey is None:
        return True
    return hr.will_stoop(bird, prey, trained=False)


def _int(value: Any, default: int = 0) -> int:
    return value if isinstance(value, int) else default


def hunters_of(ground: Ground, values: dict[str, Any]) -> list[hr.Hunter]:
    area = values.get("area") or None
    return [
        hr.hunter_of(c, area) for c in _characters(ground.saga, values.get("hunters"))
    ]


def huntsmen_of(ground: Ground, values: dict[str, Any]) -> list[hr.Huntsman]:
    area = values.get("area") or None
    named = _characters(ground.saga, values.get("huntsmen"))
    if not named and ground.on_journey:
        named = _characters(ground.saga, values.get("hunters"))
    if named or ground.on_journey:
        return [hr.huntsman_of(c, area) for c in named]
    hunt = _int(values.get("huntsman_hunt"), DEFAULT_HUNT)
    return [
        hr.Huntsman(
            HOUSEHOLD_HUNTSMAN,
            hunt=hunt,
            animal_handling=hunt,
            area_lore=_int(values.get("huntsman_lore"), DEFAULT_AREA_LORE),
        )
    ]


def _hawker(ground: Ground, values: dict[str, Any]) -> tuple[str, int]:
    character = ground.saga.character(values.get("hawker") or "")
    if character is not None:
        return character.name, hr.hawker_total(character)
    return "The falconer", _int(values.get("falconer"), DEFAULT_FALCONER)


def _establishment(ground: Ground, kind: str) -> manors.Establishment | None:
    if ground.holder is None:
        return None
    return next(
        (e for e in manors.establishments(ground.holder) if e.get("kind") == kind),
        None,
    )


def _season_line(ground: Ground, quarry: hr.Quarry) -> str:
    season = ground.saga.current_season
    if quarry.in_season(season):
        return ""
    return (
        f"[$text-error]Out of season: the {quarry.name.lower()} is hunted in "
        f"{' and '.join(s.lower() for s in quarry.seasons)}[/] [dim]({hr.LOM} "
        "p. 54)[/]"
    )


def _ground_lines(ground: Ground, values: dict[str, Any]) -> list[str]:
    """The manor's kennels, mews and hunting rights, or the journey's
    hunting spot and poaching."""
    lines: list[str] = []
    if ground.on_journey:
        best = max(
            (
                c.characteristics.intelligence + hr.area_lore(c, values.get("area"))
                for c in _characters(
                    ground.saga,
                    [*(values.get("hunters") or []), *(values.get("huntsmen") or [])],
                )
            ),
            default=None,
        )
        need = (
            f"the best of the party rolls {best:+d} + a simple die"
            if best is not None
            else "name who hunts"
        )
        lines.append(
            f"First find a hunting spot: Intelligence + Area Lore against "
            f"[b]{hr.FREE_GOODS.ease}[/]; {need} [dim]({hr.CG} p. 83)[/]."
        )
        if values.get("reserved"):
            lines.append(
                "[$text-error]Poaching in a lord's reserve: fiercely punished "
                f"when caught[/] [dim]({hr.LOM} p. 49)[/]"
            )
        return lines
    kind = "Mews" if _hawking(values) else "Kennels"
    held = _establishment(ground, kind)
    if held is None:
        wanted = "a mews for its birds" if kind == "Mews" else hr.LEAST_PACK
        lines.append(
            f"[dim]No {kind.lower()} on this holding's list: a hunt needs "
            f"{wanted} ({hr.LOM} p. 60).[/]"
        )
    else:
        lines.append(
            f"[dim]{kind}: {manors.quality_now(held)}, {_int(held.get('animals'))} "
            f"{manors.ANIMALS[kind]}.[/]"
        )
    if ground.holder is not None and not manors.is_covenant(ground.holder):
        rights = manors.household(ground.holder).get("hunting", "")
        if rights:
            lines.append(f"[dim]Hunting rights: {escape(rights)}.[/]")
    return lines


def _hounds_live(ground: Ground, values: dict[str, Any]) -> list[str]:
    quarry = quarry_of(ground.saga, values.get("quarry"))
    hound = hr.HOUNDS.get(values.get("hound") or "", hr.HOUNDS[hr.RUNNING_DOG])
    if quarry is None:
        return ["[$text-error]Choose the quarry.[/]"]
    terrain = hr.TERRAIN_BONUS if values.get("native", True) else 0
    lines = [
        f"[b]{escape(quarry.name)}[/]: [dim]{escape(quarry.words)} "
        f"({escape(quarry.source)})[/]",
    ]
    season = _season_line(ground, quarry)
    if season:
        lines.append(season)
    men = huntsmen_of(ground, values)
    quest = "; ".join(
        f"{escape(m.name)} tracks at {m.perception + min(m.hunt, hr.LYMER_HUNT):+d}, "
        f"quiets at {m.presence + m.animal_handling:+d}, judges at "
        f"{m.intelligence + m.hunt:+d}"
        for m in men
    )
    lines.append(
        f"The quest, each + a simple die against [b]{hr.TRACK_EASE}[/]: {quest} "
        f"[dim]({hr.LOM} p. 52)[/]"
    )
    lines.append(
        f"The chase, an hour a round: Pursuit [b]{hound.pursuit:+d}[/] [dim]"
        f"({escape(hound.name)}: Perception {hound.perception:+d} + Hunt "
        f"{hound.hunt} + {hound.hunt_bonus})[/] against Evasion [b]"
        f"{quarry.evasion + terrain:+d}[/] [dim](Dexterity {quarry.dexterity:+d} + "
        f"Athletics {quarry.athletics} + Terrain {terrain:+d})[/], each + a stress "
        f"die; four rounds won either way end it, not necessarily in a row (a "
        f"tie counts for neither), or nightfall. [dim]A quarry or pack spent "
        f"past its last Fatigue level also ends it: the app's reading, the "
        f"book leaves it open ({hr.LOM} p. 52).[/]"
    )
    riders = hunters_of(ground, values)
    if riders:
        lines.append(
            f"Keeping up, Dexterity + Ride + a stress die against "
            f"[b]{hr.RIDE_EASE}[/]: "
            + ", ".join(f"{escape(h.name)} {h.dexterity + h.ride:+d}" for h in riders)
            + f"; every {hr.RIDE_STAMINA_EVERY} hours Stamina + Ride + a simple "
            f"die against {hr.RIDE_STAMINA_EASE} or a Long-Term Fatigue level."
        )
    else:
        lines.append("[dim]No hunter named: the hounds and huntsmen alone.[/]")
    if values.get("relay", True):
        lines.append(
            "The relay: Intelligence + Hunt + 6 + a stress die against the Evasion "
            "Total for fresh dogs, then Intelligence + Area Lore + a stress die "
            f"to cut the Terrain Bonus [dim]({hr.LOM} p. 53)[/]."
        )
    if quarry.dangerous:
        lines.append(
            "[dim]A dangerous beast at bay: fight out the kill as a melee "
            f"({hr.LOM} p. 53).[/]"
        )
    return lines


def _hawking_live(ground: Ground, values: dict[str, Any]) -> list[str]:
    who, total = _hawker(ground, values)
    bird = hr.BIRDS.get(values.get("bird") or "", hr.BIRDS["gyrfalcon"])
    prey = hr.PREY.get(values.get("prey") or "", hr.PREY["partridge"])
    lines = [
        f"[b]{escape(bird.name)}[/]: [dim]{escape(bird.words)} ({hr.LOM} p. 59)[/]",
        f"{escape(who)}: Presence + Animal Handling [b]{total:+d}[/] + a simple "
        f"die, read on the hawking table: 7 or more and the bird attacks "
        f"[dim]({hr.LOM} p. 58; the Gift's penalty included)[/].",
        f"[dim]At 21 or more it goes on attacking after the first strike; the "
        f"book sets no limit, and the app stops it on a kill or after "
        f"{hr.MOST_STRIKES} strikes, its own limit.[/]",
        f"Its Attack {bird.attack:+d} against the {prey.name.lower()}'s Defense "
        f"{prey.defense:+d}, Damage {bird.damage:+d} against Soak {prey.soak:+d}.",
    ]
    if not _stoops(values) and not values.get("trained"):
        lines.append(
            f"[$text-error]The {bird.name.lower()} will not stoop at prey of "
            f"Size {prey.size}[/] [dim]unless trained to it.[/]"
        )
    return lines


def hunt_live(ground: Ground) -> Callable[[dict[str, Any]], str]:
    def live(values: dict[str, Any]) -> str:
        lines = (
            _hawking_live(ground, values)
            if _hawking(values)
            else _hounds_live(ground, values)
        )
        lines += _ground_lines(ground, values)
        return "\n".join(lines)

    return live


def hunt_problem(ground: Ground) -> Callable[[dict[str, Any]], str | None]:
    def problem(values: dict[str, Any]) -> str | None:
        if _hunting_with_hounds(values):
            if quarry_of(ground.saga, values.get("quarry")) is None:
                return "Choose the quarry."
            if _int(values.get("hours"), 1) < 1:
                return "A chase needs an hour of daylight at least."
            if _int(values.get("huntsman_hunt"), 0) < 0:
                return "A Hunt score can't be below 0."
        if (
            ground.on_journey
            and not values.get("hunters")
            and not values.get("huntsmen")
            and not values.get("hawker")
        ):
            return "Name who hunts: the hunt is written in their Diaries."
        return None

    return problem


@dataclass
class Outcome:
    """What a hunt came to: its title, its lines, and each hunter's
    Long-Term Fatigue lost."""

    title: str
    lines: list[str] = field(default_factory=list)
    long_term: dict[str, int] = field(default_factory=dict)


def _find_spot(
    ground: Ground, values: dict[str, Any], rng: random.Random
) -> tuple[bool, str]:
    """On a journey: the party's best Intelligence + Area Lore finds a
    hunting spot (C&G p. 83)."""
    party = _characters(
        ground.saga, [*(values.get("hunters") or []), *(values.get("huntsmen") or [])]
    )
    hawker = ground.saga.character(values.get("hawker") or "")
    if hawker is not None:
        party.append(hawker)
    if not party:
        return True, ""
    area = values.get("area") or None
    best = max(
        party, key=lambda c: c.characteristics.intelligence + hr.area_lore(c, area)
    )
    roll = hr.area_lore_roll(
        best.characteristics.intelligence,
        hr.area_lore(best, area),
        hr.FREE_GOODS.ease,
        rng,
        saga=ground.saga,
    )
    if roll.succeeded:
        return True, f"{best.name} knows where game is to be had ({hr.said(roll)})."
    return False, f"{best.name} finds no hunting ground hereabouts ({hr.said(roll)})."


def hunt_outcome(ground: Ground, values: dict[str, Any], rng: random.Random) -> Outcome:
    """Roll the hunt: the hawk's flight, or the quest, the assembly and the
    chase."""
    if ground.on_journey:
        found, line = _find_spot(ground, values, rng)
        if not found:
            return Outcome("The Hunt: no game found", [line])
        lines = [line] if line else []
    else:
        lines = []
    if values.get("reserved"):
        lines.append("Poached in a lord's reserve.")
    if _hawking(values):
        return _fly(ground, values, rng, lines)
    return _ride(ground, values, rng, lines)


def _fly(
    ground: Ground, values: dict[str, Any], rng: random.Random, lines: list[str]
) -> Outcome:
    who, total = _hawker(ground, values)
    bird = hr.BIRDS.get(values.get("bird") or "", hr.BIRDS["gyrfalcon"])
    prey = hr.PREY.get(values.get("prey") or "", hr.PREY["partridge"])
    flown = hr.hawk(
        total,
        bird,
        prey,
        rng,
        loyal=_int(values.get("loyal")),
        trained=bool(values.get("trained")),
        saga=ground.saga,
    )
    lines.append(f"{who} flies the {bird.name.lower()} at a {prey.name.lower()}.")
    lines += flown.lines
    if flown.killed:
        result = f"a {prey.name.lower()} taken"
    elif flown.lost:
        result = f"the {bird.name.lower()} lost"
    else:
        result = "nothing taken"
    return Outcome(f"Hawking: {result}", lines)


def _ride(
    ground: Ground, values: dict[str, Any], rng: random.Random, lines: list[str]
) -> Outcome:
    quarry = quarry_of(ground.saga, values.get("quarry"))
    assert quarry is not None  # hunt_problem refuses a hunt without one
    hound = hr.HOUNDS.get(values.get("hound") or "", hr.HOUNDS[hr.RUNNING_DOG])
    hunters = hunters_of(ground, values)
    men = huntsmen_of(ground, values)
    quest = hr.quest(men, hunters, rng, ground.saga)
    lines += quest.lines
    name = quarry.name.lower()
    if not quest.found:
        lines.append("No fit beast is found: there is no chase today.")
        return Outcome(f"The Hunt: no {name} found", lines)
    done = hr.chase(
        hound,
        quarry,
        hunters,
        men if values.get("relay", True) else [],
        rng,
        native=bool(values.get("native", True)),
        hours=_int(values.get("hours"), 12),
        saga=ground.saga,
    )
    lines += done.lines
    if done.cornered:
        at_bay = [h.name for h in hr.still_riding(hunters, done)]
        lines.append(
            (
                f"{', '.join(at_bay)} close{'s' if len(at_bay) == 1 else ''} in for the kill"
                if at_bay
                else "The hunters come up at last for the kill"
            )
            + (
                ": a dangerous beast, best fought out as a melee."
                if quarry.dangerous
                else "; the beast is unmade, the hounds given the curee, and the "
                "meat carried to the larder."
            )
        )
    title = f"The Hunt: a {name} " + ("brought to bay" if done.cornered else "escapes")
    if done.long_term:
        lines.append(
            "Long-Term Fatigue: "
            + ", ".join(
                f"{who} {plural(n, 'level')}" for who, n in done.long_term.items()
            )
            + "."
        )
    return Outcome(title, lines, done.long_term)


def hunt(
    ground: Ground, values: dict[str, Any], rng: random.Random | None = None
) -> list[str]:
    """Roll the hunt and write it: each character's Diary, the manor's
    lord's or covenant's, and the hunters' Long-Term Fatigue."""
    saga = ground.saga
    done = hunt_outcome(ground, values, rng or random.Random())
    note = str(values.get("note") or "")
    text = f"{ground.place}: " + " ".join(done.lines) + (f" {note}" if note else "")
    people = _characters(
        saga, [*(values.get("hunters") or []), *(values.get("huntsmen") or [])]
    )
    hawker = saga.character(values.get("hawker") or "")
    if hawker is not None and _hawking(values):
        people.append(hawker)
    covenant = (
        manors.holder_covenant(saga, ground.holder)
        if ground.holder is not None
        else None
    )
    lord = [ground.holder] if ground.holder is not None and covenant is None else []
    diaries.write(
        saga.current_year,
        saga.current_season,
        done.title,
        text,
        characters=people,
        covenants=[covenant] if covenant is not None else [],
        neighbours=lord,
    )
    for character in people:
        for _ in range(done.long_term.get(character.name, 0)):
            if harm.lose_fatigue(character, long_term=True):
                break
    return notes(f"{done.title}.", *done.lines)


def _hunt_form(ground: Ground, rng: random.Random | None) -> Form:
    return Form(
        f"{HUNT_TITLE}: {escape(ground.where)}",
        lambda: hunt_fields(ground),
        lambda values: hunt(ground, values, rng),
        validate=hunt_problem(ground),
        live=hunt_live(ground),
        save_label="Hunt",
        help_id=_help(ground),
        inspector="The Hunt",
    )


def hunt_on_manor(
    saga: Saga, holder: Neighbour, index: int, rng: random.Random | None = None
) -> Command:
    """More's The Hunt on the chosen manor."""
    listed = manors.manor_list(holder)
    if index >= len(listed):
        return Refuse(HUNT_TITLE, "Choose a manor first.")
    covenant = manors.holder_covenant(saga, holder)
    return _hunt_form(Ground(saga, holder, listed[index], covenant), rng)


def hunt_on_journey(
    saga: Saga, covenant: Covenant | None = None, rng: random.Random | None = None
) -> Command:
    """More's The Hunt on Ahead: a hunt on the road."""
    if not any(c.animal is None for c in saga.characters):
        return Refuse(HUNT_TITLE, "The saga has no characters to hunt.")
    return _hunt_form(Ground(saga, covenant=covenant), rng)


# -- Area Lore's form --


def _sought_options() -> list[tuple[str, str]]:
    return [(f"{s.ease}+: {s.words}", s.key) for s in hr.SOUGHT] + [
        ("Something else, at an Ease Factor", hr.OTHER)
    ]


def lore_fields(ground: Ground) -> list[DialogField]:
    return [
        DialogField(
            "who",
            "Who asks",
            "select",
            None,
            options=_person_options(ground.saga),
            required=True,
        ),
        _area_field(ground.saga),
        DialogField(
            "sought",
            "Looking for",
            "select",
            hr.FREE_GOODS.key,
            options=_sought_options(),
            required=True,
            hint=f"The Area Lore Ease Factors ({hr.CG} p. 83).",
        ),
        DialogField(
            "ease",
            "Ease Factor",
            "int",
            9,
            show_if=lambda v: v.get("sought") == hr.OTHER,
        ),
        DialogField(
            "away",
            "He lives",
            "select",
            hr.AT_HOME,
            options=[(label, key) for key, label in hr.AWAY.items()],
            required=True,
            hint=f"Away from his own ground he subtracts 3 ({hr.CG} p. 82).",
        ),
        DialogField("what", "What exactly", "text", "", placeholder="a farrier"),
    ]


def _ease(values: dict[str, Any]) -> tuple[int, str]:
    key = values.get("sought") or hr.FREE_GOODS.key
    if key == hr.OTHER:
        return _int(values.get("ease"), 9), "something else"
    sought = hr.SOUGHT_BY_KEY.get(key, hr.FREE_GOODS)
    return sought.ease, sought.words


def _asker(ground: Ground, values: dict[str, Any]) -> Character | None:
    return ground.saga.character(values.get("who") or "")


def lore_live(ground: Ground) -> Callable[[dict[str, Any]], str]:
    def live(values: dict[str, Any]) -> str:
        ease, words = _ease(values)
        who = _asker(ground, values)
        if who is None:
            return f"[b]{escape(words)}[/]: Ease Factor [b]{ease}[/]. Choose who asks."
        area = values.get("area") or None
        score = hr.area_lore(who, area)
        away = hr.away_penalty(values.get("away") or hr.AT_HOME)
        total = who.characteristics.intelligence + score + away
        need = ease - total
        lines = [
            f"[b]{escape(words)}[/] {BULLET} Ease Factor [b]{ease}[/] [dim]({hr.CG} "
            "p. 83)[/]",
            f"{escape(who.name)}: Intelligence {who.characteristics.intelligence:+d} + "
            f"Area Lore {score}" + (f" {away:+d} away" if away else "") + f" = "
            f"[b]{total:+d}[/] + a simple die: "
            + (
                "certain"
                if need <= 1
                else f"{need} or more"
                if need <= 10
                else "beyond him"
            )
            + ".",
            f"[dim]He knows how to find it or whom to ask; Charm or Bargain win it "
            f"({hr.CG} p. 82). {escape(ground.place)}.[/]",
        ]
        return "\n".join(lines)

    return live


def lore_problem(values: dict[str, Any]) -> str | None:
    if not values.get("who"):
        return "Choose who asks."
    if values.get("sought") == hr.OTHER and _int(values.get("ease"), 0) < 0:
        return "An Ease Factor can't be below 0."
    return None


def seek(
    ground: Ground, values: dict[str, Any], rng: random.Random | None = None
) -> list[str]:
    """Roll Area Lore and write what came of it in the asker's Diary."""
    saga = ground.saga
    who = _asker(ground, values)
    assert who is not None  # lore_problem refuses a form without one
    ease, words = _ease(values)
    roll = hr.area_lore_roll(
        who.characteristics.intelligence,
        hr.area_lore(who, values.get("area") or None),
        ease,
        rng or random.Random(),
        where=values.get("away") or hr.AT_HOME,
        saga=saga,
    )
    what = str(values.get("what") or "") or words
    found = bool(roll.succeeded)
    text = (
        f"{ground.place}, looking for {what}: "
        + ("he knows where, or whom to ask" if found else "he doesn't know")
        + f" ({hr.said(roll)})."
    )
    diaries.write(
        saga.current_year,
        saga.current_season,
        AREA_LORE_TITLE + (": found" if found else ": not found"),
        text,
        characters=[who],
    )
    return notes(f"{who.name}: {text}")


def _lore_form(ground: Ground, rng: random.Random | None) -> Form:
    return Form(
        f"{AREA_LORE_TITLE}: {escape(ground.where)}",
        lambda: lore_fields(ground),
        lambda values: seek(ground, values, rng),
        validate=lore_problem,
        live=lore_live(ground),
        save_label="Roll",
        help_id=_help(ground),
        inspector="Area Lore",
    )


def area_lore_on_manor(
    saga: Saga, holder: Neighbour, index: int, rng: random.Random | None = None
) -> Command:
    """More's Area Lore on the chosen manor: seeking in its hinterland."""
    listed = manors.manor_list(holder)
    if index >= len(listed):
        return Refuse(AREA_LORE_TITLE, "Choose a manor first.")
    covenant = manors.holder_covenant(saga, holder)
    return _lore_form(Ground(saga, holder, listed[index], covenant), rng)


def area_lore_on_journey(
    saga: Saga, covenant: Covenant | None = None, rng: random.Random | None = None
) -> Command:
    """More's Area Lore on Ahead: seeking along the road."""
    if not any(c.animal is None for c in saga.characters):
        return Refuse(AREA_LORE_TITLE, "The saga has no characters to ask.")
    return _lore_form(Ground(saga, covenant=covenant), rng)

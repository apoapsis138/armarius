"""A Criamon magus's The Enigma tab and its forms -- no UI in here: the
path he walks (Change Path; More: Follow an Avenue), its five stations and
what the next avenue needs, and his stigmata (Add, Edit, Delete). The
rules and their pages are rules.criamon's (Houses of Hermes: Mystery Cults
pp. 50-51, 58-73).

Pattern: the avenues are the tradition catalog's Initiation Scripts, so
Follow an Avenue only plans an Initiation season (the Strategy the season
registry picks for "undergo_initiation"), and the season does the rest;
the stigmata are a selectable list + details panel, keyed by SectionOps."""

from __future__ import annotations

from typing import Any

from .. import catalog
from ..commands import Form, SectionOps, delete, notes
from ..form_spec import DialogField, pairs
from ..markup import escape, fit
from ..models import SEASONS, Character, Saga, SeasonPlan, Stigma
from ..models.criamon import GHOST_GUIDE, HOUSE_GUIDE, STIGMA_KINDS
from ..rules import criamon as cr
from ..rules import mysteries
from ..rules.season_work.initiation import ordeal_reduction
from ..seasons.plans import plan_for, set_plan
from ..sections import CRIAMON_PATH_SECTION, STIGMATA_SECTION
from .church import Entry

MC = "HoH:MC"
#: The help pages of the forms that have their own.
AVENUE_HELP = "follow-avenue"
PATH_HELP = "change-path"
UNDERGO = "undergo_initiation"

EMPTY_PANEL = "[dim]Choose a station or a stigma.[/]"


def ok(words: str) -> str:
    return f"[$text-success]{words}[/]"


def warn(words: str) -> str:
    return f"[$text-warning]{words}[/]"


def bad(words: str) -> str:
    return f"[$text-error]{words}[/]"


def _col(words: str, width: int) -> str:
    """A column of a row: `words` fitted short of `width`, escaped."""
    return escape(fit(words, width - 1)) + " "


def _when(season: str, year: int | None) -> str:
    return " ".join(str(part) for part in (season, year) if part)


def _vf_name(vf_id: str) -> str:
    found = catalog.load_virtue_flaw_catalog_by_id().get(vf_id)
    return found.name if found is not None else vf_id


# -- the path --


def guide_words(guide: cr.Guide | None) -> str:
    if guide is None:
        return warn("the one named is gone")
    if guide.house:
        return f"a guide the House provides: Pre + Lore {guide.total}"
    who = "a ghostly Primus" if guide.ghost else escape(guide.name)
    words = f"{who}: Pre {guide.presence:+d}, Lore {guide.lore} = {guide.total}"
    return warn(words + ", not of the House") if guide.outsider else words


def _lore_words(character: Character, path: cr.Path | None) -> str:
    lore = cr.cult_lore(character)
    found = cr.next_station(character, path)
    if found is None:
        return str(lore)
    needs = cr.lore_needed(found[0])
    words = f"{lore} ({needs} for the next station)"
    return words if lore >= needs else warn(words)


def path_facts(saga: Saga, character: Character) -> list[tuple[str, str]]:
    """The path's facts: (label, markup)."""
    path = cr.path_of(character)
    if path is None:
        where = "none yet (the Winding Path)"
        station = "—"
    else:
        where = path.name
        reached = cr.station_reached(character, path)
        station = f"{reached} of {len(path.stations)}"
        if reached:
            station += f": {path.stations[reached - 1].name}"
    flaws = ", ".join(_vf_name(vf) for vf in cr.path_flaws(character)) or "none yet"
    guide = cr.guide_of(saga, character, character.enigma.guide_id)
    return [
        ("Path", where),
        ("Station", station),
        ("Enigmatic Wisdom", str(cr.wisdom(character))),
        ("House Criamon Lore", _lore_words(character, path)),
        ("Flaws of the path", escape(flaws)),
        ("Guide", guide_words(guide)),
    ]


def _reductions(character: Character) -> list[tuple[str, int, int]]:
    """His past Ordeals as (size, Initiations since, reduction)."""
    if not mysteries.ordeals_count(character):
        return []
    return [
        (
            o.size,
            o.initiations_since,
            mysteries.ORDEAL_REDUCTIONS[o.size][o.initiations_since],
        )
        for o in character.ordeals
        if o.size in mysteries.ORDEAL_REDUCTIONS and o.initiations_since < 3
    ]


def target_words(character: Character) -> str:
    """The Target worked out: "21 − 3 (his first Initiation since a Minor
    Ordeal) = 18"."""
    reduction = ordeal_reduction(character)
    target = cr.target(reduction)
    if not reduction:
        return f"Target [b]{target}[/]"
    why = cr.reduction_words(_reductions(character))
    return f"Target {cr.STATION_TARGET} − {cr.STATION_TARGET - target} ({why}) = [b]{target}[/]"


def _components(station: cr.Station, extra: int = 0) -> str:
    parts = [f"{name} +{bonus}" for name, bonus in station.components]
    if extra:
        parts.append(f"his aptitude for the path (head binding) +{extra}")
    return ", ".join(parts)


def next_text(saga: Saga, character: Character) -> str:
    """The next avenue: its station, the Target against the guide and the
    Script, and what stands in the way."""
    path = cr.path_of(character)
    if path is None:
        return (
            "[$label]Next:[/] he walks no path yet: Change Path chooses one, "
            "or Follow an Avenue steps onto a path's first station."
        )
    if not path.stations:
        return (
            f"[$label]Next:[/] {path.title}'s stations aren't printed; the Primi "
            f"keep those of their old paths ({MC} pp. 58-59)."
        )
    found = cr.next_station(character, path)
    if found is None:
        return (
            f"[$label]Next:[/] none: he has reached the last station of {path.title}."
        )
    place, station = found
    guide = cr.guide_of(saga, character, character.enigma.guide_id)
    route = cr.avenue(character, path, place, guide, ordeal_reduction(character))
    extra = route.script - station.bonus
    lines = [
        f"[$label]Next:[/] {escape(station.avenue)}, to the Station of "
        f"{escape(station.name)} (a Major Virtue, {cr.STATION_TARGET}).",
    ]
    if guide is not None:
        lines.append(
            f"{target_words(character)}; guide {guide.total} + Script "
            f"{route.script} ({escape(_components(station, extra))}) = "
            f"[b]{route.total}[/]: "
            + (ok("enough") if route.enough else bad("short"))
            + "."
        )
    else:
        lines.append(f"{target_words(character)}; Script {route.script}.")
    lines += [bad(escape(problem)) for problem in route.problems]
    lines += [warn(escape(words)) for words in route.warnings]
    return "\n".join(lines)


def aside_text(character: Character) -> str:
    """The stations he holds on other paths, set aside, and the rule."""
    path = cr.path_of(character)
    aside = cr.set_aside(character, path)
    rule = (
        "[dim]One path at a time: a magus who steps onto another keeps only his "
        f"Enigmatic Wisdom; rejoining, he regains its stations ({MC} pp. 58-60).[/]"
    )
    if not aside:
        return rule
    named = ", ".join(f"{s.name} ({p.title})" for p, s in aside)
    return f"[$label]Set aside:[/] {escape(named)}.\n" + rule


def path_text(saga: Saga, character: Character) -> str:
    """The terminal's path section: the facts on two lines, the next
    avenue and the rule of one path at a time."""
    facts = path_facts(saga, character)
    line = "  ·  ".join
    lines = [
        line(f"[$label]{k}:[/] {v}" for k, v in facts[:3]),
        line(f"[$label]{k}:[/] {v}" for k, v in facts[3:]),
        "",
        next_text(saga, character),
        aside_text(character),
    ]
    if character.enigma.notes.strip():
        lines += ["", escape(character.enigma.notes.strip())]
    return "\n".join(lines)


def path_desk_text(saga: Saga, character: Character) -> str:
    """The desktop's words under the facts."""
    return next_text(saga, character) + "\n" + aside_text(character)


def path_title(character: Character) -> str:
    path = cr.path_of(character)
    return path.title if path is not None else "The Winding Path"


def path_fields(saga: Saga, character: Character) -> list[DialogField]:
    enigma = character.enigma
    return [
        DialogField(
            "path",
            "Path",
            "select",
            enigma.path,
            options=[
                ("As his stations show", ""),
                *[(p.title, p.key) for p in cr.paths_open_to(character)],
            ],
            hint="One path at a time: stepping onto another keeps only his "
            f"Enigmatic Wisdom of the old one's stations ({MC} p. 58). The "
            "Path of the Mirror is the Primus's alone (pp. 57, 59): it is "
            "offered when his Hermetic background names him the Primus.",
        ),
        DialogField(
            "guide",
            "Guide",
            "select",
            _guide_value(saga, character),
            options=guide_options(saga, character),
            required=True,
        ),
        DialogField(
            "primus_presence",
            "A ghostly Primus's Presence",
            "int",
            enigma.primus_presence,
            hint=f"The Presence he had in life; his Lore is {cr.GHOST_LORE} "
            f"({MC} p. 60).",
        ),
        DialogField(
            "aptitude",
            "Head bound in infancy (or a like modification) for",
            "select",
            enigma.aptitude_path,
            options=[
                ("No path", ""),
                *[(p.title, p.key) for p in cr.PATHS.values() if p.stations],
            ],
            hint=f"+{cr.HEAD_BINDING} to that path's first station only: a "
            "cone suits Seeming, a double-lobed skull the Body; castration, "
            f"broken bones or severed joints work alike ({MC} p. 51).",
        ),
        DialogField("notes", "Notes", "area", enigma.notes),
    ]


def _guide_value(saga: Saga, character: Character) -> str:
    """His guide as the Guide field shows it: the House's when none is
    named, or when the one named is gone."""
    chosen = character.enigma.guide_id or HOUSE_GUIDE
    known = {value for _, value in guide_options(saga, character)}
    return chosen if chosen in known else HOUSE_GUIDE


def guide_options(saga: Saga, character: Character) -> list[tuple[str, str]]:
    found = [
        (
            f"{c.name} (Pre {c.characteristics.presence:+d}, Lore {cr.cult_lore(c)}"
            + ("; not of the House" if not cr.is_criamon(c) else "")
            + ")",
            c.id,
        )
        for c in cr.guides(saga, character)
    ]
    return [
        (
            f"A guide the House provides (Presence + Lore {cr.ASSUMED_GUIDE})",
            HOUSE_GUIDE,
        ),
        *found,
        (
            f"A ghostly Primus at the Cave of Twisting Shadows (Lore {cr.GHOST_LORE})",
            GHOST_GUIDE,
        ),
    ]


def path_form(saga: Saga, character: Character) -> Form:
    """Change Path: the path, the guide, a ghostly Primus's Presence."""

    def apply(values: dict[str, Any]) -> None:
        enigma = character.enigma
        enigma.path = values.get("path") or ""
        enigma.guide_id = values.get("guide") or ""
        enigma.primus_presence = int(values.get("primus_presence") or 0)
        enigma.aptitude_path = values.get("aptitude") or ""
        enigma.notes = values.get("notes") or ""

    return Form(
        "Change Path",
        lambda: path_fields(saga, character),
        apply,
        help_id=PATH_HELP,
    )


def path_ops(saga: Saga, character: Character) -> SectionOps:
    return SectionOps(
        edit=lambda _row: path_form(saga, character),
        rows=lambda: [path_title(character)],
    )


# -- Follow an Avenue --


def avenue_options(character: Character) -> list[tuple[str, str]]:
    """The avenues he may follow: the next on his path, then the next on
    each other path (stepping onto it)."""
    current = cr.path_of(character)
    ordered = [current] if current is not None else []
    ordered += [p for p in cr.PATHS.values() if p is not current]
    found: list[tuple[str, str]] = []
    for path in ordered:
        nxt = cr.next_station(character, path)
        if nxt is None:
            continue
        place, station = nxt
        label = (
            f"{cr.NUMERALS[place - 1]}: {station.avenue.removeprefix('The ')} "
            f"({station.name})"
        )
        if path is not current:
            label += f", stepping onto {path.title}"
        found.append((label, cr.script_key(path, place)))
    return found


def _chosen(values: dict[str, Any]) -> tuple[cr.Path, int, cr.Station] | None:
    found = cr.station_of_script(values.get("station") or "")
    if found is None:
        return None
    path, place = found
    return path, place, path.stations[place - 1]


def avenue_fields(saga: Saga, character: Character) -> list[DialogField]:
    options = avenue_options(character)
    guide = _guide_value(saga, character)
    guides = guide_options(saga, character)

    def is_station(path: str, place: int) -> Any:
        def shown(values: dict[str, Any]) -> bool:
            found = _chosen(values)
            return found is not None and (found[0].key, found[1]) == (path, place)

        return shown

    return [
        DialogField(
            "station",
            "Avenue",
            "select",
            options[0][1] if options else None,
            options=options,
            required=True,
        ),
        DialogField("guide", "Guide", "select", guide, options=guides, required=True),
        DialogField(
            "talisman",
            "Lose his talisman in place of the special time and place",
            "check",
            False,
            hint="The same +3, not an added one (p. 64).",
            show_if=is_station("seeming", 3),
        ),
        DialogField(
            "season", "Season", "select", saga.current_season, options=pairs(SEASONS)
        ),
        DialogField("year", "Year", "int", saga.current_year),
    ]


def _guide_from(saga: Saga, character: Character, guide_id: str) -> cr.Guide | None:
    return cr.guide_of(saga, character, guide_id)


def _on_success(character: Character, station: cr.Station) -> str:
    parts = [f"the Station of {station.name} (Major)"]
    granted, lifted, _ = cr.station_gifts(character, station)
    parts += [_vf_name(vf.vf_id) for vf in granted]
    parts += [f"{_vf_name(vf.vf_id)} lifted to an ordinary Gift" for vf in lifted]
    if station.replaces is not None:
        old, new = station.replaces
        parts.append(f"{_vf_name(new)} (Major) replacing {_vf_name(old)}")
    parts += [_vf_name(vf) for vf, _ in station.gains]
    if station.by_hand:
        parts.append(station.by_hand)
    parts.append("a new stigma")
    return "On success: " + ", ".join(parts) + "."


def avenue_live(saga: Saga, character: Character) -> Any:
    """The inspector: the total against the Target, the Lore it needs,
    the avenue's story and what it brings."""

    def live(values: dict[str, Any]) -> str:
        found = _chosen(values)
        if found is None:
            return "[dim]He has reached every station he can.[/]"
        path, place, station = found
        guide = _guide_from(saga, character, values.get("guide") or "")
        route = cr.avenue(character, path, place, guide, ordeal_reduction(character))
        reduction = cr.STATION_TARGET - route.target
        why = cr.reduction_words(_reductions(character))
        lines = [
            f"Guide {guide.total if guide else 0} + Script {route.script} = "
            f"[b]{route.total}[/] against Target [b]{route.target}[/]"
            + (f" ({cr.STATION_TARGET}, −{reduction} for {why})" if reduction else "")
            + ": "
            + (ok("enough") if route.enough else bad("short")),
        ]
        if route.script > station.bonus:
            lines.append(
                f"His head was bound in infancy for {path.title}: "
                f"+{route.script - station.bonus} to its first station ({MC} p. 51)."
            )
        lines += [bad(escape(problem)) for problem in route.problems]
        lines += [warn(escape(words)) for words in route.warnings]
        lines.append(
            f"The avenue's story: {escape(station.story)} ({MC} p. {station.page}). "
            "Failing, he may try again; utter failure may bring a Twilight check."
        )
        if values.get("talisman"):
            lines.append(
                "He gives up his talisman in place of the special time and "
                "place: the same +3."
            )
        lines.append(escape(_on_success(character, station)))
        current = cr.path_of(character)
        if current is not None and current is not path:
            lines.append(
                warn(
                    f"He steps from {current.title} onto {path.title}: its "
                    "stations are set aside while he walks it."
                )
            )
        season, year = values.get("season") or "", values.get("year")
        if season and isinstance(year, int):
            planned = plan_for(saga, character, season, year)
            if planned is not None:
                lines.append(warn(f"This replaces his plan for {season} {year}."))
        lines.append(f"[dim]{MC} pp. 59-60, {station.page}; DE pp. 387-389.[/]")
        return "\n".join(lines)

    return live


def avenue_form(saga: Saga, character: Character) -> Form:
    """Follow an Avenue: plans the Initiation season that follows it."""

    def apply(values: dict[str, Any]) -> list[str]:
        found = _chosen(values)
        if found is None:
            return notes("Nothing planned: he has no avenue left to follow.")
        path, place, station = found
        guide = values.get("guide") or ""
        season = values.get("season") or saga.current_season
        year = int(values.get("year") or saga.current_year)
        set_plan(
            saga,
            SeasonPlan(
                character.id,
                year,
                season,
                UNDERGO,
                teacher_id=None
                if guide in (GHOST_GUIDE, HOUSE_GUIDE)
                else guide or None,
                hedge_script=cr.script_key(path, place),
                effect_id=station.virtue_id,
                details="He gives up his talisman in place of the special time "
                "and place (the same +3)."
                if values.get("talisman")
                else "",
            ),
        )
        enigma = character.enigma
        enigma.guide_id = guide
        if cr.path_of(character) is not path:
            enigma.path = path.key
        return notes(
            f"Planned for {season} {year}: {station.avenue}, to the Station of "
            f"{station.name} (Undergo an Initiation, on Planning)."
        )

    return Form(
        "Follow an Avenue",
        lambda: avenue_fields(saga, character),
        apply,
        live=avenue_live(saga, character),
        save_label="Plan",
        help_id=AVENUE_HELP,
        inspector="The Avenue",
    )


def avenue_step(saga: Saga, character: Character) -> Form:
    """More's Follow an Avenue."""
    return avenue_form(saga, character)


# -- the stations --

W_ST, W_GIVES, W_SCRIPT = 28, 22, 11


def _station_entry(
    character: Character, path: cr.Path, place: int, station: cr.Station
) -> Entry:
    have = station.virtue_id in cr.held(character)
    nxt = cr.next_station(character, path)
    numeral = cr.NUMERALS[place - 1]
    if have:
        when, tone = (
            cr.when_reached(character, station.virtue_id) or "reached",
            "text-success",
        )
    elif nxt is not None and nxt[0] == place:
        needs = cr.lore_needed(place)
        if cr.cult_lore(character) < needs:
            when, tone = f"needs Lore {needs}", "text-warning"
        else:
            when, tone = "next", "text-success"
    else:
        when, tone = "", "label"
    script = f"+{station.bonus} vs {station.printed_target}"
    ordeal = "; ".join(name for name, _ in station.components if "Ordeal" in name)
    coloured = f"[${tone}]{escape(when)}[/]" if when else ""
    gives = escape(station.gives) if when else f"[dim]{escape(station.gives)}[/]"
    return Entry(
        row=_col(f"{numeral} {station.name}", W_ST)
        + _col(station.gives, W_GIVES)
        + _col(script, W_SCRIPT)
        + coloured,
        title=station.name[0].upper() + station.name[1:],
        subtitle=f"Station {numeral} of {path.title}",
        rubric=numeral,
        meta=station.avenue,
        badge=(when, tone) if when else ("", "label"),
        body=gives,
        note=f"[i]{escape(ordeal)}.[/]" if ordeal else "",
        info="\n".join(
            [
                f"[b]{escape(station.name)}[/]  ·  {escape(station.avenue)}",
                escape(station.gives),
                f"[$label]Script:[/] {script}"
                + (f"  ·  [i]{escape(ordeal)}[/]" if ordeal else ""),
                *(
                    [
                        f"[$label]Target as printed:[/] {station.printed_target} "
                        f"({cr.STATION_TARGET} − {station.printed_reduction[1]}, "
                        f"{escape(station.printed_reduction[0])}; {MC} p. "
                        f"{station.page})."
                    ]
                    if station.printed_reduction
                    else []
                ),
                f"[$label]{escape(station.avenue)}:[/] {escape(station.story)} "
                f"({MC} p. {station.page}).",
                *([f"[$label]Reached:[/] {coloured}"] if have else []),
            ]
        ),
    )


def station_entries(character: Character) -> list[Entry]:
    path = cr.path_of(character)
    if path is None:
        return []
    return [
        _station_entry(character, path, place, station)
        for place, station in enumerate(path.stations, start=1)
    ]


def stations_title(character: Character) -> str:
    path = cr.path_of(character)
    if path is None or not path.stations:
        return "Stations"
    return f"Stations ({cr.station_reached(character, path)} of {len(path.stations)})"


def stations_header() -> str:
    return (
        "  "
        + fit("Station", W_ST)
        + fit("Gives", W_GIVES)
        + fit("Script", W_SCRIPT)
        + "Reached"
    )


def stations_empty(character: Character) -> str:
    path = cr.path_of(character)
    if path is not None and not path.stations:
        return f"[dim]{path.title}'s stations aren't printed ({MC} pp. 58-59).[/]"
    return (
        "[dim]On no path yet (the Winding Path): Change Path chooses one, or "
        "Follow an Avenue steps onto one.[/]"
    )


def station_rows(character: Character) -> list[tuple[int | None, str]]:
    entries = station_entries(character)
    if not entries:
        return [(None, stations_empty(character))]
    return [(n, e.row) for n, e in enumerate(entries)]


def station_info(character: Character, index: int | None) -> str:
    entries = station_entries(character)
    if index is None or not 0 <= index < len(entries):
        return EMPTY_PANEL
    return entries[index].info


# -- the stigmata --

W_WHERE, W_MARK, W_MARKS = 13, 26, 28

STIGMA_RULE = (
    "[dim]No mechanical cause and no removing it, even by magic; burned "
    "away, it grows back or takes the scar into its pattern. Another Criamon "
    "magus reads what it marks with Int + Enigmatic Wisdom against "
    f"{cr.READ_STIGMA_EASE} ({MC} pp. 50, 60).[/]"
)


def marks_words(stigma: Stigma) -> str:
    """What the stigma marks: its particular, or its kind."""
    if stigma.detail.strip():
        return stigma.detail.strip()
    label = STIGMA_KINDS.get(stigma.why, "")
    if label.startswith(("The ", "A ", "An ")):
        return label[0].lower() + label[1:]
    return label


def stigma_entry(stigma: Stigma) -> Entry:
    when = _when(stigma.season, stigma.year)
    why = marks_words(stigma)
    marks = f"{why}, {when}" if when else why
    where_when = ", ".join(part for part in (stigma.where, when) if part)
    return Entry(
        row=_col(stigma.where, W_WHERE)
        + _col(stigma.mark, W_MARK)
        + escape(fit(marks, W_MARKS).rstrip()),
        title=stigma.mark or "(a mark)",
        subtitle=" · ".join(part for part in (stigma.where, when) if part),
        rubric="∞" if stigma.why == "twilight" else "¶",
        meta=where_when,
        badge=(why, "label"),
        body="",
        note="",
        info="\n".join(
            [
                f"[b]{escape(stigma.mark)}[/]  ·  {escape(stigma.where)}",
                f"[$label]Marks:[/] {escape(marks)}.",
                "",
                STIGMA_RULE,
            ]
        ),
    )


def stigma_entries(character: Character) -> list[Entry]:
    return [stigma_entry(s) for s in character.enigma.stigmata]


def stigmata_title(character: Character) -> str:
    return f"Stigmata ({len(character.enigma.stigmata)})"


def stigmata_header() -> str:
    return "  " + fit("Where", W_WHERE) + fit("Mark", W_MARK) + "What it marks"


STIGMATA_EMPTY = (
    "[dim]None yet: the first usually appears when he answers the Riddle of "
    "the Magus (a adds one).[/]"
)


def stigma_rows(character: Character) -> list[tuple[int | None, str]]:
    found = character.enigma.stigmata
    if not found:
        return [(None, STIGMATA_EMPTY)]
    return [(n, stigma_entry(s).row) for n, s in enumerate(found)]


def stigma_info(character: Character, index: int | None) -> str:
    found = character.enigma.stigmata
    if index is None or not 0 <= index < len(found):
        return EMPTY_PANEL
    return stigma_entry(found[index]).info


def stigma_fields(existing: Stigma | None, saga: Saga) -> list[DialogField]:
    s = existing or Stigma("", "", season=saga.current_season)
    return [
        DialogField("where", "Where", "text", s.where, required=True),
        DialogField("mark", "The mark", "text", s.mark, required=True),
        DialogField(
            "why",
            "What it marks",
            "select",
            s.why,
            options=[(label, key) for key, label in STIGMA_KINDS.items()],
        ),
        DialogField(
            "detail",
            "Which",
            "text",
            s.detail,
            placeholder="(the Station of True Sight; Enigmatic Wisdom 4...)",
        ),
        DialogField(
            "season",
            "Season",
            "select",
            s.season or None,
            options=pairs(SEASONS),
            allow_blank=True,
        ),
        DialogField(
            "year", "Year", "optint", s.year if existing else saga.current_year
        ),
    ]


def _stigma_from(values: dict[str, Any], existing: Stigma | None) -> Stigma:
    made = existing or Stigma("", "")
    made.where = values.get("where") or ""
    made.mark = values.get("mark") or ""
    made.why = values.get("why") or "other"
    made.detail = values.get("detail") or ""
    made.season = values.get("season") or ""
    made.year = values.get("year")
    return made


def stigma_ops(saga: Saga, character: Character) -> SectionOps:
    """Add, Edit and Delete a stigma."""
    found = character.enigma.stigmata

    def form(index: int | None) -> Form:
        existing = found[index] if index is not None else None

        def apply(values: dict[str, Any]) -> None:
            made = _stigma_from(values, existing)
            if index is None:
                found.append(made)

        return Form(
            "Add Stigma" if index is None else "Edit Stigma",
            lambda: stigma_fields(existing, saga),
            apply,
            live=lambda _values: STIGMA_RULE,
            save_label="Add" if index is None else "Save",
            help_id=STIGMATA_SECTION,
        )

    return SectionOps(
        add=lambda: form(None),
        edit=form,
        remove=lambda index: delete(found, index, f"the stigma {found[index].mark}"),
        rows=lambda: [s.mark for s in found],
    )


# -- the tab as a whole --


def ops(saga: Saga, character: Character) -> dict[str, SectionOps]:
    """Each Enigma section's verbs."""
    return {
        CRIAMON_PATH_SECTION: path_ops(saga, character),
        STIGMATA_SECTION: stigma_ops(saga, character),
    }

"""More's An Artist's Career and A Scholar's Career: the rolls and
Reputation deeds Art & Academe gives artists and scholars between their
seasons, each written in the Diary -- no UI in here. An artist seeks or
keeps a sponsor, performs in trying conditions, or records a deed that
moves his Artist Reputation; a scholar seeks a place at a school, or
records a deed that moves his Academic Reputation. The rules and their
pages are rules.artistry's (pp. 123-135) and rules.scholarship's (pp.
79-89, 102-103)."""

from __future__ import annotations

import random
from typing import Any

from .. import diaries
from ..commands import Command, Form, Refuse, notes
from ..form_spec import DialogField
from ..markup import escape
from ..models import Character, Saga
from ..rules import artistry, dice, reputations, scholarship
from ..rules.season_work import city_guild

ARTIST_TITLE = "An Artist's Career"
ARTIST_HELP = "artist-career"
SCHOLAR_TITLE = "A Scholar's Career"
SCHOLAR_HELP = "scholar-career"
SPONSOR, PERFORM, KEEP, DEED = "sponsor", "perform", "keep", "deed"
ENTRY, ACADEMIC = "entry", "academic"


def artist_crafts(character: Character) -> list[str]:
    """The Crafts and Professions an artist could work in."""
    return [
        a.name
        for a in character.abilities
        if a.name.startswith(("Craft", "Profession"))
    ]


def _is(key: str, what: str, default: str) -> Any:
    return lambda values: (values.get(key) or default) == what


def _stress(saga: Saga, rng: random.Random) -> tuple[int, bool, str]:
    die = dice.stress_die(rng, 1, saga=saga)
    return die.value, die.botched, "a botch" if die.botched else str(die.value)


# -- An Artist's Career ----------------------------------------------------------


def artist_fields(character: Character) -> list[DialogField]:
    crafts = artist_crafts(character)
    sponsoring = _is("roll", SPONSOR, SPONSOR)
    deed = _is("roll", DEED, SPONSOR)
    return [
        DialogField(
            "roll",
            "What",
            "select",
            SPONSOR,
            options=[
                ("Seek a sponsor (a season)", SPONSOR),
                ("Perform in trying conditions", PERFORM),
                ("Keep a sponsor after a season off", KEEP),
                ("A deed for the Artist Reputation", DEED),
            ],
            required=True,
        ),
        DialogField(
            "craft",
            "Craft or Profession",
            "select",
            crafts[0] if crafts else None,
            options=[(escape(c), c) for c in crafts],
            required=True,
        ),
        DialogField(
            "kind",
            "Sponsorship",
            "select",
            "benefactor",
            options=[
                (f"{label} ({change:+d})", key)
                for key, (label, change) in artistry.SPONSOR_KINDS.items()
            ],
            show_if=sponsoring,
        ),
        DialogField(
            "status",
            "Sponsor's Social Virtue",
            "select",
            "free",
            options=[
                (f"{label} (+{change})", key)
                for key, (label, change) in artistry.SPONSOR_STATUS.items()
            ],
            show_if=sponsoring,
        ),
        DialogField(
            "sponsor_reputation",
            "Sponsor's Reputation",
            "int",
            0,
            show_if=sponsoring,
            hint="His highest business or social Reputation, added to the Ease "
            "Factor (A&A p. 131).",
        ),
        DialogField(
            "repeat",
            "Asking him again (+3)",
            "check",
            False,
            show_if=sponsoring,
        ),
        DialogField(
            "scout",
            "Pick him first (+3)",
            "check",
            False,
            show_if=sponsoring,
            hint="Perception + Folk Ken against 12 first: success adds +3; a "
            "botch picks the wrong man, who refuses.",
        ),
        DialogField(
            "quality",
            "The piece's Aesthetic Quality",
            "int",
            0,
            show_if=_is("roll", PERFORM, SPONSOR),
        ),
        DialogField(
            "characteristic",
            "Characteristic",
            "select",
            "communication",
            options=[("Communication", "communication"), ("Dexterity", "dexterity")],
            show_if=_is("roll", PERFORM, SPONSOR),
        ),
        DialogField(
            "deed",
            "Deed",
            "select",
            "craft_raised",
            options=[
                (
                    f"{label} ({xp:+d} xp)" if xp is not None else label,
                    key,
                )
                for key, (label, xp) in artistry.REPUTATION_EVENTS.items()
            ],
            show_if=deed,
        ),
        DialogField(
            "amount",
            "Its xp",
            "int",
            0,
            show_if=lambda v: (
                deed(v) and (v.get("deed") or "craft_raised") in artistry.TYPED_EVENTS
            ),
            hint="The Might's magnitude, the instructor's Reputation or the "
            "piece's Aesthetic Quality.",
        ),
    ]


def _artist_validate(values: dict[str, Any]) -> str | None:
    if int(values.get("sponsor_reputation") or 0) < 0:
        return "A sponsor's Reputation can't be below 0."
    if int(values.get("amount") or 0) < 0:
        return "Type the xp as a number of 0 or more: the deed says if it is lost."
    if int(values.get("quality") or 0) < 0:
        return "An Aesthetic Quality can't be below 0."
    return None


def artist_live(character: Character) -> Any:
    """The inspector: the roll, and what the Artist Reputation brings."""

    def inspect(values: dict[str, Any]) -> str:
        craft = str(values.get("craft") or "")
        rep = artistry.reputation_score(character, craft) if craft else 0
        trade = artistry.trade(craft) if craft else "Artist"
        lines = [
            f"[b]{escape(character.name)}[/]  [$label]{escape(trade)} Reputation {rep}[/]"
        ]
        what = values.get("roll") or SPONSOR
        if what == SPONSOR:
            kind = str(values.get("kind") or "benefactor")
            status = str(values.get("status") or "free")
            ease = artistry.sponsor_ease(
                kind, status, int(values.get("sponsor_reputation") or 0)
            )
            total = artistry.sponsor_total(character, craft)
            lines += [
                f"Communication + Bargain + Reputation [b]{total}[/] + a stress die "
                f"against [b]{ease}[/] [dim](A&A p. 131)[/]",
                f"At Reputation {rep} he needs {artistry.sponsor_needs(rep)}.",
                f"A character sponsoring him pays at least {artistry.sponsor_cost(rep)} "
                "Mythic Pound(s) a season's piece.",
            ]
        elif what == PERFORM:
            quality = int(values.get("quality") or 0)
            total = artistry.performance_total(
                character, craft, str(values.get("characteristic") or "")
            )
            lines.append(
                f"[b]{total}[/] + a stress die against [b]"
                f"{artistry.performance_ease(quality)}[/] (Aesthetic Quality / 2) "
                "[dim](A&A p. 125)[/]"
            )
        elif what == KEEP:
            lines.append(
                f"A simple die: {artistry.ABANDON_ON} or more and the sponsor "
                "abandons him [dim](A&A p. 131)[/]"
            )
        else:
            lines.append(
                "Gains and losses of Artist Reputation xp [dim](A&A p. 126)[/]"
                + ("; from 10 he loses none." if artistry.loses_nothing(rep) else "")
            )
        lines += [f"• {line}" for line in artistry.benefits(rep)]
        if rep >= artistry.LEGENDARY_AT and craft:
            legend = artistry.legendary(character, craft)
            lines.append(
                f"As a legendary artist: Might {legend.might}, {legend.powers} "
                f"powers of magnitude {legend.magnitude} at most [dim](A&A p. 129)[/]"
            )
        return "\n".join(lines)

    return inspect


def _add_reputation(character: Character, craft: str, xp: int) -> str:
    """Add (or take off) Artist Reputation xp; nothing is lost from 10."""
    rep = artistry.reputation_score(character, craft)
    if xp < 0 and artistry.loses_nothing(rep):
        return "At Artist Reputation 10 he loses no Reputation xp."
    city_guild.add_trade_reputation(character, artistry.trade(craft), xp)
    return (
        f"{xp:+d} xp in the {artistry.trade(craft)} Reputation: now "
        f"{artistry.reputation_score(character, craft)}."
    )


def _seek_sponsor(
    saga: Saga,
    character: Character,
    craft: str,
    values: dict[str, Any],
    rng: random.Random,
) -> list[str]:
    kind = str(values.get("kind") or "benefactor")
    status = str(values.get("status") or "free")
    ease = artistry.sponsor_ease(
        kind, status, int(values.get("sponsor_reputation") or 0)
    )
    bonus = artistry.SPONSOR_REPEAT_BONUS if values.get("repeat") else 0
    lines: list[str] = []
    if values.get("scout"):
        die, botched, shown = _stress(saga, rng)
        scout = artistry.scout_total(character) + die
        if botched:
            return [
                f"Picking the sponsor: {shown}. The wrong man: he refuses outright."
            ]
        if scout >= artistry.SCOUT_EASE:
            bonus += artistry.SPONSOR_SCOUT_BONUS
        lines.append(
            f"Picking the sponsor: {scout} against {artistry.SCOUT_EASE}"
            + (": +3." if scout >= artistry.SCOUT_EASE else ".")
        )
    die, botched, shown = _stress(saga, rng)
    total = artistry.sponsor_total(character, craft) + bonus + die
    label = artistry.SPONSOR_KINDS[kind][0]
    if botched:
        lines.append(f"{label}: {shown}. Refused for good: he must find another.")
    elif total >= ease:
        lines.append(
            f"{label}: {total} against {ease}: he becomes the sponsor's client."
        )
        gained = artistry.SPONSOR_XP.get(kind, 0)
        if gained:
            lines.append(_add_reputation(character, craft, gained))
    else:
        lines.append(
            f"{label}: {total} against {ease}: no agreement; asking again next "
            "season adds +3."
        )
    return lines


def apply_artist(
    saga: Saga, character: Character, values: dict[str, Any], rng: random.Random
) -> list[str]:
    craft = str(values.get("craft") or "")
    what = values.get("roll") or SPONSOR
    if what == SPONSOR:
        name, lines = (
            "Sought a sponsor",
            _seek_sponsor(saga, character, craft, values, rng),
        )
    elif what == PERFORM:
        quality = int(values.get("quality") or 0)
        ease = artistry.performance_ease(quality)
        die, botched, shown = _stress(saga, rng)
        total = (
            artistry.performance_total(
                character, craft, str(values.get("characteristic") or "")
            )
            + die
        )
        if botched:
            outcome = f"Die {shown}: something dire befalls the performers."
        elif total >= ease:
            outcome = f"{total} against {ease}: the performance succeeds."
        else:
            outcome = f"{total} against {ease}: acceptable but lacking."
        name, lines = "Performed", [outcome]
    elif what == KEEP:
        die = dice.simple_die(rng)
        kept = die < artistry.ABANDON_ON
        name = "A sponsor's patience"
        lines = [
            f"Simple die {die}: "
            + ("the sponsor keeps faith." if kept else "the sponsor abandons him.")
        ]
    else:
        key = str(values.get("deed") or "craft_raised")
        label, xp = artistry.REPUTATION_EVENTS[key]
        if xp is None:
            amount = int(values.get("amount") or 0)
            xp = -amount if artistry.TYPED_EVENTS[key] else amount
        name, lines = (
            f"Artist's deed: {label}",
            [label + ".", _add_reputation(character, craft, xp)],
        )
    diaries.write(
        saga.current_year,
        saga.current_season,
        name,
        " ".join([*lines, f"Rules: {artistry.SOURCE}."]),
        characters=[character],
    )
    return notes(*map(escape, lines), f"Written in {escape(character.name)}'s Diary.")


def artist_form(
    saga: Saga, character: Character | None, rng: random.Random | None = None
) -> Command:
    if character is None:
        return Refuse(ARTIST_TITLE, "Choose a character first.")
    if not artist_crafts(character):
        return Refuse(
            ARTIST_TITLE,
            f"{escape(character.name)} has no Craft or Profession to make art with.",
        )
    return Form(
        f"{ARTIST_TITLE}: {escape(character.name)}",
        lambda: artist_fields(character),
        lambda values: apply_artist(saga, character, values, rng or random.Random()),
        validate=_artist_validate,
        live=artist_live(character),
        save_label="Roll",
        help_id=ARTIST_HELP,
        inspector="The Artist",
    )


# -- A Scholar's Career ----------------------------------------------------------

#: The school a place is sought at, as the Limits of Education name it.
ENTRY_SCHOOL = {
    "rural_parish": "rural_parish",
    "urban_parish": "urban_parish",
    "cathedral": "cathedral",
    "monastic": "monastic",
    "urban_citizen": "municipal",
    "urban_foreigner": "municipal",
}
_ALL_PERSUADE = ("Bargain", "Charm", "Guile", "Intrigue")


def scholar_fields(character: Character) -> list[DialogField]:
    entry = _is("roll", ENTRY, ENTRY)
    academic = _is("roll", ACADEMIC, ENTRY)
    deeds = [
        *((f"{label} (+1 xp)", key) for key, label in scholarship.GOOD_DEEDS.items()),
        *(
            (f"{label} (Bad, {xp} xp)", key)
            for key, (label, xp) in scholarship.BAD_DEEDS.items()
        ),
    ]
    named = [r.name for r in character.reputations if reputations.is_academic(r)]
    return [
        DialogField(
            "roll",
            "What",
            "select",
            ENTRY,
            options=[
                ("Seek a place at a school", ENTRY),
                ("A deed for the Academic Reputation", ACADEMIC),
            ],
            required=True,
        ),
        DialogField(
            "school",
            "School",
            "select",
            "cathedral",
            options=[
                (f"{label} ({ease})", key)
                for key, (label, ease, _a, _b) in scholarship.ENTRY.items()
            ],
            show_if=entry,
        ),
        DialogField(
            "ability",
            "Ability",
            "select",
            "Charm",
            options=[(a, a) for a in _ALL_PERSUADE],
            show_if=entry,
            hint="Bargain, Charm or Guile (and Intrigue, but for a parish school): "
            "the parent's, for a child (A&A pp. 81-86).",
        ),
        DialogField(
            "gift",
            "A wealthy family's gift",
            "int",
            0,
            show_if=entry,
            hint="+1 to +3 for a valuable contribution.",
        ),
        DialogField(
            "deed",
            "Deed",
            "select",
            "tractatus",
            options=deeds,
            show_if=academic,
        ),
        DialogField(
            "reputation",
            "Reputation",
            "text",
            "",
            placeholder=", ".join(named) or "(blank: his highest, or a new one)",
            show_if=academic,
            hint="The Academic Reputation it goes to, by name; a new name starts one.",
        ),
        DialogField(
            "interfaith",
            "Against another faith (double)",
            "check",
            False,
            show_if=academic,
            hint="Disputing or writing against another faith (A&A p. 88).",
        ),
    ]


def _scholar_validate(values: dict[str, Any]) -> str | None:
    if (values.get("roll") or ENTRY) == ENTRY:
        school = str(values.get("school") or "cathedral")
        ability = str(values.get("ability") or "Charm")
        if ability not in scholarship.ENTRY[school][2]:
            return f"{scholarship.ENTRY[school][0]} isn't won with {ability}."
        if not 0 <= int(values.get("gift") or 0) <= scholarship.GIFT_BONUS_MAX:
            return "A gift adds +1 to +3 (0 for none)."
    return None


def scholar_live(character: Character) -> Any:
    def inspect(values: dict[str, Any]) -> str:
        good = scholarship.highest_good_academic(character)
        bad = scholarship.highest_bad_academic(character)
        lines = [
            f"[b]{escape(character.name)}[/]  [$label]Academic Reputation: Good "
            f"{good}, Bad {bad}[/]"
        ]
        if (values.get("roll") or ENTRY) == ENTRY:
            school = str(values.get("school") or "cathedral")
            label, ease, _a, takes_bad = scholarship.ENTRY[school]
            ability = str(values.get("ability") or "Charm")
            total = scholarship.entry_total(
                character, school, ability, int(values.get("gift") or 0)
            )
            lines.append(
                f"Presence + {escape(ability)}"
                + (" - highest Bad Reputation" if takes_bad else "")
                + f" [b]{total}[/] + a stress die against [b]{ease}[/] "
                "[dim](A&A pp. 81-86)[/]"
            )
            lines.append(
                f"{label} teaches "
                + "; ".join(scholarship.limit_lines(ENTRY_SCHOOL[school]))
                + " [dim](A&A p. 79)[/]"
            )
            least, most = scholarship.FEES[school]
            if most:
                fee = f"{least:g}" if least == most else f"{least:g} to {most:.2g}"
                lines.append(f"A year costs {fee} Mythic Pound(s).")
            if scholarship.EDUCATED not in {vf.vf_id for vf in character.virtues_flaws}:
                lines.append("A school's students have the Educated Virtue.")
        else:
            lines.append(
                "Hermetic Arts earn none; Good and Bad Reputations rise as Abilities "
                "[dim](A&A p. 103)[/]"
            )
        return "\n".join(lines)

    return inspect


def apply_scholar(
    saga: Saga, character: Character, values: dict[str, Any], rng: random.Random
) -> list[str]:
    if (values.get("roll") or ENTRY) == ENTRY:
        school = str(values.get("school") or "cathedral")
        label, ease, _a, _b = scholarship.ENTRY[school]
        ability = str(values.get("ability") or "Charm")
        die, botched, shown = _stress(saga, rng)
        total = (
            scholarship.entry_total(
                character, school, ability, int(values.get("gift") or 0)
            )
            + die
        )
        name = f"Sought a place: {label.lower()}"
        if botched:
            lines = [f"Die {shown}: this teacher will never take him."]
        elif total >= ease:
            gained = scholarship.add_academic_xp(character, 1)
            lines = [
                f"{total} against {ease}: accepted as a student.",
                f"1 xp in his {gained.name} Reputation (A&A p. 103).",
            ]
        else:
            lines = [f"{total} against {ease}: refused; he may try again next year."]
    else:
        key = str(values.get("deed") or "tractatus")
        multiple = scholarship.INTERFAITH_MULTIPLE if values.get("interfaith") else 1
        if key in scholarship.GOOD_DEEDS:
            label, xp = scholarship.GOOD_DEEDS[key], 1
        else:
            label, lost = scholarship.BAD_DEEDS[key]
            xp = -lost
        name = f"Academic deed: {label}"
        reputation = scholarship.add_academic_xp(
            character, xp * multiple, str(values.get("reputation") or "").strip()
        )
        lines = [
            f"{label}: {abs(xp * multiple)} xp toward the "
            f"{'Bad' if xp < 0 else 'Good'} Academic Reputation {reputation.name}, "
            f"now {abs(reputation.score)}."
        ]
    diaries.write(
        saga.current_year,
        saga.current_season,
        name,
        " ".join([*lines, f"Rules: {scholarship.SOURCE}."]),
        characters=[character],
    )
    return notes(*map(escape, lines), f"Written in {escape(character.name)}'s Diary.")


def scholar_form(
    saga: Saga, character: Character | None, rng: random.Random | None = None
) -> Command:
    if character is None:
        return Refuse(SCHOLAR_TITLE, "Choose a character first.")
    return Form(
        f"{SCHOLAR_TITLE}: {escape(character.name)}",
        lambda: scholar_fields(character),
        lambda values: apply_scholar(saga, character, values, rng or random.Random()),
        validate=_scholar_validate,
        live=scholar_live(character),
        save_label="Roll",
        help_id=SCHOLAR_HELP,
        inspector="The Scholar",
    )

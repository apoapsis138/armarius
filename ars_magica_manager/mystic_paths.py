"""The More actions of a holy life on a character: Mystic Path, Spiritual
Path and Monistic Revelation (The Church pp. 19-24), Invoke God's Aid
(Realms of Power: The Divine pp. 41-42), Font of Knowledge (DE p. 165;
Antagonists p. 109) and Commanding Aura (DE pp. 74, 420). Each is a form
with a live inspector, rolled or kept on saving -- no UI in here. The
rules are rules.mysticism's, rules.divine_state's, rules.gods_aid's and
rules.font_of_knowledge's.

What is kept: the path, a Spiritual Path and a monist's Revelations are
progress records (rules.divine_state, rules.mysticism); a Virtue gained,
a Vow, Poor or a Faith Point go on the sheet; every roll and choice is
written in the Diary."""

from __future__ import annotations

import random
from typing import Any

from . import catalog, diaries, sourcebooks
from .commands import Command, Form, Refuse, notes
from .form_spec import DialogField
from .markup import BULLET, escape
from .models import Character, Progress, Saga, VirtueFlawDef, VirtueFlawInstance
from .rules import creation_characteristics as cch
from .rules import derived, dice
from .rules import divine_state as ds
from .rules import font_of_knowledge as fok
from .rules import gods_aid as aid
from .rules import holy_influence as holy
from .rules import mysticism as my
from .rules import pilgrimage as pil
from .rules.theban_customs import pious

HELP_PATH = "mystic-path"
HELP_SPIRITUAL = "spiritual-path"
HELP_REVELATION = "monistic-revelation"
HELP_AID = "gods-aid"
HELP_FONT = "font-of-knowledge"
HELP_AURA = "commanding-aura"


def _books(saga: Saga) -> frozenset[str] | None:
    return sourcebooks.saga_books(saga)


def the_church(saga: Saga) -> bool:
    return sourcebooks.in_play(my.BOOK, _books(saga))


def rop_divine(saga: Saga) -> bool:
    return sourcebooks.in_play(aid.BOOK, _books(saga))


def _rng(rng: random.Random | None) -> random.Random:
    return rng or random.Random()


def _number(value: Any) -> int:
    return int(value) if value is not None else 0


def _bullets(lines: list[str]) -> str:
    return "\n".join(f"{BULLET} {escape(line)}" for line in lines)


def _catalog(saga: Saga) -> list[VirtueFlawDef]:
    books = _books(saga)
    return [
        d
        for d in catalog.load_virtue_flaw_catalog()
        if sourcebooks.in_play(d.source, books)
    ]


def _gain(saga: Saga, character: Character, vf_id: str) -> str:
    """Add a Virtue (its Supernatural Ability at 1, without the Gift's
    penalty): what was gained, in words."""
    entry = catalog.load_virtue_flaw_catalog_by_id()[vf_id]
    instance = VirtueFlawInstance(vf_id)
    character.virtues_flaws.append(instance)
    cch.apply_virtue(saga, character, instance)
    said = f"He gains {entry.name}."
    ability = pil.grant_ability(character, entry)
    if ability is not None:
        said += f" {ability.name} starts at {pil.GAINED_ABILITY_SCORE}."
    return said


def _has(character: Character, vf_id: str) -> bool:
    return any(vf.vf_id == vf_id for vf in character.virtues_flaws)


# -- Mystic Path --

PATH_TITLE = "Mystic Path"
NONE = "none"


def path_fields(character: Character) -> list[DialogField]:
    return [
        DialogField(
            "path",
            "His path",
            "select",
            my.path(character) or NONE,
            options=[
                ("No mystic path", NONE),
                ("Contemplative: the imitation of Christ", my.CONTEMPLATIVE),
                ("Monistic: the self lost in God", my.MONISTIC),
            ],
            required=True,
            hint="One at a time; both need a positive Pious trait and a tie "
            "to the Divine (The Church p. 21).",
        )
    ]


def _chosen(values: dict[str, Any]) -> str:
    chosen = str(values.get("path") or NONE)
    return "" if chosen == NONE else chosen


def path_problem(character: Character) -> Any:
    def problem(values: dict[str, Any]) -> str | None:
        chosen = _chosen(values)
        if chosen == my.path(character):
            return "That is his path already." if chosen else "He follows no path."
        if not chosen:
            return my.leave_problem(character)
        found = my.path_problems(character, chosen)
        return found[0] if found else None

    return problem


def path_lines(character: Character, values: dict[str, Any]) -> list[str]:
    chosen = _chosen(values)
    faith = character.background.true_faith_score
    found: list[str] = [f"Pious {pious(character):+d}."]
    ties = my.divine_ties(character)
    found.append(
        "Tied to the Divine by " + ", ".join(ties) + "."
        if ties
        else "Not tied to the Divine."
    )
    if chosen == my.CONTEMPLATIVE:
        found += [
            "Prayer on Christ's life and Passion, Mass and communion, and "
            "repentance of sin; no sinful trait (RoP: The Divine p. 40).",
            "Warping: the Divine Ascent at 2 Warping Points from one event, "
            "its form the Divine Form (TC p. 21).",
            "Revelations by Spiritual Paths: More's Spiritual Path, and the "
            "Spiritual path seasons (TC p. 22).",
        ]
    elif chosen == my.MONISTIC:
        holy_ = my.holy_abilities(character)
        found += [
            "Warping: the Divine Ascent at a single Warping Point, its form the "
            "Divine Gloom (TC p. 23).",
            "A season practising a Holy Ability gives his Concentration in "
            f"experience ({my.practice_xp(character, holy_[0]) if holy_ else 4}), "
            "not 4: type it as the practice's Source Quality.",
            "Revelations from his Ascents: More's Monistic Revelation (TC p. 24).",
        ]
    if ds.divine_form(character):
        found.append(
            f"Divine Form: Magic Resistance +{ds.form_resistance(character)}, Soak "
            f"+{ds.form_soak(character)}, Penetration +{ds.form_penetration(character)}; "
            f"an impious act {ds.impious_botch_dice(character)} more botch dice."
        )
    if ds.divine_gloom(character):
        found.append(
            "Divine Gloom: each Warping Point brings an experience point to holy "
            "Abilities and costs one from mundane ones."
        )
    gifts = my.faith_gifts(faith)
    if gifts:
        found += [f"{g} (TC p. 23)." for g in gifts]
    if faith >= my.HIGH_FAITH_AT and my.faith_point_bonus(faith) > 3:
        found.append(f"A Faith Point spent adds +{my.faith_point_bonus(faith)}.")
    if chosen:
        found += my.path_problems(character, chosen)
    return found


def mystic_path_form(saga: Saga, character: Character | None) -> Command:
    """More's Mystic Path: the path followed, or left, in the Diary."""
    if character is None:
        return Refuse(PATH_TITLE, "Choose a character first.")
    who = character

    def apply(values: dict[str, Any]) -> list[str]:
        chosen = _chosen(values)
        ds.set_path(who, chosen)
        line = (
            f"He follows {chosen.lower()}."
            if chosen
            else "He leaves the mystic's path."
        )
        diaries.write_ruled(saga, who, PATH_TITLE, line, my.SOURCE)
        return notes(escape(line))

    return Form(
        f"{PATH_TITLE}: {escape(who.name)}",
        lambda: path_fields(who),
        apply,
        validate=path_problem(who),
        live=lambda values: _bullets(path_lines(who, values)),
        help_id=HELP_PATH,
        inspector="The Path",
    )


# -- Spiritual Path --

SPIRIT_TITLE = "Spiritual Path"
BEGIN, COUNT, CLAIM = "begin", "count", "claim"


def _what(*whats: str) -> Any:
    return lambda values: (values.get("what") or BEGIN) in whats


def _kind_is(key: str) -> Any:
    return lambda values: (
        _what(BEGIN)(values) and (values.get("kind") or "minor_holy") == key
    )


def spiritual_fields(saga: Saga, character: Character) -> list[DialogField]:
    records = my.spiritual_paths(character)
    whats = [("Begin a path to a Revelation", BEGIN)]
    if records:
        whats += [
            ("A Quest Component done", COUNT),
            ("Claim the Revelation", CLAIM),
        ]
    defs = _catalog(saga)
    fields = [
        DialogField(
            "what",
            "What",
            "select",
            COUNT if records else BEGIN,
            options=whats,
            required=True,
        ),
        DialogField(
            "kind",
            "The Revelation",
            "select",
            "minor_holy",
            options=[
                (f"{r.label} (Path Total {r.total})", r.key)
                for r in my.REVELATIONS.values()
            ],
            show_if=_what(BEGIN),
        ),
    ]
    for key in my.REVELATIONS:
        fields.append(
            DialogField(
                f"virtue_{key}",
                "The Virtue revealed",
                "select",
                None,
                options=[
                    (escape(d.name), d.id) for d in my.revelations(character, defs, key)
                ],
                allow_blank=True,
                show_if=_kind_is(key),
                hint="Usually aligned with the Divine; never True Faith (TC p. 22).",
            )
        )
    if records:
        fields += [
            DialogField(
                "record",
                "The path",
                "select",
                records[0].name,
                options=[
                    (escape(f"{r.name} ({r.points} of {r.target})"), r.name)
                    for r in records
                ],
                show_if=_what(COUNT, CLAIM),
            ),
            DialogField(
                "component",
                "Quest Component",
                "select",
                my.STORY_COMPONENTS[0],
                options=[
                    (f"+{my.COMPONENTS[k].value}: {my.COMPONENTS[k].label}", k)
                    for k in my.STORY_COMPONENTS
                ],
                show_if=_what(COUNT),
                hint="A season's components are planned on This Season.",
            ),
            DialogField(
                "vow",
                "The vow",
                "text",
                "",
                placeholder="e.g. never to eat meat",
                show_if=lambda v: _what(COUNT)(v) and v.get("component") == "vow",
            ),
            DialogField(
                "cross_faith",
                "A Faith Point for taking the cross",
                "check",
                True,
                hint="Taking the cross gives one temporary Faith Point (TC p. 19).",
                show_if=lambda v: _what(COUNT)(v) and v.get("component") == "crusade",
            ),
        ]
    return fields


def _record(character: Character, values: dict[str, Any]) -> Progress | None:
    return my.find_path(character, str(values.get("record") or ""))


def _virtue(values: dict[str, Any]) -> VirtueFlawDef | None:
    key = str(values.get("kind") or "minor_holy")
    vf_id = values.get(f"virtue_{key}")
    return catalog.load_virtue_flaw_catalog_by_id().get(str(vf_id or ""))


def _revealed(record: Progress) -> VirtueFlawDef | None:
    """The Virtue a path is to: the catalog's of its name."""
    return next(
        (
            d
            for d in catalog.load_virtue_flaw_catalog()
            if d.type == "Virtue" and d.name == record.name
        ),
        None,
    )


def spiritual_problem(character: Character) -> Any:
    def problem(values: dict[str, Any]) -> str | None:
        what = values.get("what") or BEGIN
        if what == BEGIN:
            virtue = _virtue(values)
            return my.begin_problem(character, virtue.name if virtue else "")
        record = _record(character, values)
        if what == COUNT:
            key = str(values.get("component") or "")
            if key == "vow" and not str(values.get("vow") or "").strip():
                return "Say what he vows."
            return my.component_problem(character, record, key)
        found = my.claim_problem(record)
        if found is None and record is not None and _revealed(record) is None:
            return f"No Virtue is named {record.name}."
        return found

    return problem


def spiritual_lines(character: Character, values: dict[str, Any]) -> list[str]:
    what = values.get("what") or BEGIN
    if what == BEGIN:
        revelation = my.REVELATIONS[str(values.get("kind") or "minor_holy")]
        found = [
            f"Path Total {revelation.total}: Quest Components worth "
            f"{revelation.total} grant it; Pious isn't taken off (TC p. 22).",
            "+1 a season serving the poor or the Church, or of personal "
            "devotion; +3 a season preaching (once); +6 a minor pilgrimage, a "
            "Vow or a quest; +9 a season preaching to infidels, error "
            "revealed, wealth given as alms, or a year on crusade.",
        ]
        if revelation.holy:
            found.append(
                "A Supernatural Ability gained so starts at 1, with no penalty "
                "for his other Supernatural Abilities or Arts."
            )
        return found
    record = _record(character, values)
    if record is None:
        return ["Choose the path."]
    found = [f"{record.name}: {record.points} of {record.target}."]
    if what == COUNT:
        key = str(values.get("component") or "")
        component = my.COMPONENTS.get(key)
        if component is not None:
            after = record.points + component.value
            found.append(
                f"+{component.value}: {after} of {record.target}"
                + (", reached." if after >= record.target else ".")
            )
            if key == "vow":
                found.append("He takes the Minor Flaw Vow.")
            if key == "alms":
                found.append(
                    "He loses Wealthy."
                    if _has(character, my.WEALTHY)
                    else "He takes the Poor Flaw: holy poverty."
                )
            if key == "crusade":
                found.append(
                    "He finds the money for his travel and keep; the troupe may "
                    "lift a Social Status Flaw (TC p. 19)."
                )
    else:
        found.append(my.claim_problem(record) or "Reached: the Revelation is his.")
    return found


def apply_spiritual(
    saga: Saga, character: Character, values: dict[str, Any]
) -> list[str]:
    what = values.get("what") or BEGIN
    if what == BEGIN:
        virtue = _virtue(values)
        if virtue is None:
            raise LookupError("That Virtue is no longer in the catalog.")
        key = str(values.get("kind") or "minor_holy")
        record = my.begin(character, virtue.name, key)
        heading = f"Spiritual Path begun: {record.name}"
        line = f"Path Total {record.target}: Quest Components must reach it."
    else:
        record = _record(character, values)
        if record is None:
            raise LookupError("That path is no longer under way.")
        if what == COUNT:
            key = str(values.get("component") or "")
            value = my.count(record, key)
            heading = f"Spiritual Path: {record.name}"
            parts = [
                f"{my.COMPONENTS[key].label}: +{value}, {record.points} of "
                f"{record.target}."
            ]
            parts += _component_effects(saga, character, key, values)
            if record.done:
                parts.append("Reached: claim the Revelation.")
            line = " ".join(parts)
        else:
            virtue = _revealed(record)
            if virtue is None:
                raise LookupError(f"No Virtue is named {record.name}.")
            line = _gain(saga, character, virtue.id)
            my.claim(record)
            heading = f"Revelation: {record.name}"
    diaries.write_ruled(saga, character, heading, line, my.SOURCE)
    return notes(escape(line), f"Written in {escape(character.name)}'s Diary.")


def _component_effects(
    saga: Saga, character: Character, key: str, values: dict[str, Any]
) -> list[str]:
    if key == "vow":
        character.virtues_flaws.append(VirtueFlawInstance(my.VOW))
        return [f"He vows {str(values.get('vow') or '').strip()}: the Minor Flaw Vow."]
    if key == "alms":
        wealthy = next(
            (vf for vf in character.virtues_flaws if vf.vf_id == my.WEALTHY), None
        )
        if wealthy is not None:
            cch.unapply_virtue(saga, character, wealthy)
            character.virtues_flaws.remove(wealthy)
            return ["He loses Wealthy."]
        poor = VirtueFlawInstance(my.POOR)
        character.virtues_flaws.append(poor)
        cch.apply_virtue(saga, character, poor)
        return ["He takes the Poor Flaw."]
    if key == "crusade" and values.get("cross_faith"):
        character.background.faith_points += pil.CRUSADER_FAITH
        return [f"+{pil.CRUSADER_FAITH} Faith Point for taking the cross."]
    return []


def spiritual_path_form(saga: Saga, character: Character | None) -> Command:
    """More's Spiritual Path: a path begun, a Quest Component counted, or
    its Revelation claimed."""
    if character is None:
        return Refuse(SPIRIT_TITLE, "Choose a character first.")
    who = character
    return Form(
        f"{SPIRIT_TITLE}: {escape(who.name)}",
        lambda: spiritual_fields(saga, who),
        lambda values: apply_spiritual(saga, who, values),
        validate=spiritual_problem(who),
        live=lambda values: _bullets(spiritual_lines(who, values)),
        help_id=HELP_SPIRITUAL,
        inspector="The Path to the Revelation",
    )


# -- Monistic Revelation --

REVELATION_TITLE = "Monistic Revelation"


def revelation_fields(saga: Saga, character: Character) -> list[DialogField]:
    defs = _catalog(saga)

    def choices(size: int) -> list[tuple[str, str]]:
        return [
            (escape(d.name), d.id)
            for d in pil.gainable(character, defs, size)
            if d.id != my.TRUE_FAITH
        ]

    first = my.first_revelation(character)

    def virtue_shown(choice: str) -> Any:
        return lambda v: not first and v.get("choice") == choice

    return [
        DialogField(
            "points",
            "Warping Points the Ascent brought",
            "int",
            1,
            hint="Those that set it off and those from the roll's margin.",
        ),
        DialogField(
            "choice",
            "The Revelation brings",
            "select",
            my.KEEP_MUNDANE,
            options=[(label, key) for key, (label, _n) in my.INTEGRATIONS.items()],
            required=True,
        ),
        DialogField(
            "minor",
            "The Minor Virtue",
            "select",
            None,
            options=choices(pil.MINOR),
            allow_blank=True,
            show_if=virtue_shown(my.MINOR_VIRTUE),
        ),
        DialogField(
            "major",
            "The Major Virtue",
            "select",
            None,
            options=choices(pil.MAJOR),
            allow_blank=True,
            show_if=virtue_shown(my.MAJOR_VIRTUE),
        ),
        DialogField(
            "realm",
            "The realm",
            "select",
            next(
                (r for r in my.LORE_REALMS if r not in my.lore_realms(character)),
                my.LORE_REALMS[0],
            ),
            options=[(f"{r} Lore", r) for r in my.LORE_REALMS],
            show_if=lambda v: v.get("choice") == my.REALM_LORE,
        ),
    ]


def _choice(values: dict[str, Any]) -> str:
    return str(values.get("choice") or my.KEEP_MUNDANE)


def revelation_problem(character: Character) -> Any:
    def problem(values: dict[str, Any]) -> str | None:
        points = _number(values.get("points"))
        if points < 1:
            return "An Ascent brings at least 1 Warping Point."
        choice = _choice(values)
        found = my.integration_problem(
            character, choice, points, str(values.get("realm") or "")
        )
        if found:
            return found
        if not my.first_revelation(character):
            if choice == my.MINOR_VIRTUE and not values.get("minor"):
                return "Choose the Minor Virtue."
            if choice == my.MAJOR_VIRTUE and not values.get("major"):
                return "Choose the Major Virtue."
        return None

    return problem


def revelation_lines(character: Character, values: dict[str, Any]) -> list[str]:
    total = my.integration_total(character)
    against = character.aging.warping_score
    chance = aid.opposed_chance(total, against) * 100
    found = [
        f"Intelligence + Concentration {total:+d} + stress die, against Warping "
        f"Score {against} + stress die (no botch): {chance:.0f}% (TC p. 24).",
        "Failing, the Gloom comes as usual; succeeding, it comes, and with it "
        "what he chose.",
    ]
    choice = _choice(values)
    if choice in (my.MINOR_VIRTUE, my.MAJOR_VIRTUE) and my.first_revelation(character):
        found.append("His first Revelation is always Second Sight.")
    held = my.lore_realms(character)
    if held:
        found.append("Dominion Lore serves him for " + ", ".join(held) + " Lore.")
    problem = revelation_problem(character)(values)
    if problem:
        found.append(problem)
    return found


def apply_revelation(
    saga: Saga, character: Character, values: dict[str, Any], rng: random.Random
) -> list[str]:
    total = my.integration_total(character)
    against = character.aging.warping_score
    mine = dice.stress_die(rng, 1, saga=saga)
    theirs = dice.stress_die(rng, 0, saga=saga).value
    rolled = f"{total} + {'a botch' if mine.botched else mine.value} against {against} + {theirs}"
    if mine.botched or total + mine.value < against + theirs:
        line = f"{rolled}: no Revelation; the Divine Gloom comes as usual."
        diaries.write_ruled(saga, character, REVELATION_TITLE, line, my.SOURCE)
        return notes(escape(line))
    choice = _choice(values)
    if choice == my.KEEP_MUNDANE:
        what = "he loses no mundane experience to this Gloom."
    elif choice in (my.MINOR_VIRTUE, my.MAJOR_VIRTUE):
        vf_id = (
            my.SECOND_SIGHT
            if my.first_revelation(character)
            else str(values.get("minor" if choice == my.MINOR_VIRTUE else "major"))
        )
        what = _gain(saga, character, vf_id)
        my.note_revelation(
            character, catalog.load_virtue_flaw_catalog_by_id()[vf_id].name
        )
    else:
        realm = "Infernal" if choice == my.INFERNAL_LORE else str(values.get("realm"))
        my.note_revelation(character, f"{realm} Lore")
        what = f"his Dominion Lore serves for {realm} Lore in any roll."
    line = f"{rolled}: a Revelation: {what}"
    diaries.write_ruled(saga, character, REVELATION_TITLE, line, my.SOURCE)
    return notes(escape(line))


def monistic_revelation_form(
    saga: Saga, character: Character | None, rng: random.Random | None = None
) -> Command:
    """More's Monistic Revelation: the roll to integrate an Ascent's
    Revelation, and what it brings."""
    if character is None:
        return Refuse(REVELATION_TITLE, "Choose a character first.")
    who, chance = character, _rng(rng)
    return Form(
        f"{REVELATION_TITLE}: {escape(who.name)}",
        lambda: revelation_fields(saga, who),
        lambda values: apply_revelation(saga, who, values, chance),
        validate=revelation_problem(who),
        live=lambda values: _bullets(revelation_lines(who, values)),
        save_label="Roll",
        help_id=HELP_REVELATION,
        inspector="The Integration",
    )


# -- Invoke God's Aid --

AID_TITLE = "Invoke God's Aid"


def aid_fields(character: Character) -> list[DialogField]:
    return [
        DialogField(
            "aim",
            "What he asks God's aid in",
            "text",
            "",
            required=True,
            placeholder="e.g. the fight with the knight",
        ),
        DialogField(
            "group",
            "For his followers too",
            "check",
            False,
            hint="One with spiritual authority, for a few parishioners or an army.",
        ),
        DialogField(
            "ceremony",
            "Leading them with Ceremony",
            "check",
            False,
            show_if=lambda v: bool(v.get("group")),
        ),
        DialogField(
            "others",
            "The others' Communication + Dominion Lore",
            "int",
            0,
            show_if=lambda v: bool(v.get("group")) and bool(v.get("ceremony")),
        ),
        DialogField("war", "In battle", "check", False),
        DialogField(
            "foe",
            "Against",
            "select",
            aid.INFIDEL,
            options=[(label, key) for key, label in aid.FOES.items()],
            show_if=lambda v: bool(v.get("war")),
        ),
    ]


def _aid_total(character: Character, values: dict[str, Any]) -> int:
    ceremony = bool(values.get("group")) and bool(values.get("ceremony"))
    return aid.total(character, ceremony=ceremony, others=_number(values.get("others")))


def aid_problem(character: Character) -> Any:
    def problem(values: dict[str, Any]) -> str | None:
        if not str(values.get("aim") or "").strip():
            return "Say what he asks God's aid in."
        if found := aid.may_ask(character):
            return found
        group = bool(values.get("group"))
        if found := aid.group_problem(
            character, for_group=group, ceremony=group and bool(values.get("ceremony"))
        ):
            return found
        if _number(values.get("others")) < 0:
            return "The others' total can't be below 0."
        if values.get("war") and (found := aid.war_problem(str(values.get("foe")))):
            return found
        return None

    return problem


def aid_lines(character: Character, values: dict[str, Any]) -> list[str]:
    total = _aid_total(character, values)
    odds = ", ".join(f"+{b} {c * 100:.0f}%" for b, c in aid.chances(total))
    found = [
        f"Stress die + Communication + Dominion Lore{' + Ceremony' if values.get('ceremony') and values.get('group') else ''} "
        f"{total:+d}: 9 gives +1, 15 +2, 24 +3 ({odds}).",
        f"He spends a {aid.point(character)} Point. A 0 rolls {holy.AID_BOTCH_DICE} "
        "botch dice: divine disfavour until penance.",
        "The bonus adds to each roll in the scene made toward the aim, "
        "spellcasting too, until one fails or the scene ends (p. 41).",
    ]
    if values.get("group"):
        found.append("His followers gain the bonus, and so does he (p. 42).")
    if values.get("war"):
        found.append(
            "A Trained Group adds a member's bonus to its combat bonus, beyond "
            "three times the leader's Leadership; only the highest counts, lost "
            "when the group fails a roll or splits (p. 42)."
        )
    problem = aid_problem(character)(values)
    if problem:
        found.append(problem)
    return found


def apply_aid(
    saga: Saga, character: Character, values: dict[str, Any], rng: random.Random
) -> list[str]:
    total = _aid_total(character, values)
    spent = aid.point(character)
    if spent == "Faith":
        character.background.faith_points -= 1
    else:
        character.background.confidence_points -= 1
    rolled = dice.roll(rng, total, botch_dice=holy.AID_BOTCH_DICE, saga=saga)
    aim = str(values.get("aim") or "").strip()
    if rolled.die.botched:
        line = (
            f"A botch ({rolled.die.botches} zero(s)) asking God's aid in {aim}: "
            "divine disfavour, until penance."
        )
    else:
        bonus = aid.bonus(rolled.total)
        line = f"{total:+d} + {rolled.die.value} = {rolled.total}: " + (
            f"+{bonus} to his rolls toward {aim} this scene, until one fails."
            if bonus
            else f"short of 9: no aid in {aim}."
        )
    line += f" A {spent} Point spent."
    diaries.write_ruled(saga, character, "God's Aid", line, aid.SOURCE)
    return notes(escape(line))


def gods_aid_form(
    saga: Saga, character: Character | None, rng: random.Random | None = None
) -> Command:
    """More's Invoke God's Aid: the prayer's roll and its bonus, in the
    Diary."""
    if character is None:
        return Refuse(AID_TITLE, "Choose a character first.")
    who, chance = character, _rng(rng)
    return Form(
        f"{AID_TITLE}: {escape(who.name)}",
        lambda: aid_fields(who),
        lambda values: apply_aid(saga, who, values, chance),
        validate=aid_problem(who),
        live=lambda values: _bullets(aid_lines(who, values)),
        save_label="Pray",
        help_id=HELP_AID,
        inspector="The Prayer",
    )


# -- Font of Knowledge --

FONT_TITLE = "Font of Knowledge"


def font_fields() -> list[DialogField]:
    return [
        DialogField(
            "ability",
            "The untrained Ability",
            "text",
            "",
            required=True,
            placeholder="e.g. Magic Lore",
        ),
        DialogField(
            "uses",
            "Times drawn on today",
            "int",
            0,
            hint="Failures count too.",
        ),
    ]


def font_problem(character: Character) -> Any:
    def problem(values: dict[str, Any]) -> str | None:
        name = str(values.get("ability") or "").strip()
        if not name:
            return "Name the Ability."
        if not fok.untrained(character, name):
            return f"He has {name} already: the Font serves only untrained Abilities."
        if _number(values.get("uses")) < 0:
            return "The times today can't be below 0."
        return None

    return problem


def font_lines(character: Character, values: dict[str, Any]) -> list[str]:
    total = fok.total(character)
    ease = fok.ease(_number(values.get("uses")))
    chance = aid.stress_chance(total, ease) * 100
    found = [
        f"Intelligence + Font of Knowledge {total:+d} + stress die against {ease} "
        f"(6 + 3 a use today): {chance:.0f}% (DE p. 165).",
        f"Succeeding, he attempts the task as if he had the Ability at "
        f"{fok.AS_IF_SCORE}.",
    ]
    problem = font_problem(character)(values)
    if problem:
        found.append(problem)
    return found


def apply_font(
    saga: Saga, character: Character, values: dict[str, Any], rng: random.Random
) -> list[str]:
    name = str(values.get("ability") or "").strip()
    ease = fok.ease(_number(values.get("uses")))
    rolled = dice.roll(rng, fok.total(character), ease_factor=ease, saga=saga)
    shown = "a botch" if rolled.die.botched else str(rolled.die.value)
    if rolled.succeeded and not rolled.die.botched:
        line = f"{fok.total(character):+d} + {shown} against {ease}: he may use {name} at {fok.AS_IF_SCORE}."
    else:
        line = f"{fok.total(character):+d} + {shown} against {ease}: the Font is silent on {name}."
    diaries.write_ruled(saga, character, FONT_TITLE, line, fok.SOURCE)
    return notes(escape(line))


def font_form(
    saga: Saga, character: Character | None, rng: random.Random | None = None
) -> Command:
    """More's Font of Knowledge: the roll to use an untrained Ability at 2."""
    if character is None:
        return Refuse(FONT_TITLE, "Choose a character first.")
    who, chance = character, _rng(rng)
    return Form(
        f"{FONT_TITLE}: {escape(who.name)}",
        font_fields,
        lambda values: apply_font(saga, who, values, chance),
        validate=font_problem(who),
        live=lambda values: _bullets(font_lines(who, values)),
        save_label="Roll",
        help_id=HELP_FONT,
        inspector="The Font",
    )


# -- Commanding Aura --

AURA_TITLE = "Commanding Aura"
COMMANDING_AURA = "vf_commanding_aura"


def has_aura(character: Character) -> bool:
    return bool(character.background.church_rank) or _has(character, COMMANDING_AURA)


def aura_fields(character: Character) -> list[DialogField]:
    return [
        DialogField(
            "withdrawn",
            "Withdrawn until penance",
            "check",
            ds.aura_withdrawn(character),
            hint="A legatus missus who delays or strays from his mission, or one "
            "God's will excommunicates (DE pp. 74, 420).",
        ),
        DialogField(
            "why",
            "Why",
            "text",
            "",
            show_if=lambda v: bool(v.get("withdrawn")),
        ),
    ]


def aura_lines(character: Character, values: dict[str, Any]) -> list[str]:
    rank = character.background.church_rank
    resistance = derived.OFFICE_RESISTANCE.get(rank, 0)
    found = [
        (
            f"{rank}: Magic Resistance {resistance}, Soak +{resistance // 5}, "
            "and an Aura of Rightful Authority to Voice range, Penetration 0."
            if rank
            else "No office set on Biographical Detail: the Virtue's Aura of "
            "Rightful Authority, to Voice range, Penetration 0."
        ),
        "A relic's Magic Resistance adds to the office's, not to Soak (DE p. 420).",
        "A legatus missus loses the aura when his mission is done (DE p. 74).",
    ]
    if values.get("withdrawn"):
        found.append("Withdrawn: no Magic Resistance, Soak or aura from it.")
    return found


def aura_problem(character: Character) -> Any:
    def problem(values: dict[str, Any]) -> str | None:
        if bool(values.get("withdrawn")) == ds.aura_withdrawn(character):
            return "Nothing changes."
        return None

    return problem


def commanding_aura_form(saga: Saga, character: Character | None) -> Command:
    """More's Commanding Aura: withdrawn until penance, or restored."""
    if character is None:
        return Refuse(AURA_TITLE, "Choose a character first.")
    who = character

    def apply(values: dict[str, Any]) -> list[str]:
        withdrawn = bool(values.get("withdrawn"))
        why = str(values.get("why") or "").strip()
        ds.set_aura_withdrawn(who, withdrawn, why)
        line = (
            "His Commanding Aura is withdrawn until penance"
            + (f": {why}." if why else ".")
            if withdrawn
            else "His penance done, his Commanding Aura returns."
        )
        diaries.write_ruled(saga, who, AURA_TITLE, line, ds.SOURCE)
        return notes(escape(line))

    return Form(
        f"{AURA_TITLE}: {escape(who.name)}",
        lambda: aura_fields(who),
        apply,
        validate=aura_problem(who),
        live=lambda values: _bullets(aura_lines(who, values)),
        help_id=HELP_AURA,
        inspector="The Aura",
    )


# -- where each is offered --


def offers_path(saga: Saga, character: Character) -> bool:
    return the_church(saga) and character.animal is None


def offers_spiritual(saga: Saga, character: Character) -> bool:
    return the_church(saga) and my.path(character) == my.CONTEMPLATIVE


def offers_revelation(saga: Saga, character: Character) -> bool:
    return (
        the_church(saga)
        and my.path(character) == my.MONISTIC
        and bool(ds.ascents(character))
    )


def offers_aid(saga: Saga, character: Character) -> bool:
    return rop_divine(saga) and character.animal is None


def offers_font(_saga: Saga, character: Character) -> bool:
    return fok.holds(character)


def offers_aura(_saga: Saga, character: Character) -> bool:
    return has_aura(character)

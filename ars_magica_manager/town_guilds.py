"""A town's guilds (City & Guild, Chapter III: Guilds, pp. 41-50; the
number of guilds, p. 54), and the saga's characters who belong to them.

- There are craft, service and merchant guilds (p. 41). Members rank as
  apprentices, journeymen, masters and senior masters under a dean; the
  officials, most guilds six, are senior masters chosen for six months
  (pp. 43, 49-50).
- A rough guide by rank (p. 42): an apprentice of 10-20 has Craft 3; a
  journeyman of 20-30, Craft 5 and Bargain 2; a master of 30-40, Craft 5-6
  and Bargain 3; a senior master of 40-50, Craft 7 and Leadership 3; a
  dean of 50 or more, Craft 7 and Leadership 5.
- What a rank needs (pp. 43-50): Guild Lore 1 for a journeyman, 2 for a
  master, 3 for a senior master or dean; Craft 5 for a journeyman or
  master and 7 for a senior master; Leadership half the Craft score for a
  master or senior master; Artes Liberales for a master; and the Social
  Status Virtue: Guild Apprentice, Journeyman, Guild Master, Senior Master
  (Major) or Guild Dean.
- Rising: seven years an apprentice, then an apprentice piece, a stress
  die + a Characteristic + Craft against 9 (p. 45); a journeyman joining
  another town's guild makes one against 12 (p. 47); a master pays about
  a year's income and needs a majority of the senior masters (p. 47).

Kept in Neighbour.details: "guilds" (each a towns.Guild) and
"guild_members" (each a GuildMember: a character, by id, in a guild, by
its trade)."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Required, TypedDict, cast

from . import towns
from .commands import Command, Confirm, Form, Refuse, SectionOps
from .form_spec import DialogField, pairs
from .grids import Grid
from .markup import BULLET, escape
from .models import Character, Neighbour, Saga, details_list
from .neighbour_lists import KindList, KindTab, list_ops
from .rules import scores
from .sections import GUILD_MEMBERS_SECTION, GUILDS_SECTION

SOURCE = "City & Guild, Chapter III: Guilds, pp. 41-50; Number of Guilds, p. 54"
CG = "C&G"

GUILD_KINDS: tuple[str, ...] = ("Craft", "Service", "Merchant")

#: Most guilds' officials (p. 50).
OFFICIALS = 6


@dataclass(frozen=True)
class Rank:
    """A rank in a guild: its name, the rough age, Craft and second
    Ability for it (p. 42), what it needs (Guild Lore, Craft, Leadership
    as half the Craft, Artes Liberales), and the Social Status Virtues
    that give it."""

    name: str
    age: str
    guide: str
    lore: int = 0
    craft: int = 0
    leadership: bool = False
    artes: bool = False
    virtues: frozenset[str] = frozenset()


RANKS: dict[str, Rank] = {
    "apprentice": Rank(
        "Apprentice", "10-20", "Craft 3", virtues=frozenset({"vf_guild_apprentice"})
    ),
    "journeyman": Rank(
        "Journeyman",
        "20-30",
        "Craft 5, Bargain 2",
        lore=1,
        craft=5,
        virtues=frozenset({"vf_journeyman", "vf_journeyman_rhine_tribunal"}),
    ),
    "master": Rank(
        "Master",
        "30-40",
        "Craft 5-6, Bargain 3",
        lore=2,
        craft=5,
        leadership=True,
        artes=True,
        virtues=frozenset({"vf_guild_master"}),
    ),
    "senior": Rank(
        "Senior master",
        "40-50",
        "Craft 7, Leadership 3",
        lore=3,
        craft=7,
        leadership=True,
        artes=True,
        virtues=frozenset({"vf_senior_master"}),
    ),
    "official": Rank(
        "Official",
        "40-50",
        "Craft 7, Leadership 3",
        lore=3,
        craft=7,
        leadership=True,
        artes=True,
        virtues=frozenset({"vf_senior_master"}),
    ),
    "dean": Rank(
        "Dean",
        "50+",
        "Craft 7, Leadership 5",
        lore=3,
        craft=7,
        leadership=True,
        artes=True,
        virtues=frozenset({"vf_guild_dean"}),
    ),
}


class GuildMember(TypedDict, total=False):
    """One of the saga's characters in a guild of the town, and his rank."""

    character_id: Required[str]
    guild: str
    rank: str
    note: str


def members(neighbour: Neighbour) -> list[GuildMember]:
    return cast(list[GuildMember], details_list(neighbour, "guild_members"))


def guild_name(guild: towns.Guild) -> str:
    trade = guild["trade"]
    return f"the {trade}' guild" if trade.endswith("s") else f"the {trade} guild"


def _count(value: Any) -> int:
    return int(value) if value else 0


def head_count(guild: towns.Guild) -> int:
    """Its members by rank: apprentices, journeymen, masters and senior
    masters (the officials and dean are senior masters, p. 43)."""
    return sum(
        _count(guild.get(key))
        for key in ("apprentices", "journeymen", "masters", "senior")
    )


# -- a character's standing in his guild --


def _matching(character: Character, *names: str) -> int:
    wanted = {n.casefold() for n in names if n}
    return max(
        (a.level for a in character.abilities if a.name.casefold() in wanted), default=0
    )


def craft_level(character: Character, craft: str) -> int:
    """His score in the guild's Craft, named as the guild names it, or as
    Craft: or Profession: it."""
    craft = craft.strip()
    if not craft:
        return 0
    return _matching(character, craft, f"Craft: {craft}", f"Profession: {craft}")


def guild_lore(character: Character) -> int:
    """His Guild Lore: an (Organization) Lore of a guild (p. 43)."""
    return max(
        (
            a.level
            for a in character.abilities
            if "lore" in a.name.casefold() and "guild" in a.name.casefold()
        ),
        default=0,
    )


def shortfalls(character: Character, guild: towns.Guild, rank_key: str) -> list[str]:
    """What he lacks for his rank (pp. 43-50), each as words."""
    rank = RANKS.get(rank_key)
    if rank is None:
        return []
    found = []
    craft = craft_level(character, guild.get("craft", ""))
    if rank.craft and craft < rank.craft:
        found.append(f"Craft {rank.craft} (has {craft})")
    lore = guild_lore(character)
    if rank.lore and lore < rank.lore:
        found.append(f"Guild Lore {rank.lore} (has {lore})")
    if rank.leadership:
        leadership = scores.ability_level(character, "Leadership")
        if leadership * 2 < craft:
            found.append(f"Leadership half his Craft (has {leadership})")
    if rank.artes and scores.ability_level(character, "Artes Liberales") < 1:
        found.append("Artes Liberales")
    if not {vf.vf_id for vf in character.virtues_flaws} & rank.virtues:
        found.append(f"the Social Status Virtue for a {rank.name.lower()}")
    return found


# -- the Guilds list --


def guilds_title(_saga: Saga, neighbour: Neighbour) -> str:
    return f"Guilds ({len(towns.guilds(neighbour))})"


def guilds_header(saga: Saga, neighbour: Neighbour) -> str:
    people = towns.population(neighbour)
    if people is None:
        return ""
    return (
        f"[$label]A town of {people:,}[/] has "
        f"{towns.guilds_expected(people, saga.current_year)} guilds in "
        f"{saga.current_year}; its first is usually its merchants' "
        f"[dim]({CG} p. 54)[/]"
    )


def _shown(value: Any) -> str:
    return "" if value is None else str(value)


def guilds_grid(_saga: Saga, neighbour: Neighbour) -> Grid:
    rows = []
    for g in towns.guilds(neighbour):
        masters = _count(g.get("masters")) + _count(g.get("senior"))
        rows.append(
            [
                g["trade"],
                g.get("kind") or "Craft",
                g.get("craft", ""),
                g.get("dean", ""),
                str(masters) if masters else "",
                _shown(g.get("journeymen")),
                _shown(g.get("apprentices")),
                str(head_count(g)) if head_count(g) else "",
            ]
        )
    return Grid(
        [
            "Trade",
            "Kind",
            "Craft",
            "Dean",
            "Masters",
            "Journeymen",
            "Apprentices",
            "Members",
        ],
        rows,
        list(range(len(rows))),
        "No guilds recorded: a town's first is usually its merchants'.",
        caps=[18, 8, 18, 20, 7, 10, 11, 0],
    )


def guild_info(saga: Saga, neighbour: Neighbour, row: int) -> str:
    listed = towns.guilds(neighbour)
    if row >= len(listed):
        return ""
    g = listed[row]
    head = " · ".join(
        part
        for part in (
            f"{g.get('kind') or 'Craft'} guild",
            escape(g.get("craft", "")),
            escape(g.get("hall", "")),
        )
        if part
    )
    officials = g.get("officials")
    lines = [
        f"[i]{head}[/]",
        f"[$label]Ranks[/] [dim]({CG} pp. 43-50)[/]",
        f"{BULLET} Dean: [b]{escape(g.get('dean') or '—')}[/]",
        f"{BULLET} Officials: [b]{OFFICIALS if officials is None else officials}[/]"
        + (" [dim](most guilds' six, p. 50)[/]" if officials is None else ""),
        f"{BULLET} Senior masters: [b]{_count(g.get('senior'))}[/]",
        f"{BULLET} Masters: [b]{_count(g.get('masters'))}[/]",
        f"{BULLET} Journeymen: [b]{_count(g.get('journeymen'))}[/]",
        f"{BULLET} Apprentices: [b]{_count(g.get('apprentices'))}[/]",
        f"[$label]Members:[/] [b]{head_count(g)}[/]",
    ]
    ours = [m for m in members(neighbour) if m.get("guild") == g["trade"]]
    for m in ours:
        character = saga.character(m["character_id"])
        if character is not None:
            rank = RANKS.get(m.get("rank") or "", RANKS["apprentice"])
            lines.append(f"{BULLET} {escape(character.name)}, {rank.name.lower()}")
    lines.append(
        "[dim]Rising: an apprentice piece after seven years, a stress die + "
        "Characteristic + Craft against 9 (p. 45); 12 to join another town's "
        "guild (p. 47); a master pays about a year's income and needs the "
        "senior masters' vote (p. 47).[/]"
    )
    return "\n".join(lines)


def guild_fields(
    _saga: Saga, _neighbour: Neighbour, guild: towns.Guild | None
) -> list[DialogField]:
    g = guild or {}
    return [
        DialogField(
            "trade",
            "Trade",
            "text",
            g.get("trade", ""),
            required=True,
            placeholder="e.g. Weavers",
        ),
        DialogField(
            "kind",
            "Kind",
            "select",
            g.get("kind", "Craft"),
            options=pairs(GUILD_KINDS),
            required=True,
        ),
        DialogField(
            "craft",
            "Craft",
            "text",
            g.get("craft", ""),
            hint="The Craft or Profession its members practise, as their "
            "Ability names it (Weaver for Craft: Weaver).",
        ),
        DialogField("hall", "Guildhall", "text", g.get("hall", "")),
        DialogField("dean", "Dean", "text", g.get("dean", "")),
        DialogField(
            "officials",
            "Officials",
            "optint",
            g.get("officials"),
            hint="Most guilds have six (p. 50).",
        ),
        DialogField("senior", "Senior masters", "optint", g.get("senior")),
        DialogField("masters", "Masters", "optint", g.get("masters")),
        DialogField("journeymen", "Journeymen", "optint", g.get("journeymen")),
        DialogField("apprentices", "Apprentices", "optint", g.get("apprentices")),
    ]


def _members_problem(values: dict[str, Any]) -> str | None:
    for key, label in (
        ("officials", "Officials"),
        ("senior", "Senior masters"),
        ("masters", "Masters"),
        ("journeymen", "Journeymen"),
        ("apprentices", "Apprentices"),
    ):
        if (values.get(key) or 0) < 0:
            return f"{label} can't be fewer than none."
    return None


def guild_ops(saga: Saga, neighbour: Neighbour) -> SectionOps:
    """Add, Edit and Delete on the guilds: renaming a guild keeps its
    members in it, and deleting one takes them out."""
    base = list_ops(
        saga,
        neighbour,
        "guilds",
        "Guild",
        guild_fields,
        guild_name,
        validate=_members_problem,
    )
    add, edit, remove = base.add, base.edit, base.remove
    assert add is not None and edit is not None and remove is not None

    def edited(index: int) -> Command:
        old = towns.guilds(neighbour)[index]["trade"]
        form = edit(index)
        if not isinstance(form, Form):
            return form
        apply = form.apply

        def rename(values: dict[str, Any]) -> None:
            apply(values)
            for m in members(neighbour):
                if m.get("guild") == old:
                    m["guild"] = values["trade"]

        return replace(form, apply=rename)

    def removed(index: int) -> Command:
        trade = towns.guilds(neighbour)[index]["trade"]
        confirm = remove(index)
        if not isinstance(confirm, Confirm):
            return confirm
        apply = confirm.apply
        ours = [m for m in members(neighbour) if m.get("guild") == trade]

        def delete() -> None:
            apply()
            listed = members(neighbour)
            listed[:] = [m for m in listed if m.get("guild") != trade]

        question = confirm.question
        if ours:
            question = question.removesuffix("?") + (
                f"? Its {len(ours)} member{'' if len(ours) == 1 else 's'} from the "
                "saga leave it."
            )
        return replace(confirm, question=question, apply=delete)

    return SectionOps(add=add, edit=edited, remove=removed, rows=base.rows)


# -- the saga's characters in the guilds --


def _guild(neighbour: Neighbour, trade: str) -> towns.Guild | None:
    return next((g for g in towns.guilds(neighbour) if g["trade"] == trade), None)


def _member_name(saga: Saga, entry: GuildMember) -> str:
    character = saga.character(entry["character_id"])
    return character.name if character is not None else "(a character no longer here)"


def members_title(_saga: Saga, neighbour: Neighbour) -> str:
    return f"Members from the Saga ({len(members(neighbour))})"


def members_grid(saga: Saga, neighbour: Neighbour) -> Grid:
    rows, styles = [], {}
    for i, entry in enumerate(members(neighbour)):
        character = saga.character(entry["character_id"])
        guild = _guild(neighbour, entry.get("guild", ""))
        rank = RANKS.get(entry.get("rank") or "", RANKS["apprentice"])
        if character is None or guild is None:
            rows.append([_member_name(saga, entry), entry.get("guild", ""), rank.name])
            rows[-1] += ["", "", "no such guild" if guild is None else ""]
            styles[(i, 5)] = "$text-warning"
            continue
        lacking = shortfalls(character, guild, entry.get("rank") or "apprentice")
        rows.append(
            [
                character.name,
                guild["trade"],
                rank.name,
                str(craft_level(character, guild.get("craft", ""))),
                str(guild_lore(character)),
                f"lacks {len(lacking)}" if lacking else "fits",
            ]
        )
        styles[(i, 5)] = "$text-warning" if lacking else "$text-success"
    return Grid(
        ["Member", "Guild", "Rank", "Craft", "Guild Lore", "Rank's needs"],
        rows,
        list(range(len(rows))),
        "None of the saga's characters belongs to a guild here.",
        styles=styles,
        caps=[24, 18, 13, 5, 10, 0],
    )


def member_info(saga: Saga, neighbour: Neighbour, row: int) -> str:
    listed = members(neighbour)
    if row >= len(listed):
        return ""
    entry = listed[row]
    character = saga.character(entry["character_id"])
    guild = _guild(neighbour, entry.get("guild", ""))
    rank = RANKS.get(entry.get("rank") or "", RANKS["apprentice"])
    if character is None or guild is None:
        return "[$text-warning]Its character or guild is no longer here.[/]"
    lines = [
        f"[i]{rank.name} of {escape(guild_name(guild))}[/]",
        f"[$label]A {rank.name.lower()}, as a rough guide:[/] aged {rank.age}, "
        f"{rank.guide} [dim]({CG} p. 42)[/]",
    ]
    lacking = shortfalls(character, guild, entry.get("rank") or "apprentice")
    if lacking:
        lines.append("[$text-warning]For his rank he lacks [dim](pp. 43-50)[/]:[/]")
        lines += [f"{BULLET} {escape(what)}" for what in lacking]
    else:
        lines.append("[$text-success]He has what his rank needs (pp. 43-50).[/]")
    if entry.get("note"):
        lines.append(escape(entry.get("note", "")))
    return "\n".join(lines)


def member_fields(
    saga: Saga, neighbour: Neighbour, entry: GuildMember | None
) -> list[DialogField]:
    e = entry or {}
    trades = [g["trade"] for g in towns.guilds(neighbour)]
    return [
        DialogField(
            "character_id",
            "Character",
            "select",
            e.get("character_id"),
            options=[(escape(c.name), c.id) for c in saga.characters],
            required=True,
        ),
        DialogField(
            "guild",
            "Guild",
            "select",
            e.get("guild") or (trades[0] if trades else None),
            options=[(escape(t), t) for t in trades],
            required=True,
        ),
        DialogField(
            "rank",
            "Rank",
            "select",
            e.get("rank", "apprentice"),
            options=[(r.name, key) for key, r in RANKS.items()],
            required=True,
        ),
        DialogField("note", "Note", "text", e.get("note", "")),
    ]


def member_ops(saga: Saga, neighbour: Neighbour) -> SectionOps:
    base = list_ops(
        saga,
        neighbour,
        "guild_members",
        "Member",
        member_fields,
        lambda e: _member_name(saga, e),
    )
    add = base.add
    assert add is not None

    def added() -> Command:
        if not towns.guilds(neighbour):
            return Refuse("Add a Member", "Add the guild first, then its members.")
        return add()

    return replace(base, add=added)


GUILDS_TAB = KindTab(
    "Guilds",
    "tab-nb-guilds",
    (
        KindList(
            GUILDS_SECTION,
            guilds_title,
            guilds_grid,
            guild_ops,
            guild_info,
            guilds_header,
        ),
        KindList(
            GUILD_MEMBERS_SECTION, members_title, members_grid, member_ops, member_info
        ),
    ),
    icon="faction",
    panel="[dim]Choose a guild to see its ranks, or a member his standing.[/]",
)

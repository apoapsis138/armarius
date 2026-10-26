"""The Rhine Tribunal's customs (Guardians of the Forests: The Rhine
Tribunal): its magi band together in gilds, political factions that
cut across House and covenant (pp. 27-29). A magus belongs to one gild
at most, joins freely and publicly, and may not join a gild he has the
(Gild) Enmity Flaw for (p. 22); a gild has a leader or leaders and an
agenda, and the book gives it no dues. Notice of a case is due a season
before the meeting, as under the core rules: the book sets no other
period.

A gild is kept in the package's data as {"name", "agenda", "leader_ids"
(character ids), "magi" (its members' character ids), "members" (the
covenants most of whose magi belong to it)}: the roster gains a Gild
column, the sheet a Gilds list, a covenant's form a gild for each of its
magi, and a magus's sheet his gild. Saves made before the agenda had
its name kept it as "dues".

The Tremere of the Rhine have given their sigils to the House's two
exarchs, Stentorius and Severicus, who cast them (pp. 84, 109); the
package's "sigil_held_by" ({character id: holder's id}) says whose
sigil another casts, so its owner casts no vote of his own."""

from __future__ import annotations

import re
from typing import Any

from .. import tribunals, world
from ..commands import Command, Confirm, Form, Refuse, SectionOps
from ..form_spec import DialogField
from ..grids import Grid
from ..markup import escape
from ..models import Character, Covenant, Saga, Tribunal
from ..rules import rhine_ranks as ranks
from ..sections import GILDS_SECTION
from . import (
    PackageList,
    PackageTab,
    PackageVerb,
    RosterColumn,
    TribunalPackage,
    data,
    entries,
    register,
)

KEY = "rhine"


def gilds(tribunal: Tribunal) -> list[dict[str, Any]]:
    """The Tribunal's gilds, in the order entered."""
    found = entries(tribunal, KEY, "gilds")
    for gild in found:
        if "dues" in gild:
            gild.setdefault("agenda", gild.pop("dues"))
    return found


#: A gild's leaders at most (the Apple Gild's triumvirate, p. 29).
LEADERS = 3


def gild_of(tribunal: Tribunal, character_id: str) -> dict[str, Any] | None:
    """The gild the magus belongs to, or None: a magus may belong to one
    gild only (Guardians of the Forests p. 28)."""
    return next((g for g in gilds(tribunal) if character_id in g.get("magi", [])), None)


def join(tribunal: Tribunal, character_id: str, gild: dict[str, Any] | None) -> None:
    """The magus leaves any gild he is in and joins `gild` (None: none)."""
    for each in gilds(tribunal):
        magi = each.get("magi", [])
        if character_id in magi:
            magi.remove(character_id)
    if gild is not None:
        gild.setdefault("magi", []).append(character_id)


def enmities(character: Character) -> set[str]:
    """The trees of the gilds the magus has the (Gild) Enmity Flaw for:
    he may not join them (p. 22)."""
    found = set()
    for vf in character.virtues_flaws:
        if vf.vf_id == ENMITY:
            tree = gild_tree(vf.params.get("gild", ""))
            if tree is not None:
                found.add(tree)
    return found


def may_join(character: Character, gild: dict[str, Any]) -> bool:
    return gild_tree(gild.get("name", "")) not in enmities(character)


def sigil_held_by(tribunal: Tribunal) -> dict[str, str]:
    """Whose sigil another magus casts, by the owner's character id."""
    found = data(tribunal, KEY).setdefault("sigil_held_by", {})
    if not isinstance(found, dict):
        raise ValueError(f"The sigils held should be a mapping, not {found!r}.")
    return found


def casts_no_vote(_saga: Saga, tribunal: Tribunal, magus: Character) -> bool:
    """A magus whose sigil another casts has no vote of his own."""
    return magus.id in sigil_held_by(tribunal)


#: The trees the Rhine's gilds are named for, each with its symbol.
GILD_TREES = ("Oak", "Hawthorn", "Ash", "Elder", "Linden", "Apple")


def gild_tree(name: str) -> str | None:
    """The tree a gild's name names ("Oak Gild (Eichengilde)": "Oak"),
    whose symbol it bears; None for a name naming none, or several."""
    words = set(re.findall(r"[a-z]+", name.lower()))
    found = [tree for tree in GILD_TREES if tree.lower() in words]
    return found[0] if len(found) == 1 else None


#: The (Gild) Enmity Flaw.
ENMITY = "vf_gild_enmity"


def gilds_of(tribunal: Tribunal, covenant: Covenant) -> list[str]:
    """The names of the gilds most of `covenant`'s magi belong to."""
    return [g["name"] for g in gilds(tribunal) if covenant.id in g.get("members", [])]


def roster_gilds(saga: Saga, tribunal: Tribunal, covenant: Covenant) -> str:
    """The roster's Gild: the gilds most of its magi belong to, then any
    other gild one of its magi has joined."""
    names = gilds_of(tribunal, covenant)
    for magus in world.covenant_magi(saga, covenant):
        gild = gild_of(tribunal, magus.id)
        if gild is not None and gild["name"] not in names:
            names.append(gild["name"])
    return ", ".join(names)


def _members(saga: Saga, gild: dict[str, Any]) -> list[str]:
    names = []
    for ident in gild.get("members", []):
        covenant = saga.covenant(ident)
        if covenant is not None:
            names.append(covenant.name)
    return names


def gilds_title(_saga: Saga, tribunal: Tribunal) -> str:
    return f"Gilds ({len(gilds(tribunal))})"


def _leaders(saga: Saga, gild: dict[str, Any]) -> str:
    found = (saga.character(i) for i in gild.get("leader_ids", []))
    return ", ".join(c.name for c in found if c is not None)


def _magi_text(saga: Saga, gild: dict[str, Any]) -> str:
    names = [c.name for c in (saga.character(i) for i in gild.get("magi", [])) if c]
    covenants = _members(saga, gild)
    parts = [", ".join(names)] if names else []
    if covenants:
        parts.append("most of " + ", ".join(covenants))
    return "; ".join(parts)


def gilds_grid(saga: Saga, tribunal: Tribunal) -> Grid:
    """Each gild: who leads it, its magi and the covenants most of whose
    magi belong to it, and its agenda."""
    rows = [
        [g["name"], _leaders(saga, g), _magi_text(saga, g), g.get("agenda", "")]
        for g in gilds(tribunal)
    ]
    return Grid(
        ["Gild", "Led by", "Members", "Agenda"],
        rows,
        list(range(len(rows))),
        "No gilds yet: the Rhine's magi band together in gilds, political "
        "factions across House and covenant, a magus in one at most.",
        caps=[18, 20, 30, 0],
        stretch=3,
    )


def covenant_gild_fields(
    saga: Saga, tribunal: Tribunal, covenant: Covenant | None
) -> list[DialogField]:
    """A covenant's own form: a tick for each of the Tribunal's gilds, on
    for those most of its magi belong to, and each of its magi's gild."""
    ident = covenant.id if covenant is not None else None
    found = [
        DialogField(
            f"gild_{index}",
            escape(gild["name"]),
            "check",
            ident in gild.get("members", []),
            hint="The gilds most of its magi belong to." if index == 0 else "",
        )
        for index, gild in enumerate(gilds(tribunal))
    ]
    magi = world.covenant_magi(saga, covenant) if covenant is not None else []
    for magus in magi:
        mine = gild_of(tribunal, magus.id)
        found.append(
            DialogField(
                f"gild_of_{magus.id}",
                f"Gild: {escape(magus.name)}",
                "select",
                str(gilds(tribunal).index(mine)) if mine is not None else None,
                options=[
                    (escape(g["name"]), str(index))
                    for index, g in enumerate(gilds(tribunal))
                    if may_join(magus, g)
                ],
                allow_blank=True,
                placeholder="(no gild)",
                hint="One gild at most, never one he has the Enmity Flaw "
                "for (Guardians of the Forests pp. 22, 28).",
            )
        )
    return found


def save_covenant_gilds(tribunal: Tribunal, ident: str, values: dict[str, Any]) -> None:
    """Keep a covenant's gild ticks: it joins the gilds ticked and
    leaves the others."""
    for index, gild in enumerate(gilds(tribunal)):
        key = f"gild_{index}"
        if key not in values:
            continue
        members = gild.setdefault("members", [])
        if values[key] and ident not in members:
            members.append(ident)
        elif not values[key] and ident in members:
            members.remove(ident)
    listed = gilds(tribunal)
    for key, value in values.items():
        if not key.startswith("gild_of_"):
            continue
        chosen = listed[int(value)] if value not in (None, "") else None
        join(tribunal, key.removeprefix("gild_of_"), chosen)


def gild_fields(
    saga: Saga, tribunal: Tribunal, gild: dict[str, Any] | None
) -> list[DialogField]:
    """A gild: its name, its agenda, its leaders, and a tick for each
    covenant of the Tribunal most of whose magi belong to it."""
    members = set(gild.get("members", [])) if gild is not None else set()
    leaders = list(gild.get("leader_ids", [])) if gild is not None else []
    magi = [
        (escape(m.name), m.id)
        for c in tribunals.covenants_of(saga, tribunal)
        for m in world.covenant_magi(saga, c)
    ]
    fields = [
        DialogField(
            "name",
            "Gild",
            "text",
            gild["name"] if gild is not None else "",
            required=True,
            placeholder="e.g. Hermetic",
        ),
        DialogField(
            "agenda",
            "Agenda",
            "text",
            gild.get("agenda", "") if gild is not None else "",
            placeholder="e.g. to restore the Tribunal's ancient glory",
            hint="What it stands for; a member is expected to vote with it.",
        ),
    ]
    fields += [
        DialogField(
            f"leader_{n}",
            "Led by" if n == 0 else "And by",
            "select",
            leaders[n] if n < len(leaders) else None,
            options=magi,
            allow_blank=True,
            placeholder="(not recorded)",
        )
        for n in range(LEADERS)
    ]
    fields += [
        DialogField(f"member_{c.id}", escape(c.name), "check", c.id in members)
        for c in tribunals.covenants_of(saga, tribunal)
    ]
    return fields


def _gild_from(
    saga: Saga, tribunal: Tribunal, values: dict[str, Any], gild: dict[str, Any]
) -> None:
    gild["name"] = values["name"]
    gild["agenda"] = values.get("agenda", "")
    gild.pop("dues", None)
    leaders = [values.get(f"leader_{n}") for n in range(LEADERS)]
    gild["leader_ids"] = list(dict.fromkeys(i for i in leaders if i))
    gild.setdefault("magi", [])
    shown = {c.id for c in tribunals.covenants_of(saga, tribunal)}
    # Members no longer in the Tribunal stay, unseen, as the form can't
    # show them.
    kept = [m for m in gild.get("members", []) if m not in shown]
    gild["members"] = kept + [
        ident for ident in sorted(shown) if values.get(f"member_{ident}")
    ]


def gild_ops(saga: Saga, tribunal: Tribunal) -> SectionOps:
    def form(gild: dict[str, Any] | None) -> Form:
        def apply(values: dict[str, Any]) -> None:
            target = gild if gild is not None else {}
            _gild_from(saga, tribunal, values, target)
            if gild is None:
                gilds(tribunal).append(target)

        return Form(
            "Add a Gild" if gild is None else "Edit a Gild",
            lambda: gild_fields(saga, tribunal, gild),
            apply,
            save_label="Add" if gild is None else "Save",
        )

    def remove(index: int) -> Command:
        gild = gilds(tribunal)[index]

        def apply() -> None:
            gilds(tribunal).remove(gild)

        return Confirm(f"Delete the gild {escape(gild['name'])}?", apply)

    return SectionOps(
        add=lambda: form(None),
        edit=lambda index: form(gilds(tribunal)[index]),
        remove=remove,
        rows=lambda: [g["name"] for g in gilds(tribunal)],
    )


# -- the ranks: marks of approval, the archmage's challenge, the sigils
# conferred (rules.rhine_ranks) --


def _mapping(tribunal: Tribunal, name: str) -> dict[str, Any]:
    found = data(tribunal, KEY).setdefault(name, {})
    if not isinstance(found, dict):
        raise ValueError(f"The Tribunal's {name} should be a mapping, not {found!r}.")
    return found


def marks(tribunal: Tribunal, character_id: str) -> list[dict[str, Any]]:
    """The marks of approval the magus holds, each {"sponsor_id",
    "asked", "year"}."""
    return _mapping(tribunal, "marks").setdefault(character_id, [])


def challenge_record(tribunal: Tribunal, archmage_id: str) -> dict[str, Any]:
    """An archmage's challenge: {"contest", "bouts": [{"challenger_id",
    "won", "year"}]}."""
    return _mapping(tribunal, "challenges").setdefault(
        archmage_id, {"contest": "", "bouts": []}
    )


def bouts(tribunal: Tribunal, archmage_id: str) -> list[ranks.Bout]:
    found = challenge_record(tribunal, archmage_id).get("bouts", [])
    return [ranks.Bout(b.get("challenger_id", ""), bool(b.get("won"))) for b in found]


def challenged_by(tribunal: Tribunal, challenger_id: str) -> list[str]:
    """The archmagi the magus has challenged."""
    return [
        ident
        for ident, record in _mapping(tribunal, "challenges").items()
        if any(b.get("challenger_id") == challenger_id for b in record.get("bouts", []))
    ]


def promotions(tribunal: Tribunal) -> list[dict[str, Any]]:
    """Each rank won here, whose sigils the next meeting's rite confers:
    {"character_id", "rank", "year", "sigils", "conferred" (the meeting's
    year, or None), "names" (the retired magi whose sigils)}."""
    return entries(tribunal, KEY, "promotions")


def entrusted(tribunal: Tribunal) -> dict[str, list[str]]:
    """The retired magi whose sigils each magus wields by proxy, by his
    character id, as the rite conferred them."""
    return _mapping(tribunal, "entrusted")


def _promote(
    saga: Saga, tribunal: Tribunal, magus: Character, to: str, deed: str = ""
) -> None:
    ranks.promote(magus, to, deed)
    promotions(tribunal).append(
        {
            "character_id": magus.id,
            "rank": to,
            "year": saga.current_year,
            "sigils": 1,
            "conferred": None,
            "names": [],
        }
    )


def tribunal_magi(saga: Saga, tribunal: Tribunal) -> list[Character]:
    """The magi of the Tribunal's covenants."""
    return [
        m
        for c in tribunals.covenants_of(saga, tribunal)
        for m in world.covenant_magi(saga, c)
    ]


def _magus_options(magi: list[Character]) -> list[tuple[str, str]]:
    return [(escape(f"{m.name} ({ranks.rank_name(m)})"), m.id) for m in magi]


def _gild_name(tribunal: Tribunal, magus: Character) -> str:
    gild = gild_of(tribunal, magus.id)
    return gild["name"] if gild is not None else ""


def enmity_gilds(tribunal: Tribunal, magus: Character) -> list[str]:
    """The names of the gilds the magus has the Enmity Flaw for."""
    trees = enmities(magus)
    return [g["name"] for g in gilds(tribunal) if gild_tree(g["name"]) in trees]


def _sponsors(
    saga: Saga, tribunal: Tribunal, applicant: Character, extra: Character | None
) -> list[ranks.Sponsor]:
    found = [saga.character(m.get("sponsor_id")) for m in marks(tribunal, applicant.id)]
    magi = [m for m in found if m is not None]
    if extra is not None and extra not in magi:
        magi.append(extra)
    return [ranks.Sponsor(m, _gild_name(tribunal, m)) for m in magi]


def mark_text(saga: Saga, tribunal: Tribunal, values: dict[str, Any]) -> str:
    """The form's live line: the marks the applicant would hold, and what
    custom frowns on in them."""
    applicant = saga.character(values.get("applicant"))
    if applicant is None:
        return ""
    sponsors = _sponsors(
        saga, tribunal, applicant, saga.character(values.get("sponsor"))
    )
    names = ", ".join(s.magus.name for s in sponsors)
    count = min(len(sponsors), ranks.MARKS)
    lines = [
        f"{count} of {ranks.MARKS} marks"
        + (f": {names}" if names else "")
        + (f". {applicant.name} becomes a master." if count == ranks.MARKS else ".")
    ]
    lines += ranks.mark_warnings(
        saga, applicant, sponsors, enmity_gilds(tribunal, applicant)
    )
    return "\n".join(escape(line) for line in lines)


def mark_form(saga: Saga, tribunal: Tribunal) -> Form:
    """A master gives a journeyman his mark of approval; the third makes
    him a master (Guardians of the Forests pp. 22-23)."""
    magi = tribunal_magi(saga, tribunal)

    def fields() -> list[DialogField]:
        return [
            DialogField(
                "applicant",
                "Applicant",
                "select",
                None,
                options=_magus_options([m for m in magi if not ranks.is_master(m)]),
                required=True,
                hint="A journeyman famed for his magical prowess (a Redcap: for "
                "his loyal service).",
            ),
            DialogField(
                "sponsor",
                "Mark given by",
                "select",
                None,
                options=_magus_options([m for m in magi if ranks.is_master(m)]),
                required=True,
                hint="A master not of his covenant or House; the three from "
                "three different gilds.",
            ),
            DialogField(
                "asked",
                "Asked of him",
                "text",
                "",
                placeholder="e.g. a summa for the Great Library",
                hint="What the master asked before giving his token, if anything.",
            ),
        ]

    def validate(values: dict[str, Any]) -> str | None:
        applicant = saga.character(values.get("applicant"))
        sponsor = saga.character(values.get("sponsor"))
        if applicant is None or sponsor is None:
            return None
        given = [m.get("sponsor_id", "") for m in marks(tribunal, applicant.id)]
        return ranks.mark_problem(applicant, sponsor, given) or None

    def apply(values: dict[str, Any]) -> None:
        applicant = saga.character(values["applicant"])
        assert applicant is not None
        held = marks(tribunal, applicant.id)
        held.append(
            {
                "sponsor_id": values["sponsor"],
                "asked": values.get("asked", ""),
                "year": saga.current_year,
            }
        )
        if len(held) >= ranks.MARKS:
            _promote(saga, tribunal, applicant, ranks.MASTER)

    return Form(
        "Mark of Approval",
        fields,
        apply,
        validate=validate,
        live=lambda values: mark_text(saga, tribunal, values),
        save_label="Give",
    )


def mark_step(saga: Saga, tribunal: Tribunal, _row: int) -> Command:
    """More's Mark of Approval (on any gild: the mark is the master's
    own)."""
    magi = tribunal_magi(saga, tribunal)
    if not any(ranks.is_master(m) for m in magi):
        return Refuse(
            "Mark of Approval",
            "No master belongs to the Tribunal's covenants: only masters give "
            "marks of approval.",
        )
    return mark_form(saga, tribunal)


WON, LOST = "Won", "Lost"


def _archmagi(saga: Saga) -> list[Character]:
    return [c for c in saga.characters if ranks.is_archmage(c)]


def is_rhine_magus(saga: Saga, magus: Character) -> bool:
    """Whether the magus belongs to a Rhine Tribunal: his covenant's
    Tribunal keeps the Rhine's customs. One with no covenant, or of a
    covenant in no Tribunal, is taken as not."""
    covenant = saga.covenant(magus.covenant_id) if magus.covenant_id else None
    tribunal = tribunals.of(saga, covenant) if covenant is not None else None
    return tribunal is not None and tribunal.package == KEY


def challengers(saga: Saga, tribunal: Tribunal) -> list[Character]:
    """Who may challenge an archmage: the Rhine's masters (this
    Tribunal's first), and any magus of another Tribunal, who needn't be a
    master since archmagi are found throughout the Order (p. 24; Errata
    p. 42). None is an archmage already."""
    found = [m for m in tribunal_magi(saga, tribunal) if ranks.is_master(m)]
    found += [
        m
        for m in saga.characters
        if m.type == "magus"
        and m not in found
        and (ranks.is_master(m) or not is_rhine_magus(saga, m))
    ]
    return [m for m in found if not ranks.is_archmage(m)]


def _challenger_options(saga: Saga, magi: list[Character]) -> list[tuple[str, str]]:
    """A Rhine magus by his rank; one of another Tribunal by its name, as
    the Rhine's ranks aren't his."""
    found = []
    for m in magi:
        if is_rhine_magus(saga, m):
            label = ranks.rank_name(m)
        else:
            covenant = saga.covenant(m.covenant_id) if m.covenant_id else None
            tribunal = tribunals.of(saga, covenant) if covenant is not None else None
            label = tribunal.name if tribunal is not None else "no Tribunal"
        found.append((escape(f"{m.name} ({label})"), m.id))
    return found


def challenge_text(saga: Saga, tribunal: Tribunal, values: dict[str, Any]) -> str:
    """The form's live line: the archmage's contest and losses, and what
    custom frowns on."""
    challenger = saga.character(values.get("challenger"))
    archmage = saga.character(values.get("archmage"))
    if challenger is None or archmage is None:
        return ""
    fought = bouts(tribunal, archmage.id)
    lost = ranks.losses(fought)
    lines = [f"{archmage.name} has lost {lost} of {ranks.LOSSES}."]
    lines += ranks.challenge_warnings(
        saga, challenger, archmage, fought, challenged_by(tribunal, challenger.id)
    )
    return "\n".join(escape(line) for line in lines)


def challenge_form(saga: Saga, tribunal: Tribunal) -> Form:
    """A master challenges an archmage at the archmage's own contest; the
    winner is made archmage (Guardians of the Forests p. 24). A magus of
    another Tribunal may challenge too, master or not."""
    able = challengers(saga, tribunal)

    def contest_of(values: dict[str, Any]) -> str:
        ident = values.get("archmage")
        if not ident:
            return ""
        return _mapping(tribunal, "challenges").get(ident, {}).get("contest", "")

    def spell_of(values: dict[str, Any]) -> dict[str, Any]:
        challenger = saga.character(values.get("challenger"))
        if challenger is None:
            return {}
        has = ranks.invented_magnitude(challenger) >= ranks.ARCHMAGE_MAGNITUDE
        return {"spell": has}

    def fields() -> list[DialogField]:
        return [
            DialogField(
                "challenger",
                "Challenger",
                "select",
                None,
                options=_challenger_options(saga, able),
                required=True,
                hint="A Rhine master, or a magus of another Tribunal; never "
                "twice against the same archmage.",
                fills=spell_of,
            ),
            DialogField(
                "archmage",
                "Archmage",
                "select",
                None,
                options=_magus_options(_archmagi(saga)),
                required=True,
                hint="Seven losses and he is challenged no more.",
            ),
            DialogField(
                "contest",
                "Contest",
                "text",
                "",
                placeholder="e.g. to defeat him in certamen",
                hint="Set by the archmage the first time he is challenged, then "
                "his for life; it must involve magical powers.",
                show_if=lambda v: not contest_of(v),
            ),
            DialogField(
                "spell",
                "Has invented a spell of 7th magnitude",
                "check",
                bool(able and spell_of({"challenger": able[0].id}).get("spell")),
                hint="Ticked for you when one he invented is recorded.",
            ),
            DialogField(
                "deed",
                "Great deed",
                "text",
                "",
                required=True,
                placeholder="e.g. the binding of the Black Forest's wyrm",
                hint="Famed throughout the Order, and of benefit to it.",
            ),
            DialogField(
                "outcome",
                "Outcome",
                "select",
                LOST,
                options=[(WON, WON), (LOST, LOST)],
                required=True,
            ),
        ]

    def validate(values: dict[str, Any]) -> str | None:
        challenger = saga.character(values.get("challenger"))
        archmage = saga.character(values.get("archmage"))
        if challenger is None or archmage is None:
            return None
        problem = ranks.challenge_problem(
            challenger,
            archmage,
            bouts(tribunal, archmage.id),
            is_rhine_magus(saga, challenger),
        )
        if problem:
            return problem
        if not values.get("spell"):
            return (
                "A challenger must have invented a spell of at least 7th "
                "magnitude (Guardians of the Forests p. 24)."
            )
        if not contest_of(values) and not (values.get("contest") or "").strip():
            return "Name the archmage's contest: he sets it at his first challenge."
        return None

    def apply(values: dict[str, Any]) -> None:
        challenger = saga.character(values["challenger"])
        assert challenger is not None
        record = challenge_record(tribunal, values["archmage"])
        if not record.get("contest"):
            record["contest"] = (values.get("contest") or "").strip()
        won = values.get("outcome") == WON
        record.setdefault("bouts", []).append(
            {
                "challenger_id": challenger.id,
                "won": won,
                "year": saga.current_year,
            }
        )
        if won and is_rhine_magus(saga, challenger):
            _promote(saga, tribunal, challenger, ranks.ARCHMAGE, values["deed"])
        elif won:
            # A magus of another Tribunal takes no Rhine rank and holds no
            # proxies at its meetings, so no sigil is owed him at its rite.
            ranks.acclaim(challenger, values["deed"])

    return Form(
        "The Archmage's Challenge",
        fields,
        apply,
        validate=validate,
        live=lambda values: challenge_text(saga, tribunal, values),
        save_label="Record",
    )


def challenge_step(saga: Saga, tribunal: Tribunal, _row: int) -> Command:
    """More's Archmage's Challenge."""
    if not challengers(saga, tribunal):
        return Refuse(
            "The Archmage's Challenge",
            "No magus can challenge: a Rhine magus must be a master first, "
            "and no magus of another Tribunal is in the saga.",
        )
    if not _archmagi(saga):
        return Refuse("The Archmage's Challenge", "No archmage is in the saga.")
    return challenge_form(saga, tribunal)


def magus_facts(
    saga: Saga, tribunal: Tribunal, character: Character
) -> list[tuple[str, str]]:
    """A Rhine magus's gild, who casts his sigil when another does, the
    marks of approval he holds, the retired magi's sigils he wields, and
    an apprentice a journeyman may not formally take."""
    found = []
    gild = gild_of(tribunal, character.id)
    if gild is not None:
        found.append(("Gild", gild["name"]))
    holder = saga.character(sigil_held_by(tribunal).get(character.id))
    if holder is not None:
        found.append(("Sigil", f"cast by {holder.name}"))
    held = _mapping(tribunal, "marks").get(character.id, [])
    if held and not ranks.is_master(character):
        found.append(("Marks", f"{len(held)} of {ranks.MARKS} toward master"))
    proxies = entrusted(tribunal).get(character.id, [])
    if proxies:
        found.append(("Sigils by proxy", ", ".join(proxies)))
    if not ranks.is_master(character):
        for apprentice in ranks.apprentices_of(saga, character):
            found.append(
                (
                    "Apprentice",
                    f"{apprentice.name}: a journeyman's, so a recruited hedge "
                    "wizard at his Gauntlet, never his filius (GotF p. 24)",
                )
            )
    return found


RHINE = TribunalPackage(
    KEY,
    "Rhine",
    customs="Gilds",
    book="GotF",
    skips_grand_tribunal=True,
    columns=(RosterColumn("Gild", roster_gilds, 20),),
    tabs=(
        PackageTab(
            "Gilds",
            "tab-trib-gilds",
            (
                PackageList(
                    GILDS_SECTION,
                    gilds_title,
                    gilds_grid,
                    gild_ops,
                    more=(
                        PackageVerb("rhine_mark", "Mark of Approval", mark_step),
                        PackageVerb(
                            "rhine_challenge", "Archmage's Challenge", challenge_step
                        ),
                    ),
                ),
            ),
        ),
    ),
    meeting_steps=("rhine_rite",),
    about="Its magi band together in gilds, political factions across "
    "House and covenant, one gild to a magus.",
    covenant_fields=covenant_gild_fields,
    save_covenant=save_covenant_gilds,
    magus_facts=magus_facts,
    casts_no_vote=casts_no_vote,
)

register(RHINE)

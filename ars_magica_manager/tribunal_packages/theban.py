"""The Theban Tribunal's customs (The Sundered Eagle: The Theban
Tribunal), in the book's own terms. Its magi are politai (citizens) or
metoikoi (resident foreigners); a polites earns tokens for services to
the community and shards for acts against its unity, and any polites
with a shard may be ostracised. Every magus present votes once, by
voting sigil, politai and metoikoi alike, so the troupe's votes are
counted as under the core rules. Each covenant belongs to one of four
phylai, and the Council of Magistrates (the archai, the archon, the
polemarch and the logothete) holds the Tribunal's offices.

Kept in the package's data: "magi", each {"character_id", "status"
("polites" or "metoikos"), "tokens", "shards", "services",
"ostracised_until", "why"}; "archai", each {"office", "holder_id",
"term_ends", "duties"}; and "phylai", {covenant id: phyle}. Saves made
before the book's terms were used say "liturgies" for services."""

from __future__ import annotations

from typing import Any

from .. import coinage, treasury
from ..arts import ARTS
from ..commands import Command, Confirm, Form, Refuse, SectionOps
from ..form_spec import DialogField
from ..grids import Grid
from ..markup import escape
from ..models import Covenant, Saga, TreasuryEntry, Tribunal
from ..sections import ARCHAI_SECTION, TOKENS_SECTION
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

KEY = "theban"

#: The four phylai, each with the lands whose covenants belong to it.
PHYLAI: dict[str, str] = {
    "Ionian": "the western mainland: Thessaly, Epiros, the Peloponnese",
    "Aegean": "around the Aegean: Boeotia, Euboea, Macedonia, the northern islands",
    "Kretan": "Candia, the Cyclades, the Dodecanese and southern Nicaea",
    "Propontian": "Thrace, northern Nicaea, Constantinople and the Black Sea",
}

#: A magus's standing in the polity, as the book names it.
STATUSES: dict[str, str] = {
    "polites": "Polites",
    "metoikos": "Metoikos",
}


def magi(tribunal: Tribunal) -> list[dict[str, Any]]:
    """Each magus's status, tokens, shards and services, in the order
    entered."""
    found = entries(tribunal, KEY, "magi")
    for entry in found:
        if "liturgies" in entry:
            entry.setdefault("services", entry.pop("liturgies"))
    return found


def archai(tribunal: Tribunal) -> list[dict[str, Any]]:
    """The Council of Magistrates' offices, in the order entered."""
    return entries(tribunal, KEY, "archai")


def phylai(tribunal: Tribunal) -> dict[str, str]:
    """Each covenant's phyle, by covenant id."""
    found = data(tribunal, KEY).setdefault("phylai", {})
    if not isinstance(found, dict):
        raise ValueError(f"The Tribunal's phylai should be a mapping, not {found!r}.")
    return found


def phyle_of(_saga: Saga, tribunal: Tribunal, covenant: Covenant) -> str:
    """The covenant's phyle, or "" if none is entered."""
    return phylai(tribunal).get(covenant.id, "")


def is_metoikos(entry: dict[str, Any]) -> bool:
    return entry.get("status") == "metoikos"


def _name(saga: Saga, character_id: str | None) -> str:
    character = saga.character(character_id)
    return character.name if character is not None else "(gone)"


def ostracised(saga: Saga, entry: dict[str, Any]) -> bool:
    """Whether the magus is ostracised this year."""
    until = entry.get("ostracised_until")
    return until is not None and until >= saga.current_year


def _offices_of(tribunal: Tribunal, character_id: str) -> list[str]:
    return [a["office"] for a in archai(tribunal) if a.get("holder_id") == character_id]


def standing(saga: Saga, tribunal: Tribunal, entry: dict[str, Any]) -> str:
    """The magus's offices, or that they are ostracised and until when."""
    if ostracised(saga, entry):
        return f"Ostracised to {entry['ostracised_until']}"
    return ", ".join(_offices_of(tribunal, entry.get("character_id", "")))


# -- the phylai --


def phyle_field(
    _saga: Saga, tribunal: Tribunal, covenant: Covenant | None
) -> DialogField:
    return DialogField(
        "phyle",
        "Phyle",
        "select",
        phylai(tribunal).get(covenant.id) if covenant is not None else None,
        options=[(f"{name}: {lands}", name) for name, lands in PHYLAI.items()],
        allow_blank=True,
        placeholder="(not entered)",
        hint="The tribe its magi belong to, set by where the covenant lies.",
    )


def save_phyle(tribunal: Tribunal, covenant: Covenant, value: Any) -> None:
    if value:
        phylai(tribunal)[covenant.id] = value
    else:
        phylai(tribunal).pop(covenant.id, None)


def covenant_phyle_fields(
    saga: Saga, tribunal: Tribunal, covenant: Covenant | None
) -> list[DialogField]:
    """A covenant's own form: its phyle."""
    return [phyle_field(saga, tribunal, covenant)]


def save_covenant_phyle(tribunal: Tribunal, ident: str, values: dict[str, Any]) -> None:
    if "phyle" not in values:
        return
    if values["phyle"]:
        phylai(tribunal)[ident] = values["phyle"]
    else:
        phylai(tribunal).pop(ident, None)


# -- tokens and shards --


def tokens_title(_saga: Saga, tribunal: Tribunal) -> str:
    return f"Tokens and Shards ({len(magi(tribunal))})"


def tokens_grid(saga: Saga, tribunal: Tribunal) -> Grid:
    """Each magus: their covenant, whether polites or metoikos, their tokens, shards and services, and their standing (an
    office, or ostracism)."""
    rows = []
    styles: dict[tuple[int, int], str] = {}
    for index, entry in enumerate(magi(tribunal)):
        character = saga.character(entry.get("character_id"))
        covenant = saga.covenant(character.covenant_id) if character else None
        if ostracised(saga, entry):
            styles[(index, 6)] = "$text-error"
        if is_metoikos(entry):
            styles[(index, 2)] = "$label"
        rows.append(
            [
                _name(saga, entry.get("character_id")),
                covenant.name if covenant is not None else "",
                STATUSES["metoikos" if is_metoikos(entry) else "polites"],
                str(entry.get("tokens", 0)),
                str(entry.get("shards", 0)),
                str(entry.get("services", 0)),
                standing(saga, tribunal, entry),
            ]
        )
    return Grid(
        ["Magus", "Covenant", "Status", "Tokens", "Shards", "Services", "Standing"],
        rows,
        list(range(len(rows))),
        "No magus's tokens recorded: a polites earns tokens for services to "
        "the community and shards for acts against its unity.",
        styles,
        caps=[20, 14, 8, 6, 6, 8, 0],
    )


def _magus_options(saga: Saga) -> list[tuple[str, str]]:
    return [(escape(c.name), c.id) for c in saga.characters if c.type == "magus"]


def token_fields(saga: Saga, entry: dict[str, Any] | None) -> list[DialogField]:
    e = entry or {}
    return [
        DialogField(
            "character_id",
            "Magus",
            "select",
            e.get("character_id"),
            options=_magus_options(saga),
            required=True,
            hint="A magus of the saga, at any detail.",
        ),
        DialogField(
            "status",
            "Status",
            "select",
            e.get("status", "polites"),
            options=[
                ("Polites (citizen)", "polites"),
                ("Metoikos (resident foreigner)", "metoikos"),
            ],
            hint="A metoikos is a guest, or a polites who has lost his rights.",
        ),
        DialogField("tokens", "Tokens", "int", e.get("tokens", 0)),
        DialogField("shards", "Shards", "int", e.get("shards", 0)),
        DialogField(
            "services",
            "Services",
            "int",
            e.get("services", 0),
            hint="Services to the community, each earning a token.",
        ),
        DialogField(
            "ostracised_until",
            "Ostracised until (year)",
            "optint",
            e.get("ostracised_until"),
            hint="Leave blank unless the Tribunal has ostracised them.",
        ),
        DialogField("why", "Why", "text", e.get("why", "")),
    ]


def _token_problem(values: dict[str, Any]) -> str | None:
    for key, words in (
        ("tokens", "Tokens"),
        ("shards", "Shards"),
        ("services", "Services"),
    ):
        if (values.get(key) or 0) < 0:
            return f"{words} can't be fewer than none."
    if values.get("status") == "metoikos" and (
        (values.get("tokens") or 0) or (values.get("shards") or 0)
    ):
        return "A metoikos holds no tokens or shards."
    return None


def token_ops(saga: Saga, tribunal: Tribunal) -> SectionOps:
    def form(entry: dict[str, Any] | None) -> Form:
        def apply(values: dict[str, Any]) -> None:
            target = entry if entry is not None else {}
            target.update(values)
            if entry is None:
                magi(tribunal).append(target)

        return Form(
            "Add a Magus's Tokens" if entry is None else "Edit Tokens and Shards",
            lambda: token_fields(saga, entry),
            apply,
            validate=_token_problem,
            save_label="Add" if entry is None else "Save",
        )

    def remove(index: int) -> Command:
        entry = magi(tribunal)[index]

        def apply() -> None:
            magi(tribunal).remove(entry)

        name = escape(_name(saga, entry.get("character_id")))
        return Confirm(f"Delete {name}'s tokens and shards?", apply)

    return SectionOps(
        add=lambda: form(None),
        edit=lambda index: form(magi(tribunal)[index]),
        remove=remove,
        rows=lambda: [_name(saga, m.get("character_id")) for m in magi(tribunal)],
    )


# -- neutralization --


def _entry(tribunal: Tribunal, character_id: str | None) -> dict[str, Any] | None:
    return next(
        (e for e in magi(tribunal) if e.get("character_id") == character_id), None
    )


def _count(entry: dict[str, Any] | None, key: str) -> int:
    return int((entry or {}).get(key) or 0)


def log(tribunal: Tribunal, name: str) -> list[dict[str, Any]]:
    """A list the package keeps of what was done between meetings
    ("neutralizations", "longevity_rituals"), oldest first."""
    return entries(tribunal, KEY, name)


def neutralize_problem(
    saga: Saga, tribunal: Tribunal, token_id: str | None, shard_id: str | None
) -> str | None:
    """Why the magus `token_id` can't spend a token to have `shard_id`
    serve a season and lose a shard (None: he can). Neutralization is
    between politai, a token for a shard, never between a magus and
    himself nor a magus of his own covenant (The Sundered Eagle pp.
    28-29)."""
    token_holder, shard_holder = saga.character(token_id), saga.character(shard_id)
    if token_holder is None or shard_holder is None:
        return "Choose the magus spending a token and the one with a shard."
    if token_holder.id == shard_holder.id:
        return "A magus can't neutralize his own shards with his own tokens."
    if (
        token_holder.covenant_id
        and token_holder.covenant_id == shard_holder.covenant_id
    ):
        return (
            f"{token_holder.name} and {shard_holder.name} share a covenant: a "
            "magus may not neutralize the shards of one of his own covenant."
        )
    for magus, key, words in (
        (token_holder, "tokens", "a token"),
        (shard_holder, "shards", "a shard"),
    ):
        entry = _entry(tribunal, magus.id)
        if entry is None or is_metoikos(entry) or _count(entry, key) < 1:
            return f"{magus.name} holds no {key}: neutralization needs {words}."
    return None


def neutralize(
    saga: Saga, tribunal: Tribunal, token_id: str, shard_id: str, service: str
) -> None:
    """A token and a shard surrendered to the witnessing Redcap, for a
    season's service owed by the shard's holder."""
    for ident, key in ((token_id, "tokens"), (shard_id, "shards")):
        entry = _entry(tribunal, ident)
        assert entry is not None
        entry[key] = _count(entry, key) - 1
    log(tribunal, "neutralizations").append(
        {
            "token_id": token_id,
            "shard_id": shard_id,
            "service": service,
            "year": saga.current_year,
            "season": saga.current_season,
        }
    )


def neutralize_form(saga: Saga, tribunal: Tribunal, entry: dict[str, Any]) -> Form:
    """The chosen magus's shard neutralized by another's token: who
    spends the token, and the season's service he asks for."""
    shard_id = entry.get("character_id")

    def fields() -> list[DialogField]:
        holders = [
            (escape(_name(saga, e.get("character_id"))), str(e.get("character_id")))
            for e in magi(tribunal)
            if not is_metoikos(e)
            and _count(e, "tokens") > 0
            and e.get("character_id") != shard_id
        ]
        return [
            DialogField(
                "shard",
                "",
                "info",
                f"{escape(_name(saga, shard_id))} holds {_count(entry, 'shards')} "
                "shards, and may refuse the service.",
            ),
            DialogField(
                "token_id",
                "Token spent by",
                "select",
                None,
                options=holders,
                required=True,
                hint="A magus of another covenant; a Redcap witnesses it.",
            ),
            DialogField(
                "service",
                "The season's service",
                "text",
                "",
                required=True,
                placeholder="e.g. a season's help in the laboratory",
            ),
        ]

    def validate(values: dict[str, Any]) -> str | None:
        return neutralize_problem(saga, tribunal, values.get("token_id"), shard_id)

    def apply(values: dict[str, Any]) -> None:
        assert shard_id is not None
        neutralize(saga, tribunal, values["token_id"], shard_id, values["service"])

    return Form(
        "Neutralize a Shard",
        fields,
        apply,
        validate=validate,
        save_label="Neutralize",
    )


def neutralize_step(saga: Saga, tribunal: Tribunal, row: int) -> Command:
    """More's Neutralize on the chosen magus: his shard for another's
    token."""
    entry = magi(tribunal)[row]
    name = escape(_name(saga, entry.get("character_id")))
    if is_metoikos(entry) or _count(entry, "shards") < 1:
        return Refuse("Neutralize a Shard", f"{name} holds no shard to neutralize.")
    return neutralize_form(saga, tribunal, entry)


# -- the Tribunal's Longevity Ritual --

#: The tokens earned for crafting the Tribunal's Longevity Ritual: one,
#: or two for a Ritual of the tenth magnitude or more (p. 28).
CRAFTER_TOKENS, GREAT_CRAFTER_TOKENS = 1, 2


def longevity_eligible(saga: Saga, tribunal: Tribunal) -> list[dict[str, Any]]:
    """The magi who may apply for the Ritual the Tribunal sponsors each
    year: politai with no shard and no Longevity Ritual in force (The
    Sundered Eagle p. 30)."""
    found = []
    for entry in magi(tribunal):
        magus = saga.character(entry.get("character_id"))
        if magus is None or is_metoikos(entry) or ostracised(saga, entry):
            continue
        if _count(entry, "shards") or magus.aging.longevity_modifier > 0:
            continue
        found.append(entry)
    return found


def longevity_winner(
    saga: Saga, applicants: list[dict[str, Any]]
) -> dict[str, Any] | None:
    """The applicant with the most tokens; on a tie the elder."""

    def key(entry: dict[str, Any]) -> tuple[int, int]:
        magus = saga.character(entry.get("character_id"))
        born = magus.background.year_born if magus is not None else None
        return (-_count(entry, "tokens"), born if born is not None else 10**6)

    with_tokens = [e for e in applicants if _count(e, "tokens") > 0]
    return min(with_tokens, key=key) if with_tokens else None


def longevity_form(saga: Saga, tribunal: Tribunal) -> Form:
    """This year's sponsored Longevity Ritual: the applicants, and who
    crafts it. The winner surrenders all his tokens; the crafter earns
    one, or two for a Ritual of tenth magnitude or more."""
    eligible = longevity_eligible(saga, tribunal)

    def fields() -> list[DialogField]:
        found = [
            DialogField(
                f"apply_{e['character_id']}",
                f"Applies: {escape(_name(saga, e['character_id']))} "
                f"({_count(e, 'tokens')} tokens)",
                "check",
                _count(e, "tokens") > 0,
            )
            for e in eligible
        ]
        found += [
            DialogField(
                "crafter_id",
                "Crafted by",
                "select",
                None,
                options=_magus_options(saga),
                allow_blank=True,
                placeholder="(not yet chosen)",
                hint="A volunteer, traditionally at Epidauros.",
            ),
            DialogField(
                "great",
                "A Ritual of the 10th magnitude or more",
                "check",
                False,
                hint="Earns the crafter two tokens rather than one.",
            ),
        ]
        return found

    def chosen(values: dict[str, Any]) -> dict[str, Any] | None:
        applied = [e for e in eligible if values.get(f"apply_{e['character_id']}")]
        return longevity_winner(saga, applied)

    def validate(values: dict[str, Any]) -> str | None:
        if any(
            r.get("year") == saga.current_year
            for r in log(tribunal, "longevity_rituals")
        ):
            return f"The Tribunal has sponsored its Ritual for {saga.current_year}."
        if chosen(values) is None:
            return "No applicant holds a token: there is no one to sponsor."
        return None

    def apply(values: dict[str, Any]) -> None:
        winner = chosen(values)
        assert winner is not None
        record: dict[str, Any] = {
            "year": saga.current_year,
            "winner_id": winner["character_id"],
            "tokens": _count(winner, "tokens"),
        }
        winner["tokens"] = 0
        crafter = values.get("crafter_id")
        if crafter:
            entry = _entry(tribunal, crafter)
            if entry is not None and not is_metoikos(entry):
                earned = GREAT_CRAFTER_TOKENS if values.get("great") else CRAFTER_TOKENS
                entry["tokens"] = _count(entry, "tokens") + earned
                record.update(crafter_id=crafter, crafter_tokens=earned)
        log(tribunal, "longevity_rituals").append(record)

    return Form(
        "The Tribunal's Longevity Ritual",
        fields,
        apply,
        validate=validate,
        save_label="Award",
    )


# -- loans of vis from the treasury --

#: A loan of more pawns than this, not for an emergency, needs the People's
#: Assembly's approval (The Sundered Eagle p. 28 says "large" and gives no
#: number).
LARGE_LOAN = 10


def loan_holders(tribunal: Tribunal) -> dict[str, str]:
    """The magus each treasury loan made by Lend Vis went to: character
    id by the loan's treasury id."""
    found = data(tribunal, KEY).setdefault("loan_holders", {})
    if not isinstance(found, dict):
        raise ValueError(f"The loans' holders should be a mapping, not {found!r}.")
    return found


def loans_of(saga: Saga, tribunal: Tribunal, character_id: str) -> list[TreasuryEntry]:
    """The magus's loans of vis not yet repaid: those lent him by Lend
    Vis, and any typed in under his name."""
    holders = loan_holders(tribunal)
    name = _name(saga, character_id)
    return [
        e
        for e in tribunal.treasury
        if e.kind == "loan"
        and not e.paid
        and e.art
        and (
            holders.get(e.id) == character_id or (e.id not in holders and e.who == name)
        )
    ]


def _vis_in_hand(tribunal: Tribunal, art: str) -> float:
    return treasury.balance(tribunal).get(art, 0)


def lend_problem(values: dict[str, Any]) -> str | None:
    """Why the loan can't be made as entered (None: it can)."""
    pawns = values.get("pawns") or 0
    if pawns < 1:
        return "Lend at least a pawn."
    if (
        pawns > LARGE_LOAN
        and not values.get("emergency")
        and not values.get("assembly")
    ):
        return (
            f"A loan of more than {LARGE_LOAN} pawns, not for an emergency, needs "
            "the People's Assembly's approval."
        )
    return None


def lend_form(saga: Saga, tribunal: Tribunal, entry: dict[str, Any]) -> Form:
    """A polites's petition to the tamias for vis from the Tribunal's
    coffers, repaid by a plan agreed with him and without interest, since
    usury is a sin; a large loan not for an emergency must be approved by
    the People's Assembly (The Sundered Eagle pp. 28, 30)."""
    ident = str(entry.get("character_id"))
    name = _name(saga, ident)

    def fields() -> list[DialogField]:
        return [
            DialogField(
                "who",
                "",
                "info",
                f"{escape(name)} petitions the tamias for vis, repaid without interest.",
            ),
            DialogField(
                "art",
                "Art",
                "select",
                "Vim",
                options=[(art, art) for art in ARTS],
                required=True,
            ),
            DialogField("pawns", "Pawns", "int", 0),
            DialogField(
                "due_year",
                "Repaid by (year)",
                "optint",
                tribunal.next_year,
                hint="The plan's last payment; the next meeting unless agreed otherwise.",
            ),
            DialogField(
                "plan",
                "Repayment plan",
                "text",
                "",
                placeholder="e.g. two pawns a year from his Creo source",
            ),
            DialogField(
                "emergency",
                "For an emergency",
                "check",
                False,
                hint="Healing or another need for Ritual magic: no vote is needed.",
            ),
            DialogField(
                "assembly",
                "Approved by the People's Assembly",
                "check",
                False,
                show_if=lambda v: (
                    (v.get("pawns") or 0) > LARGE_LOAN and not v.get("emergency")
                ),
                hint=f"Needed for a loan of more than {LARGE_LOAN} pawns.",
            ),
            DialogField(
                "into_vis",
                "Into the magus's own vis",
                "check",
                True,
                hint="The pawns join his vis, for his project.",
            ),
        ]

    def live(values: dict[str, Any]) -> str:
        art = values.get("art") or "Vim"
        held = _vis_in_hand(tribunal, art)
        whole = int(held) if float(held).is_integer() else held
        return (
            f"The treasury's record holds {whole} pawns of {escape(art)}; the "
            "vaults on Delos hold several hundred more."
        )

    def apply(values: dict[str, Any]) -> None:
        pawns = int(values["pawns"])
        art = values.get("art") or "Vim"
        terms = ["interest-free"]
        if values.get("plan"):
            terms.append(f"plan: {values['plan']}")
        if values.get("emergency"):
            terms.append("for an emergency")
        elif values.get("assembly"):
            terms.append("approved by the People's Assembly")
        loan = TreasuryEntry(
            "loan",
            pawns,
            art=art,
            who=name,
            due_year=values.get("due_year"),
            note=f"Lent {saga.current_year}, " + "; ".join(terms),
        )
        tribunal.treasury.append(loan)
        loan_holders(tribunal)[loan.id] = ident
        magus = saga.character(ident)
        if values.get("into_vis") and magus is not None:
            key = art.lower()
            magus.raw_vis[key] = magus.raw_vis.get(key, 0) + pawns

    return Form(
        "Lend Vis from the Treasury",
        fields,
        apply,
        validate=lend_problem,
        live=live,
        save_label="Lend",
    )


def lend_step(saga: Saga, tribunal: Tribunal, row: int) -> Command:
    """More's Lend Vis on the chosen magus: only a polites may borrow."""
    entry = magi(tribunal)[row]
    name = escape(_name(saga, entry.get("character_id")))
    if saga.character(entry.get("character_id")) is None:
        return Refuse("Lend Vis", f"{name} is no longer in the saga.")
    if is_metoikos(entry) or ostracised(saga, entry):
        return Refuse(
            "Lend Vis",
            f"{name} is not a polites: only a citizen may petition the "
            "treasurer for a loan.",
        )
    return lend_form(saga, tribunal, entry)


def repay_form(saga: Saga, tribunal: Tribunal, character_id: str) -> Form:
    """A loan repaid: the pawns lent, no more, since the Tribunal takes no
    interest (The Sundered Eagle p. 28)."""
    loans = loans_of(saga, tribunal, character_id)
    magus = saga.character(character_id)

    def fields() -> list[DialogField]:
        return [
            DialogField(
                "loan",
                "Loan",
                "select",
                loans[0].id,
                options=[
                    (
                        escape(
                            treasury.amount_text(e)
                            + (f", due {e.due_year}" if e.due_year else "")
                        ),
                        e.id,
                    )
                    for e in loans
                ],
                required=True,
                hint="Repaid as lent: the Tribunal takes no interest.",
            ),
            DialogField(
                "from_vis",
                "From the magus's own vis",
                "check",
                True,
            ),
        ]

    def chosen(values: dict[str, Any]) -> TreasuryEntry:
        return next((e for e in loans if e.id == values.get("loan")), loans[0])

    def validate(values: dict[str, Any]) -> str | None:
        loan = chosen(values)
        if values.get("from_vis") and magus is not None:
            has = magus.raw_vis.get(loan.art.lower(), 0)
            if has < loan.amount:
                return (
                    f"{magus.name} has {has} pawns of {loan.art}: the loan is "
                    f"{treasury.amount_text(loan)}."
                )
        return None

    def apply(values: dict[str, Any]) -> None:
        loan = chosen(values)
        loan.paid = True
        loan.note = f"{loan.note}; repaid {saga.current_year}".lstrip("; ")
        if values.get("from_vis") and magus is not None:
            key = loan.art.lower()
            magus.raw_vis[key] = magus.raw_vis.get(key, 0) - int(loan.amount)
            if not magus.raw_vis[key]:
                del magus.raw_vis[key]

    return Form(
        "Repay a Loan of Vis", fields, apply, validate=validate, save_label="Repay"
    )


def repay_step(saga: Saga, tribunal: Tribunal, row: int) -> Command:
    """More's Repay on the chosen magus: one of his loans of vis."""
    entry = magi(tribunal)[row]
    ident = str(entry.get("character_id"))
    if not loans_of(saga, tribunal, ident):
        name = escape(_name(saga, ident))
        return Refuse("Repay a Loan", f"{name} owes the treasury no vis.")
    return repay_form(saga, tribunal, ident)


# -- the Council of Magistrates --


def archai_title(_saga: Saga, tribunal: Tribunal) -> str:
    return f"The Council of Magistrates ({len(archai(tribunal))})"


def archai_grid(saga: Saga, tribunal: Tribunal) -> Grid:
    """Each office: who holds it, when their term ends, and its duties."""
    rows = []
    styles: dict[tuple[int, int], str] = {}
    for index, office in enumerate(archai(tribunal)):
        holder = office.get("holder_id")
        if not holder:
            styles[(index, 1)] = "$label"
        ends = office.get("term_ends")
        rows.append(
            [
                office["office"],
                _name(saga, holder) if holder else "vacant",
                f"to {ends}" if ends is not None else "",
                office.get("duties", ""),
            ]
        )
    return Grid(
        ["Office", "Holder", "Term", "Duties"],
        rows,
        list(range(len(rows))),
        "No magistrates recorded: the archon, the polemarch, the logothete "
        "and the archai, chosen at each meeting.",
        styles,
        caps=[22, 20, 7, 0],
        stretch=3,
    )


def archon_fields(saga: Saga, office: dict[str, Any] | None) -> list[DialogField]:
    o = office or {}
    return [
        DialogField(
            "office",
            "Office",
            "text",
            o.get("office", ""),
            required=True,
            placeholder="e.g. Polemarch",
        ),
        DialogField(
            "holder_id",
            "Held by",
            "select",
            o.get("holder_id"),
            options=_magus_options(saga),
            allow_blank=True,
            placeholder="(vacant)",
        ),
        DialogField("term_ends", "Term ends (year)", "optint", o.get("term_ends")),
        DialogField(
            "duties",
            "Duties",
            "text",
            o.get("duties", ""),
            placeholder="e.g. Enforces the Tribunal's sentences",
        ),
    ]


def archon_ops(saga: Saga, tribunal: Tribunal) -> SectionOps:
    def form(office: dict[str, Any] | None) -> Form:
        def apply(values: dict[str, Any]) -> None:
            target = office if office is not None else {}
            target.update(values)
            target["holder_id"] = values.get("holder_id") or None
            if office is None:
                archai(tribunal).append(target)

        return Form(
            "Add an Office" if office is None else "Edit an Office",
            lambda: archon_fields(saga, office),
            apply,
            save_label="Add" if office is None else "Save",
        )

    def remove(index: int) -> Command:
        office = archai(tribunal)[index]

        def apply() -> None:
            archai(tribunal).remove(office)

        return Confirm(f"Delete the office {escape(office['office'])}?", apply)

    return SectionOps(
        add=lambda: form(None),
        edit=lambda index: form(archai(tribunal)[index]),
        remove=remove,
        rows=lambda: [a["office"] for a in archai(tribunal)],
    )


THEBAN = TribunalPackage(
    KEY,
    "Theban",
    customs="The Polity",
    book="TSE",
    quorum_needs_quaesitor=False,
    redcaps_vote=False,
    praeco_votes=True,
    columns=(RosterColumn("Phyle", phyle_of, 10, phyle_field, save_phyle),),
    tabs=(
        PackageTab(
            "The Polity",
            "tab-trib-tokens",
            (
                PackageList(
                    TOKENS_SECTION,
                    tokens_title,
                    tokens_grid,
                    token_ops,
                    more=(
                        PackageVerb("neutralize_shard", "Neutralize", neutralize_step),
                        PackageVerb(
                            "tribunal_longevity",
                            "Longevity Ritual",
                            lambda saga, tribunal, _row: longevity_form(saga, tribunal),
                        ),
                        PackageVerb("lend_vis", "Lend Vis", lend_step),
                        PackageVerb("repay_vis_loan", "Repay a Loan", repay_step),
                    ),
                ),
                PackageList(ARCHAI_SECTION, archai_title, archai_grid, archon_ops),
            ),
        ),
    ),
    meeting_steps=(
        "assembly",
        "apprentice_presentation",
        "ostrakismos",
        "sentences",
        "conduct_of_archai",
        "common_vis",
        "end_of_term",
        "sortition",
        "archon_polemarch",
        "propitiation",
    ),
    about="Its magi are politai or metoikoi, each voting once; a polites "
    "earns tokens for services and shards for wrongs; its covenants belong "
    "to four phylai; and its Council of Magistrates is chosen at each "
    "meeting.",
    covenant_fields=covenant_phyle_fields,
    save_covenant=save_covenant_phyle,
    coins=coinage.pounds_in_coins,
)

register(THEBAN)

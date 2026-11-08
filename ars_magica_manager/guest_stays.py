"""A stay as a guest at another covenant of the saga: Stay as Guest on a
magus, the host's Guests list, and Pay the Fee.

The stay (models.GuestStay) names the host, when it began and the year it
ends with, the yearly fee and whether the guest may use the host's
library and has a laboratory there. While it lasts, the guest's casting
counts the host's aura (unless Current Location says he is elsewhere),
and the host's library is open to him for study and copying when the
terms say so (scribal hospitality, DE p. 381). His seasons, laboratory
work, aging and warping stay with his own records. A host of the Rhine
Tribunal starts from its Peripheral Code's terms (rules.hospitality).

Pay the Fee hands the year's vis or silver from the guest to the host as
Give does, both Diaries saying so; a fee in service is written in both
Diaries. Either marks that year paid.

Pattern: commands.Form over the character (as Current Location), the
Guests list's Edit in the sheet's core_ops, like any section's.
"""

from __future__ import annotations

from typing import Any

from . import giving, tribunals, viewing, vis
from .commands import Command, Form, Refuse, SectionOps, notes
from .form_spec import DialogField, pairs
from .grids import Grid
from .markup import escape
from .models import (
    FEE_NONE,
    FEE_SERVICE,
    FEE_SILVER,
    FEE_VIS,
    SEASONS,
    Character,
    Covenant,
    CovenantDiaryEntry,
    DiaryEntry,
    GuestStay,
    Saga,
)
from .rules import hospitality, realms
from .rules.hospitality import Terms
from .sections import GUESTS_SECTION

TITLE = "Stay as Guest"
HELP_ID = "guest-stay"
PAY_TITLE = "Pay the Fee"
#: The Staying select's value for no stay.
NOT_A_GUEST = ""
#: The Tribunal package whose Peripheral Code sets the terms.
RHINE = "rhine"

_FEE_LABELS = {
    FEE_VIS: "Pawns of vis a year",
    FEE_SILVER: "Pounds of silver a year",
    FEE_SERVICE: "Seasons of service a year",
    FEE_NONE: "No fee",
}


def host_terms(saga: Saga, covenant: Covenant | None) -> Terms | None:
    """The host's usual conditions of hospitality: the Rhine's Peripheral
    Code for a covenant of a Rhine Tribunal; None (the troupe agrees
    them) elsewhere."""
    if covenant is None:
        return None
    tribunal = tribunals.of(saga, covenant)
    if tribunal is not None and tribunal.package == RHINE:
        return hospitality.RHINE_TERMS
    return None


def hosts(saga: Saga, character: Character) -> list[Covenant]:
    """The covenants he could stay at: every one but his own."""
    return [c for c in viewing.shown(saga.covenants) if c.id != character.covenant_id]


def host_of(saga: Saga, character: Character) -> Covenant | None:
    stay = character.stay
    return saga.covenant(stay.host_id) if stay is not None else None


def _terms_fill(saga: Saga, values: dict[str, Any]) -> dict[str, Any]:
    """The host's own terms, filled in when the host is chosen."""
    terms = host_terms(saga, saga.covenant(values.get("host") or None))
    if terms is None:
        return {}
    year = values.get("year")
    return {
        "fee_kind": terms.fee_kind,
        "fee": terms.fee,
        "laboratory": terms.laboratory,
        **(
            {"until_year": year + terms.shortest - 1}
            if isinstance(year, int) and terms.shortest is not None
            else {}
        ),
    }


def _staying(values: dict[str, Any]) -> bool:
    return bool(values.get("host"))


def _fee_asked(values: dict[str, Any]) -> bool:
    return _staying(values) and values.get("fee_kind") not in (None, FEE_NONE)


def fields(saga: Saga, character: Character) -> list[DialogField]:
    stay = character.stay
    covenants = hosts(saga, character)
    if stay is None:
        # A new stay starts now, on the first host's terms.
        first = covenants[0] if covenants else None
        terms = host_terms(saga, first)
        stay = GuestStay(
            "",
            year=saga.current_year,
            season=saga.current_season,
            until_year=(
                saga.current_year + terms.shortest - 1
                if terms is not None and terms.shortest is not None
                else None
            ),
            fee_kind=terms.fee_kind if terms is not None else FEE_NONE,
            fee=terms.fee if terms is not None else 0,
            laboratory=terms.laboratory if terms is not None else False,
        )
        host_value = NOT_A_GUEST
    else:
        host_value = stay.host_id
    return [
        DialogField(
            "host",
            "Staying at",
            "select",
            host_value,
            options=[
                ("Not a guest anywhere", NOT_A_GUEST),
                *((escape(c.name), c.id) for c in covenants),
            ],
            fills=lambda values: _terms_fill(saga, values),
            hint="A Rhine covenant's Peripheral Code fills in its terms.",
        ),
        DialogField(
            "year",
            "Since (year)",
            "int",
            stay.year or saga.current_year,
            show_if=_staying,
        ),
        DialogField(
            "season",
            "Since (season)",
            "select",
            stay.season or saga.current_season,
            options=pairs(SEASONS),
            show_if=_staying,
        ),
        DialogField(
            "until_year",
            "Until the end of",
            "optint",
            stay.until_year,
            placeholder="open-ended",
            show_if=_staying,
        ),
        DialogField(
            "fee_kind",
            "Fee",
            "select",
            stay.fee_kind,
            options=[(label, kind) for kind, label in _FEE_LABELS.items()],
            show_if=_staying,
        ),
        DialogField("fee", "How many", "int", stay.fee, show_if=_fee_asked),
        DialogField(
            "library",
            "May study and copy from its library",
            "check",
            stay.library,
            show_if=_staying,
        ),
        DialogField(
            "laboratory",
            "Has a laboratory there",
            "check",
            stay.laboratory,
            show_if=_staying,
        ),
        DialogField(
            "terms",
            "Conditions of hospitality",
            "area",
            stay.terms,
            show_if=_staying,
        ),
    ]


def validate(saga: Saga, values: dict[str, Any]) -> str | None:
    if not _staying(values):
        return None
    if _fee_asked(values) and int(values.get("fee") or 0) < 1:
        return "Give the fee, or choose No fee."
    terms = host_terms(saga, saga.covenant(values.get("host") or None))
    return hospitality.length_problem(
        terms, values.get("year"), values.get("until_year")
    )


def _write(
    saga: Saga, character: Character, host: Covenant, mine: str, its: str
) -> None:
    """A line in the guest's Diary and one in the host's."""
    year, season = saga.current_year, saga.current_season
    character.diary.append(DiaryEntry(year=year, season=season, name=mine))
    host.diary.append(
        CovenantDiaryEntry(year=year, season=season, name=its, category="Inhabitants")
    )


def live(saga: Saga, character: Character, values: dict[str, Any]) -> str:
    host = saga.covenant(values.get("host") or None)
    if host is None:
        if character.stay is None:
            return f"{escape(character.name)} is at home."
        left = host_of(saga, character)
        return (
            f"Saving ends the stay at {escape(left.name) if left else 'its host'}: "
            "both Diaries say so."
        )
    aura, realm = realms.aura_of(host)
    terms = host_terms(saga, host)
    lines = [
        f"While a guest, his casting counts {escape(host.name)}'s {realm} aura of "
        f"{aura}, unless Current Location says he is elsewhere."
    ]
    if values.get("library"):
        lines.append(
            "Its library's books join those he may study and copy (scribal "
            "hospitality, DE p. 381)."
        )
    if terms is not None:
        lines.append(
            f"{escape(host.name)} keeps the Rhine's Peripheral Code: at least 3 "
            "years and at most 7, 3 pawns of vis a year or a season's service, "
            "no laboratory owed (Guardians of the Forests p. 20)."
        )
    return "\n".join(lines)


def apply(saga: Saga, character: Character, values: dict[str, Any]) -> list[str]:
    before = host_of(saga, character)
    host = saga.covenant(values.get("host") or None)
    if host is None:
        character.stay = None
        if before is None:
            return []
        _write(
            saga,
            character,
            before,
            f"Left {before.name}, where he was a guest",
            f"{character.name}'s stay as a guest ended",
        )
        return notes(f"{escape(character.name)}'s stay at {escape(before.name)} ended.")
    kind = str(values.get("fee_kind") or FEE_NONE)
    stay = GuestStay(
        host.id,
        year=values.get("year"),
        season=str(values.get("season") or ""),
        until_year=values.get("until_year"),
        fee_kind=kind,
        fee=int(values.get("fee") or 0) if kind != FEE_NONE else 0,
        library=bool(values.get("library")),
        laboratory=bool(values.get("laboratory")),
        terms=str(values.get("terms") or ""),
        paid=list(character.stay.paid)
        if character.stay is not None and character.stay.host_id == host.id
        else [],
    )
    character.stay = stay
    if before is not host:
        if before is not None:
            _write(
                saga,
                character,
                before,
                f"Left {before.name}, where he was a guest",
                f"{character.name}'s stay as a guest ended",
            )
        _write(
            saga,
            character,
            host,
            f"A guest at {host.name}: {hospitality.fee_words(stay)}",
            f"{character.name} came as a guest: {hospitality.fee_words(stay)}",
        )
    return notes(f"{escape(character.name)} is a guest at {escape(host.name)}.")


def stay_form(saga: Saga, character: Character | None) -> Command:
    if character is None:
        return Refuse(TITLE, "Choose a character first.")
    if not hosts(saga, character):
        return Refuse(TITLE, "The saga has no other covenant for him to stay at.")
    return Form(
        f"{TITLE}: {escape(character.name)}",
        lambda: fields(saga, character),
        lambda values: apply(saga, character, values),
        validate=lambda values: validate(saga, values),
        live=lambda values: live(saga, character, values),
        help_id=HELP_ID,
        inspector="The Stay",
    )


# -- the host's Guests list --


def guests(saga: Saga, covenant: Covenant) -> list[Character]:
    """The characters staying at the covenant as its guests, by name."""
    return sorted(
        (c for c in saga.characters if hospitality.guest_at(c, covenant.id)),
        key=lambda c: c.name.casefold(),
    )


def title(saga: Saga, covenant: Covenant) -> str:
    return f"Guests ({len(guests(saga, covenant))})"


def _when(year: int | None, season: str) -> str:
    return f"{season} {year}".strip() if year is not None else season


def _this_year(saga: Saga, stay: GuestStay) -> str:
    year = saga.current_year
    if stay.fee <= 0:
        return ""
    if year in stay.paid:
        return "Paid"
    return "Due" if hospitality.due(stay, year) else ""


def grid(saga: Saga, covenant: Covenant) -> Grid:
    rows: list[list[str]] = []
    styles: dict[tuple[int, int], str] = {}
    for index, guest in enumerate(guests(saga, covenant)):
        stay = guest.stay
        assert stay is not None
        paid = _this_year(saga, stay)
        if paid == "Due":
            styles[(index, 4)] = "$text-warning"
        rows.append(
            [
                guest.name,
                _when(stay.year, stay.season),
                str(stay.until_year) if stay.until_year is not None else "",
                hospitality.fee_words(stay),
                paid,
            ]
        )
    return Grid(
        ["Guest", "Since", "Until", "Fee", "This Year"],
        rows,
        list(range(len(rows))),
        "None: Stay as Guest, on a magus's Casting Scores, makes one.",
        styles,
        caps=[24, 12, 6, 34, 0],
    )


def detail_text(saga: Saga, covenant: Covenant, row: int | None) -> str:
    """The chosen guest's stay (markup)."""
    found = guests(saga, covenant)
    if row is None or not 0 <= row < len(found):
        return "[$label]Choose a guest to see the terms of his stay.[/]"
    guest = found[row]
    stay = guest.stay
    assert stay is not None
    home = saga.covenant(guest.covenant_id)
    lines = [
        f"[b]{escape(guest.name)}[/], of {escape(home.name) if home else 'no covenant'}",
        f"[$label]Since:[/] {_when(stay.year, stay.season)}"
        + (f"; until the end of {stay.until_year}" if stay.until_year else ""),
        f"[$label]Fee:[/] {hospitality.fee_words(stay)}"
        + (
            f"; paid for {', '.join(str(y) for y in sorted(stay.paid))}"
            if stay.paid
            else ""
        ),
        "[$label]Library:[/] "
        + ("may study and copy" if stay.library else "closed to him")
        + "; [$label]laboratory:[/] "
        + ("one of the covenant's" if stay.laboratory else "none given"),
    ]
    if stay.terms.strip():
        lines += ["", escape(stay.terms.strip())]
    return "\n".join(lines)


def ops(saga: Saga, covenant: Covenant) -> SectionOps:
    """The Guests list's Edit: the chosen guest's Stay as Guest."""
    return SectionOps(
        edit=lambda row: stay_form(saga, guests(saga, covenant)[row]),
        rows=lambda: [g.name for g in guests(saga, covenant)],
    )


def section_ops(saga: Saga, covenant: Covenant) -> dict[str, SectionOps]:
    return {GUESTS_SECTION: ops(saga, covenant)}


# -- Pay the Fee --


def can_pay(saga: Saga, covenant: Covenant, row: int | None) -> bool:
    """Whether the chosen guest owes this year's fee."""
    found = guests(saga, covenant)
    if row is None or not 0 <= row < len(found):
        return False
    stay = found[row].stay
    return stay is not None and hospitality.due(stay, saga.current_year)


def _vis_options(guest: Character) -> list[tuple[str, str]]:
    return [
        (escape(held.label), str(index))
        for index, held in enumerate(vis.held(guest))
        if held.pawns > 0
    ]


def pay_form(saga: Saga, covenant: Covenant, row: int | None) -> Command:
    found = guests(saga, covenant)
    if row is None or not 0 <= row < len(found):
        return Refuse(PAY_TITLE, "Choose a guest first.")
    guest = found[row]
    stay = guest.stay
    assert stay is not None
    year = saga.current_year
    if not hospitality.due(stay, year):
        return Refuse(PAY_TITLE, f"{escape(guest.name)} owes no fee for {year}.")
    heading = f"{PAY_TITLE}: {escape(guest.name)}, {year}"
    if stay.fee_kind == FEE_VIS:
        options = _vis_options(guest)
        if not options:
            return Refuse(
                PAY_TITLE,
                f"{escape(guest.name)} holds no vis. Give him some, or record the "
                "fee as paid another way by editing the stay.",
            )

        def pay_vis(values: dict[str, Any]) -> list[str]:
            held = vis.held(guest)[int(values["store"])]
            pawns = int(values.get("pawns") or 0)
            what = giving.give_now(saga, giving.VIS, guest, held, pawns, covenant)
            stay.paid.append(year)
            return notes(f"Paid {escape(what)} to {escape(covenant.name)}.")

        def vis_problem(values: dict[str, Any]) -> str | None:
            held = vis.held(guest)[int(values["store"])]
            return giving.problem(
                giving.VIS, guest, held, int(values.get("pawns") or 0)
            )

        return Form(
            heading,
            lambda: [
                DialogField(
                    "store", "From his vis", "select", options[0][1], options=options
                ),
                DialogField("pawns", "Pawns", "int", stay.fee),
            ],
            pay_vis,
            validate=vis_problem,
            save_label="Pay",
            help_id=HELP_ID,
        )
    if stay.fee_kind == FEE_SILVER:

        def pay_silver(values: dict[str, Any]) -> list[str]:
            pounds = int(values.get("pounds") or 0)
            what = giving.give_now(saga, giving.SILVER, guest, None, pounds, covenant)
            stay.paid.append(year)
            return notes(f"Paid {escape(what)} to {escape(covenant.name)}.")

        return Form(
            heading,
            lambda: [DialogField("pounds", "Pounds", "int", stay.fee)],
            pay_silver,
            validate=lambda values: giving.problem(
                giving.SILVER, guest, None, int(values.get("pounds") or 0)
            ),
            save_label="Pay",
            help_id=HELP_ID,
        )

    def serve(values: dict[str, Any]) -> list[str]:
        what = str(values.get("service") or "").strip()
        served = f"{stay.fee} season{'s' if stay.fee != 1 else ''} of service"
        _write(
            saga,
            guest,
            covenant,
            f"Served {covenant.name} for his hospitality ({served})"
            + (f": {what}" if what else ""),
            f"{guest.name} served the covenant for his hospitality ({served})"
            + (f": {what}" if what else ""),
        )
        stay.paid.append(year)
        return notes(f"{escape(guest.name)}'s service for {year} is written down.")

    return Form(
        heading,
        lambda: [
            DialogField(
                "service",
                "The service given",
                "text",
                "",
                placeholder="what he did for the covenant",
            )
        ],
        serve,
        save_label="Record",
        help_id=HELP_ID,
    )

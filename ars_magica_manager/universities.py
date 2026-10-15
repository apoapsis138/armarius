"""A university or school in detail (Art & Academe): what kind of school
it is, its fees, its faculties and its masters; and what is worked out
from them: the highest an Academic Ability can be taught there, the
degrees it grants, and each master's Academic Reputation from the
licence he holds.

Every university has a Faculty of Arts and at least one higher faculty
(Medicine, Law or Theology), each with six to twelve endowed chairs. A
student there pays 2 pounds a year for tuition, food and rent, and 2 for
books. A licence starts its holder's Good Academic Reputation: 1 for a
Baccalaureus, 2 for a Magister in Artibus or a cathedral school master,
3 for a Doctor.

Kept in Neighbour.details: "school", "fees", "faculties" (each
{"faculty", "rector", "chairs"}) and "masters" (each {"name", "licence",
"faculty", "who"}: "who" a character's id, or None)."""

from __future__ import annotations

from typing import Any

from .character_sheet import Fact
from .commands import SectionOps
from .form_spec import DialogField, pairs
from .grids import Grid
from .markup import escape
from .models import Neighbour, Saga
from .neighbour_lists import KindList, KindTab, details_list, list_ops
from .sections import FACULTIES_SECTION, MASTERS_SECTION

#: The kinds of school: the highest an Academic Ability can be taught
#: there (None for a university's, which has no limit), and its yearly
#: fees in pounds.
SCHOOLS: dict[str, tuple[int | None, float]] = {
    "University": (None, 4),
    "Cathedral school": (6, 1),
    "Monastic school": (4, 0),
    "Urban school": (5, 0.3),
    "Urban parish school": (3, 0.2),
    "Rural parish school": (2, 0.1),
}

FACULTIES: tuple[str, ...] = ("Arts", "Medicine", "Law", "Theology")

#: Each licence, and the Good Academic Reputation it starts.
LICENCES: dict[str, int] = {
    "Baccalaureus": 1,
    "Magister in Artibus": 2,
    "Cathedral school master": 2,
    "Doctor": 3,
}


# -- the record --


def school(neighbour: Neighbour) -> str:
    found = neighbour.details.get("school")
    return found if found in SCHOOLS else "University"


def faculties(neighbour: Neighbour) -> list[dict[str, Any]]:
    return details_list(neighbour, "faculties")


def masters(neighbour: Neighbour) -> list[dict[str, Any]]:
    return details_list(neighbour, "masters")


# -- worked out --


def fees(neighbour: Neighbour) -> float:
    """A student's fees a year, in pounds: those entered, or its kind's."""
    entered = neighbour.details.get("fees")
    return float(entered) if entered is not None else SCHOOLS[school(neighbour)][1]


def degrees(neighbour: Neighbour) -> list[str]:
    """The licences it grants: a university's from its faculties."""
    if school(neighbour) != "University":
        return []
    held = {f.get("faculty") for f in faculties(neighbour)}
    found = ["Baccalaureus", "Magister in Artibus"] if "Arts" in held else []
    return found + [
        f"Doctor in {f}" for f in ("Medicine", "Law", "Theology") if f in held
    ]


def _pounds(amount: float) -> str:
    return f"{amount:g} pound{'' if amount == 1 else 's'}"


def facts(_saga: Saga, neighbour: Neighbour) -> list[Fact]:
    kind = school(neighbour)
    limit = SCHOOLS[kind][0]
    found = [
        Fact("School", kind),
        Fact("Fees", f"{_pounds(fees(neighbour))} a year"),
        Fact("Teaches up to", "no limit" if limit is None else str(limit)),
    ]
    if kind == "University":
        found.append(Fact("Degrees", ", ".join(degrees(neighbour)) or "none yet"))
    return found


# -- the form --


def fields(_saga: Saga, neighbour: Neighbour | None) -> list[DialogField]:
    """What New University and Edit add to the common fields."""
    d = neighbour.details if neighbour is not None else {}
    return [
        DialogField(
            "school",
            "School",
            "select",
            d.get("school", "University"),
            options=pairs(tuple(SCHOOLS)),
            required=True,
        ),
        DialogField(
            "fees",
            "Fees (pounds a year)",
            "optint",
            d.get("fees"),
            hint="Blank for its kind's: 4 at a university, 1 at a cathedral school.",
        ),
    ]


def problem(values: dict[str, Any]) -> str | None:
    if (values.get("fees") or 0) < 0:
        return "Fees can't be less than none."
    return None


# -- faculties --


def faculties_title(_saga: Saga, neighbour: Neighbour) -> str:
    return f"Faculties ({len(faculties(neighbour))})"


def faculties_grid(_saga: Saga, neighbour: Neighbour) -> Grid:
    rows = []
    for faculty in faculties(neighbour):
        taught = sum(
            1 for m in masters(neighbour) if m.get("faculty") == faculty["faculty"]
        )
        chairs = faculty.get("chairs")
        rows.append(
            [
                faculty["faculty"],
                faculty.get("rector", ""),
                "" if chairs is None else str(chairs),
                str(taught),
            ]
        )
    return Grid(
        ["Faculty", "Rector", "Chairs", "Masters listed"],
        rows,
        list(range(len(rows))),
        "No faculties recorded: a university has Arts and at least one of "
        "Medicine, Law and Theology.",
        caps=[10, 22, 6, 0],
    )


def faculty_fields(
    _saga: Saga, _neighbour: Neighbour, faculty: dict[str, Any] | None
) -> list[DialogField]:
    f = faculty or {}
    return [
        DialogField(
            "faculty",
            "Faculty",
            "select",
            f.get("faculty", "Arts"),
            options=pairs(FACULTIES),
            required=True,
        ),
        DialogField("rector", "Rector", "text", f.get("rector", "")),
        DialogField(
            "chairs",
            "Endowed chairs",
            "optint",
            f.get("chairs"),
            hint="Six to twelve; half as many masters again visit.",
        ),
    ]


def _chairs_problem(values: dict[str, Any]) -> str | None:
    if (values.get("chairs") or 0) < 0:
        return "Chairs can't be fewer than none."
    return None


def faculty_ops(saga: Saga, neighbour: Neighbour) -> SectionOps:
    return list_ops(
        saga,
        neighbour,
        "faculties",
        "Faculty",
        faculty_fields,
        lambda f: f"the Faculty of {f['faculty']}",
        validate=_chairs_problem,
    )


# -- masters --


def _master_name(saga: Saga, master: dict[str, Any]) -> str:
    character = saga.character(master.get("who"))
    return character.name if character is not None else master.get("name", "")


def masters_title(_saga: Saga, neighbour: Neighbour) -> str:
    return f"Masters ({len(masters(neighbour))})"


def masters_grid(saga: Saga, neighbour: Neighbour) -> Grid:
    """Each master, his licence and faculty, and the Good Academic
    Reputation his licence starts."""
    rows = [
        [
            _master_name(saga, m),
            m.get("licence", ""),
            m.get("faculty", ""),
            str(LICENCES.get(m.get("licence", ""), 0)),
        ]
        for m in masters(neighbour)
    ]
    return Grid(
        ["Master", "Licence", "Faculty", "Academic Reputation"],
        rows,
        list(range(len(rows))),
        "No masters recorded.",
        caps=[22, 24, 10, 0],
    )


def master_fields(
    saga: Saga, _neighbour: Neighbour, master: dict[str, Any] | None
) -> list[DialogField]:
    m = master or {}
    return [
        DialogField(
            "name",
            "Name",
            "text",
            m.get("name", ""),
            placeholder="e.g. Master Gerard",
            hint="Or choose a character below.",
        ),
        DialogField(
            "who",
            "Character",
            "select",
            m.get("who"),
            options=[(escape(c.name), c.id) for c in saga.characters],
            allow_blank=True,
            placeholder="(none)",
        ),
        DialogField(
            "licence",
            "Licence",
            "select",
            m.get("licence", "Magister in Artibus"),
            options=[(f"{k} (Reputation {r})", k) for k, r in LICENCES.items()],
            required=True,
        ),
        DialogField(
            "faculty",
            "Faculty",
            "select",
            m.get("faculty", "Arts"),
            options=pairs(FACULTIES),
            required=True,
        ),
    ]


def _master_problem(values: dict[str, Any]) -> str | None:
    if not (values.get("name") or "").strip() and not values.get("who"):
        return "Name the master, or choose a character."
    return None


def master_ops(saga: Saga, neighbour: Neighbour) -> SectionOps:
    return list_ops(
        saga,
        neighbour,
        "masters",
        "Master",
        master_fields,
        lambda m: _master_name(saga, m),
        validate=_master_problem,
    )


TAB = KindTab(
    "Studium",
    "tab-nb-studium",
    (
        KindList(FACULTIES_SECTION, faculties_title, faculties_grid, faculty_ops),
        KindList(MASTERS_SECTION, masters_title, masters_grid, master_ops),
    ),
)

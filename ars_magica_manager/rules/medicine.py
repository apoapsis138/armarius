"""A physician's regimen (Art & Academe, Chapter Three: Medicine,
Prevention of Disease): a diet and a regime of exercise and bloodletting
that, once the patient has lived under it for a year, raises their Living
Conditions Modifier for Aging rolls:

    +1  for up to Medicine x 5 clients   (Medicine 1 at least)
    +2  for up to Medicine clients       (Medicine 4)
    +3  for a single client              (Medicine 7)

Each physician keeps a single regimen, and it needs regular bloodletting
by a chirurgeon with Chirurgy 3 (the physician may be his own). Eucrasia,
the balance it keeps, is lost by a month away, a neglected diet or
exercise, broken sleep, a disease, a day under a Corpus spell or a
Wizard's Twilight, and takes another year to win back.
"""

from __future__ import annotations

from ..models import Character, Saga
from .lab import ability_score

SOURCE = "Art & Academe, Chapter Three: Medicine, Prevention of Disease, p. 59"

#: Each regimen's bonus: (the Medicine it needs, its clients as a
#: multiple of Medicine, or 0 for a single client).
REGIMENS: dict[int, tuple[int, int]] = {1: (1, 5), 2: (4, 1), 3: (7, 0)}
CHIRURGY_NEEDED = 3
#: Years under the regimen before it helps.
YEARS_TO_TAKE = 1


def medicine(physician: Character) -> int:
    return sum(ability_score(physician, "Medicine"))


def regimen_level(medicine_score: int, wanted: int) -> int:
    """The best regimen up to `wanted` a physician of `medicine_score` can
    keep (0: none)."""
    return max(
        [
            0,
            *(
                bonus
                for bonus, (need, _) in REGIMENS.items()
                if bonus <= wanted and need <= medicine_score
            ),
        ]
    )


def client_limit(medicine_score: int, level: int) -> int:
    """How many clients a physician keeps on a regimen of this level."""
    _, per = REGIMENS[level]
    return per * medicine_score if per else 1


def clients(saga: Saga, physician: Character) -> list[Character]:
    """The physician's clients, in the saga's order."""
    return [
        c
        for c in saga.characters
        if c.aging.regimen and c.aging.regimen_by == physician.id
    ]


def chirurgeon(saga: Saga, physician: Character) -> Character | None:
    """A chirurgeon with Chirurgy 3 the physician can call on: himself, or
    someone at his covenant (anyone in the saga when he has none)."""
    for c in [physician, *saga.characters]:
        same = physician.covenant_id is None or c.covenant_id == physician.covenant_id
        if same and sum(ability_score(c, "Chirurgy")) >= CHIRURGY_NEEDED:
            return c
    return None


def regimen_problems(saga: Saga, character: Character) -> list[str]:
    """Why a regimen gives nothing although the physician's Medicine keeps
    it: he keeps a single regimen (its level is his first client's), only
    as many clients as its level allows (the first in the saga), and
    needs a chirurgeon with Chirurgy 3."""
    physician = saga.character(character.aging.regimen_by)
    if physician is None or not character.aging.regimen:
        return []
    found = []
    mine = clients(saga, physician)
    level = character.aging.regimen
    if mine and mine[0].aging.regimen != level:
        found.append(
            f"{physician.name} keeps a single regimen, +{mine[0].aging.regimen} "
            f"(for {mine[0].name})"
        )
    else:
        limit = client_limit(medicine(physician), level)
        same = [c for c in mine if c.aging.regimen == level]
        if character in same and same.index(character) >= limit:
            found.append(f"a +{level} regimen keeps only {limit} client(s)")
    if chirurgeon(saga, physician) is None:
        found.append(f"no chirurgeon with Chirurgy {CHIRURGY_NEEDED} to bleed them")
    return found


def regimen_bonus(saga: Saga, character: Character) -> int:
    """The regimen's bonus to Living Conditions this year: nothing until
    the patient has lived under it a year, no more than the physician's
    Medicine keeps, and nothing while a rule above stops it."""
    aging = character.aging
    physician = saga.character(aging.regimen_by)
    since = aging.regimen_since
    if physician is None or since is None or saga.current_year - since < YEARS_TO_TAKE:
        return 0
    if regimen_problems(saga, character):
        return 0
    return regimen_level(medicine(physician), aging.regimen)


def regimen_text(saga: Saga, character: Character) -> str:
    """The aging section's line on the regimen ("" for none)."""
    aging = character.aging
    physician = saga.character(aging.regimen_by)
    wanted, since, year = aging.regimen, aging.regimen_since, saga.current_year
    if not wanted:
        return ""
    if physician is None:
        return "Regimen: its physician is gone; it gives nothing."
    can = regimen_level(medicine(physician), wanted)
    line = f"Regimen by {physician.name}: +{wanted} to Living Conditions for aging"
    if can < wanted:
        need = REGIMENS[wanted][0]
        line += (
            f"; Medicine {medicine(physician)} keeps "
            + (f"+{can} at most" if can else "none")
            + f" (+{wanted} needs {need})"
        )
    stopped = regimen_problems(saga, character)
    if stopped:
        return line + "; it gives nothing: " + "; ".join(stopped) + " (A&A p. 59)."
    if since is None:
        return line + "; type the year it began."
    if year - since < YEARS_TO_TAKE:
        return line + f", from {since + YEARS_TO_TAKE}"
    return line

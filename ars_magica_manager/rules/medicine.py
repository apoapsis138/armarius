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

from ..models import Character
from .lab import ability_score

SOURCE = (
    "Art & Academe, Chapter Three: Medicine, Prevention of Disease "
    "(https://www.redcap.org/page/Art_%26_Academe)"
)

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


def regimen_bonus(
    physician: Character | None, wanted: int, since: int | None, year: int
) -> int:
    """The regimen's bonus to Living Conditions in `year`: nothing until
    the patient has lived under it a year, and no more than the
    physician's Medicine keeps."""
    if physician is None or since is None or year - since < YEARS_TO_TAKE:
        return 0
    return regimen_level(medicine(physician), wanted)


def regimen_text(
    physician: Character | None, wanted: int, since: int | None, year: int
) -> str:
    """The aging section's line on the regimen ("" for none)."""
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
    if since is None:
        return line + "; type the year it began."
    if year - since < YEARS_TO_TAKE:
        return line + f", from {since + YEARS_TO_TAKE}"
    return line

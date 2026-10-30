"""The supplement each More action comes from, so an action is offered only
while its book is in play.

An action listed here needs one of its books among the saga's books in
play (`sourcebooks.saga_books`); one not listed is the Definitive
Edition's, or spans books in a way its own rule decides (the faith actions,
which the Religion chapter offers by religion, and a tradition's casting,
which Traditions Offered decides). `actions.available` asks this before the
action's own rule, so a rule never has to remember its book.

The book for each action is the one its rules module cites."""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import sourcebooks

if TYPE_CHECKING:
    from .models import Saga

#: Action -> the books that bring it (any one in play is enough).
ACTION_BOOKS: dict[str, tuple[str, ...]] = {
    # Art & Academe: disputation, ligatures, the apothecary, careers.
    "disputatio": ("A&A",),
    "make_ligature": ("A&A",),
    "apothecary_store": ("A&A",),
    "artist_career": ("A&A",),
    "scholar_career": ("A&A",),
    # Lords of Men: the tournament (pp. 64-69).
    "tourney_season": ("LoM",),
    "melee_event": ("LoM",),
    # City & Guild: Labor Points and selling goods.
    "labor_story": ("C&G",),
    "invest_labor": ("C&G",),
    "sell_goods": ("C&G",),
    # The Sundered Eagle: the Theban Tribunal's Byzantine customs.
    "theban_letter": ("TSE",),
    "invoke_oath": ("TSE",),
    "make_greek_fire": ("TSE",),
    "paint_icon": ("TSE",),
    "venerate_icon": ("TSE",),
    "mothers_curse": ("TSE",),
    # Realms of Power: The Infernal: sin, tarnish and the Goetic Arts.
    "indulge_sin": ("RoP:I",),
    "infernal_influence": ("RoP:I",),
    "ars_goetia": ("RoP:I",),
    # Apprentices: an apprentice's magic and the Gauntlet.
    "turbulence": ("App",),
    "gauntlet": ("App",),
    "lose_the_gift": ("App",),
    "learn_cantation": ("App",),
    # Realms of Power: Faerie: dealing with faeries.
    "ars_fabulosa": ("RoP:F",),
    "faerie_bargain": ("RoP:F",),
    "faerie_offer": ("RoP:F",),
    # Houses of Hermes: Societates: the lacuna, and House Tytalus's covers.
    "cast_in_lacuna": ("HoH:S",),
    "disguise_roll": ("HoH:S",),
    # The Church: the pilgrim's road.
    "pilgrimage": ("TC",),
    # Realms of Power: The Divine: baraka, the Hajj, holy influence.
    "invoke_baraka": ("RoP:D",),
    "hajj": ("RoP:D",),
    "holy_influence": ("RoP:D",),
    # The Mysteries, Revised Edition.
    "spirits_and_names": ("TMRE",),
    "dream_working": ("TMRE",),
    "hermetic_sacrifice": ("TMRE",),
    "tmre_divination": ("TMRE",),
    "tmre_astrology": ("TMRE",),
    "philosophic_alchemy": ("TMRE",),
    "great_elixir": ("TMRE",),
    "experiment_script": ("TMRE",),
    # House Acclaim: Bonisagus in True Lineages, Flambeau in Societates.
    "house_acclaim": ("HoH:TL", "HoH:S"),
    # Hermetic Projects: a Wizard's War tunnel.
    "open_tunnel": ("HP",),
    # Grogs: rewards, punishments and pensions for the covenfolk.
    "discipline_grog": ("Grogs",),
    "grog_pension": ("Grogs",),
}


#: The character page's other placed actions, each checked and found to be
#: the Definitive Edition's (or decided by its own rule), so a new action
#: placed on the character page must join one list or the other.
NO_BOOK: frozenset[str] = frozenset(
    {
        # The Definitive Edition.
        "create_familiar",
        "lab_text_access",
        "take_harm",
        "recovery_roll",
        "end_session",
        "reputation_roll",
        "plan_copying",
        "clear_copying",
        "command_beast",
        "craft_by_magic",
        "place_aging_points",
        "resolve_twilight",
        "whereabouts",
        "guest_stay",
        "trait_roll",
        "share_spell",
        "boost_spell",
        "give_silver",
        "certamen_duel",
        # Hubris is the Definitive Edition's Flaw (p. 242); Mystery Cults'
        # table of what raises it is used when that book is in play.
        "verditius_hubris",
        "change_virtues_flaws",
        # Grogs' story experience, on the Definitive Edition's (p. 376).
        "grog_story_xp",
        # Traditions and their casting: Traditions Offered decides by book.
        "edit_traditions",
        "hedge_cast",
        # The faith actions: the Religion chapter offers each by religion
        # from The Church or Realms of Power: The Divine (rules.faiths).
        "invoke_saint",
        "threaten_saint",
        "patron_saint",
        "devotion_points",
        "act_of_piety",
        "mystic_path",
        "spiritual_path",
        "monistic_revelation",
        "gods_aid",
        "font_of_knowledge",
        "commanding_aura",
    }
)


def book_allows(action: str, saga: Saga | None) -> bool:
    """Whether `action`'s book is in play in `saga` (always, for an action
    with no book of its own)."""
    books = ACTION_BOOKS.get(action)
    if books is None:
        return True
    in_play = sourcebooks.saga_books(saga)
    return any(sourcebooks.in_play(book, in_play) for book in books)

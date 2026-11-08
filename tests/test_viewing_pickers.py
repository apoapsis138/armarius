"""A player's pickers don't name what the players don't know of: the
options a form lists (owners, holders, covenants, spouses, rivals, kinds of
neighbour...) leave out a hidden character, covenant or neighbour, and the
storyguide's list is the whole saga. One table walks the builders."""

import pytest

from ars_magica_manager import (
    books,
    disputations,
    guest_stays,
    marriages,
    neighbour_filter,
    viewing,
)
from ars_magica_manager.form_spec import covenant_options
from ars_magica_manager.forms import certamen_duel, polemic
from ars_magica_manager.forms import device as device_forms
from ars_magica_manager.models import (
    Character,
    Covenant,
    EnchantedDevice,
    Neighbour,
    Player,
    Saga,
)

HIDDEN_PERSON = "Hidden Hanno"
HIDDEN_COVENANT = "Hidden Hold"
HIDDEN_LORD = "Hidden Lord"


def _saga() -> Saga:
    """A troupe (one played covenant and magus) and three records the
    players don't know of: a person, a covenant and a lord."""
    played = Covenant(id="home", saga_id="s", name="Home", played=True)
    hidden_covenant = Covenant(
        id="hold", saga_id="s", name=HIDDEN_COVENANT, played=False, known=False
    )
    magus = Character(id="m1", name="Leandro", type="magus", covenant_id="home")
    magus.background.player = "Alex"
    rival = Character(id="m2", name="Rival", type="magus", covenant_id="home")
    rival.background.player = "Bea"
    hidden_person = Character(
        id="hanno", name=HIDDEN_PERSON, type="magus", covenant_id="hold", known=False
    )
    lord = Neighbour(id="lord", name=HIDDEN_LORD, kind="lord", known=False)
    return Saga(
        id="s",
        name="S",
        covenants=[played, hidden_covenant],
        characters=[magus, rival, hidden_person],
        neighbours=[lord],
    )


def _names(options) -> str:
    return " | ".join(str(label) for label, *_ in options)


def _all_names(records) -> str:
    return " | ".join(r.name for r in records)


#: (label, builder(saga) -> text of everything it lists, hidden name it must
#: leave out for a player)
BUILDERS = {
    "covenant options": (lambda s: _names(covenant_options(s)), HIDDEN_COVENANT),
    "book owners": (lambda s: _names(books.owner_options(s)), HIDDEN_PERSON),
    "book owners (covenants)": (
        lambda s: _names(books.owner_options(s)),
        HIDDEN_COVENANT,
    ),
    "device holders": (lambda s: _names(device_forms.holder_options(s)), HIDDEN_PERSON),
    "device holders (covenants)": (
        lambda s: _names(device_forms.holder_options(s)),
        HIDDEN_COVENANT,
    ),
    "disputation opponents": (
        lambda s: " | ".join(
            str(o)
            for f in disputations.fields(s, s.characters[0])
            for o in getattr(f, "options", None) or []
        ),
        HIDDEN_PERSON,
    ),
    "spouses": (lambda s: _names(marriages._spouse_options(s)), HIDDEN_PERSON),
    "spouses (lords)": (lambda s: _names(marriages._spouse_options(s)), HIDDEN_LORD),
    "houses": (lambda s: _names(marriages._house_options(s)), HIDDEN_LORD),
    "certamen rivals": (
        lambda s: _all_names(certamen_duel._rivals(s, s.characters[0])),
        HIDDEN_PERSON,
    ),
    "guest hosts": (
        lambda s: _all_names(guest_stays.hosts(s, s.characters[0])),
        HIDDEN_COVENANT,
    ),
    "polemic authors": (lambda s: _names(polemic._magi_options(s)), HIDDEN_PERSON),
    "neighbour kinds": (
        lambda s: " | ".join(k.key for k in neighbour_filter.kinds(s)),
        "lord",
    ),
}


@pytest.mark.parametrize("name", list(BUILDERS))
def test_the_storyguide_lists_everything_and_a_player_what_they_know(name):
    build, hidden = BUILDERS[name]
    saga = _saga()
    # The troupe's lord is a known one, so the "lord" kind is only hidden
    # while no known neighbour of that kind exists.
    try:
        viewing.use(viewing.STORYGUIDE_VIEWER, saga)
        assert hidden in build(saga), "the storyguide sees it"
        player = Player(id="p1", name="Alex", role="player")
        viewing.use(viewing.viewer_for(player), saga)
        assert hidden not in build(saga), "a player must not"
    finally:
        viewing.use(viewing.STORYGUIDE_VIEWER, None)


def test_an_edit_form_keeps_the_value_it_already_holds():
    """A book owned by a record the players don't know of still shows its
    owner when a player opens it: the options keep the current value."""
    saga = _saga()
    player = Player(id="p1", name="Alex", role="player")
    try:
        viewing.use(viewing.viewer_for(player), saga)
        value = books.owner_value("covenant", "hold")
        options = books.owner_options(saga, keep=value)
        assert value in [v for _, v in options]
        device = EnchantedDevice(
            id="d", name="Ring", holder_kind="covenant", holder_id="hold"
        )
        fields = device_forms._device_holder_fields(saga, device, None)
        holder = next(f for f in fields if f.key == "holder")
        assert "covenant:hold" in [value for _, value in holder.options or []]
        others = device_forms.holder_options(saga)
        assert "covenant:hold" not in [value for _, value in others]
    finally:
        viewing.use(viewing.STORYGUIDE_VIEWER, None)

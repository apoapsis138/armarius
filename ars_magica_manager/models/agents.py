"""An agent: someone a character controls through a personal bond (Lords
of Men pp. 22-25). The rules are rules.agents'."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .common import known_fields
from .traits import new_instance_id


@dataclass
class Agent:
    """A potential or recruited agent of the character who keeps him."""

    name: str
    #: The agent's social standing (rules.agents.STATUS_RESISTANCE's keys).
    status: str = "free"
    #: The flaws and resources that make him harder to win
    #: (rules.agents.MODIFIERS' keys), counted once each.
    modifiers: list[str] = field(default_factory=list)
    #: What draws him to the principal, as a Personality Trait ("Loves
    #: wife"), and its strength; a new agent's is 0.
    bond_trait: str = ""
    bond: int = 0
    #: Agency experience counted toward the Bond's next level.
    bond_xp: int = 0
    #: Whether he has been impressed (the Presence + Leadership roll); only
    #: then can Agency experience wear his resistance down.
    impressed: bool = False
    #: What is left of his resistance; 0 once he is an agent. None until
    #: worked out from the Agent Recruitment Table.
    resistance: int | None = None
    #: What the principal gains through him: Abilities, wealth, men.
    resources: str = ""
    #: Held only by coercion: he hates the principal (Difficult Underlings
    #: for him, and a Story Flaw of his own).
    coerced: bool = False
    #: The neighbour record he is, if any.
    neighbour_id: str | None = None
    notes: str = ""
    id: str = field(default_factory=new_instance_id)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Agent:
        d = dict(data)
        d["modifiers"] = [str(m) for m in d.get("modifiers") or []]
        for key in ("bond", "bond_xp"):
            value = d.get(key, 0)
            if not isinstance(value, int):
                raise ValueError(f"Agent {d.get('name')!r}: {key} must be a number.")
        return cls(**known_fields(cls, d))

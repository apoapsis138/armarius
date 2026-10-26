"""Seasonal activities from the supplements, planned on the character
sheet: the names the rest of the app imports from here. The activities
themselves are registered by each book's module of rules/season_work."""

from __future__ import annotations

from .season_work import ACTIVITIES, BY_KEY
from .season_work.academe import ACADEME
from .season_work.base import SimpleActivity
from .season_work.church import CHURCH
from .season_work.city_guild import CITY_GUILD
from .season_work.covenants import COVENANTS
from .season_work.definitive import DE_TAMING, SOURCE
from .season_work.initiation import DE_INITIATION, MYSTERIES
from .season_work.lords import LORDS
from .season_work.societates import SOCIETATES

__all__ = [
    "ACADEME",
    "ACTIVITIES",
    "BY_KEY",
    "CHURCH",
    "CITY_GUILD",
    "COVENANTS",
    "DE_INITIATION",
    "DE_TAMING",
    "LORDS",
    "MYSTERIES",
    "SOCIETATES",
    "SOURCE",
    "SimpleActivity",
]

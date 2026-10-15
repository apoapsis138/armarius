"""The Laboratory and its features."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from ..arts import ARTS, TECHNIQUES
from .common import known_fields
from .traits import VirtueFlawInstance, new_instance_id


@dataclass
class LabCharacteristics:
    """The 8 Laboratory Characteristics' manual (base) component only.

    Each Characteristic's effective total is manual + virtue_sum +
    flaw_sum (see laboratories.lab_characteristic_total) -- virtue_sum and
    flaw_sum are derived from the lab's attached Virtues/Flaws, never stored
    here.
    """

    size: int = 0
    refinement: int = 0
    general_quality: int = 0
    upkeep: int = 0
    safety: int = 0
    warping: int = 0
    health: int = 0
    aesthetics: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LabCharacteristics:
        return cls(**known_fields(cls, data))


@dataclass
class NamedDescription:
    """A name + a free-text description -- shared shape for a Laboratory's
    Rooms and its Inventory "items that influence the lab"."""

    name: str
    description: str = ""


@dataclass
class ArcaneConnection:
    """An Arcane Connection kept in a laboratory: what it
    connects to, and whether it has been fixed (made permanent by a season
    of lab work and a pawn of Vim) or lasts only a while."""

    id: str
    #: Whom or what it connects to ("a lock of Banna's hair").
    to: str
    fixed: bool = False
    #: A temporary one: how long it lasts, as typed ("until Summer 1222").
    lasts: str = ""
    #: Where it came from.
    source: str = ""
    description: str = ""
    #: When it was fixed, if the app fixed it.
    fixed_year: int | None = None
    fixed_season: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ArcaneConnection:
        return cls(**known_fields(cls, data))


#: What a laboratory Diary entry can record, for its Activity Type: the lab
#: activities of reference/lab-sheet-design-doc.md, then the rest of a
#: season's lab work, and Other. A Diary entry's `activity` is one of these
#: or "" (not set -- every entry written before Activity Type existed).
LAB_ACTIVITIES: tuple[str, ...] = (
    "Invent Spell",
    "Learn Spell from Teacher",
    "Extract Vis",
    "Fix Arcane Connection",
    "Open Item for Enchantment",
    "Instill Effect (Invested Device)",
    "Lesser Enchantment",
    "Charged Item",
    "Longevity Ritual",
    "Bind Familiar",
    "Empower Familiar Bond",
    "Train Apprentice",
    "Translate Lab Text",
    "Arcane Experimentation",
    "Original Research",
    "Study",
    "Refine Laboratory",
    "Build/Modify Laboratory",
    "Other",
)


#: The 8 Activity Specializations a laboratory can have (ArM5 p.115 and
#: reference/laboratory-features-reference.md); with the 15 Arts they make
#: every Specialization.
LAB_ACTIVITY_SPECIALIZATIONS: tuple[str, ...] = (
    "Experimentation",
    "Familiar",
    "Items",
    "Longevity Rituals",
    "Spells",
    "Teaching",
    "Texts",
    "Vis Extraction",
)
LAB_SPECIALIZATIONS: tuple[str, ...] = (*LAB_ACTIVITY_SPECIALIZATIONS, *ARTS)


#: The lab Virtues a Feature is built on, and the points each gives it
#: (reference/laboratory-features-reference.md).
FEATURE_VIRTUE_POINTS: dict[str, int] = {
    "labvf_lesser_feature": 1,
    "labvf_greater_feature": 3,
}
#: The Focus Flaws, each with the Feature Virtue it goes with and the extra
#: points it gives that Feature.
FOCUS_FLAWS: dict[str, tuple[str, int]] = {
    "labvf_lesser_focus": ("labvf_lesser_feature", 2),
    "labvf_greater_focus": ("labvf_greater_feature", 4),
}


@dataclass
class LabFeatureDef:
    """A catalog Laboratory Feature (Altar, Cauldron...): what it is and the
    Specializations its points may go to. "Any Technique" in the source is
    stored as the five Techniques."""

    id: str
    name: str
    description: str
    specializations: tuple[str, ...]
    #: The book(s) it's from (sourcebooks); every entry so far is Covenants'.
    source: str = "Covenants"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LabFeatureDef:
        specializations: list[str] = []
        for name in data["specializations"]:
            specializations += TECHNIQUES if name == "Any Technique" else [name]
        unknown = set(specializations) - set(LAB_SPECIALIZATIONS)
        if unknown:
            raise ValueError(f"Unknown Specializations {unknown} for {data['id']!r}")
        return cls(
            data["id"],
            data["name"],
            data["description"],
            tuple(specializations),
            data.get("source", "Covenants"),
        )


@dataclass
class LabSpecialtyGrant:
    """Points a Feature (or its Focus) puts into one Specialization."""

    specialization: str
    points: int


@dataclass
class LabFeature:
    """A Feature installed in a laboratory, built on one of its Lesser or
    Greater Feature Virtues (`virtue_id`, a VirtueFlawInstance.id; None when
    it has none yet, e.g. converted from old notes). `feature_id` is the
    catalog Feature, None for a custom one; `name` is the user's own label
    ("Large Brass Cauldron"). `allocations` spend the Virtue's points; with
    `focus` (the lab's Focus Flaw is built around it) `focus_allocations`
    spend the Focus's."""

    id: str
    name: str
    feature_id: str | None = None
    virtue_id: str | None = None
    allocations: list[LabSpecialtyGrant] = field(default_factory=list)
    focus: bool = False
    focus_allocations: list[LabSpecialtyGrant] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LabFeature:
        d = dict(data)
        d["allocations"] = [
            LabSpecialtyGrant(**known_fields(LabSpecialtyGrant, g))
            for g in d.get("allocations", [])
        ]
        d["focus_allocations"] = [
            LabSpecialtyGrant(**known_fields(LabSpecialtyGrant, g))
            for g in d.get("focus_allocations", [])
        ]
        return cls(**known_fields(cls, d))


def _feature_from_old_text(
    text: str, feature_names: dict[str, str] | None = None, *, id: str = ""
) -> LabFeature:
    """An older save's free-text Feature as a LabFeature named with the text,
    of the catalog Feature named in it (by whole word, a plural too: "Big
    windows" is a Window), else custom. `feature_names` maps catalog names
    to ids (loaded from the catalog when not given)."""
    if feature_names is None:
        from ..catalog import load_lab_feature_catalog

        feature_names = {f.name: f.id for f in load_lab_feature_catalog()}
    feature_id = None
    for name in sorted(feature_names, key=len, reverse=True):
        if re.search(rf"\b{re.escape(name)}s?\b", text, re.IGNORECASE):
            feature_id = feature_names[name]
            break
    return LabFeature(id=id or new_instance_id(), name=text, feature_id=feature_id)


def link_unlinked_features(lab: Laboratory) -> None:
    """Give each Feature without a Virtue the first Lesser/Greater Feature
    Virtue no other Feature has (old notes carry no link)."""
    taken = {f.virtue_id for f in lab.features if f.virtue_id}
    free = [
        vf.id
        for vf in lab.virtues_flaws
        if vf.vf_id in FEATURE_VIRTUE_POINTS and vf.id not in taken
    ]
    for feature in lab.features:
        if feature.virtue_id is None and free:
            feature.virtue_id = free.pop(0)


@dataclass
class LabSpecialtyEntry:
    """Points in one Specialization from a source the app doesn't work out
    itself (a Virtue/Flaw such as Subterranean, a magical effect...), typed
    in by the user. `specialization` is one of LAB_SPECIALIZATIONS, or ""
    for old free text that named none (the text is kept in `source`)."""

    specialization: str
    points: int = 1
    source: str = ""


def _parse_old_specialty(text: str) -> LabSpecialtyEntry:
    """An older save's free-text Specialty ("Terram +1") as an entry: the
    Specialization it names, its number (1 when there isn't one), the source
    "(from old notes)". Text that names no Specialization becomes a 0-point
    entry keeping the text, for the user to fix."""
    words = text.split()
    points = 1
    if words and re.fullmatch(r"[+-]?\d+", words[-1]):
        points = int(words.pop())
    name = " ".join(words).casefold()
    for specialization in LAB_SPECIALIZATIONS:
        if specialization.casefold() == name:
            return LabSpecialtyEntry(specialization, points, "(from old notes)")
    return LabSpecialtyEntry("", 0, text)


@dataclass
class DiaryEntry:
    """One entry of a laboratory's or a character's Diary."""

    year: int
    season: str = "Spring"  # one of SEASONS
    name: str = ""
    details: str = ""
    #: A lab Diary: one of LAB_ACTIVITIES. A character's Diary: the season
    #: activity's label (rules.activities.ACTIVITIES). "" when not set.
    activity: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DiaryEntry:
        return cls(**known_fields(cls, data))


@dataclass
class Laboratory:
    id: str
    #: None while the lab isn't assigned to a covenant (a legal state).
    covenant_id: str | None
    name: str
    owner_id: str | None = None
    location: str = ""
    #: Manual adjustment on top of the covenant's aura this lab inherits
    #: (e.g. from Virtues) -- see laboratories.lab_aura_total().
    aura_modifier: int = 0
    #: The place it is in and which level, when not its covenant's (a lab
    #: built in a regio; places.py).
    place_id: str | None = None
    place_level: int = 0
    characteristics: LabCharacteristics = field(default_factory=LabCharacteristics)
    features: list[LabFeature] = field(default_factory=list)
    #: Specialization points from sources entered by hand (see
    #: laboratories.lab_specializations for the totals).
    specialties: list[LabSpecialtyEntry] = field(default_factory=list)
    #: Specializations the user turned off (or that arrived over a cap);
    #: they keep their points but don't count.
    dropped_specializations: list[str] = field(default_factory=list)
    #: Whether the sanctum's boundary is marked (Code of Hermes).
    sanctum_marked: bool = False
    rooms: list[NamedDescription] = field(default_factory=list)
    inventory_items: list[NamedDescription] = field(default_factory=list)
    raw_vis: dict[str, int] = field(default_factory=dict)  # Art -> pawns
    diary: list[DiaryEntry] = field(default_factory=list)
    virtues_flaws: list[VirtueFlawInstance] = field(default_factory=list)
    arcane_connections: list[ArcaneConnection] = field(default_factory=list)
    #: Moving it by mundane means: the seasons done so far (0: not
    #: moving; pack, then two reassembling).
    move_seasons: int = 0
    #: One of its covenant's starting laboratories: its Build
    #: Points count against the covenant's at creation.
    starting: bool = False
    #: Being created by the book: the creation checks run and
    #: the Creation Worksheet is offered. New records start In Creation;
    #: older saves load In Play (False).
    in_creation: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Laboratory:
        d = dict(data)
        d.pop("aura", None)  # moved to Covenant.aura -- discard the old per-lab value
        legacy_size = d.pop("size", None)
        if "characteristics" not in d:
            d["characteristics"] = LabCharacteristics(size=legacy_size or 0)
        else:
            d["characteristics"] = LabCharacteristics.from_dict(d["characteristics"])
        d["rooms"] = [
            NamedDescription(**known_fields(NamedDescription, r))
            for r in d.get("rooms", [])
        ]
        d["inventory_items"] = [
            NamedDescription(**known_fields(NamedDescription, i))
            for i in d.get("inventory_items", [])
        ]
        d["arcane_connections"] = [
            ArcaneConnection.from_dict(c) for c in d.get("arcane_connections", [])
        ]
        d["diary"] = [DiaryEntry.from_dict(entry) for entry in d.get("diary", [])]
        d["virtues_flaws"] = [
            VirtueFlawInstance(**known_fields(VirtueFlawInstance, vf))
            for vf in d.get("virtues_flaws", [])
        ]
        # Ids given at load are the same every time (not new_instance_id):
        # a hosted saga's saves compare the file as loaded.
        for i, vf in enumerate(d["virtues_flaws"]):
            vf.id = vf.id or f"{d.get('id', '')}-vf{i}"
        old_features = [f for f in d.get("features", []) if isinstance(f, str)]
        d["features"] = [
            _feature_from_old_text(f, id=f"{d.get('id', '')}-feature{i}")
            if isinstance(f, str)  # older saves' free text
            else LabFeature.from_dict(f)
            for i, f in enumerate(d.get("features", []))
        ]
        d["specialties"] = [
            _parse_old_specialty(s)
            if isinstance(s, str)  # older saves' free text
            else LabSpecialtyEntry(**known_fields(LabSpecialtyEntry, s))
            for s in d.get("specialties", [])
        ]
        lab = cls(**known_fields(cls, d))
        if old_features:
            link_unlinked_features(lab)
        return lab

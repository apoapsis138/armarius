"""What a season is for: the groups the activity pickers list and filter
seasonal activities by (rules.activities.Activity.group), each activity
carrying its own. Lab work has groups of its own, as the laboratory's
Planning tab plans it apart from the character sheet."""

from __future__ import annotations

STUDY = "Study"
WRITING = "Writing & books"
WORK = "Work & trade"
TEACHING = "Teaching & apprentices"
FAITH = "Faith"
ORDER = "Order & covenant"
MYSTERIES = "Mysteries"
ADVENTURE = "Adventure & travel"
REST = "Rest & other"
TRADITION = "Tradition"

INVENTING = "Inventing"
ENCHANTING = "Enchanting"
FAMILIAR = "Familiar"
TEXTS_AND_VIS = "Texts and vis"
LABORATORY = "The laboratory"

#: The character sheet's groups, in the order the picker lists them.
GROUPS: tuple[str, ...] = (
    STUDY,
    WRITING,
    WORK,
    TEACHING,
    FAITH,
    ORDER,
    MYSTERIES,
    ADVENTURE,
    REST,
    TRADITION,
)

#: Lab work's groups, in the order the picker lists them.
LAB_GROUPS: tuple[str, ...] = (
    INVENTING,
    ENCHANTING,
    FAMILIAR,
    TEXTS_AND_VIS,
    LABORATORY,
)

"""Form builders for the records (DialogField lists for FieldsDialog) and the
bespoke forms that aren't FieldsDialogs, one module per area. Everything
other code uses is re-exported here, so it imports from `screens.forms`."""

from .character import EditArtsScreen as EditArtsScreen
from .character import _aging_fields as _aging_fields
from .character import _biographical_fields as _biographical_fields
from .character import _bond_power_fields as _bond_power_fields
from .character import _character_info_dialog as _character_info_dialog
from .character import _characteristics_dialog as _characteristics_dialog
from .character import _characteristics_from as _characteristics_from
from .character import _familiar_binding_dialog as _familiar_binding_dialog
from .character import (
    _familiar_characteristics_fields as _familiar_characteristics_fields,
)
from .character import _familiar_info_fields as _familiar_info_fields
from .character import _fatigue_fields as _fatigue_fields
from .character import _hermetic_fields as _hermetic_fields
from .character import _wounds_fields as _wounds_fields
from .covenant import _buy_specialist_dialog as _buy_specialist_dialog
from .covenant import _contested_fields as _contested_fields
from .covenant import _covenant_fields as _covenant_fields
from .covenant import _improve_income_dialog as _improve_income_dialog
from .covenant import _inhabitant_fields as _inhabitant_fields
from .covenant import _possession_dialog as _possession_dialog
from .covenant import _possession_fields as _possession_fields
from .creation import RULE_OPTION_PREFIX as RULE_OPTION_PREFIX
from .creation import _character_create_dialog as _character_create_dialog
from .creation import _covenant_create_fields as _covenant_create_fields
from .creation import _familiar_create_fields as _familiar_create_fields
from .creation import _laboratory_create_fields as _laboratory_create_fields
from .creation import _saga_fields as _saga_fields
from .creation import saga_rule_options as saga_rule_options
from .creation import template_key as template_key
from .enchantment import _enchanted_device_dialog as _enchanted_device_dialog
from .enchantment import _instilled_effect_dialog as _instilled_effect_dialog
from .importing import DuplicateBookScreen as DuplicateBookScreen
from .importing import ImportScreen as ImportScreen
from .importing import SpellImportHelperScreen as SpellImportHelperScreen
from .laboratory import NEW_FEATURE_VIRTUE as NEW_FEATURE_VIRTUE
from .laboratory import _lab_characteristics_fields as _lab_characteristics_fields
from .laboratory import _lab_feature_dialog as _lab_feature_dialog
from .laboratory import _lab_feature_type_dialog as _lab_feature_type_dialog
from .laboratory import _lab_identity_fields as _lab_identity_fields
from .library import _book_fields as _book_fields
from .library import _book_from_values as _book_from_values
from .library import _book_live as _book_live
from .library import _research_fields as _research_fields
from .library import _research_from_values as _research_from_values
from .saga import _save_folder_dialog as _save_folder_dialog
from .season_plans import _breakthrough_dialog as _breakthrough_dialog
from .season_plans import _grog_year_dialog as _grog_year_dialog
from .season_plans import _season_plan_dialog as _season_plan_dialog
from .spells import _level_fill as _level_fill
from .spells import _mastery_dialog as _mastery_dialog
from .spells import _spell_fields as _spell_fields
from .spells import _spell_from_values as _spell_from_values
from .spells import _spell_live as _spell_live
from .spells import _spell_problem as _spell_problem

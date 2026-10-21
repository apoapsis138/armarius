"""Season plans and advancing the season: keeping each
character's plan, the text the sheets show for it, and applying a season.

Advancing works out every plan's outcome first (rules.activities.outcomes), from
the saga as it stood before the season, and only then applies them, so one
character's results can't change another's (or their own) that same season:
raising Magic Theory by Exposure doesn't raise this season's Lab Total. Each
applied outcome adds experience and writes a Diary entry on the character;
the applied plans are then removed. Like the other domain modules it returns
markup text, never widgets.

One module per part; everything other code uses is re-exported here.
"""

from .advance import advance_summary as advance_summary
from .advance import apply as apply
from .advance import finish_season as finish_season
from .advance import make_record as make_record
from .advance import record_label as record_label
from .advance import record_table as record_table
from .advance import record_text as record_text
from .advance import resolve as resolve
from .advance import year_end_aging as year_end_aging
from .advance import year_end_grogs as year_end_grogs
from .character_effects import age_character as age_character
from .character_effects import gain_warping as gain_warping
from .character_effects import living_conditions as living_conditions
from .covenant import SEASON_KINDS as SEASON_KINDS
from .covenant import covenant_people as covenant_people
from .covenant import covenant_season as covenant_season
from .covenant import lapsed_resources as lapsed_resources
from .covenant import season_info_text as season_info_text
from .covenant import season_rows as season_rows
from .covenant import season_table as season_table
from .covenant import season_title as season_title
from .lab_apply import discovery_moves as discovery_moves
from .lab_apply import perform_ritual_again as perform_ritual_again
from .lab_apply import plan_lab_finish as plan_lab_finish
from .lab_apply import take_discovery_move as take_discovery_move
from .lab_apply import year_end_business as year_end_business
from .lab_queue import lab_queue as lab_queue
from .lab_queue import lab_queue_info as lab_queue_info
from .lab_queue import lab_queue_rows as lab_queue_rows
from .lab_queue import lab_queue_table as lab_queue_table
from .lab_queue import plan_lab_work as plan_lab_work
from .lab_queue import scheduled_with as scheduled_with
from .plans import AHEAD as AHEAD
from .plans import ahead_info as ahead_info
from .plans import ahead_rows as ahead_rows
from .plans import ahead_table as ahead_table
from .plans import ahead_title as ahead_title
from .plans import book_label as book_label
from .plans import clear_plan as clear_plan
from .plans import due_plans as due_plans
from .plans import live_text as live_text
from .plans import plan_for as plan_for
from .plans import plan_summary as plan_summary
from .plans import plan_text as plan_text
from .plans import planning_year as planning_year
from .plans import seasons_ahead as seasons_ahead
from .plans import set_plan as set_plan
from .plans import subject_options as subject_options
from .plans import unplanned as unplanned
from .plans import work_text as work_text
from .plans import working_seasons_note as working_seasons_note

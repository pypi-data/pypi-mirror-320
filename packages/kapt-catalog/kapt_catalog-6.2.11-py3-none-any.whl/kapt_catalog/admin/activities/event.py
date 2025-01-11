# Local application / specific library imports
from kapt_catalog.admin.activities.activity import ActivityChildAdmin
from kapt_catalog.models.activities.event import EventActivity


class EventActivityAdmin(ActivityChildAdmin):
    model = EventActivity

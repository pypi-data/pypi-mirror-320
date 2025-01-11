# Local application / specific library imports
from kapt_catalog.admin.activities.activity import ActivityChildAdmin
from kapt_catalog.models.activities.poi import PointOfInterestActivity


class PointOfInterestActivityAdmin(ActivityChildAdmin):
    model = PointOfInterestActivity

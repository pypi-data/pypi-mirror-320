# Third party
from kapt_catalog.models.activities import Labelling

# Local application / specific library imports
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.activities.common import (
    CommonActivityUpdater,
)


class BaseSpecificActivityUpdater:
    activity = None
    touristic_object = None
    common_updater = None

    def __init__(self, activity, touristic_object):
        self.activity = activity
        self.touristic_object = touristic_object
        self.common_updater = CommonActivityUpdater(touristic_object, activity)

    def fill_attributes(self):
        # First we remove all labelling before update...
        self.activity.main_labelling = None
        self.activity.default_labelling = None
        self.activity.prefectoral_labelling = None
        Labelling.objects.filter(activity=self.activity).delete()
        self.common_updater.name()

    def fill_relations(self):
        pass

    def update(self):
        self.fill_attributes()
        self.common_updater.save_activity()
        self.fill_relations()
        self.common_updater.update()
        self.common_updater.reference_profile()
        return self.activity


class BaseAccommodationActivityUpdater(BaseSpecificActivityUpdater):
    pass

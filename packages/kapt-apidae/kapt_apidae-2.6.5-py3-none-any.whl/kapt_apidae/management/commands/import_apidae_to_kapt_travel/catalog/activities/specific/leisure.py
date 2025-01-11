# Local application / specific library imports
from kapt_apidae.management import ScriptError
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.activities.specific import (
    BaseSpecificActivityUpdater,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.characteristics.generated_characteristics import (
    CULTURAL_ACTIVITY,
    EQUIPMENT_ACTIVITY,
    SPORT_ACTIVITY,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.utils import (
    get_characteristic,
)


class LeisureActivityUpdater(BaseSpecificActivityUpdater):
    def fill_attributes(self):
        super().fill_attributes()
        # Patch to convert old type to new characteristic format.
        # To delete when all the project will be updated
        # by FP
        try:
            self.activity.distance = self.touristic_object.distance
            self.activity.elevation = self.touristic_object.difference_in_level
            self.activity.daily_duration = self.touristic_object.daily_duration
            self.activity.roaming_duration = self.touristic_object.mobility_duration
        except AttributeError:
            # Not an equipment
            pass

    def fill_relations(self):
        self.activity.categories.clear()

        if self.activity.type.identifier == "sport-activity":
            for category in self.touristic_object.sport_activities.all():
                if category.active is True:
                    self.activity.categories.add(
                        get_characteristic(SPORT_ACTIVITY[category.id]["identifier"])
                    )

        elif self.activity.type.identifier == "cultural-activity":
            for category in self.touristic_object.cultural_activities.all():
                if category.active is True:
                    self.activity.categories.add(
                        get_characteristic(CULTURAL_ACTIVITY[category.id]["identifier"])
                    )

        elif self.activity.type.identifier == "equipment-activity":
            for category in self.touristic_object.equipment_activities.all():
                if category.active is True:
                    self.activity.categories.add(
                        get_characteristic(
                            EQUIPMENT_ACTIVITY[category.id]["identifier"]
                        )
                    )

        else:
            raise ScriptError("Leisure activity with unknown type", self.activity)

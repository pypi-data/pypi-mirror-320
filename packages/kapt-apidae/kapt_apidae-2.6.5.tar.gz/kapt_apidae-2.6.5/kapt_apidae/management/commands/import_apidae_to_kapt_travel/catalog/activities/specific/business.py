# Local application / specific library imports
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.activities.specific import (
    BaseSpecificActivityUpdater,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.characteristics.generated_characteristics import (
    BUSINESS_AND_SERVICE_ACTIVITY,
    COMMERCES_SERVICES_TYPES,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.utils import (
    get_characteristic,
)


class BusinessActivityUpdater(BaseSpecificActivityUpdater):
    def fill_attributes(self):
        super().fill_attributes()
        # Patch to convert old type to new characteristic format.
        # To delete when all the project will be updated
        # by FP
        if self.activity.type.identifier in [
            "business-activity",
            "service-activity",
            "associative-activity",
        ]:
            self.activity.type = get_characteristic(
                COMMERCES_SERVICES_TYPES[self.touristic_object.type_id]["identifier"]
            )

    def fill_relations(self):
        # Clear characteristics if update
        self.activity.categories.clear()
        for category in self.touristic_object.detailed_types.all():
            if category.active is True:
                self.activity.categories.add(
                    get_characteristic(
                        BUSINESS_AND_SERVICE_ACTIVITY[category.id]["identifier"]
                    )
                )

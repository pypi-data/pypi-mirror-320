# Local application / specific library imports
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.activities.specific import (
    BaseSpecificActivityUpdater,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.characteristics.generated_characteristics import (
    NATURAL_HERITAGE_ACTIVITY,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.utils import (
    get_characteristic,
)


class NaturalHeritageActivityUpdater(BaseSpecificActivityUpdater):
    def fill_relations(self):
        # Categories
        # Clear characteristics if update
        self.activity.categories.clear()
        for category in self.touristic_object.categories.all():
            if category.active is True:
                self.activity.categories.add(
                    get_characteristic(
                        NATURAL_HERITAGE_ACTIVITY[category.id]["identifier"]
                    )
                )

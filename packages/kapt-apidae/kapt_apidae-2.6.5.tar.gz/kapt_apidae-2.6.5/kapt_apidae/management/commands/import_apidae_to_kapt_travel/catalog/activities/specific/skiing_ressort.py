# Local application / specific library imports
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.activities.specific import (
    BaseSpecificActivityUpdater,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.characteristics.generated_characteristics import (
    SKIING_ACTIVITY_CATEGORY,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.utils import (
    get_characteristic,
)


class SkiingResortActivityUpdater(BaseSpecificActivityUpdater):
    def fill_relations(self):
        self.activity.categories.clear()
        for category in self.touristic_object.types.all():
            if category.active is True:
                self.activity.categories.add(
                    get_characteristic(
                        SKIING_ACTIVITY_CATEGORY[category.id]["identifier"]
                    )
                )

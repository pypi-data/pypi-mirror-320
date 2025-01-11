# Local application / specific library imports
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.activities.specific import (
    BaseSpecificActivityUpdater,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.characteristics.generated_characteristics import (
    EQUIPMENT_ACTIVITY,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.utils import (
    get_characteristic,
)


class EquipmentActivityUpdater(BaseSpecificActivityUpdater):
    def fill_relations(self):
        # Categories
        # Clear characteristics if update
        self.activity.categories.clear()
        for category in self.touristic_object.equipment_activities.all():
            if category.active is True:
                self.activity.categories.add(
                    get_characteristic(EQUIPMENT_ACTIVITY[category.id]["identifier"])
                )

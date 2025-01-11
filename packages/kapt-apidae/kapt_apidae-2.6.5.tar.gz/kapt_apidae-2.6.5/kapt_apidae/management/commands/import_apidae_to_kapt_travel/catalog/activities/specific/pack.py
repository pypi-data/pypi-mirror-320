# Local application / specific library imports
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.activities.specific import (
    BaseSpecificActivityUpdater,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.characteristics.generated_characteristics import (
    PACK_ACTIVITY_CATEGORY,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.utils import (
    get_characteristic,
)


class PackActivityUpdater(BaseSpecificActivityUpdater):
    def fill_attributes(self):
        super().fill_attributes()
        self.activity.number_of_days = self.touristic_object.days_quantity
        self.activity.number_of_nights = self.touristic_object.nights_quantity

    def fill_relations(self):
        self.activity.categories.clear()
        for category in self.touristic_object.activities_category.all():
            if category.active is True:
                self.activity.categories.add(
                    get_characteristic(
                        PACK_ACTIVITY_CATEGORY[category.id]["identifier"]
                    )
                )

        # 1483 -> Prix une personne
        self.common_updater.min_max_price(1483)

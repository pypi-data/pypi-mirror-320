# Local application / specific library imports
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.activities.specific import (
    BaseAccommodationActivityUpdater,
)


class OutdoorAccommodationActivityUpdater(BaseAccommodationActivityUpdater):
    def fill_attributes(self):
        super().fill_attributes()
        self.activity.area = self.touristic_object.surface_area
        # Camping
        if self.touristic_object.type_id in [2409, 2410]:
            if self.touristic_object.ranked_campingplot_quantity:
                self.activity.number_of_pitches = (
                    self.touristic_object.ranked_campingplot_quantity
                )

    def fill_relations(self):
        self.common_updater.prefectoral_classement(self.touristic_object.ranking)
        self.common_updater.labels()

        # 1446 -> Forfait
        self.common_updater.min_max_price(1446)

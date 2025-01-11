# Third party
from kapt_catalog.models import Structure

# Local application / specific library imports
from .mapping import CORRESPONDENCE_EVENT_REACH
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.activities.specific import (
    BaseSpecificActivityUpdater,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.characteristics.generated_characteristics import (
    EVENT_CATEGORIES,
    EVENT_TYPES,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.utils import (
    get_characteristic,
)
from kapt_apidae.utils import model_field_exists


class EventActivityUpdater(BaseSpecificActivityUpdater):
    def fill_attributes(self):
        super().fill_attributes()
        if (
            hasattr(self.touristic_object, "manifestation_reach")
            and hasattr(self.touristic_object.manifestation_reach, "id")
            and self.touristic_object.manifestation_reach.id
            in CORRESPONDENCE_EVENT_REACH.keys()
        ):
            self.activity.reach = CORRESPONDENCE_EVENT_REACH[
                self.touristic_object.manifestation_reach.id
            ]
        else:
            self.activity.reach = 0

        # Place name
        if not model_field_exists(Structure, "place_name"):
            self.activity.place_name = self.touristic_object.place_name

    def fill_relations(self):
        self.activity.types.clear()
        for event_type in self.touristic_object.manifestation_types.all():
            self.activity.types.add(
                get_characteristic(EVENT_TYPES[event_type.id]["identifier"])
            )

        # Event categories
        self.activity.categories.clear()
        for event_category in self.touristic_object.categories.all():
            self.activity.categories.add(
                get_characteristic(EVENT_CATEGORIES[event_category.id]["identifier"])
            )

        # 1754 -> Tarif adulte
        # 4123 -> Tarif unique
        # 4099 -> Groupe adulte
        # 4100 -> Groupe enfants
        self.common_updater.min_max_price([4123, 1754, 4099, 4100])

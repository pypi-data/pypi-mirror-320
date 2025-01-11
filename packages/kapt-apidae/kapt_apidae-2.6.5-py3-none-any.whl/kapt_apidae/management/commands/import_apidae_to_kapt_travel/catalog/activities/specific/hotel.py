from django.core.exceptions import ObjectDoesNotExist
from kapt_catalog.models.activities import Labelling

# Local application / specific library imports
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.activities.specific import (
    BaseAccommodationActivityUpdater,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.characteristics import (
    LABELS,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.utils import (
    get_touristic_label,
)


class HotelActivityUpdater(BaseAccommodationActivityUpdater):
    def fill_attributes(self):
        super().fill_attributes()
        self.activity.capacity = None
        self.activity.ranked_rooms_quantity = None
        self.activity.hotel_declared_rooms_quantity = None
        self.activity.single_rooms_quantity = None
        self.activity.double_rooms_quantity = None
        self.activity.suite_rooms_quantity = None
        self.activity.reduced_mobility_rooms_quantity = None

        if self.touristic_object.max_capacity:
            self.activity.capacity = self.touristic_object.max_capacity

        if self.touristic_object.ranked_rooms_quantity:
            self.activity.ranked_rooms_quantity = (
                self.touristic_object.ranked_rooms_quantity
            )

        if self.touristic_object.hotel_declared_rooms_quantity:
            self.activity.hotel_declared_rooms_quantity = (
                self.touristic_object.hotel_declared_rooms_quantity
            )

        if self.touristic_object.single_rooms_quantity:
            self.activity.single_rooms_quantity = (
                self.touristic_object.single_rooms_quantity
            )

        if self.touristic_object.double_rooms_quantity:
            self.activity.double_rooms_quantity = (
                self.touristic_object.double_rooms_quantity
            )

        if self.touristic_object.suite_rooms_quantity:
            self.activity.suite_rooms_quantity = (
                self.touristic_object.suite_rooms_quantity
            )

        if self.touristic_object.reduced_mobility_rooms_quantity:
            self.activity.reduced_mobility_rooms_quantity = (
                self.touristic_object.reduced_mobility_rooms_quantity
            )

        if (
            self.touristic_object.ranked_rooms_quantity
            or self.touristic_object.hotel_declared_rooms_quantity
        ):
            self.activity.number_of_rooms = (
                self.touristic_object.hotel_declared_rooms_quantity
                or self.touristic_object.ranked_rooms_quantity
            )

    def fill_relations(self):
        self.common_updater.prefectoral_classement(self.touristic_object.ranking)

        for chain in self.touristic_object.chains.all():
            current_label, _ = get_touristic_label(chain, LABELS)
            if current_label is not None:
                try:
                    labelling = Labelling.objects.get(
                        activity=self.activity, touristic_label=current_label
                    )
                except ObjectDoesNotExist:
                    labelling = Labelling()
                labelling.activity = self.activity
                labelling.touristic_label = current_label
                labelling.priority = 15
                labelling.save()

        self.common_updater.labels()

        # 1466 -> Chambre double
        self.common_updater.min_max_price(1466)

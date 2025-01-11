# Third party
from django.core.exceptions import ObjectDoesNotExist
from kapt_catalog.models.activities import Labelling
from kapt_catalog.models.activities.accommodation import AccommodationActivity

# Local application / specific library imports
from kapt_apidae.conf import settings as local_settings
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.activities.specific import (
    BaseAccommodationActivityUpdater,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.characteristics import (
    LABELS,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.utils import (
    get_touristic_label,
)


class RentalActivityUpdater(BaseAccommodationActivityUpdater):
    def fill_attributes(self):
        super().fill_attributes()
        self.activity.capacity = (
            self.touristic_object.capacity or self.touristic_object.max_capacity or 1
        )
        self.activity.max_capacity = self.touristic_object.max_capacity
        if self.touristic_object.type_id == 2619:
            self.activity.number_of_occurrences = (
                self.touristic_object.bedrooms_quantity or 1
            )
        self.activity.area = self.touristic_object.surface_area
        self.activity.number_of_rooms = self.touristic_object.bedrooms_quantity

    def fill_relations(self):
        # Chambres d'hotes
        if self.touristic_object.type_id == 2619:
            # 1484 -> 2 personnes
            self.common_updater.min_max_price(1484)
        # Meublès et gîtes et pas insolites
        elif self.touristic_object.type_id not in [2619, 2626]:
            # 1480 -> semaine
            self.common_updater.min_max_price(1480)
        elif (
            local_settings.IMPORT_UNUSUAL_ACCOMMODATION_RATES
            and self.touristic_object.type_id == 2626
        ):
            self.common_updater.min_max_price(
                local_settings.IMPORT_UNUSUAL_ACCOMMODATION_RATES_TYPE
            )
        # Labels
        self.common_updater.prefectoral_classement(
            self.touristic_object.prefectural_classification
        )

        if self.touristic_object.label_type is not None:
            current_label, _ = get_touristic_label(
                self.touristic_object.label_type, LABELS
            )
            if current_label is not None:
                try:
                    labelling = Labelling.objects.get(
                        activity=self.activity, touristic_label=current_label
                    )
                except ObjectDoesNotExist:
                    labelling = Labelling()
                labelling.activity = self.activity
                labelling.touristic_label = current_label
                labelling.priority = 20
                labelling.save()

        self.common_updater.labels()

        # Housing type
        habitation_types = self.touristic_object.habitation_types.all()
        housing_type = None
        if len(habitation_types) > 0:
            for habitation_type in habitation_types:
                if habitation_type.pk in AccommodationActivity.HOUSING_TYPES:
                    housing_type = habitation_type.pk
                    break

        self.activity.housing_type = housing_type

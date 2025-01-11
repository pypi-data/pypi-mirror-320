# Third party
from django.core.exceptions import ObjectDoesNotExist
from kapt_catalog.models.activities import Labelling

# Local application / specific library imports
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.activities.specific import (
    BaseSpecificActivityUpdater,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.characteristics import (
    LABELS,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.characteristics.generated_characteristics import (
    GROUP_ACCOMMODATION_AGREMENTS,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.utils import (
    get_characteristic,
    get_touristic_label,
)


class GroupAccommodationActivityUpdater(BaseSpecificActivityUpdater):
    def fill_attributes(self):
        super().fill_attributes()
        self.activity.capacity = self.touristic_object.capacity

    def fill_relations(self):
        # Labels
        self.common_updater.prefectoral_classement(
            self.touristic_object.prefectural_classification
        )

        if self.touristic_object.chain_and_label is not None:
            current_label, _ = get_touristic_label(
                self.touristic_object.chain_and_label, LABELS
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
                labelling.priority = 1
                labelling.save()

        self.common_updater.labels()

    def fill_agrements(self):
        for agrement in self.touristic_object.agrements.all():
            if agrement.active is True:
                self.activity.characteristics.add(
                    get_characteristic(
                        GROUP_ACCOMMODATION_AGREMENTS[agrement.id]["identifier"]
                    )
                )

    def update(self):
        activity = super().update()
        self.fill_agrements()
        return activity

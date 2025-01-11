# Third party
from django.core.exceptions import ObjectDoesNotExist
from kapt_catalog.models.activities import Labelling

# Local application / specific library imports
from kapt_apidae.conf import settings as local_settings
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.activities.specific import (
    BaseSpecificActivityUpdater,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.characteristics import (
    RESTAURANT_RANKING,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.characteristics.generated_characteristics import (
    RESTAURANT_SPECIALTIES,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.characteristics.handmade_characteristics import (
    RESTAURANT_CATEGORY,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.utils import (
    get_characteristic,
    get_touristic_label,
)


class MealActivityUpdater(BaseSpecificActivityUpdater):
    def fill_attributes(self):
        super().fill_attributes()
        self.activity.capacity = self.touristic_object.maximum_capacity

    def fill_relations(self):
        # Categories
        # Clear characteristics if update
        self.activity.categories.clear()
        self.common_updater.min_max_price(local_settings.MEAL_RATES_TYPE)

        for category in self.touristic_object.categories.all():
            if category.active is True:
                self.activity.categories.add(
                    get_characteristic(RESTAURANT_CATEGORY[category.id]["identifier"])
                )

        # Specialties
        # Clear characteristics if update
        self.activity.specialties.clear()
        for specialty in self.touristic_object.specialities.all():
            if specialty.active is True:
                self.activity.specialties.add(
                    get_characteristic(
                        RESTAURANT_SPECIALTIES[specialty.id]["identifier"]
                    )
                )

        # Guides ranking
        for label in (
            self.touristic_object.guides_ranking.all()
            | self.touristic_object.chains.all()
        ):
            if label.active is True:
                current_label, ranking_label = get_touristic_label(
                    label, RESTAURANT_RANKING
                )
                if current_label is not None:
                    try:
                        labelling = Labelling.objects.get(
                            activity=self.activity, touristic_label=current_label
                        )
                    except ObjectDoesNotExist:
                        labelling = Labelling(
                            activity=self.activity,
                            touristic_label=current_label,
                            priority=1,
                        )
                    # TODO: bib gourmand
                    if ranking_label is not None:
                        labelling.rating = ranking_label
                    labelling.save()

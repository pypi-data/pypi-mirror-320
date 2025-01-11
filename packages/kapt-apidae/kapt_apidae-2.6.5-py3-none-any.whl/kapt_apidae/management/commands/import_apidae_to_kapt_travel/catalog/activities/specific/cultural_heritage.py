# Local application / specific library imports
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.activities.specific import (
    BaseSpecificActivityUpdater,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.characteristics.generated_characteristics import (
    CULTURAL_HERITAGE_ACTIVITY,
    CULTURAL_HERITAGE_THEME,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.utils import (
    get_characteristic,
)


class CulturalHeritageActivityUpdater(BaseSpecificActivityUpdater):
    def fill_relations(self):
        # Categories
        # Clear characteristics if update
        self.activity.categories.clear()
        self.activity.themes.clear()

        # Categories
        if self.touristic_object.type_id is not None:
            self.activity.categories.add(
                get_characteristic(
                    CULTURAL_HERITAGE_ACTIVITY[self.touristic_object.type_id][
                        "identifier"
                    ]
                )
            )
        # Themes
        for theme in self.touristic_object.subjects.all():
            # Check if the BaseElement is active, else pass
            if theme.active is True:
                self.activity.themes.add(
                    get_characteristic(CULTURAL_HERITAGE_THEME[theme.id]["identifier"])
                )
        # 1750 -> Tarif adulte
        # 5250 -> Plein tarif
        self.common_updater.min_max_price([1750, 5250])

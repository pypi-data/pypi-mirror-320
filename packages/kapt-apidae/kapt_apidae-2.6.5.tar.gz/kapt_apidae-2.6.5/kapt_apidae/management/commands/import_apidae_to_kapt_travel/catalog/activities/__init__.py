# Third party
from kapt_catalog.models import ActivityReference
from kapt_catalog.models.activities.accommodation import (
    AccommodationActivity,
    BnBActivity,
    CamperVanActivity,
    CampingActivity,
    HolidayVillageActivity,
    HomestayActivity,
    HotelActivity,
    RelayActivity,
    RentalActivity,
    YouthHostelActivity,
)
from kapt_catalog.models.activities.event import EventActivity
from kapt_catalog.models.activities.leisure import LeisureActivity
from kapt_catalog.models.activities.meal import MealActivity, TableActivity
from kapt_catalog.models.activities.pack import PackActivity
from kapt_catalog.models.activities.poi import PointOfInterestActivity

# Local application / specific library imports
from kapt_apidae.management import ScriptError
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.activities.specific.area import (
    AreaActivityUpdater,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.activities.specific.business import (
    BusinessActivityUpdater,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.activities.specific.cultural_heritage import (
    CulturalHeritageActivityUpdater,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.activities.specific.equipment import (
    EquipmentActivityUpdater,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.activities.specific.event.updater import (
    EventActivityUpdater,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.activities.specific.group_accommodation import (
    GroupAccommodationActivityUpdater,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.activities.specific.hotel import (
    HotelActivityUpdater,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.activities.specific.leisure import (
    LeisureActivityUpdater,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.activities.specific.meal import (
    MealActivityUpdater,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.activities.specific.natural_heritage import (
    NaturalHeritageActivityUpdater,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.activities.specific.outdoor_accommodation import (
    OutdoorAccommodationActivityUpdater,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.activities.specific.pack import (
    PackActivityUpdater,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.activities.specific.rental import (
    RentalActivityUpdater,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.activities.specific.skiing_ressort import (
    SkiingResortActivityUpdater,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.activities.specific.structure import (
    StructureActivityUpdater,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.activities.specific.tasting import (
    TastingActivityUpdater,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.characteristics.generated_characteristics import (
    COMMERCES_SERVICES_TYPES,
    SKIING_ACTIVITY_TYPE,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.characteristics.handmade_characteristics import (
    ITINERARY_EQUIPMENT_ACTIVITY,
    RENTAL_ACCOMMODATION_TYPE,
    RESTAURANT_TYPE,
    STRUCTURE_TYPE,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.utils import (
    get_characteristic,
)
from kapt_apidae.models import (
    Activity,
    AllInclusiveTrip,
    Area,
    BusinessAndService,
    CelebrationAndManifestation,
    CulturalHeritage,
    Equipment,
    GroupAccommodation,
    HotelAccommodation,
    NaturalHeritage,
    OutDoorHotelAccommodation,
    RentalAccommodation,
    Restaurant,
    SkiingArea,
    Structure,
    Tasting,
)


class ActivityUpdater:
    touristic_object = None
    activity = None

    def __init__(self, touristic_object, activity):
        self.touristic_object = touristic_object
        self.activity = activity

    def update(self):
        if isinstance(self.touristic_object, RentalAccommodation):
            if not isinstance(self.activity, TableActivity):
                rental_activity_updater = RentalActivityUpdater(
                    self.activity, self.touristic_object
                )
                rental_activity_updater.update()

        if isinstance(self.touristic_object, Restaurant):
            meal_activity_updater = MealActivityUpdater(
                self.activity, self.touristic_object
            )
            meal_activity_updater.update()

        if isinstance(self.touristic_object, CulturalHeritage):
            cultural_heritage_activity_updater = CulturalHeritageActivityUpdater(
                self.activity, self.touristic_object
            )
            cultural_heritage_activity_updater.update()

        if isinstance(self.touristic_object, NaturalHeritage):
            natural_heritage_activity_updater = NaturalHeritageActivityUpdater(
                self.activity, self.touristic_object
            )
            natural_heritage_activity_updater.update()

        if isinstance(self.touristic_object, Equipment):
            is_itinerary = False
            for activity in self.touristic_object.equipment_activities.all():
                if activity.id in ITINERARY_EQUIPMENT_ACTIVITY:
                    is_itinerary = True

            if is_itinerary:
                equipment_activity_updater = LeisureActivityUpdater(
                    self.activity, self.touristic_object
                )
            else:
                equipment_activity_updater = EquipmentActivityUpdater(
                    self.activity, self.touristic_object
                )

            equipment_activity_updater.update()

        if isinstance(self.touristic_object, Tasting):
            tasting_activity_updater = TastingActivityUpdater(
                self.activity, self.touristic_object
            )
            tasting_activity_updater.update()

        if isinstance(self.touristic_object, BusinessAndService):
            business_activity_updater = BusinessActivityUpdater(
                self.activity, self.touristic_object
            )
            business_activity_updater.update()

        if isinstance(self.touristic_object, Activity):
            leisure_activity_updater = LeisureActivityUpdater(
                self.activity, self.touristic_object
            )
            leisure_activity_updater.update()

        if isinstance(self.touristic_object, HotelAccommodation):
            hotel_activity_updater = HotelActivityUpdater(
                self.activity, self.touristic_object
            )
            hotel_activity_updater.update()

        if isinstance(self.touristic_object, GroupAccommodation):
            group_accommodation_activity_updater = GroupAccommodationActivityUpdater(
                self.activity, self.touristic_object
            )
            group_accommodation_activity_updater.update()

        if isinstance(self.touristic_object, OutDoorHotelAccommodation):
            outdoor_accommodation_activity_updater = (
                OutdoorAccommodationActivityUpdater(
                    self.activity, self.touristic_object
                )
            )
            outdoor_accommodation_activity_updater.update()

        if isinstance(self.touristic_object, Structure):
            structure_activity_updater = StructureActivityUpdater(
                self.activity, self.touristic_object
            )
            structure_activity_updater.update()

        if isinstance(self.touristic_object, SkiingArea):
            skiing_ressort_activity_updater = SkiingResortActivityUpdater(
                self.activity, self.touristic_object
            )
            skiing_ressort_activity_updater.update()

        if isinstance(self.touristic_object, AllInclusiveTrip):
            pack_activity_updater = PackActivityUpdater(
                self.activity, self.touristic_object
            )
            pack_activity_updater.update()

        if isinstance(self.touristic_object, CelebrationAndManifestation):
            event_activity_updater = EventActivityUpdater(
                self.activity, self.touristic_object
            )
            event_activity_updater.update()

        if isinstance(self.touristic_object, Area):
            area_activity_updater = AreaActivityUpdater(
                self.activity, self.touristic_object
            )
            area_activity_updater.update()


class ActivityCreator:
    touristic_object = None
    structure = None
    aspect = None

    def __init__(self, touristic_object, structure, aspect):
        self.touristic_object = touristic_object
        self.structure = structure
        self.aspect = aspect

    def create(self):
        activity = None

        if isinstance(self.touristic_object, RentalAccommodation):
            if self.touristic_object.type_id == 2626:  # Insolite, a BNB with no rooms ?
                activity = BnBActivity(
                    structure=self.structure,
                    type=get_characteristic(
                        RENTAL_ACCOMMODATION_TYPE[self.touristic_object.type_id][
                            "identifier"
                        ]
                    ),
                )
            elif self.touristic_object.type_id == 2619:  # Bnb
                activity = BnBActivity(
                    structure=self.structure,
                    type=get_characteristic("bnb-activity-type"),
                )
            elif self.touristic_object.type_id == 5902:  # HomeStay
                activity = HomestayActivity(
                    structure=self.structure,
                    type=get_characteristic("homestay-activity-type"),
                )
            else:
                activity = RentalActivity(
                    structure=self.structure,
                    type=get_characteristic(
                        RENTAL_ACCOMMODATION_TYPE[self.touristic_object.type_id][
                            "identifier"
                        ]
                    ),
                )

        if isinstance(self.touristic_object, Restaurant):
            try:
                meal_type = get_characteristic(
                    RESTAURANT_TYPE[self.touristic_object.type_id]["identifier"]
                )
            except KeyError:
                meal_type = get_characteristic("restaurant-activity-type")
            activity = MealActivity(structure=self.structure, type=meal_type)

        if isinstance(self.touristic_object, CulturalHeritage):
            activity = PointOfInterestActivity(
                structure=self.structure,
                type=get_characteristic("cultural-heritage-activity"),
            )

        if isinstance(self.touristic_object, NaturalHeritage):
            activity = PointOfInterestActivity(
                structure=self.structure,
                type=get_characteristic("natural-heritage-activity"),
            )

        if isinstance(self.touristic_object, SkiingArea):
            activity = PointOfInterestActivity(
                structure=self.structure,
                type=get_characteristic(
                    SKIING_ACTIVITY_TYPE[self.touristic_object.classification_id][
                        "identifier"
                    ]
                ),
            )

        if isinstance(self.touristic_object, Equipment):
            is_itinerary = False
            for activity in self.touristic_object.equipment_activities.all():
                if activity.id in ITINERARY_EQUIPMENT_ACTIVITY:
                    is_itinerary = True

            if is_itinerary:
                activity = LeisureActivity(
                    structure=self.structure,
                    type=get_characteristic("equipment-activity"),
                )
            else:
                activity = PointOfInterestActivity(
                    structure=self.structure,
                    type=get_characteristic("equipment-activity"),
                )

        if isinstance(self.touristic_object, Tasting):
            activity = PointOfInterestActivity(
                structure=self.structure, type=get_characteristic("tasting-activity")
            )

        # TODO: Put type initialisation into update method
        if isinstance(self.touristic_object, BusinessAndService):
            activity = PointOfInterestActivity(
                structure=self.structure,
                type=get_characteristic(
                    COMMERCES_SERVICES_TYPES[self.touristic_object.type_id][
                        "identifier"
                    ]
                ),
            )

        if isinstance(self.touristic_object, Activity):
            # Type Sport
            if self.touristic_object.type_id == 1789:
                type_object = get_characteristic("sport-activity")
            # Type Cultural
            # 362662 specific case for grenoble as they can't modify this object (waiting for 6 month, without results)
            elif (
                self.touristic_object.type_id == 1790
                or self.touristic_object.pk == 362662
            ):
                type_object = get_characteristic("cultural-activity")
            else:
                raise ScriptError("Activity unknown", self.touristic_object.type)
            activity = LeisureActivity(structure=self.structure, type=type_object)

        if isinstance(self.touristic_object, HotelAccommodation):
            try:
                activity = HotelActivity(
                    structure=self.structure,
                    type=get_characteristic(
                        RENTAL_ACCOMMODATION_TYPE[self.touristic_object.type_id][
                            "identifier"
                        ]
                    ),
                )
            except KeyError:
                activity = HotelActivity(
                    structure=self.structure,
                    type=get_characteristic("hotel-activity-type"),
                )

        if isinstance(self.touristic_object, GroupAccommodation):
            # HolidayVillage
            if self.touristic_object.type_id in [2642, 2644, 2651, 2413, 2649, 2650]:
                activity = HolidayVillageActivity(
                    structure=self.structure,
                    type=get_characteristic(
                        RENTAL_ACCOMMODATION_TYPE[self.touristic_object.type_id][
                            "identifier"
                        ]
                    ),
                )

            elif self.touristic_object.type_id in [2647, 2648]:
                activity = RelayActivity(
                    structure=self.structure,
                    type=get_characteristic(
                        RENTAL_ACCOMMODATION_TYPE[self.touristic_object.type_id][
                            "identifier"
                        ]
                    ),
                )

            # elif self.touristic_object.type_id in [2649, 2650]:
            #     activity = HotelActivity(structure=self.structure, type=get_characteristic(RENTAL_ACCOMMODATION_TYPE[self.touristic_object.type_id]['identifier']))

            elif self.touristic_object.type_id in [
                2641,
                2640,
                2652,
            ]:  # Auberges de jeunesse
                activity = YouthHostelActivity(
                    structure=self.structure,
                    type=get_characteristic(
                        RENTAL_ACCOMMODATION_TYPE[self.touristic_object.type_id][
                            "identifier"
                        ]
                    ),
                )

            elif self.touristic_object.type_id in [2643]:  # Gîte de groupe
                activity = RentalActivity(
                    structure=self.structure,
                    type=get_characteristic(
                        RENTAL_ACCOMMODATION_TYPE[self.touristic_object.type_id][
                            "identifier"
                        ]
                    ),
                )

            elif self.touristic_object.type_id in [2646]:  # Autres hébergements
                activity = AccommodationActivity(
                    structure=self.structure,
                    type=get_characteristic(
                        RENTAL_ACCOMMODATION_TYPE[self.touristic_object.type_id][
                            "identifier"
                        ]
                    ),
                )

        if isinstance(self.touristic_object, OutDoorHotelAccommodation):
            # Camping
            if self.touristic_object.type_id in [2409, 2410, 2416, 3722]:
                activity = CampingActivity(
                    structure=self.structure,
                    type=get_characteristic(
                        RENTAL_ACCOMMODATION_TYPE[self.touristic_object.type_id][
                            "identifier"
                        ]
                    ),
                )
            # Campervan
            elif self.touristic_object.type_id in [2418]:
                activity = CamperVanActivity(
                    structure=self.structure,
                    type=get_characteristic(
                        RENTAL_ACCOMMODATION_TYPE[self.touristic_object.type_id][
                            "identifier"
                        ]
                    ),
                )
            # HolidayVillage
            elif self.touristic_object.type_id in [2413]:
                activity = HolidayVillageActivity(
                    structure=self.structure,
                    type=get_characteristic(
                        RENTAL_ACCOMMODATION_TYPE[self.touristic_object.type_id][
                            "identifier"
                        ]
                    ),
                )

            # Other outdoor Accommodation
            else:
                activity = AccommodationActivity(
                    structure=self.structure,
                    type=get_characteristic(
                        RENTAL_ACCOMMODATION_TYPE[self.touristic_object.type_id][
                            "identifier"
                        ]
                    ),
                )

        if isinstance(self.touristic_object, Structure):
            # Office du tourisme
            if self.touristic_object.type_id in [3166, 3196, 3840, 3988, 4011]:
                activity = PointOfInterestActivity(
                    structure=self.structure,
                    type=get_characteristic(
                        STRUCTURE_TYPE[self.touristic_object.type_id]["identifier"]
                    ),
                )

        if isinstance(self.touristic_object, AllInclusiveTrip):
            activity = PackActivity(
                structure=self.structure, type=get_characteristic("pack-activity")
            )

        if isinstance(self.touristic_object, CelebrationAndManifestation):
            activity = EventActivity(
                structure=self.structure, type=get_characteristic("event-activity")
            )

        if isinstance(self.touristic_object, Area):
            activity = PointOfInterestActivity(
                structure=self.structure, type=get_characteristic("area-activity")
            )

        if activity:
            if hasattr(activity, "aspect") and self.aspect is not None:
                activity.aspect = self.aspect
                structure_reference = activity.structure.reference
                activity.reference = ActivityReference.objects.get(
                    structure_reference=structure_reference
                )
            activity_updater = ActivityUpdater(self.touristic_object, activity)
            activity_updater.update()
        else:
            raise ScriptError("This activity is not yet handled", self.touristic_object)

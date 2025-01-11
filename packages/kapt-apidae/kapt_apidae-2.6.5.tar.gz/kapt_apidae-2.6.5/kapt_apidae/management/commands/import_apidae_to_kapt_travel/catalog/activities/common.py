# Standard Library
from datetime import datetime

# Third party
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max, Min
from kapt_associative_life.models.profile import ActivityReferenceProfile
from kapt_catalog.models import ActivityTranslation, Description, Structure
from kapt_catalog.models.activities import Labelling
from kapt_catalog.models.activities.accommodation import AccommodationActivity
from kapt_catalog.models.activities.business_tourism import (
    BusinessTourismService,
    MeetingRoom,
    RoomLayout,
)
from parler.utils.context import switch_language

# Local application / specific library imports
from .common_mixins.periods.mixin import PeriodActivityUpdateMixin
from kapt_apidae.conf.settings import GENERATE_ACTIVITY_SLUG
from kapt_apidae.management import logger
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.characteristics import (
    LABELS,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.characteristics.generated_characteristics import (
    ADAPTED_TOURISM,
    BUSINESS_TOURISM_ACCOMMODATION,
    BUSINESS_TOURISM_CATERING,
    BUSINESS_TOURISM_ROOMS_EQUIPMENTS,
    BUSINESS_TOURISM_ROOMS_LAYOUTS,
    BUSINESS_TOURISM_ROOMS_USAGE,
    CONFORT_SERVICES,
    CUSTOMER_TYPES,
    ENVIRONMENT,
    EQUIPMENTS,
    PAYMENT_METHOD,
    ROOM_EQUIPED_FOR,
    SERVICES,
    TYPOLOGIES_PROMO_APIDAE,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.characteristics.handmade_characteristics import (
    REFERENT_LABEL,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.utils import (
    copy_translated_fields,
    get_characteristic,
    get_touristic_label,
    is_translated_fields_empty,
)
from kapt_apidae.models import PriceDescription
from kapt_apidae.utils import model_field_exists


class CommonActivityUpdater(PeriodActivityUpdateMixin):
    touristic_object = None
    activity = None

    def __init__(self, touristic_object, activity):
        self.touristic_object = touristic_object
        self.activity = activity

    def update(self):
        # Caution: Gallery has been moved to structure...

        # Descriptions
        self.update_descriptions()

        # Confort services, Equipements, Services, Adapted tourism
        self.equipments_and_services()

        # Accessibility Labels
        self.accessibility_labels()

        # Payment methods
        self.payment_methods()

        # Typologies promo
        self.TYPOLOGIES_PROMO_APIDAE()

        # Environments
        self.environment()

        # Customer spec
        self.customer_specs()

        # Name
        self.name()

        # Business tourism
        self.business_tourism_services()

        # Periods
        self.update_periods()

        # Place name
        if not model_field_exists(Structure, "place_name"):
            self.activity.place_name = self.touristic_object.place_name

        # Force slug generation
        if GENERATE_ACTIVITY_SLUG is True:
            self.activity.generate_slug()

        # Activity is complete
        self.activity.is_complete = True

        self.save_activity()

        if self.touristic_object.kapt_catalog_activity_id != self.activity.id:
            self.touristic_object.kapt_catalog_activity_id = self.activity.id
            self.touristic_object.save()

        logger.info(
            str(self.activity.__class__.__name__)
            + " n° "
            + str(self.touristic_object.id)
            + " - "
            + self.activity.name
            + " updated."
        )

    def update_descriptions(self):
        # Complete
        self._update_description("detailed-description", "description")

        # Descriptions brèves
        self._update_description("short-description", "short_description")

        # Periodes d'ouvertures
        self._update_description(
            "opening-textual-description", "opening_textual_description"
        )

        # Tarifs en clairs
        self._update_description(
            "pricing-textual-description", "pricing_textual_description"
        )

        # Compléments de tarifs
        self._update_description(
            "additional-pricing-description", "additional_pricing_description"
        )

        # Bons plans
        self._update_description("good-deal-description", "good_deal")

        # Moyens d'accès
        self._update_description("access-means-description", "access_means")

        # Infos d'accueil
        self._update_description(
            "further-welcoming-informations-description",
            "further_welcoming_informations",
        )

        # Infos de résa
        self._update_description(
            "additional-booking-informations-description",
            "additional_booking_informations",
        )

        # Infos de visites
        self._update_description(
            "additional-visit-informations-description", "additional_visit_informations"
        )

    def equipments_and_services(self):
        # Reset
        self.activity.characteristics.clear()

        # Comfort services
        for service in self.touristic_object.comfort_services.filter(active=True):
            self.activity.characteristics.add(
                get_characteristic(CONFORT_SERVICES[service.id]["identifier"])
            )

        # Equipements
        for equipment in self.touristic_object.equipments.filter(active=True):
            self.activity.characteristics.add(
                get_characteristic(EQUIPMENTS[equipment.id]["identifier"])
            )

        # Services
        for service in self.touristic_object.services.filter(active=True):
            self.activity.characteristics.add(
                get_characteristic(SERVICES[service.id]["identifier"])
            )

        # Adapted tourism
        for service in self.touristic_object.accessibility_informations.filter(
            active=True
        ):
            self.activity.characteristics.add(
                get_characteristic(ADAPTED_TOURISM[service.id]["identifier"])
            )

        # Business tourism
        for service in self.touristic_object.business_tourism_rooms_equipped_for.filter(
            active=True
        ):
            self.activity.characteristics.add(
                get_characteristic(ROOM_EQUIPED_FOR[service.id]["identifier"])
            )

    def accessibility_labels(self, label_priority=5):
        for label in self.touristic_object.accessibility_labels.all():
            if label.active is True:
                touristic_label, _ = get_touristic_label(label, LABELS)
                if touristic_label is not None:
                    try:
                        labelling = Labelling.objects.get(
                            activity=self.activity, touristic_label=touristic_label
                        )
                    except ObjectDoesNotExist:
                        labelling = Labelling(priority=5)

                    labelling.activity = self.activity
                    labelling.touristic_label = touristic_label
                    labelling.save()

    def payment_methods(self):
        self.activity.means_of_payment.clear()

        for payment in self.touristic_object.payment_methods.all():
            if payment.active is True:
                self.activity.means_of_payment.add(
                    get_characteristic(PAYMENT_METHOD[payment.id]["identifier"])
                )

    def TYPOLOGIES_PROMO_APIDAE(self):
        self.activity.typologies_promo.clear()

        for promo in self.touristic_object.offers_labels.all():
            if promo.active is True:
                self.activity.typologies_promo.add(
                    get_characteristic(TYPOLOGIES_PROMO_APIDAE[promo.id]["identifier"])
                )

    def environment(self):
        self.activity.environment.clear()

        for env in self.touristic_object.environment.all():
            if env.active is True:
                self.activity.environment.add(
                    get_characteristic(ENVIRONMENT[env.id]["identifier"])
                )

    def customer_specs(self):
        # Customer type
        self.activity.customer_types.clear()

        for customer_type in self.touristic_object.customers_type.exclude(family_id=35):
            if customer_type.active is True:
                self.activity.customer_types.add(
                    get_characteristic(CUSTOMER_TYPES[customer_type.id]["identifier"])
                )

        # Age
        self.activity.min_age = self.touristic_object.minimum_age
        self.activity.max_age = self.touristic_object.maximum_age

        if self.touristic_object.minimum_age_unit == "MOIS":
            self.activity.min_age_unit = self.activity.AGE_UNIT.month
        elif self.touristic_object.minimum_age_unit == "ANNEE":
            self.activity.min_age_unit = self.activity.AGE_UNIT.year
        else:
            self.activity.min_age_unit = None

        if self.touristic_object.maximum_age_unit == "MOIS":
            self.activity.max_age_unit = self.activity.AGE_UNIT.month
        elif self.touristic_object.maximum_age_unit == "ANNEE":
            self.activity.max_age_unit = self.activity.AGE_UNIT.year
        else:
            self.activity.max_age_unit = None

    def prefectoral_classement(self, label):
        # Classement préfectoral
        if label is not None:
            current_label, rating_prefectoral_label = get_touristic_label(label, LABELS)
            try:
                labelling = Labelling.objects.get(
                    activity=self.activity, touristic_label=current_label
                )
            except ObjectDoesNotExist:
                labelling = Labelling()

            labelling.activity = self.activity
            labelling.touristic_label = current_label
            labelling.priority = 20
            if rating_prefectoral_label is not None:
                labelling.rating = rating_prefectoral_label
            labelling.save()

    def labels(self):
        # Labels secondaires, include ranking for a first label
        for label in self.touristic_object.labels.all():
            PRIORITY = 10
            if label.active is True:
                current_label, rating_label = get_touristic_label(label, LABELS)
                if current_label is not None:
                    try:
                        labelling = Labelling.objects.get(
                            activity=self.activity, touristic_label=current_label
                        )
                    except ObjectDoesNotExist:
                        labelling = Labelling()

                    labelling.activity = self.activity
                    labelling.touristic_label = current_label
                    # Upgrade priority if the label is kind of gdf, clé vacances, ...
                    if current_label.identifier in REFERENT_LABEL:
                        PRIORITY += 5
                    labelling.priority = PRIORITY
                    if rating_label is not None:
                        labelling.rating = rating_label
                    labelling.save()

        self.activity.update_main_labelling()
        self.activity.update_default_labelling()
        self.activity.update_prefectoral_labelling()

    def name(self):
        # Activity name
        for language in settings.LANGUAGES:
            language_code = language[0]

            with switch_language(self.activity, language_code):
                source_label_name = "label_{}".format(language[0])
                source_label_value = getattr(
                    self.touristic_object, source_label_name, None
                )
                if source_label_value:
                    self.activity.name = source_label_value
                else:
                    locales = ActivityTranslation.objects.filter(
                        master=self.activity, language_code=language_code
                    ).exclude(language_code=settings.LANGUAGE_CODE)
                    if locales.exists():
                        locales.delete()

    def business_tourism_services(self):
        self.activity.businesstourismservice_set.all().delete()

        if self.touristic_object.business_tourism_provided:
            business_tourism_service = BusinessTourismService.objects.create(
                activity=self.activity,
                business_tourism_max_capacity=self.touristic_object.business_tourism_max_capacity,
                equipped_meeting_rooms_quantity=self.touristic_object.equipped_meeting_rooms_quantity,
                adjustable_rooms_quantity=self.touristic_object.adjustable_rooms_quantity,
            )

            for (
                usage
            ) in self.touristic_object.business_tourism_rooms_equipped_for.all():
                business_tourism_service.characteristics.add(
                    get_characteristic(
                        BUSINESS_TOURISM_ROOMS_USAGE[usage.id]["identifier"]
                    )
                )

            for (
                equipment
            ) in self.touristic_object.business_tourism_rooms_equipments.all():
                business_tourism_service.characteristics.add(
                    get_characteristic(
                        BUSINESS_TOURISM_ROOMS_EQUIPMENTS[equipment.id]["identifier"]
                    )
                )

            for catering_characteristic in self.touristic_object.catering_rooms.all():
                business_tourism_service.characteristics.add(
                    get_characteristic(
                        BUSINESS_TOURISM_CATERING[catering_characteristic.id][
                            "identifier"
                        ]
                    )
                )

            for (
                accommodation_characteristic
            ) in self.touristic_object.accommodation_rooms.all():
                business_tourism_service.characteristics.add(
                    get_characteristic(
                        BUSINESS_TOURISM_ACCOMMODATION[accommodation_characteristic.id][
                            "identifier"
                        ]
                    )
                )

            for meeting_room in self.touristic_object.meeting_rooms.all():
                kaptravel_meeting_room = MeetingRoom.objects.create(
                    business_tourism_service=business_tourism_service,
                    name=meeting_room.name,
                    capacity=meeting_room.max_capacity,
                    area=meeting_room.surface_area,
                    height=meeting_room.height,
                    natural_lighting=meeting_room.natural_lighting,
                )

                if meeting_room.minimum_price or meeting_room.maximum_price:
                    kaptravel_meeting_room.min_price = meeting_room.minimum_price
                    kaptravel_meeting_room.max_price = meeting_room.maximum_price
                elif meeting_room.day_minimum_price or meeting_room.day_maximum_price:
                    kaptravel_meeting_room.min_price = meeting_room.day_minimum_price
                    kaptravel_meeting_room.max_price = meeting_room.day_maximum_price
                kaptravel_meeting_room.save()

                if not is_translated_fields_empty(meeting_room, "description"):
                    description_type = get_characteristic("detailed-description")
                    description_object = Description()
                    copy_translated_fields(
                        meeting_room, description_object, "description", "text"
                    )
                    description_object.type = description_type
                    description_object.content_object = kaptravel_meeting_room
                    description_object.save()

                for room_layout in meeting_room.layouts.all():
                    layout = get_characteristic(
                        BUSINESS_TOURISM_ROOMS_LAYOUTS[room_layout.layout.id][
                            "identifier"
                        ]
                    )
                    if room_layout.capacity is None:
                        room_layout.capacity = 0
                    RoomLayout.objects.create(
                        meeting_room=kaptravel_meeting_room,
                        capacity=room_layout.capacity,
                        layout=layout,
                    )

    def min_max_price(self, tarifs_type):
        """
        Associates a min and max price to an activity.
        """
        if isinstance(tarifs_type, int):
            tarifs_type = [tarifs_type]

        today = datetime.now()
        prices_dict = PriceDescription.objects.filter(
            pricing_periods__pricing_periods_objects_set=self.touristic_object.id,
            type__in=tarifs_type,
            pricing_periods__ending__gte=today,
        ).aggregate(Min("minimum_price"), Max("maximum_price"))
        self.activity.min_price = prices_dict["minimum_price__min"]
        self.activity.max_price = prices_dict["maximum_price__max"]

        # Is free
        if hasattr(self.touristic_object, "is_free"):
            self.activity.is_free = self.touristic_object.is_free

    def save_activity(self):
        if isinstance(self.activity, AccommodationActivity):
            self.activity.save(update_capacity=False, update_number_of_rooms=False)
        else:
            self.activity.save()

    def reference_profile(self):
        """
        Associates an activity profile to an activity.
        """
        try:
            assert self.activity.reference.profile is not None
        except (AssertionError, ActivityReferenceProfile.DoesNotExist):
            ref_profile = ActivityReferenceProfile(
                activity_reference=self.activity.reference
            )
            ref_profile.save()

    def _update_description(
        self, description_type_id, touristic_object_description_field
    ):
        description_type = get_characteristic(description_type_id)
        description_queryset = Description.objects.filter(
            content_type=ContentType.objects.get_for_model(self.activity),
            object_id=self.activity.id,
            type=description_type,
        )
        if not is_translated_fields_empty(
            self.touristic_object, touristic_object_description_field
        ):
            if description_queryset.exists():
                description_object = description_queryset[0]
            else:
                description_object = Description()
            copy_translated_fields(
                self.touristic_object,
                description_object,
                touristic_object_description_field,
                "text",
            )
            description_object.type = description_type
            description_object.content_object = self.activity
            description_object.save()
        else:
            if description_queryset.exists():
                description_queryset[0].delete()

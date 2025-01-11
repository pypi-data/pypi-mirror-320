# Third party
from modeltranslation.translator import TranslationOptions, translator

# Local application / specific library imports
# Polymorphic models
from kapt_apidae.models import (
    Activity,
    AllInclusiveTrip,
    Area,
    BaseElement,
    BookingOrganisation,
    BusinessAndService,
    CelebrationAndManifestation,
    CommunicationInfo,
    Contact,
    CulturalHeritage,
    Description,
    Equipment,
    GroupAccommodation,
    HotelAccommodation,
    MeetingRoom,
    Multimedia,
    NaturalHeritage,
    OpeningPeriod,
    OutDoorHotelAccommodation,
    PriceDescription,
    RentalAccommodation,
    Restaurant,
    SkiingArea,
    Structure,
    Tasting,
    TouristicObject,
)


class BaseElementTranslationOptions(TranslationOptions):
    fields = ("label",)


class TouristicObjectOptions(TranslationOptions):
    fields = (
        "label",
        "short_description",
        "description",
        "good_deal",
        "access_means",
        "links_description",
        "further_welcoming_informations",
        "opening_textual_description",
        "pricing_textual_description",
        "additional_booking_informations",
        "additional_visit_informations",
    )


class CommunicationInfoOptions(TranslationOptions):
    fields = ("description",)


class ContactOptions(TranslationOptions):
    fields = ("position",)


class OpeningPeriodOptions(TranslationOptions):
    fields = ("label", "further_hourly_informations")


class PriceDescriptionOptions(TranslationOptions):
    fields = ("additionnal_description",)


class BookingOrganisationOptions(TranslationOptions):
    fields = ("description",)


class MultimediaOptions(TranslationOptions):
    fields = ("name", "legend", "copyright", "remark")


class MeetingRoomOptions(TranslationOptions):
    fields = ("description",)


class AreaOptions(TranslationOptions):
    fields = (
        "short_description_winter",
        "description_winter",
        "minimum_age_ski_teaching",
        "kindergarten_age_groups",
        "resting_places_description",
        "accommodations_description",
    )


class AllInclusiveTripOptions(TranslationOptions):
    fields = ("location_description", "accommodation_description")


class RestaurantOptions(TranslationOptions):
    fields = ("rooms_description",)


class SkiingAreaOptions(TranslationOptions):
    fields = (
        "linked_domain_description",
        "free_ski_pass_conditions",
        "ski_pass_identifier",
        "children_validity_conditions",
        "senior_validity_conditions",
    )


class TastingOptions(TranslationOptions):
    fields = ("quality_charter_description", "aoc_description")


class DescriptionOptions(TranslationOptions):
    fields = ("text",)


translator.register(CommunicationInfo, CommunicationInfoOptions)
translator.register(Contact, ContactOptions)
translator.register(OpeningPeriod, OpeningPeriodOptions)
translator.register(PriceDescription, PriceDescriptionOptions)
translator.register(Multimedia, MultimediaOptions)
translator.register(BookingOrganisation, BookingOrganisationOptions)
translator.register(MeetingRoom, MeetingRoomOptions)
translator.register(Description, DescriptionOptions)

# Polymorphic classes
translator.register(BaseElement, BaseElementTranslationOptions)
translator.register(TouristicObject, TouristicObjectOptions)
translator.register(Area, AreaOptions)
translator.register(AllInclusiveTrip, AllInclusiveTripOptions)
translator.register(Restaurant, RestaurantOptions)
translator.register(SkiingArea, SkiingAreaOptions)
translator.register(Tasting, TastingOptions)

# As model API changed in django 1.8 modeltranslation fails with polymorphic models
# In KAPT_APIDAE v4 polymorphic elements will be removed including this monkey patch
translator.register(Structure, TranslationOptions)
translator.register(NaturalHeritage, TranslationOptions)
translator.register(CulturalHeritage, TranslationOptions)
translator.register(OutDoorHotelAccommodation, TranslationOptions)
translator.register(HotelAccommodation, TranslationOptions)
translator.register(RentalAccommodation, TranslationOptions)
translator.register(GroupAccommodation, TranslationOptions)
translator.register(CelebrationAndManifestation, TranslationOptions)
translator.register(Equipment, TranslationOptions)
translator.register(BusinessAndService, TranslationOptions)
translator.register(Activity, TranslationOptions)

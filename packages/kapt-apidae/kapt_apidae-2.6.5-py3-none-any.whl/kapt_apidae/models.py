# Third party
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices
from polymorphic.models import PolymorphicModel

# Local application / specific library imports
from .models_methods import (
    ActivityMethods,
    AllInclusiveTripMethods,
    AreaMethods,
    BaseElementMethods,
    BookingOrganisationMethods,
    BusinessAndServiceMethods,
    CelebrationAndManifestationMethods,
    CommunicationInfoMethods,
    ContactMethods,
    CulturalHeritageMethods,
    EquipmentMethods,
    GroupAccommodationMethods,
    HotelAccommodationMethods,
    MeetingRoomMethods,
    MultimediaFileMethods,
    MultimediaMethods,
    NaturalHeritageMethods,
    OpeningPeriodMethods,
    OutDoorHotelAccommodationMethods,
    PriceDescriptionMethods,
    PricingPeriodMethods,
    RentalAccommodationMethods,
    RestaurantMethods,
    RoomLayoutMethods,
    SelectionMethods,
    SkiingAreaMethods,
    StructureMethods,
    TastingMethods,
    TouristicObjectMethods,
    TouristicObjectOwnerMethods,
)
from kapt_apidae.core.db.choices import choices_factory


# TYPES
MULTIMEDIA_TYPE_CHOICES = Choices(
    ("IMAGE", _("Picture")),
    ("DOCUMENT", _("Document")),
    ("SON", _("Sound")),
    ("VIDEO", _("Video")),
    ("PLAN", _("Plan")),
    ("LOGO", _("Logo")),
    ("WEBCAM", _("Webcam")),
    ("VISITE_VIRTUELLE", _("Virtual tour")),
    ("BROCHURE_VIRTUELLE", _("Virtual booklet")),
    ("BON_PLAN", _("Good deal")),
    ("CHAINE_YOUTUBE", _("Youtube channel")),
    ("CHAINE_DAILYMOTION", _("Dailymotion channel")),
    ("GALERIE_FLICKR", _("Flickr gallery")),
    ("WEBCAM_360", _("360 webcam")),
    ("APPLICATION_IPHONE", _("iPhone application")),
    ("APPLICATION_IPAD", _("iPad application")),
    ("APPLICATION_ANDROID", _("Android application")),
    ("APPLICATION_ANDROID_TABLETTE", _("Android tablet application")),
)


AGE_UNIT_CHOICES = Choices(("MOIS", _("Months")), ("ANNEE", _("Years")))
ANIMAL_FRIENDLY = Choices(
    ("ACCEPTES", _("Accepted")),
    ("NON_ACCEPTES", _("Not accepted")),
    ("NON_DISPONIBLE", _("Unavailable")),
)

ANIMAL_FRIENDLY_EXTRA = Choices(
    ("NON_DISPONIBLE", _("Unavailable")),
    ("AVEC_SUPPLEMENT", _("With extra fees")),
    ("SANS_SUPPLEMENT", _("Without extra fees")),
)


OPENING_PERIOD_TYPE_CHOICES = Choices(
    (
        "OUVERTURE_SAUF",
        _(
            "Opened everyday on this period except on the days specified on DailyOpening"
        ),
    ),
    ("OUVERTURE_TOUS_LES_JOURS", _("Opened everyday on this period")),
    ("OUVERTURE_SEMAINE", _("Opened everyday specified on DailyOpening")),
    ("OUVERTURE_MOIS", _("Opened everyday specified on MonthlyOpening")),
)

OPENING_PERIOD_DAY_CHOICES = Choices(
    ("LUNDI", _("Monday")),
    ("MARDI", _("Tuesday")),
    ("MERCREDI", _("Wednesday")),
    ("JEUDI", _("Thursday")),
    ("VENDREDI", _("Friday")),
    ("SAMEDI", _("Saturday")),
    ("DIMANCHE", _("Sunday")),
    ("TOUS", _("Everyday")),
)

OPENING_PERIOD_DAYNUMBER_CHOICES = Choices(
    ("D_1ER", _("First")),
    ("D_2EME", _("Second")),
    ("D_3EME", _("Third")),
    ("D_4EME", _("Fourth")),
    ("D_DERNIER", _("Last")),
)

OPENING_PERIOD_MONTHDAY_ARRAY = []
for day in OPENING_PERIOD_DAY_CHOICES:
    if day[0] != "TOUS":
        for daynumber in OPENING_PERIOD_DAYNUMBER_CHOICES:
            OPENING_PERIOD_MONTHDAY_ARRAY.append(
                (
                    "{}_{}".format(daynumber[0], day[0]),
                    "{} {}".format(str(daynumber[1]), str(day[1])),
                )
            )

OPENING_PERIOD_MONTHDAY_CHOICES = Choices(*tuple(OPENING_PERIOD_MONTHDAY_ARRAY))


CLOSURE_SPECIAL_DATE = Choices(
    ("PREMIER_JANVIER", _("First of January")),
    ("PREMIER_MAI", _("First of May")),
    ("HUIT_MAI", _("Height of May")),
    ("QUATORZE_JUILLET", _("Fourteen of July")),
    ("QUINZE_AOUT", _("Fifteen of August")),
    ("PREMIER_NOVEMBRE", _("First of November")),
    ("ONZE_NOVEMBRE", _("Eleven of November")),
    ("VINGT_CINQ_DECEMBRE", _("Twenty-five of December")),
    ("BERCHTOLDSTAG", _("Berchtoldstag")),
    ("SAINT_JOSEPH", _("Saint joseph")),
    ("VENDREDI_SAINT", _("Vendredi saint")),
    ("LUNDI_PAQUES", _("Lundi paques")),
    ("ASCENSION", _("Ascension")),
    ("LUNDI_PENTECOTE", _("Lundi pentecote")),
    ("FETE_DIEU", _("Fete die")),
    ("LUNDI_DU_JEUNE_FEDERAL", _("Lundi du jeune federal")),
    ("IMMACULEE_CONCEPTION", _("Immaculee conception")),
)


TOURISTIC_OBJECTS_CORRESPONDENCE = {
    "ACTIVITE": "Activity",  # LeisureActivity
    "COMMERCE_ET_SERVICE": "BusinessAndService",  # PointOfInterestActivity
    "DEGUSTATION": "Tasting",  # PointOfInterestActivity
    "DOMAINE_SKIABLE": "SkiingArea",  # NO
    "EQUIPEMENT": "Equipment",  # PointOfInterestActivity
    "FETE_ET_MANIFESTATION": "CelebrationAndManifestation",  # EventActivity ??
    "HEBERGEMENT_COLLECTIF": "GroupAccommodation",  # AccommodationActivity
    "HEBERGEMENT_LOCATIF": "RentalAccommodation",  # AccommodationActivity
    "HOTELLERIE": "HotelAccommodation",  # AccommodationActivity
    "HOTELLERIE_PLEIN_AIR": "OutDoorHotelAccommodation",  # AccommodationActivity
    "PATRIMOINE_CULTUREL": "CulturalHeritage",  # PointOfInterestActivity > CulturalHeritageActivity
    "PATRIMOINE_NATUREL": "NaturalHeritage",  # PointOfInterestActivity > NaturalHeritageActivity
    "RESTAURATION": "Restaurant",  # MealActivity
    "SEJOUR_PACKAGE": "AllInclusiveTrip",  # NO
    "STRUCTURE": "Structure",  # NO
    "TERRITOIRE": "Area",  # NO
}

PUBLICATION_STATES_CHOICES = Choices(
    ("PUBLISHED", _("Published")), ("HIDDEN", _("Hidden")), ("DELETED", _("Deleted"))
)


OPEN_ALL_YEAR_CHOICES = Choices(("OUVERT_TOUTE_L_ANNEE", _("Open all year")))

TEMPORARILY_CLOSED_CHOICES = Choices(("FERME_TEMPORAIREMENT", _("Temporarily closed")))

ITINERARY_TYPE_CHOICES = Choices(
    ("ALLER_ITINERANCE", _("One way")),
    ("ALLER_RETOUR", _("Round-trip")),
    ("BOUCLE", _("Loop")),
)


class ImportApidaeKaptravelLog(models.Model):
    launch_date = models.DateTimeField(auto_now_add=True, verbose_name=_("Created on"))
    objects_modified = models.PositiveSmallIntegerField(
        verbose_name=_("Number of touristic objects modified"), default=0
    )
    objects_added = models.PositiveSmallIntegerField(
        verbose_name=_("Number of touristic objects added"), default=0
    )
    errors = models.PositiveSmallIntegerField(
        verbose_name=_("Number of errors"), default=0
    )
    end_date = models.DateTimeField(verbose_name=_("Ends on"), null=True, blank=True)
    duration = models.PositiveIntegerField(
        verbose_name=_("Duration (seconds)"), null=True, blank=True
    )
    launch_options = models.CharField(
        verbose_name=_("Command launch options"), max_length=2000, null=True, blank=True
    )
    coherence_test_passed = models.BooleanField(
        verbose_name=_("Coherence test passed"), default=False
    )

    def __str__(self):
        return "{} - {}".format(self.id, self.launch_date)

    class Meta:
        verbose_name = _("Import apidae to kaptravel log")
        verbose_name_plural = _("Import apidae to kaptravel logs")


# NOTE: You can test this with curl curl --data "projetId=9" http://intranet.ot-valence-showcase.kapt.mobi/apidae/settings/

# This settings is: pushed from apidae-dev, filled by kapt_apidae import script.
# It gives an information about kapt_apidae import state, based on differential cycles of apidae exports.
# import_apidae and import_apidae_kaptravel must have different differential cycles: we import all non-imported
# exports from apidae in kapt_apidae, and then, all expired data in kapt_catalog from kapt_apidae.
# It allow to have one call to import_apidae (that imports all new ImportsApidaeSettings ) and then one call on import_apidae_kaptravel


class ImportsApidaeSettings(models.Model):
    SETTINGS_CHOICES = Choices(
        ("SUCCESS", _("Export Apidae generated")),
        ("ERROR", _("Export Apidae failed")),
        ("DOWNLOAD_ERROR", _("Downloading Error")),
        ("EXTRACTION_ERROR", _("Extraction Error")),
        ("IMPORT_ERROR", _("Import Error")),
        ("NOTIFICATION_ERROR", _("Apidae notification Error")),
        ("TERMINATED", _("Export integrated")),
    )

    projetId = models.IntegerField(verbose_name=_("APIDAE website identifier"))
    statut = models.CharField(
        verbose_name=_("Export statut"), choices=SETTINGS_CHOICES, max_length=500
    )
    ponctuel = models.BooleanField(verbose_name=_("Ponctuel"), default=False)
    reinitialisation = models.BooleanField(
        verbose_name=_("Reinitialisation"), default=False
    )
    urlRecuperation = models.CharField(
        verbose_name=_("URL de récupération de l'export"),
        max_length=2000,
        null=True,
        blank=True,
    )
    urlConfirmation = models.CharField(
        verbose_name=_("URL de confirmation de prise en compte"),
        max_length=2000,
        null=True,
        blank=True,
    )
    file_downloaded = models.BooleanField(
        verbose_name=_("File has been downloaded"), default=False
    )
    file_extracted = models.BooleanField(
        verbose_name=_("File has been extracted"), default=False
    )
    import_launched = models.BooleanField(
        verbose_name=_("Import has been launched"), default=False
    )
    import_complete = models.BooleanField(
        verbose_name=_("Import has been completed"), default=False
    )
    created_on = models.DateTimeField(auto_now_add=True, verbose_name=_("Created on"))
    modified_on = models.DateTimeField(auto_now=True, verbose_name=_("Modified on"))

    def __str__(self):
        return "{} - {}".format(self.projetId, self.created_on)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class BaseElementType(models.Model):
    label = models.CharField(
        verbose_name=_("Label"), max_length=500, blank=False, unique=True, db_index=True
    )

    def __str__(self):
        return "%s" % (self.label)

    class Meta:
        verbose_name = _("Base element type")
        verbose_name_plural = _("Base element types")


class BaseElement(models.Model, BaseElementMethods):
    type = models.ForeignKey(
        BaseElementType, verbose_name=_("Type"), on_delete=models.CASCADE
    )
    label = models.CharField(verbose_name=_("Label"), max_length=500, blank=False)
    description = models.TextField(verbose_name=_("Description"), null=True, blank=True)
    order = models.IntegerField(verbose_name=_("Ordering number"), blank=False)
    active = models.BooleanField(verbose_name=_("Active"), default=True)

    family = models.ForeignKey(
        "self",
        verbose_name=_("Element family"),
        blank=True,
        null=True,
        related_name="family_set",
        on_delete=models.CASCADE,
    )
    parent = models.ForeignKey(
        "self",
        verbose_name=_("Element family"),
        blank=True,
        null=True,
        related_name="children_set",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return "%s" % (self.label)

    class Meta:
        verbose_name = _("Base element")
        verbose_name_plural = _("Base elements")


# LOCALITIES


class Locality(models.Model):
    name = models.CharField(_("Name"), max_length=200)
    code = models.CharField(_("code"), max_length=500, db_index=True)
    zip_code = models.CharField(_("Zip code"), max_length=500, db_index=True)
    country = models.ForeignKey(
        BaseElement, verbose_name=_("Country"), on_delete=models.CASCADE
    )

    def __str__(self):
        return "{} - {}".format(self.id, self.name)

    class Meta:
        verbose_name = _("Locality")
        verbose_name_plural = _("Localities")


# VARIABLE ATTRIBUTES


class VariableAttribute(models.Model):
    """critereInterne"""

    label = models.CharField(verbose_name=_("Label"), max_length=500, blank=False)
    description = models.TextField(verbose_name=_("Description"), null=True, blank=True)

    def __str__(self):
        return "%s" % (self.label)

    class Meta:
        verbose_name = _("Variable attribute")
        verbose_name_plural = _("Variable attributes")


# SELECTIONS


class Selection(models.Model, SelectionMethods):
    """Selection"""

    label = models.CharField(verbose_name=_("Label"), max_length=500, blank=False)
    touristic_objects = models.ManyToManyField(
        "TouristicObject", verbose_name=_("Touristic objects"), blank=True
    )

    def __str__(self):
        return "%s" % (self.label)

    class Meta:
        verbose_name = _("Selection")
        verbose_name_plural = _("Selections")


# TOURISTIC OBJECTS


class TouristicObjectOwner(models.Model, TouristicObjectOwnerMethods):
    type = models.ForeignKey(
        BaseElement, verbose_name=_("Owner type"), on_delete=models.CASCADE
    )
    name = models.CharField(
        verbose_name=_("Name"), max_length=500, blank=False, null=True
    )
    department = models.CharField(
        verbose_name=_("Department"), max_length=500, blank=True, null=True
    )
    created_on = models.DateTimeField(
        verbose_name=_("Creation date"), blank=True, null=True
    )
    last_update = models.DateTimeField(
        verbose_name=_("Last update"), blank=True, null=True
    )

    def __str__(self):
        return "{} - {}".format(self.type, self.name)

    class Meta:
        verbose_name = _("Object owner")
        verbose_name_plural = _("Object owners")


class CommunicationInfo(models.Model, CommunicationInfoMethods):
    type = models.ForeignKey(
        BaseElement, verbose_name=_("Communication type"), on_delete=models.CASCADE
    )
    value = models.CharField(
        verbose_name=_("Label"), max_length=2048, blank=False, null=True
    )
    description = models.TextField(verbose_name=_("Description"), null=True, blank=True)

    def __str__(self):
        return "{} - {}".format(self.type, self.value)

    class Meta:
        verbose_name = _("Communication info")
        verbose_name_plural = _("Communication infos")


class Contact(models.Model, ContactMethods):
    title = models.ForeignKey(
        BaseElement,
        verbose_name=_("Title"),
        blank=False,
        null=True,
        related_name="title_contact_object_set",
        on_delete=models.CASCADE,
    )
    first_name = models.CharField(
        verbose_name=_("First name"), max_length=500, blank=False, null=True
    )
    last_name = models.CharField(
        verbose_name=_("Last name"), max_length=500, blank=False, null=True
    )
    position = models.CharField(
        verbose_name=_("Position"), max_length=500, blank=False, null=True
    )  # titre
    function = models.ForeignKey(
        BaseElement,
        verbose_name=_("Function"),
        blank=False,
        null=True,
        related_name="function_contact_object_set",
        on_delete=models.CASCADE,
    )
    is_referent = models.BooleanField(
        verbose_name=_("This contact is the referent"), default=False, db_index=True
    )
    internal_communications = models.ManyToManyField(
        CommunicationInfo,
        verbose_name=_("Internal communication"),
        blank=True,
        related_name="internal_communication_contact_object_set",
    )

    def __str__(self):
        return "{} - {}".format(self.first_name, self.last_name)

    def delete(self, using=None):
        self.internal_communications.all().delete()
        super().delete()

    class Meta:
        verbose_name = _("Contact")
        verbose_name_plural = _("Contacts")


class DayOpeningChoices(models.Model):
    day = models.CharField(
        verbose_name=_("Opening days"),
        max_length=500,
        choices=OPENING_PERIOD_DAY_CHOICES,
    )

    def __str__(self):
        return "%s" % (self.day)


class MonthDayOpeningChoices(models.Model):
    monthday = models.CharField(
        verbose_name=_("Opening days"),
        max_length=500,
        choices=OPENING_PERIOD_MONTHDAY_CHOICES,
    )

    def __str__(self):
        return "%s" % (self.monthday)


class ExceptionalOpeningDate(models.Model):
    date = models.DateField(verbose_name=_("Exceptional opening date"))

    def __str__(self):
        return "%s" % (self.date)


class OpeningPeriod(models.Model, OpeningPeriodMethods):
    beginning = models.DateField(verbose_name=_("Beginning date"))  # dateDebut
    ending = models.DateField(verbose_name=_("Ending date"))  # dateFin
    label = models.CharField(
        verbose_name=_("Label"), max_length=500, blank=False, null=True
    )  # nom
    further_hourly_informations = models.TextField(
        verbose_name=_("Further hourly informations"), blank=True, null=True
    )  # complementHoraire
    opening_time = models.TimeField(
        verbose_name=_("Opening time"), blank=True, null=True
    )
    closing_time = models.TimeField(
        verbose_name=_("Closing time"), blank=True, null=True
    )
    type = models.CharField(
        verbose_name=_("Period type"),
        max_length=500,
        choices=OPENING_PERIOD_TYPE_CHOICES,
    )
    every_years = models.BooleanField(
        verbose_name=_("Period is repeated every years"), default=False
    )
    daily_opening = models.ManyToManyField(
        DayOpeningChoices, verbose_name=_("Daily opening days"), blank=True
    )  # ouverturesJournalieres
    monthly_opening = models.ManyToManyField(
        MonthDayOpeningChoices, verbose_name=_("Monthly opening days"), blank=True
    )  # ouverturesJourDuMois
    exceptional_opening = models.ManyToManyField(
        ExceptionalOpeningDate, verbose_name=_("Exceptional opening days"), blank=True
    )  # ouverturesExceptionnelles

    def __str__(self):
        return "{} - {}".format(self.beginning, self.ending)

    def delete(self):
        self.daily_opening.clear()
        self.monthly_opening.clear()
        self.exceptional_opening.all().delete()
        super().delete()


class ClosurePeriod(models.Model):
    closure_date = models.DateField(
        verbose_name=_("Exceptional opening days"), blank=True, null=True
    )
    closure_special_date = models.CharField(
        verbose_name=_("Special closure date"),
        max_length=500,
        choices=CLOSURE_SPECIAL_DATE,
        blank=True,
        null=True,
    )

    def __str__(self):
        return "{} - {}".format(self.closure_date, self.closure_special_date)


class PriceDescription(models.Model, PriceDescriptionMethods):
    type = models.ForeignKey(
        BaseElement, verbose_name=_("Price type"), on_delete=models.CASCADE
    )  # type - objets_lies_modifies-132058.json
    minimum_price = models.FloatField(
        verbose_name=_("Minimum price"), blank=True, null=True
    )  # minimum - objets_lies_modifies-132058.json
    maximum_price = models.FloatField(
        verbose_name=_("Maximum price"), blank=True, null=True
    )  # maximum - objets_lies_modifies-132058.json
    additionnal_description = models.TextField(
        verbose_name=_("Additional description"), blank=True, null=True
    )  # precisionTarif - objets_lies_modifies-132058.json

    def __str__(self):
        return "{} - {}".format(self.minimum_price, self.maximum_price)


class PricingPeriod(models.Model, PricingPeriodMethods):  # periodeTarif
    beginning = models.DateField(verbose_name=_("Beginning date"))  # dateDebut
    ending = models.DateField(verbose_name=_("Ending date"))  # dateFin
    prices_description = models.ManyToManyField(
        PriceDescription,
        verbose_name=_("Prices description"),
        blank=True,
        related_name="pricing_periods",
    )  # tarifs

    def __str__(self):
        return "{} - {}".format(self.beginning, self.ending)

    def delete(self):
        self.prices_description.all().delete()
        super().delete()


class BookingOrganisation(models.Model, BookingOrganisationMethods):
    referent_structure = models.ForeignKey(
        "TouristicObject",
        verbose_name=_("Referent structure"),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        verbose_name=_("Name"), max_length=500, blank=True, null=True
    )
    type = models.ForeignKey(
        BaseElement, verbose_name=_("Type"), on_delete=models.CASCADE
    )
    description = models.TextField(verbose_name=_("Description"), null=True, blank=True)

    # Informations
    internal_communications = models.ManyToManyField(
        CommunicationInfo,
        verbose_name=_("Internal communication"),
        blank=True,
        related_name="internal_communication_booking_organisation_set",
    )
    external_communications = models.ManyToManyField(
        CommunicationInfo,
        verbose_name=_("External communication"),
        blank=True,
        related_name="external_communication_booking_organisation_set",
    )

    def __str__(self):
        return "%s" % (self.name)

    class Meta:
        verbose_name = _("Booking organisation")
        verbose_name_plural = _("Booking organisations")

    def delete(self, using=None):
        self.internal_communications.all().delete()
        self.external_communications.all().delete()
        super().delete()


class MultimediaFile(models.Model, MultimediaFileMethods):
    locale = models.CharField(
        verbose_name=_("Language"),
        max_length=500,
        choices=choices_factory(settings.LANGUAGES),
    )
    url = models.URLField(verbose_name=_("Url"), max_length=2048, blank=True, null=True)
    list_url = models.URLField(
        verbose_name=_("Url for list display"), max_length=2048, blank=True, null=True
    )
    details_url = models.URLField(
        verbose_name=_("Url for details display"),
        max_length=2048,
        blank=True,
        null=True,
    )
    slideshow_url = models.URLField(
        verbose_name=_("Url for slide show display"),
        max_length=2048,
        blank=True,
        null=True,
    )
    extension = models.CharField(
        verbose_name=_("Extension"), max_length=500, blank=True, null=True
    )
    file_name = models.CharField(
        verbose_name=_("File name"), max_length=500, blank=True, null=True
    )
    size = models.IntegerField(verbose_name=_("File size"), blank=True, null=True)
    height = models.IntegerField(verbose_name=_("Hauteur"), blank=True, null=True)
    width = models.IntegerField(verbose_name=_("Largeur"), blank=True, null=True)
    modification_date = models.DateTimeField(verbose_name=_("Last modified on"))

    def __str__(self):
        return "%s" % (self.file_name)

    class Meta:
        verbose_name = _("Multimedia file")
        verbose_name_plural = _("Multimedia files")


class Multimedia(models.Model, MultimediaMethods):
    type = models.CharField(
        verbose_name=_("Type"), max_length=500, choices=MULTIMEDIA_TYPE_CHOICES
    )
    files = models.ManyToManyField(MultimediaFile, verbose_name=_("Multimedia files"))
    name = models.CharField(
        verbose_name=_("Name"), max_length=1000, blank=True, null=True
    )
    legend = models.CharField(
        verbose_name=_("Legend"), max_length=2000, blank=True, null=True
    )
    copyright = models.CharField(
        verbose_name=_("Copyright"), max_length=1000, blank=True, null=True
    )
    remark = models.CharField(
        verbose_name=_("Remark"), max_length=1000, blank=True, null=True
    )

    def __str__(self):
        return "{} - {}".format(self.get_type_display(), self.name)

    def delete(self):
        self.files.all().delete()
        super().delete()

    class Meta:
        verbose_name = _("Multimedia")
        verbose_name_plural = _("Multimedias")


class RoomLayout(models.Model, RoomLayoutMethods):
    capacity = models.PositiveSmallIntegerField(
        verbose_name=_("Capacity"), blank=True, null=True
    )  # capacite
    layout = models.ForeignKey(
        BaseElement,
        verbose_name=_("Room layout"),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )  # disposition

    def __str__(self):
        return "{} - {}".format(self.layout, self.capacity)


class MeetingRoom(models.Model, MeetingRoomMethods):
    name = models.CharField(
        verbose_name=_("Name"), max_length=500, blank=True, null=True
    )  # nom
    description = models.TextField(
        verbose_name=_("Description"), blank=True, null=True
    )  # description
    max_capacity = models.PositiveSmallIntegerField(
        verbose_name=_("Max capacity"), blank=True, null=True
    )  # capaciteMax
    surface_area = models.IntegerField(
        verbose_name=_("Surface area"), blank=True, null=True
    )  # superficie
    height = models.PositiveSmallIntegerField(
        verbose_name=_("Height"), blank=True, null=True
    )  # hauteur
    natural_lighting = models.BooleanField(
        verbose_name=_("Natural lighting"), default=False
    )  # lumiereNaturelle
    layouts = models.ManyToManyField(
        RoomLayout, verbose_name=_("Meeting rooms layouts"), blank=True
    )  # dispositions
    minimum_price = models.FloatField(
        verbose_name=_("Minimum price"), blank=True, null=True
    )  # tarifSalle
    maximum_price = models.FloatField(
        verbose_name=_("Maximum price"), blank=True, null=True
    )  # tarifSalle
    day_minimum_price = models.FloatField(
        verbose_name=_("Day minimum price"), blank=True, null=True
    )  # tarifJournee
    day_maximum_price = models.FloatField(
        verbose_name=_("Day maximum price"), blank=True, null=True
    )  # tarifJournee
    resident_minimum_price = models.FloatField(
        verbose_name=_("Resident minimum price"), blank=True, null=True
    )  # tarifResident
    resident_maximum_price = models.FloatField(
        verbose_name=_("Resident maximum price"), blank=True, null=True
    )  # tarifResident

    def __str__(self):
        return "%s" % (self.name)

    def delete(self):
        self.layouts.all().delete()
        super().delete()


# TODO: May add a boolean to indicate if the touristical object was selected in the import of if its a secondary object


class TouristicObject(PolymorphicModel, TouristicObjectMethods):
    """
    ACTIVITE,
    COMMERCE_ET_SERVICE,
    DEGUSTATION,
    DOMAINE_SKIABLE,
    EQUIPEMENT,
    FETE_ET_MANIFESTATION,
    HEBERGEMENT_COLLECTIF,
    HEBERGEMENT_LOCATIF,
    HOTELLERIE,
    HOTELLERIE_PLEIN_AIR,
    PATRIMOINE_CULTUREL,
    PATRIMOINE_NATUREL,
    RESTAURATION,
    SEJOUR_PACKAGE,
    STRUCTURE,
    TERRITOIRE
    """

    # identifier = models.IntegerField(verbose_name=_("Identifier"), primary_key=True)
    ASPECT_CHOICES = Choices(
        (1, "hiver", _("HIVER")),
        (2, "ete", _("ETE")),
        (3, "handicap", _("HANDICAP")),
        (4, "tourisme_affaires", _("TOURISME_AFFAIRES")),
        (5, "groupes", _("GROUPES")),
        (6, "prestataire_activites", _("PRESTATAIRE_ACTIVITES")),
    )

    aspect = models.PositiveSmallIntegerField(
        verbose_name=_("Aspect"),
        choices=ASPECT_CHOICES,
        blank=True,
        null=True,
        db_index=True,
    )
    apidae_identifier = models.IntegerField(verbose_name=_("Apidae Identifier"))
    label = models.CharField(verbose_name=_("Label"), max_length=500, blank=False)
    publication_state = models.CharField(
        verbose_name=_("Publication state"),
        max_length=500,
        choices=PUBLICATION_STATES_CHOICES,
        blank=True,
        null=True,
    )

    is_linked_object = models.BooleanField(
        verbose_name=_("Is a linked object"), default=False
    )

    # Management
    created_on = models.DateTimeField(
        verbose_name=_("Creation date"), blank=True, null=True
    )
    last_update = models.DateTimeField(
        verbose_name=_("Last update"), blank=True, null=True
    )
    owner = models.ForeignKey(
        TouristicObjectOwner,
        verbose_name=_("Object owner"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    # Informations
    internal_communications = models.ManyToManyField(
        CommunicationInfo,
        verbose_name=_("Internal communication"),
        blank=True,
        related_name="internal_communication_objects_set",
    )
    external_communications = models.ManyToManyField(
        CommunicationInfo,
        verbose_name=_("External communication"),
        blank=True,
        related_name="external_communication_objects_set",
    )

    # Legal mentions
    siret = models.CharField(
        verbose_name=_("SIRET"), max_length=500, blank=True, null=True
    )
    ape_naf = models.CharField(
        verbose_name=_("APE or NAF code"), max_length=500, blank=True, null=True
    )
    rcs = models.CharField(
        verbose_name=_("RCS code"), max_length=500, blank=True, null=True
    )
    license_authorization_number = models.CharField(
        verbose_name=_("License authorization number"),
        max_length=500,
        blank=True,
        null=True,
    )

    # Management
    management_type = models.ForeignKey(
        BaseElement,
        verbose_name=_("Management type"),
        blank=True,
        null=True,
        related_name="management_type_set",
        on_delete=models.SET_NULL,
    )  # modeGestion
    management_organisation = models.ForeignKey(
        "self",
        verbose_name=_("Management organisation"),
        blank=True,
        null=True,
        related_name="managed_objects_set",
        on_delete=models.SET_NULL,
    )  # structureGestion
    information_organisation = models.ForeignKey(
        "self",
        verbose_name=_("Information organisation"),
        blank=True,
        null=True,
        related_name="informed_objects_set",
        on_delete=models.SET_NULL,
    )  # structureInformation

    # Presentation
    short_description = models.TextField(
        verbose_name=_("Short description"), blank=True, null=True
    )
    description = models.TextField(verbose_name=_("Description"), blank=True, null=True)
    good_deal = models.TextField(verbose_name=_("Good deal"), blank=True, null=True)
    offers_labels = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Offers labels"),
        blank=True,
        related_name="offers_labels_set",
    )  # typologiesPromo

    # Localization
    address_1 = models.CharField(
        verbose_name=_("Address"), max_length=500, blank=True, null=True
    )
    address_2 = models.CharField(
        verbose_name=_("Address (second line)"), max_length=500, blank=True, null=True
    )
    address_3 = models.CharField(
        verbose_name=_("Address (third line)"), max_length=500, blank=True, null=True
    )
    zip_code = models.CharField(
        _("Zip code"), max_length=500, db_index=True, blank=True, null=True
    )
    distribution_office = models.CharField(
        _("Distribution office"), max_length=500, blank=True, null=True
    )
    cedex = models.CharField(_("Cedex"), max_length=500, blank=True, null=True)
    state = models.CharField(_("State"), max_length=500, blank=True, null=True)
    locality = models.ForeignKey(
        Locality,
        verbose_name=_("Locality"),
        blank=True,
        null=True,
        related_name="locality_objects_set",
        on_delete=models.SET_NULL,
    )
    landmark = models.CharField(
        _("Landmark"), max_length=500, blank=True, null=True
    )  # ReperePlan
    place = models.PositiveIntegerField(
        verbose_name=_("Place"), null=True, blank=True
    )  # Lieu id
    place_name = models.CharField(
        verbose_name=_("Place name"), max_length=500, blank=True, null=True
    )  # nomLieu
    altitude = models.IntegerField(
        verbose_name=_("Altitude"), null=True, blank=True, db_index=True
    )
    max_altitude = models.IntegerField(
        verbose_name=_("Maximum altitude"), null=True, blank=True, db_index=True
    )
    min_altitude = models.IntegerField(
        verbose_name=_("Minimum altitude"), null=True, blank=True, db_index=True
    )
    max_altitude_accommodation = models.IntegerField(
        verbose_name=_("Maximum altitude for the accommodation"),
        null=True,
        blank=True,
        db_index=True,
    )
    min_altitude_accommodation = models.IntegerField(
        verbose_name=_("Minimum altitude for the accommodation"),
        null=True,
        blank=True,
        db_index=True,
    )
    access_means = models.TextField(
        verbose_name=_("Access means"), blank=True, null=True
    )  # Complement
    latitude = models.DecimalField(
        verbose_name=_("Latitude"),
        max_digits=27,
        decimal_places=25,
        db_index=True,
        blank=True,
        null=True,
    )  # geoJson
    longitude = models.DecimalField(
        verbose_name=_("Longitude"),
        max_digits=27,
        decimal_places=24,
        db_index=True,
        blank=True,
        null=True,
    )  # geoJson

    # Surroundings description
    geographical_perimeter = models.ManyToManyField(
        Locality,
        verbose_name=_("Localities in the geographical area of the object"),
        blank=True,
        related_name="geographical_perimeter_objects_set",
    )
    environment = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Environment of the object"),
        blank=True,
        related_name="environment_set",
    )

    linked_objects = models.ManyToManyField(
        "self",
        verbose_name=_("Linked related objects"),
        blank=True,
        related_name="linked_objects_set",
        through="LinkType",
        symmetrical=False,
    )  # objetsLies
    links_description = models.TextField(
        verbose_name=_("Links description"), blank=True, null=True
    )

    # Services
    equipments = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Equipments"),
        blank=True,
        related_name="equipment_objects_set",
    )
    services = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Services"),
        blank=True,
        related_name="service_objects_set",
    )
    activities = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Activities"),
        blank=True,
        related_name="activity_objects_set",
    )

    # Comfort
    comfort_services = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Comfort services"),
        blank=True,
        related_name="comfort_services_objects_set",
    )  # conforts

    spoken_languages = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Spoken languages"),
        blank=True,
        related_name="spoken_languages_objects_set",
    )
    documentation_languages = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Documentation languages"),
        blank=True,
        related_name="documentation_languages_objects_set",
    )

    further_welcoming_informations = models.TextField(
        verbose_name=_("Further welcoming informations"), blank=True, null=True
    )  # complementAccueil

    # Accessibility
    accessibility_informations = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Accessibility informations"),
        blank=True,
        related_name="accessibility_objects_set",
    )  # tourismesAdaptes
    accessibility_labels = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Accessibility labels"),
        blank=True,
        related_name="accessibility_labels_objects_set",
    )  # labelsTourismeHandicap

    # Customer type
    customers_type = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Customer type"),
        blank=True,
        related_name="customers_type_objects_set",
    )  # typesClientele - objets_lies_modifies-132058.json:136
    group_min_size = models.PositiveSmallIntegerField(
        verbose_name=_("Group minimum size"), blank=True, null=True
    )  # tailleGroupeMin
    group_max_size = models.PositiveSmallIntegerField(
        verbose_name=_("Group maximum size"), blank=True, null=True
    )  # tailleGroupeMax
    minimum_age = models.PositiveSmallIntegerField(
        verbose_name=_("Minimum age"), blank=True, null=True
    )  # ageMin
    maximum_age = models.PositiveSmallIntegerField(
        verbose_name=_("Maximum age"), blank=True, null=True
    )  # ageMax
    minimum_age_unit = models.CharField(
        verbose_name=_("Minimum age unit"),
        max_length=500,
        choices=AGE_UNIT_CHOICES,
        blank=True,
        null=True,
    )  # uniteAgeMin objets_lies_modifies-132058.json:136
    maximum_age_unit = models.CharField(
        verbose_name=_("Maximum age unit"),
        max_length=500,
        choices=AGE_UNIT_CHOICES,
        blank=True,
        null=True,
    )  # uniteAgeMax objets_lies_modifies-132058.json:136

    # Animal friendly
    animal_friendly = models.CharField(
        verbose_name=_("Animal friendly"),
        max_length=500,
        choices=ANIMAL_FRIENDLY,
        blank=True,
        null=True,
    )  # animauxAcceptes
    animal_friendly_further_informations = models.CharField(
        verbose_name=_("Animal friendly further informations"),
        max_length=500,
        choices=ANIMAL_FRIENDLY_EXTRA,
        blank=True,
        null=True,
    )  # animauxAcceptesSupplement
    animal_friendly_description = models.TextField(
        verbose_name=_("Animal friendly textual description"), blank=True, null=True
    )  # descriptifAnimauxAcceptes

    # Opening
    opening_textual_description = models.TextField(
        verbose_name=_("Opening textual description"), blank=True, null=True
    )  # periodeEnClair
    open_all_year = models.CharField(
        verbose_name=_("Open all year"),
        max_length=500,
        choices=OPEN_ALL_YEAR_CHOICES,
        blank=True,
        null=True,
    )  # ouvertTouteLAnnee
    group_duration = models.IntegerField(
        verbose_name=_("Group duration"),
        blank=True,
        null=True,
    )  # dureeSeanceGroupe
    temporarily_closed = models.CharField(
        verbose_name=_("Temporarily closed"),
        max_length=500,
        choices=TEMPORARILY_CLOSED_CHOICES,
        blank=True,
        null=True,
    )  # fermeTemporairement
    opening_periods_description = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Opening periods description"),
        blank=True,
        related_name="opening_periods_description_objects_set",
    )  # indicationsPeriode
    additional_opening_periods_description = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Additional opening periods description"),
        blank=True,
        related_name="additional_opening_objects_set",
    )  # ouverturesComplementaires
    opening_periods = models.ManyToManyField(
        "OpeningPeriod", verbose_name=_("Opening periods"), blank=True
    )  # periodesOuvertures
    exceptional_closure_dates = models.ManyToManyField(
        "ClosurePeriod", verbose_name=_("Closure periods"), blank=True
    )

    # Pricing
    is_free = models.BooleanField(
        verbose_name=_("Is free"), default=True
    )  # gratuit - objets_lies_modifies-132058.json
    pricing_textual_description = models.TextField(
        verbose_name=_("Pricing textual description"), blank=True, null=True
    )  # tarifsEnClair - objets_lies_modifies-132058.json
    additional_pricing_description = models.TextField(
        verbose_name=_("Additional pricing description"), blank=True, null=True
    )  # complement - objets_lies_modifies-109664.json
    pricing_periods = models.ManyToManyField(
        PricingPeriod,
        verbose_name=_("Pricing periods"),
        blank=True,
        related_name="pricing_periods_objects_set",
    )  # periodes - objets_lies_modifies-109664.json
    payment_methods = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Payment methods"),
        blank=True,
        related_name="payment_methods_set",
    )  # modesPaiement - objets_lies_modifies-109664.json

    # Booking
    booking_organisations = models.ManyToManyField(
        BookingOrganisation, verbose_name=_("Booking organisations"), blank=True
    )
    additional_booking_informations = models.TextField(
        verbose_name=_("Additional booking informations"), blank=True, null=True
    )  # complement

    variable_attributes = models.ManyToManyField(
        VariableAttribute, verbose_name=_("Variable attributes"), blank=True
    )

    # Contacts
    internal_contacts = models.ManyToManyField(
        Contact,
        verbose_name=_("Internal contacts"),
        blank=True,
        related_name="internal_contact_objects_set",
    )
    external_contacts = models.ManyToManyField(
        Contact,
        verbose_name=_("External contacts"),
        blank=True,
        related_name="external_contact_objects_set",
    )

    # Multimedia
    # Pictures
    pictures = models.ManyToManyField(
        Multimedia,
        verbose_name=_("Pictures"),
        blank=True,
        related_name="picture_objects_set",
    )

    # Links
    links = models.ManyToManyField(
        Multimedia,
        verbose_name=_("HTTP links"),
        blank=True,
        related_name="httplink_objects_set",
    )

    # Business tourism
    business_tourism_provided = models.BooleanField(
        verbose_name=_("Business tourism provided"), default=False
    )  # tourismeAffairesEnabled
    business_tourism_rooms_equipped_for = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Business tourism rooms equipped for"),
        blank=True,
        related_name="business_tourism_rooms_equipped_for_objects_set",
    )  # sallesEquipeesPour
    business_tourism_rooms_equipments = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Business tourism rooms equipments"),
        blank=True,
        related_name="business_tourism_rooms_equipments_objects_set",
    )  # sallesEquipement
    catering_rooms = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Catering rooms"),
        blank=True,
        related_name="catering_rooms_objects_set",
    )  # sallesRestauration
    accommodation_rooms = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Accommodation rooms"),
        blank=True,
        related_name="accommodation_rooms_objects_set",
    )  # sallesHebergement
    meeting_rooms = models.ManyToManyField(
        MeetingRoom,
        verbose_name=_("Meeting rooms"),
        blank=True,
        related_name="meeting_rooms_objects_set",
    )  # sallesReunion
    equipped_meeting_rooms_quantity = models.SmallIntegerField(
        verbose_name=_("Equipped meeting rooms quantity"), null=True, blank=True
    )  # nombreSallesReunionEquipees
    business_tourism_max_capacity = models.IntegerField(
        verbose_name=_("Business tourism max capacity"), null=True, blank=True
    )  # capaciteMaxAccueil
    adjustable_rooms_quantity = models.IntegerField(
        verbose_name=_("Adjustable rooms quantity"), null=True, blank=True
    )  # nombreSallesModulables

    # Visits
    is_visitable = models.BooleanField(
        verbose_name=_("Is visitable ?"), default=False
    )  # visitable
    visit_languages = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Visit languages"),
        blank=True,
        related_name="visit_languages_objects_set",
    )  # languesVisite
    audio_guide_languages = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Audio-guide languages"),
        blank=True,
        related_name="audio_guide_languages_objects_set",
    )  # languesAudioGuide
    information_panels_languages = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Audio-guide languages"),
        blank=True,
        related_name="information_panels_languages_objects_set",
    )  # languesPanneauInformation
    group_visit_average_time = models.PositiveSmallIntegerField(
        verbose_name=_("Group visit average time"), blank=True, null=True
    )  # dureeMoyenneVisiteGroupe
    individual_visit_average_time = models.PositiveSmallIntegerField(
        verbose_name=_("Individual visit average time"), blank=True, null=True
    )  # dureeMoyenneVisiteIndividuelle
    individual_visit_services = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Individual visit services"),
        blank=True,
        related_name="individual_visit_services_objects_set",
    )  # prestationsVisitesIndividuelles
    group_visit_services = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Group visit services"),
        blank=True,
        related_name="group_visit_services_objects_set",
    )  # prestationsVisitesGroupees
    additional_visit_informations = models.TextField(
        verbose_name=_("Additional visit informations"), blank=True, null=True
    )  # complementVisite

    areas = models.ManyToManyField(
        "Area", verbose_name=_("Areas"), blank=True, related_name="area_objects_set"
    )

    # Import script datas
    last_import = models.DateTimeField(verbose_name=_("Last import in kapt_apidae"))

    # Prestations
    sports_activities = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Sports activities"),
        blank=True,
        related_name="sports_activities_set",
    )  # activitesSportives
    curtural_activities = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Cultural activities"),
        blank=True,
        related_name="cultural_activities_set",
    )  # activitesCulturelles

    # Meta data
    meta_data = models.TextField(verbose_name=_("Meta data"), null=True, blank=True)

    # Link to kapt-catalog Activity
    kapt_catalog_activity = models.ForeignKey(
        "kapt_catalog.Activity",
        verbose_name=_("kapt-catalog Activity"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="apidae_touristic_objects",
    )

    def __str__(self):
        return "%s" % self.label


class LinkType(models.Model):
    link_type = models.CharField(
        verbose_name=_("Link type"), max_length=500, blank=True, null=True
    )  # Type
    touristic_object = models.ForeignKey(
        TouristicObject, on_delete=models.CASCADE, related_name="touristic_object"
    )
    touristic_linked_object = models.ForeignKey(
        TouristicObject,
        on_delete=models.CASCADE,
        related_name="touristic_linked_object",
    )

    def __str__(self):
        return "{} - {}".format(self.link_type, self.touristic_object)


class Description(models.Model):
    touristic_object = models.ForeignKey(
        "TouristicObject",
        verbose_name=_("Touristic object"),
        related_name="descriptions",
        on_delete=models.CASCADE,
    )
    theme = models.ForeignKey(
        BaseElement,
        verbose_name=_("Theme"),
        related_name="theme_set",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    label = models.CharField(
        verbose_name=_("Technical name"), max_length=500, blank=True, null=True
    )
    text = models.TextField(verbose_name=_("Description"), blank=True, null=True)

    def __str__(self):
        return "%s" % (self.label)


class Area(TouristicObject, AreaMethods):
    type = models.ForeignKey(
        BaseElement,
        verbose_name=_("Type"),
        related_name="type_area_areas_set",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    is_destination = models.BooleanField(
        verbose_name=_("Is destination"), null=True, blank=True
    )
    shops_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Number of shops"), null=True, blank=True
    )
    restaurants_quantity = models.IntegerField(
        verbose_name=_("Number of restaurants"), null=True, blank=True
    )
    short_description_winter = models.TextField(
        verbose_name=_("Short description winter"), blank=True, null=True
    )
    description_winter = models.TextField(
        verbose_name=_("Description winter"), blank=True, null=True
    )
    labels = models.ManyToManyField(
        BaseElement, verbose_name=_("Labels"), related_name="labels_area_areas_set"
    )
    rankings = models.ManyToManyField(
        BaseElement, verbose_name=_("Rankings"), related_name="rankings_area_areas_set"
    )

    # Winter sports
    ski_resorts_types = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Ski resorts types"),
        blank=True,
        related_name="ski_resorts_types_areas_set",
    )  # typesStation
    snowshoes_trail_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Snowshoes trail quantity"), null=True, blank=True
    )  # nombreItinerairesRaquettes
    snowshoes_trail_kilometers = models.PositiveSmallIntegerField(
        verbose_name=_("Snowshoes trail kilometers"), null=True, blank=True
    )  # nombreKilometresItinerairesRaquettes
    pedestrian_route_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Pedestrian routes quantity"), null=True, blank=True
    )  # nombreItinerairesPietons
    pedestrian_route_kilometers = models.PositiveSmallIntegerField(
        verbose_name=_("Pedestrian routes kilometers"), null=True, blank=True
    )  # nombreKilometresItinerairesPietons
    minimum_age_ski_teaching = models.CharField(
        verbose_name=_("Minimum age for ski teaching"),
        max_length=500,
        null=True,
        blank=True,
    )  # ageMinimumEnseignementSki
    kindergarten_age_groups = models.CharField(
        verbose_name=_("Kindergarten age groups"), max_length=500, null=True, blank=True
    )  # trancheAgeAccueilEnfantGarderie

    linked_ski_resorts = models.ManyToManyField(
        TouristicObject,
        verbose_name=_("Linked ski resorts"),
        blank=True,
        related_name="linked_ski_resorts_areas_set",
    )  # domaines

    # Area accommodations
    camper_van_car_park = models.BooleanField(
        verbose_name=_("Camper van car park"), null=True, blank=True
    )
    campsite_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Campsite quantity"), null=True, blank=True
    )
    tourism_residences_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Tourism residences quantity"), null=True, blank=True
    )
    holiday_resorts_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Holiday resorts quantity"), null=True, blank=True
    )
    snow_caravans_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Snow caravans quantity"), null=True, blank=True
    )
    ranked_resting_places_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Ranked resting places quantity"), null=True, blank=True
    )
    non_classified_hotels_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Non-classified hotels quantity"), null=True, blank=True
    )
    no_stars_hotels_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("No stars hotels quantity"), null=True, blank=True
    )
    one_star_hotels_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("One star hotels quantity"), null=True, blank=True
    )
    two_star_hotels_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Two star hotels quantity"), null=True, blank=True
    )
    three_star_hotels_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Three star hotels quantity"), null=True, blank=True
    )
    four_star_hotels_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Four star hotels quantity"), null=True, blank=True
    )
    five_star_hotels_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Five star hotels quantity"), null=True, blank=True
    )
    four_star_luxury_hotels_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Four star luxury hotels quantity"), null=True, blank=True
    )

    resting_places_description = models.TextField(
        verbose_name=_("Resting places description"), blank=True, null=True
    )
    accommodations_description = models.TextField(
        verbose_name=_("Accommodations description"), blank=True, null=True
    )

    def __str__(self):
        return "%s" % self.label


class Structure(TouristicObject, StructureMethods):
    type = models.ForeignKey(
        BaseElement,
        verbose_name=_("Type"),
        null=True,
        blank=True,
        related_name="type_structure_structures_set",
        on_delete=models.SET_NULL,
    )  # structureType - objets_lies_modifies-214781.json

    def __str__(self):
        return "%s" % self.label


class AllInclusiveTrip(TouristicObject, AllInclusiveTripMethods):
    days_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Days quantity"), null=True, blank=True
    )  # nombreJours
    nights_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Nights quantity"), null=True, blank=True
    )  # nombreNuits
    location_description = models.TextField(
        verbose_name=_("Location description"), blank=True, null=True
    )  # lieuDePratique
    accommodation_description = models.TextField(
        verbose_name=_("Accommodation description"), blank=True, null=True
    )  # formuleHebergement
    accommodations_types = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Accommodations types"),
        blank=True,
        related_name="accommodations_types_all_inclusive_set",
    )  # typesHebergement
    transports_types = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Transports types"),
        blank=True,
        related_name="transports_types_all_inclusive_set",
    )  # transports
    activities_category = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Activities category"),
        blank=True,
        related_name="activity_category_all_inclusive_set",
    )  # activiteCategories

    def __str__(self):
        return "%s" % self.label


class Restaurant(TouristicObject, RestaurantMethods):
    chef_name = models.CharField(
        verbose_name=_("Chef name"), max_length=1000, blank=True, null=True
    )  # chef - objets_lies_modifies-133787.json
    brand = models.CharField(
        verbose_name=_("Brand name"), max_length=1000, blank=True, null=True
    )  # label - objets_lies_modifies-124356.json
    type = models.ForeignKey(
        BaseElement,
        verbose_name=_("Type"),
        related_name="type_restaurant_set",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )  # restaurationType - objets_lies_modifies-124356.json
    ranking = models.ForeignKey(
        BaseElement,
        verbose_name=_("Ranking"),
        related_name="ranking_restaurant_set",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )  # classement - objets_lies_modifies-124356.json
    specialities = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Specialities"),
        related_name="specialities_restaurant_set",
        blank=True,
    )  # specialites - objets_lies_modifies-124356.json
    chains = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Chains"),
        related_name="chains_restaurant_set",
        blank=True,
    )  # chaines - objets_lies_modifies-124356.json
    guides_ranking = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Guides ranking"),
        related_name="guides_ranking_restaurant_set",
        blank=True,
    )  # classementsGuides - objets_lies_modifies-124356.json
    categories = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Categories"),
        related_name="categories_restaurant_set",
        blank=True,
    )  # categories - objets_lies_modifies-133787.json
    rooms_description = models.TextField(
        verbose_name=_("Rooms description"), blank=True, null=True
    )  # descriptionSalles - objets_lies_modifies-104285.json
    rooms_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Rooms quantity"), null=True, blank=True
    )  # nombreSalles - objets_lies_modifies-104285.json
    air_conditioned_rooms_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Air-conditioned rooms quantity"), null=True, blank=True
    )  # nombreSallesClimatisees - objets_lies_modifies-124356.json
    maximum_capacity = models.PositiveSmallIntegerField(
        verbose_name=_("Maximum capacity"), null=True, blank=True
    )  # nombreMaximumCouverts - objets_lies_modifies-124356.json
    patio_capacity = models.PositiveSmallIntegerField(
        verbose_name=_("Patio capacity"), null=True, blank=True
    )  # nombreCouvertsTerrasse - objets_lies_modifies-124356.json

    def __str__(self):
        return "%s" % self.label


class NaturalHeritage(TouristicObject, NaturalHeritageMethods):
    marked_trail = models.BooleanField(
        verbose_name=_("Marked trail"), default=False
    )  # sentiersBalises
    rankings = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Rankings"),
        related_name="rankings_natural_heritage_set",
    )  # classements
    categories = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Natural heriatage categories"),
        blank=True,
        related_name="categories_natural_heritage_set",
    )  # categories

    def __str__(self):
        return "%s" % self.label


class CulturalHeritage(TouristicObject, CulturalHeritageMethods):
    type = models.ForeignKey(
        BaseElement,
        verbose_name=_("Type"),
        related_name="type_cultural_heritage_set",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )  # patrimoineCulturelType
    subjects = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Cultural heritage subjects"),
        blank=True,
        related_name="subjects_cultural_heritage_set",
    )  # themes
    categories = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Cultural heriatage categories"),
        blank=True,
        related_name="categories_cultural_heritage_set",
    )  # categories

    def __str__(self):
        return "%s" % self.label


class OutDoorHotelAccommodation(TouristicObject, OutDoorHotelAccommodationMethods):
    type = models.ForeignKey(
        BaseElement,
        verbose_name=_("Type"),
        related_name="type_outdoor_hotel_accommodation_set",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )  # hotelleriePleinAirType
    ranking_identifier = models.CharField(
        verbose_name=_("Ranking identifier"), max_length=500, blank=True, null=True
    )  # numeroClassement - objets_lies_modifies-100656.json
    ranking_date = models.DateField(
        verbose_name=_("Ranking date"), null=True, blank=True
    )  # dateClassement
    ranking = models.ForeignKey(
        BaseElement,
        verbose_name=_("Ranking"),
        null=True,
        blank=True,
        related_name="ranking_outdoor_hotel_accommodation_set",
        on_delete=models.SET_NULL,
    )  # classement
    chains = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Chains"),
        related_name="chains_outdoor_hotel_accommodation_set",
        blank=True,
    )  # chaines
    labels = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Labels"),
        related_name="labels_outdoor_hotel_accommodation_set",
        blank=True,
    )  # labels

    # Capacity
    surface_area = models.IntegerField(
        verbose_name=_("Surface area"), null=True, blank=True
    )  # superficie
    naturism = models.BooleanField(
        verbose_name=_("Naturism"), default=False
    )  # naturisme
    snow_caravans = models.BooleanField(
        verbose_name=_("Caravaneige/snow caravans"), default=False
    )  # caravaneige
    ranked_campingplot_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Ranked campingplot quantity"), null=True, blank=True
    )  # nombreEmplacementsClasses
    passing_campingplot_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Passing campingplot quantity"), null=True, blank=True
    )  # nombreEmplacementsPassages
    rental_passing_campingplot_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Rental passing campingplot quantity"), null=True, blank=True
    )  # nombreEmplacementsPassagesLocatifs
    naked_passing_campingplot_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Naked passing campingplot quantity"), null=True, blank=True
    )  # nombreEmplacementsPassagesNus
    residential_campingplot_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Residential campingplot quantity"), null=True, blank=True
    )  # nombreEmplacementsResidentiels
    snow_caravans_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Snow caravans campingplot quantity"), null=True, blank=True
    )  # nombreEmplacementsCaravaneiges
    tents_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Tents campingplot quantity"), null=True, blank=True
    )  # nombreEmplacementsTentes
    caravans_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Caravans campingplot quantity"), null=True, blank=True
    )  # nombreEmplacementsCaravanes
    campervan_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Campervan quantity"), null=True, blank=True
    )  # nombreEmplacementsCampingCars
    mobilhome_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Mobilehome quantity"), null=True, blank=True
    )  # nombreLocationMobilhomes
    tents_rental_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Tents rental quantity"), null=True, blank=True
    )  # nombreLocationTentes
    bungalow_rental_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Bungalow rental quantity"), null=True, blank=True
    )  # nombreLocationBungalows
    caravans_rental_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Caravans rental quantity"), null=True, blank=True
    )  # nombreLocationCaravanes
    declared_plots_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Declared plots quantity"), null=True, blank=True
    )  # nombreEmplacementsDeclares

    def __str__(self):
        return "%s" % self.label


class HotelAccommodation(TouristicObject, HotelAccommodationMethods):
    type = models.ForeignKey(
        BaseElement,
        verbose_name=_("Type"),
        blank=True,
        null=True,
        related_name="type_hotel_accommodation_set",
        on_delete=models.SET_NULL,
    )  # hotellerieType
    ranking_identifier = models.CharField(
        verbose_name=_("Ranking identifier"), max_length=500, blank=True, null=True
    )  # numeroClassement
    ranking_date = models.DateField(
        verbose_name=_("Ranking date"), null=True, blank=True
    )  # dateClassement
    ranking = models.ForeignKey(
        BaseElement,
        verbose_name=_("Ranking"),
        null=True,
        blank=True,
        related_name="ranking_hotel_accommodation_set",
        on_delete=models.SET_NULL,
    )  # classement
    chains = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Chains"),
        related_name="chains_hotel_accommodation_set",
        blank=True,
    )  # chaines
    labels = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Labels"),
        related_name="labels_hotel_accommodation_set",
        blank=True,
    )  # labels

    # Capacity
    ranked_rooms_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Ranked rooms quantity"), null=True, blank=True
    )  # nombreChambresClassees
    hotel_declared_rooms_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Hotel declared rooms quantity"), null=True, blank=True
    )  # nombreChambresDeclareesHotelier
    max_capacity = models.PositiveSmallIntegerField(
        verbose_name=_("Max capacity"), null=True, blank=True
    )  # nombreTotalPersonnes
    single_rooms_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Single rooms quantity"), null=True, blank=True
    )  # nombreChambresSimples
    double_rooms_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Double rooms quantity"), null=True, blank=True
    )  # nombreChambresDoubles
    suite_rooms_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Suite rooms quantity"), null=True, blank=True
    )  # nombreSuites
    reduced_mobility_rooms_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Reduced mobility rooms quantity"), null=True, blank=True
    )  # nombreChambresMobiliteReduite

    def __str__(self):
        return "%s" % self.label


class RentalAccommodation(TouristicObject, RentalAccommodationMethods):
    type = models.ForeignKey(
        BaseElement,
        verbose_name=_("Type"),
        related_name="type_rental_accommodation_set",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )  # hebergementLocatifType
    last_visit_date = models.DateField(
        verbose_name=_("Last visit date"), null=True, blank=True
    )  # dateDerniereVisite
    ranking_date = models.DateField(
        verbose_name=_("Ranking date"), null=True, blank=True
    )  # dateClassement
    ranking_identifier = models.CharField(
        verbose_name=_("Ranking identifier"), max_length=500, blank=True, null=True
    )  # numeroClassement
    label_authorization_identifier = models.CharField(
        verbose_name=_("Label authorization identifier"),
        max_length=500,
        blank=True,
        null=True,
    )  # numeroAgrementLabel
    prefectural_classification = models.ForeignKey(
        BaseElement,
        verbose_name=_("Prefectural classification"),
        null=True,
        blank=True,
        related_name="prefectural_classification_rental_accommodation_set",
        on_delete=models.SET_NULL,
    )  # classementPrefectoral
    label_type = models.ForeignKey(
        BaseElement,
        verbose_name=_("Label type"),
        null=True,
        blank=True,
        related_name="label_type_rental_accommodation_set",
        on_delete=models.SET_NULL,
    )  # typeLabel
    labels = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Labels"),
        related_name="labels_rental_accommodation_set",
        blank=True,
    )  # labels
    habitation_types = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Habitation types"),
        related_name="habitation_types_rental_accommodation_set",
        blank=True,
    )  # typesHabitation

    # Capacity
    naturism = models.BooleanField(
        verbose_name=_("Naturism"), default=False
    )  # naturisme
    capacity = models.PositiveSmallIntegerField(
        verbose_name=_("Accommodation capacity"), null=True, blank=True
    )  # capaciteHebergement
    max_capacity = models.PositiveSmallIntegerField(
        verbose_name=_("Max capacity"), null=True, blank=True
    )  # capaciteMaximumPossible
    double_beds_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Double beds quantity"), null=True, blank=True
    )  # nombreLitsDoubles
    single_beds_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Single beds quantity"), null=True, blank=True
    )  # nombreLitsSimples
    surface_area = models.IntegerField(
        verbose_name=_("Surface area"), null=True, blank=True
    )  # surface
    rooms_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Rooms quantity"), null=True, blank=True
    )  # nombrePieces
    bedrooms_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Bedrooms quantity"), null=True, blank=True
    )  # nombreChambres
    floors_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Floors quantity"), null=True, blank=True
    )  # nombreEtages
    floor_number = models.CharField(
        verbose_name=_("Floor number"), null=True, blank=True, max_length=500
    )  # numeroEtage

    def __str__(self):
        return "%s" % self.label


class GroupAccommodation(TouristicObject, GroupAccommodationMethods):
    type = models.ForeignKey(
        BaseElement,
        verbose_name=_("Type"),
        related_name="type_group_accommodation_set",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )  # hebergementCollectifType
    ranking_date = models.DateField(
        verbose_name=_("Ranking date"), null=True, blank=True
    )  # dateClassement
    ranking_identifier = models.CharField(
        verbose_name=_("Ranking identifier"), max_length=500, blank=True, null=True
    )  # numeroClassement
    prefectural_classification = models.ForeignKey(
        BaseElement,
        verbose_name=_("Prefectural classification"),
        null=True,
        blank=True,
        related_name="prefectural_classification_group_accommodation_set",
        on_delete=models.SET_NULL,
    )  # classementPrefectoral
    chain_and_label = models.ForeignKey(
        BaseElement,
        verbose_name=_("Chain and label"),
        related_name="chain_and_label_group_accommodation_set",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )  # chaineEtLabel
    labels = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Labels"),
        related_name="labels_group_accommodation_set",
        blank=True,
    )  # labels
    accommodations_types = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Accommodations types"),
        related_name="accommodations_types_group_accommodation_set",
        blank=True,
    )  # typesHebergement
    housing_types = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Housing types"),
        related_name="housing_types_group_accommodation_set",
        blank=True,
    )  # typesHabitation
    agrements = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Agrements"),
        through="AgrementsGroupAccommodation",
        related_name="agrements_group_accommodation_set",
        blank=True,
    )  # agrements

    # Capacity
    naturism = models.BooleanField(
        verbose_name=_("Naturism"), default=False
    )  # naturisme
    capacity = models.PositiveSmallIntegerField(
        verbose_name=_("Capacity"), null=True, blank=True
    )  # capaciteTotale
    youth_and_sports_capacity = models.PositiveSmallIntegerField(
        verbose_name=_("Youth and sports capacity"), null=True, blank=True
    )  # capaciteTotaleJeunesseSport
    national_education_capacity = models.PositiveSmallIntegerField(
        verbose_name=_("National education capacity"), null=True, blank=True
    )  # capaciteTotaleEducationNationale
    safety_committee_capacity = models.PositiveSmallIntegerField(
        verbose_name=_("Safety committee capacity"), null=True, blank=True
    )  # capaciteCommissionSecurite
    middle_size_dormitory_capacity = models.PositiveSmallIntegerField(
        verbose_name=_("Middle size dormitory capacity"), null=True, blank=True
    )  # nombreDortoirsMoyens
    king_size_dormitory_capacity = models.PositiveSmallIntegerField(
        verbose_name=_("King size dormitory capacity"), null=True, blank=True
    )  # nombreDortoirsGrands
    reduced_mobility_accommodations_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Reduced mobility accommodations quantity"),
        null=True,
        blank=True,
    )  # nombreHebergementsMobiliteReduite
    one_person_accommodations_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("One person accommodations quantity"), null=True, blank=True
    )  # nombreHebergementsUnePersonne
    two_persons_accommodations_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Two persons accommodations quantity"), null=True, blank=True
    )  # nombreHebergementsDeuxPersonnes
    three_persons_accommodations_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Three persons accommodations quantity"), null=True, blank=True
    )  # nombreHebergementsTroisPersonnes
    four_persons_accommodations_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Four persons accommodations quantity"), null=True, blank=True
    )  # nombreHebergementsQuatrePersonnes
    five_persons_accommodations_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Five persons accommodations quantity"), null=True, blank=True
    )  # nombreHebergementsCinqPersonnes
    six_persons_accommodations_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Six persons accommodations quantity"), null=True, blank=True
    )  # nombreHebergementsSixPersonnes
    more_than_six_persons_accommodations_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("More than six persons accommodations quantity"),
        null=True,
        blank=True,
    )  # nombreHebergementsPlusSixPersonnes

    def __str__(self):
        return "%s" % self.label


class AgrementsGroupAccommodation(models.Model):
    group_accommodation = models.ForeignKey(
        "GroupAccommodation",
        verbose_name=_("Group accommodation"),
        related_name="group_accommodation_group_accommodation_set",
        on_delete=models.CASCADE,
    )
    agrement = models.ForeignKey(
        BaseElement,
        verbose_name=_("Agrement"),
        related_name="agrement_group_accommodation_set",
        on_delete=models.CASCADE,
    )  # HebergementCollectifAgrementType
    agrement_identifier = models.CharField(
        verbose_name=_("Agrement identifier"), max_length=500, blank=True, null=True
    )  # numero

    def __str__(self):
        return "%s" % self.label


class CelebrationAndManifestation(TouristicObject, CelebrationAndManifestationMethods):
    manifestation_types = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Manifestation types"),
        blank=True,
        related_name="manifestation_types_celebration_and_manifestation_set",
    )  # typesManifestation
    categories = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Celebrations and Manifestations categories"),
        blank=True,
        related_name="categories_celebration_and_manifestation_set",
    )  # categories
    subjects = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Celebrations and Manifestations subjects"),
        blank=True,
        related_name="subjects_celebration_and_manifestation_set",
    )  # themes
    generic_type = models.ForeignKey(
        BaseElement,
        verbose_name=_("Celebrations and Manifestations generic type"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="generic_type_celebration_and_manifestation_set",
    )  # evenementGenerique
    manifestation_reach = models.ForeignKey(
        BaseElement,
        verbose_name=_("Manifestation reach/impact"),
        blank=True,
        null=True,
        related_name="reach_celebration_and_manifestation_set",
        on_delete=models.SET_NULL,
    )  # portee

    def __str__(self):
        return "%s" % self.label


class Equipment(TouristicObject, EquipmentMethods):
    type = models.ForeignKey(
        BaseElement,
        verbose_name=_("Type"),
        related_name="type_equipment_set",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )  # rubrique
    equipment_activities = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Activities"),
        related_name="activities_equipment_set",
    )  # activites

    # Itinerary
    difference_in_level = models.IntegerField(
        verbose_name=_("Level difference"), null=True, blank=True
    )  # denivellation
    distance = models.PositiveSmallIntegerField(
        verbose_name=_("Distance"), null=True, blank=True
    )  # distance
    daily_duration = models.PositiveSmallIntegerField(
        verbose_name=_("Daily duration"), null=True, blank=True
    )  # dureeJournaliere
    mobility_duration = models.PositiveSmallIntegerField(
        verbose_name=_("Mobility duration"), null=True, blank=True
    )  # dureeItinerance
    itinerary_type = models.CharField(
        verbose_name=_("Itinerary type"),
        max_length=500,
        choices=ITINERARY_TYPE_CHOICES,
        null=True,
        blank=True,
    )

    def __str__(self):
        return "%s" % self.label


class SkiingArea(TouristicObject, SkiingAreaMethods):
    classification = models.ForeignKey(
        BaseElement,
        verbose_name=_("Classification"),
        related_name="classification_skiing_area_set",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )  # classification
    types = models.ManyToManyField(
        BaseElement, verbose_name=_("Types"), related_name="types_skiing_area_set"
    )  # domaineSkiableTypes
    linked_domain_description = models.TextField(
        verbose_name=_("Linked domain description"), blank=True, null=True
    )  # identifiantDomaineRelie
    free_ski_pass_conditions = models.TextField(
        verbose_name=_("Free ski pass conditions"), blank=True, null=True
    )  # conditionForfaitGratuit
    ski_pass_identifier = models.TextField(
        verbose_name=_("Ski pass identifier"), blank=True, null=True
    )  # identifiantForfait
    children_validity_conditions = models.TextField(
        verbose_name=_("Children validity conditions"), blank=True, null=True
    )  # validiteTarifEnfant
    senior_validity_conditions = models.TextField(
        verbose_name=_("Senior validity conditions"), blank=True, null=True
    )  # validiteTarifSenior
    egps = models.ManyToManyField(
        TouristicObject,
        verbose_name=_("EGPS"),
        blank=True,
        related_name="egps_skiingarea_set",
    )  # egps
    subarea_ski_resorts = models.ManyToManyField(
        TouristicObject,
        verbose_name=_("Subarea ski resorts"),
        blank=True,
        related_name="subarea_ski_resorts_skiingarea_set",
    )  # sousDomaines
    parents_ski_resorts = models.ManyToManyField(
        TouristicObject,
        verbose_name=_("Parents ski resorts"),
        blank=True,
        related_name="parents_ski_resorts_skiingarea_set",
    )  # domainesParents
    artificial_snow = models.BooleanField(
        verbose_name=_("Artificial snow"), default=False
    )  # neigeCulture
    free_ski_lift = models.BooleanField(
        verbose_name=_("Free ski lift"), default=False
    )  # remonteeGratuite
    snow_description = models.TextField(
        verbose_name=_("Snow description"), null=True, blank=True
    )  # neigeDescription
    ski_trail_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Ski trail quantity"), null=True, blank=True
    )  # nombrePistes
    ski_trail_km = models.PositiveSmallIntegerField(
        verbose_name=_("Ski trail kilometers"), null=True, blank=True
    )  # nombreKmPiste
    green_trail_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Green ski trail quantity"), null=True, blank=True
    )  # nombrePistesVertes
    green_trail_km = models.PositiveSmallIntegerField(
        verbose_name=_("Green ski trail kilometers"), null=True, blank=True
    )  # nombreKmPisteVerte
    blue_trail_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Blue ski trail quantity"), null=True, blank=True
    )  # nombrePistesBleues
    blue_trail_km = models.PositiveSmallIntegerField(
        verbose_name=_("Blue ski trail kilometers"), null=True, blank=True
    )  # nombreKmPisteBleue
    red_trail_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Red ski trail quantity"), null=True, blank=True
    )  # nombrePistesRouges
    red_trail_km = models.PositiveSmallIntegerField(
        verbose_name=_("Red ski trail kilometers"), null=True, blank=True
    )  # nombreKmPisteRouge
    black_trail_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Black ski trail quantity"), null=True, blank=True
    )  # nombrePistesNoires
    black_trail_km = models.PositiveSmallIntegerField(
        verbose_name=_("Black ski trail kilometers"), null=True, blank=True
    )  # nombreKmPisteNoire
    skating_km = models.PositiveSmallIntegerField(
        verbose_name=_("Skating kilometers"), null=True, blank=True
    )  # nombreKmPisteSkating
    aerial_lift_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Aerial lift quantity"), null=True, blank=True
    )  # nombreRemonteesMecaniques
    platter_lift_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Platter lift quantity"), null=True, blank=True
    )  # nombreTeleskis
    chairlift_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Chairlift quantity"), null=True, blank=True
    )  # nombreTelesieges
    cable_car_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Cable car quantity"), null=True, blank=True
    )  # nombreTelecabines
    aerial_tramway_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Aerial tramway quantity"), null=True, blank=True
    )  # nombreTelepheriques
    other_lift_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Other lift quantity"), null=True, blank=True
    )  # nombreAutresRemontees
    pedestrian_accessible_lift_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Pedestrian accessible lift quantity"), null=True, blank=True
    )  # nombreRemonteesAccessiblesPietons
    handiski_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Handiski quantity"), null=True, blank=True
    )  # nombreHandiski
    cross_country_skiing_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Cross-country skiing quantity"), null=True, blank=True
    )  # nombreRemonteesSkiFond

    def __str__(self):
        return "%s" % self.label


class Tasting(TouristicObject, TastingMethods):
    aoc = models.BooleanField(
        verbose_name=_("Appellation d'origine controlée"), default=False
    )  # aoc
    quality_charter_description = models.TextField(
        verbose_name=_("Quality charter description"), blank=True, null=True
    )  # charteQualite
    aoc_description = models.TextField(
        verbose_name=_("'AOC' description"), blank=True, null=True
    )  # aocDescriptif
    production_region = models.ForeignKey(
        BaseElement,
        verbose_name=_("Production region"),
        related_name="production_region_tasting_set",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )  # regionProduction
    local_area = models.CharField(
        verbose_name=_("Local area"), max_length=500, blank=True, null=True
    )  # zoneLocale
    production_area = models.ForeignKey(
        BaseElement,
        verbose_name=_("Production area"),
        related_name="production_area_tasting_set",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )  # territoireProduction
    goods_types = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Goods types"),
        blank=True,
        related_name="goods_types_tasting_set",
    )  # typesProduit
    operators_status = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Operators status"),
        blank=True,
        related_name="operators_status_tasting_set",
    )  # statutsExploitant
    quality_charter = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Quality charter"),
        blank=True,
        related_name="quality_charter_set",
    )  # labelsChartesQualite
    aop_aoc_igps = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Aop aoc igps"),
        blank=True,
        related_name="aop_aoc_igps_set",
    )  # aop_aoc_igps

    def __str__(self):
        return "%s" % self.label


class BusinessAndService(TouristicObject, BusinessAndServiceMethods):
    type = models.ForeignKey(
        BaseElement,
        verbose_name=_("Type"),
        related_name="type_business_and_service_set",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )  # commerceEtServiceType
    detailed_types = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Detailed types"),
        related_name="detailed_types_business_and_service_set",
    )  # typesDetailles

    def __str__(self):
        return "%s" % self.label


class Activity(TouristicObject, ActivityMethods):
    session_duration = models.PositiveSmallIntegerField(
        verbose_name=_("Session duration"), null=True, blank=True
    )  # dureeSeance
    frequency = models.PositiveSmallIntegerField(
        verbose_name=_("Frequency"), null=True, blank=True
    )  # nombreJours
    type = models.ForeignKey(
        BaseElement,
        verbose_name=_("Type"),
        related_name="type_activity_set",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )  # activiteType
    durations = models.ManyToManyField(
        BaseElement, verbose_name=_("Durations"), related_name="durations_activity_set"
    )  # durees
    categories = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Categories"),
        related_name="categories_activity_set",
    )  # categories
    sport_activities = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Sport activities"),
        related_name="sport_activities_activity_set",
    )  # activitesSportives
    cultural_activities = models.ManyToManyField(
        BaseElement,
        verbose_name=_("Cultural activities"),
        related_name="cultural_activities_activity_set",
    )  # activitesCulturelles
    recipient = models.PositiveIntegerField(
        verbose_name=_("Recipient"), null=True, blank=True
    )  # Prestataire d'activité id

    def __str__(self):
        return "%s" % self.label

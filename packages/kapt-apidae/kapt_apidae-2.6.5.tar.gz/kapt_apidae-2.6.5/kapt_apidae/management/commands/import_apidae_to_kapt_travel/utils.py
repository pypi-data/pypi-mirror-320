# Standard Library
from calendar import monthrange
import datetime
import os
import sys

# Third party
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.db import transaction
from django.utils.text import slugify

# Local application / specific library imports
from kapt_apidae.conf import settings as kapt_apidae_settings
from kapt_apidae.management import logger


ROOT_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../..")

if kapt_apidae_settings.APIDAE_IN_KAPT_CATALOG:
    from kapt_catalog.models.activities import RatingUnit, TouristicLabel
    from kapt_catalog.models.characteristic import Characteristic


# django 1.6, 1.5 and 1.4 supports
try:
    transaction_method = transaction.atomic
except AttributeError:
    transaction_method = transaction.commit_on_success


def get_touristic_label(identifier, dictionary=None):
    try:
        if dictionary:
            try:
                label_rating = dictionary[identifier.id]["value"]
            except Exception:
                label_rating = None
            finally:
                return (
                    TouristicLabel.objects.get(
                        identifier=dictionary[identifier.id]["identifier"]
                    ),
                    label_rating,
                )
        else:
            return (TouristicLabel.objects.get(identifier=identifier), None)
    except KeyError:
        logger.warning("TouristicLabel" + " : " + str(identifier.id) + " key error")
        return (None, None)
    except ObjectDoesNotExist:
        logger.warning("TouristicLabel" + " : " + str(identifier.id) + " unknown")
        return (None, None)


def get_characteristic(identifier):
    try:
        return Characteristic.objects.get(identifier=identifier)
    except ObjectDoesNotExist:
        logger.warning("Characteristic" + " : " + str(identifier) + " not handle")


def create_label(label_infos):
    # Try to ignore doublons
    try:
        # Ignore this label if a label with the same name but a different identifier exists
        if (
            TouristicLabel.objects.filter(name_fr=label_infos["name_fr"])
            .exclude(identifier=label_infos["identifier"])
            .exists()
        ):
            return
    except KeyError:
        pass

    label, created = TouristicLabel.objects.get_or_create(
        identifier=label_infos["identifier"]
    )
    if created:
        label.name_fr = label_infos["name_fr"]
        label.name_en = label_infos["name_en"]
        if label.name_en == "None" or label.name_en is None:
            label.name_en = label.name_fr
        label.save()

    if not label.logo:
        file_path = os.path.join(
            ROOT_PATH, "static", "img", "{}.png".format(label.identifier)
        )
        if os.path.exists(file_path):
            file_name = "{}.png".format(slugify(label.name_fr))
            label.logo.save(file_name, File(open(file_path, "rb")))

    # Rating units
    if label.identifier == "2737":
        # Gîtes de France
        label.rating_unit = create_rating_unit(
            {"name_fr": "épis", "name_en": "épis", "identifier": "rating-unit-epi"}
        )

    elif label.identifier == "2635":
        # Clé Vacances
        label.rating_unit = create_rating_unit(
            {"name_fr": "clés", "name_en": "keys", "identifier": "rating-unit-key"}
        )

    elif label.identifier == "2964":
        # Michelin
        label.rating_unit = create_rating_unit(
            {
                "name_fr": "étoiles",
                "name_en": "stars",
                "identifier": "rating-unit-michelin-star",
            }
        )

    elif label.identifier == "2953":
        # Gault & Millau
        label.rating_unit = create_rating_unit(
            {
                "name_fr": "toques",
                "name_en": "toques",
                "identifier": "rating-unit-gault-millau-toque",
            }
        )

    # if you want to add a new rating unit, you must also check the constant
    # HANDMADE_RESTAURANT_RANKING in file handmade_characteristics.py

    label.save()

    content_type = label_infos.get("content-type", None)
    if content_type is not None:
        label.activity_types.clear()
        label.activity_types.add(
            ContentType.objects.get_by_natural_key("kapt_catalog", content_type.lower())
        )


def create_rating_unit(rating_unit_infos):
    rating_unit, created = RatingUnit.objects.get_or_create(
        identifier=rating_unit_infos["identifier"]
    )
    if created:
        rating_unit.name_fr = rating_unit_infos["name_fr"]
        rating_unit.name_en = rating_unit_infos["name_en"]
        rating_unit.save()

    if not rating_unit.icon:
        file_path = os.path.join(
            ROOT_PATH, "static", "img", "{}.png".format(rating_unit_infos["identifier"])
        )
        if os.path.exists(file_path):
            file_name = "{}.png".format(slugify(rating_unit.name_fr))
            rating_unit.icon.save(file_name, File(open(file_path, "rb")))

    return rating_unit


def purge_labels(exclude_ids):
    TouristicLabel.objects.exclude(identifier__in=exclude_ids).delete()


def create_characteristic(characteristic):
    FIELDS = ["name_fr", "name_en", "name_es", "name_it", "name_de", "name_nl"]

    if (
        "parent" in characteristic
        and characteristic["parent"] == characteristic["identifier"]
    ):
        return
    else:
        c, created = Characteristic.objects.get_or_create(
            identifier=characteristic["identifier"]
        )

        if (
            created is False
            and c.identifier in kapt_apidae_settings.EXCLUDED_CHARACTERISTICS_UPDATE
        ):
            return

        # Check if all fields are empty
        characteristic_to_do = False
        for attr_name in FIELDS:
            if (attr_name in characteristic) is True:
                characteristic_to_do = True
                break
        if not characteristic_to_do:
            return

        for attr_name in FIELDS:
            if (
                attr_name in characteristic
                and characteristic[attr_name] is not None
                and characteristic[attr_name] != "None"
            ):
                setattr(c, attr_name, characteristic[attr_name])
            else:
                setattr(c, attr_name, None)

        if "is_category" in characteristic:
            c.is_category = characteristic["is_category"]
        if "value" in characteristic:
            c.value = characteristic["value"]

        if "parent" in characteristic and not characteristic["parent"] is None:
            try:
                c.parent = Characteristic.objects.get(
                    identifier=characteristic["parent"]
                )
            except Exception:
                print("Parent missing : {}".format(characteristic["parent"]))
        c.save()


def copy_translated_fields(source, destination, src_field_name, dest_field_name):
    for language in settings.LANGUAGES:
        source_field_name = src_field_name + "_" + language[0]
        destination_field_name = dest_field_name + "_" + language[0]
        setattr(
            destination,
            destination_field_name,
            getattr(source, source_field_name, None),
        )


def is_translated_fields_empty(obj, field_name):
    for language in settings.LANGUAGES:
        if getattr(obj, "{}_{}".format(field_name, language), None) is not None:
            return False
    if getattr(obj, field_name, None) is not None:
        return False
    return True


def init_import():
    # Characteristic module is generated dynamically, so the current loaded version is out of date
    # We delete this module and we reload it after
    # We do not have to launch import_apidae_kaptravel -i twice anymore

    characteristic_class = "kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.characteristics.generated_characteristics"
    characteristic_class_2 = "kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.characteristics"
    try:
        del sys.modules[characteristic_class]
        del sys.modules[characteristic_class_2]
    except KeyError:
        pass

    from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog import (  # noqa
        characteristics,
    )

    with transaction_method():
        # Bed sizes (booking)
        create_characteristic(
            {
                "identifier": "accommodation-activity-bed-size",
                "name_fr": "Taille lit",
                "name_en": "Bed size",
                "parent": None,
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "two-people-accommodation-activity-bed-size",
                "name_fr": "Deux personnes",
                "name_en": "Two people",
                "parent": "accommodation-activity-bed-size",
                "is_category": True,
                "value": 2,
            }
        )
        create_characteristic(
            {
                "identifier": "140-cm-accommodation-activity-bed-size",
                "name_fr": "140 cm",
                "name_en": "140 cm",
                "parent": "two-people-accommodation-activity-bed-size",
                "is_category": False,
            }
        )
        create_characteristic(
            {
                "identifier": "160-cm-accommodation-activity-bed-size",
                "name_fr": "160 cm",
                "name_en": "160 cm",
                "parent": "two-people-accommodation-activity-bed-size",
                "is_category": False,
            }
        )
        create_characteristic(
            {
                "identifier": "180-cm-accommodation-activity-bed-size",
                "name_fr": "180 cm",
                "name_en": "180 cm",
                "parent": "two-people-accommodation-activity-bed-size",
                "is_category": False,
            }
        )
        create_characteristic(
            {
                "identifier": "200-cm-accommodation-activity-bed-size",
                "name_fr": "200 cm",
                "name_en": "200 cm",
                "parent": "two-people-accommodation-activity-bed-size",
                "is_category": False,
            }
        )
        create_characteristic(
            {
                "identifier": "90-cm-bunk-beds-accommodation-activity-bed-size",
                "name_fr": "90 cm (lits superposés)",
                "name_en": "90 cm bunk beds",
                "parent": "two-people-accommodation-activity-bed-size",
                "is_category": False,
            }
        )

        create_characteristic(
            {
                "identifier": "one-people-accommodation-activity-bed-size",
                "name_fr": "Une personne",
                "name_en": "One people",
                "parent": "accommodation-activity-bed-size",
                "is_category": True,
                "value": 1,
            }
        )
        create_characteristic(
            {
                "identifier": "80-cm-accommodation-activity-bed-size",
                "name_fr": "80 cm",
                "name_en": "80 cm",
                "parent": "one-people-accommodation-activity-bed-size",
                "is_category": False,
            }
        )
        create_characteristic(
            {
                "identifier": "90-cm-accommodation-activity-bed-size",
                "name_fr": "90 cm",
                "name_en": "90 cm",
                "parent": "one-people-accommodation-activity-bed-size",
                "is_category": False,
            }
        )
        create_characteristic(
            {
                "identifier": "100-cm-accommodation-activity-bed-size",
                "name_fr": "100 cm",
                "name_en": "100 cm",
                "parent": "one-people-accommodation-activity-bed-size",
                "is_category": False,
            }
        )
        create_characteristic(
            {
                "identifier": "110-cm-accommodation-activity-bed-size",
                "name_fr": "110 cm",
                "name_en": "110 cm",
                "parent": "one-people-accommodation-activity-bed-size",
                "is_category": False,
            }
        )
        create_characteristic(
            {
                "identifier": "120-cm-accommodation-activity-bed-size",
                "name_fr": "120 cm",
                "name_en": "120 cm",
                "parent": "one-people-accommodation-activity-bed-size",
                "is_category": False,
            }
        )
        create_characteristic(
            {
                "identifier": "130-cm-accommodation-activity-bed-size",
                "name_fr": "130 cm",
                "name_en": "130 cm",
                "parent": "one-people-accommodation-activity-bed-size",
                "is_category": False,
            }
        )
        create_characteristic(
            {
                "identifier": "baby-bed-accommodation-activity-bed-size",
                "name_fr": "Lit bébé",
                "name_en": "Baby bed",
                "parent": "one-people-accommodation-activity-bed-size",
                "is_category": False,
            }
        )
        create_characteristic(
            {
                "identifier": "children-bed-accommodation-activity-bed-size",
                "name_fr": "Lit enfant",
                "name_en": "Children bed",
                "parent": "one-people-accommodation-activity-bed-size",
                "is_category": False,
            }
        )

        # Categories
        create_characteristic(
            {
                "identifier": "equipment-and-service",
                "name_fr": "Equipement & Service",
                "name_en": "Equipment & Service",
                "parent": None,
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "meal-activity",
                "name_fr": "Repas",
                "name_en": "Meal",
                "parent": None,
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "accommodation-activity",
                "name_fr": "Hébergement",
                "name_en": "Accommodation",
                "parent": None,
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "visibility",
                "name_fr": "Visibilité",
                "name_en": "Visibility",
                "parent": None,
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "visibility-website",
                "name_fr": "Site Web",
                "name_en": "Website",
                "parent": "visibility",
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "payment-mean",
                "name_fr": "Moyen de paiement",
                "name_en": "Payement mean",
                "parent": None,
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "tasting-activity",
                "name_fr": "Dégustation",
                "name_en": "Tasting",
                "parent": None,
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "equipment-activity",
                "name_fr": "Equipements",
                "name_en": "Equipment",
                "parent": None,
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "cultural-heritage-activity",
                "name_fr": "Patrimoine culturel",
                "name_en": "Cultural heritage",
                "parent": None,
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "natural-heritage-activity",
                "name_fr": "Patrimoine naturel",
                "name_en": "Natural heritage",
                "parent": None,
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "business-and-service-activity",
                "name_fr": "Commerces et services",
                "name_en": "Business and services",
                "parent": None,
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "cultural-activity",
                "name_fr": "Activité culturelle",
                "name_en": "Cultural activity",
                "parent": None,
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "sport-activity",
                "name_fr": "Activité sportive",
                "name_en": "Sport activity",
                "parent": None,
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "structure-activity",
                "name_fr": "Activité structure",
                "name_en": "Structure activity",
                "parent": None,
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "skiing-resort-activity",
                "name_fr": "Station de ski",
                "name_en": "Skiing resort",
                "parent": None,
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "pack-activity",
                "name_fr": "Séjour packagé",
                "name_en": "Packaged journey",
                "parent": None,
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "event-activity",
                "name_fr": "Activité événement",
                "name_en": "Event activity",
                "parent": None,
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "area-activity",
                "name_fr": "Activité territoire",
                "name_en": "Territory activity",
                "parent": None,
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "group-accommodations-agrements",
                "name_fr": "Agréments gîte de groupe",
                "name_en": "Group accommodation agrements",
                "parent": None,
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "business-tourism-service",
                "name_fr": "Services de tourisme d'affaires",
                "name_en": "Business tourism services",
                "parent": None,
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "business-tourism-service-rooms-equipements",
                "name_fr": "Services de tourisme d'affaires equipements des salles",
                "name_en": "Business tourism services rooms equipments",
                "parent": "business-tourism-service",
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "business-tourism-service-rooms-layouts",
                "name_fr": "Services de tourisme d'affaires disposition des salles",
                "name_en": "Business tourism services rooms layouts",
                "parent": "business-tourism-service",
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "business-tourism-service-rooms-usage",
                "name_fr": "Services de tourisme d'affaires usage des salles",
                "name_en": "Business tourism services rooms usage",
                "parent": "business-tourism-service",
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "business-tourism-service-catering",
                "name_fr": "Services de tourisme d'affaires équipements de restauration",
                "name_en": "Business tourism services catering equipments",
                "parent": "business-tourism-service",
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "business-tourism-service-accommodation",
                "name_fr": "Services de tourisme d'affaires hébergements",
                "name_en": "Business tourism services accommodations",
                "parent": "business-tourism-service",
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "typologies-promo",
                "name_fr": "Typologies Promo",
                "name_en": "Promo Typologies",
                "parent": None,
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "environment",
                "name_fr": "Environnement",
                "name_en": "Environment",
                "parent": None,
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "customer-types",
                "name_fr": "Types de clientèle",
                "name_en": "Customer types",
                "parent": None,
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "adapted-tourism",
                "name_fr": "Tourisme adapté",
                "name_en": "Adapted tourism",
                "parent": "equipment-and-service",
                "is_category": True,
            }
        ),
        create_characteristic(
            {
                "identifier": "adapted-tourism-autre",
                "name_fr": "Non classés",
                "name_en": "Not classified",
                "parent": "adapted-tourism",
                "is_category": True,
            }
        ),
        create_characteristic(
            {
                "identifier": "event-category",
                "name_fr": "Catégorie d'événement",
                "name_en": "Event category",
                "parent": None,
                "is_category": True,
            }
        ),
        create_characteristic(
            {
                "identifier": "event-type",
                "name_fr": "Type d'événement",
                "name_en": "Event type",
                "parent": None,
                "is_category": True,
            }
        ),

        # Needed for the admin ...
        # TODO: Delete meal informations and activity products
        create_characteristic(
            {
                "identifier": "meal-activity-products",
                "name_fr": "TO_DELETE",
                "name_en": "Products",
                "parent": "meal-activity",
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "meal-informations",
                "name_fr": "TO_DELETE",
                "name_en": "Information",
                "parent": "meal-activity",
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "housing-type",
                "name_fr": "Informations",
                "name_en": "Information",
                "parent": "meal-activity",
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "accommodation-activity-facilities",
                "name_fr": "accommodation-activity-facilities",
                "name_en": "accommodation-activity-facilities",
                "parent": "accommodation-activity",
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "accommodation-activity-technical-characteristics",
                "name_fr": "TO_DELETE",
                "name_en": "TO_DELETE",
                "parent": "accommodation-activity",
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "accommodation-activity-services",
                "name_fr": "TO_DELETE",
                "name_en": "TO_DELETE",
                "parent": "accommodation-activity",
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "accommodation-activity-relay-facilities",
                "name_fr": "TO_DELETE",
                "name_en": "TO_DELETE",
                "parent": "accommodation-activity",
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "structures-services",
                "name_fr": "TO_DELETE",
                "name_en": "TO_DELETE",
                "parent": "accommodation-activity",
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "nearby-services",
                "name_fr": "TO_DELETE",
                "name_en": "TO_DELETE",
                "parent": "accommodation-activity",
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "nearby-leisure",
                "name_fr": "TO_DELETE",
                "name_en": "TO_DELETE",
                "parent": "accommodation-activity",
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "description",
                "name_fr": "Description",
                "name_en": "Description",
                "parent": None,
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "website-description",
                "name_fr": "Description website",
                "name_en": "Website description",
                "parent": "description",
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "detailed-description",
                "name_fr": "Description détaillée",
                "name_en": "Detailed description",
                "parent": "website-description",
                "is_category": False,
            }
        )
        create_characteristic(
            {
                "identifier": "short-description",
                "name_fr": "Description brève",
                "name_en": "Short description",
                "parent": "website-description",
                "is_category": False,
            }
        )
        create_characteristic(
            {
                "identifier": "good-deal-description",
                "name_fr": "Bons plans",
                "name_en": "Good deal",
                "parent": "website-description",
                "is_category": False,
            }
        )
        create_characteristic(
            {
                "identifier": "access-means-description",
                "name_fr": "Moyen d'accès",
                "name_en": "Access means",
                "parent": "website-description",
                "is_category": False,
            }
        )
        create_characteristic(
            {
                "identifier": "further-welcoming-informations-description",
                "name_fr": "Informations d'accueil",
                "name_en": "Further welcoming informations",
                "parent": "website-description",
                "is_category": False,
            }
        )
        create_characteristic(
            {
                "identifier": "additional-booking-informations-description",
                "name_fr": "Complément d'information de réservation",
                "name_en": "Additional booking informations",
                "parent": "website-description",
                "is_category": False,
            }
        )
        create_characteristic(
            {
                "identifier": "additional-visit-informations-description",
                "name_fr": "Complément d'information de visite",
                "name_en": "Additional visit informations",
                "parent": "website-description",
                "is_category": False,
            }
        )
        create_characteristic(
            {
                "identifier": "opening-textual-description",
                "name_fr": "Périodes d'ouverture",
                "name_en": "Opening period",
                "parent": "website-description",
                "is_category": False,
            }
        )
        create_characteristic(
            {
                "identifier": "pricing-textual-description",
                "name_fr": "Tarif en clair",
                "name_en": "Pricing textual description",
                "parent": "website-description",
                "is_category": False,
            }
        )
        create_characteristic(
            {
                "identifier": "additional-pricing-description",
                "name_fr": "Complément de tarif",
                "name_en": "Additional pricing description",
                "parent": "website-description",
                "is_category": False,
            }
        )
        create_characteristic(
            {
                "identifier": "aoc-description",
                "name_fr": "Descriptif AOC",
                "name_en": "AOC description",
                "parent": "website-description",
                "is_category": False,
            }
        )
        create_characteristic(
            {
                "identifier": "equipment-equipment-and-service",
                "name_fr": "Equipements",
                "name_en": "Equipment",
                "parent": "equipment-and-service",
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "service-equipment-and-service",
                "name_fr": "Services",
                "name_en": "Service",
                "parent": "equipment-and-service",
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "service-equipment-and-service-autre",
                "name_fr": "Autres",
                "name_en": "Other",
                "parent": "service-equipment-and-service",
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "equipment-equipment-and-service-autre",
                "name_fr": "Autres",
                "name_en": "Other",
                "parent": "equipment-equipment-and-service",
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "confort-equipment-and-service",
                "name_fr": "Prestation de confort",
                "name_en": "Confort prestation",
                "parent": "equipment-and-service",
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "confort-equipment-and-service-autre",
                "name_fr": "Autres",
                "name_en": "Other",
                "parent": "confort-equipment-and-service",
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "booking-informations",
                "name_fr": "Informations de réservation",
                "name_en": "Booking inforamtions",
                "parent": None,
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "url-booking-address",
                "name_fr": "Url de réservation",
                "name_en": "Booking Url",
                "parent": "booking-informations",
                "is_category": False,
            }
        )
        create_characteristic(
            {
                "identifier": "meal-activity-specialties",
                "name_fr": "Spécialités",
                "name_en": "Specialties",
                "parent": "meal-activity",
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "tasting-activity-type",
                "name_fr": "Type de dégustations",
                "name_en": "Tasting type",
                "parent": "tasting-activity",
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "equipment-activity-type",
                "name_fr": "Type d'équipement",
                "name_en": "Equipement type",
                "parent": "equipment-activity",
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "cultural-heritage-activity-type",
                "name_fr": "Type de patrimoine culturel",
                "name_en": "Cultural heritage type",
                "parent": "cultural-heritage-activity",
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "cultural-heritage-activity-theme",
                "name_fr": "Theme de patrimoine culturel",
                "name_en": "Cultural heritage theme",
                "parent": "cultural-heritage-activity",
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "natural-heritage-activity-type",
                "name_fr": "Type de patrimoine naturel",
                "name_en": "Natural heritage type",
                "parent": "natural-heritage-activity",
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "skiing-resort-activity-type",
                "name_fr": "Type de station de ski",
                "name_en": "Skiing resort type",
                "parent": "skiing-resort-activity",
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "business-and-service-activity-type",
                "name_fr": "Type de commerce et service",
                "name_en": "Business and services type",
                "parent": "business-and-service-activity",
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "business-tourism-category",
                "name_fr": "Tourisme d'affaires",
                "name_en": "Business tourism",
                "parent": None,
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "room-equiped-for",
                "name_fr": "Salle équipée pour",
                "name_en": "Room equiped for",
                "parent": "business-tourism-category",
                "is_category": True,
            }
        )
        create_characteristic(
            {
                "identifier": "typologies-promo-autre",
                "name_fr": "Autres",
                "name_en": "Other",
                "parent": "typologies-promo",
                "is_category": True,
            }
        )

        for dic in [
            characteristics.handmade_characteristics.RESTAURANT_CATEGORY,
            characteristics.handmade_characteristics.RESTAURANT_TYPE,
            characteristics.handmade_characteristics.STRUCTURE_TYPE,
            characteristics.generated_characteristics.RESTAURANT_SPECIALTIES,
            characteristics.generated_characteristics.TASTING_ACTIVITY,
            characteristics.generated_characteristics.EQUIPMENT_ACTIVITY,
            characteristics.generated_characteristics.CULTURAL_HERITAGE_ACTIVITY,
            characteristics.generated_characteristics.NATURAL_HERITAGE_ACTIVITY,
            characteristics.generated_characteristics.BUSINESS_AND_SERVICE_ACTIVITY,
            characteristics.generated_characteristics.SERVICES,
            characteristics.generated_characteristics.EQUIPMENTS,
            characteristics.generated_characteristics.CONFORT_SERVICES,
            characteristics.generated_characteristics.ADAPTED_TOURISM,
            characteristics.generated_characteristics.CULTURAL_ACTIVITY,
            characteristics.generated_characteristics.CULTURAL_HERITAGE_THEME,
            characteristics.generated_characteristics.SPORT_ACTIVITY,
            characteristics.generated_characteristics.PAYMENT_METHOD,
            characteristics.handmade_characteristics.RENTAL_ACCOMMODATION_TYPE,
            characteristics.generated_characteristics.ROOM_EQUIPED_FOR,
            characteristics.generated_characteristics.SKIING_ACTIVITY_TYPE,
            characteristics.generated_characteristics.SKIING_ACTIVITY_CATEGORY,
            characteristics.generated_characteristics.PACK_ACTIVITY_CATEGORY,
            characteristics.generated_characteristics.EVENT_CATEGORIES,
            characteristics.generated_characteristics.EVENT_TYPES,
            characteristics.generated_characteristics.COMMERCES_SERVICES_TYPES,
            characteristics.generated_characteristics.BUSINESS_TOURISM_ACCOMMODATION,
            characteristics.generated_characteristics.BUSINESS_TOURISM_CATERING,
            characteristics.generated_characteristics.BUSINESS_TOURISM_ROOMS_EQUIPMENTS,
            characteristics.generated_characteristics.BUSINESS_TOURISM_ROOMS_LAYOUTS,
            characteristics.generated_characteristics.BUSINESS_TOURISM_ROOMS_USAGE,
            characteristics.generated_characteristics.GROUP_ACCOMMODATION_AGREMENTS,
            characteristics.generated_characteristics.TYPOLOGIES_PROMO_APIDAE,
            characteristics.generated_characteristics.ENVIRONMENT,
            characteristics.generated_characteristics.CUSTOMER_TYPES,
        ]:
            for characteristic in dic.keys():
                create_characteristic(dic[characteristic])

        # Fix a bug with ordered dict that doesnt keep the initial order
        labels_dicts = [
            characteristics.RESTAURANT_RANKING,
            characteristics.HANDMADE_LABELS_1,
            characteristics.LABELS,
        ]

        all_labels_identifiers = []
        for dic in labels_dicts:
            for label in dic.keys():
                create_label(dic[label])
                all_labels_identifiers.append(dic[label]["identifier"])
        purge_labels(all_labels_identifiers)
        logger.info("Caracteristics and touristic labels imported !")


def get_dates_from_weekdays(weekdays, start, end):
    """
    According to http://docs.python.org/library/datetime.html, the weekday value vary from 0(Monday) to 6(Sunday).
    Starting from this premise, this function returns a set of date objects from a set of weekdays values
    and a given period ([dtstart, dtend]).
    """
    # Convert start and end to date objects if necessary
    if not isinstance(start, datetime.date):
        start = datetime.date(start.year, start.month, start.day)
    if not isinstance(end, datetime.date):
        end = datetime.date(end.year, end.month, end.day)
    date_range = (end + datetime.timedelta(days=1) - start).days
    days = [
        (start + datetime.timedelta(days=i))
        for i in range(date_range)
        if (start + datetime.timedelta(days=i)).weekday() in weekdays
    ]

    return days


def get_dates_from_monthdays(monthdays, start, end):
    """
    This function returns a set of datetime objects from a set of monthdays tuples
    and a given period ([dtstart, dtend]).
    """
    # Convert dtstart and dtend to datetimes objects if necessary
    if not isinstance(start, datetime.date):
        start = datetime.date(start.year, start.month, start.day)
    if not isinstance(end, datetime.date):
        end = datetime.date(end.year, end.month, end.day)
    date_range = (end + datetime.timedelta(days=1) - start).days

    days = list()
    for i in range(date_range):
        tmp_date = start + datetime.timedelta(days=i)
        _, last_day = monthrange(tmp_date.year, tmp_date.month)
        # Get the first and last days of this month
        first_date_of_month = tmp_date.replace(day=1)
        last_date_of_month = tmp_date.replace(day=last_day)
        # How many identical weekdays are present before and after this date in this month ?
        l_before = len(
            [
                (first_date_of_month + datetime.timedelta(days=i))
                for i in range(tmp_date.day - 1)
                if (first_date_of_month + datetime.timedelta(days=i)).weekday()
                == tmp_date.weekday()
            ]
        )
        l_after = len(
            [
                (first_date_of_month + datetime.timedelta(days=i))
                for i in range(tmp_date.day + 1, last_date_of_month.day)
                if (first_date_of_month + datetime.timedelta(days=i)).weekday()
                == tmp_date.weekday()
            ]
        )
        # Determines the corresponding monthday tuple
        monthday = (tmp_date.weekday(), l_before)
        if monthday in monthdays:
            days.append(tmp_date)
        if l_after == 0 and (tmp_date.weekday(), None) in monthdays:
            days.append(tmp_date)

    return days


def get_periods_from_dates(dates):
    """
    Given an input list of dates, returns a list of tuples of the form (start date, end date)
    representing the periods of days that are adjacents.
    """
    periods = []
    if dates:
        start_date = previous_date = dates[0]
        for d in dates:
            if (d - previous_date).days > 1:
                periods.append((start_date, previous_date))
                start_date = d
            previous_date = d
        periods.append((start_date, previous_date))
    return periods

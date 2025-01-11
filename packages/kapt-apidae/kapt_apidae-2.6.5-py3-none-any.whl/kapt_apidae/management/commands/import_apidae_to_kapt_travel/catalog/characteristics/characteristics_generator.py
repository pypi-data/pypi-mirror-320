# Standard Library
import inspect
import os

# Third party
from django.utils.text import slugify

# Local application / specific library imports
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.characteristics import (
    HANDMADE_LABELS_1,
    HANDMADE_LABELS_2,
    HANDMADE_RESTAURANT_RANKING,
)
from kapt_apidae.models import BaseElement


label_dict = [
    {
        "queryset": BaseElement.objects.filter(
            type__label__in=["RestaurationClassementGuide", "RestaurationChaine"],
        ).exclude(id__in=HANDMADE_RESTAURANT_RANKING.keys()),
        "dict_key": "GENERATED_RESTAURANT_RANKING",
        "content_type": "MealActivity",
    },
    {
        "queryset": BaseElement.objects.filter(
            type__label__in=[
                "LabelTourismeHandicap",
                "HotelleriePleinAirClassement",
                "HotelleriePleinAirTypeLabel",
                "HebergementLocatifTypeLabel",
                "HebergementCollectifChaineEtLabel",
                "HebergementCollectifTypeLabel",
                "HotellerieTypeLabel",
                "TerritoireZoneLabel",
                "HotellerieLabel",
                "HotellerieChaine",
                "HebergementLocatifLabel",
                "HebergementCollectifLabel",
                "HotelleriePleinAirLabel",
            ],
        )
        .exclude(id__in=HANDMADE_LABELS_1.keys())
        .exclude(id__in=HANDMADE_LABELS_2.keys()),
        "dict_key": "GENERATED_LABELS",
        "content_type": "AccommodationActivity",
    },
]

characteristic_dict = [
    {
        "queryset": BaseElement.objects.filter(type__label="TypeClientele"),
        "dict_key": "CUSTOMER_TYPES",
        "suffix": "-customer-types",
        "parent": "customer-types",
        "family": None,
    },
    {
        "queryset": BaseElement.objects.filter(type__label="Environnement"),
        "dict_key": "ENVIRONMENT",
        "suffix": "-environment",
        "parent": "environment",
        "family": None,
    },
    {
        "queryset": BaseElement.objects.filter(type__label="TypologiePromoSitra"),
        "dict_key": "TYPOLOGIES_PROMO_APIDAE",
        "suffix": "-typologie-promo",
        "parent": "typologies-promo",
        "family": None,
        "handle_parent": True,  # handle hierarchy inside this characteristic category
    },
    {
        "queryset": BaseElement.objects.filter(
            type__label="HebergementCollectifAgrementType"
        ),
        "dict_key": "GROUP_ACCOMMODATION_AGREMENTS",
        "suffix": "",
        "parent": "business-tourism-service-rooms-layouts",
        "family": None,
    },
    {
        "queryset": BaseElement.objects.filter(type__label="SalleDisposition"),
        "dict_key": "BUSINESS_TOURISM_ROOMS_LAYOUTS",
        "suffix": "",
        "parent": "business-tourism-service-rooms-layouts",
        "family": None,
    },
    {
        "queryset": BaseElement.objects.filter(type__label="SalleHebergement"),
        "dict_key": "BUSINESS_TOURISM_ACCOMMODATION",
        "suffix": "",
        "parent": "business-tourism-service-accommodation",
        "family": None,
    },
    {
        "queryset": BaseElement.objects.filter(type__label="SalleRestauration"),
        "dict_key": "BUSINESS_TOURISM_CATERING",
        "suffix": "",
        "parent": "business-tourism-service-catering",
        "family": None,
    },
    {
        "queryset": BaseElement.objects.filter(type__label="SalleEquipeePour"),
        "dict_key": "BUSINESS_TOURISM_ROOMS_USAGE",
        "suffix": "",
        "parent": "business-tourism-service-rooms-usage",
        "family": None,
    },
    {
        "queryset": BaseElement.objects.filter(type__label="SalleEquipement"),
        "dict_key": "BUSINESS_TOURISM_ROOMS_EQUIPMENTS",
        "suffix": "",
        "parent": "business-tourism-service-rooms-equipements",
        "family": None,
    },
    {
        "queryset": BaseElement.objects.filter(type__label="CommerceEtServiceType"),
        "dict_key": "COMMERCES_SERVICES_TYPES",
        "suffix": "",
        "parent": "business-and-service-activity",
        "family": None,
    },
    {
        "queryset": BaseElement.objects.filter(
            type__label="FeteEtManifestationCategorie"
        ),
        "dict_key": "EVENT_CATEGORIES",
        "suffix": "",
        "parent": "event-category",
        "family": None,
    },
    {
        "queryset": BaseElement.objects.filter(type__label="FeteEtManifestationType"),
        "dict_key": "EVENT_TYPES",
        "suffix": "",
        "parent": "event-type",
        "family": None,
    },
    {
        "queryset": BaseElement.objects.filter(type__label="RestaurationSpecialite"),
        "dict_key": "RESTAURANT_SPECIALTIES",
        "suffix": "-meal-activity-specialties",
        "parent": "meal-activity-specialties",
        "family": None,
    },
    {
        "queryset": BaseElement.objects.filter(type__label="DegustationTypeProduit"),
        "dict_key": "TASTING_ACTIVITY",
        "suffix": "-tasting-activity-type",
        "parent": "tasting-activity-type",
        "family": None,
    },
    {
        "queryset": BaseElement.objects.filter(type__label="EquipementActivite"),
        "dict_key": "EQUIPMENT_ACTIVITY",
        "suffix": "-equipment-activity-type",
        "parent": "equipment-activity-type",
        "family": None,
    },
    {
        "queryset": BaseElement.objects.filter(type__label="PatrimoineCulturelType"),
        "dict_key": "CULTURAL_HERITAGE_ACTIVITY",
        "suffix": "-cultural-heritage-activity-type",
        "parent": "cultural-heritage-activity-type",
        "family": None,
    },
    {
        "queryset": BaseElement.objects.filter(type__label="PatrimoineCulturelTheme"),
        "dict_key": "CULTURAL_HERITAGE_THEME",
        "suffix": "-cultural-heritage-activity-theme",
        "parent": "cultural-heritage-activity-theme",
        "family": None,
    },
    {
        "queryset": BaseElement.objects.filter(
            type__label="PatrimoineNaturelCategorie"
        ),
        "dict_key": "NATURAL_HERITAGE_ACTIVITY",
        "suffix": "-natural-heritage-activity-type",
        "parent": "natural-heritage-activity-type",
        "family": None,
    },
    {
        "queryset": BaseElement.objects.filter(
            type__label="DomaineSkiableClassification"
        ),
        "dict_key": "SKIING_ACTIVITY_TYPE",
        "suffix": "-skiing-resort-activity-type",
        "parent": "skiing-resort-activity-type",
        "family": None,
    },
    {
        "queryset": BaseElement.objects.filter(type__label="DomaineSkiableType"),
        "dict_key": "SKIING_ACTIVITY_CATEGORY",
        "suffix": "-skiing-resort-activity",
        "parent": "skiing-resort-activity",
        "family": None,
    },
    {
        "queryset": BaseElement.objects.filter(type__label="ActiviteCategorie"),
        "dict_key": "PACK_ACTIVITY_CATEGORY",
        "suffix": "-pack-activity",
        "parent": "pack-activity",
        "family": None,
    },
    {
        "queryset": BaseElement.objects.filter(
            type__label="CommerceEtServiceTypeDetaille"
        ),
        "dict_key": "BUSINESS_AND_SERVICE_ACTIVITY",
        "suffix": "-business-and-service-activity-type",
        "parent": "business-and-service-activity-type",
        "family": None,
    },
    {
        "queryset": BaseElement.objects.filter(
            type__label="ActiviteSportivePrestation"
        ),
        "dict_key": "SPORT_ACTIVITY",
        "suffix": "-sport-activity",
        "parent": "sport-activity",
        "family": None,
    },
    {
        "queryset": BaseElement.objects.filter(
            type__label="ActiviteCulturellePrestation"
        ),
        "dict_key": "CULTURAL_ACTIVITY",
        "suffix": "-cultural-activity",
        "parent": "cultural-activity",
        "family": None,
    },
    {
        "queryset": BaseElement.objects.filter(type__label="ModePaiement"),
        "dict_key": "PAYMENT_METHOD",
        "suffix": "",
        "parent": "payment-mean",
        "family": None,
    },
    {
        "queryset": BaseElement.objects.filter(type__label="PrestationService"),
        "dict_key": "SERVICES",
        "suffix": "-service",
        "parent": "service-equipment-and-service",
        "family": "full",
    },
    {
        "queryset": BaseElement.objects.filter(type__label="PrestationEquipement"),
        "dict_key": "EQUIPMENTS",
        "suffix": "-equipment",
        "parent": "equipment-equipment-and-service",
        "family": "full",
    },
    {
        "queryset": BaseElement.objects.filter(type__label__in=["PrestationConfort"]),
        "dict_key": "CONFORT_SERVICES",
        "suffix": "-confort",
        "parent": "confort-equipment-and-service",
        "family": "full",
    },
    {
        "queryset": BaseElement.objects.filter(type__label="TourismeAdapte"),
        "dict_key": "ADAPTED_TOURISM",
        "suffix": "-adapted-tourism",
        "parent": "adapted-tourism",
        "family": "full",
    },
    {
        "queryset": BaseElement.objects.filter(type__label="SalleEquipeePour"),
        "dict_key": "ROOM_EQUIPED_FOR",
        "suffix": "",
        "parent": "room-equiped-for",
        "family": "light",
    },
    {
        "queryset": BaseElement.objects.filter(type__label="FamilleCritere"),
        "dict_key": "FAMILY",
        "suffix": "",
        "parent": "confort-equipment-and-service",
        "family": "light",
    },
]


class CharacteristicsGenerator:
    generated_file = "generated_characteristics.py"
    generation_path = None

    def __init__(self, generated_file=None, generation_path=None):
        if generated_file:
            self.generated_file = generated_file
        if generation_path:
            self.generation_path = generation_path
        else:
            self.generation_path = os.path.dirname(os.path.dirname(__file__))
        self.generated_file_path = os.path.join(
            self.generation_path, self.generated_file
        )

    def generate(self):
        generated_file = open(self.generated_file_path, "w")

        generated_file.write("# -*- coding: utf-8 -*-\n")
        generated_file.write("from __future__ import unicode_literals\n")
        generated_file.write("from collections import OrderedDict\n")
        generated_file.write("\n")
        generated_file.write(
            "# The content of this file is generated using import_apidae_kaptravel -c\n"
        )
        generated_file.write("# Any hands edit will be destroyed.\n")
        generated_file.write("# Add hands edit to handmade_characteristics.py file\n")
        generated_file.write("\n")

        generator_methods = inspect.getmembers(self, predicate=inspect.ismethod)
        for method_name, _ in generator_methods:
            if method_name.startswith("getdict_"):
                method_result = getattr(self, method_name)()
                generated_file.write(method_result)
                generated_file.write("\n")

        # Generate CHARACTERISTICS
        for item in characteristic_dict:
            method_result = self.generate_characterisitic(
                queryset=item["queryset"],
                dict_key=item["dict_key"],
                suffix=item["suffix"],
                parent=item["parent"],
                family=item["family"],
                handle_parent=item.get("handle_parent", False),
            )
            generated_file.write(method_result)
            generated_file.write("\n")

        # Generate LABELS
        for item in label_dict:
            method_result = self.generate_label(
                queryset=item["queryset"],
                dict_key=item["dict_key"],
                content_type=item["content_type"],
            )
            generated_file.write(method_result)
            generated_file.write("\n")

        generated_file.close()

    def get_translated_base_element(self, element):
        translated_element = {}
        for lang in ("fr", "en", "es", "it", "de", "nl"):
            translated_element[lang] = getattr(
                element, f"label_{lang}", getattr(element, "label_fr", None)
            )
        return translated_element

    def generate_characterisitic(
        self, queryset, dict_key, suffix, parent, family, handle_parent
    ):
        queryset = queryset.order_by("order")
        dict_as_string = ""
        dict_as_string += "{} = OrderedDict([".format(dict_key)
        for q in queryset:
            for property, value in vars(q).items():
                if "label" in property and value is not None:
                    setattr(q, property, value.replace('"', "'"))
                    if len(value) > 90:
                        setattr(q, property, value[:90] + "...")
            translated_element = self.get_translated_base_element(q)

            # APIDAE families are different from APIDAE parents, but are handled the same way in this script
            if family:
                if q.family_id is not None:
                    family_translated_element = self.get_translated_base_element(
                        q.family
                    )

                    if family == "full":
                        dict_as_string += (
                            '\n   (%d, {"identifier": "%s", "name_fr": "%s", "name_en": "%s", "name_es": "%s", "name_it": "%s", "name_de": "%s", "name_nl": "%s", "parent": "%s", "is_category": True}),'
                            % (
                                q.family_id,
                                slugify(q.family.label_en) + suffix,
                                family_translated_element["fr"],
                                family_translated_element["en"],
                                family_translated_element["es"],
                                family_translated_element["it"],
                                family_translated_element["de"],
                                family_translated_element["nl"],
                                parent,
                            )
                        )

                    dict_as_string += (
                        '\n   (%d, {"identifier": "%s", "name_fr": "%s", "name_en": "%s", "name_es": "%s", "name_it": "%s", "name_de": "%s", "name_nl": "%s", "parent": "%s", "is_category": False}),'
                        % (
                            q.id,
                            slugify(q.label_en),
                            translated_element["fr"],
                            translated_element["en"],
                            translated_element["es"],
                            translated_element["it"],
                            translated_element["de"],
                            translated_element["nl"],
                            slugify(q.family.label_en) + suffix,
                        )
                    )
                else:  # no family
                    if family == "full":
                        dict_as_string += (
                            '\n   (%d, {"identifier": "%s", "name_fr": "%s", "name_en": "%s", "name_es": "%s", "name_it": "%s", "name_de": "%s", "name_nl": "%s", "parent": "%s", "is_category": False}),'
                            % (
                                q.id,
                                slugify(q.label_en),
                                translated_element["fr"],
                                translated_element["en"],
                                translated_element["es"],
                                translated_element["it"],
                                translated_element["de"],
                                translated_element["nl"],
                                parent
                                + "-autre",  # bind this item with a custom "other" parent
                            )
                        )
                    else:
                        dict_as_string += (
                            '\n   (%d, {"identifier": "%s", "name_fr": "%s", "name_en": "%s", "name_es": "%s", "name_it": "%s", "name_de": "%s", "name_nl": "%s", "parent": "%s", "is_category": False}),'
                            % (
                                q.id,
                                slugify(q.label_en),
                                translated_element["fr"],
                                translated_element["en"],
                                translated_element["es"],
                                translated_element["it"],
                                translated_element["de"],
                                translated_element["nl"],
                                parent,
                            )
                        )
            elif handle_parent:
                if q.parent is not None:
                    if q.parent.label_en is None:
                        q.parent.label_en = q.parent.label_fr
                    parent_translated_element = self.get_translated_base_element(
                        q.parent
                    )
                    dict_as_string += (
                        '\n   (%d, {"identifier": "%s", "name_fr": "%s", "name_en": "%s", "name_es": "%s", "name_it": "%s", "name_de": "%s", "name_nl": "%s", "parent": "%s", "is_category": True}),'
                        % (
                            q.parent.id,
                            slugify(q.parent.label_en) + suffix,
                            parent_translated_element["fr"],
                            parent_translated_element["en"],
                            parent_translated_element["es"],
                            parent_translated_element["it"],
                            parent_translated_element["de"],
                            parent_translated_element["nl"],
                            parent,
                        )
                    )
                    dict_as_string += (
                        '\n   (%d, {"identifier": "%s", "name_fr": "%s", "name_en": "%s", "name_es": "%s", "name_it": "%s", "name_de": "%s", "name_nl": "%s", "parent": "%s", "is_category": False}),'
                        % (
                            q.id,
                            slugify(q.label_en) + suffix,
                            translated_element["fr"],
                            translated_element["en"],
                            translated_element["es"],
                            translated_element["it"],
                            translated_element["de"],
                            translated_element["nl"],
                            slugify(q.parent.label_en) + suffix,
                        )
                    )
                else:
                    dict_as_string += (
                        '\n   (%d, {"identifier": "%s", "name_fr": "%s", "name_en": "%s", "name_es": "%s", "name_it": "%s", "name_de": "%s", "name_nl": "%s", "parent": "%s", "is_category": False}),'
                        % (
                            q.id,
                            slugify(q.label_en) + suffix,
                            translated_element["fr"],
                            translated_element["en"],
                            translated_element["es"],
                            translated_element["it"],
                            translated_element["de"],
                            translated_element["nl"],
                            parent + "-autre",
                        )
                    )
            else:
                dict_as_string += (
                    '\n   (%d, {"identifier": "%s", "name_fr": "%s", "name_en": "%s", "name_es": "%s", "name_it": "%s", "name_de": "%s", "name_nl": "%s", "parent": "%s", "is_category": False}),'
                    % (
                        q.id,
                        slugify(q.label_en) + suffix,
                        translated_element["fr"],
                        translated_element["en"],
                        translated_element["es"],
                        translated_element["it"],
                        translated_element["de"],
                        translated_element["nl"],
                        parent,
                    )
                )
        dict_as_string += "\n])"
        return dict_as_string

    def generate_label(self, queryset, dict_key, content_type):
        dict_as_string = ""
        queryset = queryset.order_by("id")
        dict_as_string += "{} = OrderedDict([".format(dict_key)

        for q in queryset:
            translated_element = self.get_translated_base_element(q)
            dict_as_string += (
                '\n   (%d, {"identifier": "%s", "name_fr": "%s", "name_en": "%s", "name_es": "%s", "name_it": "%s", "name_de": "%s", "name_nl": "%s", "content-type": "%s"}),'
                % (
                    q.id,
                    q.id,
                    translated_element["fr"],
                    translated_element["en"],
                    translated_element["es"],
                    translated_element["it"],
                    translated_element["de"],
                    translated_element["nl"],
                    content_type,
                )
            )

        dict_as_string += "\n])"
        return dict_as_string

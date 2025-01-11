# Standard Library
from datetime import datetime
import json

# Third party
import dateutil.parser
from django.core.exceptions import FieldDoesNotExist, ObjectDoesNotExist
from django.utils.timezone import get_default_timezone, make_aware, now

# Local application / specific library imports
import kapt_apidae  # Avoid circular import
import kapt_apidae.models
from kapt_apidae.utils import convert_translated_fields


class UpdateFromDictObject:
    def update_from_dict(self, dictionary, save=True):
        for key, value in dictionary.items():
            setattr(self, key, value)
        if save:
            self.save()


class BaseElementMethods(UpdateFromDictObject):
    def update_from_json(self, base_element_json, save=True):
        # Type and identifier of the base element
        type_label = base_element_json["elementReferenceType"]
        json_identifier = base_element_json["id"]
        base_element_type, _ = kapt_apidae.models.BaseElementType.objects.get_or_create(
            label=type_label
        )
        # We create a dictionary for each object of json file. Optional values are filled with None
        base_element_as_dict = {
            "id": json_identifier,
            "type": base_element_type,
            "order": base_element_json["ordre"]
            if "ordre" in base_element_json
            else 1000,
            "active": base_element_json["actif"],
            "description": base_element_json.get("description", None),
        }

        base_element_as_dict.update(
            convert_translated_fields(base_element_json, "libelle%s", "label_%s")
        )
        if save is True:
            self.update_from_dict(base_element_as_dict)
        else:
            return base_element_as_dict

    def update_foreign_keys_from_json(self, base_element_json):
        base_element_foreign_keys_as_dict = {"parent": None, "family": None}
        parent_json = base_element_json.get("parent", None)
        if parent_json:
            parent_id = parent_json.get("id", None)
            if parent_id:
                try:
                    base_element_foreign_keys_as_dict[
                        "parent"
                    ] = kapt_apidae.models.BaseElement.objects.get(pk=parent_id)
                except ObjectDoesNotExist:
                    pass
        family_json = base_element_json.get("familleCritere", None)
        if family_json:
            family_id = family_json.get("id", None)
            if family_id:
                try:
                    base_element_foreign_keys_as_dict[
                        "family"
                    ] = kapt_apidae.models.BaseElement.objects.get(pk=family_id)
                except ObjectDoesNotExist:
                    pass

        label_type_json = base_element_json.get("typeLabel", None)
        if label_type_json:
            label_type_id = label_type_json.get("id", None)
            if label_type_id:
                if hasattr(self, "label_type"):
                    try:
                        base_element_foreign_keys_as_dict[
                            "label_type"
                        ] = kapt_apidae.models.BaseElement.objects.get(pk=label_type_id)
                    except ObjectDoesNotExist:
                        pass

        self.update_from_dict(base_element_foreign_keys_as_dict)


class SelectionMethods(UpdateFromDictObject):
    def update_from_json(self, selection_json):
        selection_dict = {
            "id": selection_json.get("id"),
            "label": selection_json.get("nom", None),
        }
        self.update_from_dict(selection_dict)
        self.update_fk_and_m2m_from_json(selection_json)

    def update_fk_and_m2m_from_json(self, selection_json):
        self.touristic_objects.clear()
        if "objetsTouristiques" in selection_json:
            touristical_objects_list = selection_json["objetsTouristiques"]
            if touristical_objects_list:
                for touristical_object_json in touristical_objects_list:
                    if "id" in touristical_object_json:
                        touristical_object_id = touristical_object_json["id"]
                        try:
                            touristic_object = (
                                kapt_apidae.models.TouristicObject.objects.get(
                                    apidae_identifier=touristical_object_id,
                                    aspect__isnull=True,
                                )
                            )
                            self.touristic_objects.add(touristic_object)
                        except ObjectDoesNotExist:
                            print(
                                "Warning Touristic object id n° {} not found !".format(
                                    touristical_object_id
                                )
                            )


class TouristicObjectOwnerMethods(UpdateFromDictObject):
    def update_from_json(self, owner_json):
        created_on_json = owner_json.get("dateCreation", None)
        last_update_json = owner_json.get("dateModification", None)

        if created_on_json:
            created_on = dateutil.parser.parse(created_on_json)
        else:
            created_on = None

        if last_update_json:
            last_update = dateutil.parser.parse(last_update_json)
        else:
            last_update = None

        owner_dict = {
            "id": owner_json.get("id", None),
            "type": None,
            "name": owner_json.get("nom", None),
            "department": owner_json.get("departement", None),
            "created_on": created_on,
            "last_update": last_update,
        }
        owner_type = owner_json.get("type", None)
        if owner_type:
            owner_type_id = owner_type.get("id", None)
            if owner_type_id:
                owner_dict["type"] = kapt_apidae.models.BaseElement.objects.get(
                    pk=owner_type_id
                )
        self.update_from_dict(owner_dict)


class CommunicationInfoMethods(UpdateFromDictObject):
    def update_from_json(self, communication_info_json):
        communication_info_dict = {"type": None, "value": None}
        try:
            value = communication_info_json.get("coordonnees", None).get("fr")
            communication_info_dict["value"] = value
        except AttributeError:
            pass
        type_json = communication_info_json.get("type", None)
        if type_json:
            type_id = type_json.get("id", None)
            if type_id:
                type_ = kapt_apidae.models.BaseElement.objects.get(pk=type_id)
                communication_info_dict["type"] = type_
        description_json = communication_info_json.get("observation", None)
        communication_info_dict.update(
            convert_translated_fields(description_json, "libelle%s", "description_%s")
        )
        self.update_from_dict(communication_info_dict)


class CommunicationInfoM2MMethods:
    def update_internal_communications_from_json(self, internal_communications_json):
        model_meta = self._meta
        try:
            # get_field raise FieldDoesNotExist on error
            model_meta.get_field("internal_communications")
            for communcication_object in self.internal_communications.all():
                communcication_object.delete()
            if internal_communications_json:
                for internal_communication_json in internal_communications_json:
                    internal_communication_type_json = internal_communication_json.get(
                        "type", None
                    )
                    if internal_communication_type_json:
                        type_id = internal_communication_type_json.get("id", None)
                        if type_id:
                            communication_info_object = (
                                kapt_apidae.models.CommunicationInfo()
                            )
                            communication_info_object.update_from_json(
                                internal_communication_json
                            )
                            self.internal_communications.add(communication_info_object)
        except FieldDoesNotExist:
            pass

    def update_external_communications_from_json(self, external_communications_json):
        model_meta = self._meta
        try:
            # get_field raise FieldDoesNotExist on error
            model_meta.get_field("external_communications")
            for communcication_object in self.external_communications.all():
                communcication_object.delete()
            if external_communications_json:
                for external_communication_json in external_communications_json:
                    external_communication_type_json = external_communication_json.get(
                        "type", None
                    )
                    if external_communication_type_json:
                        type_id = external_communication_type_json.get("id", None)
                        if type_id:
                            communication_info_object = (
                                kapt_apidae.models.CommunicationInfo()
                            )
                            communication_info_object.update_from_json(
                                external_communication_json
                            )
                            self.external_communications.add(communication_info_object)
        except FieldDoesNotExist:
            pass


class ContactMethods(UpdateFromDictObject, CommunicationInfoM2MMethods):
    def update_from_json(self, contact_json):
        contact_dict = {
            "title": None,
            "first_name": contact_json.get("prenom", None),
            "last_name": contact_json.get("nom", None),
            "function": None,
            "is_referent": contact_json.get("referent", None),
        }

        title_json = contact_json.get("civilite", None)
        if title_json:
            title_id = title_json.get("id", None)
            if title_id:
                contact_dict["title"] = kapt_apidae.models.BaseElement.objects.get(
                    pk=title_id
                )

        function_json = contact_json.get("fonction", None)
        if function_json:
            function_id = function_json.get("id", None)
            if function_id:
                contact_dict["function"] = kapt_apidae.models.BaseElement.objects.get(
                    pk=function_id
                )

        position_json = contact_json.get("titre", None)
        contact_dict.update(
            convert_translated_fields(position_json, "libelle%s", "position_%s")
        )
        self.update_from_dict(contact_dict)

        # M2M
        internal_communications_json = contact_json.get("moyensCommunication", None)
        self.update_internal_communications_from_json(internal_communications_json)


class OpeningPeriodMethods(UpdateFromDictObject):
    def update_from_json(self, opening_period_json):
        opening_period_dict = {
            "beginning": None,
            "ending": None,
            "opening_time": None,
            "closing_time": None,
            "type": None,
            "every_years": opening_period_json.get("tousLesAns", False),
        }

        beginning_json = opening_period_json.get("dateDebut", None)
        ending_json = opening_period_json.get("dateFin", None)
        opening_time = opening_period_json.get("horaireOuverture", None)
        closing_time = opening_period_json.get("horaireFermeture", None)
        type_ = opening_period_json.get("type", None)
        if beginning_json:
            opening_period_dict["beginning"] = dateutil.parser.parse(beginning_json)
        if ending_json:
            opening_period_dict["ending"] = dateutil.parser.parse(ending_json)
        if opening_time:
            opening_period_dict["opening_time"] = dateutil.parser.parse(
                opening_time
            ).time()
        if closing_time:
            opening_period_dict["closing_time"] = dateutil.parser.parse(
                closing_time
            ).time()

        if type_ in kapt_apidae.models.OPENING_PERIOD_TYPE_CHOICES:
            opening_period_dict["type"] = type_

        label_json = opening_period_json.get("nom", None)
        further_hourly_informations_json = opening_period_json.get(
            "complementHoraire", None
        )

        opening_period_dict.update(
            convert_translated_fields(label_json, "libelle%s", "label_%s")
        )
        opening_period_dict.update(
            convert_translated_fields(
                further_hourly_informations_json,
                "libelle%s",
                "further_hourly_informations_%s",
            )
        )

        self.update_from_dict(opening_period_dict)

        # M2M
        self.update_fk_and_m2m_from_json(opening_period_json)

    def update_fk_and_m2m_from_json(self, opening_period_json):
        self.daily_opening.clear()
        daily_opening_json = opening_period_json.get("ouverturesJournalieres", None)
        if daily_opening_json:
            for day_json in daily_opening_json:
                day_name_json = day_json.get("jour", None)
                if day_name_json:
                    (
                        day_object,
                        _,
                    ) = kapt_apidae.models.DayOpeningChoices.objects.get_or_create(
                        day=day_name_json
                    )
                    self.daily_opening.add(day_object)

        self.monthly_opening.clear()
        monthly_opening_json = opening_period_json.get("ouverturesJourDuMois", None)
        if monthly_opening_json:
            for monthday_json in monthly_opening_json:
                day_json = monthday_json.get("jour", None)
                daynumber_json = monthday_json.get("jourDuMois", None)
                if day_json and daynumber_json:
                    monthday_label = "{}_{}".format(daynumber_json, day_json)
                    if (
                        monthday_label
                        in kapt_apidae.models.OPENING_PERIOD_MONTHDAY_CHOICES
                    ):
                        (
                            monthday_object,
                            _,
                        ) = kapt_apidae.models.MonthDayOpeningChoices.objects.get_or_create(
                            monthday=monthday_label
                        )
                        self.monthly_opening.add(monthday_object)

        self.exceptional_opening.all().delete()
        exceptional_opening_json = opening_period_json.get(
            "ouverturesExceptionnelles", None
        )
        if exceptional_opening_json:
            for exceptional_opening_date_json in exceptional_opening_json:
                exceptional_opening_date_value = exceptional_opening_date_json.get(
                    "dateOuverture", None
                )
                if exceptional_opening_date_value:
                    date_value = dateutil.parser.parse(exceptional_opening_date_value)
                    exceptional_opening_date_object = (
                        kapt_apidae.models.ExceptionalOpeningDate(date=date_value)
                    )
                    exceptional_opening_date_object.save()
                    self.exceptional_opening.add(exceptional_opening_date_object)


class PriceDescriptionMethods(UpdateFromDictObject):
    def update_from_json(self, price_description_json):
        price_description_dict = {
            "type": None,
            "minimum_price": price_description_json.get("minimum", None),
            "maximum_price": price_description_json.get("maximum", None),
        }
        type_json = price_description_json.get("type", None)
        if type_json:
            type_id = type_json.get("id", None)
            if type_id:
                price_description_dict["type"] = kapt_apidae.models.BaseElement(
                    pk=type_id
                )

        price_description_dict.update(
            convert_translated_fields(
                price_description_json.get("precisionTarif", None),
                "libelle%s",
                "additionnal_description_%s",
            )
        )
        # Save
        self.update_from_dict(price_description_dict)


class PricingPeriodMethods(UpdateFromDictObject):
    def update_from_json(self, pricing_period_json):
        pricing_period_dict = {"beginning": None, "ending": None}

        beginning_json = pricing_period_json.get("dateDebut", None)
        ending_json = pricing_period_json.get("dateFin", None)

        if beginning_json:
            pricing_period_dict["beginning"] = dateutil.parser.parse(beginning_json)
        if ending_json:
            pricing_period_dict["ending"] = dateutil.parser.parse(ending_json)

        # Save
        self.update_from_dict(pricing_period_dict)
        # M2M
        self.update_fk_and_m2m_from_json(pricing_period_json)

    def update_fk_and_m2m_from_json(self, pricing_period_json):
        self.prices_description.all().delete()
        prices_description_json = pricing_period_json.get("tarifs", None)
        if prices_description_json:
            for price_description_json in prices_description_json:
                price_description_object = kapt_apidae.models.PriceDescription()
                price_description_object.update_from_json(price_description_json)
                self.prices_description.add(price_description_object)


class BookingOrganisationMethods(UpdateFromDictObject, CommunicationInfoM2MMethods):
    def update_from_json(self, booking_organisation_json):
        booking_organisation_dict = {
            "referent_structure": None,
            "name": booking_organisation_json.get("nom", None),
            "type": None,
        }
        referent_structure_json = booking_organisation_json.get(
            "structureReference", None
        )
        if referent_structure_json:
            referent_structure_id = referent_structure_json.get("id", None)
            if referent_structure_id:
                try:
                    referent_structure_object = (
                        kapt_apidae.models.TouristicObject.objects.get(
                            apidae_identifier=referent_structure_id, aspect__isnull=True
                        )
                    )
                    booking_organisation_dict[
                        "referent_structure"
                    ] = referent_structure_object
                except ObjectDoesNotExist:
                    pass

        type_json = booking_organisation_json.get("type", None)
        if type_json:
            type_id = type_json.get("id", None)
            if type_id:
                booking_organisation_dict[
                    "type"
                ] = kapt_apidae.models.BaseElement.objects.get(pk=type_id)
        description_json = booking_organisation_json.get("observation", None)
        booking_organisation_dict.update(
            convert_translated_fields(description_json, "libelle%s", "description_%s")
        )

        self.update_from_dict(booking_organisation_dict)
        internal_communications_json = booking_organisation_json.get(
            "moyensCommunication", None
        )
        external_communications_json = booking_organisation_json.get(
            "moyensCommunicationExternes", None
        )

        self.update_internal_communications_from_json(internal_communications_json)
        self.update_external_communications_from_json(external_communications_json)


class MultimediaFileMethods(UpdateFromDictObject):
    def update_from_json(self, multimedia_file_json):
        modification_date_json = multimedia_file_json.get("lastModifiedDate", None)
        file_locale_json = multimedia_file_json.get("locale", None)

        if modification_date_json:
            modification_date = dateutil.parser.parse(modification_date_json)
        else:
            modification_date = make_aware(datetime.now(), get_default_timezone())

        multimedia_file_dict = {
            "locale": file_locale_json,
            "url": multimedia_file_json.get("url", None),
            "list_url": multimedia_file_json.get("urlListe", None),
            "details_url": multimedia_file_json.get("urlFiche", None),
            "slideshow_url": multimedia_file_json.get("urlDiaporama", None),
            "extension": multimedia_file_json.get("extension", None),
            "file_name": multimedia_file_json.get("fileName", None),
            "size": multimedia_file_json.get("taille", None),
            "height": multimedia_file_json.get("hauteur", None),
            "width": multimedia_file_json.get("largeur", None),
            "modification_date": modification_date,
        }

        if multimedia_file_dict["url"] is not None:
            # Force static APIDAE url to HTTPS
            multimedia_file_dict["url"] = multimedia_file_dict["url"].replace(
                "http://static.apidae-tourisme.com",
                "https://static.apidae-tourisme.com",
            )

        self.update_from_dict(multimedia_file_dict)


class MultimediaMethods(UpdateFromDictObject):
    def update_from_json(self, multimedia_json):
        multimedia_dict = {"type": multimedia_json.get("type", None)}
        name_json = multimedia_json.get("nom", None)
        multimedia_dict.update(
            convert_translated_fields(name_json, "libelle%s", "name_%s")
        )

        legend_json = multimedia_json.get("legende", None)
        multimedia_dict.update(
            convert_translated_fields(legend_json, "libelle%s", "legend_%s")
        )

        copyright_json = multimedia_json.get("copyright", None)
        multimedia_dict.update(
            convert_translated_fields(copyright_json, "libelle%s", "copyright_%s")
        )

        remark_son = multimedia_json.get("observation", None)
        multimedia_dict.update(
            convert_translated_fields(remark_son, "libelle%s", "remark_%s")
        )

        # Save the object in order to add the files
        self.update_from_dict(multimedia_dict)

        # Add, update or delete the Files
        multimedia_files_json = multimedia_json.get("traductionFichiers", None)
        self.update_files_from_json(multimedia_files_json)

    def update_files_from_json(self, multimedia_files_json):
        if multimedia_files_json:
            multimedia_objects_ids = []
            for multimedia_file_json in multimedia_files_json:
                file_locale_json = multimedia_file_json.get("locale", None)
                if file_locale_json:
                    try:
                        multimedia_file_object = self.files.get(locale=file_locale_json)
                    except ObjectDoesNotExist:
                        multimedia_file_object = (
                            kapt_apidae.models.MultimediaFile()
                        )  # Avoid circular import
                    multimedia_file_object.update_from_json(multimedia_file_json)
                    self.files.add(multimedia_file_object)
                    multimedia_objects_ids.append(multimedia_file_object.id)
            # Remove removed files
            self.files.exclude(id__in=multimedia_objects_ids).delete()
        else:
            # If there are no pictures files attached with this object we removed it
            self.delete()


class RoomLayoutMethods(UpdateFromDictObject):
    def update_from_json(self, room_layout_json):
        layout_json = room_layout_json.get("disposition", None)
        room_layout_dict = {
            "capacity": room_layout_json.get("capacite", None),
            "layout": None,
        }

        if layout_json:
            room_layout_id = layout_json.get("id", None)
            room_layout_dict["layout"] = kapt_apidae.models.BaseElement.objects.get(
                pk=room_layout_id
            )

        # Save
        self.update_from_dict(room_layout_dict)


class MeetingRoomMethods(UpdateFromDictObject):
    def update_from_json(self, meeting_room_json):
        meeting_room_dict = {
            "name": meeting_room_json.get("nom", None),
            "max_capacity": meeting_room_json.get("capaciteMax", None),
            "surface_area": meeting_room_json.get("superficie", None),
            "height": meeting_room_json.get("hauteur", None),
            "natural_lighting": meeting_room_json.get("lumiereNaturelle", False),
            "minimum_price": None,
            "maximum_price": None,
            "day_minimum_price": None,
            "day_maximum_price": None,
            "resident_minimum_price": None,
            "resident_maximum_price": None,
        }

        price_json = meeting_room_json.get("tarifSalle", None)
        if price_json:
            minimum_price_json = price_json.get("minimum", None)
            maximum_price_json = price_json.get("maximum", None)
            if minimum_price_json:
                meeting_room_dict["minimum_price"] = minimum_price_json
            if maximum_price_json:
                meeting_room_dict["maximum_price"] = maximum_price_json

        day_price_json = meeting_room_json.get("tarifJournee", None)
        if day_price_json:
            minimum_day_price_json = day_price_json.get("minimum", None)
            maximum_day_price_json = day_price_json.get("maximum", None)
            if minimum_day_price_json:
                meeting_room_dict["day_minimum_price"] = minimum_day_price_json
            if maximum_day_price_json:
                meeting_room_dict["day_maximum_price"] = maximum_day_price_json

        resident_price_json = meeting_room_json.get("tarifResident", None)
        if resident_price_json:
            minimum_resident_price_json = resident_price_json.get("minimum", None)
            maximum_resident_price_json = resident_price_json.get("maximum", None)
            if minimum_resident_price_json:
                meeting_room_dict[
                    "resident_minimum_price"
                ] = minimum_resident_price_json
            if maximum_resident_price_json:
                meeting_room_dict[
                    "resident_maximum_price"
                ] = maximum_resident_price_json

        meeting_room_dict.update(
            convert_translated_fields(
                meeting_room_json.get("description", None),
                "libelle%s",
                "description_%s",
            )
        )

        # Save
        self.update_from_dict(meeting_room_dict)
        # M2M
        self.update_fk_and_m2m_from_json(meeting_room_json)

    def update_fk_and_m2m_from_json(self, meeting_room_json):
        self.layouts.all().delete()

        # Layouts
        room_layouts = meeting_room_json.get("dispositions", None)
        if room_layouts:
            for room_layout_json in room_layouts:
                room_layout_object = kapt_apidae.models.RoomLayout()
                room_layout_object.update_from_json(room_layout_json)
                self.layouts.add(room_layout_object)


class TouristicObjectMethods(UpdateFromDictObject):
    def update_touristic_object_from_json_to_dict(
        self, touristical_object_json, is_linked_object=False, aspect=None
    ):
        # Shall I deport the ForeignKey creation on the same mechanism as M2M creation ?
        # Maybe will be mandatory because we try to get some maybe non-created objects..
        # Please think about it

        touristical_object_dict = {
            "apidae_identifier": touristical_object_json["id"],
            "aspect": aspect,
            "publication_state": touristical_object_json.get("state", None),
            "is_linked_object": is_linked_object,
            "last_import": now(),
        }

        # Label
        label_json = touristical_object_json.get("nom", None)
        touristical_object_dict.update(
            convert_translated_fields(label_json, "libelle%s", "label_%s")
        )

        # Management
        management_dict = {"created_on": None, "last_update": None, "owner": None}

        management_json = touristical_object_json.get("gestion", None)
        if management_json:
            created_on_json = management_json.get("dateCreation", None)
            last_update_json = management_json.get("dateExportModification", None)

            if created_on_json:
                management_dict["created_on"] = dateutil.parser.parse(created_on_json)
            else:
                management_dict["created_on"] = None

            if last_update_json:
                management_dict["last_update"] = dateutil.parser.parse(last_update_json)
            else:
                management_dict["last_update"] = None

            owner_json = management_json.get("membreProprietaire", None)
            if owner_json:
                owner_id = owner_json.get("id", None)
                if owner_id:
                    try:
                        owner_object = (
                            kapt_apidae.models.TouristicObjectOwner.objects.get(
                                id=owner_id
                            )
                        )
                    except ObjectDoesNotExist:
                        owner_object = kapt_apidae.models.TouristicObjectOwner()

                    owner_object.update_from_json(owner_json)
                    management_dict["owner"] = owner_object

        # It's not a good idea to delete TouristicObjectOwner instance because with postgre, if we delete
        # and owner shared with several Touristicobjects, they are all deleted !
        # if old_owner and not management_dict["owner"]:
        # old_owner.delete()

        touristical_object_dict.update(management_dict)

        # Informations
        informations_dict = {
            "siret": None,
            "ape_naf": None,
            "rcs": None,
            "license_authorization_number": None,
            "management_type": None,
            "management_organisation": None,
            "information_organisation": None,
        }

        # old_management_type = self.management_type
        # old_management_organisation = self.management_organisation

        informations_json = touristical_object_json.get("informations", None)
        if informations_json:
            legal_mentions_json = informations_json.get("informationsLegales", None)
            if legal_mentions_json:
                informations_dict["siret"] = legal_mentions_json.get("siret", None)
                informations_dict["ape_naf"] = legal_mentions_json.get(
                    "codeApeNaf", None
                )
                informations_dict["rcs"] = legal_mentions_json.get("rcs", None)
                informations_dict[
                    "license_authorization_number"
                ] = legal_mentions_json.get("numeroAgrementLicence", None)

                management_type_json = legal_mentions_json.get("modeGestion", None)

                if management_type_json:
                    management_type_json_id = management_type_json.get("id", None)
                    management_type_object = kapt_apidae.models.BaseElement.objects.get(
                        pk=management_type_json_id
                    )
                    informations_dict["management_type"] = management_type_object

        touristical_object_dict.update(informations_dict)

        # Presentation
        presentation_json = touristical_object_json.get("presentation", None)

        short_description_json = description_json = good_deal_json = None
        if presentation_json:
            short_description_json = presentation_json.get("descriptifCourt", None)
            description_json = presentation_json.get("descriptifDetaille", None)
            good_deal_json = presentation_json.get("bonsPlans", None)

        # Short description
        touristical_object_dict.update(
            convert_translated_fields(
                short_description_json, "libelle%s", "short_description_%s"
            )
        )

        # Description
        touristical_object_dict.update(
            convert_translated_fields(description_json, "libelle%s", "description_%s")
        )

        # Good deal
        touristical_object_dict.update(
            convert_translated_fields(good_deal_json, "libelle%s", "good_deal_%s")
        )

        # Localization
        access_means_json = None
        localization_dict = {
            "address_1": None,
            "address_2": None,
            "address_3": None,
            "zip_code": None,
            "distribution_office": None,
            "cedex": None,
            "state": None,
            "locality": None,
            "landmark": None,
            "altitude": None,
            "max_altitude": None,
            "min_altitude": None,
            "max_altitude_accommodation": None,
            "min_altitude_accommodation": None,
            "latitude": None,
            "longitude": None,
        }

        localisation_json = touristical_object_json.get("localisation", None)
        if localisation_json:
            address_json = localisation_json.get("adresse", None)

            if address_json:
                localization_dict["address_1"] = address_json.get("adresse1", None)
                localization_dict["address_2"] = address_json.get("adresse2", None)
                localization_dict["address_3"] = address_json.get("adresse3", None)
                localization_dict["zip_code"] = address_json.get("codePostal", None)
                localization_dict["distribution_office"] = address_json.get(
                    "bureauDistribution", None
                )
                localization_dict["cedex"] = address_json.get("cedex", None)
                localization_dict["state"] = address_json.get("etat", None)

                locality_json = address_json.get("commune", None)
                if locality_json:
                    locality_id = locality_json.get("id", None)
                    if locality_id:
                        locality_object = kapt_apidae.models.Locality.objects.get(
                            pk=locality_id
                        )
                        localization_dict["locality"] = locality_object

            geolocalisation_json = localisation_json.get("geolocalisation", None)

            if geolocalisation_json and geolocalisation_json.get("valide", None):
                localization_dict["landmark"] = geolocalisation_json.get(
                    "reperePlan", None
                )
                localization_dict["altitude"] = geolocalisation_json.get(
                    "altitude", None
                )
                localization_dict["max_altitude"] = geolocalisation_json.get(
                    "altitudeMaxi", None
                )
                localization_dict["min_altitude"] = geolocalisation_json.get(
                    "altitudeMini", None
                )
                localization_dict[
                    "max_altitude_accommodation"
                ] = geolocalisation_json.get("altitudeMaxiHebergement", None)
                localization_dict[
                    "min_altitude_accommodation"
                ] = geolocalisation_json.get("altitudeMiniHebergement", None)
                access_means_json = geolocalisation_json.get("complement", None)

                geojson_jon = geolocalisation_json.get("geoJson", None)
                if geojson_jon:
                    coordinates_json = geojson_jon.get("coordinates", None)
                    if coordinates_json:
                        localization_dict["latitude"] = coordinates_json[1]
                        localization_dict["longitude"] = coordinates_json[0]

            # Place
            place_json = localisation_json.get("lieuObjetTouristique", None)
            if place_json is not None:
                localization_dict["place"] = place_json.get("id")

        # Access means
        touristical_object_dict.update(
            convert_translated_fields(access_means_json, "libelle%s", "access_means_%s")
        )

        touristical_object_dict.update(localization_dict)

        # Links description
        links_description_json = None
        links_json = touristical_object_json.get("liens", None)
        if links_json:
            links_description_json = links_json.get("complement", None)
        touristical_object_dict.update(
            convert_translated_fields(
                links_description_json, "libelle%s", "links_description_%s"
            )
        )

        # Services
        services_dict = {
            "group_min_size": None,
            "group_max_size": None,
            "minimum_age": None,
            "maximum_age": None,
            "minimum_age_unit": None,
            "maximum_age_unit": None,
        }

        further_welcoming_informations_json = None
        services_json = touristical_object_json.get("prestations", None)
        if services_json:
            further_welcoming_informations_json = services_json.get(
                "complementAccueil", None
            )

            services_dict["group_min_size"] = services_json.get("tailleGroupeMin", None)
            services_dict["group_max_size"] = services_json.get("tailleGroupeMax", None)
            services_dict["minimum_age"] = services_json.get("ageMin", None)
            services_dict["maximum_age"] = services_json.get("ageMax", None)
            services_dict["minimum_age_unit"] = services_json.get("uniteAgeMin", None)
            services_dict["maximum_age_unit"] = services_json.get("uniteAgeMax", None)
            animal_friendly_ = services_json.get("animauxAcceptes", None)
            if animal_friendly_ in kapt_apidae.models.ANIMAL_FRIENDLY:
                services_dict["animal_friendly"] = animal_friendly_

            animal_friendly_further_informations_ = services_json.get(
                "animauxAcceptesSupplement", None
            )
            if (
                animal_friendly_further_informations_
                in kapt_apidae.models.ANIMAL_FRIENDLY_EXTRA
            ):
                services_dict[
                    "animal_friendly_further_informations"
                ] = animal_friendly_further_informations_

            services_dict["animal_friendly_description"] = services_json.get(
                "descriptifAnimauxAcceptes", None
            )

        touristical_object_dict.update(
            convert_translated_fields(
                further_welcoming_informations_json,
                "libelle%s",
                "further_welcoming_informations_%s",
            )
        )
        touristical_object_dict.update(services_dict)

        # Opening informations
        opening_dict = {"open_all_year": None, "temporarily_closed": None}

        opening_description_json = None
        opening_json = touristical_object_json.get("ouverture", None)
        if opening_json:
            opening_description_json = opening_json.get("periodeEnClair", None)
            opening_dict["open_all_year"] = opening_json.get("ouvertTouteLAnnee", None)
            opening_dict["temporarily_closed"] = opening_json.get(
                "fermeTemporairement", None
            )

        touristical_object_dict.update(
            convert_translated_fields(
                opening_description_json, "libelle%s", "opening_textual_description_%s"
            )
        )
        touristical_object_dict.update(opening_dict)

        # Pricing informations
        pricing_dict = {"is_free": True}

        pricing_textual_description_json = None
        additional_pricing_description_json = None
        pricing_json = touristical_object_json.get("descriptionTarif", None)
        if pricing_json:
            pricing_dict["is_free"] = pricing_json.get("gratuit", True)
            pricing_textual_description_json = pricing_json.get("tarifsEnClair", None)
            additional_pricing_description_json = pricing_json.get("complement", None)

        touristical_object_dict.update(
            convert_translated_fields(
                pricing_textual_description_json,
                "libelle%s",
                "pricing_textual_description_%s",
            )
        )
        touristical_object_dict.update(
            convert_translated_fields(
                additional_pricing_description_json,
                "libelle%s",
                "additional_pricing_description_%s",
            )
        )
        touristical_object_dict.update(pricing_dict)

        # Additional booking informations
        additional_booking_informations_json = None
        booking_json = touristical_object_json.get("reservation", None)
        if booking_json:
            additional_booking_informations_json = booking_json.get("complement", None)
        touristical_object_dict.update(
            convert_translated_fields(
                additional_booking_informations_json,
                "libelle%s",
                "additional_booking_informations_%s",
            )
        )

        # Business tourism
        business_tourism_json = touristical_object_json.get("tourismeAffaires", None)
        business_tourism_dict = {
            "business_tourism_provided": False,
            "equipped_meeting_rooms_quantity": None,
            "business_tourism_max_capacity": None,
            "adjustable_rooms_quantity": None,
        }

        if business_tourism_json:
            business_tourism_dict[
                "business_tourism_provided"
            ] = business_tourism_json.get("tourismeAffairesEnabled", False)
            business_tourism_dict[
                "equipped_meeting_rooms_quantity"
            ] = business_tourism_json.get("nombreSallesReunionEquipees", None)
            business_tourism_dict[
                "business_tourism_max_capacity"
            ] = business_tourism_json.get("capaciteMaxAccueil", None)
            business_tourism_dict[
                "adjustable_rooms_quantity"
            ] = business_tourism_json.get("nombreSallesModulables", None)

        touristical_object_dict.update(business_tourism_dict)

        # Visits
        visits_json = touristical_object_json.get("visites", None)
        additional_visit_informations_json = None
        visits_dict = {
            "is_visitable": False,
            "group_visit_average_time": None,
            "individual_visit_average_time": None,
        }

        if visits_json:
            visits_dict["is_visitable"] = visits_json.get("visitable", False)
            visits_dict["group_visit_average_time"] = visits_json.get(
                "dureeMoyenneVisiteGroupe", None
            )
            visits_dict["individual_visit_average_time"] = visits_json.get(
                "dureeMoyenneVisiteIndividuelle", None
            )
            additional_visit_informations_json = visits_json.get(
                "complementVisite", None
            )

        visits_dict.update(
            convert_translated_fields(
                additional_visit_informations_json,
                "libelle%s",
                "additional_visit_informations_%s",
            )
        )
        touristical_object_dict.update(visits_dict)

        # Meta data
        metadata_json = touristical_object_json.get("metadonnees", None)
        if metadata_json is not None:
            touristical_object_dict.update({"meta_data": json.dumps(metadata_json)})
        else:
            touristical_object_dict.update({"meta_data": None})

        return touristical_object_dict

    def update_touristic_object_fk_and_m2m_from_json(
        self, touristical_object_json, is_linked_object=False
    ):
        # Sports activities
        info_presta_activities_json = touristical_object_json.get(
            "informationsPrestataireActivites", None
        )
        if info_presta_activities_json:
            presta_activity = info_presta_activities_json.get(
                "prestataireActivites", False
            )
            if presta_activity:
                sports_activities_json = info_presta_activities_json.get(
                    "activitesSportives", None
                )
                self.sports_activities.clear()
                if sports_activities_json:
                    for sport_activity_json in sports_activities_json:
                        sport_activity_id = sport_activity_json.get("id", None)
                        if sport_activity_id:
                            sport_activity_object = (
                                kapt_apidae.models.BaseElement.objects.get(
                                    pk=sport_activity_id
                                )
                            )
                            self.sports_activities.add(sport_activity_object)

        # Informations
        informations_json = touristical_object_json.get("informations", None)

        for communication_object in self.internal_communications.all():
            communication_object.delete()

        for communication_object in self.external_communications.all():
            communication_object.delete()

        self.management_organisation = None
        self.information_organisation = None

        if informations_json:
            internal_communications_json = informations_json.get(
                "moyensCommunication", None
            )
            external_communications_json = informations_json.get(
                "moyensCommunicationExternes", None
            )

            if internal_communications_json:
                for internal_communication_json in internal_communications_json:
                    internal_communication_type_json = internal_communication_json.get(
                        "type", None
                    )
                    if internal_communication_type_json:
                        type_id = internal_communication_type_json.get("id", None)
                        if type_id:
                            communication_info_object = (
                                kapt_apidae.models.CommunicationInfo()
                            )
                            communication_info_object.update_from_json(
                                internal_communication_json
                            )
                            self.internal_communications.add(communication_info_object)
            if external_communications_json:
                for external_communication_json in external_communications_json:
                    external_communication_type_json = external_communication_json.get(
                        "type", None
                    )
                    if external_communication_type_json:
                        type_id = external_communication_type_json.get("id", None)
                        if type_id:
                            communication_info_object = (
                                kapt_apidae.models.CommunicationInfo()
                            )
                            communication_info_object.update_from_json(
                                external_communication_json
                            )
                            self.external_communications.add(communication_info_object)

            management_organisation = informations_json.get("structureGestion", None)
            if management_organisation and not is_linked_object:
                management_organisation_id = management_organisation.get("id", None)
                if management_organisation_id:
                    try:
                        management_organisation_object = (
                            kapt_apidae.models.TouristicObject.objects.get(
                                apidae_identifier=management_organisation_id,
                                aspect__isnull=True,
                            )
                        )
                        self.management_organisation = management_organisation_object
                    except ObjectDoesNotExist:
                        pass

            information_organisation = informations_json.get(
                "structureInformation", None
            )
            if information_organisation and not is_linked_object:
                information_organisation_id = information_organisation.get("id", None)
                if information_organisation_id:
                    try:
                        information_organisation_object = (
                            kapt_apidae.models.TouristicObject.objects.get(
                                apidae_identifier=information_organisation_id,
                                aspect__isnull=True,
                            )
                        )
                        self.information_organisation = information_organisation_object
                    except ObjectDoesNotExist:
                        pass

        # Presentation
        presentation_json = touristical_object_json.get("presentation", None)

        if presentation_json:
            # Labels
            offers_labels_json = presentation_json.get("typologiesPromoSitra", None)
            if offers_labels_json:
                offers_labels_ids = []
                for offer_label_json in offers_labels_json:
                    offer_id = offer_label_json.get("id", None)
                    if offer_id:
                        offer_label_object = kapt_apidae.models.BaseElement.objects.get(
                            pk=offer_id
                        )
                        self.offers_labels.add(offer_label_object)
                        offers_labels_ids.append(offer_label_object.id)
                for offer_label_object in self.offers_labels.exclude(
                    id__in=offers_labels_ids
                ):
                    self.offers_labels.remove(offer_label_object)
            else:
                self.offers_labels.clear()

        # Surroundings description
        localisation_json = touristical_object_json.get("localisation", None)
        if localisation_json:
            environment_json = localisation_json.get("environnements", None)
            if environment_json:
                environment_ids = []
                for geographicalelement_json in environment_json:
                    geographicalelement_id = geographicalelement_json.get("id", None)
                    if geographicalelement_id:
                        geographicalelement_object = (
                            kapt_apidae.models.BaseElement.objects.get(
                                pk=geographicalelement_id
                            )
                        )
                        self.environment.add(geographicalelement_object)
                        environment_ids.append(geographicalelement_object.id)
                for geographicalelement_object in self.environment.exclude(
                    id__in=environment_ids
                ):
                    self.environment.remove(geographicalelement_object)
            else:
                self.environment.clear()

            geographical_perimeter_json = localisation_json.get(
                "perimetreGeographique", None
            )
            if geographical_perimeter_json:
                geographical_perimeter_ids = []
                for locality_json in geographical_perimeter_json:
                    locality_id = locality_json.get("id", None)
                    if locality_id:
                        locality_object = kapt_apidae.models.Locality.objects.get(
                            pk=locality_id
                        )
                        self.geographical_perimeter.add(locality_object)
                        geographical_perimeter_ids.append(locality_object.id)
                for locality_object in self.geographical_perimeter.exclude(
                    id__in=geographical_perimeter_ids
                ):
                    self.geographical_perimeter.remove(locality_object)
            else:
                self.geographical_perimeter.clear()

        # Linked objects
        links_json = touristical_object_json.get("liens", None)
        # We clear all linked_objects
        self.linked_objects.clear()
        if links_json and not is_linked_object:
            linked_objects_json = links_json.get("liensObjetsTouristiquesTypes", None)
            if linked_objects_json:
                for linked_object_json in linked_objects_json:
                    linked_touristic_object = linked_object_json.get(
                        "objetTouristique", None
                    )
                    linked_touristic_type = linked_object_json.get("type", None)
                    if linked_touristic_object is not None:
                        link_id = linked_touristic_object.get("id", None)
                        if link_id:
                            try:
                                linked_object = (
                                    kapt_apidae.models.TouristicObject.objects.get(
                                        apidae_identifier=link_id, aspect__isnull=True
                                    )
                                )
                                link_type = kapt_apidae.models.LinkType(
                                    link_type=linked_touristic_type,
                                    touristic_object=self,
                                    touristic_linked_object=linked_object,
                                )
                                link_type.save()
                            except ObjectDoesNotExist:
                                print(
                                    "No TouristicObject found for pk: #{} (it is a linked object of TouristicObject #{})".format(
                                        link_id, self.pk
                                    )
                                )

        # Descriptions
        self.descriptions.all().delete()

        # Private descriptions
        private_descriptions_json = touristical_object_json.get("donneesPrivees", None)
        if private_descriptions_json and not is_linked_object:
            for private_description_json in private_descriptions_json:
                private_description_text = private_description_json.get(
                    "descriptif", None
                )
                private_description_type = private_description_json.get(
                    "nomTechnique", None
                )
                if private_description_type is not None:
                    private_description = kapt_apidae.models.Description(
                        touristic_object=self, label=private_description_type
                    )
                    private_description_text_translations = convert_translated_fields(
                        private_description_text, "libelle%s", "text_%s"
                    )
                    for key in private_description_text_translations:
                        setattr(
                            private_description,
                            key,
                            private_description_text_translations[key],
                        )
                    private_description.save()

        # Thematic descriptions
        presentation_json = touristical_object_json.get("presentation", None)
        if presentation_json:
            thematic_descriptions_json = presentation_json.get(
                "descriptifsThematises", None
            )
            if thematic_descriptions_json and not is_linked_object:
                for thematic_description_json in thematic_descriptions_json:
                    thematic_description_text = thematic_description_json.get(
                        "description", None
                    )
                    thematic_description_type = thematic_description_json.get(
                        "theme", None
                    )
                    if thematic_description_type is not None:
                        theme_id = thematic_description_type.get("id", None)
                        if theme_id:
                            theme = kapt_apidae.models.BaseElement.objects.get(
                                pk=theme_id
                            )
                            thematic_description = kapt_apidae.models.Description(
                                touristic_object=self, label=theme.label, theme=theme
                            )
                            thematic_description_text_translations = (
                                convert_translated_fields(
                                    thematic_description_text, "libelle%s", "text_%s"
                                )
                            )
                            for key in thematic_description_text_translations:
                                setattr(
                                    thematic_description,
                                    key,
                                    thematic_description_text_translations[key],
                                )
                            thematic_description.save()

        # Services
        equipments_json = None
        favours_json = None
        activities_json = None
        comfort_services_json = None
        spoken_languages_json = None
        documentation_languages_json = None
        accessibility_json = None
        accessibility_labels_json = None
        customers_type_json = None

        services_json = touristical_object_json.get("prestations", None)
        if services_json:
            equipments_json = services_json.get("equipements", None)
            favours_json = services_json.get("services", None)
            activities_json = services_json.get("activites", None)
            comfort_services_json = services_json.get("conforts", None)
            spoken_languages_json = services_json.get("languesParlees", None)
            documentation_languages_json = services_json.get(
                "languesDocumentation", None
            )
            accessibility_json = services_json.get("tourismesAdaptes", None)
            accessibility_labels_json = services_json.get(
                "labelsTourismeHandicap", None
            )
            customers_type_json = services_json.get("typesClientele", None)

            equipments_ids = []
            if equipments_json:
                for serviceelement_json in equipments_json:
                    serviceelement_id = serviceelement_json.get("id", None)
                    if serviceelement_id:
                        serviceelement_object = (
                            kapt_apidae.models.BaseElement.objects.get(
                                pk=serviceelement_id
                            )
                        )
                        self.equipments.add(serviceelement_object)
                        equipments_ids.append(serviceelement_object.id)
            for serviceelement_object in self.equipments.exclude(id__in=equipments_ids):
                self.equipments.remove(serviceelement_object)

            favours_ids = []
            if favours_json:
                for serviceelement_json in favours_json:
                    serviceelement_id = serviceelement_json.get("id", None)
                    if serviceelement_id:
                        serviceelement_object = (
                            kapt_apidae.models.BaseElement.objects.get(
                                pk=serviceelement_id
                            )
                        )
                        self.services.add(serviceelement_object)
                        favours_ids.append(serviceelement_object.id)
            for serviceelement_object in self.services.exclude(id__in=favours_ids):
                self.services.remove(serviceelement_object)

            activities_ids = []
            if activities_json:
                for serviceelement_json in activities_json:
                    serviceelement_id = serviceelement_json.get("id", None)
                    if serviceelement_id:
                        serviceelement_object = (
                            kapt_apidae.models.BaseElement.objects.get(
                                pk=serviceelement_id
                            )
                        )
                        self.activities.add(serviceelement_object)
                        activities_ids.append(serviceelement_object.id)
            for serviceelement_object in self.activities.exclude(id__in=activities_ids):
                self.activities.remove(serviceelement_object)

            comfort_services_ids = []
            if comfort_services_json:
                for comfort_service_json in comfort_services_json:
                    comfort_service_id = comfort_service_json.get("id", None)
                    if comfort_service_id:
                        comfort_service_object = (
                            kapt_apidae.models.BaseElement.objects.get(
                                pk=comfort_service_id
                            )
                        )
                        self.comfort_services.add(comfort_service_object)
                        comfort_services_ids.append(comfort_service_object.id)
            for comfort_service_object in self.comfort_services.exclude(
                id__in=comfort_services_ids
            ):
                self.comfort_services.remove(comfort_service_object)

            spoken_languages_ids = []
            if spoken_languages_json:
                for spoken_language_json in spoken_languages_json:
                    spoken_languageelement_id = spoken_language_json.get("id", None)
                    if spoken_languageelement_id:
                        spoken_languageelement_object = (
                            kapt_apidae.models.BaseElement.objects.get(
                                pk=spoken_languageelement_id
                            )
                        )
                        self.spoken_languages.add(spoken_languageelement_object)
                        spoken_languages_ids.append(spoken_languageelement_object.id)
            for spoken_languageelement_object in self.spoken_languages.exclude(
                id__in=spoken_languages_ids
            ):
                self.spoken_languages.remove(spoken_languageelement_object)

            documentation_languages_ids = []
            if documentation_languages_json:
                for documentation_language_json in documentation_languages_json:
                    documentation_languageelement_id = documentation_language_json.get(
                        "id", None
                    )
                    if documentation_languageelement_id:
                        documentation_languageelement_object = (
                            kapt_apidae.models.BaseElement.objects.get(
                                pk=documentation_languageelement_id
                            )
                        )
                        self.documentation_languages.add(
                            documentation_languageelement_object
                        )
                        documentation_languages_ids.append(
                            documentation_languageelement_object.id
                        )
            for (
                documentation_languageelement_object
            ) in self.documentation_languages.exclude(
                id__in=documentation_languages_ids
            ):
                self.documentation_languages.remove(
                    documentation_languageelement_object
                )

            accessibility_ids = []
            if accessibility_json:
                for accessibletourismelement_json in accessibility_json:
                    accessibletourismelement_id = accessibletourismelement_json.get(
                        "id", None
                    )
                    if accessibletourismelement_id:
                        accessibletourismelement_object = (
                            kapt_apidae.models.BaseElement.objects.get(
                                pk=accessibletourismelement_id
                            )
                        )
                        self.accessibility_informations.add(
                            accessibletourismelement_object
                        )
                        accessibility_ids.append(accessibletourismelement_object.id)
            for (
                accessibletourismelement_object
            ) in self.accessibility_informations.exclude(id__in=accessibility_ids):
                self.accessibility_informations.remove(accessibletourismelement_object)

            accessibility_labels_ids = []
            if accessibility_labels_json:
                for accessibletourismelement_json in accessibility_labels_json:
                    accessibletourismelement_id = accessibletourismelement_json.get(
                        "id", None
                    )
                    if accessibletourismelement_id:
                        accessibletourismelement_object = (
                            kapt_apidae.models.BaseElement.objects.get(
                                pk=accessibletourismelement_id
                            )
                        )
                        self.accessibility_labels.add(accessibletourismelement_object)
                        accessibility_labels_ids.append(
                            accessibletourismelement_object.id
                        )
            for accessibletourismelement_object in self.accessibility_labels.exclude(
                id__in=accessibility_labels_ids
            ):
                self.accessibility_labels.remove(accessibletourismelement_object)

            customers_type_ids = []
            if customers_type_json:
                for customer_type_json in customers_type_json:
                    customer_type_id = customer_type_json.get("id", None)
                    if customer_type_id:
                        customer_type_object = (
                            kapt_apidae.models.BaseElement.objects.get(
                                pk=customer_type_id
                            )
                        )
                        self.customers_type.add(customer_type_object)
                        customers_type_ids.append(customer_type_object.id)
            for customer_type_object in self.customers_type.exclude(
                id__in=customers_type_ids
            ):
                self.customers_type.remove(customer_type_object)

        if not services_json or not equipments_json:
            self.equipments.clear()

        if not services_json or not favours_json:
            self.services.clear()

        if not services_json or not activities_json:
            self.activities.clear()

        if not services_json or not comfort_services_json:
            self.comfort_services.clear()

        if not services_json or not spoken_languages_json:
            self.spoken_languages.clear()

        if not services_json or not documentation_languages_json:
            self.documentation_languages.clear()

        if not services_json or not accessibility_json:
            self.accessibility_informations.clear()

        if not services_json or not accessibility_labels_json:
            self.accessibility_labels.clear()

        if not services_json or not customers_type_json:
            self.customers_type.clear()

        # Opening Informations
        self.opening_periods_description.clear()
        self.additional_opening_periods_description.clear()
        for opening_period in self.opening_periods.all():
            opening_period.delete()
        self.exceptional_closure_dates.all().delete()

        opening_json = touristical_object_json.get("ouverture", None)
        if opening_json:
            # Group duration informations
            group_duration_json = opening_json.get("dureeSeanceGroupe", None)
            self.group_duration = group_duration_json

            opening_periods_description_json = opening_json.get(
                "indicationsPeriode", None
            )
            if opening_periods_description_json:
                for opening_period_description_json in opening_periods_description_json:
                    opening_period_description_id = opening_period_description_json.get(
                        "id", None
                    )
                    if opening_period_description_id:
                        opening_period_description_object = (
                            kapt_apidae.models.BaseElement.objects.get(
                                pk=opening_period_description_id
                            )
                        )
                        self.opening_periods_description.add(
                            opening_period_description_object
                        )

            additional_opening_periods_description_json = opening_json.get(
                "ouverturesComplementaires", None
            )
            if additional_opening_periods_description_json:
                for (
                    additional_opening_period_description_json
                ) in additional_opening_periods_description_json:
                    additional_opening_period_description_id = (
                        additional_opening_period_description_json.get("id", None)
                    )
                    if additional_opening_period_description_id:
                        additional_opening_period_description_object = (
                            kapt_apidae.models.BaseElement.objects.get(
                                pk=additional_opening_period_description_id
                            )
                        )
                        self.additional_opening_periods_description.add(
                            additional_opening_period_description_object
                        )

            opening_periods_json = opening_json.get("periodesOuvertures", None)
            if opening_periods_json:
                for opening_period_json in opening_periods_json:
                    opening_period_object = kapt_apidae.models.OpeningPeriod()
                    opening_period_object.update_from_json(opening_period_json)
                    self.opening_periods.add(opening_period_object)

            closing_periods_json = opening_json.get("fermeturesExceptionnelles", None)
            if closing_periods_json:
                for closing_period_json in closing_periods_json:
                    closure_date_value = closing_period_json.get("dateFermeture", None)
                    closure_special_date_value = closing_period_json.get(
                        "dateSpeciale", None
                    )

                    if closure_date_value:
                        closure_date = dateutil.parser.parse(closure_date_value)
                        closure_period_object = kapt_apidae.models.ClosurePeriod(
                            closure_date=closure_date
                        )
                        closure_period_object.save()
                        self.exceptional_closure_dates.add(closure_period_object)
                    if closure_special_date_value:
                        if (
                            closure_special_date_value
                            in kapt_apidae.models.CLOSURE_SPECIAL_DATE
                        ):
                            closure_period_object = kapt_apidae.models.ClosurePeriod(
                                closure_special_date=closure_special_date_value
                            )
                            closure_period_object.save()
                            self.exceptional_closure_dates.add(closure_period_object)

        # Pricing
        self.payment_methods.clear()
        for pricing_period in self.pricing_periods.all():
            pricing_period.delete()

        pricing_json = touristical_object_json.get("descriptionTarif", None)
        if pricing_json:
            # Pricing periods
            pricing_periods_json = pricing_json.get("periodes", None)
            if pricing_periods_json:
                for pricing_period_json in pricing_periods_json:
                    pricing_period_object = kapt_apidae.models.PricingPeriod()
                    pricing_period_object.update_from_json(pricing_period_json)
                    self.pricing_periods.add(pricing_period_object)

            # Payment methods
            payment_methods_json = pricing_json.get("modesPaiement", None)
            if payment_methods_json:
                for payment_method_json in payment_methods_json:
                    payment_method_id = payment_method_json.get("id", None)
                    if payment_method_id:
                        payment_method_object = (
                            kapt_apidae.models.BaseElement.objects.get(
                                pk=payment_method_id
                            )
                        )
                        self.payment_methods.add(payment_method_object)

        # Booking
        # Unfortunately, we can't identify precisely the existing booking centers, we have to remove all of them before creating them back...
        for booking_organisation in self.booking_organisations.all():
            booking_organisation.delete()

        booking_json = touristical_object_json.get("reservation", None)
        if booking_json:
            booking_organisations_objects_json = booking_json.get("organismes", None)
            if booking_organisations_objects_json:
                for (
                    booking_organisation_object_json
                ) in booking_organisations_objects_json:
                    bookingorganisation_object = (
                        kapt_apidae.models.BookingOrganisation()
                    )
                    bookingorganisation_object.update_from_json(
                        booking_organisation_object_json
                    )
                    self.booking_organisations.add(bookingorganisation_object)

        # Variable attributes
        variable_attributes_json = touristical_object_json.get("criteresInternes", None)
        if variable_attributes_json:
            variable_attributes_ids = []
            for variable_attribute_json in variable_attributes_json:
                variable_attribute_id = variable_attribute_json.get("id", None)
                if variable_attribute_id:
                    variable_attribute_object = (
                        kapt_apidae.models.VariableAttribute.objects.get(
                            pk=variable_attribute_id
                        )
                    )
                    self.variable_attributes.add(variable_attribute_object)
                    variable_attributes_ids.append(variable_attribute_object.id)
            for variable_attribute_object in self.variable_attributes.exclude(
                id__in=variable_attributes_ids
            ):
                self.variable_attributes.remove(variable_attribute_object)
        else:
            self.variable_attributes.clear()

        # Contacts
        contacts_json = touristical_object_json.get("contacts", None)
        if contacts_json:
            contacts_ids = []
            for contact_json in contacts_json:
                contact_function_json = contact_json.get("fonction", None)
                if contact_function_json:
                    contact_function_id_json = contact_function_json.get("id", None)
                    try:
                        contact_object = self.internal_contacts.get(
                            function_id=contact_function_id_json
                        )
                    except ObjectDoesNotExist:
                        contact_object = kapt_apidae.models.Contact()
                    contact_object.update_from_json(contact_json)
                    self.internal_contacts.add(contact_object)
                    contacts_ids.append(contact_object.id)
            for contact_object in self.internal_contacts.exclude(id__in=contacts_ids):
                self.internal_contacts.remove(contact_object)
                contact_object.delete()
        else:
            for contact in self.internal_contacts.all():
                contact.delete()

        external_contacts_json = touristical_object_json.get("contactsExternes", None)
        if external_contacts_json:
            external_contacts_ids = []
            for external_contact_json in external_contacts_json:
                external_contact_json = external_contact_json.get("contact", None)
                if external_contact_json:
                    external_contact_function_json = external_contact_json.get(
                        "fonction", None
                    )

                    if external_contact_function_json:
                        external_contact_function_id_json = (
                            external_contact_function_json.get("id", None)
                        )
                        try:
                            external_contact_object = self.external_contacts.get(
                                function_id=external_contact_function_id_json
                            )
                        except ObjectDoesNotExist:
                            external_contact_object = kapt_apidae.models.Contact()
                        external_contact_object.update_from_json(external_contact_json)
                        self.external_contacts.add(external_contact_object)
                        external_contacts_ids.append(external_contact_object.id)
            for external_contact in self.external_contacts.exclude(
                id__in=external_contacts_ids
            ):
                self.external_contacts.remove(external_contact)
                external_contact.delete()
        else:
            for contact in self.external_contacts.all():
                contact.delete()

        # Pictures
        # We can't retrieve old files because ITEA doesn't fill fields properly, so we remove all pictures and re-import them

        # Delete
        for picture_object in self.pictures.all():
            self.pictures.remove(picture_object)
            picture_object.delete()

        # Re-create
        pictures_json = touristical_object_json.get("illustrations", None)
        if pictures_json:
            for picture_json in pictures_json:
                files_list_json = picture_json.get("traductionFichiers", None)
                if files_list_json and len(files_list_json) > 0:
                    picture_object = kapt_apidae.models.Multimedia()
                    picture_object.update_from_json(picture_json)
                    self.pictures.add(picture_object)

        # Links
        links_json = touristical_object_json.get("multimedias", None)
        for link in self.links.all():
            link.delete()
        if links_json:
            for link_json in links_json:
                # is_link = link_json.get("link", None)
                link_object = kapt_apidae.models.Multimedia()
                link_object.update_from_json(link_json)
                self.links.add(link_object)

        # Business tourism
        self.business_tourism_rooms_equipped_for.clear()
        self.business_tourism_rooms_equipments.clear()
        self.catering_rooms.clear()
        self.accommodation_rooms.clear()
        for meeting_room in self.meeting_rooms.all():
            meeting_room.delete()

        business_tourism_json = touristical_object_json.get("tourismeAffaires", None)
        if business_tourism_json:
            # Rooms equipped for
            business_tourism_rooms_equipped_for_json = business_tourism_json.get(
                "sallesEquipeesPour", None
            )
            if business_tourism_rooms_equipped_for_json:
                for equipped_for_json in business_tourism_rooms_equipped_for_json:
                    equipped_for_id = equipped_for_json.get("id", None)
                    if equipped_for_id:
                        business_tourism_rooms_equipped_for_object = (
                            kapt_apidae.models.BaseElement.objects.get(
                                pk=equipped_for_id
                            )
                        )
                        self.business_tourism_rooms_equipped_for.add(
                            business_tourism_rooms_equipped_for_object
                        )

            # Rooms equipments
            business_tourism_rooms_equipments_json = business_tourism_json.get(
                "sallesEquipement", None
            )
            if business_tourism_rooms_equipments_json:
                for room_equipment_json in business_tourism_rooms_equipments_json:
                    room_equipment_id = room_equipment_json.get("id", None)
                    if room_equipment_id:
                        business_tourism_room_equipment_object = (
                            kapt_apidae.models.BaseElement.objects.get(
                                pk=room_equipment_id
                            )
                        )
                        self.business_tourism_rooms_equipments.add(
                            business_tourism_room_equipment_object
                        )

            # Catering rooms
            catering_rooms_json = business_tourism_json.get("sallesRestauration", None)
            if catering_rooms_json:
                for catering_room_json in catering_rooms_json:
                    catering_room_id = catering_room_json.get("id", None)
                    if catering_room_id:
                        catering_room_object = (
                            kapt_apidae.models.BaseElement.objects.get(
                                pk=catering_room_id
                            )
                        )
                        self.catering_rooms.add(catering_room_object)

            # Accommodation rooms
            accommodation_rooms_json = business_tourism_json.get(
                "sallesHebergement", None
            )
            if accommodation_rooms_json:
                for accommodation_room_json in accommodation_rooms_json:
                    accommodation_room_id = accommodation_room_json.get("id", None)
                    if accommodation_room_id:
                        accommodation_room_object = (
                            kapt_apidae.models.BaseElement.objects.get(
                                pk=accommodation_room_id
                            )
                        )
                        self.accommodation_rooms.add(accommodation_room_object)

            meeting_rooms_json = business_tourism_json.get("sallesReunion", None)
            if meeting_rooms_json:
                for meeting_room_json in meeting_rooms_json:
                    meeting_room_object = kapt_apidae.models.MeetingRoom()
                    meeting_room_object.update_from_json(meeting_room_json)
                    self.meeting_rooms.add(meeting_room_object)

        # Visits
        visits_json = touristical_object_json.get("visites", None)
        self.visit_languages.clear()
        self.audio_guide_languages.clear()
        self.information_panels_languages.clear()
        self.individual_visit_services.clear()
        self.group_visit_services.clear()

        if visits_json:
            # Visit languages
            visit_languages_json = visits_json.get("languesVisite", None)
            if visit_languages_json:
                for visit_language_json in visit_languages_json:
                    visit_language_id = visit_language_json.get("id", None)
                    if visit_language_id:
                        visit_language_object = (
                            kapt_apidae.models.BaseElement.objects.get(
                                pk=visit_language_id
                            )
                        )
                        self.visit_languages.add(visit_language_object)

            # Audioguide languages
            audio_guide_languages_json = visits_json.get("languesAudioGuide", None)
            if audio_guide_languages_json:
                for audio_guide_language_json in audio_guide_languages_json:
                    audio_guide_language_id = audio_guide_language_json.get("id", None)
                    if audio_guide_language_id:
                        audio_guide_object = kapt_apidae.models.BaseElement.objects.get(
                            pk=audio_guide_language_id
                        )
                        self.audio_guide_languages.add(audio_guide_object)

            # Information panels languages
            information_panels_languages_json = visits_json.get(
                "languesPanneauInformation", None
            )
            if information_panels_languages_json:
                for (
                    information_panels_language_json
                ) in information_panels_languages_json:
                    information_panels_language_id = (
                        information_panels_language_json.get("id", None)
                    )
                    if information_panels_language_id:
                        information_panels_language_object = (
                            kapt_apidae.models.BaseElement.objects.get(
                                pk=information_panels_language_id
                            )
                        )
                        self.information_panels_languages.add(
                            information_panels_language_object
                        )

            # Individual visit services
            individual_visit_services_json = visits_json.get(
                "prestationsVisitesIndividuelles", None
            )
            if individual_visit_services_json:
                for individual_visit_service_json in individual_visit_services_json:
                    individual_visit_service_id = individual_visit_service_json.get(
                        "id", None
                    )
                    if individual_visit_service_id:
                        individual_visit_service_object = (
                            kapt_apidae.models.BaseElement.objects.get(
                                pk=individual_visit_service_id
                            )
                        )
                        self.individual_visit_services.add(
                            individual_visit_service_object
                        )

            # Group visit services
            group_visit_services_json = visits_json.get(
                "prestationsVisitesGroupees", None
            )
            if group_visit_services_json:
                for group_visit_service_json in group_visit_services_json:
                    group_visit_service_id = group_visit_service_json.get("id", None)
                    if group_visit_service_id:
                        group_visit_service_object = (
                            kapt_apidae.models.BaseElement.objects.get(
                                pk=group_visit_service_id
                            )
                        )
                        self.group_visit_services.add(group_visit_service_object)

        # Areas
        areas_json = touristical_object_json.get("territoires", None)
        self.areas.clear()
        if areas_json:
            for area_json in areas_json:
                area_id = area_json.get("id", None)
                if area_id:
                    area_object = kapt_apidae.models.Area.objects.filter(
                        apidae_identifier=area_id
                    ).first()
                    self.areas.add(area_object)

        self.save()

    def delete_touristic_object_childs(self, *args, **kwargs):
        print("delete childs of %d" % self.id)
        # Delete owner
        self.owner.delete()
        # Communication infos
        print(self.internal_communications.all())
        for communication_object in self.internal_communications.all():
            communication_object.delete()

        for communication_object in self.external_communications.all():
            communication_object.delete()


class AreaMethods:
    def update_from_json(self, area_json, is_linked_object=False, aspect=None):
        # Area specific part
        area_specific_data_json = area_json.get("informationsTerritoire", None)

        # We need to differentiate between a short and long version of area object to retrive the type
        if area_specific_data_json:
            area_type = area_specific_data_json.get("territoireType", None)
        else:
            area_type = area_json.get("territoireType", None)

        area_dict = {
            "type": None,
            "is_destination": None,
            "shops_quantity": None,
            "restaurants_quantity": None,
            "snowshoes_trail_quantity": None,
            "snowshoes_trail_kilometers": None,
            "pedestrian_route_quantity": None,
            "pedestrian_route_kilometers": None,
            "minimum_age_ski_teaching": None,
            "kindergarten_age_groups": None,
            "camper_van_car_park": None,
            "campsite_quantity": None,
            "tourism_residences_quantity": None,
            "holiday_resorts_quantity": None,
            "snow_caravans_quantity": None,
            "ranked_resting_places_quantity": None,
            "non_classified_hotels_quantity": None,
            "no_stars_hotels_quantity": None,
            "one_star_hotels_quantity": None,
            "two_star_hotels_quantity": None,
            "three_star_hotels_quantity": None,
            "four_star_hotels_quantity": None,
            "five_star_hotels_quantity": None,
            "four_star_luxury_hotels_quantity": None,
        }

        if area_type:
            type_id = area_type.get("id", None)
            if type_id:
                area_dict["type"] = kapt_apidae.models.BaseElement.objects.get(
                    pk=type_id
                )

        minimum_age_ski_teaching_json = None
        kindergarten_age_groups_json = None
        resting_places_description_json = None
        accommodations_description_json = None

        if area_specific_data_json:
            area_dict["is_destination"] = area_specific_data_json.get(
                "destination", None
            )
            area_dict["shops_quantity"] = area_specific_data_json.get(
                "nombreCommerces", None
            )
            area_dict["restaurants_quantity"] = area_specific_data_json.get(
                "nombreRestaurants", None
            )

            winter_sports_json = area_specific_data_json.get("sportsHiver", None)
            if winter_sports_json:
                area_dict["snowshoes_trail_quantity"] = area_specific_data_json.get(
                    "nombreItinerairesRaquettes", None
                )
                area_dict["snowshoes_trail_kilometers"] = area_specific_data_json.get(
                    "nombreKilometresItinerairesRaquettes", None
                )
                area_dict["pedestrian_route_quantity"] = area_specific_data_json.get(
                    "nombreItinerairesPietons", None
                )
                area_dict["pedestrian_route_kilometers"] = area_specific_data_json.get(
                    "nombreKilometresItinerairesPietons", None
                )
                minimum_age_ski_teaching_json = area_specific_data_json.get(
                    "ageMinimumEnseignementSki", None
                )
                kindergarten_age_groups_json = area_specific_data_json.get(
                    "trancheAgeAccueilEnfantGarderie", None
                )

            accommodation_json = area_specific_data_json.get("hebergement", None)
            if accommodation_json:
                area_dict["camper_van_car_park"] = accommodation_json.get(
                    "parkingCampingCar", None
                )
                area_dict["campsite_quantity"] = area_specific_data_json.get(
                    "nombreCampings", None
                )
                area_dict["tourism_residences_quantity"] = area_specific_data_json.get(
                    "nombreResidencesTourisme", None
                )
                area_dict["holiday_resorts_quantity"] = area_specific_data_json.get(
                    "nombreVillagesVacances", None
                )
                area_dict["snow_caravans_quantity"] = area_specific_data_json.get(
                    "nombreCaravaneiges", None
                )
                area_dict[
                    "ranked_resting_places_quantity"
                ] = area_specific_data_json.get("nombreMeublesClasses", None)
                area_dict[
                    "non_classified_hotels_quantity"
                ] = area_specific_data_json.get("nombreHotelsNonClasses", None)
                area_dict["no_stars_hotels_quantity"] = area_specific_data_json.get(
                    "nombreHotelsSansEtoile", None
                )
                area_dict["one_star_hotels_quantity"] = area_specific_data_json.get(
                    "nombreHotelsUneEtoile", None
                )
                area_dict["two_star_hotels_quantity"] = area_specific_data_json.get(
                    "nombreHotelsDeuxEtoiles", None
                )
                area_dict["three_star_hotels_quantity"] = area_specific_data_json.get(
                    "nombreHotelsTroisEtoiles", None
                )
                area_dict["four_star_hotels_quantity"] = area_specific_data_json.get(
                    "nombreHotelsQuatreEtoiles", None
                )
                area_dict["five_star_hotels_quantity"] = area_specific_data_json.get(
                    "nombreHotelsCinqEtoiles", None
                )
                area_dict[
                    "four_star_luxury_hotels_quantity"
                ] = area_specific_data_json.get("nombreHotelsQuatreEtoilesLuxe", None)
                resting_places_description_json = area_specific_data_json.get(
                    "descriptifMeubles", None
                )
                accommodations_description_json = area_specific_data_json.get(
                    "descriptifAutres", None
                )

        area_dict.update(
            convert_translated_fields(
                minimum_age_ski_teaching_json,
                "libelle%s",
                "minimum_age_ski_teaching_%s",
            )
        )
        area_dict.update(
            convert_translated_fields(
                kindergarten_age_groups_json, "libelle%s", "kindergarten_age_groups_%s"
            )
        )
        area_dict.update(
            convert_translated_fields(
                resting_places_description_json,
                "libelle%s",
                "resting_places_description_%s",
            )
        )
        area_dict.update(
            convert_translated_fields(
                accommodations_description_json,
                "libelle%s",
                "accommodations_description_%s",
            )
        )

        # Common fields
        touristical_object_dict = self.update_touristic_object_from_json_to_dict(
            area_json, is_linked_object, aspect=aspect
        )
        area_dict.update(touristical_object_dict)

        # Save object
        self.update_from_dict(area_dict)

    def update_fk_and_m2m_from_json(self, area_json, is_linked_object=False):
        self.update_touristic_object_fk_and_m2m_from_json(area_json, is_linked_object)

        # Area specific part
        area_specific_data_json = area_json.get("informationsTerritoire", None)

        if area_specific_data_json:
            # Labels
            labels_json = area_specific_data_json.get("zoneLabels", None)
            self.labels.clear()
            if labels_json:
                for label_json in labels_json:
                    label_id = label_json.get("id", None)
                    if label_id:
                        label_object = kapt_apidae.models.BaseElement.objects.get(
                            pk=label_id
                        )
                        self.labels.add(label_object)

            # Rankings
            rankings_json = area_specific_data_json.get("zoneClassements", None)
            self.rankings.clear()
            if rankings_json:
                for ranking_json in rankings_json:
                    ranking_id = ranking_json.get("id", None)
                    if ranking_id:
                        ranking_object = kapt_apidae.models.BaseElement.objects.get(
                            pk=ranking_id
                        )
                        self.rankings.add(ranking_object)

            # Ski resorts
            self.ski_resorts_types.clear()
            self.linked_ski_resorts.clear()
            winter_sports_json = area_specific_data_json.get("sportsHiver", None)

            if winter_sports_json:
                # Types
                ski_resorts_types_json = winter_sports_json.get("typesStation", None)
                if ski_resorts_types_json:
                    for ski_resorts_type_json in ski_resorts_types_json:
                        ski_resorts_type_id = ski_resorts_type_json.get("id", None)
                        ski_resorts_type_object = (
                            kapt_apidae.models.BaseElement.objects.get(
                                pk=ski_resorts_type_id
                            )
                        )
                        self.ski_resorts_types.add(ski_resorts_type_object)

                # Linked ressorts
                linked_ski_ressorts_json = winter_sports_json.get("domaines", None)
                if linked_ski_ressorts_json:
                    for linked_ski_ressort_json in linked_ski_ressorts_json:
                        linked_ski_ressort_object_json = linked_ski_ressort_json.get(
                            "objetTouristique", None
                        )
                        if linked_ski_ressort_object_json and not is_linked_object:
                            linked_ski_ressort_id = linked_ski_ressort_object_json.get(
                                "id", None
                            )
                            try:
                                ski_resorts_type_object = (
                                    kapt_apidae.models.TouristicObject.objects.get(
                                        apidae_identifier=linked_ski_ressort_id,
                                        aspect__isnull=True,
                                    )
                                )
                                self.linked_ski_resorts.add(ski_resorts_type_object)
                            except ObjectDoesNotExist:
                                pass


class StructureMethods:
    def update_from_json(self, structure_json, is_linked_object=False, aspect=None):
        # Structure specific part
        structure_specific_data_json = structure_json.get("informationsStructure", None)

        structure_dict = {"type": None}

        if structure_specific_data_json:
            structure_type_json = structure_specific_data_json.get("entiteType", None)

            if structure_type_json:
                structure_type_id = structure_type_json.get("id", None)

                if structure_type_id:
                    structure_type_object = kapt_apidae.models.BaseElement.objects.get(
                        pk=structure_type_id
                    )
                    structure_dict["type"] = structure_type_object

        # Common fields
        touristical_object_dict = self.update_touristic_object_from_json_to_dict(
            structure_json, is_linked_object, aspect=aspect
        )
        structure_dict.update(touristical_object_dict)

        # Save object
        self.update_from_dict(structure_dict)

    def update_fk_and_m2m_from_json(self, structure_json, is_linked_object=False):
        self.update_touristic_object_fk_and_m2m_from_json(
            structure_json, is_linked_object
        )

        # Structure specific part
        # structure_specific_data_json = structure_json.get("informationsStructure", None)


class AllInclusiveTripMethods:
    def update_from_json(
        self, all_inclusive_trip_json, is_linked_object=False, aspect=None
    ):
        # All inclusive specific part
        all_inclusive_specific_data_json = all_inclusive_trip_json.get(
            "informationsSejourPackage", None
        )

        all_inclusive_trip_dict = {
            "days_quantity": all_inclusive_specific_data_json.get("nombreJours", None),
            "nights_quantity": all_inclusive_specific_data_json.get(
                "nombreNuits", None
            ),
        }

        all_inclusive_trip_dict.update(
            convert_translated_fields(
                all_inclusive_specific_data_json.get("lieuDePratique", None),
                "libelle%s",
                "location_description_%s",
            )
        )
        all_inclusive_trip_dict.update(
            convert_translated_fields(
                all_inclusive_specific_data_json.get("accommodation_description", None),
                "libelle%s",
                "accommodation_description_%s",
            )
        )

        # Common fields
        touristical_object_dict = self.update_touristic_object_from_json_to_dict(
            all_inclusive_trip_json, is_linked_object, aspect=aspect
        )
        all_inclusive_trip_dict.update(touristical_object_dict)

        # Save object
        self.update_from_dict(all_inclusive_trip_dict)

    def update_fk_and_m2m_from_json(
        self, all_inclusive_trip_json, is_linked_object=False
    ):
        self.update_touristic_object_fk_and_m2m_from_json(
            all_inclusive_trip_json, is_linked_object
        )

        # All inclusive specific part
        all_inclusive_specific_data_json = all_inclusive_trip_json.get(
            "informationsSejourPackage", None
        )

        # Accommodation types
        accommodations_types_json = all_inclusive_specific_data_json.get(
            "typesHebergement", None
        )
        self.accommodations_types.clear()
        if accommodations_types_json:
            for accommodation_type_json in accommodations_types_json:
                accommodation_type_id = accommodation_type_json.get("id", None)
                if accommodation_type_id:
                    accommodation_type_object = (
                        kapt_apidae.models.BaseElement.objects.get(
                            pk=accommodation_type_id
                        )
                    )
                    self.accommodations_types.add(accommodation_type_object)

        # Transports types
        transports_types_json = all_inclusive_specific_data_json.get("transports", None)
        self.transports_types.clear()
        if transports_types_json:
            for transport_type_json in transports_types_json:
                transport_type_id = transport_type_json.get("id", None)
                if transport_type_id:
                    transport_type_object = kapt_apidae.models.BaseElement.objects.get(
                        pk=transport_type_id
                    )
                    self.transports_types.add(transport_type_object)

        # Activity category
        activities_category_json = all_inclusive_specific_data_json.get(
            "activiteCategories", None
        )
        self.activities_category.clear()
        if activities_category_json:
            for activity_category_json in activities_category_json:
                activity_category_id = activity_category_json.get("id", None)
                if activity_category_id:
                    activity_category_object = (
                        kapt_apidae.models.BaseElement.objects.get(
                            pk=activity_category_id
                        )
                    )
                    self.activities_category.add(activity_category_object)

        # Sports activities
        sports_activities_json = all_inclusive_specific_data_json.get(
            "activitesSportives", None
        )
        self.sports_activities.clear()
        if sports_activities_json:
            for sport_activity_json in sports_activities_json:
                sport_activity_id = sport_activity_json.get("id", None)
                if sport_activity_id:
                    sport_activity_object = kapt_apidae.models.BaseElement.objects.get(
                        pk=sport_activity_id
                    )
                    self.sports_activities.add(sport_activity_object)

        # Cultural activities
        curtural_activities_json = all_inclusive_specific_data_json.get(
            "activitesCulturelles", None
        )
        self.curtural_activities.clear()
        if curtural_activities_json:
            for curtural_activity_json in curtural_activities_json:
                curtural_activity_id = curtural_activity_json.get("id", None)
                if curtural_activity_id:
                    curtural_activity_object = (
                        kapt_apidae.models.BaseElement.objects.get(
                            pk=curtural_activity_id
                        )
                    )
                    self.curtural_activities.add(curtural_activity_object)


class RestaurantMethods:
    def update_from_json(self, restaurant_json, is_linked_object=False, aspect=None):
        # Restaurant specific part
        restaurant_specific_data_json = restaurant_json.get(
            "informationsRestauration", None
        )

        restaurant_dict = {
            "chef_name": None,
            "brand": None,
            "type": None,
            "ranking": None,
            "rooms_quantity": None,
            "air_conditioned_rooms_quantity": None,
            "maximum_capacity": None,
            "patio_capacity": None,
        }

        rooms_description_json = None
        if restaurant_specific_data_json:
            restaurant_dict["chef_name"] = restaurant_specific_data_json.get(
                "chef", None
            )
            restaurant_dict["brand"] = restaurant_specific_data_json.get("label", None)

            restaurant_type_json = restaurant_specific_data_json.get(
                "restaurationType", None
            )
            if restaurant_type_json:
                restaurant_type_id = restaurant_type_json.get("id", None)
                if restaurant_type_id:
                    restaurant_dict[
                        "type"
                    ] = kapt_apidae.models.BaseElement.objects.get(
                        pk=restaurant_type_id
                    )

            restaurant_ranking_json = restaurant_specific_data_json.get(
                "classement", None
            )
            if restaurant_ranking_json:
                restaurant_ranking_id = restaurant_ranking_json.get("id", None)
                if restaurant_ranking_id:
                    restaurant_dict[
                        "ranking"
                    ] = kapt_apidae.models.BaseElement.objects.get(
                        pk=restaurant_ranking_id
                    )

            capacity_json = restaurant_specific_data_json.get("capacite", None)
            if capacity_json:
                rooms_description_json = capacity_json.get("descriptionSalles", None)
                restaurant_dict["rooms_quantity"] = capacity_json.get(
                    "nombreSalles", None
                )
                restaurant_dict["air_conditioned_rooms_quantity"] = capacity_json.get(
                    "nombreSallesClimatisees", None
                )
                restaurant_dict["maximum_capacity"] = capacity_json.get(
                    "nombreMaximumCouverts", None
                )
                restaurant_dict["patio_capacity"] = capacity_json.get(
                    "nombreCouvertsTerrasse", None
                )

        restaurant_dict.update(
            convert_translated_fields(
                rooms_description_json, "libelle%s", "rooms_description_%s"
            )
        )

        # Common fields
        touristical_object_dict = self.update_touristic_object_from_json_to_dict(
            restaurant_json, is_linked_object, aspect=aspect
        )
        restaurant_dict.update(touristical_object_dict)

        # Save object
        self.update_from_dict(restaurant_dict)

    def update_fk_and_m2m_from_json(self, restaurant_json, is_linked_object=False):
        self.update_touristic_object_fk_and_m2m_from_json(
            restaurant_json, is_linked_object
        )

        # Restaurant specific part
        restaurant_specific_data_json = restaurant_json.get(
            "informationsRestauration", None
        )

        # Specialities
        specialities_json = restaurant_specific_data_json.get("specialites", None)
        self.specialities.clear()
        if specialities_json:
            for speciality_json in specialities_json:
                speciality_id = speciality_json.get("id", None)
                if speciality_id:
                    speciality_object = kapt_apidae.models.BaseElement.objects.get(
                        pk=speciality_id
                    )
                    self.specialities.add(speciality_object)

        # Chains
        chains_json = restaurant_specific_data_json.get("chaines", None)
        self.chains.clear()
        if chains_json:
            for chain_json in chains_json:
                chains_id = chain_json.get("id", None)
                if chains_id:
                    chain_object = kapt_apidae.models.BaseElement.objects.get(
                        pk=chains_id
                    )
                    self.chains.add(chain_object)

        # Guide ranking
        guides_ranking_json = restaurant_specific_data_json.get(
            "classementsGuides", None
        )
        self.guides_ranking.clear()
        if guides_ranking_json:
            for guide_ranking_json in guides_ranking_json:
                guide_ranking_id = guide_ranking_json.get("id", None)
                if guide_ranking_id:
                    guide_ranking_object = kapt_apidae.models.BaseElement.objects.get(
                        pk=guide_ranking_id
                    )
                    self.guides_ranking.add(guide_ranking_object)

        # Categories
        categories_json = restaurant_specific_data_json.get("categories", None)
        self.categories.clear()
        if categories_json:
            for category_json in categories_json:
                category_id = category_json.get("id", None)
                if category_id:
                    category_object = kapt_apidae.models.BaseElement.objects.get(
                        pk=category_id
                    )
                    self.categories.add(category_object)


class NaturalHeritageMethods:
    def update_from_json(
        self, natural_heritage_json, is_linked_object=False, aspect=None
    ):
        # Natural heritage specific part
        natural_heritage_specific_data_json = natural_heritage_json.get(
            "informationsPatrimoineNaturel", None
        )

        natural_heritage_dict = {
            "marked_trail": natural_heritage_specific_data_json.get(
                "sentiersBalises", False
            )
        }

        # Common fields
        touristical_object_dict = self.update_touristic_object_from_json_to_dict(
            natural_heritage_json, is_linked_object, aspect=aspect
        )
        natural_heritage_dict.update(touristical_object_dict)

        # Save object
        self.update_from_dict(natural_heritage_dict)

    def update_fk_and_m2m_from_json(
        self, natural_heritage_json, is_linked_object=False
    ):
        self.update_touristic_object_fk_and_m2m_from_json(
            natural_heritage_json, is_linked_object
        )

        # Natural heritage specific part
        natural_heritage_specific_data_json = natural_heritage_json.get(
            "informationsPatrimoineNaturel", None
        )

        # Rankings
        self.rankings.clear()
        rankings_json = natural_heritage_specific_data_json.get("classements", None)
        if rankings_json:
            for ranking_json in rankings_json:
                ranking_id = ranking_json.get("id", None)
                if ranking_id:
                    ranking_object = kapt_apidae.models.BaseElement.objects.get(
                        pk=ranking_id
                    )
                    self.rankings.add(ranking_object)

        # Categories
        self.categories.clear()
        categories_json = natural_heritage_specific_data_json.get("categories", None)
        if categories_json:
            for category_json in categories_json:
                category_id = category_json.get("id", None)
                if category_id:
                    category_object = kapt_apidae.models.BaseElement.objects.get(
                        pk=category_id
                    )
                    self.categories.add(category_object)


class CulturalHeritageMethods:
    def update_from_json(
        self, cultural_heritage_json, is_linked_object=False, aspect=None
    ):
        # Cultural heritage specific part
        cultural_heritage_specific_data_json = cultural_heritage_json.get(
            "informationsPatrimoineCulturel", None
        )
        cultural_heritage_dict = {"type": None}

        type_json = cultural_heritage_specific_data_json.get(
            "patrimoineCulturelType", None
        )
        if type_json:
            type_id = type_json.get("id", None)
            if type_id:
                cultural_heritage_dict[
                    "type"
                ] = kapt_apidae.models.BaseElement.objects.get(pk=type_id)

        # Common fields
        touristical_object_dict = self.update_touristic_object_from_json_to_dict(
            cultural_heritage_json, is_linked_object, aspect=aspect
        )
        cultural_heritage_dict.update(touristical_object_dict)

        # Save object
        self.update_from_dict(cultural_heritage_dict)

    def update_fk_and_m2m_from_json(
        self, cultural_heritage_json, is_linked_object=False
    ):
        self.update_touristic_object_fk_and_m2m_from_json(
            cultural_heritage_json, is_linked_object
        )

        # Cultural heritage specific part
        cultural_heritage_specific_data_json = cultural_heritage_json.get(
            "informationsPatrimoineCulturel", None
        )

        # Subjects
        self.subjects.clear()
        subjects_json = cultural_heritage_specific_data_json.get("themes", None)
        if subjects_json:
            for subject_json in subjects_json:
                subject_id = subject_json.get("id", None)
                if subject_id:
                    subject_object = kapt_apidae.models.BaseElement.objects.get(
                        pk=subject_id
                    )
                    self.subjects.add(subject_object)

        # Categories
        self.categories.clear()
        categories_json = cultural_heritage_specific_data_json.get("categories", None)
        if categories_json:
            for category_json in categories_json:
                category_id = category_json.get("id", None)
                if category_id:
                    category_object = kapt_apidae.models.BaseElement.objects.get(
                        pk=category_id
                    )
                    self.categories.add(category_object)


class OutDoorHotelAccommodationMethods:
    def update_from_json(
        self, outdoor_hotel_accommodation_json, is_linked_object=False, aspect=None
    ):
        # Outdoor hotel accommodation specific part
        outdoor_hotel_accommodation_specific_data_json = (
            outdoor_hotel_accommodation_json.get("informationsHotelleriePleinAir", None)
        )

        outdoor_hotel_accommodation_dict = {
            "type": None,
            "ranking_identifier": outdoor_hotel_accommodation_specific_data_json.get(
                "numeroClassement", None
            ),
            "ranking_date": None,
            "ranking": None,
            "surface_area": None,
            "naturism": False,
            "snow_caravans": None,
            "ranked_campingplot_quantity": None,
            "passing_campingplot_quantity": None,
            "rental_passing_campingplot_quantity": None,
            "naked_passing_campingplot_quantity": None,
            "residential_campingplot_quantity": None,
            "snow_caravans_quantity": None,
            "tents_quantity": None,
            "caravans_quantity": None,
            "campervan_quantity": None,
            "mobilhome_quantity": None,
            "tents_rental_quantity": None,
            "bungalow_rental_quantity": None,
            "caravans_rental_quantity": None,
        }

        type_json = outdoor_hotel_accommodation_specific_data_json.get(
            "hotelleriePleinAirType", None
        )
        if type_json:
            type_id = type_json.get("id", None)
            if type_id:
                outdoor_hotel_accommodation_dict[
                    "type"
                ] = kapt_apidae.models.BaseElement.objects.get(pk=type_id)

        ranking_date_json = outdoor_hotel_accommodation_specific_data_json.get(
            "dateClassement", None
        )
        if ranking_date_json:
            outdoor_hotel_accommodation_dict["ranking_date"] = dateutil.parser.parse(
                ranking_date_json
            )

        ranking_json = outdoor_hotel_accommodation_specific_data_json.get(
            "classement", None
        )
        if ranking_json:
            ranking_id = ranking_json.get("id", None)
            if ranking_id:
                ranking_object = kapt_apidae.models.BaseElement.objects.get(
                    pk=ranking_id
                )
                outdoor_hotel_accommodation_dict["ranking"] = ranking_object

        # Capacity
        capacity_json = outdoor_hotel_accommodation_specific_data_json.get(
            "capacite", None
        )
        if capacity_json:
            outdoor_hotel_accommodation_dict["surface_area"] = capacity_json.get(
                "superficie", None
            )
            outdoor_hotel_accommodation_dict["naturism"] = capacity_json.get(
                "naturisme", False
            )
            outdoor_hotel_accommodation_dict["snow_caravans"] = capacity_json.get(
                "caravaneige", False
            )
            outdoor_hotel_accommodation_dict[
                "ranked_campingplot_quantity"
            ] = capacity_json.get("nombreEmplacementsClasses", None)
            outdoor_hotel_accommodation_dict[
                "passing_campingplot_quantity"
            ] = capacity_json.get("nombreEmplacementsPassages", None)
            outdoor_hotel_accommodation_dict[
                "rental_passing_campingplot_quantity"
            ] = capacity_json.get("nombreEmplacementsPassagesLocatifs", None)
            outdoor_hotel_accommodation_dict[
                "naked_passing_campingplot_quantity"
            ] = capacity_json.get("nombreEmplacementsPassagesNus", None)
            outdoor_hotel_accommodation_dict[
                "residential_campingplot_quantity"
            ] = capacity_json.get("nombreEmplacementsResidentiels", None)
            outdoor_hotel_accommodation_dict[
                "snow_caravans_quantity"
            ] = capacity_json.get("nombreEmplacementsCaravaneiges", None)
            outdoor_hotel_accommodation_dict["tents_quantity"] = capacity_json.get(
                "nombreEmplacementsTentes", None
            )
            outdoor_hotel_accommodation_dict["caravans_quantity"] = capacity_json.get(
                "nombreEmplacementsCaravanes", None
            )
            outdoor_hotel_accommodation_dict["campervan_quantity"] = capacity_json.get(
                "nombreEmplacementsCampingCars", None
            )
            outdoor_hotel_accommodation_dict["mobilhome_quantity"] = capacity_json.get(
                "nombreLocationMobilhomes", None
            )
            outdoor_hotel_accommodation_dict[
                "tents_rental_quantity"
            ] = capacity_json.get("nombreLocationTentes", None)
            outdoor_hotel_accommodation_dict[
                "bungalow_rental_quantity"
            ] = capacity_json.get("nombreLocationBungalows", None)
            outdoor_hotel_accommodation_dict[
                "caravans_rental_quantity"
            ] = capacity_json.get("nombreLocationCaravanes", None)
            outdoor_hotel_accommodation_dict[
                "declared_plots_quantity"
            ] = capacity_json.get("nombreEmplacementsDeclares", None)

        # Common fields
        touristical_object_dict = self.update_touristic_object_from_json_to_dict(
            outdoor_hotel_accommodation_json, is_linked_object, aspect=aspect
        )
        outdoor_hotel_accommodation_dict.update(touristical_object_dict)

        # Save object
        self.update_from_dict(outdoor_hotel_accommodation_dict)

    def update_fk_and_m2m_from_json(
        self, outdoor_hotel_accommodation_json, is_linked_object=False
    ):
        self.update_touristic_object_fk_and_m2m_from_json(
            outdoor_hotel_accommodation_json, is_linked_object
        )

        # Outdoor hotel accommodation specific part
        outdoor_hotel_accommodation_specific_data_json = (
            outdoor_hotel_accommodation_json.get("informationsHotelleriePleinAir", None)
        )

        # Chains
        self.chains.clear()
        chains_json = outdoor_hotel_accommodation_specific_data_json.get(
            "chaines", None
        )
        if chains_json:
            for chain_json in chains_json:
                chain_id = chain_json.get("id", None)
                if chain_id:
                    chain_object = kapt_apidae.models.BaseElement.objects.get(
                        pk=chain_id
                    )
                    self.chains.add(chain_object)

        # Labels
        self.labels.clear()
        labels_json = outdoor_hotel_accommodation_specific_data_json.get("labels", None)
        if labels_json:
            for label_json in labels_json:
                label_id = label_json.get("id", None)
                if label_id:
                    label_object = kapt_apidae.models.BaseElement.objects.get(
                        pk=label_id
                    )
                    self.labels.add(label_object)


class HotelAccommodationMethods:
    def update_from_json(
        self, hotel_accommodation_json, is_linked_object=False, aspect=None
    ):
        # Hotel accommodation specific part
        hotel_accommodation_specific_data_json = hotel_accommodation_json.get(
            "informationsHotellerie", None
        )

        hotel_accommodation_dict = {
            "type": None,
            "ranking_identifier": hotel_accommodation_specific_data_json.get(
                "numeroClassement", None
            ),
            "ranking_date": None,
            "ranking": None,
            "ranked_rooms_quantity": None,
            "hotel_declared_rooms_quantity": None,
            "max_capacity": None,
            "single_rooms_quantity": None,
            "double_rooms_quantity": None,
            "suite_rooms_quantity": None,
            "reduced_mobility_rooms_quantity": None,
        }

        type_json = hotel_accommodation_specific_data_json.get("hotellerieType", None)
        if type_json:
            type_id = type_json.get("id", None)
            if type_id:
                hotel_accommodation_dict[
                    "type"
                ] = kapt_apidae.models.BaseElement.objects.get(pk=type_id)

        ranking_date_json = hotel_accommodation_specific_data_json.get(
            "dateClassement", None
        )
        if ranking_date_json:
            hotel_accommodation_dict["ranking_date"] = dateutil.parser.parse(
                ranking_date_json
            )

        ranking_json = hotel_accommodation_specific_data_json.get("classement", None)
        if ranking_json:
            ranking_id = ranking_json.get("id", None)
            if ranking_id:
                ranking_object = kapt_apidae.models.BaseElement.objects.get(
                    pk=ranking_id
                )
                hotel_accommodation_dict["ranking"] = ranking_object

        # Capacity
        capacity_json = hotel_accommodation_specific_data_json.get("capacite", None)
        if capacity_json:
            hotel_accommodation_dict["ranked_rooms_quantity"] = capacity_json.get(
                "nombreChambresClassees", None
            )
            hotel_accommodation_dict[
                "hotel_declared_rooms_quantity"
            ] = capacity_json.get("nombreChambresDeclareesHotelier", None)
            hotel_accommodation_dict["max_capacity"] = capacity_json.get(
                "nombreTotalPersonnes", None
            )
            hotel_accommodation_dict["single_rooms_quantity"] = capacity_json.get(
                "nombreChambresSimples", None
            )
            hotel_accommodation_dict["double_rooms_quantity"] = capacity_json.get(
                "nombreChambresDoubles", None
            )
            hotel_accommodation_dict["suite_rooms_quantity"] = capacity_json.get(
                "nombreSuites", None
            )
            hotel_accommodation_dict[
                "reduced_mobility_rooms_quantity"
            ] = capacity_json.get("nombreChambresMobiliteReduite", None)

        # Common fields
        touristical_object_dict = self.update_touristic_object_from_json_to_dict(
            hotel_accommodation_json, is_linked_object, aspect=aspect
        )
        hotel_accommodation_dict.update(touristical_object_dict)

        # Save object
        self.update_from_dict(hotel_accommodation_dict)

    def update_fk_and_m2m_from_json(
        self, hotel_accommodation_json, is_linked_object=False
    ):
        self.update_touristic_object_fk_and_m2m_from_json(
            hotel_accommodation_json, is_linked_object
        )

        # Hotel accommodation specific part
        hotel_accommodation_specific_data_json = hotel_accommodation_json.get(
            "informationsHotellerie", None
        )

        # Chains
        self.chains.clear()
        chains_json = hotel_accommodation_specific_data_json.get("chaines", None)
        if chains_json:
            for chain_json in chains_json:
                chain_id = chain_json.get("id", None)
                if chain_id:
                    chain_object = kapt_apidae.models.BaseElement.objects.get(
                        pk=chain_id
                    )
                    self.chains.add(chain_object)

        # Labels
        self.labels.clear()
        labels_json = hotel_accommodation_specific_data_json.get("labels", None)
        if labels_json:
            for label_json in labels_json:
                label_id = label_json.get("id", None)
                if label_id:
                    label_object = kapt_apidae.models.BaseElement.objects.get(
                        pk=label_id
                    )
                    self.labels.add(label_object)


class RentalAccommodationMethods:
    def update_from_json(
        self, rental_accommodation_json, is_linked_object=False, aspect=None
    ):
        # Rental accommodation specific part
        rental_accommodation_specific_data_json = rental_accommodation_json.get(
            "informationsHebergementLocatif", None
        )

        rental_accommodation_dict = {
            "type": None,
            "last_visit_date": None,
            "ranking_date": None,
            "ranking_identifier": rental_accommodation_specific_data_json.get(
                "numeroClassement", None
            ),
            "label_authorization_identifier": rental_accommodation_specific_data_json.get(
                "numeroAgrementLabel", None
            ),
            "prefectural_classification": None,
            "label_type": None,
            "naturism": False,
            "capacity": None,
            "max_capacity": None,
            "double_beds_quantity": None,
            "single_beds_quantity": None,
            "surface_area": None,
            "rooms_quantity": None,
            "bedrooms_quantity": None,
            "floors_quantity": None,
            "floor_number": None,
        }

        type_json = rental_accommodation_specific_data_json.get(
            "hebergementLocatifType", None
        )
        if type_json:
            type_id = type_json.get("id", None)
            if type_id:
                rental_accommodation_dict[
                    "type"
                ] = kapt_apidae.models.BaseElement.objects.get(pk=type_id)

        last_visit_date_json = rental_accommodation_specific_data_json.get(
            "dateDerniereVisite", None
        )
        if last_visit_date_json:
            rental_accommodation_dict["last_visit_date"] = dateutil.parser.parse(
                last_visit_date_json
            )

        ranking_date_json = rental_accommodation_specific_data_json.get(
            "dateClassement", None
        )
        if ranking_date_json:
            rental_accommodation_dict["ranking_date"] = dateutil.parser.parse(
                ranking_date_json
            )

        prefectural_classification_json = rental_accommodation_specific_data_json.get(
            "classementPrefectoral", None
        )
        if prefectural_classification_json:
            prefectural_classification_id = prefectural_classification_json.get(
                "id", None
            )
            if prefectural_classification_id:
                prefectural_classification_object = (
                    kapt_apidae.models.BaseElement.objects.get(
                        pk=prefectural_classification_id
                    )
                )
                rental_accommodation_dict[
                    "prefectural_classification"
                ] = prefectural_classification_object

        label_type_json = rental_accommodation_specific_data_json.get("typeLabel", None)
        if label_type_json:
            label_type_id = label_type_json.get("id", None)
            if label_type_id:
                label_type_object = kapt_apidae.models.BaseElement.objects.get(
                    pk=label_type_id
                )
                rental_accommodation_dict["label_type"] = label_type_object

        # Capacity
        capacity_json = rental_accommodation_specific_data_json.get("capacite", None)
        if capacity_json:
            rental_accommodation_dict["naturism"] = capacity_json.get(
                "naturisme", False
            )
            rental_accommodation_dict["capacity"] = capacity_json.get(
                "capaciteHebergement", None
            )
            rental_accommodation_dict["max_capacity"] = capacity_json.get(
                "capaciteMaximumPossible", None
            )
            rental_accommodation_dict["double_beds_quantity"] = capacity_json.get(
                "nombreLitsDoubles", None
            )
            rental_accommodation_dict["single_beds_quantity"] = capacity_json.get(
                "nombreLitsSimples", None
            )
            rental_accommodation_dict["surface_area"] = capacity_json.get(
                "surface", None
            )
            rental_accommodation_dict["rooms_quantity"] = capacity_json.get(
                "nombrePieces", None
            )
            rental_accommodation_dict["bedrooms_quantity"] = capacity_json.get(
                "nombreChambres", None
            )
            rental_accommodation_dict["floors_quantity"] = capacity_json.get(
                "nombreEtages", None
            )
            rental_accommodation_dict["floor_number"] = capacity_json.get(
                "numeroEtage", None
            )

        # Common fields
        touristical_object_dict = self.update_touristic_object_from_json_to_dict(
            rental_accommodation_json, is_linked_object, aspect=aspect
        )
        rental_accommodation_dict.update(touristical_object_dict)

        # Save object
        self.update_from_dict(rental_accommodation_dict)

    def update_fk_and_m2m_from_json(
        self, rental_accommodation_json, is_linked_object=False
    ):
        self.update_touristic_object_fk_and_m2m_from_json(
            rental_accommodation_json, is_linked_object
        )

        # Rental accommodation specific part
        rental_accommodation_specific_data_json = rental_accommodation_json.get(
            "informationsHebergementLocatif", None
        )

        # Labels
        self.labels.clear()
        labels_json = rental_accommodation_specific_data_json.get("labels", None)
        if labels_json:
            for label_json in labels_json:
                label_id = label_json.get("id", None)
                if label_id:
                    label_object = kapt_apidae.models.BaseElement.objects.get(
                        pk=label_id
                    )
                    self.labels.add(label_object)

        # Habitation types
        self.habitation_types.clear()
        habitation_types_json = rental_accommodation_specific_data_json.get(
            "typesHabitation", None
        )
        if habitation_types_json:
            for habitation_type_json in habitation_types_json:
                habitation_type_id = habitation_type_json.get("id", None)
                if habitation_type_id:
                    habitation_type_object = kapt_apidae.models.BaseElement.objects.get(
                        pk=habitation_type_id
                    )
                    self.habitation_types.add(habitation_type_object)


class GroupAccommodationMethods:
    def update_from_json(
        self, group_accommodation_json, is_linked_object=False, aspect=None
    ):
        # Group accommodation specific part
        group_accommodation_specific_data_json = group_accommodation_json.get(
            "informationsHebergementCollectif", None
        )

        group_accommodation_dict = {
            "type": None,
            "ranking_date": None,
            "ranking_identifier": group_accommodation_specific_data_json.get(
                "numeroClassement", None
            ),
            "prefectural_classification": None,
            "chain_and_label": None,
            "naturism": False,
            "capacity": None,
            "youth_and_sports_capacity": None,
            "national_education_capacity": None,
            "safety_committee_capacity": None,
            "middle_size_dormitory_capacity": None,
            "king_size_dormitory_capacity": None,
            "reduced_mobility_accommodations_quantity": None,
            "one_person_accommodations_quantity": None,
            "two_persons_accommodations_quantity": None,
            "three_persons_accommodations_quantity": None,
            "four_persons_accommodations_quantity": None,
            "five_persons_accommodations_quantity": None,
            "six_persons_accommodations_quantity": None,
            "more_than_six_persons_accommodations_quantity": None,
        }

        type_json = group_accommodation_specific_data_json.get(
            "hebergementCollectifType", None
        )
        if type_json:
            type_id = type_json.get("id", None)
            if type_id:
                group_accommodation_dict[
                    "type"
                ] = kapt_apidae.models.BaseElement.objects.get(pk=type_id)

        ranking_date_json = group_accommodation_specific_data_json.get(
            "dateClassement", None
        )
        if ranking_date_json:
            group_accommodation_dict["ranking_date"] = dateutil.parser.parse(
                ranking_date_json
            )

        prefectural_classification_json = group_accommodation_specific_data_json.get(
            "classementPrefectoral", None
        )
        if prefectural_classification_json:
            prefectural_classification_id = prefectural_classification_json.get(
                "id", None
            )
            if prefectural_classification_id:
                prefectural_classification_object = (
                    kapt_apidae.models.BaseElement.objects.get(
                        pk=prefectural_classification_id
                    )
                )
                group_accommodation_dict[
                    "prefectural_classification"
                ] = prefectural_classification_object

        chain_and_label_json = group_accommodation_specific_data_json.get(
            "chaineEtLabel", None
        )
        if chain_and_label_json:
            chain_and_label_id = chain_and_label_json.get("id", None)
            if chain_and_label_id:
                chain_and_label_object = kapt_apidae.models.BaseElement.objects.get(
                    pk=chain_and_label_id
                )
                group_accommodation_dict["chain_and_label"] = chain_and_label_object

        # Capacity
        capacity_json = group_accommodation_specific_data_json.get("capacite", None)
        if capacity_json:
            group_accommodation_dict["naturism"] = capacity_json.get("naturisme", False)
            group_accommodation_dict["capacity"] = capacity_json.get(
                "capaciteTotale", None
            )
            group_accommodation_dict["youth_and_sports_capacity"] = capacity_json.get(
                "capaciteTotaleJeunesseSport", None
            )
            group_accommodation_dict["national_education_capacity"] = capacity_json.get(
                "capaciteTotaleEducationNationale", None
            )
            group_accommodation_dict["safety_committee_capacity"] = capacity_json.get(
                "capaciteCommissionSecurite", None
            )
            group_accommodation_dict[
                "middle_size_dormitory_capacity"
            ] = capacity_json.get("nombreDortoirsMoyens", None)
            group_accommodation_dict[
                "king_size_dormitory_capacity"
            ] = capacity_json.get("nombreDortoirsGrands", None)
            group_accommodation_dict[
                "reduced_mobility_accommodations_quantity"
            ] = capacity_json.get("nombreHebergementsMobiliteReduite", None)
            group_accommodation_dict[
                "one_person_accommodations_quantity"
            ] = capacity_json.get("nombreHebergementsUnePersonne", None)
            group_accommodation_dict[
                "two_persons_accommodations_quantity"
            ] = capacity_json.get("nombreHebergementsDeuxPersonnes", None)
            group_accommodation_dict[
                "three_persons_accommodations_quantity"
            ] = capacity_json.get("nombreHebergementsTroisPersonnes", None)
            group_accommodation_dict[
                "four_persons_accommodations_quantity"
            ] = capacity_json.get("nombreHebergementsQuatrePersonnes", None)
            group_accommodation_dict[
                "five_persons_accommodations_quantity"
            ] = capacity_json.get("nombreHebergementsCinqPersonnes", None)
            group_accommodation_dict[
                "six_persons_accommodations_quantity"
            ] = capacity_json.get("nombreHebergementsSixPersonnes", None)
            group_accommodation_dict[
                "more_than_six_persons_accommodations_quantity"
            ] = capacity_json.get("nombreHebergementsPlusSixPersonnes", None)

        # Common fields
        touristical_object_dict = self.update_touristic_object_from_json_to_dict(
            group_accommodation_json, is_linked_object, aspect=aspect
        )
        group_accommodation_dict.update(touristical_object_dict)

        # Save object
        self.update_from_dict(group_accommodation_dict)

    def update_fk_and_m2m_from_json(
        self, group_accommodation_json, is_linked_object=False
    ):
        self.update_touristic_object_fk_and_m2m_from_json(
            group_accommodation_json, is_linked_object
        )

        # Group accommodation specific part
        group_accommodation_specific_data_json = group_accommodation_json.get(
            "informationsHebergementCollectif", None
        )

        # Labels
        self.labels.clear()
        labels_json = group_accommodation_specific_data_json.get("labels", None)
        if labels_json:
            for label_json in labels_json:
                label_id = label_json.get("id", None)
                if label_id:
                    label_object = kapt_apidae.models.BaseElement.objects.get(
                        pk=label_id
                    )
                    self.labels.add(label_object)

        # Accommodations types
        self.accommodations_types.clear()
        accommodations_types_json = group_accommodation_specific_data_json.get(
            "typesHebergement", None
        )
        if accommodations_types_json:
            for accommodations_type_json in accommodations_types_json:
                accommodations_type_id = accommodations_type_json.get("id", None)
                if accommodations_type_id:
                    accommodations_type_object = (
                        kapt_apidae.models.BaseElement.objects.get(
                            pk=accommodations_type_id
                        )
                    )
                    self.accommodations_types.add(accommodations_type_object)

        # Housing types
        self.housing_types.clear()
        housing_types_json = group_accommodation_specific_data_json.get(
            "typesHabitation", None
        )
        if housing_types_json:
            for housing_type_json in housing_types_json:
                housing_type_id = housing_type_json.get("id", None)
                if housing_type_id:
                    housing_type_object = kapt_apidae.models.BaseElement.objects.get(
                        pk=housing_type_id
                    )
                    self.housing_types.add(housing_type_object)

        # Agrements
        kapt_apidae.models.AgrementsGroupAccommodation.objects.filter(
            group_accommodation=self
        ).delete()
        agrements_json = group_accommodation_specific_data_json.get("agrements", None)
        if agrements_json:
            for agrement_json in agrements_json:
                agrement_type_json = agrement_json.get("type", None)
                if agrement_type_json:
                    agrement_id = agrement_type_json.get("id", None)
                    if agrement_id:
                        agrement_object = kapt_apidae.models.BaseElement.objects.get(
                            pk=agrement_id
                        )
                        agrement_identifier_json = agrement_json.get("numero", None)
                        kapt_apidae.models.AgrementsGroupAccommodation.objects.create(
                            group_accommodation=self,
                            agrement=agrement_object,
                            agrement_identifier=agrement_identifier_json,
                        )


class CelebrationAndManifestationMethods:
    def update_from_json(
        self, celebration_and_manifestation_json, is_linked_object=False, aspect=None
    ):
        celebration_and_manifestation_specific_data_json = (
            celebration_and_manifestation_json.get(
                "informationsFeteEtManifestation", None
            )
        )

        celebration_and_manifestation_dict = {
            "place_name": celebration_and_manifestation_specific_data_json.get(
                "nomLieu", None
            ),
            "generic_type": None,
            "manifestation_reach": None,
        }

        generic_type_json = celebration_and_manifestation_specific_data_json.get(
            "evenementGenerique", None
        )
        if generic_type_json:
            generic_type_id = generic_type_json.get("id", None)
            if generic_type_id:
                celebration_and_manifestation_dict[
                    "generic_type"
                ] = kapt_apidae.models.BaseElement.objects.get(pk=generic_type_id)

        manifestation_reach_json = celebration_and_manifestation_specific_data_json.get(
            "portee", None
        )
        if manifestation_reach_json:
            manifestation_reach_id = manifestation_reach_json.get("id", None)
            if manifestation_reach_id:
                celebration_and_manifestation_dict[
                    "manifestation_reach"
                ] = kapt_apidae.models.BaseElement.objects.get(
                    pk=manifestation_reach_id
                )

        # Common fields
        touristical_object_dict = self.update_touristic_object_from_json_to_dict(
            celebration_and_manifestation_json, is_linked_object, aspect=aspect
        )
        celebration_and_manifestation_dict.update(touristical_object_dict)

        # Save object
        self.update_from_dict(celebration_and_manifestation_dict)

    def update_fk_and_m2m_from_json(
        self, celebration_and_manifestation_json, is_linked_object=False
    ):
        self.update_touristic_object_fk_and_m2m_from_json(
            celebration_and_manifestation_json, is_linked_object
        )

        celebration_and_manifestation_specific_data_json = (
            celebration_and_manifestation_json.get(
                "informationsFeteEtManifestation", None
            )
        )

        # Manifestation types
        manifestation_types_json = celebration_and_manifestation_specific_data_json.get(
            "typesManifestation", None
        )
        self.manifestation_types.clear()
        if manifestation_types_json:
            for manifestation_type_json in manifestation_types_json:
                manifestation_type_id = manifestation_type_json.get("id", None)
                if manifestation_type_id:
                    manifestation_type_object = (
                        kapt_apidae.models.BaseElement.objects.get(
                            pk=manifestation_type_id
                        )
                    )
                    self.manifestation_types.add(manifestation_type_object)

        # Categories
        categories_json = celebration_and_manifestation_specific_data_json.get(
            "categories", None
        )
        self.categories.clear()
        if categories_json:
            for category_json in categories_json:
                category_id = category_json.get("id", None)
                if category_id:
                    category_object = kapt_apidae.models.BaseElement.objects.get(
                        pk=category_id
                    )
                    self.categories.add(category_object)

        # Subjects
        subjects_json = celebration_and_manifestation_specific_data_json.get(
            "themes", None
        )
        self.subjects.clear()
        if subjects_json:
            for subject_json in subjects_json:
                subject_id = subject_json.get("id", None)
                if subject_id:
                    subject_object = kapt_apidae.models.BaseElement.objects.get(
                        pk=subject_id
                    )
                    self.subjects.add(subject_object)


class EquipmentMethods:
    def update_from_json(self, equipment_json, is_linked_object=False, aspect=None):
        equipment_specific_data_json = equipment_json.get(
            "informationsEquipement", None
        )

        equipment_dict = {
            "type": None,
            "difference_in_level": None,
            "distance": None,
            "daily_duration": None,
            "mobility_duration": None,
            "itinerary_type": None,
        }

        type_json = equipment_specific_data_json.get("informationsEquipement", None)
        if type_json:
            type_id = type_json.get("id", None)
            if type_id:
                equipment_dict["type"] = kapt_apidae.models.BaseElement.objects.get(
                    pk=type_id
                )

        itinerary_json = equipment_specific_data_json.get("itineraire", None)
        if itinerary_json:
            equipment_dict["difference_in_level"] = itinerary_json.get(
                "denivellation", False
            )
            equipment_dict["distance"] = itinerary_json.get("distance", None)
            equipment_dict["daily_duration"] = itinerary_json.get(
                "dureeJournaliere", None
            )
            equipment_dict["mobility_duration"] = itinerary_json.get(
                "dureeItinerance", None
            )
            equipment_dict["itinerary_type"] = itinerary_json.get(
                "itineraireType", None
            )

        # Common fields
        touristical_object_dict = self.update_touristic_object_from_json_to_dict(
            equipment_json, is_linked_object, aspect=aspect
        )
        equipment_dict.update(touristical_object_dict)

        # Save object
        self.update_from_dict(equipment_dict)

    def update_fk_and_m2m_from_json(self, equipment_json, is_linked_object=False):
        self.update_touristic_object_fk_and_m2m_from_json(
            equipment_json, is_linked_object
        )

        equipment_specific_data_json = equipment_json.get(
            "informationsEquipement", None
        )
        # Activities
        equipment_activities_json = equipment_specific_data_json.get("activites", None)
        self.equipment_activities.clear()
        if equipment_activities_json:
            for equipment_activity_json in equipment_activities_json:
                equipment_activity_id = equipment_activity_json.get("id", None)
                if equipment_activity_id:
                    equipment_activity_object = (
                        kapt_apidae.models.BaseElement.objects.get(
                            pk=equipment_activity_id
                        )
                    )
                    self.equipment_activities.add(equipment_activity_object)


class SkiingAreaMethods:
    def update_from_json(self, skiing_area_json, is_linked_object=False, aspect=None):
        skiing_area_specific_data_json = skiing_area_json.get(
            "informationsDomaineSkiable", None
        )

        skiing_area_dict = {
            "classification": None,
            "artificial_snow": skiing_area_specific_data_json.get(
                "neigeCulture", False
            ),
            "free_ski_lift": skiing_area_specific_data_json.get(
                "remonteeGratuite", False
            ),
            "snow_description": skiing_area_specific_data_json.get(
                "neigeDescription", None
            ),
            "ski_trail_quantity": skiing_area_specific_data_json.get(
                "nombrePistes", None
            ),
            "ski_trail_km": skiing_area_specific_data_json.get("nombreKmPiste", None),
            "green_trail_quantity": skiing_area_specific_data_json.get(
                "nombrePistesVertes", None
            ),
            "green_trail_km": skiing_area_specific_data_json.get(
                "nombreKmPisteVerte", None
            ),
            "blue_trail_quantity": skiing_area_specific_data_json.get(
                "nombrePistesBleues", None
            ),
            "blue_trail_km": skiing_area_specific_data_json.get(
                "nombreKmPisteBleue", None
            ),
            "red_trail_quantity": skiing_area_specific_data_json.get(
                "nombrePistesRouges", None
            ),
            "red_trail_km": skiing_area_specific_data_json.get(
                "nombreKmPisteRouge", None
            ),
            "black_trail_quantity": skiing_area_specific_data_json.get(
                "nombrePistesNoires", None
            ),
            "black_trail_km": skiing_area_specific_data_json.get(
                "nombreKmPisteNoire", None
            ),
            "skating_km": skiing_area_specific_data_json.get(
                "nombreKmPisteSkating", None
            ),
            "aerial_lift_quantity": skiing_area_specific_data_json.get(
                "nombreRemonteesMecaniques", None
            ),
            "platter_lift_quantity": skiing_area_specific_data_json.get(
                "nombreTeleskis", None
            ),
            "chairlift_quantity": skiing_area_specific_data_json.get(
                "nombreTelesieges", None
            ),
            "cable_car_quantity": skiing_area_specific_data_json.get(
                "nombreTelecabines", None
            ),
            "aerial_tramway_quantity": skiing_area_specific_data_json.get(
                "nombreTelepheriques", None
            ),
            "other_lift_quantity": skiing_area_specific_data_json.get(
                "nombreAutresRemontees", None
            ),
            "pedestrian_accessible_lift_quantity": skiing_area_specific_data_json.get(
                "nombreRemonteesAccessiblesPietons", None
            ),
            "handiski_quantity": skiing_area_specific_data_json.get(
                "nombreHandiski", None
            ),
            "cross_country_skiing_quantity": skiing_area_specific_data_json.get(
                "nombreRemonteesSkiFond", None
            ),
        }

        classification_json = skiing_area_specific_data_json.get("classification", None)
        if classification_json:
            classification_id = classification_json.get("id", None)
            if classification_id:
                skiing_area_dict[
                    "classification"
                ] = kapt_apidae.models.BaseElement.objects.get(pk=classification_id)

        skiing_area_dict.update(
            convert_translated_fields(
                skiing_area_specific_data_json.get("identifiantDomaineRelie", None),
                "libelle%s",
                "linked_domain_description_%s",
            )
        )
        skiing_area_dict.update(
            convert_translated_fields(
                skiing_area_specific_data_json.get("conditionForfaitGratuit", None),
                "libelle%s",
                "free_ski_pass_conditions_%s",
            )
        )
        skiing_area_dict.update(
            convert_translated_fields(
                skiing_area_specific_data_json.get("identifiantForfait", None),
                "libelle%s",
                "ski_pass_identifier_%s",
            )
        )
        skiing_area_dict.update(
            convert_translated_fields(
                skiing_area_specific_data_json.get("validiteTarifEnfant", None),
                "libelle%s",
                "children_validity_conditions_%s",
            )
        )
        skiing_area_dict.update(
            convert_translated_fields(
                skiing_area_specific_data_json.get("validiteTarifSenior", None),
                "libelle%s",
                "senior_validity_conditions_%s",
            )
        )

        # Common fields
        touristical_object_dict = self.update_touristic_object_from_json_to_dict(
            skiing_area_json, is_linked_object, aspect=aspect
        )
        skiing_area_dict.update(touristical_object_dict)

        # Save object
        self.update_from_dict(skiing_area_dict)

    def update_fk_and_m2m_from_json(self, skiing_area_json, is_linked_object=False):
        self.update_touristic_object_fk_and_m2m_from_json(
            skiing_area_json, is_linked_object
        )

        skiing_area_specific_data_json = skiing_area_json.get(
            "informationsDomaineSkiable", None
        )

        # Types
        self.types.clear()
        types_json = skiing_area_specific_data_json.get("domaineSkiableTypes", None)
        if types_json:
            for type_json in types_json:
                type_id = type_json.get("id", None)
                if type_id:
                    type_object = kapt_apidae.models.BaseElement.objects.get(pk=type_id)
                    self.types.add(type_object)

        # EGPS
        self.egps.clear()
        egps_list_json = skiing_area_specific_data_json.get("egps", None)
        if egps_list_json and not is_linked_object:
            for egps_json in egps_list_json:
                egps_toursistical_object_json = egps_json.get("objetTouristique", None)
                if egps_toursistical_object_json:
                    egps_id = egps_toursistical_object_json.get("id", None)
                    if egps_id:
                        try:
                            egps_object = (
                                kapt_apidae.models.TouristicObject.objects.get(
                                    apidae_identifier=egps_id, aspect__isnull=True
                                )
                            )
                            self.egps.add(egps_object)
                        except ObjectDoesNotExist:
                            pass

        # Subarea ski ressorts
        self.subarea_ski_resorts.clear()
        subarea_ski_resorts_json = skiing_area_specific_data_json.get(
            "sousDomaines", None
        )
        if subarea_ski_resorts_json and not is_linked_object:
            for subarea_ski_resort_json in subarea_ski_resorts_json:
                subarea_toursistical_object_json = subarea_ski_resort_json.get(
                    "objetTouristique", None
                )
                if subarea_toursistical_object_json:
                    subarea_id = subarea_toursistical_object_json.get("id", None)
                    if subarea_id:
                        try:
                            subarea_object = (
                                kapt_apidae.models.TouristicObject.objects.get(
                                    apidae_identifier=subarea_id, aspect__isnull=True
                                )
                            )
                            self.subarea_ski_resorts.add(subarea_object)
                        except ObjectDoesNotExist:
                            pass

        # Parents ski ressorts
        self.parents_ski_resorts.clear()
        parents_ski_resorts_json = skiing_area_specific_data_json.get(
            "domainesParents", None
        )
        if parents_ski_resorts_json and not is_linked_object:
            for parent_ski_resort_json in parents_ski_resorts_json:
                parent_ski_resort_toursistical_object_json = parent_ski_resort_json.get(
                    "objetTouristique", None
                )
                if parent_ski_resort_toursistical_object_json:
                    parent_ski_resort_toursistical_object_id = (
                        parent_ski_resort_toursistical_object_json.get("id", None)
                    )
                    if parent_ski_resort_toursistical_object_id:
                        try:
                            parent_ski_resort_object = kapt_apidae.models.TouristicObject.objects.get(
                                apidae_identifier=parent_ski_resort_toursistical_object_id,
                                aspect__isnull=True,
                            )
                            self.parents_ski_resorts.add(parent_ski_resort_object)
                        except ObjectDoesNotExist:
                            pass


class TastingMethods:
    def update_from_json(self, tasting_json, is_linked_object=False, aspect=None):
        tasting_specific_data_json = tasting_json.get("informationsDegustation", None)

        tasting_dict = {
            "aoc": tasting_specific_data_json.get("aoc", False),
            "production_region": None,
            "local_area": tasting_specific_data_json.get("zoneLocale", None),
            "production_area": None,
        }

        # Production region
        production_region_json = tasting_specific_data_json.get(
            "regionProduction", None
        )
        if production_region_json:
            production_region_id = production_region_json.get("id", None)
            if production_region_id:
                tasting_dict[
                    "production_region"
                ] = kapt_apidae.models.BaseElement.objects.get(pk=production_region_id)

        # Production area
        production_area_json = tasting_specific_data_json.get(
            "territoireProduction", None
        )
        if production_area_json:
            production_area_id = production_area_json.get("id", None)
            if production_area_id:
                tasting_dict[
                    "production_area"
                ] = kapt_apidae.models.BaseElement.objects.get(pk=production_area_id)

        tasting_dict.update(
            convert_translated_fields(
                tasting_specific_data_json.get("charteQualite", None),
                "libelle%s",
                "quality_charter_description_%s",
            )
        )
        tasting_dict.update(
            convert_translated_fields(
                tasting_specific_data_json.get("aocDescriptif", None),
                "libelle%s",
                "aoc_description_%s",
            )
        )

        # Common fields
        touristical_object_dict = self.update_touristic_object_from_json_to_dict(
            tasting_json, is_linked_object, aspect=aspect
        )
        tasting_dict.update(touristical_object_dict)

        # Save object
        self.update_from_dict(tasting_dict)

    def update_fk_and_m2m_from_json(self, tasting_json, is_linked_object=False):
        self.update_touristic_object_fk_and_m2m_from_json(
            tasting_json, is_linked_object
        )

        tasting_specific_data_json = tasting_json.get("informationsDegustation", None)

        # Goods types
        self.goods_types.clear()
        goods_types_json = tasting_specific_data_json.get("typesProduit", None)
        if goods_types_json:
            for good_type_json in goods_types_json:
                good_type_id = good_type_json.get("id", None)
                if good_type_id:
                    good_type_object = kapt_apidae.models.BaseElement.objects.get(
                        pk=good_type_id
                    )
                    self.goods_types.add(good_type_object)

        # LableChartesQualite
        self.quality_charter.clear()
        quality_charters_json = tasting_specific_data_json.get(
            "labelsChartesQualite", None
        )
        if quality_charters_json:
            for quality_charter_json in quality_charters_json:
                quality_charter_id = quality_charter_json.get("id", None)
                if quality_charter_id:
                    quality_charter_object = kapt_apidae.models.BaseElement.objects.get(
                        pk=quality_charter_id
                    )
                    self.quality_charter.add(quality_charter_object)

        # aopAocIgps
        self.aop_aoc_igps.clear()
        aop_aoc_igps_json = tasting_specific_data_json.get("aopAocIgps", None)
        if aop_aoc_igps_json:
            for aop_aoc_igp_json in aop_aoc_igps_json:
                aop_aoc_igp_id = aop_aoc_igp_json.get("id", None)
                if aop_aoc_igp_id:
                    aop_aoc_igp_object = kapt_apidae.models.BaseElement.objects.get(
                        pk=aop_aoc_igp_id
                    )
                    self.aop_aoc_igps.add(aop_aoc_igp_object)

        # Operators status
        self.operators_status.clear()
        operators_status_json = tasting_specific_data_json.get(
            "statutsExploitant", None
        )
        if operators_status_json:
            for operator_status_json in operators_status_json:
                operator_status_id = operator_status_json.get("id", None)
                if operator_status_id:
                    operator_status_object = kapt_apidae.models.BaseElement.objects.get(
                        pk=operator_status_id
                    )
                    self.operators_status.add(operator_status_object)


class BusinessAndServiceMethods:
    def update_from_json(
        self, business_and_service_json, is_linked_object=False, aspect=None
    ):
        business_and_service_specific_data_json = business_and_service_json.get(
            "informationsCommerceEtService", None
        )

        business_and_service_dict = {"type": None}

        # Type
        type_json = business_and_service_specific_data_json.get(
            "commerceEtServiceType", None
        )
        if type_json:
            type_id = type_json.get("id", None)
            if type_id:
                business_and_service_dict[
                    "type"
                ] = kapt_apidae.models.BaseElement.objects.get(pk=type_id)

        # Common fields
        touristical_object_dict = self.update_touristic_object_from_json_to_dict(
            business_and_service_json, is_linked_object, aspect=aspect
        )
        business_and_service_dict.update(touristical_object_dict)

        # Save object
        self.update_from_dict(business_and_service_dict)

    def update_fk_and_m2m_from_json(
        self, business_and_service_json, is_linked_object=False
    ):
        self.update_touristic_object_fk_and_m2m_from_json(
            business_and_service_json, is_linked_object
        )

        business_and_service_specific_data_json = business_and_service_json.get(
            "informationsCommerceEtService", None
        )

        # Detailed types
        self.detailed_types.clear()
        detailed_types_json = business_and_service_specific_data_json.get(
            "typesDetailles", None
        )
        if detailed_types_json:
            for detailed_type_json in detailed_types_json:
                detailed_type_id = detailed_type_json.get("id", None)
                if detailed_type_id:
                    detailed_type_object = kapt_apidae.models.BaseElement.objects.get(
                        pk=detailed_type_id
                    )
                    self.detailed_types.add(detailed_type_object)


class ActivityMethods:
    def update_from_json(self, activity_json, is_linked_object=False, aspect=None):
        activity_specific_data_json = activity_json.get("informationsActivite", None)

        activity_dict = {
            "session_duration": activity_specific_data_json.get("dureeSeance", None),
            "frequency": activity_specific_data_json.get("nombreJours", None),
            "type": None,
            "place_name": activity_specific_data_json.get("nomLieu", None),
        }

        # Type
        type_json = activity_specific_data_json.get("activiteType", None)
        if type_json:
            type_id = type_json.get("id", None)
            if type_id:
                activity_dict["type"] = kapt_apidae.models.BaseElement.objects.get(
                    pk=type_id
                )

        # Prestataire
        recipient_json = activity_specific_data_json.get("prestataireActivites", None)
        if recipient_json:
            recipient_id = recipient_json.get("id", None)
            if recipient_id:
                activity_dict["recipient"] = recipient_id

        # Common fields
        touristical_object_dict = self.update_touristic_object_from_json_to_dict(
            activity_json, is_linked_object, aspect=aspect
        )
        activity_dict.update(touristical_object_dict)

        # Save object
        self.update_from_dict(activity_dict)

    def update_fk_and_m2m_from_json(self, activity_json, is_linked_object=False):
        self.update_touristic_object_fk_and_m2m_from_json(
            activity_json, is_linked_object
        )

        activity_specific_data_json = activity_json.get("informationsActivite", None)

        # Durations
        self.durations.clear()
        durations_json = activity_specific_data_json.get("durees", None)
        if durations_json:
            for duration_json in durations_json:
                duration_id = duration_json.get("id", None)
                if duration_id:
                    duration_object = kapt_apidae.models.BaseElement.objects.get(
                        pk=duration_id
                    )
                    self.durations.add(duration_object)

        # Categories
        self.categories.clear()
        categories_json = activity_specific_data_json.get("categories", None)
        if categories_json:
            for category_json in categories_json:
                category_id = category_json.get("id", None)
                if category_id:
                    category_object = kapt_apidae.models.BaseElement.objects.get(
                        pk=category_id
                    )
                    self.categories.add(category_object)

        # Sport activities
        self.sport_activities.clear()
        sport_activities_json = activity_specific_data_json.get(
            "activitesSportives", None
        )
        if sport_activities_json:
            for sport_activity_json in sport_activities_json:
                sport_activity_id = sport_activity_json.get("id", None)
                if sport_activity_id:
                    sport_activity_object = kapt_apidae.models.BaseElement.objects.get(
                        pk=sport_activity_id
                    )
                    self.sport_activities.add(sport_activity_object)

        # Cultural activities
        self.cultural_activities.clear()
        cultural_activities_json = activity_specific_data_json.get(
            "activitesCulturelles", None
        )
        if cultural_activities_json:
            for cultural_activity_json in cultural_activities_json:
                cultural_activity_id = cultural_activity_json.get("id", None)
                if cultural_activity_id:
                    cultural_activity_object = (
                        kapt_apidae.models.BaseElement.objects.get(
                            pk=cultural_activity_id
                        )
                    )
                    self.cultural_activities.add(cultural_activity_object)

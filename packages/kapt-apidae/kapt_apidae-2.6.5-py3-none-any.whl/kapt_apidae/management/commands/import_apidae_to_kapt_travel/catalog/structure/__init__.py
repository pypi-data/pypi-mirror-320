import json

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from kapt_catalog.models import Description, SpokenLanguage, Structure
from kapt_catalog.models.structure import StructureContact
from kapt_contact.models.contact import Contact
from kapt_geo.models import Address

from kapt_apidae.conf import settings as local_settings
from kapt_apidae.conf.settings import BOOKING_URL_PARSE_METHOD as parse_booking_link
from kapt_apidae.management import ScriptError
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.activities import (
    ActivityCreator,
    ActivityUpdater,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.characteristics.handmade_characteristics import (
    SPOKEN_LANGUAGES,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.common import (
    update_address_object,
    update_contact_communication_infos,
    update_gallery,
)
from kapt_apidae.models import CommunicationInfo
from kapt_apidae.utils import model_field_exists


if local_settings.IMPORT_OPENSYSTEM_REFERENCES:
    from kapt_catalog.models import OpenSystemReference

if local_settings.IMPORT_FAIRGUEST_METADATA:
    from kapt_catalog.models import FairGuestMetaData


class CatalogStructureUpdater:
    structure = None
    touristic_object = None
    aspect = None

    def __init__(self, structure, touristic_object, aspect):
        self.structure = structure
        self.touristic_object = touristic_object
        self.aspect = aspect

    def update(self):
        # Structure name

        # We unfortunately need to truncate the structure name to max_length as we will never can increase the size of name field of Structure in kapt-catalog due to the way translations are handled in migrations O_o
        # Fortunatelly, we dont use this field actually in front
        for language in settings.LANGUAGES:
            source_field_name = "label_" + language[0]
            destination_field_name = "name_" + language[0]
            label_value = getattr(self.touristic_object, source_field_name, None)
            if label_value is not None:
                label_value = label_value[
                    : Structure._meta.get_field("name").max_length
                ]

            setattr(
                self.structure,
                destination_field_name,
                label_value,
            )

        # Altitude
        self.structure.elevation = self.touristic_object.altitude
        # Address
        if self.structure.id:
            address_object = self.structure.address
        else:
            address_object = Address()
        self.structure.address = update_address_object(
            self.touristic_object, address_object
        )

        # Place name (has been moved from activity to structure)
        if model_field_exists(Structure, "place_name"):
            self.structure.place_name = self.touristic_object.place_name

        # Save
        self.structure.save()

        # Gallery (has been moved from activity to structure)
        update_gallery(self.structure, self.touristic_object)

        # Contacts
        self.contacts()

        # descriptions: Actually, attached to the activity and not structure (but we clean them just in case)
        Description.objects.filter(
            content_type=ContentType.objects.get_for_model(self.structure),
            object_id=self.structure.id,
        ).delete()

        # spoken_languages
        self.spoken_languages()

        # Booking information
        self.booking_informations()

        # FairGUEST metadata
        self.fairguest_metadata()

        # nearby_leisures: Not used with Apidae (but we clean them just in case)
        self.structure.nearby_leisures.clear()

        # nearby_services: Not used with Apidae (but we clean them just in case)
        self.structure.nearby_services.clear()

        # on_site_services: Not used with Apidae (but we clean them just in case)
        self.structure.on_site_services.clear()

        self.activities()

        return self.structure

    def contacts(self):
        contacts_list = []

        # From member
        if self.structure.reference.member_set.exists():
            member_object = self.structure.reference.member_set.all()[0]
            member_contact = member_object.referent_contact
            contacts_list.append(member_contact)
            self._attach_contact(member_contact, False)

        # Internal or external communication
        communication_infos = CommunicationInfo.objects.filter(
            Q(internal_communication_objects_set=self.touristic_object)
            | Q(external_communication_objects_set=self.touristic_object)
        ).order_by("pk")
        if communication_infos.exists():
            if Contact.objects.filter(
                structurecontact__structure=self.structure, member__isnull=True
            ).exists():
                communication_contact = Contact.objects.filter(
                    structurecontact__structure=self.structure, member__isnull=True
                )[0]
            else:
                communication_contact = Contact()
            communication_contact = update_contact_communication_infos(
                communication_contact, communication_infos
            )
            communication_contact.save()
            contacts_list.append(communication_contact)
            self._attach_contact(communication_contact, True)
        else:
            Contact.objects.filter(
                structurecontact__structure=self.structure, member__isnull=True
            ).delete()

        # Handle contacts removal
        StructureContact.objects.filter(structure=self.structure).exclude(
            contact__in=contacts_list
        ).delete()

    def spoken_languages(self):
        self.structure.spoken_languages.clear()

        # We guess that all Apidae Object speak French
        self.structure.spoken_languages.add(SpokenLanguage.objects.get(code="fr"))
        # For all language except 'French'
        for language in self.touristic_object.spoken_languages.all().exclude(id=1197):
            try:
                self.structure.spoken_languages.add(
                    SpokenLanguage.objects.get(code=SPOKEN_LANGUAGES[language.id])
                )
            except Exception:
                raise ScriptError(
                    "New language to handle " + str(language.label_fr), language
                )

    def booking_informations(self):
        # If no url found, reset the value
        self.structure.booking_url = None
        for booking in self.touristic_object.booking_organisations.all():
            self.structure.booking_url = parse_booking_link(booking)

        self.structure.save()

        # Opensystem meta data
        if local_settings.IMPORT_OPENSYSTEM_REFERENCES:
            try:
                opensystemreference = self.structure.reference.opensystemreference
                opensystemreference.delete()
            except OpenSystemReference.DoesNotExist:
                pass

            if self.touristic_object.meta_data:
                meta_data = json.loads(self.touristic_object.meta_data)

                if len(meta_data) > 0:
                    for meta_data_node in meta_data:
                        if (
                            "noeudId" in meta_data_node
                            and meta_data_node["noeudId"] == "open-system"
                        ):
                            meta_data_node_contents = meta_data_node.get("contenus", [])

                            for content in meta_data_node_contents:
                                content_meta = content.get("metadonnee", None)
                                if content_meta:
                                    widget = content_meta.get("widget", None)
                                    if widget:
                                        uis = widget.get("uis", [])
                                        integration = widget.get("integration", {})
                                        integration_id = integration.get("id", None)
                                        basket_id = integration.get("idPanier", None)

                                        for ui in uis:
                                            reference = ui.get("ui", None)
                                            if reference:
                                                try:
                                                    opensystemreference = (
                                                        self.structure.reference.opensystemreference
                                                    )
                                                except OpenSystemReference.DoesNotExist:
                                                    opensystemreference = OpenSystemReference(
                                                        structure_reference=self.structure.reference
                                                    )
                                                opensystemreference.identifier = (
                                                    reference
                                                )
                                                opensystemreference.id_integration = (
                                                    integration_id
                                                )
                                                opensystemreference.id_basket = (
                                                    basket_id
                                                )

                                                opensystemreference.save()

    def fairguest_metadata(self):
        if local_settings.IMPORT_FAIRGUEST_METADATA:
            try:
                fairguest_metadata = self.structure.reference.fairguestmetadata
            except FairGuestMetaData.DoesNotExist:
                fairguest_metadata = FairGuestMetaData(
                    structure_reference=self.structure.reference
                )

            if self.touristic_object.meta_data:
                meta_data = json.loads(self.touristic_object.meta_data)

                if len(meta_data) > 0:
                    for meta_data_node in meta_data:
                        if (
                            "noeudId" in meta_data_node
                            and meta_data_node["noeudId"] == "fairguest"
                        ):
                            meta_data_node_contents = meta_data_node.get("contenus", [])

                            for content in meta_data_node_contents:
                                content_meta = content.get("metadonnee", None)
                                if content_meta:
                                    fairguest_metadata.grade = content_meta.get("note")
                                    fairguest_metadata.label = content_meta.get(
                                        "label", ""
                                    )
                                    fairguest_metadata.color = content_meta.get(
                                        "couleur"
                                    )
                                    fairguest_metadata.comments_count = (
                                        content_meta.get("nombreAvis")
                                    )
                                    fairguest_metadata.date_updated = content_meta.get(
                                        "dateMaj"
                                    )

                                    fairguest_metadata.save()

    def activities(self):
        activities = self.structure.activity_set.all()
        # Update existing activities,
        if activities.exists():
            for activity in activities:
                activity_updater = ActivityUpdater(self.touristic_object, activity)
                activity_updater.update()
        # Creation
        else:
            activity_creator = ActivityCreator(
                self.touristic_object, self.structure, self.aspect
            )
            activity_creator.create()

    def _attach_contact(self, referent_contact, is_referent=False):
        structure_contact_object, _ = StructureContact.objects.get_or_create(
            structure=self.structure, contact=referent_contact
        )
        if is_referent is True:
            referent_structure_contacts = StructureContact.objects.filter(
                structure=self.structure, is_referent=True
            )
            for referent_structure_contact in referent_structure_contacts:
                referent_structure_contact.is_referent = False
                referent_structure_contact.save()

        structure_contact_object.is_referent = is_referent
        structure_contact_object.save()

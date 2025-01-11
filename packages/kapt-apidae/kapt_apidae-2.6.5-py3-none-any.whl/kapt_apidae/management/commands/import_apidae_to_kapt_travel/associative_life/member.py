# Third party
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from kapt_associative_life.models.member import MembershipStatus
from kapt_contact.models import COMPANY_LEGAL_FORM, ContactUser
from kapt_contact.models.contact import Individual, Institution
from kapt_geo.models import Country

# Local application / specific library imports
from kapt_apidae.conf import settings as apidae_settings
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.common import (
    update_contact_communication_infos,
)


class MemberUpdater:
    member = None
    touristic_object = None

    def __init__(self, member, touristic_object):
        self.member = member
        self.touristic_object = touristic_object

    def from_apidae_structure(self, apidae_structure):
        if self.member.id:
            self.member.referent_contact = (
                self._update_referent_contact_apidae_structure(
                    self.member.referent_contact, apidae_structure
                )
            )
        else:
            self.member.membership_status = self._get_membership_status()
            self.member.referent_contact = (
                self._update_referent_contact_apidae_structure(
                    Institution(), apidae_structure
                )
            )

        self.member.save()
        return self.member

    def from_apidae_object_owner(self, apidae_object_owner):
        if self.member.id:
            self.member.referent_contact = (
                self._update_referent_contact_from_apidae_object_owner(
                    self.member.referent_contact, apidae_object_owner
                )
            )
        else:
            self.member.membership_status = self._get_membership_status()
            self.member.referent_contact = (
                self._update_referent_contact_from_apidae_object_owner(
                    Institution(), apidae_object_owner
                )
            )
        self.member.save()
        return self.member

    def user(self):
        contact_object = self.member.referent_contact
        try:
            # Get or create by do not commit
            user = ContactUser.objects.get(contact=contact_object)
        except ObjectDoesNotExist:
            user = ContactUser(contact=contact_object)
            user.username = self.member.former_identifier
            user.save()
        return user

    def _update_referent_contact_from_apidae_object_owner(
        self, referent_contact, apidae_object_owner
    ):
        default_legal_form = COMPANY_LEGAL_FORM.NC

        referent_contact.company_name = apidae_object_owner.name
        if not referent_contact.id:
            referent_contact.company_legal_form = default_legal_form

        # Re-init contact
        referent_contact.address_1 = None
        referent_contact.address_2 = None
        referent_contact.zipcode = None
        referent_contact.city = None
        referent_contact.country = None
        referent_contact.first_phone_number = None
        referent_contact.second_phone_number = None
        referent_contact.fax_phone_number = None
        referent_contact.first_email = None
        referent_contact.second_email = None
        referent_contact.website_url = None
        referent_contact.save()
        return referent_contact

    def _update_referent_contact_apidae_structure(
        self, referent_contact, apidae_structure
    ):
        default_legal_form = COMPANY_LEGAL_FORM.NC

        referent_contact.company_name = apidae_structure.label_fr
        if not referent_contact.id:
            referent_contact.company_legal_form = default_legal_form

        # Re-init contact
        referent_contact.address_1 = None
        referent_contact.address_2 = None
        referent_contact.zipcode = None
        referent_contact.city = None
        referent_contact.country = None
        referent_contact.first_phone_number = None
        referent_contact.second_phone_number = None
        referent_contact.fax_phone_number = None
        referent_contact.first_email = None
        referent_contact.second_email = None
        referent_contact.website_url = None

        # Fill address
        if apidae_structure.address_1:
            referent_contact.address_1 = apidae_structure.address_1
            if apidae_structure.address_2:
                referent_contact.address_2 = apidae_structure.address_2
            elif apidae_structure.address_3:
                referent_contact.address_2 = apidae_structure.address_3
        elif apidae_structure.address_2:
            referent_contact.address_1 = apidae_structure.address_2
            if apidae_structure.address_3:
                referent_contact.address_2 = apidae_structure.address_3
        elif apidae_structure.address_3:
            referent_contact.address_1 = apidae_structure.address_3

        if apidae_structure.zip_code:
            referent_contact.zipcode = apidae_structure.zip_code

        if apidae_structure.locality:
            if apidae_structure.locality.name:
                referent_contact.city = apidae_structure.locality.name
            if apidae_structure.locality.country:
                if (
                    referent_contact._meta.get_field("country").get_internal_type()
                    == "ForeignKey"
                ):
                    countries = Country.objects.filter(
                        name=apidae_structure.locality.country.label_fr
                    )
                    if len(countries) > 0:
                        referent_contact.country = countries[0]
                else:
                    referent_contact.country = (
                        apidae_structure.locality.country.label_fr
                    )

        referent_contact = update_contact_communication_infos(
            referent_contact, apidae_structure.internal_communications.all()
        )
        referent_contact.save()

        # Unfortunately the only thing we can do is: remove all contacts and re-create them.
        for individual_contact in referent_contact.individual_set.all():
            individual_contact.delete()

        if apidae_structure.internal_contacts.exists():
            for apidae_contact in apidae_structure.internal_contacts.all():
                # Create individual contacts for this Institution
                individual_contact = Individual(gender=1)

                if apidae_contact.title_id == 441:
                    individual_contact.gender = 3
                if apidae_contact.title_id == 442:
                    individual_contact.gender = 2

                if apidae_contact.first_name:
                    individual_contact.first_name = apidae_contact.first_name
                if apidae_contact.last_name:
                    individual_contact.last_name = apidae_contact.last_name

                individual_contact = update_contact_communication_infos(
                    individual_contact, apidae_contact.internal_communications.all()
                )
                individual_contact.institution_id = referent_contact.id
                individual_contact.save()
        return referent_contact

    def _get_membership_status(self):
        if hasattr(settings, "KT_APIDAE_ADHERENT_VARIABLE_ATTRIBUTE") and hasattr(
            settings, "KT_APIDAE_TOURISM_OFFICE_AREA_ID"
        ):
            if self.touristic_object.variable_attributes.filter(
                label=settings.KT_APIDAE_ADHERENT_VARIABLE_ATTRIBUTE
            ).exists():
                if self.touristic_object.areas.filter(
                    id=settings.KT_APIDAE_TOURISM_OFFICE_AREA_ID
                ).exists():
                    return MembershipStatus.objects.get(
                        slug_identifier=apidae_settings.MEMBER_ON_AREA_STATUS
                    )
                else:
                    return MembershipStatus.objects.get(
                        slug_identifier=apidae_settings.MEMBER_OUTSIDE_AREA_STATUS
                    )
            else:
                return MembershipStatus.objects.get(
                    slug_identifier=apidae_settings.NOT_MEMBER_STATUS
                )
        return self._get_default_membership_status()

    def _get_default_membership_status(self):
        membership_status, created = MembershipStatus.objects.get_or_create(
            slug_identifier="adherent"
        )
        if created:
            membership_status.name_en = "Member"
            membership_status.name_fr = "Adhérent"
            membership_status.visible = 1
            membership_status.save()
        return membership_status

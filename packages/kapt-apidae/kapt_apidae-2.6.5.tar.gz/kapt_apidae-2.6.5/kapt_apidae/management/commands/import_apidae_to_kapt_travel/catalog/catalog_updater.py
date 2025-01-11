# Standard Library
from datetime import MAXYEAR, datetime
import logging

# Third party
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import get_default_timezone, make_aware, now
from kapt_associative_life.models.member import Member
from kapt_catalog.models.structure import Structure
from kapt_validity.models import Period

# Local application / specific library imports
from kapt_apidae.conf import settings as apidae_settings
from kapt_apidae.management import ScriptError
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.associative_life.member import (
    MemberUpdater,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.structure import (
    CatalogStructureUpdater,
)
from kapt_apidae.utils import model_field_exists


logger = logging.getLogger(__name__)


class CatalogUpdater:
    touristic_object = None
    structure_reference = None
    aspect = None

    def __init__(self, touristic_object, structure_reference, aspect=None):
        self.touristic_object = touristic_object
        self.structure_reference = structure_reference
        self.aspect = aspect

    def update_generic_touristic_object(
        self, cpt_to_added, cpt_to_modified, cpt_to_error
    ):
        try:
            # Update
            # Be sure, the first thing to do is to identify the member/contact etc.
            if self.touristic_object.management_organisation:
                # In this case, we have an Apidae "STRUCTURE", so we will retrieve the following member
                apidae_structure = self.touristic_object.management_organisation
                try:
                    member_object = Member.objects.get(
                        former_identifier=apidae_settings.APIDAE_FORMER_IDENTIFIER
                        % str(apidae_structure.id)
                    )
                except ObjectDoesNotExist:
                    member_object = Member(
                        former_identifier=apidae_settings.APIDAE_FORMER_IDENTIFIER
                        % str(apidae_structure.id)
                    )

                member_updater = MemberUpdater(member_object, self.touristic_object)
                member_object = member_updater.from_apidae_structure(apidae_structure)

            else:
                # Okay those kinds of objects have no structure, we will attach them to the object owner (e.g: the O.T)
                apidae_object_owner = self.touristic_object.owner

                try:
                    member_object = Member.objects.get(
                        former_identifier="APIDAE_MANAGER_%d" % apidae_object_owner.id
                    )
                except ObjectDoesNotExist:
                    member_object = Member(
                        former_identifier="APIDAE_MANAGER_%d" % apidae_object_owner.id
                    )

                member_updater = MemberUpdater(member_object, self.touristic_object)
                member_object = member_updater.from_apidae_object_owner(
                    apidae_object_owner
                )

            logger.debug("Working on id #" + str(self.structure_reference))

            # Add self.structure_reference to member
            member_object.structures_references.add(self.structure_reference)

            # Test if member has changed, remove the reference from the previous member
            old_members = self.structure_reference.member_set.exclude(
                pk=member_object.pk
            )
            for old_member in old_members:
                old_member.structures_references.remove(self.structure_reference)

            # User accounts generation
            member_updater.user()

            # Validity period from now until 01/01 of the next year
            validity_period = self._get_validity_period()

            # Get structure, for current validity period
            try:
                if model_field_exists(Structure, "aspect"):
                    structure = Structure.objects.get(
                        reference=self.structure_reference,
                        validity_period=validity_period,
                        aspect=self.aspect,
                    )
                else:
                    structure = Structure.objects.get(
                        reference=self.structure_reference,
                        validity_period=validity_period,
                    )
            except ObjectDoesNotExist:
                structure = Structure(
                    reference=self.structure_reference,
                    validity_period=validity_period,
                    aspect=self.aspect,
                )
                cpt_to_added += 1

            # From now on, we will update the structure and its associated objects only if no lock
            # is set on the structure reference
            if not self.structure_reference.external_lock:
                structure_updater = CatalogStructureUpdater(
                    structure, self.touristic_object, self.aspect
                )
                structure = structure_updater.update()
                cpt_to_modified += 1

        except ScriptError as e:
            cpt_to_error += 1
            logger.error(e)
            logger.error(str(e))
            return cpt_to_added, cpt_to_modified, cpt_to_error

        except Exception as e:
            logger.error(str(e))
            cpt_to_error += 1

            logger.exception(
                "ExceptionError on object id %s (%s)"
                % (self.touristic_object.id, self.touristic_object.label)
            )
            logger.exception(str(e))
            return cpt_to_added, cpt_to_modified, cpt_to_error

        return cpt_to_added, cpt_to_modified, cpt_to_error

    def _get_validity_period(self):
        # Until the end of times
        try:
            validity_period = Period.objects.get(
                formatted_identifier=apidae_settings.APIDAE_FORMER_IDENTIFIER
                % "VALIDITY"
            )
        except ObjectDoesNotExist:
            if Period.objects.filter(label="2015").exists():
                raise Exception(
                    "Validity period match an old format, please run kapt_apidae migrations"
                )

            validity_period = Period(
                label="Apidae",
                formatted_identifier=apidae_settings.APIDAE_FORMER_IDENTIFIER
                % "VALIDITY",
                valid_from=now(),
            )

            if settings.USE_TZ is True:
                validity_period.valid_until = make_aware(
                    datetime(MAXYEAR, 12, 30), get_default_timezone()
                )
            else:
                validity_period.valid_until = datetime(MAXYEAR, 12, 31, 23, 59, 59)
            validity_period.save()
        return validity_period

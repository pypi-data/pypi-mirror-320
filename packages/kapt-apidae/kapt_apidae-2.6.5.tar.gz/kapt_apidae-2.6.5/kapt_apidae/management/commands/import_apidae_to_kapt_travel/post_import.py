# Standard Library
import re

# Third party
from django.db.models import Count
from taggit.models import Tag

# Local application / specific library imports
from kapt_apidae.conf import settings as apidae_settings
from kapt_apidae.models import Area, Selection, TouristicObject, VariableAttribute


APIDAE_IN_KAPT_CATALOG = apidae_settings.APIDAE_IN_KAPT_CATALOG

TAGGED_MODELS = []
if APIDAE_IN_KAPT_CATALOG:
    from kapt_associative_life.models.profile import ActivityReferenceProfile
    from kapt_catalog.models.activities import Activity
    from kapt_catalog.models.reference import StructureReference

    from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.activities.common import (
        CommonActivityUpdater,
    )

    TAGGED_MODELS.append(StructureReference)


""" This file contains methods that must be run when the import has ended. """


# Tools
def apidae_former_id_to_int(former_identifier):
    int_identifier_regex = re.search(r"(\d+)", former_identifier)
    if not int_identifier_regex or not len(int_identifier_regex.groups()) == 1:
        raise Exception("Malformed identifier for object %s" % former_identifier)
    return int_identifier_regex.groups()[0]


def apidae_ids_to_int_ids(former_ids):
    ids = []
    for former_id in former_ids:
        int_id = apidae_former_id_to_int(former_id)
        ids.append(int_id)
    return ids


def update_tags():
    update_selections()
    update_variable_attributes()
    update_activity_flags()


def update_selections():
    # All objects that belongs to a selection must be tagged with something starting with SELECTION_TAG_PREFIX
    SELECTION_TAG_PREFIX = "selection_"

    # All selections
    apidae_selections = Selection.objects.all()

    # Removing selections
    # A list containing the name of all tags related to apidae selections.
    selections_tags_name = [
        "%s%d" % (SELECTION_TAG_PREFIX, selection_identifier)
        for selection_identifier in apidae_selections.values_list("id", flat=True)
    ]
    # Removing removed selections
    Tag.objects.filter(name__startswith=SELECTION_TAG_PREFIX).exclude(
        name__in=selections_tags_name
    ).delete()

    # Add/delete tags foreach selection
    for apidae_selection in apidae_selections:
        # The name of the tag used to describe the selection
        selection_tag_name = "%s%d" % (SELECTION_TAG_PREFIX, apidae_selection.id)

        for tagged_model in TAGGED_MODELS:
            # All the objects of the current model tagged with this selection
            tagged_references = tagged_model.objects.filter(
                tags__name=selection_tag_name
            )

            # The ids of the objects in the selection, in apidae database
            selection_objects_id = apidae_selection.touristic_objects.values_list(
                "apidae_identifier", flat=True
            )

            # The former identifiers for all the objects belonging to the selection
            selection_former_identifiers = [
                apidae_settings.APIDAE_FORMER_IDENTIFIER % apidae_identifier
                for apidae_identifier in selection_objects_id
            ]

            # The list of objects that must be tagged
            references_to_tag = tagged_model.objects.filter(
                former_identifier__in=selection_former_identifiers
            )

            # Add tag to the objects that exists in our database and that need to be inside the selection
            for obj in references_to_tag:
                obj.tags.add(selection_tag_name)

            # Remove tag for the objects removed from the selection
            for obj in tagged_references.exclude(
                former_identifier__in=selection_former_identifiers
            ):
                obj.tags.remove(selection_tag_name)


def update_variable_attributes():
    # All objects that belongs to a variable attribute must be tagged with something starting with VARIABLE_ATTRIBUTE_TAG_PREFIX
    VARIABLE_ATTRIBUTE_TAG_PREFIX = "attribute_"

    # All variable attributes
    apidae_variable_attributes = VariableAttribute.objects.all()

    # Removing variable attributes
    # A list containing the name of all tags related to apidae variable attributes.
    variable_attributes_tags_name = [
        "%s%d" % (VARIABLE_ATTRIBUTE_TAG_PREFIX, variable_attribute_identifier)
        for variable_attribute_identifier in apidae_variable_attributes.values_list(
            "id", flat=True
        )
    ]

    # Removing removed selections
    Tag.objects.filter(name__startswith=VARIABLE_ATTRIBUTE_TAG_PREFIX).exclude(
        name__in=variable_attributes_tags_name
    ).delete()

    # Add/delete tags foreach variable attribute
    for apidae_variable_attribute in apidae_variable_attributes:
        # The name of the tag used to describe the variable attribute
        variable_attribute_tag_name = "%s%d" % (
            VARIABLE_ATTRIBUTE_TAG_PREFIX,
            apidae_variable_attribute.id,
        )

        for tagged_model in TAGGED_MODELS:
            # All the models objects of the current model with this variable attribute
            tagged_references = tagged_model.objects.filter(
                tags__name=variable_attribute_tag_name
            )

            # The ids of the objects in the selection, in apidae database
            variable_attribute_objects_id = (
                apidae_variable_attribute.touristicobject_set.values_list(
                    "apidae_identifier", flat=True
                )
            )

            # The former identifiers for all the objects belonging to this variable attribute
            variable_attribute_former_identifiers = [
                apidae_settings.APIDAE_FORMER_IDENTIFIER % apidae_identifier
                for apidae_identifier in variable_attribute_objects_id
            ]

            # The list of objects that must be tagged
            references_to_tag = tagged_model.objects.filter(
                former_identifier__in=variable_attribute_former_identifiers
            )

            # Add tag to the objects that exists in our database and that need to be tagged with this variable attribute
            for obj in references_to_tag:
                obj.tags.add(variable_attribute_tag_name)

            # Remove tag for the objects removed from this variable attribute tagging
            for obj in tagged_references.exclude(
                former_identifier__in=variable_attribute_former_identifiers
            ):
                obj.tags.remove(variable_attribute_tag_name)


def update_activity_flags():
    if apidae_settings.ADHERENT_VARIABLE_ATTRIBUTE is not None:
        if not isinstance(apidae_settings.ADHERENT_VARIABLE_ATTRIBUTE, list):
            adherent_variable_attribute_list = [
                apidae_settings.ADHERENT_VARIABLE_ATTRIBUTE
            ]
        else:
            adherent_variable_attribute_list = (
                apidae_settings.ADHERENT_VARIABLE_ATTRIBUTE
            )

        member_attributes = VariableAttribute.objects.filter(
            label__in=adherent_variable_attribute_list
        ).values_list("id", flat=True)
        touristic_objects_id = TouristicObject.objects.filter(
            variable_attributes__pk__in=member_attributes
        ).values_list("apidae_identifier", flat=True)

        # All the models objects of the current model tagged for this area
        flagged_activities = Activity.objects.filter(
            reference__profile__is_registered=True
        )

        # The former identifiers for all the objects belonging to this variable attribute
        references_former_identifiers = [
            apidae_settings.APIDAE_FORMER_IDENTIFIER % apidae_identifier
            for apidae_identifier in touristic_objects_id
        ]

        # The list of activities that must be flagged
        activities_to_flag = Activity.objects.filter(
            structure__reference__former_identifier__in=references_former_identifiers
        )

        for activity in activities_to_flag:
            try:
                common_activity_updater = CommonActivityUpdater(None, activity)
                activity.reference.profile.is_registered = True
                activity.reference.profile.status = (
                    ActivityReferenceProfile.STATUS.classical_registration
                )
                activity.reference.profile.save()
                common_activity_updater.save_activity()
            except (AssertionError, ActivityReferenceProfile.DoesNotExist):
                pass

        for activity in flagged_activities.exclude(
            structure__reference__former_identifier__in=references_former_identifiers
        ):
            try:
                common_activity_updater = CommonActivityUpdater(None, activity)
                activity.reference.profile.is_registered = False
                activity.reference.profile.status = (
                    ActivityReferenceProfile.STATUS.no_registration
                )
                activity.reference.profile.save()
                common_activity_updater.save_activity()
            except (AssertionError, ActivityReferenceProfile.DoesNotExist):
                pass

    if apidae_settings.AREA_ID:
        area_obj = Area.objects.get(apidae_identifier=apidae_settings.AREA_ID)

        # All the models objects of the current model tagged for this area
        flagged_activities = Activity.objects.filter(reference__profile__on_area=True)

        # The ids of the objects in the territory, in apidae database
        area_apidae_objects_id = area_obj.area_objects_set.values_list(
            "apidae_identifier", flat=True
        )

        # The former identifiers for all the objects belonging to this variable attribute
        area_former_identifiers = [
            apidae_settings.APIDAE_FORMER_IDENTIFIER % apidae_identifier
            for apidae_identifier in area_apidae_objects_id
        ]

        # The list of objects that own activities that must be flagged
        activities_to_flag = Activity.objects.filter(
            structure__reference__former_identifier__in=area_former_identifiers
        )

        for activity in activities_to_flag:
            try:
                common_activity_updater = CommonActivityUpdater(None, activity)
                activity.reference.profile.on_area = True
                activity.reference.profile.save()
                common_activity_updater.save_activity()
            except (AssertionError, ActivityReferenceProfile.DoesNotExist):
                pass

        for activity in flagged_activities.exclude(
            structure__reference__former_identifier__in=area_former_identifiers
        ):
            try:
                common_activity_updater = CommonActivityUpdater(None, activity)
                activity.reference.profile.on_area = False
                activity.reference.profile.save()
                common_activity_updater.save_activity()
            except (AssertionError, ActivityReferenceProfile.DoesNotExist):
                pass


def remove_empty_gallery():
    for sr in StructureReference.objects.filter(is_active=False):
        if sr.structure_set.exists():
            if sr.structure_set.first().gallery:
                for media in sr.structure_set.first().gallery.media_links.all():
                    media.delete()
                for plan in sr.structure_set.first().gallery.plan_set.all():
                    plan.delete()
                for photo in sr.structure_set.first().gallery.photo_set.all():
                    photo.delete()


def deactivate_deleted_touristic_object():
    for tagged_model in TAGGED_MODELS:
        # KAPTravel data
        local_data = tagged_model.objects.all()
        # KAPTAPidae data
        referent_data = TouristicObject.objects.annotate(
            selections_count=Count("selection")
        ).filter(selections_count__gt=0)

        # KAPTApidae data tagged like in KAPTravel : APIDAE_
        referent_tagged_data = [
            apidae_settings.APIDAE_FORMER_IDENTIFIER % (identifier)
            for identifier in referent_data.values_list("apidae_identifier", flat=True)
        ]

        # Activate all KAPTAPidae touristic_objects
        for reference in local_data.filter(
            former_identifier__startswith=apidae_settings.APIDAE_PREFIX,
            former_identifier__in=referent_tagged_data,
        ):
            reference.is_active = True
            reference.save()

        # Deactivate removed touristic_object in KAPTApidae
        for reference in local_data.filter(
            former_identifier__startswith=apidae_settings.APIDAE_PREFIX
        ).exclude(former_identifier__in=referent_tagged_data):
            reference.is_active = False
            reference.save()

        referent_tagged_data = [
            apidae_settings.APIDAE_FORMER_IDENTIFIER % (identifier)
            for identifier in referent_data.filter(
                publication_state="HIDDEN"
            ).values_list("apidae_identifier", flat=True)
        ]
        # Desactivate HIDDEN objects in kapt_apidae
        for reference in local_data.filter(
            former_identifier__startswith=apidae_settings.APIDAE_PREFIX,
            former_identifier__in=referent_tagged_data,
        ):
            reference.is_active = False
            reference.save()


def link_activities():
    activities = Activity.objects.select_related("structure__reference").filter(
        structure__reference__is_active=True,
        structure__reference__former_identifier__startswith=apidae_settings.APIDAE_PREFIX,
    )

    for activity in activities:
        # Retrieve the Apidae related object
        structurereference_former_id = activity.structure.reference.former_identifier
        touristic_object_id = apidae_former_id_to_int(structurereference_former_id)
        touristic_object = TouristicObject.objects.get(
            apidae_identifier=touristic_object_id, aspect=activity.aspect
        )

        # The linked objects in Apidae object
        linked_objects_ids = touristic_object.linked_objects.values_list(
            "apidae_identifier", flat=True
        )

        # Create the former identifiers
        if linked_objects_ids:
            linked_objects_former_identifiers = [
                apidae_settings.APIDAE_FORMER_IDENTIFIER % ident
                for ident in linked_objects_ids
            ]

        activity.linked_activityreferences.clear()

        # Retrieve the related StructureReference and fill linked_structurereferences_formeridentifiers_ids
        if linked_objects_ids:
            linked_activities = Activity.objects.filter(
                reference__structure_reference__former_identifier__in=linked_objects_former_identifiers,
                reference__structure_reference__is_active=True,
            )

            for linked_activity in linked_activities:
                activity.linked_activityreferences.add(linked_activity.reference)

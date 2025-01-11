# Third party
from django.utils.translation import activate, get_language
from kapt_catalog.models import Activity

# Local application / specific library imports
from kapt_apidae.conf import settings as apidae_settings
from kapt_apidae.models import Description, LinkType, TouristicObject


def get_apidae_object(activity):
    return activity.apidae_touristic_objects.filter(aspect=activity.aspect).first()


def get_linked_objects(activity, link_type=None, apidae_object=None):
    """Use like this in kapt_catalog :
    from kapt_apidae.requests import get_linked_objects
    linked_objects = get_linked_objects(activity)
    """
    if apidae_object is None:
        apidae_object = get_apidae_object(activity)

    if apidae_object is None:
        return []

    linked_objects_id = []
    if link_type:
        linked_objects_id = LinkType.objects.filter(
            touristic_object=apidae_object, link_type=link_type
        ).values_list("touristic_linked_object_id", flat=True)
    else:
        linked_objects_id = LinkType.objects.filter(
            touristic_object=apidae_object
        ).values_list("touristic_linked_object_id", flat=True)
    # We append former identifier to results
    linked_objects = TouristicObject.objects.filter(
        pk__in=linked_objects_id
    ).values_list("apidae_identifier", flat=True)
    linked_objects_references = map(
        lambda x: apidae_settings.APIDAE_FORMER_IDENTIFIER % (x), linked_objects
    )

    try:
        return Activity.no_aspects.filter(
            structure__reference__former_identifier__in=linked_objects_references
        )
    except AttributeError:
        return Activity.objects.filter(
            structure__reference__former_identifier__in=linked_objects_references
        )


def get_private_descriptions(activity, private_type, language=None, apidae_object=None):
    """Use like this in kapt_catalog :
    from kapt_apidae.requests import get_private_descriptions
    private_descriptions = get_private_descriptions(activity, "XXXXXX")
    """

    if apidae_object is None:
        apidae_object = get_apidae_object(activity)

    if apidae_object is None:
        return None

    try:
        if language:
            initial_language = get_language()
            activate(language)
            private_description = getattr(
                apidae_object.descriptions.get(label=private_type), "text"
            )
            activate(initial_language)
        else:
            private_description = getattr(
                apidae_object.descriptions.get(label=private_type), "text"
            )
        return private_description
    except Description.DoesNotExist:
        return


def get_thematic_descriptions(activity, thematic_id, language=None, apidae_object=None):
    """Use like this in kapt_catalog :
    from kapt_apidae.requests import get_thematic_descriptions
    private_descriptions = get_thematic_descriptions(activity, "XXXXXX")
    """

    if apidae_object is None:
        apidae_object = get_apidae_object(activity)

    if apidae_object is None:
        return None

    try:
        if language:
            initial_language = get_language()
            activate(language)
            private_description = getattr(
                apidae_object.descriptions.get(theme_id=thematic_id), "text"
            )
            activate(initial_language)
        else:
            private_description = getattr(
                apidae_object.descriptions.get(theme_id=thematic_id), "text"
            )
        return private_description
    except Description.DoesNotExist:
        return


def get_all_thematic_descriptions(activity, apidae_object=None):
    """Use like this in kapt_catalog :
    from kapt_apidae.requests import get_all_thematic_descriptions
    thematic_descriptions = get_all_thematic_descriptions(activity)
    """

    if apidae_object is None:
        apidae_object = get_apidae_object(activity)

    if apidae_object is None:
        return None

    thematic_descriptions = apidae_object.descriptions.filter(
        theme__isnull=False
    ).select_related("theme")

    return thematic_descriptions


def get_apidae_field(activity, field, apidae_object=None):
    """Use like this in kapt_catalog :
    from kapt_apidae.requests import get_apidae_field
    field_value = get_apidae_field(activity, field)
    """

    if apidae_object is None:
        apidae_object = get_apidae_object(activity)

    if apidae_object is None:
        return None

    return getattr(apidae_object, field, None)

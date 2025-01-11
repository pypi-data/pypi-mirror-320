# Standard Library
import json

# Third party
from django.core.exceptions import ObjectDoesNotExist
from kapt_catalog.models import StructureReference
from taggit.models import Tag

# Local application / specific library imports
# Local
from kapt_apidae.conf import settings as apidae_settings
from kapt_apidae.management import logger
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.post_import import (
    apidae_former_id_to_int,
)
from kapt_apidae.models import Selection


class CoherenceTester:
    selection_file = None

    def __init__(self, selection_file):
        super().__init__()
        self.selection_file = selection_file

    def check_selections(self):
        logger.info("Starting checking selections from {}".format(self.selection_file))

        json_file = open(self.selection_file)
        selections_from_file = json.load(json_file)
        json_file.close()

        selections_ids = []
        for selection in selections_from_file:
            selection_id = selection["id"]
            selections_ids.append(selection_id)
            if "objetsTouristiques" in selection:
                selection_objets = selection["objetsTouristiques"]
                selection_name = selection["nom"]

                logger.info(
                    "Checking selection %d - %s" % (selection_id, selection_name)
                )

                try:
                    selection_object = Selection.objects.get(pk=selection_id)
                except ObjectDoesNotExist as e:
                    raise e

                try:
                    tag_object = Tag.objects.get(name="selection_%s" % selection_id)
                except ObjectDoesNotExist as e:
                    raise e

                logger.info("Retrieved selection from kaptravel and kapt-apidae -> OK")

                selection_structurereferences = StructureReference.objects.filter(
                    tags__name=tag_object.name
                )
                selection_tourisitic_object_ids = []
                apidae_ignored_touristic_object_cpt = 0
                kapt_travel_ignored_touristic_object_cpt = 0

                for tourisitic_object in selection_objets:
                    tourisitic_object_id = tourisitic_object["id"]
                    selection_tourisitic_object_ids.append(int(tourisitic_object_id))

                    try:
                        selection_object.touristic_objects.get(
                            apidae_identifier=tourisitic_object_id
                        )
                    except ObjectDoesNotExist as e:
                        if apidae_settings.IGNORE_LIST is not None:
                            if tourisitic_object_id in apidae_settings.IGNORE_LIST:
                                logger.warning(
                                    "tourisitic object id: {} ignored (Found in IGNORE_LIST)".format(
                                        tourisitic_object_id
                                    )
                                )
                                apidae_ignored_touristic_object_cpt += 1
                                continue

                        logger.error(
                            "Tourisitic object id: {} not found...".format(
                                tourisitic_object_id
                            )
                        )
                        raise e

                    structurereference = selection_structurereferences.filter(
                        former_identifier=apidae_settings.APIDAE_FORMER_IDENTIFIER
                        % tourisitic_object_id
                    )

                    if structurereference.count() == 0:
                        if tourisitic_object_id in apidae_settings.IGNORE_LIST:
                            kapt_travel_ignored_touristic_object_cpt += 1
                        else:
                            raise Exception(
                                "Object #{} not tagged with selection {}".format(
                                    tourisitic_object_id, selection_id
                                )
                            )

                if (
                    selection_object.touristic_objects.count()
                    != len(selection_objets) - apidae_ignored_touristic_object_cpt
                ):
                    raise Exception(
                        "Invalid count between selection {} and kapt_apidae import".format(
                            selection_object
                        )
                    )

                if (
                    selection_structurereferences.count()
                    != len(selection_objets) - kapt_travel_ignored_touristic_object_cpt
                ):
                    raise Exception(
                        "Invalid count between selection {} and kaptravel import".format(
                            selection_object
                        )
                    )

                for structurereference in selection_structurereferences:
                    apidae_id = int(
                        apidae_former_id_to_int(structurereference.former_identifier)
                    )

                    if apidae_id not in selection_tourisitic_object_ids:
                        raise Exception(
                            "StructureReference {} is in selection {} but shouldn't".format(
                                structurereference.former_identifier, selection_id
                            )
                        )

        selection_tags = [
            "selection_{}".format(temp_selection_id)
            for temp_selection_id in selections_ids
        ]
        out_of_date_tags = Tag.objects.filter(name__startswith="selection_").exclude(
            name__in=selection_tags
        )
        if out_of_date_tags.exists():
            raise Exception(
                "Some deleted selections still exists in kapt_catalog {}".format(
                    out_of_date_tags.values_list("name", flat=True)
                )
            )

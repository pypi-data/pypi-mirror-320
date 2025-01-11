# Standard Library
from datetime import datetime
import json
import logging
import math
import sys

# Third party
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Count
from django.utils import translation
from django.utils.timezone import get_default_timezone, make_aware
from kapt_catalog.models.reference import StructureReference

# Local application / specific library imports
from kapt_apidae.conf import settings as kapt_apidae_settings
from kapt_apidae.core.exceptions import (
    ObjectUnchangedException,
    ObjectUpdateFailedException,
)
from kapt_apidae.management import ScriptError
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.catalog_updater import (
    CatalogUpdater,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.catalog.characteristics.characteristics_generator import (
    CharacteristicsGenerator,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.post_import import (
    deactivate_deleted_touristic_object,
    link_activities,
    remove_empty_gallery,
    update_tags,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.testing import (
    CoherenceTester,
)
from kapt_apidae.models import ImportApidaeKaptravelLog, TouristicObject
from kapt_apidae.utils import get_aspect_id


DEFAULT_TZ = get_default_timezone()
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Import tourism object from Kapt-apidae"

    database_logger = None
    cpt_to_added = 0
    cpt_to_modified = 0
    cpt_to_error = 0

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            "-o",
            "--only",
            dest="only",
            nargs="+",
            default=False,
            help="Import TouristicObject from kapt-apidae (only the given ids list)",
        )
        parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            dest="force",
            default=False,
            help="Import TouristicObject from kapt-apidae (force all objects, use gt=id to restart from a given id)",
        )
        parser.add_argument(
            "-d",
            "--differential",
            action="store_true",
            dest="differential",
            default=False,
            help="Import TouristicObject from kapt-apidae (differential mode)",
        )
        parser.add_argument(
            "-p",
            "--post_import",
            action="store_true",
            dest="post_import",
            default=False,
            help="Run only post import operations",
        )
        parser.add_argument(
            "-i",
            "--init",
            action="store_true",
            dest="init_parameters",
            default=False,
            help="Init database for kapt-apidae",
        )
        parser.add_argument(
            "-c",
            "--coherence",
            nargs="+",
            dest="coherence",
            default=False,
            help="Check kapt_catalog coherence, based on a selection file",
        )

    def handle(self, *args, **options):
        if self._init_script(args, options) is False:
            return
        if options["init_parameters"]:
            self._generate_characteristics()
            self._init_import()

        if options["only"] or options["force"] or options["differential"]:
            self._import_apidae_kaptravel(args, options)

        if options["post_import"]:
            self._post_import()

        if options["coherence"]:
            self._check_coherence(options["coherence"])

        self._end_script()

    def _get_database_logger(self):
        if self.database_logger:
            database_logger = self.database_logger
        else:
            database_logger = ImportApidaeKaptravelLog.objects.create()
            self.database_logger = database_logger
        return database_logger

    def _init_script(self, args, options):
        argv = sys.argv[:]
        if (
            not options["only"]
            and not options["force"]
            and not options["differential"]
            and not options["post_import"]
            and not options["init_parameters"]
            and not options["coherence"]
        ):
            self.print_help(argv[0], argv[1])
            return False

        database_logger = self._get_database_logger()
        database_logger.launch_date = make_aware(datetime.now(), DEFAULT_TZ)
        launch_options = {"options": options, "args": args}
        database_logger = self._get_database_logger()
        database_logger.launch_options = json.dumps(launch_options)
        database_logger.save()

        logger.info("------------------------------------------------------")
        logger.info("Launched import_apidae_to_kapt_travel script")
        logger.info("------------------------------------------------------")
        logger.info(
            "Script launched at {}".format(
                database_logger.launch_date.strftime("%d/%m/%y %H:%M:%S")
            )
        )

        # If not set, activate the translation for the given thread
        current_language = translation.get_language()
        if current_language is None:
            translation.activate(settings.LANGUAGE_CODE)

    def _end_script(self):
        database_logger = self._get_database_logger()

        database_logger.end_date = make_aware(datetime.now(), DEFAULT_TZ)
        duration = database_logger.end_date - database_logger.launch_date

        database_logger.duration = int(math.ceil(duration.total_seconds()))
        database_logger.objects_modified = self.cpt_to_modified
        database_logger.objects_added = self.cpt_to_added
        database_logger.errors = self.cpt_to_error
        database_logger.save()

        logger.info(
            "Script terminated at {} in {} seconds".format(
                database_logger.end_date.strftime("%d/%m/%y %H:%M:%S"),
                database_logger.duration,
            )
        )
        logger.info("")
        logger.info(">> %d TouristicObject modified", database_logger.objects_modified)
        logger.info(">> %d TouristicObject added", database_logger.objects_added)
        logger.info(">> %d TouristicObject error", database_logger.errors)

    def _import_apidae_kaptravel(self, args, options):
        try:
            touristic_object_queryset = None
            if options["only"]:
                touristic_object_queryset = list(
                    TouristicObject.objects.filter(
                        apidae_identifier__in=options["only"], aspect__isnull=True
                    ).values_list("apidae_identifier", flat=True)
                )
                if len(touristic_object_queryset) < len(options["only"]):
                    logger.warning(
                        "One or several provided id(s) is/are wrong ! Please be sure that those objects are in kapt_apidae tables"
                    )

                logger.info("Limited import :")
                for i in range(0, len(options["only"])):
                    logger.info("   * " + str(options["only"][i]))

            elif options["force"] or options["differential"]:
                touristic_object_queryset = list(
                    TouristicObject.objects.annotate(
                        selections_count=Count("selection")
                    )
                    .filter(selections_count__gt=0)
                    .values_list("apidae_identifier", flat=True)
                )
                if kapt_apidae_settings.IGNORE_LIST is not None:
                    for apidae_identifier in kapt_apidae_settings.IGNORE_LIST:
                        try:
                            touristic_object_queryset.remove(apidae_identifier)
                        except ValueError:
                            logger.warning(
                                "Touristic object {} is not anymore in selection, you can remove it from IGNORE_LIST".format(
                                    apidae_identifier
                                )
                            )
                    logger.warning(
                        "{} Touristic Object are ignored !".format(
                            len(kapt_apidae_settings.IGNORE_LIST)
                        )
                    )
                    for i in kapt_apidae_settings.IGNORE_LIST:
                        logger.warning("   * " + str(i))

            if touristic_object_queryset and len(touristic_object_queryset) > 0:
                logger.info(
                    "Updating data for up to {} objects".format(
                        len(touristic_object_queryset)
                    )
                )
                logger.info("Importing kapt_apidae objects in kaptravel")

                (
                    cpt_to_added,
                    cpt_to_modified,
                    cpt_to_error,
                ) = self._update_kaptravel_from_queryset(
                    touristic_object_queryset, options["differential"]
                )

                self.cpt_to_added = cpt_to_added
                self.cpt_to_modified = cpt_to_modified
                self.cpt_to_error = cpt_to_error

            elif not options["post_import"]:
                raise ScriptError(
                    "No Apidae TouristicObject in the QuerySet, please be sure that the kapt_apidae.import_apidae script has been run",
                    None,
                )

            if options["force"] or options["differential"]:
                self._post_import()

        except KeyboardInterrupt:
            pass

        except Exception as e:
            logger.error(e)
            raise

    def _post_import(self):
        logger.info("Running post import operations")
        try:
            update_tags()
            deactivate_deleted_touristic_object()
            remove_empty_gallery()
            link_activities()
        except Exception as e:
            logger.error(e)
            raise

    def _generate_characteristics(self):
        """Generate dictionaries of facilities and services"""
        logger.info("Generating characteristics file")
        generator = CharacteristicsGenerator(
            generated_file="characteristics/generated_characteristics.py"
        )
        generator.generate()

    def _init_import(self):
        logger.info("Initializing import script data")
        from kapt_apidae.management.commands.import_apidae_to_kapt_travel.utils import (
            init_import,
        )

        try:
            init_import()
        except Exception as e:
            logger.error(e)
            raise

    def _update_kaptravel_from_queryset(
        self, touristic_object_identifier_list, differential_mode
    ):
        cpt_to_added = cpt_to_modified = cpt_to_error = 0
        for touristic_object_identifier in touristic_object_identifier_list:
            try:
                # Get general object
                touristic_object = TouristicObject.objects.get(
                    apidae_identifier=touristic_object_identifier, aspect__isnull=True
                )
                with transaction.atomic():
                    # Get reference
                    structure_reference, _ = StructureReference.objects.get_or_create(
                        former_identifier=kapt_apidae_settings.APIDAE_FORMER_IDENTIFIER
                        % str(touristic_object_identifier)
                    )

                    if structure_reference.identifier is None:
                        structure_reference.identifier = touristic_object_identifier
                        structure_reference.save()

                    # Differential mode
                    if (
                        differential_mode
                        and structure_reference.last_import
                        == touristic_object.last_update
                    ):
                        raise ObjectUnchangedException("Object hasn't changed")

                    logger.info(
                        "Starting updating {} #{}".format(
                            touristic_object.__class__.__name__,
                            touristic_object_identifier,
                        )
                    )
                    updater = CatalogUpdater(touristic_object, structure_reference)
                    previous_cpt_to_error = cpt_to_error
                    (
                        cpt_to_added,
                        cpt_to_modified,
                        cpt_to_error,
                    ) = updater.update_generic_touristic_object(
                        cpt_to_added, cpt_to_modified, cpt_to_error
                    )

                    if kapt_apidae_settings.ASPECTS:
                        for aspect in kapt_apidae_settings.ASPECTS:
                            # Get aspect object
                            try:
                                touristic_object = TouristicObject.objects.get(
                                    apidae_identifier=touristic_object_identifier,
                                    aspect=get_aspect_id(aspect),
                                )
                                logger.info(
                                    "With aspect {} : Starting updating {} #{}".format(
                                        aspect,
                                        touristic_object.__class__.__name__,
                                        touristic_object_identifier,
                                    )
                                )
                                updater = CatalogUpdater(
                                    touristic_object,
                                    structure_reference,
                                    get_aspect_id(aspect),
                                )
                                (
                                    cpt_to_added,
                                    cpt_to_modified,
                                    cpt_to_error,
                                ) = updater.update_generic_touristic_object(
                                    cpt_to_added, cpt_to_modified, cpt_to_error
                                )
                            except TouristicObject.DoesNotExist:
                                pass

                    if previous_cpt_to_error == cpt_to_error:
                        structure_reference.last_import = touristic_object.last_update
                        structure_reference.save()
                    else:
                        raise ObjectUpdateFailedException
            except (ObjectUnchangedException, ObjectUpdateFailedException):
                # Logger has already been alerted of the problem, skip the object and go on the next loop
                pass
            except TouristicObject.DoesNotExist:
                if aspect is None:
                    logger.error(
                        "TouristicObject #{} not found".format(
                            touristic_object_identifier
                        )
                    )
                else:
                    pass
        return cpt_to_added, cpt_to_modified, cpt_to_error

    def _check_coherence(self, path):
        logger.info("Checking kapt_catalog coherence")
        if not path:
            logger.error("You must provide path to selections file you want to check")
            return

        try:
            tester = CoherenceTester(selection_file=path)
            tester.check_selections()
            database_logger = self._get_database_logger()
            database_logger.coherence_test_passed = True
            database_logger.save()
        except Exception as e:
            logger.error(e)
            raise

# Standard Library
import datetime
import json
import logging
import os
import re
import shutil
from zipfile import ZipFile

# Third party
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import mail_admins
from django.core.management import call_command
from django.core.management.base import BaseCommand
import requests

# Local application / specific library imports
from kapt_apidae.conf import settings as kapt_apidae_settings
from kapt_apidae.management import print_progress
from kapt_apidae.models import (
    BaseElement,
    ImportsApidaeSettings,
    Locality,
    Selection,
    TouristicObject,
    VariableAttribute,
)
from kapt_apidae.utils import get_aspect_id, get_touristic_object_model_class


logger = logging.getLogger(__name__)

# Reading section
JSON_FILES = {
    "base_elements": "elements_reference.json",
    "localities": "communes.json",
    "areas": "territoires.json",
    "internal_criterias": "criteres_internes.json",
    "objects_selection": "selections.json",
    "removed_linked_objects": "objets_lies_supprimes.json",
    "removed_touristical_objects": "objets_supprimes.json",
    "linked_objects": "objets_lies/objets_lies_modifies-%d.json",
    "modified_objects": "objets_modifies/objets_modifies-%d.json",
}

JSON_FOLDERS = {"linked_objects": "objets_lies", "modified_objects": "objets_modifies"}

# Contains the touristical objects types and indicate whether they are linked objects or not
TOURISTICAL_OBJECTS_TYPE = {"linked_objects": True, "modified_objects": False}

JSON_FILES_REGEX = {
    "linked_objects": r"objets_lies_modifies-(\d+)\.json",
    "modified_objects": r"objets_modifies-(\d+)\.json",
}

# Folders path
DOWNLOAD_FOLDER = "%s/exports/kapt-apidae/zip_files/" % settings.PROJECT_PATH

EXPORT_FOLDER = "%s/exports/kapt-apidae/json/" % settings.PROJECT_PATH


# Returns the ids list for a given object type: linked_objects or modified_objects
def get_objects_ids(objects_type):
    folder_name = JSON_FOLDERS[objects_type]
    files_folder = EXPORT_FOLDER
    folder_absolute_path = "{}{}".format(files_folder, folder_name)
    file_regex = JSON_FILES_REGEX[objects_type]
    ids_list = []
    if os.path.exists(folder_absolute_path):
        dir_content = os.listdir(folder_absolute_path)
        for file_name in dir_content:
            ids_list.append(int(re.search(file_regex, file_name).group(1)))
    return ids_list


def get_json_aspect(aspect_name, json_as_object):
    aspect_found = False
    try:
        if "aspects" in json_as_object.keys():
            for aspect in json_as_object["aspects"]:
                if aspect["aspect"] == aspect_name:
                    aspect_found = True
                    for key in aspect["champsAspect"]:
                        fields = key.split(".")
                        node_value = aspect
                        node_to_modify = json_as_object
                        for field in fields:
                            try:
                                node_value = node_value[field]
                            except KeyError:
                                node_value = None
                        for field in fields[:-1]:
                            try:
                                node_to_modify = node_to_modify[field]
                            except KeyError:
                                node_to_modify[field] = {}
                                node_to_modify = node_to_modify[field]
                        node_to_modify[fields[-1]] = node_value
            json_as_object.pop("aspects", None)
    except AttributeError:
        pass

    return json_as_object, aspect_found


# Returns the content of a json file
def get_json_content(file_name, object_id=None, aspect=None):
    files_folder = EXPORT_FOLDER
    json_relative_path = JSON_FILES[file_name]
    if object_id:
        json_relative_path = json_relative_path % object_id
    json_absolute_path = "{}{}".format(files_folder, json_relative_path)
    try:
        with open(json_absolute_path) as json_file:
            json_as_object = json.load(json_file)
            if kapt_apidae_settings.ASPECT:
                json_as_object, aspect_found = get_json_aspect(
                    kapt_apidae_settings.ASPECT, json_as_object
                )
            if aspect:
                json_as_object, aspect_found = get_json_aspect(aspect, json_as_object)
                # Only in this case we return if the aspect has been find
                return json_as_object, aspect_found
    except OSError:
        json_as_object = []
    return json_as_object


class Command(BaseCommand):
    args = "<directory>"
    help = "Import APIDAE objects into the database"

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            "-b",
            "--base",
            action="store_true",
            dest="base_elements",
            default=False,
            help="Import base elements",
        )
        parser.add_argument(
            "-m",
            "--municipalities",
            action="store_true",
            dest="municipalities",
            default=False,
            help="Import municipalities",
        )
        parser.add_argument(
            "-c",
            "--variableattributes",
            action="store_true",
            dest="variable_attributes",
            default=False,
            help="Import variable attributes",
        )
        parser.add_argument(
            "-t",
            "--territory",
            action="store_true",
            dest="areas",
            default=False,
            help="Import areas",
        )
        parser.add_argument(
            "-l",
            "--linked_objects",
            action="store_true",
            dest="linked",
            default=False,
            help="Import linked objects (pointed by primary objects)",
        )
        parser.add_argument(
            "-p",
            "--primary_objects",
            nargs="*",
            dest="primary",
            default=False,
            help="Import primary objects (objects selected by our client)",
        )
        parser.add_argument(
            "-r",
            "--remove",
            action="store_true",
            dest="remove",
            default=False,
            help="Remove out of date APIDAE objects",
        )
        parser.add_argument(
            "-s",
            "--selections",
            action="store_true",
            dest="selections",
            default=False,
            help="Import apidae selections",
        )
        parser.add_argument(
            "-a",
            "--all",
            action="store_true",
            dest="all",
            default=False,
            help="Re-import all datas",
        )
        parser.add_argument(
            "-d",
            "--daily",
            action="store_true",
            dest="daily",
            default=False,
            help="Launch daily import script",
        )
        parser.add_argument(
            "-x",
            "--verbose",
            action="store_true",
            dest="verbose",
            default=False,
            help="Add debug information",
        )
        parser.add_argument(
            "-g",
            "--garbage_collector",
            action="store_true",
            dest="garbage_collector",
            default=False,
            help="Full clean kapt_apidae",
        )

    def handle(self, *args, **options):
        if options["verbose"]:
            self.verbose = True
        else:
            self.verbose = False

        if options["base_elements"]:
            self.import_base_elements(**options)

        if options["municipalities"]:
            self.import_municipalities(**options)

        if options["variable_attributes"]:
            self.import_variable_attributes(**options)

        if options["areas"]:
            self.import_areas(import_only=args, **options)

        if options["linked"]:
            self.import_touristical_objects(
                objects_type="linked_objects", import_only=args, **options
            )

        if options["primary"] or options["primary"] == []:
            self.import_touristical_objects(
                objects_type="modified_objects",
                import_only=options["primary"],
                **options
            )

        if options["remove"]:
            self.remove_touristical_objects(**options)

        if options["selections"]:
            self.selections(**options)

        if options["all"]:
            self.import_all(**options)

        if options["daily"]:
            self.import_daily(**options)

        if options["garbage_collector"]:
            self.remove_all_touristical_objects(**options)

    # Methods you can call directly
    def import_base_elements(self, **options):
        # Retrieve the content of the json in memory
        json_content = get_json_content("base_elements")
        # Retrieve the identifiers of the objects that are already in the database. It will help us with bulk_creation.
        database_identifiers = BaseElement.objects.all().values_list("id", flat=True)
        # We store all the new bas elements in an array for bulk creation
        new_base_elements = []
        # Counter
        loop_counter = 0

        # We go through the json file, for each base element
        for base_element_json in json_content:
            loop_counter += 1
            json_identifier = base_element_json["id"]
            if json_identifier in database_identifiers:
                base_element_object = BaseElement.objects.get(id=json_identifier)
                base_element_object.update_from_json(base_element_json)
            else:
                new_base_elements.append(
                    BaseElement(
                        **BaseElement().update_from_json(base_element_json, save=False)
                    )
                )
            print_progress(
                loop_counter,
                2 * len(json_content),
                prefix="Base elements",
                suffix="",
                decimals=0,
                bar_length=100,
            )

        BaseElement.objects.bulk_create(new_base_elements)
        # Unfortunately, we need a second loop to add the foreign keys.
        for base_element_json in json_content:
            loop_counter += 1
            base_element_object = BaseElement.objects.get(id=base_element_json["id"])
            base_element_object.update_foreign_keys_from_json(base_element_json)
            print_progress(
                loop_counter,
                2 * len(json_content),
                prefix="Base elements",
                suffix="",
                decimals=0,
                bar_length=100,
            )

    def import_municipalities(self, **options):
        # Retrieve the content of the json in memory
        json_content = get_json_content("localities")

        # Retrieve the identifiers of the objects that are already in the database. It will help us with bulk_creation.
        database_identifiers = Locality.objects.all().values_list("id", flat=True)

        # We store all the new localities in an array for bulk creation
        new_localities = []

        # We store the countries objects to prevent 37000 requests
        countries_objects = {}

        # Counter
        loop_counter = 0

        # We go through the json file, for each base element
        for locality_json in json_content:
            loop_counter += 1
            json_identifier = locality_json["id"]
            json_country = locality_json["pays"]["id"]
            if json_country not in countries_objects:
                countries_objects[json_country] = BaseElement.objects.get(
                    pk=json_country
                )

            # We create a dictionary for each object of json file. Optional values are filled with None
            locality_as_dict = {
                "id": json_identifier,
                "name": locality_json["nom"],
                "code": locality_json["code"],
                "zip_code": locality_json["codePostal"],
                "country": countries_objects[json_country],
            }

            if json_identifier in database_identifiers:
                # Update
                Locality.objects.filter(id=json_identifier).update(**locality_as_dict)
            else:
                # Create
                new_localities.append(Locality(**locality_as_dict))
            print_progress(
                loop_counter,
                len(json_content),
                prefix="Municipalities",
                suffix="",
                decimals=0,
                bar_length=100,
            )

        # Bulk create all new objects
        Locality.objects.bulk_create(new_localities)

    def import_variable_attributes(self, **options):
        # Retrieve the content of the json in memory
        json_content = get_json_content("internal_criterias")

        # Retrieve the identifiers of the objects that are already in the database.
        database_identifiers = VariableAttribute.objects.all().values_list(
            "id", flat=True
        )

        # Counter
        loop_counter = 0

        # We go through the json file, for each base element
        for variable_attribute_json in json_content:
            loop_counter += 1
            json_identifier = variable_attribute_json["id"]

            # We create a dictionary for each object of json file. Optional values are filled with None
            variable_attribute_dict = {
                "id": json_identifier,
                "label": variable_attribute_json["libelle"],
                "description": variable_attribute_json.get("commentaire", None),
            }

            if json_identifier in database_identifiers:
                # Update
                VariableAttribute.objects.filter(id=json_identifier).update(
                    **variable_attribute_dict
                )
            else:
                # Create
                VariableAttribute(**variable_attribute_dict).save()
            print_progress(
                loop_counter,
                len(json_content),
                prefix="Variables attributes",
                suffix="",
                decimals=0,
                bar_length=100,
            )

    # Import all areas
    def import_areas(self, import_only=None, **options):
        # Limit import to a list of APIDAE identifiers: list creation
        import_only_list = []
        if import_only and len(import_only) > 0:
            for identifier in import_only:
                try:
                    import_only_list.append(int(identifier))
                except Exception:
                    raise Exception("Supplied value must be an integer")

        # Retrieve the content of the json in memory
        json_content = get_json_content("areas")

        # We must skip area objects set in selections as they must be imported as primary objects instead of simple area
        selections_json_content = get_json_content("objects_selection")

        selection_ids = []
        for selection in selections_json_content:
            if "objetsTouristiques" in selection:
                for touristical_object in selection["objetsTouristiques"]:
                    selection_ids.append(touristical_object["id"])
        selection_ids_set = set(selection_ids)

        # Counter
        loop_counter = 0
        # For each area, import it
        for area_json in json_content:
            loop_counter += 1
            area_json_id = area_json["id"]

            # If import_only_list is set and object is not in user list or object id is in selections, skip this loop
            if (
                len(import_only_list) > 0
                and area_json_id not in import_only_list
                or area_json_id in selection_ids_set
            ):
                continue
            self.import_touristic_object_core(area_json, is_linked_object=True)
            print_progress(
                loop_counter,
                2 * len(json_content),
                prefix="Areas",
                suffix="",
                decimals=0,
                bar_length=100,
            )

        # A second loop is mandatory for m2m
        for area_json in json_content:
            loop_counter += 1
            area_json_id = area_json["id"]
            if (
                len(import_only_list) > 0
                and area_json_id not in import_only_list
                or area_json_id in selection_ids_set
            ):
                continue
            self.import_touristic_object_relations(area_json)
            print_progress(
                loop_counter,
                2 * len(json_content),
                prefix="Areas",
                suffix="",
                decimals=0,
                bar_length=100,
            )

    # Import secondary objects
    def import_touristical_objects(
        self, objects_type=None, import_only=None, **options
    ):
        # Limit import to a list of apidae identifiers: list creation
        import_only_list = []
        if import_only and len(import_only) > 0:
            for identifier in import_only:
                try:
                    import_only_list.append(int(identifier))
                except Exception:
                    raise Exception("Supplied value must be an integer")
        if objects_type in TOURISTICAL_OBJECTS_TYPE:
            is_linked_object = TOURISTICAL_OBJECTS_TYPE[objects_type]
            ids_list = get_objects_ids(objects_type)

            # Limit import to a list of apidae identifiers: check that supplied ids are in our import folder
            if import_only and len(import_only_list) > 0:
                for only_identifier in import_only_list:
                    if int(only_identifier) not in ids_list:
                        raise Exception("Unknown identifier %s" % only_identifier)
                ids_list = import_only_list
            # Counter
            loop_counter = 0
            # Import ids list
            for identifier in ids_list:
                loop_counter += 1
                json_content = get_json_content(objects_type, identifier)
                self.import_touristic_object_core(json_content, is_linked_object)
                if kapt_apidae_settings.ASPECTS:
                    for aspect in kapt_apidae_settings.ASPECTS:
                        json_content, aspect_found = get_json_content(
                            objects_type, identifier, aspect
                        )
                        if aspect_found:
                            self.import_touristic_object_core(
                                json_content, is_linked_object, aspect
                            )

                print_progress(
                    loop_counter,
                    2 * len(ids_list),
                    prefix="Touristic objects",
                    suffix="",
                    decimals=0,
                    bar_length=100,
                )

            for identifier in ids_list:
                loop_counter += 1
                json_content = get_json_content(objects_type, identifier)
                self.import_touristic_object_relations(json_content, is_linked_object)
                if kapt_apidae_settings.ASPECTS:
                    for aspect in kapt_apidae_settings.ASPECTS:
                        json_content, aspect_found = get_json_content(
                            objects_type, identifier, aspect
                        )
                        if aspect_found:
                            self.import_touristic_object_relations(
                                json_content, is_linked_object, aspect
                            )

                print_progress(
                    loop_counter,
                    2 * len(ids_list),
                    prefix="Touristic objects",
                    suffix="",
                    decimals=0,
                    bar_length=100,
                )

    def import_touristic_object_core(
        self, touristic_object_json, is_linked_object=False, aspect=None
    ):
        if self.verbose:
            logger.info("Working on core of object %s" % touristic_object_json["id"])
        model_class = get_touristic_object_model_class(touristic_object_json)
        try:
            touristic_object = model_class.objects.get(
                apidae_identifier=touristic_object_json["id"],
                aspect=get_aspect_id(aspect),
            )
        except ObjectDoesNotExist:
            touristic_object = model_class()
        touristic_object.update_from_json(
            touristic_object_json, is_linked_object, get_aspect_id(aspect)
        )

    def import_touristic_object_relations(
        self, touristic_object_json, is_linked_object=False, aspect=None
    ):
        if self.verbose:
            logger.info(
                "Working on relations of object %s" % touristic_object_json["id"]
            )
        model_class = get_touristic_object_model_class(touristic_object_json)
        try:
            touristic_object = model_class.objects.get(
                apidae_identifier=touristic_object_json["id"],
                aspect=get_aspect_id(aspect),
            )
        except ObjectDoesNotExist:
            touristic_object = model_class()

        touristic_object.update_fk_and_m2m_from_json(
            touristic_object_json, is_linked_object
        )

    def remove_touristical_objects(self, **options):
        self.stdout.write("Removing out of date objects")

        # Remove primary objects
        json_content = get_json_content("removed_touristical_objects")
        for identifier in json_content:
            try:
                touristic_objects = TouristicObject.objects.filter(
                    apidae_identifier=identifier, is_linked_object=False
                )
                for touristic_object in touristic_objects:
                    logger.warning("Calling delete on object %d" % touristic_object.id)
                    touristic_object.delete()
            except ObjectDoesNotExist:
                logger.info(
                    "Tried to removed an object not present in database : (%d)"
                    % identifier
                )

        # Remove linked object
        json_content = get_json_content("removed_linked_objects")
        for identifier in json_content:
            try:
                touristic_objects = TouristicObject.objects.filter(
                    apidae_identifier=identifier, is_linked_object=True
                )
                for touristic_object in touristic_objects:
                    logger.warning("Calling delete on object %d" % touristic_object.id)
                    touristic_object.delete()
            except ObjectDoesNotExist:
                logger.info(
                    "Tried to removed an object not present in database : (%d)"
                    % identifier
                )

    def remove_all_touristical_objects(self, **options):
        # Called when we re-init all the import
        # Must be the perfect inverse of import_all

        user_input = input(
            "Are you sure ? This will trash all kapt_apidae data !!! (type yes): "
        )

        if user_input != "yes":
            logger.warning("Full clean cancelled.")
            return

        # Delete selections
        logger.info("Begin to delete all selections")
        Selection.objects.all().delete()
        logger.info("Selections trashed")

        # Delete primary objects
        logger.info("Begin to delete all primary objects")
        TouristicObject.objects.filter(is_linked_object=False).delete()
        logger.info("Primary objects trashed")

        # Delete linked objects
        logger.info("Begin to delete all linked objects")
        linked_touristic_objects = TouristicObject.objects.filter(is_linked_object=True)
        for linked_touristic_object in linked_touristic_objects:
            try:
                logger.info("Deleting {}".format(linked_touristic_object.id))
                linked_touristic_object.delete()
            except ObjectDoesNotExist:
                # This linked object has been removed by another linked object
                continue

        logger.info("Linked objects trashed")

        # Delete variable attributes
        logger.info("Begin to delete all variable attributes objects")
        VariableAttribute.objects.all().delete()
        logger.info("Variable attributes objects trashed")

        # Delete municipalities
        logger.info("Begin to delete all municipalities objects")
        Locality.objects.all().delete()
        logger.info("Municipalities objects trashed")

        # Delete base elements
        logger.info("Begin to delete all base elements objects")
        BaseElement.objects.all().delete()
        logger.info("Base elements objects trashed")

    def selections(self, **options):
        json_content = get_json_content("objects_selection")
        selections_ids = []
        loop_counter = 0
        for selection_json in json_content:
            loop_counter += 1
            selections_ids.append(selection_json["id"])
            try:
                selection_object = Selection.objects.get(id=selection_json["id"])
            except ObjectDoesNotExist:
                selection_object = Selection()

            selection_object.update_from_json(selection_json)
            print_progress(
                loop_counter,
                len(json_content),
                prefix="Selections",
                suffix="",
                decimals=0,
                bar_length=100,
            )

        # Remove selections missing from the import
        Selection.objects.all().exclude(id__in=selections_ids).delete()

    def import_all(self, **options):
        logger.info("------------------------------------------------------")
        logger.info("Launched import_apidae script")
        logger.info("------------------------------------------------------")
        logger.info(
            "Script launched at {}".format(
                datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")
            )
        )

        self.import_base_elements(**options)
        self.import_municipalities(**options)
        self.import_variable_attributes(**options)
        self.import_areas(**options)
        self.import_touristical_objects(objects_type="linked_objects", **options)
        self.import_touristical_objects(objects_type="modified_objects", **options)
        self.remove_touristical_objects(**options)
        self.selections(**options)

    def create_folders(self):
        if not os.path.exists(EXPORT_FOLDER):
            os.makedirs(EXPORT_FOLDER)
        if not os.path.exists(DOWNLOAD_FOLDER):
            os.makedirs(DOWNLOAD_FOLDER)

    def download_archives(self, imports_settings_list):
        for imports_settings in imports_settings_list:
            file_url = imports_settings.urlRecuperation
            file_local_url = "{}{}".format(DOWNLOAD_FOLDER, os.path.basename(file_url))

            if not os.path.exists(file_local_url):
                try:
                    r = requests.get(file_url, stream=True)
                    if r.status_code == 200:
                        with open(file_local_url, "wb") as local_file:
                            for chunk in r.iter_content(1024):
                                local_file.write(chunk)

                    imports_settings.file_downloaded = True
                    imports_settings.save()

                except Exception as e:
                    imports_settings.statut = "DOWNLOAD_ERROR"
                    imports_settings.save()
                    raise e

    def open_archive(self, url_recuperation):
        file_url = url_recuperation
        file_local_url = DOWNLOAD_FOLDER + os.path.basename(file_url)

        if os.path.exists(file_local_url):
            return file_local_url
        else:
            raise Exception(
                "Archive file %s does not exists in %s"
                % (os.path.basename(file_url), DOWNLOAD_FOLDER)
            )

    def prepare_files(self, file_local_url):
        # Remove previous download
        shutil.rmtree(EXPORT_FOLDER)
        # Extract new import
        with ZipFile(file_local_url) as zipFile:
            zipFile.extractall(EXPORT_FOLDER)

    def notify_apidae(self, url_confirmation):
        try:
            response = requests.get(url_confirmation)
            if response.status_code != 200:
                raise
            response.close()
        except Exception:
            raise

    def import_daily(self, **options):
        self.import_apidae_daily()
        if kapt_apidae_settings.APIDAE_IN_KAPT_CATALOG:
            selections_json_file = "{}/{}".format(
                EXPORT_FOLDER,
                JSON_FILES["objects_selection"],
            )
            call_command(
                "import_apidae_kaptravel",
                init_parameters=True,
                differential=True,
                coherence=selections_json_file,
            )

    def import_apidae_daily(self, **options):
        imports_settings_list = ImportsApidaeSettings.objects.filter(
            import_complete=False
        ).order_by("created_on")

        # Check that everything is initialized
        self.create_folders()

        # Download all archives
        self.download_archives(imports_settings_list)

        for imports_settings in imports_settings_list:
            try:
                # Getting files
                try:
                    file_local_url = self.open_archive(imports_settings.urlRecuperation)
                except Exception:
                    raise

                # Extract files
                try:
                    self.prepare_files(file_local_url)
                    imports_settings.file_extracted = True
                    imports_settings.save()
                except Exception:
                    imports_settings.statut = "EXTRACTION_ERROR"
                    imports_settings.save()
                    raise

                # Launch import
                try:
                    imports_settings.import_launched = True
                    imports_settings.save()

                    # Garbage collector, need more tests before being used in production
                    # if imports_settings.reinitialisation:
                    #     self.remove_all_touristical_objects(**options)
                    self.import_all(**options)
                    imports_settings.import_complete = True
                except Exception:
                    imports_settings.statut = "IMPORT_ERROR"
                    imports_settings.save()
                    raise

                # Notify apidae
                try:
                    self.notify_apidae(imports_settings.urlConfirmation)
                except Exception:
                    imports_settings.statut = "NOTIFICATION_ERROR"
                    imports_settings.save()
                    raise

                imports_settings.statut = "TERMINATED"
                imports_settings.save()

                # Remove archive file
                os.remove(file_local_url)

            except Exception as exception:
                message = "<h1>Rapport d'échec</h1> \
                <br>Import for apidae ID {} failed with status : {} \
                <br><br> \
                <h2>Paramètres : </h2> \
                Reinitialisation : {} \
                <br> Ponctuel : {} \
                <br> Url de recuperation : {} \
                <br> Url de confirmation : {} \
                <br> Export téléchargé : {} \
                <br> Export dézippé : {} \
                <br> Import démarré : {} \
                <br> Import terminé : {} \
                <h2>Exception : </h2> \
                <br> {} ".format(
                    str(imports_settings.projetId),
                    imports_settings.statut,
                    str(imports_settings.reinitialisation),
                    str(imports_settings.ponctuel),
                    imports_settings.urlRecuperation,
                    imports_settings.urlConfirmation,
                    str(imports_settings.file_downloaded),
                    str(imports_settings.file_extracted),
                    str(imports_settings.import_launched),
                    str(imports_settings.import_complete),
                    exception,
                )

                mail_admins("Import apidae error", "", html_message=message)
                # If one of the import fails, we break the loop
                logger.error(exception)
                raise

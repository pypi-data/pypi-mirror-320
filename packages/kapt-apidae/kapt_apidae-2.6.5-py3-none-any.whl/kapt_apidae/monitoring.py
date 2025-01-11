# Standard Library
import datetime
import json

# Third party
from django.db.models import Q
from django.utils import timezone
from django.utils.timezone import get_default_timezone, make_aware

# Local application / specific library imports
from kapt_apidae.models import ImportApidaeKaptravelLog, ImportsApidaeSettings


DEFAULT_TZ = get_default_timezone()


class ApidaeImportMonitor:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def apidae_daily_packet_received(self):
        last_differential_export = self._get_differential_exports().first()
        yesterday = make_aware(
            (datetime.datetime.now() - datetime.timedelta(days=1)).replace(
                hour=21, minute=00, second=00, microsecond=0
            ),
            DEFAULT_TZ,
        )

        if last_differential_export is not None:
            return last_differential_export.created_on > yesterday
        return False

    def apidae_daily_import_performed(self):
        last_differential_export = self._get_differential_exports().first()
        yesterday = make_aware(
            (datetime.datetime.now() - datetime.timedelta(days=1)).replace(
                hour=21, minute=00, second=00, microsecond=0
            ),
            DEFAULT_TZ,
        )

        if last_differential_export is not None:
            if last_differential_export.created_on > yesterday:
                return last_differential_export.import_complete
        return False

    def all_apidae_daily_packet_imported_in_KAPTAPidae(self):
        differential_exports = self._get_differential_exports().filter(
            Q(file_downloaded=False)
            | Q(file_extracted=False)
            | Q(import_launched=False)
            | Q(import_complete=False)
        )
        return not differential_exports.exists()

    def apidae_to_kaptravel_ran_today(self):
        return self._get_today_apidae_kaptravel_logs().exists()

    def apidae_to_kaptravel_finished_today(self):
        return (
            self._get_today_apidae_kaptravel_logs()
            .filter(end_date__isnull=False)
            .exists()
        )

    def apidae_to_kaptravel_today_objects_modified(self):
        last_ended_import = self._get_last_today_ended_apidae_kaptravel_log()
        if last_ended_import is not None:
            return last_ended_import.objects_modified
        else:
            return 0

    def apidae_to_kaptravel_today_added(self):
        last_ended_import = self._get_last_today_ended_apidae_kaptravel_log()
        if last_ended_import is not None:
            return last_ended_import.objects_added
        else:
            return 0

    def apidae_to_kaptravel_today_errors(self):
        last_ended_import = self._get_last_today_ended_apidae_kaptravel_log()
        if last_ended_import is not None:
            return last_ended_import.errors
        else:
            return 0

    def apidae_to_kaptravel_today_duration(self):
        last_ended_import = self._get_last_today_ended_apidae_kaptravel_log()
        if last_ended_import is not None:
            return last_ended_import.duration
        else:
            return None

    def apidae_to_kaptravel_today_options(self):
        last_ended_import = self._get_last_today_ended_apidae_kaptravel_log()
        if last_ended_import is not None:
            launch_options_txt = last_ended_import.launch_options
            launch_options = json.loads(launch_options_txt)
            options_names = []
            for option, value in launch_options["options"].items():
                if value is True:
                    options_names.append(option)
            return options_names
        else:
            return None

    def apidae_to_kaptravel_today_coherence(self):
        last_ended_import = self._get_last_today_ended_apidae_kaptravel_log()
        if last_ended_import is not None:
            return last_ended_import.coherence_test_passed
        else:
            return False

    def _get_last_reinitialized_importsettings(self):
        last_reinitialized_import = (
            ImportsApidaeSettings.objects.filter(reinitialisation=True)
            .order_by("-created_on")
            .first()
        )
        if last_reinitialized_import is not None:
            return last_reinitialized_import
        else:
            raise Exception("Import has never been initialized")

    def _get_differential_exports(self):
        return ImportsApidaeSettings.objects.filter(
            created_on__gte=self._get_last_reinitialized_importsettings().created_on
        ).order_by("-created_on")

    def _get_today_apidae_kaptravel_logs(self):
        return ImportApidaeKaptravelLog.objects.filter(
            launch_date__gte=timezone.now() - timezone.timedelta(hours=24)
        )

    def _get_last_today_ended_apidae_kaptravel_log(self):
        return (
            self._get_today_apidae_kaptravel_logs()
            .filter(end_date__isnull=False)
            .order_by("-launch_date")
            .first()
        )

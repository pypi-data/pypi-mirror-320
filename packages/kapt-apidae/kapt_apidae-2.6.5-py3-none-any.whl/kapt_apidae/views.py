import json
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.core import management
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import CreateView
import requests

from kapt_apidae import __version__ as apidae_version
from kapt_apidae.conf import settings as apidae_settings
from kapt_apidae.models import ImportApidaeKaptravelLog, ImportsApidaeSettings
from kapt_apidae.monitoring import ApidaeImportMonitor
from kapt_apidae.tasks import force_import_kapt_apidae, import_kapt_apidae
from kapt_apidae.utils import (
    get_apidae_json_data,
    get_apidae_status,
    launch_manual_apidae_export,
)


try:
    from kapt_site import __version__ as site_version
except ImportError:
    site_version = "N.C"
try:
    from kapt_catalog import __version__ as catalog_version
except ImportError:
    catalog_version = "N.C"


class ImportsApidaeSettingsCreateView(CreateView):
    """
    This view allow the Apidae server to creates a ImportsApidaeSettings object when the Apidae export is terminated
    """

    model = ImportsApidaeSettings

    fields = [
        "projetId",
        "statut",
        "ponctuel",
        "reinitialisation",
        "urlRecuperation",
        "urlConfirmation",
    ]

    template_name = "import_settings.html"
    success_url = "."
    http_method_names = ["post"]

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def http_method_not_allowed(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)
        if apidae_settings.DUPLICATE_NOTIFICATION:
            for duplicate_url in apidae_settings.DUPLICATE_URLS:
                requests.post(duplicate_url, data=request.POST)
        return HttpResponse(status=200)


class MonitoringView(View):
    def get(self, request, *args, **kwargs):
        import_monitor = ApidaeImportMonitor()
        json_dict = {
            "apidae_daily_packet_received": import_monitor.apidae_daily_packet_received(),
            "apidae_daily_import_performed": import_monitor.apidae_daily_import_performed(),
            "all_apidae_daily_packet_imported_in_KAPTAPidae": import_monitor.all_apidae_daily_packet_imported_in_KAPTAPidae(),
            "apidae_to_kaptravel_ran_today": import_monitor.apidae_to_kaptravel_ran_today(),
            "apidae_to_kaptravel_finished_today": import_monitor.apidae_to_kaptravel_finished_today(),
            "apidae_to_kaptravel_today_objects_modified": import_monitor.apidae_to_kaptravel_today_objects_modified(),
            "apidae_to_kaptravel_today_added": import_monitor.apidae_to_kaptravel_today_added(),
            "apidae_to_kaptravel_today_errors": import_monitor.apidae_to_kaptravel_today_errors(),
            "apidae_to_kaptravel_today_duration": import_monitor.apidae_to_kaptravel_today_duration(),
            "apidae_to_kaptravel_today_options": import_monitor.apidae_to_kaptravel_today_options(),
            "apidae_to_kaptravel_today_coherence": import_monitor.apidae_to_kaptravel_today_coherence(),
            "version": apidae_version,
            "apidae_version": apidae_version,
            "site_version": site_version,
            "catalog_version": catalog_version,
            "auto-start": apidae_settings.AUTO_IMPORT,
        }

        response = HttpResponse(json.dumps(json_dict), content_type="application/json")
        response["Access-Control-Allow-Origin"] = "*"
        return response


class RefreshCurrentPageData(View):
    """
    This view allows the user to launch an import.
    It retrieves the json from apidae's api and reimports it.
    """

    def get(self, request, *args, **kwargs):
        apidae_identifier = self.kwargs.get("apidae_identifier")
        return_path = request.GET.get("return_path")
        data = get_apidae_json_data(apidae_identifier)
        if len(data) > 350:
            folder_path = (
                settings.PROJECT_PATH / "exports/kapt-apidae/json/objets_modifies/"
            )
            if not folder_path.exists():
                folder_path.mkdir(parents=True)

            file_path = folder_path / f"objets_modifies-{apidae_identifier}.json"

            with open(file_path, "w") as file:
                file.write(data)

            management.call_command("import_apidae", primary=[apidae_identifier])
            management.call_command("import_apidae_kaptravel", only=[apidae_identifier])
            messages.success(request, "Synchronisation effectuée.")
            return redirect(return_path)
        else:
            messages.error(
                request,
                "Erreurs lors de la récupération du json, veuillez vérifier le status d'APIDAE",
            )
            return redirect(return_path)


class LaunchApidaeExport(View):
    """
    This view allows the user to launch a partial or complete export of the project to APIDAE
    """

    def get(self, request, *args, **kwargs):
        export_type = self.kwargs.get("export_type")
        return_path = request.GET.get("return_path")
        export_status = launch_manual_apidae_export(export_type)

        if export_status == "export_launched":
            messages.success(request, "Export lancé.")
            return redirect(return_path)
        else:
            messages.error(
                request,
                "Erreur lors de l'export, veuillez vérifier le status d'APIDAE",
            )
            return redirect(return_path)


class GetKaptApidaeStatus(View):
    """
    This view allows the user to see the status of the latest project import.
    """

    def get(self, request):
        last_apidae_kapttravel_log = ImportApidaeKaptravelLog.objects.filter(
            launch_date__gte=timezone.now() - timezone.timedelta(hours=24)
        ).last()
        last_apidae_settings_import = ImportsApidaeSettings.objects.last()
        return render(
            request,
            "import_status.html",
            {
                "last_apidae_kapttravel_log": last_apidae_kapttravel_log,
                "last_apidae_settings_import": last_apidae_settings_import,
            },
        )


class GetApidaeStatus(View):
    """
    This view allows the user to see the status of APIDAE without useless html
    """

    def get(self, request):
        return render(
            request,
            "apidae_status.html",
            {"content": get_apidae_status()},
        )


class ForceImport(View):
    """
    This view allows the user to launch a forced import
    """

    def get(self, request):
        return_path = request.GET.get("return_path")
        force_import_kapt_apidae()
        messages.success(request, "Import forcé en cours.")
        return redirect(return_path)


class DailyImport(View):
    """
    This view allows the user to launch a daily import
    """

    def get(self, request):
        return_path = request.GET.get("return_path")
        import_kapt_apidae()
        messages.success(request, "Import quotidien en cours.")
        return redirect(return_path)


class ImportLogView(View):
    def get(self, request):
        file_path = Path.home() / "admin/logs/kapt-travel/import_kapt_apidae.log"
        with open(file_path) as file:
            file_content = file.read()

        return render(request, "import_logs.html", {"file_content": file_content})


class FlushRedisDatabaseView(View):
    def get(self, request):
        import subprocess

        return_path = request.GET.get("return_path")
        REDIS_DB = apidae_settings.get_secret("REDIS_DB", None)

        if REDIS_DB:
            subprocess.run(["redis-cli", "-n", REDIS_DB, "flushdb"])
            messages.success(request, "Base redis flushed.")
        else:
            messages.error(request, "Pas de base redis configurée.")

        return redirect(return_path)

# Third party
from django.urls import path

# Local application / specific library imports
from kapt_apidae.views import (
    DailyImport,
    FlushRedisDatabaseView,
    ForceImport,
    GetApidaeStatus,
    GetKaptApidaeStatus,
    ImportLogView,
    ImportsApidaeSettingsCreateView,
    LaunchApidaeExport,
    MonitoringView,
    RefreshCurrentPageData,
)


app_name = "kapt_apidae"  # Enregistrement du namespace


urlpatterns = [
    path(
        "refresh-current-page-data/<int:apidae_identifier>/",
        RefreshCurrentPageData.as_view(),
        name="refresh-current-page-data",
    ),
    path(
        "launch-apidae-export/<str:export_type>/",
        LaunchApidaeExport.as_view(),
        name="launch-apidae-export",
    ),
    path(
        "get-kapt-apidae-status/",
        GetKaptApidaeStatus.as_view(),
        name="get-kapt-apidae-status",
    ),
    path("get-apidae-status/", GetApidaeStatus.as_view(), name="get-apidae-status"),
    path("force-import/", ForceImport.as_view(), name="force-import"),
    path("daily-import/", DailyImport.as_view(), name="daily-import"),
    path("flush-redis-db/", FlushRedisDatabaseView.as_view(), name="flush-redis-db"),
    path(
        "settings/",
        ImportsApidaeSettingsCreateView.as_view(),
        name="apidae-create-settings",
    ),
    path("monitoring/", MonitoringView.as_view(), name="apidae-monitoring"),
    path("log/", ImportLogView.as_view(), name="apidae-import-log"),
]

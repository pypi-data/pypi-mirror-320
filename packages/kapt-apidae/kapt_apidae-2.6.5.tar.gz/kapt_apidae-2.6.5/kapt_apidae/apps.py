# Third party
from django.apps import AppConfig


class KaptApidaeRegistryConfig(AppConfig):
    label = "kapt_apidae"
    name = "kapt_apidae"
    verbose_name = "Kapt - Apidae"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        from . import receivers  # noqa

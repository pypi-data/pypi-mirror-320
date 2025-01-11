# Third party
from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin

# Local application / specific library imports
from kapt_apidae.models import ImportsApidaeSettings, TouristicObject


@admin.register(TouristicObject)
class TouristicObjectAdmin(PolymorphicParentModelAdmin):
    base_model = TouristicObject
    list_display = ("polymorphic_ctype", "label")
    child_models = ()


@admin.register(ImportsApidaeSettings)
class ImportsApidaeSettingsAdmin(admin.ModelAdmin):
    base_model = ImportsApidaeSettings
    list_display = ("projetId", "created_on", "statut", "import_complete")
    list_filter = ("statut",)

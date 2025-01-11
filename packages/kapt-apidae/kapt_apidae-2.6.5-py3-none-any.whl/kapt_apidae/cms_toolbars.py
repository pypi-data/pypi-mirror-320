# Third party
import re
from urllib.parse import urlencode

from cms.constants import LEFT
from cms.toolbar_base import CMSToolbar
from cms.toolbar_pool import toolbar_pool
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from kapt_apidae.conf.settings import PROJECT_ID, SHOW_CMS_MENU
from kapt_apidae.core.toolbar.items import CustomSubMenu
from kapt_apidae.models import ImportsApidaeSettings
from kapt_apidae.utils import get_apidae_error_status


class SettingsToolbarApidae(CMSToolbar):
    def get_or_create_menu_custom(
        self,
        toolbar,
        key,
        verbose_name=None,
        disabled=False,
        side=LEFT,
        position=None,
        led=True,
        to_check=None,
        ok_condition=None,
        warning_condition=None,
        error_condition=None,
    ):
        toolbar.populate()
        if key in toolbar.menus:
            menu = toolbar.menus[key]
            if verbose_name:
                menu.name = verbose_name
            if menu.side != side:
                menu.side = side
            if position:
                toolbar.remove_item(menu)
                toolbar.add_item(menu, position=position)
            return menu
        menu = CustomSubMenu(
            verbose_name,
            toolbar.csrf_token,
            disabled=disabled,
            side=side,
            led=led,
            to_check=to_check,
            ok_condition=ok_condition,
            warning_condition=warning_condition,
            error_condition=error_condition,
        )
        toolbar.menus[key] = menu
        toolbar.add_item(menu, position=position)
        return menu

    def populate(self):
        last_object = ImportsApidaeSettings.objects.order_by("-id").first()
        last_import_status = last_object.get_statut_display() if last_object else None

        params = urlencode({"return_path": self.request.get_full_path()})

        # Append a 'Apidae' menu to the toolbar
        apidae_settings_menu = self.get_or_create_menu_custom(
            self.toolbar,
            "apidae-menu",
            _("Apidae"),
            position=9,
            led=True,
            to_check=last_import_status,
            ok_condition="Export integrated",
            warning_condition="Error",
            error_condition="Fatal Error",
        )
        apidae_detail_url = self.request.get_full_path()
        if "detail" in apidae_detail_url:
            try:
                apidae_identifier = re.search(
                    r"-(\d+)/", apidae_detail_url.split("?")[0]
                ).group(1)
            # django check seo url: django-check-seo/?page=/fr/catalogue/detail/train-de-l-ardeche-groupes-313232/
            # trying to get left part of a split("?") returns django-check-seo/, and there's no `-(\d+)` in this str
            # current fix is just to return here, preventing the toolbar to populate
            except AttributeError:
                return

            apidae_settings_menu.add_link_item_custom(
                _("Voir la fiche sur Apidae"),
                url=f"https://base.apidae-tourisme.com/consulter/objet-touristique/{apidae_identifier}/",
                position=0,
                target_blank=True,
            )

            apidae_settings_menu.add_link_item_custom(
                _("Modifier la fiche sur Apidae"),
                url=f"https://base.apidae-tourisme.com/gerer/objet-touristique/{apidae_identifier}/consulter/",
                position=1,
                target_blank=True,
            )

            refresh_current_page_data_url = reverse(
                "kapt_apidae:refresh-current-page-data",
                kwargs={"apidae_identifier": apidae_identifier},
            )
            refresh_current_page_data_url = f"{refresh_current_page_data_url}?{params}"
            apidae_settings_menu.add_link_item(
                _("Synchroniser les données de la page avec Apidae"),
                url=refresh_current_page_data_url,
                position=2,
            )

            if self.request.user.is_superuser:
                apidae_settings_menu.add_link_item_custom(
                    _("Faire une demande de modification de la fiche Apidae"),
                    url=f"https://base.apidae-tourisme.com/gerer/objet-touristique/{apidae_identifier}/consulter/?36-10.IBehaviorListener.0-actionsGlobales2-campagneMiseAJourDemandeContainer-campagneMiseAJourDemandeSaisiePremium&_=1690205151306",
                    position=3,
                    target_blank=True,
                )
                apidae_settings_menu.add_link_item_custom(
                    _("Visualiser le projet sur Apidae"),
                    url=f"https://base.apidae-tourisme.com/diffuser/projet/{PROJECT_ID}#tab-informations",
                    position=4,
                    target_blank=True,
                )
                apidae_settings_menu.add_link_item_custom(
                    _("Visualiser le référentiel sur Apidae"),
                    url="https://base.apidae-tourisme.com/diffuser/dev-tools/referentiel/elements-reference/",
                    position=5,
                    target_blank=True,
                )
            apidae_settings_menu.add_break(position=6)

        # Launch a partial export
        launch_apidae_export_url = reverse(
            "kapt_apidae:launch-apidae-export", kwargs={"export_type": "partial"}
        )
        launch_apidae_export_url = f"{launch_apidae_export_url}?{params}"
        apidae_settings_menu.add_link_item(
            _("Lancer un export partiel des données du projet sur Apidae"),
            url=launch_apidae_export_url,
            position=7,
        )

        # Launch a full export
        launch_apidae_export_url = reverse(
            "kapt_apidae:launch-apidae-export", kwargs={"export_type": "full"}
        )
        launch_apidae_export_url = f"{launch_apidae_export_url}?{params}"
        apidae_settings_menu.add_link_item(
            _("Lancer un export complet des données du projet Apidae"),
            url=launch_apidae_export_url,
            position=8,
        )

        apidae_settings_menu.add_break(position=9)
        apidae_settings_menu.add_sideframe_item_custom(
            _("Voir le status d'Apidae"),
            url=reverse("kapt_apidae:get-apidae-status"),
            position=10,
            led=True,
            to_check=get_apidae_error_status(),
            ok_condition="green",
            warning_condition="orange",
            error_condition="red",
        )

        apidae_settings_menu.add_sideframe_item_custom(
            _("Voir le statut du dernier import du projet"),
            url=reverse("kapt_apidae:get-kapt-apidae-status"),
            position=11,
            led=True,
            to_check=last_import_status,
            ok_condition="Export integrated",
            warning_condition="Error",
            error_condition="Fatal Error",
        )

        if self.request.user.is_superuser:
            apidae_settings_menu.add_link_item(
                _("Forcer l'import du projet"),
                url=f'{reverse("kapt_apidae:force-import")}?{params}',
                position=12,
            )
            apidae_settings_menu.add_link_item(
                _("Relancer l'import quotidien"),
                url=f'{reverse("kapt_apidae:daily-import")}?{params}',
                position=13,
            )

            apidae_settings_menu.add_sideframe_item(
                _("Voir les logs d'import"),
                url=reverse("kapt_apidae:apidae-import-log"),
                position=14,
            )

            apidae_settings_menu.add_link_item(
                _("Vider le cache redis"),
                url=f'{reverse("kapt_apidae:flush-redis-db")}?{params}',
                position=15,
            )


if SHOW_CMS_MENU:
    toolbar_pool.register(SettingsToolbarApidae)

# Third party
import base64
import json

from bs4 import BeautifulSoup
from django.apps import apps
from django.conf import settings
from django.db import models
import requests

import kapt_apidae.models


def get_aspect_id(aspect):
    ASPECTS = {
        "HIVER": 1,
        "ETE": 2,
        "HANDICAP": 3,
        "TOURISME_AFFAIRES": 4,
        "GROUPES": 5,
        "PRESTATAIRE_ACTIVITES": 6,
    }
    if aspect:
        return ASPECTS[aspect]


def convert_translated_fields(
    json, field_name_template_json, model_field_name_template
):
    """
    Convert translated fields from json to our database model.
    Ex: Convert libelleFr to label_fr and libelleEn to label_en.
    Returns a dict containing the fields names in our database and the value in the json.
     The default value returned is None
    """
    translated_fields_dict = {}
    for language in settings.LANGUAGES:
        field_key_json = field_name_template_json % language[0].title()
        model_field_name = model_field_name_template % language[0]
        if json:
            field_value_json = json.get(field_key_json, None)
            translated_fields_dict[model_field_name] = field_value_json
        else:
            translated_fields_dict[model_field_name] = None
    return translated_fields_dict


def get_touristic_object_model_class(touristicobject_json):
    type_label = touristicobject_json["type"]
    # We retrieve the model class according to the type of base element
    model_name = kapt_apidae.models.TOURISTIC_OBJECTS_CORRESPONDENCE.get(
        type_label, None
    )
    model_class = apps.get_model("kapt_apidae", model_name)
    return model_class


def default_parse_booking_link(booking_information):
    for communication in (
        booking_information.external_communications.all()
        | booking_information.internal_communications.all()
    ):
        if communication.type_id == 205:  # Website
            if (
                communication.description == "Drôme Dispo"
                or communication.description == "Réservation"
                or (
                    ("cdt-isere" in communication.value)
                    and (".ingenie.fr" in communication.value)
                )
                or (
                    ("reserver-" in communication.value)
                    and (".ingenie.fr" in communication.value)
                )
                or ("reservation" in communication.value)
                or (
                    ("-resa" in communication.value)
                    and (".ingenie.fr" in communication.value)
                )
                or ("logishotels" in communication.value)
            ):
                return communication.value
    if (
        booking_information.type_id in [473, 475]
        and booking_information.description is not None
    ):
        if ".for-system.com" in booking_information.description:
            if booking_information.name == "FR":
                return booking_information.description


def model_field_exists(cls, field):
    try:
        cls._meta.get_field(field)
        return True
    except models.FieldDoesNotExist:
        return False


def get_apidae_error_status():
    colors = []
    response = requests.get("https://status.apidae-tourisme.com/").text
    content = BeautifulSoup(response, "html.parser")

    divs = content.find_all("div", class_="pull-right")

    for div in divs:
        small_tag = div.find("small")
        if small_tag:
            color = small_tag.get_attribute_list("class")[1]
            colors.append(color)

    color_mapping = {
        "reds": "red",
        "yellows": "orange",
    }

    for color in color_mapping.keys():
        if color in colors:
            return color_mapping[color]
    else:
        return "green"


def get_apidae_json_data(apidae_identifier):
    from kapt_apidae.conf.settings import PROJECT_API_KEY, PROJECT_ID

    session = requests.Session()
    url = f"https://api.apidae-tourisme.com/api/v002/objet-touristique/get-by-id/{apidae_identifier}/?apiKey={PROJECT_API_KEY}&projetId={PROJECT_ID}&locales=fr,en,it,de,es,nl&responseFields=@all"
    return session.get(url).text


def launch_manual_apidae_export(export_type):
    from kapt_apidae.conf.settings import LOGIN, PASSWORD, PROJECT_ID

    session = requests.Session()
    response = session.get("https://base.apidae-tourisme.com/diffuser/projet/")
    csrf = session.cookies.get("_csrf")
    atob = response.text.split("window.atob('")[1].split("'")[0]
    temp_data = json.loads(base64.b64decode(atob))
    state = temp_data["extraParams"]["state"]
    clientId = temp_data["clientID"]
    nonce = temp_data["extraParams"]["nonce"]

    session.get(
        f"https://login.plateforme.apidae-tourisme.com/authorize?client_id={clientId}&response_type=code"
    )

    # login
    url = "https://login.plateforme.apidae-tourisme.com/usernamepassword/login"
    payload = json.dumps(
        {
            "client_id": clientId,
            "redirect_uri": "http://base.apidae-tourisme.com/login/oauth2/code/auth0",
            "tenant": "apidae",
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "nonce": nonce,
            "connection": "Username-Password-Authentication",
            "username": LOGIN,
            "password": PASSWORD,
            "popup_options": {},
            "sso": "true",
            "protocol": "oauth2",
            "_csrf": csrf,
            "_intstate": "deprecated",
        }
    )
    headers = {
        "authority": "login.plateforme.apidae-tourisme.com",
        "auth0-client": "eyJuYW1lIjoibG9jay5qcy11bHAiLCJ2ZXJzaW9uIjoiMTEuMjQuNSIsImVudiI6eyJhdXRoMC5qcy11bHAiOiI5LjEzLjQifX0=",
        "content-type": "application/json",
        "origin": "https://login.plateforme.apidae-tourisme.com",
        "referer": "https://login.plateforme.apidae-tourisme.com/login?state="
        + state
        + "&protocol=oauth2&response_type=code",
    }

    response = session.request("POST", url, data=payload, headers=headers)

    soup = BeautifulSoup(response.text, "html.parser")
    wresult = soup.find("input", {"name": "wresult"}).get("value")
    wctx = soup.find("input", {"name": "wctx"}).get("value")

    session.request(
        "POST",
        "https://login.plateforme.apidae-tourisme.com/login/callback",
        data={"wa": "wsignin1.0", "wresult": wresult, "wctx": wctx},
    )

    # # FIN DU LOGIN
    session.get("https://base.apidae-tourisme.com/tableau-bord/")

    session.get("https://base.apidae-tourisme.com/diffuser/projet/")

    session.get(f"https://base.apidae-tourisme.com/diffuser/projet/{PROJECT_ID}")

    # Open la popup demande de calcul
    url = f"https://base.apidae-tourisme.com/diffuser/projet/{PROJECT_ID}?5-1.IBehaviorListener.0-projetFichePanel-projetOperationsExceptionnellesPanel-demandeExportPonctuelLink&spid=2&_=1687418673047"
    headers = {
        "authority": "base.apidae-tourisme.com",
        "referer": "https://base.apidae-tourisme.com/diffuser/projet/"
        + PROJECT_ID
        + "?5&spid=2",
        "wicket-ajax": "true",
        "wicket-ajax-baseurl": f"diffuser/projet/{PROJECT_ID}?5&amp;spid=2",
        "x-requested-with": "XMLHttpRequest",
    }
    session.request("GET", url, headers=headers)

    # Launch export
    url = f"https://base.apidae-tourisme.com/diffuser/projet/{PROJECT_ID}?5-1.IBehaviorListener.0-projetFichePanel-projetOperationsExceptionnellesPanel-demandeExportPonctuelPopupPanel-container-footer-valider&spid=2"
    headers = {
        "authority": "base.apidae-tourisme.com",
        "accept": "application/xml, text/xml, */*; q=0.01",
        "accept-language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "origin": "https://base.apidae-tourisme.com",
        "referer": "https://base.apidae-tourisme.com/diffuser/projet/"
        + PROJECT_ID
        + "?6&spid=2",
        "wicket-ajax": "true",
        "wicket-ajax-baseurl": "diffuser/projet/" + PROJECT_ID + "?6&amp;spid=2",
        "wicket-focusedelementid": "valider",
        "x-requested-with": "XMLHttpRequest",
    }

    # partial export payload
    if export_type == "partial":
        payload = "id1b0_hf_0=&generationContenu=on&export=on&optionsContainer%3AexportOptions%3Aformat=JSON&projetFichePanel%3AprojetOperationsExceptionnellesPanel%3AdemandeExportPonctuelPopupPanel%3Acontainer%3Afooter%3Avalider=1"

    # full export payload
    else:
        payload = "id557_hf_0=&generationContenu=on&export=on&optionsContainer%3AexportOptions%3Areset=on&optionsContainer%3AexportOptions%3Areference=on&optionsContainer%3AexportOptions%3Aformat=JSON&projetFichePanel%3AprojetOperationsExceptionnellesPanel%3AdemandeExportPonctuelPopupPanel%3Acontainer%3Afooter%3Avalider=1"

    response = session.request("POST", url, headers=headers, data=payload)
    if "Votre demande d&#039;export ponctuel a bien été enregistrée." in response.text:
        return "export_launched"


def get_apidae_status():
    response = requests.get("https://status.apidae-tourisme.com/")
    content = response.text

    # Remove all unnecessary items from the page
    modified_content = BeautifulSoup(content, "html.parser")
    nav_menu = modified_content.find("nav", class_="menu")
    if nav_menu:
        nav_menu.decompose()

    navbar = modified_content.find("div", id="navbar")
    if navbar:
        navbar.decompose()

    img_logo = modified_content.find("img", id="img-logo")
    if img_logo:
        img_logo.decompose()

    footer = modified_content.find("div", class_="pa-footer")
    if footer:
        footer.decompose()
    return str(modified_content)

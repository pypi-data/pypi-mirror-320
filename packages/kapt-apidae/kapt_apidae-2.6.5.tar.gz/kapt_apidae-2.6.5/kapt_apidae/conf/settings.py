import os

from django.conf import settings

from kapt_apidae.utils import default_parse_booking_link


# Secrets handling
# --------------------------------------
def get_secret(setting, default=None):
    try:
        if os.environ[setting].lower() in ("true", "on"):
            return True
        elif os.environ[setting].lower() in ("false", "off"):
            return False
        return os.environ[setting]
    except KeyError:
        return default


# Import from kapt_apidae to kapt_catalog tree when running kapt_apidae -d
APIDAE_IN_KAPT_CATALOG = getattr(settings, "KT_APIDAE_IN_KAPT_CATALOG", True)

# Force activity slug generation (useful if kapt_catalog ACTIVITY_AUTOMATIC_SLUG_GENERATION is False in case of multiSIT)
GENERATE_ACTIVITY_SLUG = getattr(
    settings, "KT_APIDAE_FORCE_ACTIVITY_SLUG_GENERATION", False
)

# Provide here a list of characteristics identifiers that must'nt be updated by import_apidae_kaptravel -i command
EXCLUDED_CHARACTERISTICS_UPDATE = getattr(
    settings, "KT_APIDAE_EXCLUDED_CHARACTERISTICS_UPDATE", []
)

# If you do not want the global aspect, define here the aspect to use
ASPECT = getattr(settings, "KT_APIDAE_ASPECT", None)

# If you want to handle several aspects
ASPECTS = getattr(settings, "KT_APIDAE_ASPECTS", None)

# If you want to exclude some touristic Objects
IGNORE_LIST = getattr(settings, "KT_APIDAE_IGNORE_LIST", [])

# Former identifier
APIDAE_PREFIX = getattr(settings, "KT_APIDAE_PREFIX", "APIDAE_")
APIDAE_FORMER_IDENTIFIER = APIDAE_PREFIX + "%s"

# Membership Status
MEMBER_ON_AREA_STATUS = getattr(
    settings, "KT_APIDAE_MEMBER_ON_AREA_STATUS", "member-on-the-area"
)
MEMBER_OUTSIDE_AREA_STATUS = getattr(
    settings, "KT_APIDAE_MEMBER_OUTSIDE_AREA_STATUS", "member-outside-area"
)
NOT_MEMBER_STATUS = getattr(settings, "KT_APIDAE_NOT_MEMBER_STATUS", "not-member")
ADHERENT_VARIABLE_ATTRIBUTE = getattr(
    settings, "KT_APIDAE_ADHERENT_VARIABLE_ATTRIBUTE", None
)
AREA_ID = getattr(settings, "KT_APIDAE_AREA_ID", None)
# Auto import Apidae data
AUTO_IMPORT = getattr(settings, "KT_APIDAE_AUTO_IMPORT", True)

# Duplicate notification import
DUPLICATE_NOTIFICATION = getattr(settings, "KT_APIDAE_DUPLICATE_NOTIFICATION", False)
DUPLICATE_URLS = getattr(settings, "KT_APIDAE_DUPLICATE_URLS", [])

# Min max prices
IMPORT_UNUSUAL_ACCOMMODATION_RATES_TYPE = getattr(
    settings, "KT_APIDAE_IMPORT_UNUSUAL_ACCOMMODATION_RATES_TYPE", 1484
)
MEAL_RATES_TYPE = getattr(settings, "KT_APIDAE_MEAL_RATES_TYPE", 1502)

IMPORT_OPENSYSTEM_REFERENCES = getattr(
    settings, "KT_APIDAE_IMPORT_OPENSYSTEM_REFERENCES", False
)

IMPORT_FAIRGUEST_METADATA = getattr(
    settings, "KT_APIDAE_IMPORT_FAIRGUEST_METADATA", False
)

# For ah-tourisme
IMPORT_UNUSUAL_ACCOMMODATION_RATES = getattr(
    settings, "KT_APIDAE_IMPORT_UNUSUAL_ACCOMMODATION_RATES", False
)

BOOKING_URL_PARSE_METHOD = getattr(
    settings, "KT_APIDAE_BOOKING_URL_PARSE_METHOD", default_parse_booking_link
)

# Handle apidae's menu in CMS Toolbar
SHOW_CMS_MENU = False
PROJECT_ID = get_secret("KT_APIDAE_PROJECT_ID", None)
PROJECT_API_KEY = get_secret("KT_APIDAE_PROJECT_API_KEY", None)
LOGIN = get_secret("KT_APIDAE_LOGIN", None)
PASSWORD = get_secret("KT_APIDAE_PASSWORD", None)
if all(
    variable is not None for variable in [PROJECT_ID, PROJECT_API_KEY, LOGIN, PASSWORD]
):
    SHOW_CMS_MENU = True

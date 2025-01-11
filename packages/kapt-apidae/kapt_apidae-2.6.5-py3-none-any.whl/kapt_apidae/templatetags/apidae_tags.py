# Third party
from django import template


try:
    from kapt_catalog.utils.functions import get_aspect_name

    register = template.Library()

    @register.simple_tag
    def aspect_name(aspect):
        if aspect is None:
            return "Default"
        return get_aspect_name(aspect)

except ImportError:
    pass

# Standard Library
import sys

# Third party
from model_utils import Choices


def choices_factory(choices):
    """
    Handles dynamic choices for model fields.
    This is required because Django >= 1.7 will introspect the
    content of the choices tuple in order to add the related
    values in the generated migration.
    We have to prevent Django from creating migrations on behalf
    of a third party app.
    """
    if "makemigrations" in sys.argv or "migrate" in sys.argv:  # pragma: no cover
        return []
    return Choices(*choices) if not isinstance(choices, Choices) else choices

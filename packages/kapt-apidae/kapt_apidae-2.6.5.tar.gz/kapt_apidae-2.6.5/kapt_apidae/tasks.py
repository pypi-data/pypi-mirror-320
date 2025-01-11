# Standard Library
import logging

# Third party
from celery import shared_task
from django.core.management import call_command


logger = logging.getLogger(__name__)


@shared_task
def import_kapt_apidae():
    call_command("import_apidae", daily=True)


@shared_task
def force_import_kapt_apidae():
    call_command("import_apidae_kaptravel", force=True)

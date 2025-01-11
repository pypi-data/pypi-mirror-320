# Third party
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

# Local application / specific library imports
from kapt_apidae.conf import settings as apidae_settings
from kapt_apidae.models import ImportsApidaeSettings, TouristicObject
from kapt_apidae.tasks import import_kapt_apidae


@receiver(post_save, sender=ImportsApidaeSettings)
def post_save_apidae_settigns(sender, instance, created, **kwargs):
    if created:
        if apidae_settings.AUTO_IMPORT:
            import_kapt_apidae.delay()


@receiver(pre_delete, sender=TouristicObject)
def pre_delete_touristicalobject(sender, instance, **kwargs):
    # Owner
    owner = instance.owner
    instance.owner = None
    instance.save()
    # If the owner owne only this touristic_object we delete it !
    if owner:
        if owner.touristicobject_set.all().count() == 0:
            owner.delete()

    # Communication infos
    for communication_object in instance.internal_communications.all():
        communication_object.delete()
    for communication_object in instance.external_communications.all():
        communication_object.delete()

    # Opening and closure periods
    for opening_period in instance.opening_periods.all():
        opening_period.delete()
    instance.exceptional_closure_dates.all().delete()

    # Pricing periods
    for pricing_period in instance.pricing_periods.all():
        pricing_period.delete()

    # Booking
    for booking_organisation in instance.booking_organisations.all():
        booking_organisation.delete()

    # Contacts
    for contact in instance.internal_contacts.all():
        contact.delete()
    for contact in instance.external_contacts.all():
        contact.delete()

    # Pictures
    for picture in instance.pictures.all():
        picture.delete()

    for link in instance.links.all():
        link.delete()

    # Meeting rooms
    for meeting_room in instance.meeting_rooms.all():
        meeting_room.delete()


# Registering signals
pre_delete.connect(
    pre_delete_touristicalobject,
    sender=TouristicObject,
    dispatch_uid="pre_delete_touristicalobject",
)

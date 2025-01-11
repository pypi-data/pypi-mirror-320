# Standard Library
from difflib import SequenceMatcher
import os
from os.path import basename
from tempfile import TemporaryFile


try:
    from urllib.parse import urlparse
except ImportError:  # Python 2 fallback
    from urlparse import urlparse

from urllib.parse import urlsplit

# Third party
from PIL import ImageFile
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.utils.text import slugify
from kapt_gallery.models import (
    DailymotionVideoHttpLink,
    DocumentHttpLink,
    Gallery,
    MediaHttpLink,
    MovieFileHttpLink,
    Photo,
    Plan,
    VimeoVideoHttpLink,
    YoutubeVideoHttpLink,
    get_file_name,
)
from kapt_geo.models import Country, Place
import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException
import requests

# Local application / specific library imports
from kapt_apidae.management import ScriptError, logger
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.utils import (
    copy_translated_fields,
)
from kapt_apidae.models import MULTIMEDIA_TYPE_CHOICES, ImportsApidaeSettings


ImageFile.LOAD_TRUNCATED_IMAGES = True

CORRESPONDENCE_MULTIMEDIA_LINKS_TYPES = {
    # We deactivate channel because it's not a media, it's more an contact information -> kapt-contact
    # MULTIMEDIA_TYPE_CHOICES.CHAINE_DAILYMOTION: DailymotionVideoHttpLink,
    # MULTIMEDIA_TYPE_CHOICES.CHAINE_YOUTUBE: YoutubeVideoHttpLink,
    MULTIMEDIA_TYPE_CHOICES.DOCUMENT: DocumentHttpLink
}

all_imports_settings = ImportsApidaeSettings.objects.all()

if all_imports_settings.exists():
    user_agent = "KAPT - SITE: {}".format(all_imports_settings[0].projetId)
else:
    user_agent = "KAPT"


def download_to_file_field(url, field):
    with TemporaryFile() as tf:
        r = requests.get(url, stream=True, headers={"User-Agent": user_agent})
        for chunk in r.iter_content(chunk_size=4096):
            tf.write(chunk)

        tf.seek(0)
        field.save(basename(urlsplit(url).path), File(tf))


def update_contact_communication_infos(contact_object, communication_infos):
    # Re-init contact_object communication infos
    contact_object.first_phone_number = None
    contact_object.fax_phone_number = None
    contact_object.first_email = None
    contact_object.second_email = None
    contact_object.second_phone_number = None
    contact_object.website_url = None
    contact_object.facebook_url = None
    contact_object.twitter_url = None
    contact_object.googleplus_url = None

    # Fill communication
    for communication_info in communication_infos:
        try:
            if communication_info.type_id in [201, 206]:
                if not contact_object.first_phone_number:
                    contact_object.first_phone_number = phonenumbers.format_number(
                        phonenumbers.parse(communication_info.value, "FR"),
                        phonenumbers.PhoneNumberFormat.E164,
                    )
                elif not contact_object.second_phone_number:
                    contact_object.second_phone_number = phonenumbers.format_number(
                        phonenumbers.parse(communication_info.value, "FR"),
                        phonenumbers.PhoneNumberFormat.E164,
                    )
            elif communication_info.type_id in [202, 206]:
                if not contact_object.fax_phone_number:
                    contact_object.fax_phone_number = phonenumbers.format_number(
                        phonenumbers.parse(communication_info.value, "FR"),
                        phonenumbers.PhoneNumberFormat.E164,
                    )
            elif communication_info.type_id == 204:
                if not contact_object.first_email:
                    contact_object.first_email = communication_info.value
                elif not contact_object.second_email:
                    contact_object.second_email = communication_info.value
            elif communication_info.type_id == 205:
                if not contact_object.website_url:
                    contact_object.website_url = communication_info.value
            elif communication_info.type_id == 207:
                if not contact_object.facebook_url:
                    contact_object.facebook_url = communication_info.value
            elif communication_info.type_id == 3755:
                if not contact_object.twitter_url:
                    contact_object.twitter_url = communication_info.value
            elif communication_info.type_id == 3789:
                if not contact_object.googleplus_url:
                    contact_object.googleplus_url = communication_info.value
        except NumberParseException as e:
            logger.warning(
                str(contact_object.__class__.__name__)
                + " n° "
                + str(contact_object.id)
                + " : "
                + str(e)
            )

    return contact_object


def _test_gallery(structure):
    if structure.gallery:
        gallery = structure.gallery
    else:
        gallery = Gallery()

    gallery.name = "structure_%d" % structure.id
    gallery.slugname = slugify(gallery.name)
    gallery.save()

    # Attach gallery to activity
    structure.gallery = gallery
    structure.save()
    return gallery


def update_gallery(structure, touristic_object):
    # If pictures
    if touristic_object.pictures.exists():
        gallery = _test_gallery(structure)

        # Erase photo order in gallery
        gallery.photo_set.all().update(number=None)

        photos_ids = []
        photo_loop = 0
        for picture in touristic_object.pictures.all().order_by("pk"):
            photo_loop += 1
            file_objects = picture.files.filter(locale="fr")
            if file_objects.exists():
                file_object = file_objects[0]
                try:
                    photo_slug = slugify(file_object.url)
                    photo_object = gallery.photo_set.filter(
                        former_identifier=photo_slug
                    )
                    if photo_object.exists():
                        photo_object = photo_object[0]
                    else:
                        photo_object = Photo(
                            gallery=gallery, former_identifier=photo_slug
                        )

                    # Update photo number
                    photo_object.number = photo_loop
                    photo_path = os.path.join(
                        settings.MEDIA_ROOT,
                        get_file_name(photo_object, os.path.basename(file_object.url)),
                    )
                    photo_path_exists = os.path.isfile(photo_path)

                    if (
                        photo_object.upload_date != file_object.modification_date
                        or not photo_path_exists
                    ):
                        if photo_path_exists:
                            os.remove(photo_path)
                        download_to_file_field(file_object.url, photo_object.file)

                    # Update type
                    if photo_loop == 1:
                        photo_object.type = "main"
                    elif picture.type == "IMAGE":
                        photo_object.type = "gallery"
                    else:
                        raise ScriptError(
                            "Image type (main image, gallery image ...) not handle",
                            file_object,
                        )

                    # Retrieve "fr" name or global
                    copy_translated_fields(picture, photo_object, "name", "name")
                    # Retrieve "fr" copyright or global
                    copy_translated_fields(
                        picture, photo_object, "copyright", "copyright"
                    )
                    # Retrieve labels
                    copy_translated_fields(picture, photo_object, "legend", "label")
                    # Update modification date
                    photo_object.upload_date = file_object.modification_date
                    # Save
                    photo_object.save()
                    photos_ids.append(photo_object.id)

                    # You may need to update your thumbs here
                except (KeyError, OSError) as exception:
                    logger.warning(
                        "%s : Cannot identify image file %s: %s"
                        % (str(__file__.__class__.__name__), file_object.url, exception)
                    )

        # Handle removal
        for photo in gallery.photo_set.exclude(id__in=photos_ids):
            photo.delete()

    elif structure.gallery is not None:
        [photo.delete() for photo in structure.gallery.photo_set.all()]
        structure.gallery.save()

    # Fetch or remove the links associated with the touristic object that can be embedded in
    # a KapTravel gallery.
    if touristic_object.links.exists():
        gallery = _test_gallery(structure)

        # if plans
        plan_ids = []
        plan_loop = 0
        for plan in touristic_object.links.filter(type="PLAN").order_by("pk"):
            plan_loop += 1
            file_objects = plan.files.filter(locale="fr")
            if file_objects.exists():
                file_object = file_objects[0]
                try:
                    plan_number = plan_loop
                    plan_slug = slugify(file_object.url)
                    plan_object = gallery.photo_set.filter(former_identifier=plan_slug)
                    if plan_object.exists():
                        plan_object = plan_object[0]
                        if plan_object.upload_date == file_object.modification_date:
                            plan_ids.append(plan_object.id)

                            # Retrieve "fr" name or global
                            if plan.name_fr is not None:
                                plan_object.name = plan.name_fr
                            else:
                                plan_object.name = plan.name

                            # Retrieve "fr" copyright or global
                            if plan.copyright_fr is not None:
                                plan_object.copyright = plan.copyright_fr
                            else:
                                plan_object.copyright = plan.copyright

                            # Retrieve labels
                            copy_translated_fields(plan, plan_object, "legend", "label")
                            plan_object.number = plan_number
                            plan_object.save()
                            continue
                    else:
                        plan_object = Plan(gallery=gallery, former_identifier=plan_slug)

                    plan_object.number = plan_number

                    # Retrieve "fr" name or global
                    if plan.name_fr is not None:
                        plan_object.name = plan.name_fr
                    else:
                        plan_object.name = plan.name

                    # Retrieve "fr" copyright or global
                    if plan.copyright_fr is not None:
                        plan_object.copyright = plan.copyright_fr
                    else:
                        plan_object.copyright = plan.copyright

                    # Retrieve labels
                    copy_translated_fields(plan, plan_object, "legend", "label")
                    download_to_file_field(file_object.url, plan_object.file)
                    plan_object.save()
                    plan_object.upload_date = file_object.modification_date
                    plan_object.save()
                    plan_ids.append(plan_object.id)

                    # You may need to update your thumbs here
                except (KeyError, OSError) as exception:
                    logger.warning(
                        "%s : Cannot identify image file %s: %s"
                        % (str(__file__.__class__.__name__), file_object.url, exception)
                    )

            # Handle removal
            for plan in gallery.plan_set.exclude(id__in=plan_ids):
                plan.delete()

        # Handle videos
        added_links_ids = []
        for media_link in touristic_object.links.all():
            if media_link.type in CORRESPONDENCE_MULTIMEDIA_LINKS_TYPES.keys():
                for multimedia in media_link.files.all():
                    if multimedia.url:
                        if media_link.type in [MULTIMEDIA_TYPE_CHOICES.DOCUMENT]:
                            link = DocumentHttpLink(
                                gallery=structure.gallery,
                                url=multimedia.url,
                                type=media_link.type,
                                extension=multimedia.extension,
                                locale=multimedia.locale,
                            )
                        else:
                            link = CORRESPONDENCE_MULTIMEDIA_LINKS_TYPES[
                                media_link.type
                            ](
                                gallery=structure.gallery,
                                url=multimedia.url,
                                locale=multimedia.locale,
                            )
                        copy_translated_fields(media_link, link, "name", "label")
                        link.save()
                        added_links_ids.append(link.id)
            else:
                for multimedia in media_link.files.filter(locale="fr"):
                    if multimedia.url:
                        if media_link.type == "VIDEO":
                            if multimedia.extension is not None:
                                link = MovieFileHttpLink(
                                    gallery=structure.gallery, url=multimedia.url
                                )
                            else:
                                parsed_uri = urlparse(multimedia.url)
                                domain = "{uri.scheme}://{uri.netloc}/".format(
                                    uri=parsed_uri
                                )
                                if "youtube" in domain or "youtu.be" in domain:
                                    link = YoutubeVideoHttpLink(
                                        gallery=structure.gallery, url=multimedia.url
                                    )
                                elif "vimeo" in domain:
                                    link = VimeoVideoHttpLink(
                                        gallery=structure.gallery, url=multimedia.url
                                    )
                                elif "dailymotion" in domain:
                                    link = DailymotionVideoHttpLink(
                                        gallery=structure.gallery, url=multimedia.url
                                    )
                                else:
                                    link = MediaHttpLink(
                                        gallery=structure.gallery, url=multimedia.url
                                    )
                        else:
                            link = MediaHttpLink(
                                gallery=structure.gallery, url=multimedia.url
                            )
                        copy_translated_fields(media_link, link, "name", "label")
                        link.save()
                        added_links_ids.append(link.id)

        # Handle removal
        for link in gallery.media_links.exclude(id__in=added_links_ids):
            link.delete()

    elif structure.gallery is not None:
        # structure.gallery.delete()
        # structure.gallery = None
        [link.delete() for link in structure.gallery.media_links.all()]
        [plan.delete() for plan in structure.gallery.plan_set.all()]
        structure.gallery.save()


def update_address_object(touristic_object, address_object, country_code="FR"):
    # Get country code
    country = Country.objects.get(fips_code=country_code)
    # Get and set place
    place_object = None
    try:
        places = Place.objects.filter(
            country=country,
            admin4_code=touristic_object.locality.code,
            feature_class="P",
        )
        if not places.exists():
            places = Place.objects.filter(
                country=country,
                admin2_code=touristic_object.locality.code[:2],
                name=touristic_object.locality.name,
                feature_class="P",
            )
            if not places.exists():
                places = Place.objects.filter(
                    country=country,
                    admin2_code=touristic_object.locality.code[:2],
                    feature_class="P",
                )
        for place in places:
            geoname_slug = slugify(place.name)
            if geoname_slug.find("saint") == 0:
                geoname_slug = "st%s" % geoname_slug[5:]
            if geoname_slug == slugify(touristic_object.locality.name):
                place_object = place
            if touristic_object.address_3 and geoname_slug == slugify(
                touristic_object.address_3
            ):
                place_object = place

        if not place_object:
            high_value = 0
            high_locality = None
            for place in places:
                geoname_slug = slugify(place.name)
                city_slug = slugify(touristic_object.locality.name)
                if geoname_slug.find("saint") == 0:
                    geoname_slug = "st%s" % geoname_slug[5:]
                s = SequenceMatcher(None, geoname_slug, city_slug)
                ratio = s.ratio()
                if ratio > high_value:
                    high_value = ratio
                    high_locality = place
            place_object = high_locality
    except ObjectDoesNotExist:
        logger.error("Unknown place for id : " + str(touristic_object.id))

    # Address
    # Re-init: id address1 is still None before saving it will fail
    address1 = address2 = None

    # Set addresses
    if touristic_object.address_1:
        address1 = touristic_object.address_1
        if touristic_object.address_2:
            address2 = touristic_object.address_2
        elif touristic_object.address_3:
            address2 = touristic_object.address_3
    elif touristic_object.address_2:
        address1 = touristic_object.address_2
        if touristic_object.address_3:
            address2 = touristic_object.address_3
    elif touristic_object.address_3:
        address1 = touristic_object.address_3
    return address_object.update_address(
        address1=address1,
        address2=address2,
        latitude=touristic_object.latitude,
        longitude=touristic_object.longitude,
        place=place_object,
    )

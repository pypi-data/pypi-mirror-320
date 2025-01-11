# Third party
from django.contrib.contenttypes.models import ContentType
from django.contrib.sitemaps import ping_google
from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver

# Local application / specific library imports
from kapt_catalog.conf import settings as catalog_settings
from kapt_catalog.models import (
    Activity,
    ActivityReference,
    Description,
    Structure,
    StructureReference,
)
from kapt_catalog.models.activities.accommodation import (
    AccommodationActivity,
    Bed,
    BedReference,
    BnBActivity,
    CamperVanActivity,
    CampingActivity,
    HolidayVillageActivity,
    HomestayActivity,
    HotelActivity,
    RelayActivity,
    RentalActivity,
    RiadActivity,
    Room,
    RoomReference,
    YouthHostelActivity,
)
from kapt_catalog.models.activities.event import EventActivity
from kapt_catalog.models.activities.leisure import LeisureActivity
from kapt_catalog.models.activities.meal import InnActivity, MealActivity, TableActivity
from kapt_catalog.models.activities.pack import PackActivity
from kapt_catalog.models.activities.poi import PointOfInterestActivity


@receiver(pre_save, sender=Structure)
def create_reference(sender, instance, **kwargs):
    if not instance.reference_id:
        instance.reference = StructureReference.objects.create()


@receiver(pre_delete, sender=Structure, dispatch_uid="pre_delete_structure")
def structure_pre_delete(sender, **kwargs):
    """
    Prevents orphans from being created in the database (eg: with generic fk)
    """

    instance = kwargs["instance"]
    # Descriptions
    descriptions = Description.objects.filter(
        content_type=ContentType.objects.get_for_model(instance), object_id=instance.id
    )
    for description in descriptions:
        description.delete()


@receiver(pre_save, sender=ActivityReference, dispatch_uid="pre_save_activityreference")
def activityreference_pre_save(sender, **kwargs):
    """
    Create an activity number, relative to its Structure, and fill former_identifier and formatted_identifier fields
    """
    # Avoid circular import, if you find a better way...
    from kapt_catalog.models import StructureReference

    instance = kwargs["instance"]
    if not instance.activity_number:
        try:
            structure_reference = instance.structure_reference
        except StructureReference.DoesNotExist:  # pragma: no cover
            raise LookupError(
                "StructureReference is missing. Is it excluded form the form?"
            )

        if structure_reference.activityreference_set.exists():
            last_activity_number = (
                structure_reference.activityreference_set.all().order_by(
                    "-activity_number"
                )[:1][0]
            )
            instance.activity_number = last_activity_number.activity_number + 1

        else:
            instance.activity_number = 1

    if (
        not instance.former_identifier
        and instance.structure_reference.former_identifier
    ):
        structure_former_identifier = instance.structure_reference.former_identifier
        instance.former_identifier = "{}_{}".format(
            structure_former_identifier,
            instance.activity_number,
        )

    if (
        not instance.formatted_identifier
        and instance.structure_reference.formatted_identifier
    ):
        structure_formatted_identifier = (
            instance.structure_reference.formatted_identifier
        )
        instance.formatted_identifier = "{}-{}".format(
            structure_formatted_identifier,
            instance.activity_number,
        )


def activity_pre_save(sender, **kwargs):
    """
    Creates an activity reference if it does not exist
    """
    # Avoid circular import, if you find a better way...
    from kapt_catalog.models import ActivityReference

    instance = kwargs["instance"]
    if not instance.reference_id:
        structure_reference = instance.structure.reference
        instance.reference = ActivityReference.objects.create(
            structure_reference=structure_reference
        )


def activity_post_save(sender, **kwargs):
    """
    Handles coherence between the activity and its reference.
    """
    instance = kwargs["instance"]
    created = kwargs.get("created", False)
    if created:
        # As the ActivityReference instance is created before the Activity instance
        # some signal receivers based on the 'post_save' signal on ActivityReference
        # instances might not work. If the activity was created, we trigger this signal
        # again.
        instance.reference.save()


def activity_pre_delete(sender, **kwargs):
    """
    Prevents orphans from being created in the database (eg: with generic fk)
    """

    instance = kwargs["instance"]
    # Descriptions
    descriptions = Description.objects.filter(
        content_type=ContentType.objects.get_for_model(instance), object_id=instance.id
    )
    for description in descriptions:
        description.delete()


def ping_google_activity_handler(sender, **kwargs):
    activity = kwargs["instance"]

    if activity.is_active:
        try:
            if catalog_settings.ACTIVITY_SITEMAP_PING_GOOGLE_URL:
                ping_google(catalog_settings.ACTIVITY_SITEMAP_PING_GOOGLE_URL)
            else:
                ping_google()
        except Exception:
            # Bare 'except' because we could get a variety
            # of HTTP-related exceptions.
            pass


pre_delete.connect(
    activity_pre_delete, sender=Activity, dispatch_uid="pre_delete_activity"
)
pre_save.connect(activity_pre_save, sender=Activity, dispatch_uid="pre_save_activity")
post_save.connect(
    activity_post_save, sender=Activity, dispatch_uid="post_save_activity"
)
for subclass in [
    AccommodationActivity,
    EventActivity,
    LeisureActivity,
    MealActivity,
    PointOfInterestActivity,
    BnBActivity,
    RentalActivity,
    CampingActivity,
    CamperVanActivity,
    HotelActivity,
    HolidayVillageActivity,
    RelayActivity,
    YouthHostelActivity,
    HomestayActivity,
    RiadActivity,
    TableActivity,
    InnActivity,
    PackActivity,
]:
    pre_delete.connect(
        activity_pre_delete,
        sender=subclass,
        dispatch_uid="pre_delete_activity_{}".format(subclass.__name__.lower()),
    )
    pre_save.connect(
        activity_pre_save,
        sender=subclass,
        dispatch_uid="pre_save_activity_{}".format(subclass.__name__.lower()),
    )
    post_save.connect(
        activity_post_save,
        sender=subclass,
        dispatch_uid="post_save_activity_{}".format(subclass.__name__.lower()),
    )


if catalog_settings.ACTIVITY_SITEMAP_PING_GOOGLE:
    post_save.connect(
        ping_google_activity_handler,
        sender=Activity,
        dispatch_uid="post_save_activity_ping_google",
    )
    for subclass in [
        AccommodationActivity,
        EventActivity,
        LeisureActivity,
        MealActivity,
        PointOfInterestActivity,
        BnBActivity,
        RentalActivity,
        CampingActivity,
        CamperVanActivity,
        HotelActivity,
        HolidayVillageActivity,
        RelayActivity,
        YouthHostelActivity,
        HomestayActivity,
        RiadActivity,
        TableActivity,
        InnActivity,
    ]:
        post_save.connect(
            ping_google_activity_handler,
            sender=subclass,
            dispatch_uid="post_save_activity_ping_google_{}".format(
                subclass.__name__.lower()
            ),
        )


@receiver(pre_save, sender=RoomReference, dispatch_uid="pre_save_roomreference")
def roomreference_pre_save(sender, **kwargs):
    """
    Create an room number, relative to its AccommodationActivity, and fill former_identifier and formatted_identifier fields
    """
    # Avoid circular import, if you find a better way...
    from kapt_catalog.models import ActivityReference

    instance = kwargs["instance"]
    if not instance.room_number:
        try:
            activity_reference = instance.activity_reference
        except ActivityReference.DoesNotExist:
            raise LookupError("ActivityReference is missing")

        if activity_reference.roomreference_set.exists():
            last_room_number = activity_reference.roomreference_set.all().order_by(
                "-room_number"
            )[:1][0]
            instance.room_number = last_room_number.room_number + 1

        else:
            instance.room_number = 1

    if not instance.former_identifier and instance.activity_reference.former_identifier:
        activity_former_identifier = instance.activity_reference.former_identifier
        instance.former_identifier = "{}_{}".format(
            activity_former_identifier,
            instance.room_number,
        )

    if (
        not instance.formatted_identifier
        and instance.activity_reference.formatted_identifier
    ):
        activity_formatted_identifier = instance.activity_reference.formatted_identifier
        instance.formatted_identifier = "{}-{}".format(
            activity_formatted_identifier,
            instance.room_number,
        )


@receiver(pre_save, sender=BedReference, dispatch_uid="pre_save_bedreference")
def bedreference_pre_save(sender, **kwargs):
    """
    Create an bed number, relative to its Room, and fill former_identifier and formatted_identifier fields
    """
    # Avoid circular import, if you find a better way...
    from kapt_catalog.models import RoomReference

    instance = kwargs["instance"]
    if not instance.bed_number:
        try:
            room_reference = instance.room_reference
        except RoomReference.DoesNotExist:
            raise LookupError("RoomReference is missing")

        if room_reference.bedreference_set.exists():
            last_bed_number = room_reference.bedreference_set.all().order_by(
                "-bed_number"
            )[:1][0]
            instance.bed_number = last_bed_number.bed_number + 1

        else:
            instance.bed_number = 1

    if not instance.former_identifier and instance.room_reference.former_identifier:
        room_former_identifier = instance.room_reference.former_identifier
        instance.former_identifier = "{}_{}".format(
            room_former_identifier,
            instance.bed_number,
        )

    if (
        not instance.formatted_identifier
        and instance.room_reference.formatted_identifier
    ):
        room_formatted_identifier = instance.room_reference.formatted_identifier
        instance.formatted_identifier = "{}-{}".format(
            room_formatted_identifier,
            instance.bed_number,
        )


@receiver(pre_save, sender=Room, dispatch_uid="pre_save_room")
def room_pre_save(sender, **kwargs):
    """
    Creates a room reference if it does not exist
    """
    instance = kwargs["instance"]
    if not instance.reference_id:
        activity_reference = instance.accommodation.reference
        room_reference = RoomReference(activity_reference=activity_reference)
        room_reference.save()
        instance.reference = room_reference


@receiver(pre_save, sender=Bed, dispatch_uid="pre_save_bed")
def bed_pre_save(sender, **kwargs):
    """
    Creates a bed reference if it does not exist
    """
    # Avoid circular import, if you find a better way...
    from kapt_catalog.models import BedReference

    instance = kwargs["instance"]
    if not instance.reference_id:
        room_reference = instance.room.reference
        instance.reference = BedReference.objects.create(room_reference=room_reference)

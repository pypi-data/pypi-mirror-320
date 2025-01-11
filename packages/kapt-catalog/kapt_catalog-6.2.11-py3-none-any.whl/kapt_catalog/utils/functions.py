# Third party
from django.conf import settings
from django.utils import translation
from kapt_gallery.models import Photo

# Local application / specific library imports
from kapt_catalog.constants import PREFECTORAL_LABELLING_CHARACTERISTIC_IDENTIFIER
from kapt_catalog.models import (
    ActivityTranslation,
    Description,
    Structure,
    StructureReference,
)
from kapt_catalog.models.activities import Labelling
from kapt_catalog.models.characteristic import Characteristic


def fetch_translated_descriptions_form_data(form_instance, translated_fields):
    """
    Retrieve the data associated with the given characteristics and initialize the fields of the considered ModelForm.
    These data are fetched for each language defined in the Django settings.
    The translated fields must be specified as follow:
        translated_fields = (
            (
                'description-website-location',     # Prefix of the form field AND slug of the wanted characteristic
                forms.CharField,                    # Form field class
                {'label': _('Number')}              # Form field class arguments
            ),
            # ...
        )
    """
    model_instance = form_instance.instance
    for field in translated_fields:
        try:
            descriptions = model_instance.descriptions.all().filter(
                type=Characteristic.objects.get(identifier=field[0])
            )
            assert len(descriptions) == 1
        except AssertionError:
            pass
        else:
            for language in settings.LANGUAGES:
                form_instance.fields[field[0] + "_" + language[0]].initial = getattr(
                    descriptions[0], "text_" + language[0]
                )


def save_translated_descriptions_form_data(
    form_instance, translated_fields, commit=True
):
    """
    Save the data associated with the given characteristics by using the cleaned data of the associated fields of the considered ModelForm.
    These data are saved for each language defined in the Django settings.
    The translated fields must be specified as follow:
        translated_fields = (
            (
                'description-website-location',     # Prefix of the form field AND slug of the wanted characteristic
                forms.CharField,                    # Form field class
                {'label': _('Number')}              # Form field class arguments
            ),
            # ...
        )
    """
    model_instance = form_instance.instance
    descriptions = list()
    for field in translated_fields:
        env_type = Characteristic.objects.get(identifier=field[0])
        # Fetch the description object
        try:
            descriptions_list = model_instance.descriptions.all().filter(
                type=Characteristic.objects.get(identifier=field[0])
            )
            assert len(descriptions_list) == 1
        except AssertionError:
            # Else create it
            text_langs = {}
            for language in settings.LANGUAGES:
                text_langs["text_" + [0]] = form_instance.cleaned_data[
                    field[0] + "_" + language[0]
                ]
            description = Description(
                content_object=model_instance, type=env_type, **text_langs
            )
        else:
            description = descriptions_list[0]
            [
                setattr(
                    description,
                    "text_" + language[0],
                    form_instance.cleaned_data[field[0] + "_" + language[0]],
                )
                for language in settings.LANGUAGES
            ]
        descriptions.append(description)

    if commit:
        # Save descriptions
        [description.save() for description in descriptions]


def retrieve_main_photos_of_activity_qs(activity_qs, structure_ids=None):
    if structure_ids is None:
        structure_ids = [a.structure_id for a in activity_qs]

    activity_main_photos = Photo.objects.filter(
        type=Photo.TYPE.main, gallery__structure__id__in=structure_ids
    ).values("gallery__structure", "file")
    photos_dict = {}
    for p in activity_main_photos:
        photos_dict[p["gallery__structure"]] = p["file"]

    for a in activity_qs:
        a.photo = photos_dict[a.structure_id] if a.structure_id in photos_dict else None


def retrieve_address_of_activity_qs(activity_qs, structure_ids=None):
    if structure_ids is None:
        structure_ids = [a.structure_id for a in activity_qs]

    structures = (
        Structure.objects.filter(pk__in=structure_ids)
        .only("id", "address")
        .select_related("address__place")
    )

    address_dict = {}

    for structure in structures:
        address_dict[structure.id] = structure.address

    for a in activity_qs:
        a.structure.address = (
            address_dict[a.structure_id] if a.structure_id in address_dict else None
        )
        a.address = (
            address_dict[a.structure_id] if a.structure_id in address_dict else None
        )


def retrieve_translations_of_activity_qs(activity_qs):
    activity_ids = [a.id for a in activity_qs]
    language_code = translation.get_language()
    default_language_code = settings.PARLER_DEFAULT_LANGUAGE_CODE

    parler_translations = ActivityTranslation.objects.filter(
        master_id__in=activity_ids,
        language_code__in=[language_code, default_language_code],
    )

    translations_dict = {}

    for parler_translation in parler_translations:
        if (
            parler_translation.master_id not in translations_dict
            or parler_translation.language_code == language_code
        ):
            translations_dict[parler_translation.master_id] = parler_translation

    for a in activity_qs:
        a.structure.parler_translations = (
            translations_dict[a.id] if a.id in translations_dict else None
        )


def retrieve_types_of_activity_qs(activity_qs):
    activity_type_ids = [a.type_id for a in activity_qs]

    types = Characteristic.objects.filter(pk__in=activity_type_ids)

    types_dict = {}

    for t in types:
        types_dict[t.id] = t

    for a in activity_qs:
        a.type = types_dict[a.type_id]


def retrieve_labelling_of_activity_qs(activity_qs):
    activity_ids = [a.pk for a in activity_qs]
    activity_labellings = {a.pk: [] for a in activity_qs}

    labellings = Labelling.objects.filter(activity__id__in=activity_ids).select_related(
        "touristic_label__rating_unit"
    )

    for labelling in labellings:
        activity_labellings[labelling.activity_id].append(labelling)

    for a in activity_qs:
        a.labelling_prefetch = []

        for labelling in activity_labellings[a.pk]:
            a.labelling_prefetch.append(labelling)

            if a.main_labelling_id == labelling.id:
                a.main_labelling = labelling
            elif (
                labelling.touristic_label.identifier
                == PREFECTORAL_LABELLING_CHARACTERISTIC_IDENTIFIER
            ):
                a.prefectoral_labelling = labelling


def retrieve_tags_of_activity_qs(activity_qs):
    activities_structure_references_ids = {}
    structure_references_ids = []

    for a in activity_qs:
        activities_structure_references_ids[a.id] = a.structure.reference_id
        structure_references_ids.append(a.structure.reference_id)

    structure_references = {
        sr.pk: sr.tags.all()
        for sr in StructureReference.objects.filter(
            pk__in=structure_references_ids
        ).prefetch_related("tags")
    }

    for a in activity_qs:
        a.tags = structure_references[activities_structure_references_ids[a.id]]


def get_aspect_name(aspect):
    ASPECTS = {
        1: "HIVER",
        2: "ETE",
        3: "HANDICAP",
        4: "TOURISME_AFFAIRES",
        5: "GROUPES",
        6: "PRESTATAIRE_ACTIVITES",
    }
    if aspect:
        return ASPECTS[aspect]

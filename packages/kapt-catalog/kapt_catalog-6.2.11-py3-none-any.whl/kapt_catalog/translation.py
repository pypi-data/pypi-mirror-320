# Third party
from modeltranslation.translator import TranslationOptions, translator

# Local application / specific library imports
from kapt_catalog.models import (
    ActivityCategory,
    Characteristic,
    Description,
    RatingUnit,
    Structure,
    TouristicLabel,
)
from kapt_catalog.models.activities.accommodation import Room


class StructureTranslationOptions(TranslationOptions):
    fields = ("name",)


class TouristicLabelTranslationOptions(TranslationOptions):
    fields = ("name",)


class RatingUnitTranslationOptions(TranslationOptions):
    fields = ("name",)


class CharacteristicTranslationOptions(TranslationOptions):
    fields = ("name",)


class DescriptionTranslationOptions(TranslationOptions):
    fields = ("text",)


class ActivityCategoryOptions(TranslationOptions):
    fields = ("name",)


class RoomOptions(TranslationOptions):
    fields = ("name",)


translator.register(Structure, StructureTranslationOptions)
translator.register(Characteristic, CharacteristicTranslationOptions)
translator.register(Description, DescriptionTranslationOptions)
translator.register(RatingUnit, RatingUnitTranslationOptions)
translator.register(TouristicLabel, TouristicLabelTranslationOptions)
translator.register(ActivityCategory, ActivityCategoryOptions)
translator.register(Room, RoomOptions)

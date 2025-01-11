# Standard Library
# Standard library imports
import random

# Third party
from django.template.defaultfilters import slugify
import factory
from faker import Factory as FakerFactory

# Local application / specific library imports
from kapt_catalog.models import (
    EVENT_REACHES_CHOICES,
    AccommodationActivity,
    Activity,
    ActivityReference,
    Bed,
    BnBActivity,
    CampingActivity,
    EventActivity,
    InnActivity,
    Labelling,
    LeisureActivity,
    MealActivity,
    MealActivityProducts,
    RatingUnit,
    RelayActivity,
    RentalActivity,
    Room,
    TableActivity,
    TouristicLabel,
)
from kapt_catalog.test.factories.catalog.characteristic import CharacteristicFactory
from kapt_catalog.test.factories.catalog.reference import StructureReferenceFactory
from kapt_catalog.test.factories.catalog.structure import StructureFactory


faker = FakerFactory.create()


class ActivityReferenceFactory(factory.DjangoModelFactory):
    FACTORY_FOR = ActivityReference
    former_identifier = factory.Sequence(lambda t: faker.text(max_nb_chars=40))
    formatted_identifier = factory.Sequence(lambda t: faker.text(max_nb_chars=40))
    activity_number = factory.LazyAttribute(lambda t: faker.random_int())
    structure_reference = factory.SubFactory(StructureReferenceFactory)


class ActivityFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Activity
    reference = factory.SubFactory(ActivityReferenceFactory)
    structure = factory.SubFactory(StructureFactory)
    name = factory.LazyAttribute(lambda t: faker.text(max_nb_chars=50))
    slug = factory.LazyAttribute(lambda t: slugify(t.name))
    type = factory.SubFactory(CharacteristicFactory)


class AccommodationActivityFactory(ActivityFactory):
    FACTORY_FOR = AccommodationActivity
    number_of_floors = 1


class BnBActivityFactory(AccommodationActivityFactory):
    FACTORY_FOR = BnBActivity


class RentalActivityFactory(AccommodationActivityFactory):
    FACTORY_FOR = RentalActivity


class CampingActivityFactory(AccommodationActivityFactory):
    FACTORY_FOR = CampingActivity


class RelayActivityFactory(AccommodationActivityFactory):
    FACTORY_FOR = RelayActivity


class MealActivityFactory(ActivityFactory):
    FACTORY_FOR = MealActivity


class TableActivityFactory(ActivityFactory):
    FACTORY_FOR = TableActivity


class InnActivityFactory(ActivityFactory):
    FACTORY_FOR = InnActivity


class EventActivityFactory(ActivityFactory):
    FACTORY_FOR = EventActivity
    reach = factory.LazyAttribute(
        lambda t: random.choice([x[0] for x in EVENT_REACHES_CHOICES])
    )


class LeisureActivityFactory(ActivityFactory):
    FACTORY_FOR = LeisureActivity


class RoomFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Room
    accommodation = factory.SubFactory(AccommodationActivityFactory)
    name = factory.LazyAttribute(lambda t: faker.text(max_nb_chars=50))


class BedFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Bed
    room = factory.SubFactory(RoomFactory)
    size = factory.SubFactory(CharacteristicFactory)


class TouristicLabelFactory(factory.DjangoModelFactory):
    FACTORY_FOR = TouristicLabel
    name = factory.LazyAttribute(lambda t: faker.text(max_nb_chars=200))
    identifier = factory.LazyAttributeSequence(
        lambda t, n: "{}-{}".format(slugify(faker.text(max_nb_chars=20)), t)
    )


class RatingUnitFactory(factory.DjangoModelFactory):
    FACTORY_FOR = RatingUnit
    name = factory.LazyAttribute(lambda t: faker.text(max_nb_chars=30))
    identifier = factory.LazyAttributeSequence(
        lambda t, n: "{}-{}".format(faker.text(max_nb_chars=20), t)
    )


class LabellingFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Labelling
    activity = factory.SubFactory(ActivityFactory)
    touristic_label = factory.SubFactory(TouristicLabelFactory)
    rating = factory.LazyAttribute(lambda t: random.randrange(0, 5))
    priority = factory.LazyAttribute(lambda t: random.randrange(0, 5))


class MealActivityProductsFactory(factory.DjangoModelFactory):
    FACTORY_FOR = MealActivityProducts
    mealactivity = factory.SubFactory(MealActivityFactory)
    product = factory.SubFactory(CharacteristicFactory)
    distance = 10.0

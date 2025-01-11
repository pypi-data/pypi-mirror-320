# Third party
import factory
from faker import Factory as FakerFactory

# Local application / specific library imports
from kapt_catalog.models import Characteristic, Description


# Standard library imports


faker = FakerFactory.create()


class CharacteristicFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Characteristic
    name = factory.LazyAttribute(lambda t: faker.text(max_nb_chars=50))
    identifier = factory.LazyAttribute(lambda t: faker.slug(value=None))


class DescriptionFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Description
    type = factory.SubFactory(CharacteristicFactory)
    text = factory.LazyAttribute(lambda t: faker.text())

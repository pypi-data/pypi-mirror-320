# Third party
import factory
from faker import Factory as FakerFactory

# Local application / specific library imports
from kapt_catalog.models import StructureReference


# Standard library imports


faker = FakerFactory.create()


class StructureReferenceFactory(factory.DjangoModelFactory):
    FACTORY_FOR = StructureReference
    former_identifier = factory.Sequence(lambda t: faker.text(max_nb_chars=40))
    formatted_identifier = factory.Sequence(lambda t: faker.text(max_nb_chars=40))

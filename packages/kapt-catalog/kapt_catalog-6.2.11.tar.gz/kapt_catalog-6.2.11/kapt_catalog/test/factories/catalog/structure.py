# Third party
import factory
from faker import Factory as FakerFactory

# Local application / specific library imports
from kapt_catalog.models import (
    Structure,
    StructureContact,
    StructureNearbyLeisure,
    StructureNearbyServices,
)
from kapt_catalog.test.factories.catalog.characteristic import CharacteristicFactory
from kapt_catalog.test.factories.catalog.reference import StructureReferenceFactory
from kapt_catalog.test.factories.contact import IndividualFactory


# Standard library imports


faker = FakerFactory.create()


class StructureFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Structure
    reference = factory.SubFactory(StructureReferenceFactory)
    name = factory.LazyAttribute(lambda t: faker.text(max_nb_chars=40))


class StructureContactFactory(factory.DjangoModelFactory):
    FACTORY_FOR = StructureContact
    structure = factory.SubFactory(StructureFactory)
    contact = factory.SubFactory(IndividualFactory)


class StructureNearbyLeisureFactory(factory.DjangoModelFactory):
    FACTORY_FOR = StructureNearbyLeisure
    structure = factory.SubFactory(StructureFactory)
    leisure = factory.SubFactory(CharacteristicFactory)
    distance = 10.0


class StructureNearbyServicesFactory(factory.DjangoModelFactory):
    FACTORY_FOR = StructureNearbyServices
    structure = factory.SubFactory(StructureFactory)
    service = factory.SubFactory(CharacteristicFactory)
    distance = 10.0

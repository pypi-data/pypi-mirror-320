# Standard Library
import random

# Third party
import factory
from faker import Factory as FakerFactory
from kapt_contact.models import Individual


faker = FakerFactory.create()


class IndividualFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Individual
    gender = factory.LazyAttribute(lambda n: random.randrange(1, 3))
    first_name = factory.LazyAttribute(lambda t: faker.first_name())
    last_name = factory.LazyAttribute(lambda t: faker.last_name())
    first_email = factory.Sequence(lambda n: "test{}@example.com".format(n))

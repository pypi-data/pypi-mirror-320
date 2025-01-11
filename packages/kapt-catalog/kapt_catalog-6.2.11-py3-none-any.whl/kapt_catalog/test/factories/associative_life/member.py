# Third party
import factory
from faker import Factory as FakerFactory
from kapt_associative_life.models import Member, MembershipStatus

# Local application / specific library imports
from kapt_catalog.test.factories.contact import IndividualFactory


# Standard library imports


faker = FakerFactory.create()


class MembershipStatusFactory(factory.DjangoModelFactory):
    FACTORY_FOR = MembershipStatus
    name = factory.Sequence(lambda t: faker.text(max_nb_chars=30))
    slug_identifier = factory.Sequence(lambda t: faker.slug(value=None))


class MemberFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Member
    referent_contact = factory.SubFactory(IndividualFactory)
    membership_status = factory.SubFactory(MembershipStatusFactory)

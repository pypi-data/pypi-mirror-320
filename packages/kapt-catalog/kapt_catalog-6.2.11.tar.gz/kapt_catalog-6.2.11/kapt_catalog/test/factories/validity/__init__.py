# Third party
import factory
from faker import Factory as FakerFactory
from kapt_validity.models import Period


faker = FakerFactory.create()


class PeriodFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Period
    label = factory.LazyAttribute(lambda t: faker.text(max_nb_chars=10))
    valid_until = factory.LazyAttribute(
        lambda t: faker.date_time_between(start_date="+1y", end_date="+5y")
    )

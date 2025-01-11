# Third party
import factory
from faker import Factory as FakerFactory

# Local application / specific library imports
from .activities import *  # noqa
from .characteristic import *  # noqa
from .reference import *  # noqa
from .structure import *  # noqa
from kapt_catalog.models import SpokenLanguage


faker = FakerFactory.create()


class SpokenLanguageFactory(factory.DjangoModelFactory):
    FACTORY_FOR = SpokenLanguage
    code = factory.LazyAttributeSequence(lambda o, n: "a{}".format(n)[:2])

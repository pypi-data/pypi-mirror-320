# Third party
import factory
from faker import Factory as FakerFactory
from kapt_geo.models import Address, AlternateNames, Continent, Country, Place


# Standard library imports


faker = FakerFactory.create()


class ContinentFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Continent
    geonameid = factory.Sequence(lambda n: n)
    code = factory.LazyAttribute(lambda t: faker.country_code())
    name = factory.LazyAttribute(lambda t: faker.country()[:20])


class CountryFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Country
    geonameid = factory.Sequence(lambda n: n)
    iso_alpha2 = factory.LazyAttribute(lambda t: faker.lexify(text="??"))
    iso_alpha3 = factory.Sequence(lambda t: faker.lexify(text="???"))
    iso_numeric = factory.Sequence(lambda t: faker.random_int())
    fips_code = factory.LazyAttribute(lambda t: faker.lexify(text="???"))
    name = factory.LazyAttribute(lambda t: faker.text(max_nb_chars=200))
    capital = factory.LazyAttribute(lambda t: faker.city())
    area = factory.LazyAttribute(lambda t: faker.random_int())
    population = factory.LazyAttribute(lambda t: faker.random_int())
    continent = factory.SubFactory(ContinentFactory)
    tld = factory.LazyAttribute(lambda t: faker.tld())
    currency_code = factory.LazyAttribute(lambda t: faker.lexify(text="???"))
    languages = factory.LazyAttribute(lambda t: faker.text(max_nb_chars=200))


class PlaceFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Place
    geonameid = factory.Sequence(lambda n: n)
    name = factory.LazyAttribute(lambda t: faker.city())
    country = factory.SubFactory(CountryFactory)
    latitude = factory.LazyAttribute(lambda t: faker.latitude())
    longitude = factory.LazyAttribute(lambda t: faker.longitude())


class AlternateNamesFactory(factory.DjangoModelFactory):
    FACTORY_FOR = AlternateNames
    alternate_name_id = factory.Sequence(lambda n: n)
    place = factory.SubFactory(PlaceFactory)
    isolanguage = factory.Sequence(lambda t: faker.text(max_nb_chars=7))
    alternate_name = factory.Sequence(lambda t: faker.text(max_nb_chars=200))


class AddressFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Address
    place = factory.SubFactory(PlaceFactory)
    latitude = factory.LazyAttribute(lambda t: t.place.latitude)
    longitude = factory.LazyAttribute(lambda t: t.place.longitude)

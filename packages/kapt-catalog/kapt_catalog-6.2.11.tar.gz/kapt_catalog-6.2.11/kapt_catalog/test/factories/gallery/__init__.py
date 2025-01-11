# Third party
from django.template.defaultfilters import slugify
import factory
from faker import Factory as FakerFactory
from kapt_gallery.models import DocumentHttpLink, Gallery, MediaHttpLink


# Standard library imports


faker = FakerFactory.create()


class GalleryFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Gallery
    name = factory.Sequence(lambda t: faker.text(max_nb_chars=50))
    slugname = factory.LazyAttribute(lambda obj: slugify(obj.name))


class MediaHttpLinkFactory(factory.DjangoModelFactory):
    FACTORY_FOR = MediaHttpLink
    gallery = factory.SubFactory(GalleryFactory)
    url = factory.Sequence(lambda t: faker.url())


class DocumentHttpLinkFactory(MediaHttpLinkFactory):
    FACTORY_FOR = DocumentHttpLink
    type = "DOCUMENT"

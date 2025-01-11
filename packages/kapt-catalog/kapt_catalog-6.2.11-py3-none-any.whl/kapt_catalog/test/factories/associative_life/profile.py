# Third party
import factory
from faker import Factory as FakerFactory
from kapt_associative_life.models import ActivityReferenceProfile

# Local application / specific library imports
from kapt_catalog.test.factories.catalog.activities import ActivityReferenceFactory


# Standard library imports


faker = FakerFactory.create()


class ActivityReferenceProfileFactory(factory.DjangoModelFactory):
    FACTORY_FOR = ActivityReferenceProfile
    activity_reference = factory.SubFactory(ActivityReferenceFactory)

    @classmethod
    def create(cls, **kwargs):
        """Create an instance of the associated class, with overriden attrs."""
        if "activity_reference" in kwargs:
            try:
                existing_profile = kwargs["activity_reference"].profile
                existing_profile.delete()
            except ActivityReferenceProfile.DoesNotExist:
                pass
        return super().create(**kwargs)

# Standard Library
from itertools import chain
import logging

# Third party
from django.core.cache import cache
from django.db import models
from django.utils.translation import ugettext_lazy as _
from kapt_utils.models import ActiveModel
from mptt.managers import TreeManager
from mptt.models import MPTTModel, TreeForeignKey


logger = logging.getLogger(__name__)


class CharacteristicTreeManager(TreeManager):  # pragma: no cover
    """
    Add a get_descendants method to the tree manager, allowing to retrieve the descendants of a queryset.
    """

    def get_descendants(self, qs=None, include_self=False, **filters):
        get_queryset = (
            self.get_queryset if hasattr(self, "get_queryset") else self.get_query_set
        )

        if qs is None:
            qs = get_queryset()
        qs = qs.filter(**filters)

        subqueries = []
        for parent_characteristic in qs:
            subqueries.append(parent_characteristic.get_descendants(include_self))
        return list(chain(*subqueries))


# Shall we add Private/Shared somewhere ????
class Characteristic(MPTTModel, ActiveModel):
    parent = TreeForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        verbose_name=_("Parent"),
        on_delete=models.SET_NULL,
    )
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    value = models.CharField(
        max_length=20, verbose_name=_("Value"), blank=True, null=True
    )
    in_search_engine = models.BooleanField(
        verbose_name=_("Is a search engine criteria"), default=False
    )
    is_category = models.BooleanField(verbose_name=_("Is a category"), default=False)
    identifier = models.SlugField(
        max_length=150, unique=True, db_index=True, verbose_name=_("Slug identifier")
    )

    # Managers
    objects = CharacteristicTreeManager()

    class Meta:
        verbose_name = _("Characteristic")
        verbose_name_plural = _("Characteristics")
        app_label = "kapt_catalog"

    def __str__(self):
        return self.name

    def get_active_descendants(self):
        return super().get_descendants().filter(is_active=True)

    def get_choices(self):
        key = "choices-%s" % self.name
        choices = cache.get(key, None)
        if not choices:
            choices = [
                (characteristic.pk, characteristic.name)
                for characteristic in self.get_descendants().filter(is_active=True)
            ]
            cache.set(key, choices)
        return choices

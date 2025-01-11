# Third party
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices


ASPECT_CHOICES = Choices(
    (1, "hiver", _("Winter")),
    (2, "ete", _("Summer")),
    (3, "handicap", _("Handicap")),
    (4, "tourisme_affaires", _("Business tourism")),
    (5, "groupes", _("Groups")),
    (6, "prestataire_activites", _("Activities providers")),
)


class ContentTypeMixin:
    @property
    def contenttype_string(self):
        return "{}.{}".format(self._meta.app_label, self._meta.object_name)


class AspectModel(models.Model):
    aspect = models.PositiveSmallIntegerField(
        verbose_name=_("Aspect"), choices=ASPECT_CHOICES, blank=True, null=True
    )

    class Meta:
        abstract = True

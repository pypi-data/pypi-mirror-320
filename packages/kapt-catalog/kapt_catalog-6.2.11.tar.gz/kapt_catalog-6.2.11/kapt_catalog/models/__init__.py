# Third party
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _

# Local application / specific library imports
from .activities import *  # noqa
from .activities.accommodation import *  # noqa
from .activities.business_tourism import *  # noqa
from .activities.event import *  # noqa
from .activities.leisure import *  # noqa
from .activities.meal import *  # noqa
from .activities.pack import *  # noqa
from .activities.poi import *  # noqa
from .characteristic import *  # noqa
from .reference import *  # noqa
from .structure import *  # noqa


# We copy the whole list from django.conf.global_settings, and replace gettext_noop by ugettext_lazy to get the translation
ALL_LANGUAGES = (
    ("af", _("Afrikaans")),
    ("ar", _("Arabic")),
    ("az", _("Azerbaijani")),
    ("bg", _("Bulgarian")),
    ("be", _("Belarusian")),
    ("bn", _("Bengali")),
    ("br", _("Breton")),
    ("bs", _("Bosnian")),
    ("ca", _("Catalan")),
    ("cs", _("Czech")),
    ("cy", _("Welsh")),
    ("da", _("Danish")),
    ("de", _("German")),
    ("el", _("Greek")),
    ("en", _("English")),
    ("en-gb", _("British English")),
    ("eo", _("Esperanto")),
    ("es", _("Spanish")),
    ("es-ar", _("Argentinian Spanish")),
    ("es-mx", _("Mexican Spanish")),
    ("es-ni", _("Nicaraguan Spanish")),
    ("es-ve", _("Venezuelan Spanish")),
    ("et", _("Estonian")),
    ("eu", _("Basque")),
    ("fa", _("Persian")),
    ("fi", _("Finnish")),
    ("fr", _("French")),
    ("fsl", _("French Sign Language")),
    ("fy-nl", _("Frisian")),
    ("ga", _("Irish")),
    ("gl", _("Galician")),
    ("he", _("Hebrew")),
    ("hi", _("Hindi")),
    ("hr", _("Croatian")),
    ("hu", _("Hungarian")),
    ("hy", _("Armenian")),
    ("ia", _("Interlingua")),
    ("id", _("Indonesian")),
    ("is", _("Icelandic")),
    ("it", _("Italian")),
    ("ja", _("Japanese")),
    ("ka", _("Georgian")),
    ("kk", _("Kazakh")),
    ("km", _("Khmer")),
    ("kn", _("Kannada")),
    ("ko", _("Korean")),
    ("lb", _("Luxembourgish")),
    ("lt", _("Lithuanian")),
    ("lv", _("Latvian")),
    ("mk", _("Macedonian")),
    ("ml", _("Malayalam")),
    ("mn", _("Mongolian")),
    ("nb", _("Norwegian Bokmal")),
    ("ne", _("Nepali")),
    ("nl", _("Dutch")),
    ("nn", _("Norwegian Nynorsk")),
    ("oc", _("Occitan")),
    ("pa", _("Punjabi")),
    ("pl", _("Polish")),
    ("pt", _("Portuguese")),
    ("pt-br", _("Brazilian Portuguese")),
    ("ro", _("Romanian")),
    ("ru", _("Russian")),
    ("sk", _("Slovak")),
    ("sl", _("Slovenian")),
    ("sq", _("Albanian")),
    ("sr", _("Serbian")),
    ("sr-latn", _("Serbian Latin")),
    ("sv", _("Swedish")),
    ("sw", _("Swahili")),
    ("ta", _("Tamil")),
    ("te", _("Telugu")),
    ("th", _("Thai")),
    ("tr", _("Turkish")),
    ("tt", _("Tatar")),
    ("udm", _("Udmurt")),
    ("uk", _("Ukrainian")),
    ("ur", _("Urdu")),
    ("vi", _("Vietnamese")),
    ("zh-cn", _("Simplified Chinese")),
    ("zh-tw", _("Traditional Chinese")),
    ("lsf", _("French sign language")),
)

LANGUAGES_DICT = {x[0]: x[1] for x in ALL_LANGUAGES}


class Description(models.Model):
    text = models.TextField()
    type = models.ForeignKey(
        "Characteristic",
        verbose_name=_("Type"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    automated_translations = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Description")
        verbose_name_plural = _("Descriptions")
        app_label = "kapt_catalog"
        unique_together = ["type", "content_type", "object_id"]

    def __str__(self):
        if self.id:
            if isinstance(self.text, str) and len(self.text) > 20:
                return "{}...".format(self.text[:20])
            else:
                return self.text
        return "New description object"  # pragma: no cover


class SocialTourismInformations(models.Model):
    has_social_rates = models.BooleanField(default=False)
    agreement = models.ForeignKey(
        "Characteristic", related_name="agreement", on_delete=models.CASCADE
    )

    class Meta:
        abstract = True
        app_label = "kapt_catalog"


class GrantInformations(models.Model):
    has_investment_aid = models.BooleanField(default=False)
    ask_for_grant = models.BooleanField(default=False)

    class Meta:
        abstract = True
        app_label = "kapt_catalog"


class SpokenLanguage(models.Model):
    code = models.CharField(
        verbose_name=_("Code"),
        unique=True,
        max_length=10,
        choices=[(x[0], x[1]) for x in ALL_LANGUAGES],
    )

    class Meta:
        verbose_name = _("Spoken language")
        verbose_name_plural = _("Spoken languages")
        app_label = "kapt_catalog"

    def __str__(self):
        return self.get_code_display()

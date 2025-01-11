# Third party
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


# In France, default value is 15 for accommodation with no erp and a limiting capacity
MAXIMUM_CAPACITY_PER_ACCOMMODATION = getattr(
    settings, "MAXIMUM_CAPACITY_PER_ACCOMMODATION", 15
)

# Kept for retrocompatibility but will be removed in catalog 4
MAXIMUM_CAPACITY_WITHOUT_ERP_CERTIFICATE = getattr(
    settings, "MAXIMUM_CAPACITY_WITHOUT_ERP_CERTIFICATE", 15
)


MAXIMUM_CAPACITY_PER_BNB = getattr(
    settings, "MAXIMUM_CAPACITY_PER_BNB", MAXIMUM_CAPACITY_WITHOUT_ERP_CERTIFICATE
)
MAXIMUM_CAPACITY_PER_RELAY = getattr(settings, "MAXIMUM_CAPACITY_PER_RELAY", 50)

# Kept for retrocompatibility
MAXIMUM_CAPACITY_PER_RENTAL = getattr(settings, "MAXIMUM_CAPACITY_PER_RENTAL", 50)

MAXIMUM_CAPACITY_PER_RENTAL_WITH_ERP = getattr(
    settings,
    "KT_CATALOG_MAXIMUM_CAPACITY_PER_RENTAL_WITH_ERP",
    MAXIMUM_CAPACITY_PER_RENTAL,
)
MAXIMUM_CAPACITY_PER_RENTAL_WITHOUT_ERP = getattr(
    settings,
    "KT_CATALOG_MAXIMUM_CAPACITY_PER_RENTAL_WITHOUT_ERP",
    MAXIMUM_CAPACITY_WITHOUT_ERP_CERTIFICATE,
)

# Deprecated an unused. Removed in catalog v4
MAXIMUM_CAPACITY_WITH_ERP_CERTIFICATE = getattr(
    settings, "MAXIMUM_CAPACITY_WITH_ERP_CERTIFICATE", 50
)

DEFAULT_STRUCTURE_CONTACT_TYPE = (
    (0, "owner", _("Owner of the accommodation")),
    (1, "agency", _("Agency (relay or tourism office)")),
    (2, "mandatory", _("Mandatory")),
)

STRUCTURE_CONTACT_TYPE = getattr(
    settings, "KAPT_CATALOG_STRUCTURE_CONTACT_TYPE", DEFAULT_STRUCTURE_CONTACT_TYPE
)

ACCOMMODATION_ACTIVITY_AUTOMATIC_CAPACITY_UPDATE = getattr(
    settings, "ACCOMMODATION_ACTIVITY_AUTOMATIC_CAPACITY_UPDATE", False
)
ACCOMMODATION_ACTIVITY_AUTOMATIC_ROOM_QUANTITY_UPDATE = getattr(
    settings, "ACCOMMODATION_ACTIVITY_AUTOMATIC_ROOM_QUANTITY_UPDATE", False
)
ACCOMMODATION_ACTIVITY_AUTOMATIC_EDGE_ROOM_CAPACITIES_UPDATE = getattr(
    settings, "ACCOMMODATION_ACTIVITY_AUTOMATIC_EDGE_ROOM_CAPACITIES_UPDATE", False
)
ACTIVITY_AUTOMATIC_SLUG_GENERATION = getattr(
    settings, "ACTIVITY_AUTOMATIC_SLUG_GENERATION", True
)

# Sitemaps
ACTIVITY_SITEMAP_ITEMS_LOCATION = getattr(
    settings, "ACTIVITY_SITEMAP_ITEMS_LOCATION", lambda i: i.get_absolute_urls()
)
ACTIVITY_SITEMAP_PING_GOOGLE = getattr(settings, "ACTIVITY_SITEMAP_PING_GOOGLE", False)
ACTIVITY_SITEMAP_PING_GOOGLE_URL = getattr(
    settings, "ACTIVITY_SITEMAP_PING_GOOGLE_URL", False
)
ACTIVITY_SITEMAP_CHANGEFREQ = getattr(
    settings, "ACTIVITY_SITEMAP_CHANGEFREQ", "monthly"
)


# API (TODO: this should be removed as the API is now provided by kapt-site)
SEARCH_RADIUS = getattr(settings, "SEARCH_RADIUS", 50)


DEFAULT_HOUSING_TYPES = (
    (0, "apartment", _("Apartment")),  # Appartement
    (1, "boat", _("Boat")),  # Bateau
    (2, "bungalow", _("Bungalow")),  # Bungalow
    (3, "mobil-home", _("Mobil-home")),  # Mobil-home
    (4, "cabin", _("Cabin")),  # Cabane
    (5, "tree-house", _("Tree house")),  # Cabane dans les arbres
    (6, "chalet", _("Chalet")),  # Chalet
    (7, "castle", _("Castle")),  # Château
    (8, "manor", _("Manor")),  # Manoir
    (9, "ecolodge", _("Ecolodge")),  # Habitat écologique
    (21, "igloo", _("Igloo")),  # Igloo
    (10, "loft", _("Loft")),  # Loft
    (11, "townhouse", _("Townhouse")),  # Maison de ville
    (12, "caravan", _("Caravan")),  # Roulotte
    (13, "plot", _("Plot")),  # Terrain
    (14, "garden", _("Garden")),  # Jardin
    (15, "island", _("Island")),  # île
    (16, "villa", _("Villa")),  # Villa
    (17, "country-house", _("Country house")),  # Maison de campagne
    (18, "yurt", _("Yurt")),  # Yourte
    (19, "tipi", _("Tipi")),  # Tipi
    (20, "tent", _("Tent")),  # Tente
    (22, "cave-dwelling", _("Cave dwelling")),  # Habitat troglodyte
    (23, "village-house", _("Village house")),  # Maison de village
    (24, "bubble", _("Bubble")),  # Bulle
)

HOUSING_TYPES = getattr(settings, "KAPT_CATALOG_HOUSING_TYPES", DEFAULT_HOUSING_TYPES)

# Difficulty for LeisureActivity
DEFAULT_DIFFICULTY = (
    (0, "easy", _("Easy")),
    (1, "medium", _("Medium")),
    (2, "hard", _("Hard")),
)

DIFFICULTY = getattr(settings, "KAPT_CATALOG_DIFFICULTY", DEFAULT_DIFFICULTY)


DEFAULT_MEAL_ACTIVITY_SCHEDULE_TYPES = (
    (0, "lunch", _("Lunch")),
    (1, "dinner", _("Dinner")),
)

MEAL_ACTIVITY_SCHEDULE_TYPES = getattr(
    settings,
    "KAPT_CATALOG_MEAL_ACTIVITY_SCHEDULE_TYPES",
    DEFAULT_MEAL_ACTIVITY_SCHEDULE_TYPES,
)

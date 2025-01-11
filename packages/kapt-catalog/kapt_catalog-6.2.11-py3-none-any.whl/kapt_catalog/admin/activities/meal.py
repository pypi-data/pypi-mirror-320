# Third party
from django.contrib import admin

# Local application / specific library imports
from kapt_catalog.admin.activities.activity import ActivityChildAdmin
from kapt_catalog.forms.activities.meal import (
    InnActivityAdminForm,
    MealActivityProductsAdminForm,
    TableActivityAdminForm,
)
from kapt_catalog.models.activities.meal import MealActivityProducts


class MealActivityProductsInline(admin.TabularInline):
    model = MealActivityProducts
    extra = 0
    form = MealActivityProductsAdminForm


class MealActivityAdmin(ActivityChildAdmin):
    inlines = [MealActivityProductsInline]


class TableActivityAdmin(MealActivityAdmin):
    form = TableActivityAdminForm


class InnActivityAdmin(MealActivityAdmin):
    form = InnActivityAdminForm

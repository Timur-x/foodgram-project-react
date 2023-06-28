from django.contrib.admin import register, ModelAdmin

from .models import Ingredient


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)

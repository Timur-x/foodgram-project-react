from django.contrib.admin import ModelAdmin, TabularInline, register

from .models import Recipe, RecipeIngredients


class RecipeIngredientInline(TabularInline):
    model = RecipeIngredients


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = ('name', 'author',)
    list_filter = ('name', 'author', 'tags',)
    readonly_fields = ('in_favorites',)
    inlines = (RecipeIngredientInline, )

    def in_favorites(self, obj):
        return obj.favorites.count()
    in_favorites.short_description = 'Общее число добавлений в избранное'

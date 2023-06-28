from django.contrib.admin import ModelAdmin, TabularInline, register

from .models import Recipe


class RecipeIngredientsInLine(TabularInline):
    model = Recipe.ingredients.through
    extra = 1


class RecipeTagsInLine(TabularInline):
    model = Recipe.tags.through
    extra = 1


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = ('name', 'author',)
    list_filter = ('name', 'author', 'tags',)
    readonly_fields = ('in_favorites',)
    inlines = (RecipeIngredientsInLine, RecipeTagsInLine)

    def in_favorites(self, obj):
        return obj.favorites.count()
    in_favorites.short_description = 'Общее число добавлений в избранное'

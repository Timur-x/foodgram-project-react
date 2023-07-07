from django.contrib.admin import ModelAdmin, TabularInline, register

from .models import CountOfIngredient, Favorite, Recipe

EMPTY = '< Пусто >'


class RecipeIngredientsInLine(TabularInline):
    model = Recipe.ingredients.through
    extra = 1


class RecipeTagsInLine(TabularInline):
    model = Recipe.tags.through
    extra = 1


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = ('name', 'author')
    list_filter = ('name', 'author', 'tags',)
    # readonly_fields = ('in_favorite',)
    # inlines = (RecipeIngredientsInLine, RecipeTagsInLine)

    # def in_favorites(self, obj):
    #     return obj.favorites.count()
    # in_favorites.short_description = 'Общее число добавлений в избранное'


@register(Favorite)
class FavoriteAdmin(ModelAdmin):
    list_display = ('user', 'recipe',)
    list_filter = ('user', 'recipe',)


@register(CountOfIngredient)
class CountOfIngredientAdmin(ModelAdmin):
    list_display = (
        'id', 'ingredient', 'amount', 'get_measurement_unit',
        'get_recipes_count',
    )
    readonly_fields = ('get_measurement_unit',)
    list_filter = ('ingredient',)
    ordering = ('ingredient',)

    def get_measurement_unit(self, obj):
        try:
            return obj.ingredient.measurement_unit
        except CountOfIngredient.ingredient.RelatedObjectDoesNotExist:
            return EMPTY
    get_measurement_unit.short_description = 'Единица измерения'

    def get_recipes_count(self, obj):
        return obj.ingredient.count_in_recipes.count()
    get_recipes_count.short_description = 'Количество ссылок в рецептах'

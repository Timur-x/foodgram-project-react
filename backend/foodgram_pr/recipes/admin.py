from django.contrib.admin import ModelAdmin, register

from .models import Recipe


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = ('name', 'author',)
    list_filter = ('name', 'author', 'tags',)
    readonly_fields = ('in_favorites',)

    def in_favorites(self, obj):
        return obj.favorites.count()
    in_favorites.short_description = 'Общее число добавлений в избранное'

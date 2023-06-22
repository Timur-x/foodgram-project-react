from django_filters.rest_framework import (AllValuesMultipleFilter,
                                           BooleanFilter, FilterSet)

from .models import Recipe


class RecipeFilter(FilterSet):
    is_favorited = BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = BooleanFilter(method='get_is_in_shopping_cart')
    tags = AllValuesMultipleFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = ('author',)

    def get_is_favorited(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(in_favorite__user=self.request.user)

    def get_is_in_shopping_cart(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(in_favorite__user=self.request.user)

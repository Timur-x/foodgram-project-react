from django.db.models import IntegerField, Value
from django_filters.rest_framework import (AllValuesMultipleFilter,
                                           BooleanFilter, CharFilter,
                                           FilterSet)
from ingredients.models import Ingredient

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
        return queryset.filter(in_shopping_list__user=self.request.user)


class IngredientSearchFilter(FilterSet):
    name = CharFilter(method='search_by_name')

    class Meta:
        model = Ingredient
        fields = ('name',)

    def search_by_name(self, queryset, name, value):
        if not value:
            return queryset
        start_with_queryset = (
            queryset.filter(name__istartswith=value).annotate(
                order=Value(0, IntegerField())
            )
        )
        contain_queryset = (
            queryset.filter(name__icontains=value).exclude(
                pk__in=(ingredient.pk for ingredient in start_with_queryset)
            ).annotate(
                order=Value(1, IntegerField())
            )
        )
        return start_with_queryset.union(contain_queryset).order_by('order')

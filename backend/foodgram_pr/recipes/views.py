from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from ingredients.models import Ingredient
from rest_framework import exceptions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.pagination import CustomPageNumberPagination

from .filters import RecipeFilter
from .models import Favorite, Recipe, RecipeIngredients, ShoppingCart
from .permissions import IsAuthorOrAdminPermission
from .serializers.recipes import RecipeCreateUpdateSerializer, RecipeSerializer
from .serializers.shortrecipes import ShortRecipeSerializer

FILE_NAME = 'Cписок покупок.txt'
RECIPE_DELETED = 'Рецепта нет в избранном, либо он уже удален.'
THE_RECIPE_HAS_BEEN_REMOVED_FROM_THE_TRASH = ('Рецепта нет в списке покупок,'
                                              'либо он уже удален.')


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrAdminPermission,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPageNumberPagination

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateUpdateSerializer

        return RecipeSerializer

    @action(detail=True, methods=('post', 'delete'))
    def favorite(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if self.request.method == 'POST':
            Favorite.objects.create(user=user, recipe=recipe)
            serializer = ShortRecipeSerializer(
                recipe,
                context={'request': request}
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            if not Favorite.objects.filter(
                user=user,
                recipe=recipe
            ).exists():
                raise exceptions.ValidationError(RECIPE_DELETED)

            favorite = get_object_or_404(Favorite, user=user, recipe=recipe)
            favorite.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=True, methods=('post', 'delete'))
    def shopping_cart(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if self.request.method == 'POST':
            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = ShortRecipeSerializer(
                recipe,
                context={'request': request}
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            if not ShoppingCart.objects.filter(
                user=user,
                recipe=recipe
            ).exists():
                raise exceptions.ValidationError(
                    THE_RECIPE_HAS_BEEN_REMOVED_FROM_THE_TRASH
                )

            shopping_cart = get_object_or_404(
                ShoppingCart,
                user=user,
                recipe=recipe
            )
            shopping_cart.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        shopping_cart = ShoppingCart.objects.filter(user=self.request.user)
        recipes = [item.recipe.id for item in shopping_cart]
        buy_list = RecipeIngredients.objects.filter(
            recipe__in=recipes
        ).values(
            'ingredient'
        ).annotate(
            amount=Sum('amount')
        )

        content = 'Список покупок :\n\n'
        for item in buy_list:
            ingredient = Ingredient.objects.get(pk=item['ingredient'])
            amount = item['amount']
            content += (
                f'{ingredient.name}, {amount} '
                f'{ingredient.measurement_unit}\n'
            )

        response = HttpResponse(
            content, content_type='text/plain,charset=utf8'
        )
        response['Content-Disposition'] = f'attachment; filename={FILE_NAME}'

        return response

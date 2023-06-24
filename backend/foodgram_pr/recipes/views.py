from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
# from users.pagination import CustomPageNumberPagination
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (SAFE_METHODS, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,
                                   HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST,
                                   HTTP_405_METHOD_NOT_ALLOWED)

from .filters import RecipeFilter
from .models import (Favorite, Ingredient, Recipe, RecipeIngredients,
                     ShoppingCart)
from .serializers.recipes import RecipeCreateUpdateSerializer, RecipeSerializer
from .serializers.shortrecipes import ShortRecipeSerializer

FILE_NAME = 'Список покупок.txt'


class RecipeViewSet(viewsets.ModelViewSet):
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    queryset = Recipe.objects.all()
    http_method_names = ('get', 'post', 'put', 'patch', 'delete',)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipeCreateUpdateSerializer

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(author=user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        serializer = RecipeSerializer(
            instance=serializer.instance,
            context={'request': self.request}
        )
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=HTTP_201_CREATED, headers=headers
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        serializer = RecipeSerializer(
            instance=serializer.instance,
            context={'request': self.request},
        )
        return Response(
            serializer.data, status=HTTP_200_OK
        )

    @action(
        methods=('post', 'delete',),
        detail=True,
    )
    def favorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            favorite, created = Favorite.objects.get_or_create(
                user=user,
                recipe=recipe
                 )
            if created:
                serializer = ShortRecipeSerializer(favorite.recipe,
                                                   context={'request': request}
                                                   )
                return Response(serializer.data,
                                status=HTTP_201_CREATED
                                )
            return Response({'message': 'Рецепт уже в избранном.'},
                            status=HTTP_400_BAD_REQUEST
                            )

        if request.method == 'DELETE':
            try:
                favorite = Favorite.objects.get(user=user, recipe=recipe)
                favorite.delete()
                return Response(status=HTTP_204_NO_CONTENT)
            except Favorite.DoesNotExist:
                return Response({'message': 'Рецепт не найден в избранном.'},
                                status=HTTP_400_BAD_REQUEST)

        return Response(status=HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=True, methods=('post', 'delete'))
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            shopping_cart, created = ShoppingCart.objects.get_or_create(
                user=user,
                recipe=recipe
                 )
            if created:
                serializer = ShortRecipeSerializer(
                    recipe,
                    context={'request': request}
                     )
                return Response(serializer.data, status=HTTP_201_CREATED)
            return Response(
                    {'message': 'Рецепт уже в корзине покупок.'},
                    status=HTTP_400_BAD_REQUEST
                     )
        if request.method == 'DELETE':
            try:
                shopping_cart = ShoppingCart.objects.get(
                    user=user,
                    recipe=recipe
                     )
                shopping_cart.delete()
                return Response(status=HTTP_204_NO_CONTENT)
            except ShoppingCart.DoesNotExist:
                return Response(
                    {'message': 'Рецепт не найден в корзине покупок.'},
                    status=HTTP_400_BAD_REQUEST
                     )
        return Response(status=HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        user = self.request.user
        shopping_cart = ShoppingCart.objects.filter(user=user)
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

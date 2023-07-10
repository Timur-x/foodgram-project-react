from django.core.validators import MaxValueValidator, MinValueValidator
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from ingredients.models import Ingredient
from rest_framework import serializers
# from rest_framework.exceptions import ValidationError
from tags.models import Tag
from tags.serializers import TagSerializer
from users.serializers import CustomUserSerializer

from ..models import (Favorite, Recipe, RecipeIngredients, RecipeTags,
                      ShoppingCart)

COOKING_TIME_ERROR = (
    'Время приготовления должно составлять не менее 1 минуты',
    ' и не превышать 32 000 минут'
)
COOKING_TIME_MIN = 1
MAX_COOKING_TIME = 32000
INGREDIENT_MIN_AMOUNT = 1
INGREDIENT_MAX_AMOUNT = 32000
RECIPE_IN_FAVORITES = 'Рецепт уже в избранном.'
RECIPE_IN_THE_BASKET = 'Рецепт уже в списке покупок.'
TAGS_EMPTY_ERROR = 'Рецепт не может быть без тегов!'
INGREDIENTS_UNIQUE_ERROR = 'Ингредиенты не могут повторяться!'
INGREDIENTS_EMPTY_ERROR = 'Без ингредиентов рецепта не бывает!'
INGREDIENT_MIN_AMOUNT_ERROR = (
    'Количество ингредиента не может быть меньше 1!'
)
INGREDIENT_MAX_AMOUNT_ERROR = (
    'Количество ингредиента не может быть больше 32000!'
)


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField(method_name='get_id')
    name = serializers.SerializerMethodField(method_name='get_name')
    measurement_unit = serializers.SerializerMethodField(
        method_name='get_measurement_unit'
    )

    def get_id(self, obj):
        return obj.ingredient.id

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')


class CreateUpdateRecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        validators=(
            MinValueValidator(
                INGREDIENT_MIN_AMOUNT,
                message=INGREDIENT_MIN_AMOUNT_ERROR
            ),
            MaxValueValidator(
                INGREDIENT_MAX_AMOUNT,
                message=INGREDIENT_MAX_AMOUNT_ERROR
            ),
        )
    )

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = serializers.SerializerMethodField(
        method_name='get_ingredients'
    )
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )

    def get_ingredients(self, obj):
        ingredients = RecipeIngredients.objects.filter(recipe=obj)
        serializer = RecipeIngredientsSerializer(ingredients, many=True)

        return serializer.data

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        if not hasattr(obj, 'pk'):
            return False
        return user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        if not hasattr(obj, 'pk'):
            return False
        return user.shopping_list.filter(recipe=obj).exists()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = CreateUpdateRecipeIngredientsSerializer(many=True)
    image = Base64ImageField()
    # cooking_time = serializers.IntegerField(
    #     validators=[
    #         MinValueValidator(
    #             COOKING_TIME_MIN,
    #             message=COOKING_TIME_ERROR
    #         ),
    #         MaxValueValidator(
    #             MAX_COOKING_TIME,
    #             message=COOKING_TIME_ERROR
    #         )
    #     ]
    # )

    def validate(self, attrs):
        cooking_time = attrs.get('cooking_time')
        if cooking_time and (cooking_time < 1 or cooking_time > 32000):
            raise serializers.ValidationError(COOKING_TIME_ERROR)
        return attrs

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError(
                TAGS_EMPTY_ERROR
            )

        return value

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                INGREDIENTS_EMPTY_ERROR
            )
        return value

    def create(self, validated_data):
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        user = self.context['request'].user
        recipe = Recipe.objects.create(author=author, **validated_data)
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(RECIPE_IN_FAVORITES)
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(RECIPE_IN_THE_BASKET)
        recipe.tags.set(tags)
        self.add_ingredients(recipe, ingredients)
        return recipe

    def add_tags(self, recipe, tags):
        tag_objs = []
        for data in tags:
            if isinstance(data, dict) and 'name' in data:
                try:
                    tag = Tag.objects.get(name=data['name'])
                except Tag.DoesNotExist:
                    tag = Tag.objects.create(name=data['name'])
                tag_objs.append(tag)
        recipe_tags = [RecipeTags(recipe=recipe, tag=tag) for tag in tag_objs]
        RecipeTags.objects.bulk_create(recipe_tags)

    def add_ingredients(self, recipe, ingredients):
        ingredient_objs = []
        for data in ingredients:
            if isinstance(data, dict) and all(key in data for key in
                                              ['name', 'unit']):
                ingredient = Ingredient.objects.create(
                    name=data['name'],
                    unit=data['unit']
                )
                ingredient_objs.append(ingredient)
        RecipeIngredients.objects.bulk_create([
            RecipeIngredients(recipe=recipe, ingredient=ingredient)
            for ingredient in ingredient_objs
        ])

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        if tags is not None:
            self.add_tags(instance, tags)
            instance.tags.set(tags)

        ingredients = validated_data.pop('ingredients', None)
        if ingredients is not None:
            instance.ingredients.clear()
            for ingredient in ingredients:
                amount = ingredient['amount']
                ingredient = get_object_or_404(Ingredient, pk=ingredient['id'])
                RecipeIngredients.objects.update_or_create(
                    recipe=instance,
                    ingredient=ingredient,
                    defaults={'amount': amount}
                )
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        serializer = RecipeSerializer(
            instance,
            context={'request': self.context.get('request')}
        )

        return serializer.data

    class Meta:
        model = Recipe
        exclude = ('pub_date',)

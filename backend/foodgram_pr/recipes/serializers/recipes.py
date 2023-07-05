# from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from ingredients.models import Ingredient
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import (IntegerField, ModelSerializer,
                                        PrimaryKeyRelatedField,
                                        SerializerMethodField)
from tags.models import Tag
from tags.serializers import TagSerializer
from users.serializers import CustomUserSerializer

from ..models import (Favorite, Recipe, RecipeIngredients, RecipeTags,
                      ShoppingCart)

# User = get_user_model()

COOKING_TIME_ERROR = (
    'Время приготовления должно составлять не менее 1 минуты',
    ' и не превышать 32 000 минут'
)
COOKING_TIME_MIN = 1
MAX_COOKING_TIME = 32000
INGREDIENT_MIN_AMOUNT = 1
INGREDIENT_MAX_AMOUNT = 32000
TAGS_EMPTY_ERROR = 'Рецепт не может быть без тегов!'
INGREDIENTS_UNIQUE_ERROR = 'Ингредиенты не могут повторяться!'
INGREDIENTS_EMPTY_ERROR = 'Без ингредиентов рецепта не бывает!'
INGREDIENT_MIN_AMOUNT_ERROR = (
    'Количество ингредиента не может быть меньше 1!'
)
INGREDIENT_MAX_AMOUNT_ERROR = (
    'Количество ингредиента не может быть больше 32000!'
     )


class RecipeIngredientsSerializer(ModelSerializer):
    id = SerializerMethodField(method_name='get_id')
    name = SerializerMethodField(method_name='get_name')
    measurement_unit = SerializerMethodField(
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


class CreateUpdateRecipeIngredientsSerializer(ModelSerializer):
    id = IntegerField()
    amount = IntegerField(
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


class RecipeSerializer(ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = SerializerMethodField(
        method_name='get_ingredients'
    )
    is_favorited = SerializerMethodField(
        method_name='get_is_favorited'
    )
    is_in_shopping_cart = SerializerMethodField(
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
        if Favorite.objects.filter(user=user, recipe=obj).exists():
            return True

        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        if not hasattr(obj, 'pk'):
            return False
        if ShoppingCart.objects.filter(user=user, recipe=obj).exists():
            return True
        return False

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )


class RecipeCreateUpdateSerializer(ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = CreateUpdateRecipeIngredientsSerializer(many=True)
    image = Base64ImageField()
    cooking_time = IntegerField(
        validators=(
            MinValueValidator(
                COOKING_TIME_MIN,
                message=COOKING_TIME_ERROR
            ),
            MaxValueValidator(
                MAX_COOKING_TIME,
                message=COOKING_TIME_ERROR)
             )
         )

    def validate_tags(self, value):
        if not value:
            raise ValidationError(
                TAGS_EMPTY_ERROR
            )

        return value

    def validate_ingredients(self, value):
        if not value:
            raise ValidationError(
                INGREDIENTS_EMPTY_ERROR
            )
        return value

    def create(self, validated_data):
        tags_list = validated_data.pop('tags')
        ingredient_list = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for item in ingredient_list:
            ingredient = get_object_or_404(Ingredient, id=item.get('id'))
            RecipeIngredients.objects.create(
                ingredient=ingredient,
                recipe=recipe,
                amount=item.get('amount')
            )
        for item in tags_list:
            RecipeTags.objects.create(
                tag=item,
                recipe=recipe
            )
        return recipe

    def add_tags(self, recipe, tags):
        tag_objs = [Tag(**data) for data in tags]
        Tag.objects.bulk_create(tag_objs)
        recipe_tags = [RecipeTags(recipe=recipe, tag=tag) for tag in tag_objs]
        RecipeTags.objects.bulk_create(recipe_tags)

    def add_ingredients(self, recipe, ingredients):
        ingredient_objs = [Ingredient(**data) for data in ingredients]
        Ingredient.objects.bulk_create(ingredient_objs)
        recipe_ingredients = [RecipeIngredients(
            recipe=recipe,
            ingredient=ingredient
             ) for ingredient in ingredient_objs]
        RecipeIngredients.objects.bulk_create(recipe_ingredients)

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        if tags is not None:
            self.add_tags(instance, tags)
            instance.tags.set(tags)

        ingredients = validated_data.pop('ingredients', None)
        if ingredients is not None:
            self.add_ingredients(instance, ingredients)
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

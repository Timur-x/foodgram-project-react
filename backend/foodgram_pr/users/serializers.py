# from django.contrib.auth.hashers import make_password
# from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import Recipe
from recipes.serializers.recipes import RecipeSerializer
# from rest_framework.exceptions import ValidationError
from rest_framework.serializers import SerializerMethodField

# from rest_framework.validators import UniqueValidator
from .models import Subscription, User


class CustomUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField('is_subscribed_user')
    recipes = SerializerMethodField()

    def is_subscribed_user(self, obj):
        user = self.context['request'].user
        author = obj
        if user == author:
            return False
        if Subscription.objects.filter(
                user=user,
                author=author
                 ).exists():
            return True
        return False

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj)
        serializer = RecipeSerializer(recipes, many=True)
        return serializer.data

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes')


class SubscriptionSerializer(CustomUserSerializer):
    recipes = SerializerMethodField(method_name='get_recipes')
    recipes_count = SerializerMethodField(
        method_name='get_recipes_count'
    )

    def get_srs(self):
        from recipes.serializers.shortrecipes import ShortRecipeSerializer

        return ShortRecipeSerializer

    def get_recipes(self, obj):
        author_recipes = Recipe.objects.filter(author=obj)

        if 'recipes_limit' in self.context.get('request').GET:
            recipes_limit = self.context.get('request').GET['recipes_limit']
            author_recipes = author_recipes[:int(recipes_limit)]

        if author_recipes:
            serializer = self.get_srs()(
                author_recipes,
                context={'request': self.context.get('request')},
                many=True
            )
            return serializer.data

        return []

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password')

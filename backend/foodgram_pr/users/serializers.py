from django.contrib.auth.hashers import make_password
# from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import Recipe
# from rest_framework.exceptions import ValidationError
from rest_framework.serializers import SerializerMethodField

# from rest_framework.validators import UniqueValidator
from .models import User


class CustomUserSerializer(UserSerializer):
    '''Сериализация подписки.'''
    is_subscribed = SerializerMethodField(
        method_name='get_is_subscribed'
    )

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'password',
            'is_subscribed',
        )
        extra_kwargs = {
            'password': {'write_only': True, 'required': True},
        }

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and obj.subscribed_by.filter(user=user).exists()
             )

    def create(self, validated_data):
        validated_data['password'] = (
            make_password(validated_data.pop('password'))
        )
        return super().create(validated_data)


class CustomUserCreateSerializer(UserCreateSerializer):
    '''Сериализатор для создания User.'''
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password')


class SubscriptionSerializer(CustomUserSerializer):
    '''Cериализатор для модели User.'''
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

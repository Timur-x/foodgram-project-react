from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.serializers.recipes import RecipeSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

# from rest_framework.validators import UniqueValidator
from .models import Subscription, User


class CustomUserSerializer(UserSerializer):
    '''Сериализация User.'''
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        author = get_object_or_404(User, pk=obj.pk)
        # if user == author:
        #     raise ValidationError('Подписка на самого себя запрещена.')
        if user.is_anonymous:
            return False
        subscription = Subscription.objects.filter(user=user,
                                                   author=author).first()
        return subscription is not None

    def create(self, validated_data):
        validated_data['password'] = (
            make_password(validated_data.pop('password'))
        )
        return super().create(validated_data)


class CustomUserCreateSerializer(UserCreateSerializer):
    '''Сериализатор для регистрации пользователей.'''
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
         )


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, obj):
        limit = self.context['request'].query_params.get(
            'recipes_limit', settings.COUNT_RECIPES_DEFAULT
        )
        recipes = obj.recipes.all()[:int(limit)]
        return RecipeSerializer(recipes, many=True).data

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return bool(obj.subscribers.filter(user=user))

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания подписки на автора."""

    class Meta:
        model = Subscription
        fields = '__all__'

        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на этого пользователя.'
            )
        ]

    def validate(self, data):
        if data['user'] == data['author']:
            raise ValidationError(
                'Вы не можете подписаться на самого себя.')
        return data

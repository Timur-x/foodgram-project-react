from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.serializers.shortrecipes import ShortRecipeSerializer
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import SerializerMethodField

# from rest_framework.validators import UniqueValidator
from .models import Subscription, User


class CustomUserSerializer(UserSerializer):
    '''Сериализация User.'''
    is_subscribed = SerializerMethodField(
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
        # author_id = obj.pk
        # author = get_object_or_404(User, pk=author_id)
        # if user == author:
        #     raise ValidationError(
        #             'Подписка на самого себя запрещена.'
        #         )
        # if Subscription.objects.filter(
        #         user=user,
        #         author=author
        #          ).exists():
        #     raise ValidationError('Подписка уже оформлена.')

        if user.is_anonymous:
            return False

        return Subscription.objects.filter(user=user, author=obj).exists()

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


class SubscriptionSerializer(CustomUserSerializer):
    '''Cериализатор для подписки.'''
    recipes = ShortRecipeSerializer(many=True)
    recipes_count = SerializerMethodField()

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

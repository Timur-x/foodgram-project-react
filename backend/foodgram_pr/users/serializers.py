from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from recipes.models import Recipe
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Subscription, User


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        author = get_object_or_404(User, pk=id)
        if user == author:
            raise ValidationError(
                    'Подписка на самого себя запрещена.'
                )
        if Subscription.objects.filter(
                user=user,
                author=author
                 ).exists():
            raise ValidationError('Подписка уже оформлена.')

        if user.is_anonymous:
            return False

        return Subscription.objects.filter(user=user, author=obj).exists()

    def create(self, validated_data):
        validated_data['password'] = (
            make_password(validated_data.pop('password'))
        )
        return super().create(validated_data)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')


class SubscriptionSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField(method_name='get_recipes')
    recipes_count = serializers.SerializerMethodField(
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


class CustomUserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password')

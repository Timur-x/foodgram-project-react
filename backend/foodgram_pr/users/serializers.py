from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
# from recipes.models import Recipe
from recipes.serializers.shortrecipes import ShortRecipeSerializer
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import SerializerMethodField

# from rest_framework.validators import UniqueValidator
from .models import Subscription, User


class CustomUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField(
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
    recipes = ShortRecipeSerializer(many=True)
    recipes_count = SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count',)

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password')

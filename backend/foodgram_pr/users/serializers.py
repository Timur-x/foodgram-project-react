from django.contrib.auth.hashers import make_password
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import Recipe
from rest_framework.serializers import SerializerMethodField

from .models import User


class CustomUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField('is_subscribed_user')

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password',
            'is_subscribed',
        )
        extra_kwargs = {
            'password': {'write_only': True, 'required': True},
        }

    def is_subscribed_user(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and obj.subscribing.filter(user=user).exists()
        )

    def create(self, validated_data):
        validated_data['password'] = (
            make_password(validated_data.pop('password'))
        )
        return super().create(validated_data)


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
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'password')

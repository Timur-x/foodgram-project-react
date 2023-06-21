from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AnonymousUser
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.serializers.shortrecipes import ShortRecipeSerializer
from rest_framework.serializers import EmailField, SerializerMethodField
from rest_framework.validators import UniqueValidator

from .models import User


class CustomUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField('is_subscribed_user')
    email = EmailField(label='Адрес эл. почты(email)',
                       max_length=254,
                       validators=[UniqueValidator(queryset=User.objects.all())
                                   ])

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
        if user.is_anonymous:
            return False
        return obj.subscribing.filter(user=user).exists()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if isinstance(instance, AnonymousUser):
            data.pop('email', None)
            data.pop('is_subscribed', None)
        return data

    def create(self, validated_data):
        validated_data['password'] = (
            make_password(validated_data.pop('password'))
        )
        return super().create(validated_data)


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
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


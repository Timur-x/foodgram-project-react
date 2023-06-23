from django.contrib.auth.hashers import make_password
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.serializers.shortrecipes import ShortRecipeSerializer
from rest_framework.serializers import EmailField, SerializerMethodField
from rest_framework.validators import UniqueValidator

from .models import User


class CustomUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField('is_subscribed_user')
    # email = EmailField(label='Адрес эл. почты(email)',
    #                    max_length=254,
    #                    validators=[UniqueValidator(queryset=User.objects.all())
    #                                ])

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
        return bool(obj.subscribers.filter(user=user))

    def create(self, validated_data):
        validated_data['password'] = (
            make_password(validated_data.pop('password'))
        )
        return super().create(validated_data)


class SubscriptionSerializer(CustomUserSerializer):
    recipes = ShortRecipeSerializer(many=True)
    recipes_count = SerializerMethodField()

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

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password')

# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import serializers
# from recipes.models import ShoppingCart
# from rest_framework import exceptions
# from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
# from rest_framework.permissions import (IsAuthenticated,
#                                         IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from .models import User
from .pagination import CustomPageNumberPagination
from .serializers import SubscriptionCreateSerializer, SubscriptionSerializer

# class TokenCreateWithCheckBlockStatusView(TokenCreateView):
#     def _action(self, serializer):
#         if serializer.user.is_blocked:
#             return Response(
#                 {'errors': 'аккаунт заблокирован!'},
#                 status=HTTP_400_BAD_REQUEST,
#             )
#         return super()._action(serializer)


class UserSubscribeViewSet(UserViewSet):
    pagination_class = CustomPageNumberPagination

    @action(
        methods=['get'], detail=False,
        serializer_class=SubscriptionSerializer
    )
    def subscriptions(self, request):
        user = self.request.user

        def queryset():
            return User.objects.filter(subscribers__user=user)

        self.get_queryset = queryset
        return self.list(request)

    @action(
        methods=['post', 'delete'], detail=True,
        serializer_class=SubscriptionSerializer
    )
    def subscribe(self, request, id):
        user = self.request.user
        author = self.get_object()
        if request.method == 'DELETE':
            instance = user.following.filter(author=author)
            if not instance:
                raise serializers.ValidationError(
                    {
                        'errors': [
                            'Вы не подписаны на этого автора.'
                        ]
                    }
                )
            instance.delete()
            return Response(status=HTTP_204_NO_CONTENT)
        data = {
            'user': user.id,
            'author': id
        }
        subscription = SubscriptionCreateSerializer(data=data)
        subscription.is_valid(raise_exception=True)
        subscription.save()
        serializer = self.get_serializer(author)
        return Response(serializer.data, status=HTTP_201_CREATED)

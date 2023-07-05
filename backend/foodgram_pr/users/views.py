# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
# from recipes.models import ShoppingCart
# from rest_framework import exceptions
# from rest_framework.authtoken.models import Token
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from .models import User
from .pagination import CustomPageNumberPagination
from .serializers import CustomUserSerializer, SubscriptionSerializer

# class TokenCreateWithCheckBlockStatusView(TokenCreateView):
#     def _action(self, serializer):
#         if serializer.user.is_blocked:
#             return Response(
#                 {'errors': 'аккаунт заблокирован!'},
#                 status=HTTP_400_BAD_REQUEST,
#             )
#         return super()._action(serializer)


class UserSubscribeViewSet(UserViewSet):
    '''Подписка на пользователя и удалаление подписки.'''
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = CustomPageNumberPagination

    @action(
        detail=False,
        methods=('get',),
        serializer_class=SubscriptionSerializer,
        permission_classes=(IsAuthenticated, )
    )
    def subscriptions(self, request):
        # user = self.request.user
        # user_subscriptions = user.subscribers.all()
        # authors = [item.author.id for item in user_subscriptions]
        # queryset = User.objects.filter(pk__in=authors)
        queryset = User.objects.filter(subscribers__user=self.request.user)
        paginated_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(paginated_queryset, many=True)

        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=('post', 'delete'),
        serializer_class=SubscriptionSerializer
    )
    def subscribe(self, request, id=None):
        user = self.request.user
        author = self.get_object()
        if request.method == 'DELETE':
            instance = user.subscribers.filter(author=author)
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
        subscription = SubscriptionSerializer(data=data)
        subscription.is_valid(raise_exception=True)
        subscription.save()
        serializer = self.get_serializer(author)
        return Response(serializer.data, status=HTTP_201_CREATED)

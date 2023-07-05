# from django.db.models.signals import post_save
from django.db import IntegrityError
from django.http import Http404
# from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
# from recipes.models import ShoppingCart
# from rest_framework import exceptions
# from rest_framework.authtoken.models import Token
# from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                                   HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND)

from .models import Subscription, User
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
        methods=('get', 'delete',),
        detail=True,
        permission_classes=(IsAuthenticated,))
    def subscribe(self, request, user_id=None):
        try:
            author = get_object_or_404(User, pk=user_id)
        except Http404:
            return Response(
                {'detail': 'USER_NOT_FOUND'},
                status=HTTP_404_NOT_FOUND,
            )
        if request.method == 'GET':
            return self.create_subscribe(request, author)
        return self.delete_subscribe(request, author)

    def create_subscribe(self, request, author):
        if request.user == author:
            return Response(
                {'ERRORS_KEY': 'SUBSCRIBE_CANNOT_CREATE_TO_YOURSELF'},
                status=HTTP_400_BAD_REQUEST,
            )
        try:
            subscribe = Subscription.objects.create(
                user=request.user,
                author=author,
            )
        except IntegrityError:
            return Response(
                {'ERRORS_KEY': 'SUBSCRIBE_CANNOT_CREATE_TWICE'},
                status=HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_subscribtion_serializer(subscribe.author)
        return Response(serializer.data, status=HTTP_201_CREATED)

    def delete_subscribe(self, request, author):
        try:
            Subscription.objects.get(user=request.user, author=author).delete()
        except Subscription.DoesNotExist:
            return Response(
                {'ERRORS_KEY': 'SUBSCRIBE_CANNOT_DELETE'},
                status=HTTP_400_BAD_REQUEST,
            )
        return Response(
            status=HTTP_204_NO_CONTENT
        )

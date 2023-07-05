from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import exceptions
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                                   HTTP_405_METHOD_NOT_ALLOWED)

from .models import Subscription, User
from .pagination import CustomPageNumberPagination
from .serializers import CustomUserSerializer, SubscriptionSerializer

YOU_CANNOT_SUBSCRIBE_TO_YOURSELF = 'Подписатся на самого себя нельзя.'
SUBSCRIPTION_IS_ISSUED = 'Подписка уже оформлена.'
NO_SIGNATURE = 'Вы не подписаны на этого автора.'


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
        author = get_object_or_404(User, pk=id)

        if self.request.method == 'POST':
            if user == author:
                raise exceptions.ValidationError(
                    YOU_CANNOT_SUBSCRIBE_TO_YOURSELF
                )
            if Subscription.objects.filter(
                user=user,
                author=author
            ).exists():
                raise exceptions.ValidationError(SUBSCRIPTION_IS_ISSUED)

            Subscription.objects.create(user=user, author=author)
            serializer = self.get_serializer(author)

            return Response(serializer.data, status=HTTP_201_CREATED)

        if request.method == 'DELETE':
            instance = user.subscribes.filter(author=author)
            if not instance:
                raise exceptions.ValidationError(NO_SIGNATURE)
            instance.delete()
            return Response(status=HTTP_204_NO_CONTENT)

        return Response(status=HTTP_405_METHOD_NOT_ALLOWED)

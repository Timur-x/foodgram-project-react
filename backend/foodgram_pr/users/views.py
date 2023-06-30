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


class UserSubscribeViewSet(UserViewSet):
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

        if request.method == 'POST':
            if user == author:
                raise exceptions.ValidationError(
                    'Подписатся на самого себя нельзя.'
                )
            if Subscription.objects.filter(
                user=user,
                author=author
            ).exists():
                raise exceptions.ValidationError('Подписка уже оформлена.')

            Subscription.objects.create(user=user, author=author)

            return Response(status=HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not user.subscribers.filter(author=author).exists():
                raise exceptions.ValidationError(
                    'Подписка уже удалена.'
                )

            subscription = get_object_or_404(
                Subscription,
                user=user,
                author=author
            )
            subscription.delete()

            return Response(status=HTTP_204_NO_CONTENT)

        return Response(status=HTTP_405_METHOD_NOT_ALLOWED)

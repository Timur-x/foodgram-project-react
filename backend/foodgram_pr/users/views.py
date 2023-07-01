# from django.db.models.signals import post_save
# from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
# from recipes.models import ShoppingCart
from rest_framework import exceptions
# from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                                   HTTP_405_METHOD_NOT_ALLOWED)

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
                    'Подписатся на самого себя нельзя.'
                )
            if Subscription.objects.filter(
                user=user,
                author=author
            ).exists():
                raise exceptions.ValidationError('Подписка уже оформлена.')

            Subscription.objects.create(user=user, author=author)
            serializer = self.get_serializer(author)

            return Response(serializer.data, status=HTTP_201_CREATED)

        if self.request.method == 'DELETE':
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

from django.db import IntegrityError
from django.http import Http404
from django.shortcuts import get_object_or_404
from djoser.views import TokenCreateView, UserViewSet
# from rest_framework import exceptions
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,
                                   HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST,
                                   HTTP_404_NOT_FOUND)

from .models import Subscription, User
from .pagination import CustomPageNumberPagination
from .serializers import SubscriptionSerializer

# from recipes.permissions import IsAuthorOrAdminOrReadOnly


class TokenCreateWithCheckBlockStatusView(TokenCreateView):
    def _action(self, serializer):
        if not serializer.user.is_blocked():
            return Response(
                {'errors': 'аккаунт временно заблокирован!'},
                status=HTTP_400_BAD_REQUEST,
             )
        return super()._action(serializer)


class UserSubscribeViewSet(UserViewSet):
    lookup_url_kwarg = 'user_id'
    pagination_class = CustomPageNumberPagination

    def get_subscribtion_serializer(self, *args, **kwargs):
        kwargs.setdefault('context', self.get_serializer_context())
        return SubscriptionSerializer(*args, **kwargs)

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        self.get_serializer
        queryset = User.objects.filter(subscribers__user=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_subscribtion_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_subscribtion_serializer(queryset, many=True)
        return Response(serializer.data, status=HTTP_200_OK)

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

    @action(
        methods=('get', 'delete',),
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
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

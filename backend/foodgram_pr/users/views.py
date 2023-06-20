from django.shortcuts import get_object_or_404
from djoser.views import TokenCreateView, UserViewSet
from rest_framework import exceptions
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                                   HTTP_400_BAD_REQUEST,
                                   HTTP_405_METHOD_NOT_ALLOWED)

from .models import Subscription, User
from .serializers import SubscriptionSerializer
from .views import CustomUserSerializer


class PageNumberPagination(PageNumberPagination):
    page_size_query_param = 'page_size'
    max_page_size = 10


class TokenCreateWithCheckBlockStatusView(TokenCreateView):
    def _action(self, serializer):
        if serializer.user.is_blocked:
            return Response(
                {'errors': 'аккаунт заблокирован!'},
                status=HTTP_400_BAD_REQUEST,
            )
        return super()._action(serializer)


class UserSubscribeViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = PageNumberPagination

    @action(
        detail=False,
        methods=('get',),
        serializer_class=SubscriptionSerializer,
        permission_classes=(IsAuthenticated, )
    )
    def subscriptions(self, request):
        user = self.request.user

        def queryset():
            return User.objects.filter(subscriber__user=user)
        paginated_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(paginated_queryset, many=True)

        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=('post', 'delete'),
        serializer_class=SubscriptionSerializer
    )
    def subscribe(self, request, user_id=None):
        user = self.request.user
        author = get_object_or_404(User, pk=user_id)

        if self.request.method == 'POST':
            Subscription.objects.create(user=user, author=author)
            serializer = self.get_serializer(author)

            return Response(serializer.data, status=HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            if not user.subscribers.filter(author=author).exists():
                raise exceptions.ValidationError(
                    'Подписка не была оформлена, либо уже удалена.'
                )

            subscription = get_object_or_404(
                Subscription,
                user=user,
                author=author
            )
            subscription.delete()

            return Response(status=HTTP_204_NO_CONTENT)

        return Response(status=HTTP_405_METHOD_NOT_ALLOWED)

# from django.db.models.signals import post_save
# from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
# from recipes.models import ShoppingCart
from rest_framework import exceptions
# from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                                   HTTP_405_METHOD_NOT_ALLOWED)

from .models import Subscription, User
from .serializers import CustomUserSerializer, SubscriptionSerializer


class PageNumberPagination(PageNumberPagination):
    page_size_query_param = 'page_size'
    max_page_size = 10


# class TokenCreateWithCheckBlockStatusView(TokenCreateView):
#     def _action(self, serializer):
#         if serializer.user.is_blocked:
#             return Response(
#                 {'errors': 'аккаунт заблокирован!'},
#                 status=HTTP_400_BAD_REQUEST,
#             )
#         return super()._action(serializer)


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


# @receiver(post_save, sender=User)
# def create_shopping_cart(sender, instance, created, **kwargs):
#     if created:
#         ShoppingCart.objects.create(user=instance)


# @receiver(post_save, sender=User)
# def destroy_token(sender, instance, created, **kwargs):
#     if created or not instance.is_blocked:
#         return
#     token = Token.objects.filter(user=instance)
#     if token.exists():
#         token.first().delete()

# class UserMeViewSet(viewsets.ModelViewSet):
#     serializer_class = CustomUserSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return self.request.user

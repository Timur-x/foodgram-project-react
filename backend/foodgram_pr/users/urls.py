from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserSubscribeViewSet, UserViewSet

router = DefaultRouter()
router.register(r'users', UserSubscribeViewSet, basename='users')

app_name = 'users'

user_list = UserViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
user_detail = UserViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})
urlpatterns = [
    path('users/', user_list, name='user-list'),
    path('users/<int:pk>/', user_detail, name='user-detail'),
    path('users/<int:pk>/subscriptions/', UserViewSet.as_view(
        {'get': 'subscriptions'}),
         name='user-subscriptions'),
    path('users/<int:pk>/subscribe/', UserViewSet.as_view(
        {'post': 'subscribe'}),
         name='user-subscribe'),
    path('users/<int:pk>/unsubscribe/', UserViewSet.as_view(
        {'delete': 'subscribe'}),
         name='user-unsubscribe'),
    path('', include(router.urls)),
]

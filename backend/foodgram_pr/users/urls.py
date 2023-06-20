from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserSubscribeViewSet

router_v1 = DefaultRouter()
router_v1.register(r'users', UserSubscribeViewSet, basename='users')

app_name = 'users'


urlpatterns = [
    path('api/users/subscribe/', UserSubscribeViewSet.as_view(
        {'post': 'subscribe'}), name='user-subscribe'),
    path('api/users/subscriptions/', UserSubscribeViewSet.as_view(
        {'get': 'subscriptions'}), name='user-subscriptions'),
    path('', include(router_v1.urls)),
]

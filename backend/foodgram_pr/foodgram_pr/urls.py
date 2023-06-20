from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from djoser.views import TokenDestroyView
from ingredients.views import IngredientViewSet
from recipes.views import RecipeViewSet
from rest_framework.routers import DefaultRouter
from tags.views import TagViewSet
from users.views import (TokenCreateWithCheckBlockStatusView, UserMeViewSet,
                         UserSubscribeViewSet)

router_v1 = DefaultRouter()
router_v1.register('tags', TagViewSet)
router_v1.register('users', UserSubscribeViewSet, basename='users')
router_v1.register('users/me', UserMeViewSet, basename='user-me')
router_v1.register('ingredients', IngredientViewSet)
router_v1.register('recipes', RecipeViewSet)


authorization = [
    path(
        'token/login/',
        TokenCreateWithCheckBlockStatusView.as_view(), name='login'),
    path('token/logout/', TokenDestroyView.as_view(), name='logout')
     ]
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router_v1.urls)),
    path('api/auth/', include(authorization)),
    # path('api/users/me/', include(router_v1.urls)),
     ]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )

from rest_framework.viewsets import ReadOnlyModelViewSet
from django_filters.rest_framework.backends import DjangoFilterBackend

from .models import Ingredient
from .serializers import IngredientSerializer


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    search_fields = ('^name',)

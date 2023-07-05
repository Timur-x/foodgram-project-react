from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework.viewsets import ReadOnlyModelViewSet

from .filters import IngredientSearchFilter
from .models import Ingredient
from .serializers import IngredientSerializer


class IngredientViewSet(ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientSearchFilter
    queryset = Ingredient.objects.all()
    http_method_names = ('get',)

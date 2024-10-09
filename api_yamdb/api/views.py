from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ModelViewSet

from reviews.models import Category, Genre, Title

from .filters import TitleFilter
from .mixins import BasicActionsViewSet
from .serializers import (CategorySerializer,
                          GenreSerializer,
                          TitleСhangeSerializer,
                          TitleReadSerializer)


class TitlesViewSet(ModelViewSet):
    """Получить список всех объектов."""
    queryset = Title.objects.all()
    serializer_class = TitleReadSerializer
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method in ('PATCH', 'POST'):
            return TitleСhangeSerializer
        return TitleReadSerializer


class CategoryViewSet(BasicActionsViewSet):
    """Получить список всех категорий."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (SearchFilter, )
    search_fields = ('name', )
    lookup_field = 'slug'


class GenreViewSet(BasicActionsViewSet):
    """Получить список всех жанров."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('name', )
    lookup_field = 'slug'

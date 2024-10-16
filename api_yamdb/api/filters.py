import django_filters as filters

from reviews.models import Title


class TitleFilter(filters.FilterSet):
    """
    Фильтр для модели Title.

    Позволяет выполнять поиск произведений по следующим параметрам:
    - category: точное совпадение по слагу категории.
    - genre: точное совпадение по слагу жанра.
    - name: частичное совпадение по названию произведения.
    - year: точное совпадение по году выпуска.
    """

    category = filters.CharFilter(
        field_name='category__slug',
        lookup_expr='exact',
        help_text='Фильтрация по слагу категории'
    )
    genre = filters.CharFilter(
        field_name='genre__slug',
        lookup_expr='exact',
        help_text='Фильтрация по слагу жанра'
    )
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        help_text='Частичная фильтрация по названию произведения'
    )

    class Meta:
        model = Title
        fields = ['category', 'genre', 'name', 'year']

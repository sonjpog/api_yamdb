import django_filters as filters
from reviews.models import Title


class TitleFilter(filters.FilterSet):
    """
    Фильтр для модели Title, позволяющий выполнять поиск произведений
    по следующим параметрам:
    - category: точное совпадение по слагу категории
    - genre: точное совпадение по слагу жанра
    - name: частичное совпадение по названию произведения
    - year: точное совпадение по году выпуска
    - year__gt: произведения, выпущенные после указанного года
    - year__lt: произведения, выпущенные до указанного года
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
    year = filters.NumberFilter(
        field_name='year',
        lookup_expr='exact',
        help_text='Точное совпадение по году выпуска'
    )
    year__gt = filters.NumberFilter(
        field_name='year',
        lookup_expr='gt',
        help_text='Фильтрация по годам больше указанного'
    )
    year__lt = filters.NumberFilter(
        field_name='year',
        lookup_expr='lt',
        help_text='Фильтрация по годам меньше указанного'
    )

    class Meta:
        model = Title
        fields = ['category', 'genre', 'name', 'year']

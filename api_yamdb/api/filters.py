"""Фильтры используемые в модуле."""

from django_filters import rest_framework as filters

from reviews.models import Title


class TitleFilter(filters.FilterSet):
    """Фильтр поиска названия по нескольким полям."""

    category = filters.CharFilter(
        field_name='category__slug',
    )
    genre = filters.CharFilter(
        field_name='genre__slug',
    )
    name = filters.CharFilter(
        field_name='name',
    )

    class Meta:
        """Class Meta."""

        model = Title
        fields = ('category', 'genre', 'name', 'year')

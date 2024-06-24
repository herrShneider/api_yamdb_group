"""Сериалайзеры."""

from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework import serializers

from config import (
    MIN_RATING, MAX_RATING,
    USERNAME_LENGTH, EMAIL_FIELD_LENGTH,
    CONF_CODE_LENGTH
)
from reviews.models import Category, Genre, Title, Review, Comment, User
from reviews.validators import (
    validate_not_me,
    validate_username_via_regex)


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор категорий."""

    class Meta:
        """Class Meta."""

        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор жанров."""

    class Meta:
        """Class Meta."""

        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор произведений."""

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        """Class Meta."""

        model = Title
        fields = (
            'id', 'category', 'genre', 'name',
            'year', 'rating', 'description'
        )
        read_only_fields = (
            'category', 'genre', 'name',
            'year', 'rating', 'description'
        )


class TitleCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор создания и обновления произведений."""

    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug',
        required=True
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True,
        required=True
    )

    class Meta:
        """Class Meta."""

        model = Title
        fields = ('id', 'name', 'year', 'genre', 'category', 'description')


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор отзывов."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )

    score = serializers.IntegerField(
        validators=[
            MinValueValidator(MIN_RATING),
            MaxValueValidator(MAX_RATING)
        ]
    )

    class Meta:
        """Class Meta."""

        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        """Функция проверки данных."""
        if self.context['request'].method != 'POST':
            return data
        author = self.context.get('request').user
        title_id = self.context.get('view').kwargs.get('title_id')
        if Review.objects.filter(author=author, title__id=title_id).exists():
            raise serializers.ValidationError(
                'Вы уже оставили отзыв на данное произведение'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментариев."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        """Class Meta."""

        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class UserSerializer(serializers.ModelSerializer):
    """Базовая модель сериалайзера для модели User."""

    class Meta:
        """Meta-класс."""

        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role',
        )


class UserUpdateSerializer(UserSerializer):
    """Для PATCH запроса к api/v1/users/me/."""

    class Meta(UserSerializer.Meta):
        """Отключает запись в поле role."""

        read_only_fields = ('role',)


class SignUPSerializer(serializers.Serializer):
    """Сериализация регистрации и создания нового пользователя."""

    username = serializers.CharField(
        max_length=USERNAME_LENGTH,
        required=True,
        validators=(validate_not_me, validate_username_via_regex)
    )
    email = serializers.EmailField(
        max_length=EMAIL_FIELD_LENGTH,
        required=True
    )


class TokenSerializer(serializers.Serializer):
    """Сериализация проверки confirmation_code и отправки token."""

    username = serializers.CharField(
        max_length=USERNAME_LENGTH,
        required=True,
        validators=(validate_not_me, validate_username_via_regex)
    )
    confirmation_code = serializers.CharField(
        max_length=CONF_CODE_LENGTH,
        required=True
    )

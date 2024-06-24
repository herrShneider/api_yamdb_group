"""Модели."""

from django.contrib.auth.models import AbstractUser
from django.core.validators import (MinValueValidator,
                                    MaxValueValidator)
from django.db import models

from config import (
    MIN_RATING, MAX_RATING,
    CONF_CODE_LENGTH, EMAIL_FIELD_LENGTH, USERNAME_LENGTH
)
from reviews.validators import (
    validate_not_me,
    validate_username_via_regex,
    validate_year
)


NAME_MAX_LENGTH = 256
SLUG_MAX_LENGTH = 50
TEXT_LIMIT = 20


class User(AbstractUser):
    """Модель кастомного юзера."""

    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    CHOICES = [
        (ADMIN, 'Администратор'),
        (MODERATOR, 'Модератор'),
        (USER, 'Пользователь'),
    ]

    username = models.CharField(
        max_length=USERNAME_LENGTH,
        unique=True,
        validators=(validate_not_me, validate_username_via_regex)
    )
    email = models.EmailField(
        max_length=EMAIL_FIELD_LENGTH,
        unique=True
    )
    bio = models.TextField(
        'Биография',
        blank=True
    )
    role = models.CharField(
        'Пользовательская роль',
        max_length=max(len(role) for role in [ADMIN, MODERATOR, USER]),
        choices=CHOICES,
        default=USER,
        blank=True,
    )
    confirmation_code = models.CharField(
        max_length=CONF_CODE_LENGTH,
        blank=True,
        null=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:

        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        """Возвращает email в качестве главного поля пользователя."""
        return self.email

    @property
    def is_admin(self):
        """Клиент администратор."""
        return self.role == self.ADMIN or self.is_staff

    @property
    def is_moderator(self):
        """Клиент модератор."""
        return self.role == self.MODERATOR


class NameSlugModel(models.Model):
    """Базовая модель."""

    name = models.CharField(
        verbose_name='Название',
        max_length=NAME_MAX_LENGTH,
    )
    slug = models.SlugField(
        verbose_name='slug',
        max_length=50,
        unique=True,
    )

    class Meta:

        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name[:TEXT_LIMIT]


class Genre(NameSlugModel):
    """Модель жанра."""

    class Meta(NameSlugModel.Meta):

        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Category(NameSlugModel):
    """Модель категории."""

    class Meta(NameSlugModel.Meta):

        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Title(models.Model):
    """Модель произведения."""

    name = models.CharField(
        verbose_name='Название',
        max_length=NAME_MAX_LENGTH,
    )
    year = models.SmallIntegerField(
        verbose_name='Год',
        validators=[
            validate_year
        ]
    )
    description = models.TextField(
        verbose_name='Описание',
        blank=True,
        null=True
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр',
        related_name='titles'
    )
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='titles'
    )

    class Meta:

        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('year', 'name')

    def __str__(self):
        return self.name


class AuthorTextPubDateModel(models.Model):
    """Базовая модель для комментариев и отзывов."""

    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )
    text = models.TextField(
        verbose_name='Текст',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    class Meta:

        abstract = True
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:TEXT_LIMIT]


class Review(AuthorTextPubDateModel):
    """Модель отзыва."""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    score = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                MIN_RATING,
                f'Оценка не может быть ниже {MIN_RATING}.'
            ),
            MaxValueValidator(
                MAX_RATING,
                f'Оценка не может быть выше {MAX_RATING}.'
            )
        ],
        verbose_name='Оценка',
    )

    class Meta(AuthorTextPubDateModel.Meta):

        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author',),
                name='unique_review'
            )
        ]


class Comment(AuthorTextPubDateModel):
    """Модель комментария."""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
    )

    class Meta(AuthorTextPubDateModel.Meta):

        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

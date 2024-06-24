"""Views."""

import random

from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.db.models import Avg
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView

from api.filters import TitleFilter
from api.serializers import (
    CategorySerializer, CommentSerializer,
    GenreSerializer, ReviewSerializer,
    TitleCreateUpdateSerializer, TitleSerializer,
)
from config import (
    CONF_CODE_LENGTH, CONF_CODE_PATTERN,
    SERVER_EMAIL, URL_PROFILE_PREF,
    NOT_APPLICABLE_CONF_CODE
)
from reviews.models import Category, Genre, Review, Title, User
from . import permissions
from .serializers import (
    SignUPSerializer,
    TokenSerializer,
    UserSerializer,
    UserUpdateSerializer
)

HTTP_METHODS = ('get', 'post', 'patch', 'delete')
CONFIRMATION_ERROR = (
    'confirmation_code: Отсутствует обязательное поле или оно некорректно.'
)


class CategoryGenreMixin(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """Базовый класс."""

    permission_classes = (permissions.IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    ordering = ('id',)


class CategoriesViewSet(CategoryGenreMixin):
    """Класс категории."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenresViewSet(CategoryGenreMixin):
    """Класс жанры."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitlesViewSet(viewsets.ModelViewSet):
    """Класс произведения."""

    queryset = Title.objects.all().annotate(
        rating=Avg('reviews__score')
    ).order_by('year', 'name')
    serializer_class = TitleSerializer
    permission_classes = (permissions.IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    http_method_names = HTTP_METHODS
    filterset_class = TitleFilter

    def get_serializer_class(self):
        """Функция определения сериализатора."""
        if self.request.method == 'GET':
            return TitleSerializer
        return TitleCreateUpdateSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Класс отзывы."""

    serializer_class = ReviewSerializer
    permission_classes = (
        permissions.IsAuthorModeratorAdminOrReadOnly,
        IsAuthenticatedOrReadOnly
    )
    filter_backends = (filters.OrderingFilter,)
    http_method_names = HTTP_METHODS

    def get_title(self):
        """Возвращает объетк произведения."""
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        """Функция get_queryset."""
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        """Функция perfom_create."""
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """Класс комментарии."""

    serializer_class = CommentSerializer
    permission_classes = (
        permissions.IsAuthorModeratorAdminOrReadOnly,
        IsAuthenticatedOrReadOnly
    )
    filter_backends = (filters.OrderingFilter,)
    http_method_names = HTTP_METHODS

    def get_review(self):
        """Возвращает объект отзыва."""
        return get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title__id=self.kwargs.get('title_id')
        )

    def perform_create(self, serializer):
        """Функция perfom_create."""
        serializer.save(author=self.request.user, review=self.get_review())

    def get_queryset(self):
        """Функция get_queryset."""
        return self.get_review().comments.all()


def send_success_email(user):
    """Отправляет email с кодом подтверждения."""
    send_mail(
        subject='Регистрация',
        message=f'Ваш confirmation_code: {user.confirmation_code}',
        from_email=SERVER_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы администратора с users."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAdmin,)
    lookup_field = 'username'
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    http_method_names = ('get', 'post', 'patch', 'delete')
    search_fields = ('username',)

    @action(
        detail=False,
        methods=('get', 'patch'),
        permission_classes=(IsAuthenticated,),
        url_path=URL_PROFILE_PREF,
    )
    def get_users_profile(self, request):
        """Обрабатывает GET И PATCH запросы к api/v1/users/me."""
        if request.method == 'GET':
            return Response(UserSerializer(request.user).data)
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class SignUPAPIView(APIView):
    """Вьюсет для регистрации пользователей."""

    serializer_class = SignUPSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        """Обрабатывает POST запросы к api/v1/auth/signup/.

        Если данные не валидны возвращает ошибку.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = request.data.get('username')
        email = request.data.get('email')
        try:
            user, query_status = User.objects.get_or_create(
                username=username,
                email=email
            )
        except IntegrityError:
            if User.objects.filter(username=username).exists():
                raise serializers.ValidationError(
                    {
                        'username': [
                            'Обязательное поле некорректно.'
                        ]
                    }
                )
            elif User.objects.filter(email=email).exists():
                raise serializers.ValidationError(
                    {
                        'email': [
                            'Обязательное поле некорректно.'
                        ]
                    }
                )

        user.confirmation_code = ''.join(random.choices(
            CONF_CODE_PATTERN,
            k=CONF_CODE_LENGTH
        ))
        user.save()
        send_success_email(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenAPIView(APIView):
    """Вьюсет для аутентификации пользователей по коду подтверждения."""

    serializer_class = TokenSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        """Обрабатывает POST запросы к api/v1/auth/token/.

        Если данные не валидны возвращает ошибку.
        """
        confirmation_code = request.data.get('confirmation_code')
        if confirmation_code == NOT_APPLICABLE_CONF_CODE:
            raise serializers.ValidationError(CONFIRMATION_ERROR)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User,
            username=request.data.get('username')
        )
        if confirmation_code != user.confirmation_code:
            user.confirmation_code = NOT_APPLICABLE_CONF_CODE
            user.save()
            raise serializers.ValidationError(CONFIRMATION_ERROR)
        return Response({
            'token': str(RefreshToken.for_user(user).access_token)
        },
            status=status.HTTP_200_OK
        )

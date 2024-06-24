"""Файл настройки приложения."""
from django.apps import AppConfig


class ReviewsConfig(AppConfig):
    """Конфигурация."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reviews'

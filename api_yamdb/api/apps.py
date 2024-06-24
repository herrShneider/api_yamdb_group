"""Файл настройки приложения."""
from django.apps import AppConfig


class ApiConfig(AppConfig):
    """Конфигурация."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

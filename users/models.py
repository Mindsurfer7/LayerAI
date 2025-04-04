from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

# from django.contrib.postgres.fields import ArrayField


class User(AbstractUser):
    # Пока используем username, но email нам понадобится позже
    email = models.EmailField(
        _("email address"), unique=False, blank=True, null=True
    )  # пока не unique
    is_premium = models.BooleanField(default=False)

    # Кастомная аватарка
    avatar_url = models.URLField(blank=True, null=True)

    # Системные промпты (как массив строк)
    system_prompts = models.JSONField(
        default=list, blank=True, null=True
    )  # когда будет постгрес сделать ArrayField

    # Настройки пользователя (как словарь)
    settings = models.JSONField(default=dict, blank=True)

    # Язык интерфейса (можно ограничить список, но пока текст)
    language = models.CharField(max_length=32, default="en")

    # Таймзона
    timezone = models.CharField(max_length=64, default="UTC")

    # TODO: двухфакторка, подписка и т.п. — добавим позже

    def __str__(self):
        return self.username

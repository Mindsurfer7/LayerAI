from django.db import models
from django.conf import settings


class UserMemory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memories"
    )
    title = models.CharField(max_length=255)  # Краткий заголовок факта
    fact = models.TextField()  # Сам факт
    reason = models.TextField()  # Причина, почему это важно
    confidence = models.FloatField()  # Уверенность (от 0 до 1)
    source_messages = models.JSONField()  # Список ID сообщений (например, [3, 5, 7])
    fact_category = (
        models.JSONField()
    )  # интересам, привычкам, профессии, стилю общения, цели использования, ценностям, мировоззрению, предпочтениям
    created_at = models.DateTimeField(auto_now_add=True)  # Время создания

    def __str__(self):
        return f"{self.title} (user: {self.user.username})"

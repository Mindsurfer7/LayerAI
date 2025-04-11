from django.db import models
from django.conf import settings


class UserMemory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memories"
    )
    title = models.CharField(max_length=255)
    fact = models.TextField()
    reason = models.TextField()
    confidence = models.FloatField()
    source_messages = models.JSONField()
    fact_category = models.CharField(
        max_length=100,
        choices=[
            ("interests", "Interests"),
            ("habits", "Habits"),
            ("profession", "Profession"),
            ("communication_style", "Communication Style"),
            ("goals", "Goals"),
            ("values", "Values"),
            ("worldview", "Worldview"),
            ("preferences", "Preferences"),
        ],
        default="interests",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} (user: {self.user.username})"

    class Meta:
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["fact_category"]),
        ]

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

# from django.contrib.postgres.fields import ArrayField


class User(AbstractUser):
    email = models.EmailField(_("email address"), unique=False, blank=True, null=True)
    is_premium = models.BooleanField(default=False)
    avatar_url = models.URLField(blank=True, null=True)
    system_prompts = models.JSONField(
        default=list, blank=True, null=True
    )  # когда будет постгрес сделать ArrayField
    settings = models.JSONField(default=dict, blank=True)
    language = models.CharField(max_length=32, default="en")
    timezone = models.CharField(max_length=64, default="UTC")

    def __str__(self):
        return self.username

    def get_user_facts(self, category=None):

        memories = self.memories.all()
        if category:
            memories = memories.filter(fact_category=category)
        return [
            {
                "title": memory.title,
                "fact": memory.fact,
                "category": memory.fact_category,
                "confidence": memory.confidence,
            }
            for memory in memories
        ]

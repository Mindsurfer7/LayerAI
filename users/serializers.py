from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'is_premium',
            'avatar_url',
            'system_prompts',
            'settings',
            'language',
            'timezone',
        )
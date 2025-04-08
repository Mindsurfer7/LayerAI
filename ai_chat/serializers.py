# ai_chat/serializers.py
from rest_framework import serializers
from .models import Message


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ("id", "content", "role", "timestamp")

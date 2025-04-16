# ai_chat/urls.py
from django.urls import path
from .views import (
    ChatProxyView,
    ChatMessageListAPIView,
    ChatSessionCreateAPIView,
    ChatSessionListAPIView,
    TranscribeVoiceAPIView,
)

urlpatterns = [
    path("", ChatProxyView.as_view(), name="ai-chat"),
    path("chat-sessions/<int:session_id>/messages/", ChatMessageListAPIView.as_view()),
    path(
        "chat-session/create/",
        ChatSessionCreateAPIView.as_view(),
        name="chat-session-create",
    ),
    path("chat-sessions/", ChatSessionListAPIView.as_view(), name="chat-session-list"),
    path("transcribe/", TranscribeVoiceAPIView.as_view(), name="transcribe"),
]

# ai_chat/urls.py
from django.urls import path
from .views import ChatProxyView, ChatMessageListAPIView, ChatSessionCreateAPIView

urlpatterns = [
    path("", ChatProxyView.as_view(), name="ai-chat"),
    path("chat-sessions/<int:session_id>/messages/", ChatMessageListAPIView.as_view()),
    path(
        "chat-sessions/", ChatSessionCreateAPIView.as_view(), name="chat-session-create"
    ),
]

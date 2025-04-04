# ai_chat/urls.py
from django.urls import path
from .views import ChatProxyView

urlpatterns = [
    path("", ChatProxyView.as_view(), name="ai-chat"),
]

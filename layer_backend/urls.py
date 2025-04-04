from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("djoser.urls")),  # регистрация, текущий пользователь и т.п.
    path("auth/", include("djoser.urls.jwt")),  # JWT: login, refresh, verify
    path("api/ai-chat/", include("ai_chat.urls")),  # <- наша ручка
]

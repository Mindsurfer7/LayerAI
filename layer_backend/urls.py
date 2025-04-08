from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.jwt")),
    path("api/v1/ai-chat/", include("ai_chat.urls")),
    path("api/v1/memory/", include("memory.urls")),
]

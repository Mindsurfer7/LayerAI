

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('djoser.urls')),  # регистрация, текущий пользователь и т.п.
    path('auth/', include('djoser.urls.jwt')),  # JWT: login, refresh, verify
]
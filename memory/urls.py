from django.urls import path
from .views import analyze_memory

urlpatterns = [
    path("analyze/", analyze_memory, name="analyze_memory"),
]

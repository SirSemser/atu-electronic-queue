from django.urls import path
from .views import api_config

urlpatterns = [
    path("", api_config, name="api_config"),
]

from django.urls import path
from .views import public_config

urlpatterns = [
    path("config/", public_config, name="public_config"),
]

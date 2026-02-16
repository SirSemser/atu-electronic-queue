from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views
from operators.views import operator_dashboard
from siteconfig.views import app_online
def home(request):
    return redirect("/app/index/")

urlpatterns = [
    path("", home),

    path("admin/", admin.site.urls),

    # API
    path("api/", include("tickets.urls")),
    path("api/config/", include("config.urls")),  # ✅ ВАЖНО

    # Operator auth + dashboard
    path("operator/login/", auth_views.LoginView.as_view(template_name="operator/login.html"), name="operator_login"),
    path("operator/logout/", auth_views.LogoutView.as_view(next_page="/operator/login/"), name="operator_logout"),
    path("operator/", include("operators.urls")),  # ✅ лучше так
    path("accounts/profile/", lambda r: redirect("/operator/")),  # ✅ чтобы не кидало на /accounts/profile/

    # Client pages (/app/...)
    path("app/index/", TemplateView.as_view(template_name="app/index.html")),
    path("app/register/", TemplateView.as_view(template_name="app/register.html")),
    path("app/service/", TemplateView.as_view(template_name="app/service.html")),
    path("app/consultation/", TemplateView.as_view(template_name="app/consultation.html")),
    path("app/admission/", TemplateView.as_view(template_name="app/admission.html")),
    path("app/contest/", TemplateView.as_view(template_name="app/contest.html")),
    path("app/online/", TemplateView.as_view(template_name="app/online.html")),
    path("app/done/", TemplateView.as_view(template_name="app/done.html")),
    path("app/online/", app_online),
]

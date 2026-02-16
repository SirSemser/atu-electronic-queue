from django.urls import path
from . import views

urlpatterns = [
    path("", views.operator_dashboard, name="operator_dashboard"),

    # actions
    path("call-next/", views.operator_call_next, name="operator_call_next"),
    path("ticket/<int:ticket_id>/status/<str:new_status>/", views.operator_set_status, name="operator_set_status"),

    # profile
    path("profile/", views.operator_profile, name="operator_profile"),
    path("password/", views.operator_password_change, name="operator_password_change"),

    # ajax
    path("queue.json", views.operator_queue_json, name="operator_queue_json"),

    # logs
    path("logs.csv", views.operator_logs_csv, name="operator_logs_csv"),
    path("admin-logs.csv", views.admin_logs_csv, name="admin_logs_csv"),
]

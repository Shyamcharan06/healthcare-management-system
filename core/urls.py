from django.urls import path

from core import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("redirect/", views.post_login_redirect, name="post_login_redirect"),
    path("dashboard/admin/", views.admin_dashboard, name="admin_dashboard"),
    path("dashboard/admin/data.json", views.admin_dashboard_data, name="admin_dashboard_data"),
]

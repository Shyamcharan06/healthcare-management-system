from django.urls import path

from accounts import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.RoleLoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("signup/", views.signup, name="signup"),
    path("register/admin/", views.register_admin, name="register_admin"),
    path("register/doctor/", views.register_doctor, name="register_doctor"),
    path("register/patient/", views.register_patient, name="register_patient"),
    path("accounts-list/", views.account_list, name="account_list"),
]

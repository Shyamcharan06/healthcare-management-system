from django.urls import path

from patients import views

app_name = "patients"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/data.json", views.dashboard_data, name="dashboard_data"),
    path("profile/", views.profile, name="profile"),
    path("prescriptions/", views.prescription_history, name="prescription_history"),
    path("doctors/", views.doctors_consulted, name="doctors_consulted"),
]

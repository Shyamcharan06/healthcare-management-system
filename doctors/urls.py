from django.urls import path

from doctors import views

app_name = "doctors"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/data.json", views.dashboard_data, name="dashboard_data"),
    path("patients/", views.patient_list, name="patient_list"),
    path("patients/<int:patient_id>/", views.patient_detail, name="patient_detail"),
    path("patients/<int:patient_id>/notes/add/", views.add_consultation_note, name="add_consultation_note"),
    path("profile/", views.profile, name="profile"),
]

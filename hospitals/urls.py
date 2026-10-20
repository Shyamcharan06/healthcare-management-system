from django.urls import path

from hospitals import views

app_name = "hospitals"

urlpatterns = [
    path("", views.directory, name="directory"),
    path("<int:pk>/", views.hospital_detail, name="detail"),
    path("manage/", views.manage_hospitals, name="manage"),
    path("manage/<int:pk>/edit/", views.edit_hospital, name="edit"),
    path("manage/assign-doctor/", views.assign_doctor, name="assign_doctor"),
]

from django.urls import path

from prescriptions import views

app_name = "prescriptions"

urlpatterns = [
    path("", views.prescription_list, name="list"),
    path("upload/", views.upload_prescription, name="upload"),
    path("upload/verify/", views.verify_upload, name="verify_upload"),
    path("create/", views.create_prescription, name="create"),
    path("create/<int:patient_id>/", views.create_prescription, name="create_for_patient"),
    path("<int:pk>/", views.prescription_detail, name="detail"),
    path("<int:pk>/print/", views.prescription_print, name="print"),
    path("<int:pk>/download/", views.prescription_download, name="download"),
]

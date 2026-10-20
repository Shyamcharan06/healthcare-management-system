from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("hospitals/", include("hospitals.urls")),
    path("doctors/", include("doctors.urls")),
    path("patients/", include("patients.urls")),
    path("prescriptions/", include("prescriptions.urls")),
    path("medications/", include("medications.urls")),
    path("", include("core.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

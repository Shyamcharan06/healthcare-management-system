from django.contrib import admin

from doctors.models import Doctor, DoctorPatientLink, ConsultationNote


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("name", "specialization", "hospital", "department", "experience")
    list_filter = ("hospital", "department")
    search_fields = ("name", "specialization")


@admin.register(DoctorPatientLink)
class DoctorPatientLinkAdmin(admin.ModelAdmin):
    list_display = ("doctor", "patient", "linked_date")


@admin.register(ConsultationNote)
class ConsultationNoteAdmin(admin.ModelAdmin):
    list_display = ("doctor", "patient", "consultation_date", "follow_up_date")

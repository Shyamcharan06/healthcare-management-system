from django.contrib import admin

from prescriptions.models import Prescription, PrescriptionMedicine


class PrescriptionMedicineInline(admin.TabularInline):
    model = PrescriptionMedicine
    extra = 0


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "doctor", "patient", "date_issued", "status", "follow_up_date")
    list_filter = ("status",)
    inlines = [PrescriptionMedicineInline]

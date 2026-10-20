from django.contrib import admin

from medications.models import Medicine, DrugInteraction, MedicationReminder


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ("name", "dosage_info")
    search_fields = ("name",)


@admin.register(DrugInteraction)
class DrugInteractionAdmin(admin.ModelAdmin):
    list_display = ("medicine_a", "medicine_b", "severity")
    list_filter = ("severity",)


@admin.register(MedicationReminder)
class MedicationReminderAdmin(admin.ModelAdmin):
    list_display = ("patient", "medicine", "scheduled_date", "time", "status")
    list_filter = ("status", "scheduled_date")

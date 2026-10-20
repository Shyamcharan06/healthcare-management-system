from django.db import models

from doctors.models import Doctor
from patients.models import Patient
from medications.models import Medicine


def prescription_upload_path(instance, filename):
    return f"prescriptions/patient_{instance.patient_id}/{filename}"


class Prescription(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        COMPLETED = "COMPLETED", "Completed"
        ARCHIVED = "ARCHIVED", "Archived"

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="prescriptions")
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="prescriptions")
    date_issued = models.DateField(auto_now_add=True)
    follow_up_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)

    source_file = models.FileField(upload_to=prescription_upload_path, null=True, blank=True)
    uploaded_by_patient = models.BooleanField(default=False)

    class Meta:
        ordering = ["-date_issued"]

    def __str__(self):
        return f"Prescription #{self.pk} - {self.patient} / {self.doctor}"


class PrescriptionMedicine(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name="items")
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name="prescription_items")
    dosage = models.CharField(max_length=100, blank=True)
    frequency = models.CharField(max_length=100, blank=True)
    duration = models.CharField(max_length=100, blank=True)

    class Meta:
        unique_together = ("prescription", "medicine")

    def __str__(self):
        return f"{self.medicine} in Rx#{self.prescription_id}"

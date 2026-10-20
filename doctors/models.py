from django.conf import settings
from django.db import models

from hospitals.models import Hospital, Department
from patients.models import Patient


class Doctor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="doctor_profile",
        null=True, blank=True,
    )
    hospital = models.ForeignKey(Hospital, on_delete=models.SET_NULL, null=True, blank=True, related_name="doctors")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name="doctors")
    name = models.CharField(max_length=150)
    specialization = models.CharField(max_length=150, blank=True)
    experience = models.PositiveIntegerField(default=0, help_text="Years of experience")
    contact = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"Dr. {self.name}"


class DoctorPatientLink(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="patient_links")
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="doctor_links")
    linked_date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ("doctor", "patient")
        ordering = ["-linked_date"]

    def __str__(self):
        return f"{self.doctor} <-> {self.patient}"


class ConsultationNote(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="consultation_notes")
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="consultation_notes")
    consultation_date = models.DateField()
    diagnosis = models.CharField(max_length=255, blank=True)
    symptoms = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-consultation_date"]

    def __str__(self):
        return f"Note for {self.patient} by {self.doctor} on {self.consultation_date}"

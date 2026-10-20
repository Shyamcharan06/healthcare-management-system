from django.db import models

from patients.models import Patient


class Medicine(models.Model):
    name = models.CharField(max_length=200, unique=True)
    uses = models.TextField(blank=True)
    dosage_info = models.CharField(max_length=255, blank=True)
    side_effects = models.TextField(blank=True)
    precautions = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class DrugInteraction(models.Model):
    class Severity(models.TextChoices):
        LOW = "LOW", "Low"
        MODERATE = "MODERATE", "Moderate"
        SEVERE = "SEVERE", "Severe"

    medicine_a = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name="interactions_as_a")
    medicine_b = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name="interactions_as_b")
    severity = models.CharField(max_length=10, choices=Severity.choices, default=Severity.MODERATE)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ("medicine_a", "medicine_b")

    def __str__(self):
        return f"{self.medicine_a} <-> {self.medicine_b} ({self.severity})"


class MedicationReminder(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        TAKEN = "TAKEN", "Taken"
        MISSED = "MISSED", "Missed"

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="reminders")
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name="reminders")
    scheduled_date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)

    class Meta:
        ordering = ["scheduled_date", "time"]

    def __str__(self):
        return f"{self.medicine} for {self.patient} at {self.time} on {self.scheduled_date}"

from datetime import date, timedelta

from medications.models import MedicationReminder


def compute_adherence(patient, days=30):
    """Adherence % = reminders marked Taken / total reminders due, over the tracked period."""
    period_start = date.today() - timedelta(days=days)
    reminders = MedicationReminder.objects.filter(patient=patient, scheduled_date__gte=period_start)
    total_due = reminders.exclude(status=MedicationReminder.Status.PENDING).count()
    taken = reminders.filter(status=MedicationReminder.Status.TAKEN).count()
    if total_due == 0:
        return 0
    return round((taken / total_due) * 100, 1)


def check_medicine_and_interactions(medicine_ids):
    """Given an iterable of medicine ids, return info for each plus any interaction warnings among them."""
    from medications.models import Medicine, DrugInteraction

    medicine_ids = list(medicine_ids)
    medicines = list(Medicine.objects.filter(pk__in=medicine_ids))

    interactions = []
    if len(medicine_ids) > 1:
        interactions = list(
            DrugInteraction.objects.filter(
                medicine_a_id__in=medicine_ids, medicine_b_id__in=medicine_ids
            ).select_related("medicine_a", "medicine_b")
        )

    return medicines, interactions

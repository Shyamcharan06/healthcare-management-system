from datetime import datetime

from celery import shared_task
from django.utils import timezone

from medications.models import MedicationReminder


@shared_task
def mark_overdue_reminders_missed():
    now = timezone.localtime()
    overdue = MedicationReminder.objects.filter(
        status=MedicationReminder.Status.PENDING,
        scheduled_date__lte=now.date(),
    )
    count = 0
    for reminder in overdue:
        scheduled_at = datetime.combine(reminder.scheduled_date, reminder.time)
        if timezone.is_naive(scheduled_at):
            scheduled_at = timezone.make_aware(scheduled_at, now.tzinfo)
        if scheduled_at < now:
            reminder.status = MedicationReminder.Status.MISSED
            reminder.save(update_fields=["status"])
            count += 1
    return count

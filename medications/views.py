from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from accounts.models import User
from core.decorators import role_required
from medications.forms import MedicineLookupForm, MedicationReminderForm
from medications.models import MedicationReminder
from medications.utils import check_medicine_and_interactions
from patients.models import Patient


def _get_patient(request):
    return get_object_or_404(Patient, user=request.user)


@role_required(User.Role.PATIENT, User.Role.DOCTOR, User.Role.ADMIN)
def medicine_lookup(request):
    medicines = []
    interactions = []
    form = MedicineLookupForm(request.GET or None)
    if request.GET and form.is_valid():
        selected = form.cleaned_data["medicines"]
        medicines, interactions = check_medicine_and_interactions([m.pk for m in selected])
    return render(
        request,
        "medications/lookup.html",
        {"form": form, "medicines": medicines, "interactions": interactions},
    )


@role_required(User.Role.PATIENT)
def reminder_list(request):
    patient = _get_patient(request)
    if request.method == "POST":
        form = MedicationReminderForm(request.POST, patient=patient)
        if form.is_valid():
            reminder = form.save(commit=False)
            reminder.patient = patient
            reminder.save()
            messages.success(request, "Reminder scheduled.")
            return redirect("medications:reminder_list")
    else:
        form = MedicationReminderForm(patient=patient)

    reminders = MedicationReminder.objects.filter(patient=patient).select_related("medicine")
    return render(request, "medications/reminder_list.html", {"form": form, "reminders": reminders})


@role_required(User.Role.PATIENT)
def mark_taken(request, reminder_id):
    patient = _get_patient(request)
    reminder = get_object_or_404(MedicationReminder, pk=reminder_id, patient=patient)
    reminder.status = MedicationReminder.Status.TAKEN
    reminder.save()
    messages.success(request, f"Marked {reminder.medicine} as taken.")
    return redirect("medications:reminder_list")

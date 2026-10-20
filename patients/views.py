from datetime import date
from itertools import groupby

from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from accounts.models import User
from core.decorators import role_required
from doctors.models import DoctorPatientLink
from medications.models import MedicationReminder
from medications.utils import compute_adherence
from patients.forms import PatientProfileForm
from patients.models import Patient
from prescriptions.models import Prescription


def _get_patient(request):
    return get_object_or_404(Patient, user=request.user)


@role_required(User.Role.PATIENT)
def dashboard(request):
    patient = _get_patient(request)
    today = date.today()

    active_prescriptions = Prescription.objects.filter(patient=patient, status=Prescription.Status.ACTIVE)
    todays_medications = MedicationReminder.objects.filter(patient=patient, scheduled_date=today).select_related(
        "medicine"
    )
    missed_doses = MedicationReminder.objects.filter(patient=patient, status=MedicationReminder.Status.MISSED).count()
    upcoming_followups = Prescription.objects.filter(
        patient=patient, follow_up_date__gte=today
    ).select_related("doctor").order_by("follow_up_date")[:8]
    recent_prescriptions = Prescription.objects.filter(patient=patient).select_related("doctor")[:8]

    context = {
        "patient": patient,
        "active_prescription_count": active_prescriptions.count(),
        "todays_medications": todays_medications,
        "missed_doses": missed_doses,
        "adherence_pct": compute_adherence(patient),
        "upcoming_followups": upcoming_followups,
        "recent_prescriptions": recent_prescriptions,
    }
    return render(request, "patients/dashboard.html", context)


@role_required(User.Role.PATIENT)
def dashboard_data(request):
    patient = _get_patient(request)
    status_counts = {
        choice.value: Prescription.objects.filter(patient=patient, status=choice).count()
        for choice in Prescription.Status
    }
    reminder_counts = {
        choice.value: MedicationReminder.objects.filter(patient=patient, status=choice).count()
        for choice in MedicationReminder.Status
    }
    return JsonResponse({"prescription_status": status_counts, "reminder_status": reminder_counts})


@role_required(User.Role.PATIENT)
def profile(request):
    patient = _get_patient(request)
    if request.method == "POST":
        form = PatientProfileForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("patients:profile")
    else:
        form = PatientProfileForm(instance=patient)
    return render(request, "patients/profile.html", {"form": form, "patient": patient})


@role_required(User.Role.PATIENT)
def prescription_history(request):
    patient = _get_patient(request)
    query = request.GET.get("q", "").strip()

    prescriptions = Prescription.objects.filter(patient=patient).select_related(
        "doctor", "doctor__hospital"
    ).prefetch_related("items__medicine").order_by("doctor__hospital__name", "doctor__name", "-date_issued")

    if query:
        prescriptions = prescriptions.filter(
            Q(items__medicine__name__icontains=query) | Q(doctor__name__icontains=query)
        ).distinct()

    grouped = []
    for hospital, hosp_group in groupby(prescriptions, key=lambda p: p.doctor.hospital):
        hosp_group = list(hosp_group)
        by_doctor = []
        for doctor, doc_group in groupby(hosp_group, key=lambda p: p.doctor):
            by_doctor.append((doctor, list(doc_group)))
        grouped.append((hospital, by_doctor))

    return render(request, "patients/prescription_history.html", {"grouped": grouped, "query": query})


@role_required(User.Role.PATIENT)
def doctors_consulted(request):
    patient = _get_patient(request)
    links = DoctorPatientLink.objects.filter(patient=patient).select_related("doctor", "doctor__hospital")
    return render(request, "patients/doctors_consulted.html", {"links": links})

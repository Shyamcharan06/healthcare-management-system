from datetime import date

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse

from accounts.models import User
from core.decorators import role_required
from doctors.forms import ConsultationNoteForm, DoctorProfileForm
from doctors.models import Doctor, DoctorPatientLink, ConsultationNote
from patients.models import Patient
from prescriptions.models import Prescription


def _get_doctor(request):
    return get_object_or_404(Doctor, user=request.user)


@role_required(User.Role.DOCTOR)
def dashboard(request):
    doctor = _get_doctor(request)
    linked_patient_count = DoctorPatientLink.objects.filter(doctor=doctor).count()
    recent_consultations = ConsultationNote.objects.filter(doctor=doctor).select_related("patient")[:8]
    upcoming_followups = ConsultationNote.objects.filter(
        doctor=doctor, follow_up_date__gte=date.today()
    ).select_related("patient").order_by("follow_up_date")[:8]
    recent_prescriptions = Prescription.objects.filter(doctor=doctor).select_related("patient")[:8]

    context = {
        "doctor": doctor,
        "linked_patient_count": linked_patient_count,
        "recent_consultations": recent_consultations,
        "upcoming_followups": upcoming_followups,
        "recent_prescriptions": recent_prescriptions,
    }
    return render(request, "doctors/dashboard.html", context)


@role_required(User.Role.DOCTOR)
def dashboard_data(request):
    doctor = _get_doctor(request)
    status_counts = {
        choice.value: Prescription.objects.filter(doctor=doctor, status=choice).count()
        for choice in Prescription.Status
    }
    return JsonResponse({"prescription_status": status_counts})


@role_required(User.Role.DOCTOR)
def patient_list(request):
    doctor = _get_doctor(request)
    links = DoctorPatientLink.objects.filter(doctor=doctor).select_related("patient").order_by("patient__name")
    return render(request, "doctors/patient_list.html", {"links": links, "doctor": doctor})


@role_required(User.Role.DOCTOR)
def patient_detail(request, patient_id):
    doctor = _get_doctor(request)
    link = get_object_or_404(DoctorPatientLink, doctor=doctor, patient_id=patient_id)
    patient = link.patient
    prescriptions = Prescription.objects.filter(doctor=doctor, patient=patient).prefetch_related(
        "items__medicine"
    )
    notes = ConsultationNote.objects.filter(doctor=doctor, patient=patient)
    return render(
        request,
        "doctors/patient_detail.html",
        {"patient": patient, "prescriptions": prescriptions, "notes": notes},
    )


@role_required(User.Role.DOCTOR)
def add_consultation_note(request, patient_id):
    doctor = _get_doctor(request)
    link = get_object_or_404(DoctorPatientLink, doctor=doctor, patient_id=patient_id)
    patient = link.patient

    if request.method == "POST":
        form = ConsultationNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.doctor = doctor
            note.patient = patient
            note.save()
            messages.success(request, "Consultation note added.")
            return redirect("doctors:patient_detail", patient_id=patient.pk)
    else:
        form = ConsultationNoteForm()
    return render(request, "doctors/add_consultation_note.html", {"form": form, "patient": patient})


@role_required(User.Role.DOCTOR)
def profile(request):
    doctor = _get_doctor(request)
    if request.method == "POST":
        form = DoctorProfileForm(request.POST, instance=doctor)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("doctors:profile")
    else:
        form = DoctorProfileForm(instance=doctor)
    return render(request, "doctors/profile.html", {"form": form, "doctor": doctor})

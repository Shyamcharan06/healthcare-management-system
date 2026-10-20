from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render, redirect

from accounts.models import User
from core.decorators import role_required
from doctors.models import Doctor, ConsultationNote
from hospitals.models import Hospital, Department
from patients.models import Patient
from prescriptions.models import Prescription


def home(request):
    if request.user.is_authenticated:
        return redirect("core:post_login_redirect")
    return redirect("accounts:login")


@login_required
def post_login_redirect(request):
    role = request.user.role
    if role == User.Role.ADMIN:
        return redirect("core:admin_dashboard")
    if role == User.Role.DOCTOR:
        return redirect("doctors:dashboard")
    if role == User.Role.PATIENT:
        return redirect("patients:dashboard")
    return redirect("accounts:login")


@role_required(User.Role.ADMIN)
def admin_dashboard(request):
    context = {
        "hospital_count": Hospital.objects.count(),
        "department_count": Department.objects.count(),
        "doctor_count": Doctor.objects.count(),
        "patient_count": Patient.objects.count(),
        "prescription_count": Prescription.objects.count(),
        "active_prescription_count": Prescription.objects.filter(status=Prescription.Status.ACTIVE).count(),
        "recent_consultations": ConsultationNote.objects.select_related("doctor", "patient").order_by(
            "-consultation_date"
        )[:8],
    }
    return render(request, "core/admin_dashboard.html", context)


@role_required(User.Role.ADMIN)
def admin_dashboard_data(request):
    status_counts = {
        choice.value: Prescription.objects.filter(status=choice).count()
        for choice in Prescription.Status
    }
    hospital_doctor_counts = list(
        Hospital.objects.annotate(doctor_total=Count("doctors"))
        .values("name", "doctor_total")
        .order_by("-doctor_total")[:10]
    )
    return JsonResponse(
        {
            "entity_counts": {
                "Hospitals": Hospital.objects.count(),
                "Departments": Department.objects.count(),
                "Doctors": Doctor.objects.count(),
                "Patients": Patient.objects.count(),
            },
            "prescription_status": status_counts,
            "doctors_per_hospital": hospital_doctor_counts,
        }
    )

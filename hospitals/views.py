from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from accounts.models import User
from core.decorators import role_required
from doctors.models import Doctor
from hospitals.forms import HospitalForm, DepartmentForm
from hospitals.models import Hospital, Department


@login_required
def directory(request):
    hospitals = Hospital.objects.prefetch_related("departments", "doctors").all()
    return render(request, "hospitals/directory.html", {"hospitals": hospitals})


@login_required
def hospital_detail(request, pk):
    hospital = get_object_or_404(Hospital, pk=pk)
    departments = hospital.departments.prefetch_related("doctors").all()
    doctors = hospital.doctors.select_related("department").all()
    return render(
        request,
        "hospitals/hospital_detail.html",
        {"hospital": hospital, "departments": departments, "doctors": doctors},
    )


@role_required(User.Role.ADMIN)
def manage_hospitals(request):
    hospital_form = HospitalForm(prefix="hospital")
    department_form = DepartmentForm(prefix="department")

    if request.method == "POST":
        if "add_hospital" in request.POST:
            hospital_form = HospitalForm(request.POST, prefix="hospital")
            if hospital_form.is_valid():
                hospital_form.save()
                messages.success(request, "Hospital added.")
                return redirect("hospitals:manage")
        elif "add_department" in request.POST:
            department_form = DepartmentForm(request.POST, prefix="department")
            if department_form.is_valid():
                department_form.save()
                messages.success(request, "Department added.")
                return redirect("hospitals:manage")

    hospitals = Hospital.objects.prefetch_related("departments").all()
    return render(
        request,
        "hospitals/manage.html",
        {"hospitals": hospitals, "hospital_form": hospital_form, "department_form": department_form},
    )


@role_required(User.Role.ADMIN)
def edit_hospital(request, pk):
    hospital = get_object_or_404(Hospital, pk=pk)
    if request.method == "POST":
        form = HospitalForm(request.POST, instance=hospital)
        if form.is_valid():
            form.save()
            messages.success(request, "Hospital updated.")
            return redirect("hospitals:manage")
    else:
        form = HospitalForm(instance=hospital)
    return render(request, "hospitals/edit_hospital.html", {"form": form, "hospital": hospital})


@role_required(User.Role.ADMIN)
def assign_doctor(request):
    doctors = Doctor.objects.select_related("hospital", "department").all()
    if request.method == "POST":
        doctor_id = request.POST.get("doctor_id")
        hospital_id = request.POST.get("hospital_id") or None
        department_id = request.POST.get("department_id") or None
        doctor = get_object_or_404(Doctor, pk=doctor_id)
        doctor.hospital_id = hospital_id
        doctor.department_id = department_id
        doctor.save()
        messages.success(request, f"Updated hospital/department for Dr. {doctor.name}.")
        return redirect("hospitals:assign_doctor")

    hospitals = Hospital.objects.prefetch_related("departments").all()
    return render(request, "hospitals/assign_doctor.html", {"doctors": doctors, "hospitals": hospitals})

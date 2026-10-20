from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from accounts.forms import RoleLoginForm, AdminAccountForm, DoctorAccountForm, PatientAccountForm
from accounts.models import User
from core.decorators import role_required
from doctors.models import Doctor
from patients.models import Patient


class RoleLoginView(LoginView):
    template_name = "accounts/login.html"
    form_class = RoleLoginForm
    redirect_authenticated_user = True


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("accounts:login")


def signup(request):
    """Public self-service account creation for patients."""
    if request.user.is_authenticated:
        return redirect("core:post_login_redirect")

    if request.method == "POST":
        form = PatientAccountForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = User.objects.create_user(
                username=data["username"],
                email=data["email"],
                password=data["password"],
                role=User.Role.PATIENT,
            )
            Patient.objects.create(
                user=user,
                name=data["name"],
                dob=data["dob"],
                contact=data["contact"],
            )
            login(request, user)
            messages.success(request, f"Welcome, {data['name']}! Your account has been created.")
            return redirect("patients:dashboard")
    else:
        form = PatientAccountForm()
    return render(request, "accounts/signup.html", {"form": form})


@role_required(User.Role.ADMIN)
def register_admin(request):
    if request.method == "POST":
        form = AdminAccountForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            User.objects.create_user(
                username=data["username"],
                email=data["email"],
                password=data["password"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                role=User.Role.ADMIN,
                is_staff=True,
            )
            messages.success(request, f"Administrator account created for {data['username']}.")
            return redirect("accounts:register_admin")
    else:
        form = AdminAccountForm()
    return render(request, "accounts/register_admin.html", {"form": form})


@role_required(User.Role.ADMIN)
def register_doctor(request):
    if request.method == "POST":
        form = DoctorAccountForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = User.objects.create_user(
                username=data["username"],
                email=data["email"],
                password=data["password"],
                role=User.Role.DOCTOR,
            )
            Doctor.objects.create(
                user=user,
                name=data["name"],
                specialization=data["specialization"],
                experience=data["experience"],
                contact=data["contact"],
                hospital=data["hospital"],
                department=data["department"],
            )
            messages.success(request, f"Doctor account created for {data['name']}.")
            return redirect("accounts:register_doctor")
    else:
        form = DoctorAccountForm()
    return render(request, "accounts/register_doctor.html", {"form": form})


@role_required(User.Role.ADMIN)
def register_patient(request):
    if request.method == "POST":
        form = PatientAccountForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = User.objects.create_user(
                username=data["username"],
                email=data["email"],
                password=data["password"],
                role=User.Role.PATIENT,
            )
            Patient.objects.create(
                user=user,
                name=data["name"],
                dob=data["dob"],
                contact=data["contact"],
            )
            messages.success(request, f"Patient account created for {data['name']}.")
            return redirect("accounts:register_patient")
    else:
        form = PatientAccountForm()
    return render(request, "accounts/register_patient.html", {"form": form})


@role_required(User.Role.ADMIN)
def account_list(request):
    admins = User.objects.filter(role=User.Role.ADMIN)
    doctors = Doctor.objects.select_related("user", "hospital", "department").all()
    patients = Patient.objects.select_related("user").all()
    return render(
        request, "accounts/account_list.html", {"admins": admins, "doctors": doctors, "patients": patients}
    )

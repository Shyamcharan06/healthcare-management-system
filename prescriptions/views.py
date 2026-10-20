import uuid

from django.contrib import messages
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string

from accounts.models import User
from core.decorators import role_required
from doctors.models import Doctor, DoctorPatientLink
from patients.models import Patient
from prescriptions.forms import (
    PrescriptionUploadForm,
    VerifyMedicineFormSet,
    VerifyPrescriptionMetaForm,
    DoctorPrescriptionMedicineFormSet,
    DoctorPrescriptionMetaForm,
    PrescriptionStatusForm,
)
from prescriptions.models import Prescription, PrescriptionMedicine
from prescriptions.ocr import extract_text, parse_prescription_text

SESSION_ITEMS_KEY = "ocr_extracted_items"
SESSION_TEMP_FILE_KEY = "ocr_temp_file_path"
SESSION_ORIGINAL_NAME_KEY = "ocr_original_filename"


def _get_doctor(request):
    return get_object_or_404(Doctor, user=request.user)


def _get_patient(request):
    return get_object_or_404(Patient, user=request.user)


def _can_view_prescription(user, prescription):
    if user.role == User.Role.ADMIN:
        return True
    if user.role == User.Role.DOCTOR:
        return hasattr(user, "doctor_profile") and prescription.doctor_id == user.doctor_profile.pk
    if user.role == User.Role.PATIENT:
        return hasattr(user, "patient_profile") and prescription.patient_id == user.patient_profile.pk
    return False


@role_required(User.Role.PATIENT)
def upload_prescription(request):
    if request.method == "POST":
        form = PrescriptionUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.cleaned_data["file"]
            try:
                text = extract_text(uploaded_file)
                items = parse_prescription_text(text)
            except Exception:
                text = ""
                items = []
                messages.warning(
                    request,
                    "OCR is currently unavailable (Tesseract may not be installed on this server). "
                    "You can still add the prescription's medicines manually below.",
                )

            temp_name = f"tmp_ocr/{uuid.uuid4()}_{uploaded_file.name}"
            uploaded_file.seek(0)
            saved_path = default_storage.save(temp_name, ContentFile(uploaded_file.read()))

            request.session[SESSION_ITEMS_KEY] = items
            request.session[SESSION_TEMP_FILE_KEY] = saved_path
            request.session[SESSION_ORIGINAL_NAME_KEY] = uploaded_file.name

            if not items:
                messages.warning(
                    request, "OCR could not confidently extract any medicine lines. You can add them manually below."
                )
            return redirect("prescriptions:verify_upload")
    else:
        form = PrescriptionUploadForm()
    return render(request, "prescriptions/upload.html", {"form": form})


@role_required(User.Role.PATIENT)
def verify_upload(request):
    if SESSION_TEMP_FILE_KEY not in request.session:
        messages.error(request, "Please upload a prescription first.")
        return redirect("prescriptions:upload")

    items = request.session.get(SESSION_ITEMS_KEY, [])

    if request.method == "POST":
        formset = VerifyMedicineFormSet(request.POST)
        meta_form = VerifyPrescriptionMetaForm(request.POST)
        if formset.is_valid() and meta_form.is_valid():
            patient = _get_patient(request)
            prescription = Prescription.objects.create(
                doctor=meta_form.cleaned_data["doctor"],
                patient=patient,
                follow_up_date=meta_form.cleaned_data.get("follow_up_date"),
                status=Prescription.Status.ACTIVE,
                uploaded_by_patient=True,
            )

            temp_path = request.session.get(SESSION_TEMP_FILE_KEY)
            original_name = request.session.get(SESSION_ORIGINAL_NAME_KEY, "prescription")
            if temp_path and default_storage.exists(temp_path):
                with default_storage.open(temp_path, "rb") as f:
                    prescription.source_file.save(original_name, ContentFile(f.read()), save=True)
                default_storage.delete(temp_path)

            created_count = 0
            for item_form in formset:
                if not item_form.cleaned_data:
                    continue
                if not item_form.cleaned_data.get("include"):
                    continue
                medicine = item_form.cleaned_data.get("medicine")
                if not medicine:
                    continue
                PrescriptionMedicine.objects.create(
                    prescription=prescription,
                    medicine=medicine,
                    dosage=item_form.cleaned_data.get("dosage", ""),
                    frequency=item_form.cleaned_data.get("frequency", ""),
                    duration=item_form.cleaned_data.get("duration", ""),
                )
                created_count += 1

            for key in (SESSION_ITEMS_KEY, SESSION_TEMP_FILE_KEY, SESSION_ORIGINAL_NAME_KEY):
                request.session.pop(key, None)

            messages.success(request, f"Prescription saved with {created_count} medicine(s).")
            return redirect("prescriptions:detail", pk=prescription.pk)
    else:
        initial = [
            {
                "include": True,
                "raw_text": item.get("raw_text", ""),
                "medicine": item.get("medicine_id"),
                "dosage": item.get("dosage", ""),
                "frequency": item.get("frequency", ""),
                "duration": item.get("duration", ""),
            }
            for item in items
        ]
        formset = VerifyMedicineFormSet(initial=initial)
        meta_form = VerifyPrescriptionMetaForm()

    return render(
        request,
        "prescriptions/verify_upload.html",
        {"formset": formset, "meta_form": meta_form},
    )


@role_required(User.Role.DOCTOR)
def create_prescription(request, patient_id=None):
    doctor = _get_doctor(request)
    initial_meta = {"patient": patient_id} if patient_id else {}

    if request.method == "POST":
        meta_form = DoctorPrescriptionMetaForm(request.POST)
        formset = DoctorPrescriptionMedicineFormSet(request.POST)
        if meta_form.is_valid() and formset.is_valid():
            patient = meta_form.cleaned_data["patient"]
            prescription = Prescription.objects.create(
                doctor=doctor,
                patient=patient,
                follow_up_date=meta_form.cleaned_data.get("follow_up_date"),
                status=Prescription.Status.ACTIVE,
                uploaded_by_patient=False,
            )

            created_count = 0
            for item_form in formset:
                if not item_form.cleaned_data or item_form.cleaned_data.get("DELETE"):
                    continue
                medicine = item_form.cleaned_data.get("medicine")
                if not medicine:
                    continue
                PrescriptionMedicine.objects.create(
                    prescription=prescription,
                    medicine=medicine,
                    dosage=item_form.cleaned_data.get("dosage", ""),
                    frequency=item_form.cleaned_data.get("frequency", ""),
                    duration=item_form.cleaned_data.get("duration", ""),
                )
                created_count += 1

            DoctorPatientLink.objects.get_or_create(doctor=doctor, patient=patient)

            messages.success(request, f"Prescription created with {created_count} medicine(s).")
            return redirect("prescriptions:detail", pk=prescription.pk)
    else:
        meta_form = DoctorPrescriptionMetaForm(initial=initial_meta)
        formset = DoctorPrescriptionMedicineFormSet()

    return render(
        request,
        "prescriptions/create.html",
        {"meta_form": meta_form, "formset": formset},
    )


@role_required(User.Role.DOCTOR, User.Role.PATIENT, User.Role.ADMIN)
def prescription_list(request):
    if request.user.role == User.Role.DOCTOR:
        doctor = _get_doctor(request)
        prescriptions = Prescription.objects.filter(doctor=doctor)
    elif request.user.role == User.Role.PATIENT:
        patient = _get_patient(request)
        prescriptions = Prescription.objects.filter(patient=patient)
    else:
        prescriptions = Prescription.objects.all()
    prescriptions = prescriptions.select_related("doctor", "patient").prefetch_related("items__medicine")
    return render(request, "prescriptions/list.html", {"prescriptions": prescriptions})


@role_required(User.Role.DOCTOR, User.Role.PATIENT, User.Role.ADMIN)
def prescription_detail(request, pk):
    prescription = get_object_or_404(
        Prescription.objects.select_related("doctor", "patient").prefetch_related("items__medicine"), pk=pk
    )
    if not _can_view_prescription(request.user, prescription):
        raise Http404
    status_form = None
    if request.user.role == User.Role.DOCTOR and prescription.doctor.user_id == request.user.pk:
        if request.method == "POST":
            status_form = PrescriptionStatusForm(request.POST, instance=prescription)
            if status_form.is_valid():
                status_form.save()
                messages.success(request, "Status updated.")
                return redirect("prescriptions:detail", pk=pk)
        else:
            status_form = PrescriptionStatusForm(instance=prescription)
    return render(
        request, "prescriptions/detail.html", {"prescription": prescription, "status_form": status_form}
    )


@role_required(User.Role.DOCTOR, User.Role.PATIENT, User.Role.ADMIN)
def prescription_print(request, pk):
    prescription = get_object_or_404(
        Prescription.objects.select_related("doctor", "patient").prefetch_related("items__medicine"), pk=pk
    )
    if not _can_view_prescription(request.user, prescription):
        raise Http404
    return render(request, "prescriptions/print.html", {"prescription": prescription})


@role_required(User.Role.DOCTOR, User.Role.PATIENT, User.Role.ADMIN)
def prescription_download(request, pk):
    prescription = get_object_or_404(
        Prescription.objects.select_related("doctor", "patient").prefetch_related("items__medicine"), pk=pk
    )
    if not _can_view_prescription(request.user, prescription):
        raise Http404

    from xhtml2pdf import pisa

    html = render_to_string("prescriptions/pdf.html", {"prescription": prescription})
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="prescription_{prescription.pk}.pdf"'
    pisa.CreatePDF(src=html, dest=response)
    return response

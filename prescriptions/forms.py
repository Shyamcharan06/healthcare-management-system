from django import forms
from django.forms import formset_factory

from doctors.models import Doctor
from medications.models import Medicine
from prescriptions.models import Prescription


class PrescriptionUploadForm(forms.Form):
    file = forms.FileField(help_text="Upload a prescription image (JPG/PNG) or PDF.")


class VerifyMedicineItemForm(forms.Form):
    include = forms.BooleanField(required=False, initial=True)
    raw_text = forms.CharField(required=False, widget=forms.HiddenInput)
    medicine = forms.ModelChoiceField(queryset=Medicine.objects.all(), required=False)
    dosage = forms.CharField(max_length=100, required=False)
    frequency = forms.CharField(max_length=100, required=False)
    duration = forms.CharField(max_length=100, required=False)


VerifyMedicineFormSet = formset_factory(VerifyMedicineItemForm, extra=1, can_delete=False)


class VerifyPrescriptionMetaForm(forms.Form):
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.select_related("hospital"), required=True)
    follow_up_date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))


class DoctorPrescriptionMedicineForm(forms.Form):
    medicine = forms.ModelChoiceField(queryset=Medicine.objects.all())
    dosage = forms.CharField(max_length=100, required=False)
    frequency = forms.CharField(max_length=100, required=False)
    duration = forms.CharField(max_length=100, required=False)


DoctorPrescriptionMedicineFormSet = formset_factory(
    DoctorPrescriptionMedicineForm, extra=1, can_delete=True
)


class DoctorPrescriptionMetaForm(forms.Form):
    patient = forms.ModelChoiceField(queryset=None)
    follow_up_date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))

    def __init__(self, *args, **kwargs):
        from patients.models import Patient

        super().__init__(*args, **kwargs)
        self.fields["patient"].queryset = Patient.objects.all().order_by("name")


class PrescriptionStatusForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ["status"]

from django import forms

from patients.models import Patient


class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ["name", "dob", "contact"]
        widgets = {"dob": forms.DateInput(attrs={"type": "date"})}

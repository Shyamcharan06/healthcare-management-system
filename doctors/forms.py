from django import forms

from doctors.models import Doctor, ConsultationNote


class ConsultationNoteForm(forms.ModelForm):
    class Meta:
        model = ConsultationNote
        fields = ["consultation_date", "diagnosis", "symptoms", "notes", "follow_up_date"]
        widgets = {
            "consultation_date": forms.DateInput(attrs={"type": "date"}),
            "follow_up_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 4}),
        }


class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ["name", "specialization", "experience", "contact"]

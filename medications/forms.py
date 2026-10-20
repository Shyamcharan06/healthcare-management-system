from django import forms

from medications.models import Medicine, MedicationReminder


class MedicineLookupForm(forms.Form):
    medicines = forms.ModelMultipleChoiceField(
        queryset=Medicine.objects.all(),
        widget=forms.SelectMultiple(attrs={"size": 8}),
        help_text="Select one or more medicines to view info and check interactions.",
    )


class MedicationReminderForm(forms.ModelForm):
    class Meta:
        model = MedicationReminder
        fields = ["medicine", "scheduled_date", "time"]
        widgets = {
            "scheduled_date": forms.DateInput(attrs={"type": "date"}),
            "time": forms.TimeInput(attrs={"type": "time"}),
        }

    def __init__(self, *args, patient=None, **kwargs):
        super().__init__(*args, **kwargs)
        if patient is not None:
            from prescriptions.models import Prescription

            self.fields["medicine"].queryset = Medicine.objects.filter(
                prescription_items__prescription__patient=patient,
                prescription_items__prescription__status=Prescription.Status.ACTIVE,
            ).distinct()

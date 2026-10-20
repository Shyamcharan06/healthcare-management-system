from django import forms

from hospitals.models import Hospital, Department


class HospitalForm(forms.ModelForm):
    class Meta:
        model = Hospital
        fields = ["name", "address", "phone"]


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ["hospital", "name"]

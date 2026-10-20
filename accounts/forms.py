from django import forms
from django.contrib.auth.forms import AuthenticationForm

from accounts.models import User
from hospitals.models import Hospital, Department


class RoleLoginForm(AuthenticationForm):
    role = forms.ChoiceField(choices=User.Role.choices)

    field_order = ["role", "username", "password"]

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        if self.user_cache is not None and role and self.user_cache.role != role:
            raise forms.ValidationError(
                "The selected role does not match this account. Please choose the correct role."
            )
        return cleaned_data


class AdminAccountForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField(required=False)
    password = forms.CharField(widget=forms.PasswordInput)
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("A user with that username already exists.")
        return username


class DoctorAccountForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField(required=False)
    password = forms.CharField(widget=forms.PasswordInput)
    name = forms.CharField(max_length=150)
    specialization = forms.CharField(max_length=150, required=False)
    experience = forms.IntegerField(min_value=0, initial=0)
    contact = forms.CharField(max_length=100, required=False)
    hospital = forms.ModelChoiceField(queryset=Hospital.objects.all(), required=False)
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False)

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("A user with that username already exists.")
        return username


class PatientAccountForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField(required=False)
    password = forms.CharField(widget=forms.PasswordInput)
    name = forms.CharField(max_length=150)
    dob = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    contact = forms.CharField(max_length=100, required=False)

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("A user with that username already exists.")
        return username

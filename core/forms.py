from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import CandidateSkill, Job, Application, UserProfile


class CandidateSkillForm(forms.ModelForm):
    class Meta:
        model = CandidateSkill
        fields = ["skill"]


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ["title", "description", "location"]


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = []


class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ["username", "email", "role", "password1", "password2"]
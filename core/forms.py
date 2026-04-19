from django import forms
from .models import CandidateSkill, Job, Application


class CandidateSkillForm(forms.ModelForm):
    class Meta:
        model = CandidateSkill
        fields = ["candidate", "skill"]


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ["employer", "title", "description", "location"]


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["candidate", "job", "status"]
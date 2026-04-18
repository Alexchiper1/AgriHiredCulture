from django import forms
from .models import CandidateSkill, Skill


class CandidateSkillForm(forms.ModelForm):
    class Meta:
        model = CandidateSkill
        fields = ["candidate", "skill"]
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("skills/add/", views.add_candidate_skill, name="add_candidate_skill"),
    path("skills/", views.skill_list, name="skill_list"),
]
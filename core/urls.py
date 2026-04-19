from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("skills/add/", views.add_candidate_skill, name="add_candidate_skill"),
    path("skills/", views.skill_list, name="skill_list"),
    path("jobs/add/", views.add_job, name="add_job"),
    path("jobs/", views.job_list, name="job_list"),
    path("applications/add/", views.add_application, name="add_application"),
    path("applications/", views.application_list, name="application_list"),
]
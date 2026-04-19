from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="core/login.html"), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("skills/add/", views.add_candidate_skill, name="add_candidate_skill"),
    path("skills/", views.skill_list, name="skill_list"),
    path("jobs/add/", views.add_job, name="add_job"),
    path("jobs/", views.job_list, name="job_list"),
    path("applications/add/", views.add_application, name="add_application"),
    path("applications/", views.application_list, name="application_list"),
]
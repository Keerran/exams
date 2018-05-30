"""exams URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

from app import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", auth_views.login, name="login"),
    path("logout/", auth_views.logout, name="logout"),
    path("signup/", views.Signup.as_view(), name="signup"),
    path("", views.home, name="home"),
    path("addexam/", views.AddExam.as_view(), name="addexam"),
    path("addsubject/", views.AddSubject.as_view(), name="addsubject"),
    path("update/subject/", views.UpdateSubject.as_view(), name="updatesubject"),
    path("delete/subject/", views.DeleteSubject.as_view(), name="deletesubject"),
    path("update/exam/", views.UpdateExam.as_view(), name="updateexam"),
    path("delete/exam/", views.DeleteExam.as_view(), name="deleteexam"),
    path("timetable/", views.Timetable.as_view(), name="timetable"),
    path("tests/", views.Tests.as_view(), name="tests"),
    path("tests/<slug:slug>/", views.SubjectTests.as_view(), name="subject"),
    path("tests/exams/<slug:slug>", views.ExamTests.as_view(), name="exam"),
    path("tests/delete", views.DeleteTest.as_view(), name="delete_test"),
    path("subjectlist", views.SubjectList.as_view(), name="subjects"),
    path("test/", views.AdminTest.as_view(), name="test"),
]

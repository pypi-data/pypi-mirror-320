# github_issue_reporter/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('report-issue/', views.report_issue, name='report_issue'),
]

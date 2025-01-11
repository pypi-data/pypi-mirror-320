# github_issue_reporter/views.py

from django.shortcuts import render, redirect
from django.http import HttpResponse
import requests
from django.conf import settings

def report_issue(request):
    if request.method == 'POST':
        issue_title = request.POST.get('title')
        issue_body = request.POST.get('body')

        # Access settings for GitHub repo details
        github_repo_name = settings.GITHUB_REPO_NAME
        github_token = settings.GITHUB_API_TOKEN
        github_user = settings.GITHUB_USER
        github_repo_name = settings.GITHUB_REPO_NAME
        github_token = settings.GITHUB_API_TOKEN
        github_user = settings.GITHUB_USER
        
        # URL to create an issue in GitHub
        url = f"https://api.github.com/repos/{github_user}/{github_repo_name}/issues"
        
        headers = {
            'Authorization': f'Bearer {github_token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
        }
        payload = {
            'title': issue_title,
            'body': issue_body,
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 201:
            return HttpResponse("Issue reported successfully!")
        else:
            return HttpResponse(f"Failed to report issue: {response.status_code} - {response.json()}")

    return render(request, 'git_issue_reporter/report_issue.html')

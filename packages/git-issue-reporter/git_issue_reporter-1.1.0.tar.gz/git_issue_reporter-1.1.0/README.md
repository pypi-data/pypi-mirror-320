# GitHub Issue Reporter

**GitHub Issue Reporter** is a Django module that enables users to create and submit issues directly to a GitHub repository from a Django web application.

---

## Installation

1. Install the package using pip:
   ```bash
   pip install github-issue-reporter
   ```

2. Add the module to your Django project's `INSTALLED_APPS` in `settings.py`:
   ```python
   INSTALLED_APPS = [
       ...,
       'github_issue_reporter',
   ]
   ```

---

## Configuration

Add the following configuration settings to your `settings.py` file:

```python
GITHUB_REPO_NAME = "repo_name_without_extension"  # Replace with your repository name
GITHUB_USER = "github_username"    # Replace with your GitHub username
GITHUB_API_TOKEN = "github_api_token"  # Replace with your GitHub API token
```

### Notes:
- **`GITHUB_REPO_NAME`**: This is the name of your GitHub repository.
- **`GITHUB_USER`**: Your GitHub username.
- **`GITHUB_API_TOKEN`**: A personal access token generated from GitHub. (See [GitHub Personal Access Tokens](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token))

---

## Usage

### URL Configuration
At the project level, include `github_issue_reporter.urls` in your `urls.py` file:

```python
from django.urls import path, include

urlpatterns = [
    ...,
    path('module/', include('github_issue_reporter.urls')),
]
```

### Accessing the Issue Reporter
Once the module is included, you can access the issue reporting page by visiting:
```
http://<your-domain>/module/report-issue/
```

---

## Features
- **GitHub Integration**: Submit issues directly to your repository’s issue tracker.
- **Simple Setup**: Configure and start using the module with minimal effort.
- **Django Templating**: Customize the provided HTML templates to suit your application.

---

## Customization
You can override the default template `report_issue.html` by creating a custom version in your project. Place the custom template at the following path:
```
<your_app>/templates/github_issue_reporter/report_issue.html
```



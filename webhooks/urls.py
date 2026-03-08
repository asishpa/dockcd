from django.urls import path
from .views import github_webhook, CreateGitHubWebhookView


urlpatterns = [
    path(
        "github/",
        CreateGitHubWebhookView.as_view(),
        name="create-github-webhook"
    ),
    path("github/events/", github_webhook, name="github-webhook"),
]
from django.urls import path
from .views import github_webhook, CreateGitHubWebhookView, EditGitHubWebhookSecretView


urlpatterns = [
    path(
        "github/",
        CreateGitHubWebhookView.as_view(),
        name="create-github-webhook"
    ),
    path(
        "github/edit-secret/",
        EditGitHubWebhookSecretView.as_view(),
        name="edit-github-webhook-secret"
    ),
    path("github/events/", github_webhook, name="github-webhook"),
]
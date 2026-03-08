import uuid
from django.db import models
from applications.models import Application

class GitHubWebhook(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    application = models.OneToOneField(
        Application,
        on_delete=models.CASCADE,
        related_name="github_webhook"
    )

    secret = models.CharField(
        max_length=255,
        help_text="GitHub webhook secret for signature verification"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Webhook for {self.application.name}"
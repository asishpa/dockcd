import uuid
from django.db import models
from applications.models import Application

class Service(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=100)

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="services"
    )

    compose_file_path = models.CharField(
        max_length=255,
        help_text="Relative path to docker-compose file inside repo"
    )

    deploy_path = models.CharField(
        max_length=255,
        help_text="Absolute path on this server where repo is cloned"
    )

    auto_deploy = models.BooleanField(
        default=True,
        help_text="Deploy automatically on GitHub webhook"
    )
    deploy_order = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("application", "name")

    def __str__(self):
        return f"{self.application.name} :: {self.name}"
class AllowedCommands(models.Model):
    command = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.command
import uuid
from django.db import models
from services.models import Service

class Deployment(models.Model):
    STATUS_PENDING = "pending"
    STATUS_RUNNING = "running"
    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"
    STATUS_QUEUED = "queued"
    STATUS_SUPERSEDED = "superseded"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_RUNNING, "Running"),
        (STATUS_SUCCESS, "Success"),
        (STATUS_FAILED, "Failed"),
        (STATUS_QUEUED, "Queued"),
        (STATUS_SUPERSEDED, "Superseded"),
    ]
    application = models.ForeignKey("applications.Application", on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    commit_sha = models.CharField(
        max_length=64,
        blank=True,
        help_text="Git commit SHA that triggered this deployment"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )

    logs = models.TextField(blank=True)

    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.application.name} [{self.status}]"

class ServiceDeployment(models.Model):
    STATUS_PENDING = "pending"
    STATUS_QUEUEUED = "queued"
    STATUS_RUNNING = "running"
    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"

    deployment = models.ForeignKey(Deployment, on_delete=models.CASCADE, related_name="service_deployments")
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        default=STATUS_PENDING
    )
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
from django.db import models
import uuid
# Create your models here.

class Application(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=100, unique=True)
    repo_url = models.URLField(help_text="Git repository URL")
    branch = models.CharField(max_length=100, default="main")
    deploy_path = models.CharField(max_length=255, default="/opt/dockcd/apps")
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

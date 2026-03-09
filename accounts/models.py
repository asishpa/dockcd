from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    ROLE_ADMIN = "admin"
    ROLE_DEVELOPER = "developer"
    ROLE_VIEWER = "viewer"

    ROLE_CHOICES = [
        (ROLE_ADMIN, "Admin"),
        (ROLE_DEVELOPER, "Developer"),
        (ROLE_VIEWER, "Viewer"),
    ]
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_VIEWER
    )
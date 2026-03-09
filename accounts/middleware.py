from django.http import JsonResponse
from accounts.models import User

class AdminBootstrapMIddleware:
    ALLOWED_PATHS = [
        "/api/v1/accounts/bootstrap-admin/",
        "/api/v1/accounts/setup-status/"
        "/api/v1/accounts/login/"
        "/admin/"
    ]
    
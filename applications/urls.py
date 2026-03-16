from django.urls import path
from .views import ApplicationServiceStatusView, RegisterApplicationView

urlpatterns = [
    path(
        "register/",
        RegisterApplicationView.as_view(),
        name="register-application"
    ),
    path(
        "<uuid:application_id>/services/status/",
        ApplicationServiceStatusView.as_view(),
        name="application-service-status"
    )
]
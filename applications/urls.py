from django.urls import path
from .views import ApplicationListView, ApplicationServiceStatusView, RegisterApplicationView, DeleteApplicationView

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
    ),
    path("", ApplicationListView.as_view(), name="application-list"),
    path(
        "<uuid:application_id>/delete/",
        DeleteApplicationView.as_view(),
        name="delete-application"
    )
]
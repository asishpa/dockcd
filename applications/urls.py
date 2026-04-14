from django.urls import path
from .views import ApplicationListView, ApplicationServiceStatusView, RegisterApplicationView, DeleteApplicationView, SyncApplicationView, UpdateServiceDeployOrderView

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
    ),
    path(
    "<uuid:application_id>/services/deploy-order/",
    UpdateServiceDeployOrderView.as_view(),
),path(
    "applications/<uuid:application_id>/sync/",
    SyncApplicationView.as_view(),
)
]
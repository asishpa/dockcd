from django.urls import path
from .views import (
    TriggerDeploymentView,
    ApplicationDeploymentListView,
    DeploymentLogsView,
    ServiceDeploymentListView,
)

urlpatterns = [
    path(
        "trigger/",
        TriggerDeploymentView.as_view(),
        name="trigger-deployment"
    ),
    path(
        "applications/",
        ApplicationDeploymentListView.as_view(),
        name="application-deployment-list",
    ),
    path(
        "logs/",
        DeploymentLogsView.as_view(),
        name="deployment-logs",
    ),
    path(
        "services/",
        ServiceDeploymentListView.as_view(),
        name="service-deployment-list",
    ),
]
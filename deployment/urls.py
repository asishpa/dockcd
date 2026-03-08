from django.urls import path
from .views import TriggerDeploymentView

urlpatterns = [
    path(
        "trigger/",
        TriggerDeploymentView.as_view(),
        name="trigger-deployment"
    ),
]
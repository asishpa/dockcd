from django.urls import re_path
from deployment.consumer import DeploymentConsumer

print("Deployment routing loaded")
websocket_urlpatterns = [
    re_path(
        r"ws/deployments/(?P<deployment_id>[0-9a-f-]+)/logs/",
        DeploymentConsumer.as_asgi(),
    ),
]
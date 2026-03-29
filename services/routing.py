from django.urls import re_path
from services.consumers import ContainerLogsConsumer, ServiceExecConsumer

websocket_urlpatterns = [
    re_path(r'ws/containers/(?P<container_name>[^/]+)/exec/$', ServiceExecConsumer.as_asgi()),
    re_path(r'ws/containers/(?P<container_name>[^/]+)/logs/$', ContainerLogsConsumer.as_asgi()),
]
from django.urls import re_path
from services.consumers import ServiceExecConsumer

websocket_urlpatterns = [
    re_path(r'ws/services/(?P<service_id>\d+)/exec/$', ServiceExecConsumer.as_asgi()),
]
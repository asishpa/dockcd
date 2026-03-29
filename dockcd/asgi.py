import os
import django

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from deployment.routing import websocket_urlpatterns as deployment_websocket_urlpatterns
from services.routing import websocket_urlpatterns as services_websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dockcd.settings')
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": URLRouter(
        deployment_websocket_urlpatterns + services_websocket_urlpatterns
    ),
})
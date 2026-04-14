import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dockcd.settings")
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from common.jwt_middleware import JWTAuthMiddleware
from deployment.routing import websocket_urlpatterns as deployment_websocket_urlpatterns
from services.routing import websocket_urlpatterns as services_websocket_urlpatterns


application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": JWTAuthMiddleware(
        URLRouter(
            deployment_websocket_urlpatterns + services_websocket_urlpatterns
        )
    ),
})
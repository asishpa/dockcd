from urllib.parse import parse_qs
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
import logging
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken

logger = logging.getLogger(__name__)

class JWTAuthMiddleware:
    def __init__(self, app):
        self.app = app
        self.jwt_auth = JWTAuthentication()

    async def __call__(self, scope, receive, send):
        logger.info("JWT middleware triggered")

        scope["user"] = AnonymousUser()

        query_string = scope.get("query_string", b"").decode()
        query_params = parse_qs(query_string)

        token = query_params.get("token")

        if token:
            token = token[0]

            try:
                validated_token = self.jwt_auth.get_validated_token(token)
                user = await self.get_user(validated_token)

                logger.info(f"Authenticated user '{user}' via WebSocket")

                scope["user"] = user

            except InvalidToken:
                logger.warning("Invalid JWT token")

        return await self.app(scope, receive, send)

    @database_sync_to_async
    def get_user(self, validated_token):
        return self.jwt_auth.get_user(validated_token)
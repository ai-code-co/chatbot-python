import jwt
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()


@database_sync_to_async
def get_user_from_token(token):
    try:
        payload = jwt.decode(
            token,
            settings.SIMPLE_JWT["SIGNING_KEY"],
            algorithms=["HS256"]
        )
        user_id = payload.get("user_id")
        return User.objects.get(id=user_id)
    except Exception:
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # Read the token from query string
        query_string = scope.get("query_string", b"").decode()

        token = None
        if "token=" in query_string:
            token = query_string.split("token=")[1]

        # Set authenticated user in scope
        scope["user"] = await get_user_from_token(token) if token else AnonymousUser()

        return await super().__call__(scope, receive, send)

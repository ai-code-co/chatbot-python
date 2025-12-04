import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from chat import routing as api_routing
import django

# from chat.middleware import JWTAuthMiddleware
# from chat.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    #  "websocket": JWTAuthMiddleware(
    #     URLRouter(websocket_urlpatterns)
    # )

    # this is earlier to jwt auth
    "websocket": AuthMiddlewareStack(
        URLRouter(
            api_routing.websocket_urlpatterns
        )
    ),
})





import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sopdisplay_core.settings")
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path, re_path
from screen_app.routing import websocket_urlpatterns
from screen_app import consumers

django_asgi_app = get_asgi_application()

http_patterns = [
    path("station/<int:station_id>/updates/", consumers.MediaUpdatesConsumer.as_asgi()),
    path("station/stream/video/<path:file_path>/", consumers.StreamVideoConsumer.as_asgi()),
    path("station/stream/pdf/<path:file_path>/", consumers.StreamPDFConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "http": URLRouter([
        *http_patterns,
        re_path(r"", django_asgi_app),
    ]),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
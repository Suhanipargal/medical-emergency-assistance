from django.urls import re_path
from emergency import consumers

websocket_urlpatterns = [
    re_path(r'ws/alerts/$', consumers.AlertConsumer.as_asgi()),
]

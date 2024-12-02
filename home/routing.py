# routing.py
from django.urls import re_path
from . import consumers

# websocket_urlpatterns = [
#     re_path(r'ws/hive/socket-server/', consumers.Chat_Consumer.as_asgi()),
# ]

websocket_urlpatterns = [
    re_path(r'ws/hive/(?P<hive_id>\w+)/$', consumers.HiveChatConsumer.as_asgi()),
    re_path(r"ws/", consumers.HomepageConsumer.as_asgi()),  # Default WebSocket route for homepage
]



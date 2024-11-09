# chat/consumers.py
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Message, Hive  # Import Message and Hive models


class HiveChatConsumer(WebsocketConsumer):
    def connect(self):
        # Retrieve hive ID from URL route
        self.hive_id = self.scope["url_route"]["kwargs"]["hive_id"]
        self.hive_group_name = f"hive_{self.hive_id}"  # Group name specific to the hive

        # Join the hive group
        async_to_sync(self.channel_layer.group_add)(
            self.hive_group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave the hive group
        async_to_sync(self.channel_layer.group_discard)(
            self.hive_group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        # Decode message data from WebSocket
        text_data_json = json.loads(text_data)
        message_content = text_data_json["message"]

        # Send message to the hive group
        hive = Hive.objects.get(id=self.hive_id)
        message = Message.objects.create(
            user=self.scope["user"],  # Assumes user is authenticated
            hive=hive,
            body=message_content
        )
        
        async_to_sync(self.channel_layer.group_send)(
            self.hive_group_name, {
                "type": "hive_message",  # Method called when group message is received
                "message": message.body,
                "username": message.user.username,
                "timestamp": message.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    # Receive message from the hive group
    def hive_message(self, event):
        message = event["message"]
        username = event["username"]
        timestamp = event["timestamp"]

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            "message": message,
            "username": username,
            "timestamp": timestamp,
        }))

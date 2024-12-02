# chat/consumers.py
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Message, Hive, Highscore  # Import Message and Hive models
import base64
from django.core.files.base import ContentFile
from home.utils import load_spam_words


class HiveChatConsumer(WebsocketConsumer):
    def connect(self):
        self.hive_id = self.scope["url_route"]["kwargs"]["hive_id"]
        self.hive_group_name = f"hive_{self.hive_id}"
        async_to_sync(self.channel_layer.group_add)(
            self.hive_group_name,
            self.channel_name,
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.hive_group_name,
            self.channel_name,
        )

    # def receive(self, text_data):
    #     data = json.loads(text_data)
    #     message_content = data.get("message", "")
    #     file_data = data.get("file", None)
    #     hive = Hive.objects.get(id=self.hive_id)
    #     user = self.scope["user"]

    #     file = None
    #     if file_data:
    #         # Handle Base64-encoded file
    #         format, file_str = file_data.split(";base64,")
    #         ext = format.split("/")[-1]
    #         file = ContentFile(base64.b64decode(file_str), name=f"{user.username}_upload.{ext}")

    #     # Save the message to the database
    #     message = Message.objects.create(
    #         user=user,
    #         hive=hive,
    #         body=message_content,
    #         file=file,
    #     )

    #     async_to_sync(self.channel_layer.group_send)(
    #         self.hive_group_name,
    #         {
    #             "type": "hive_message",
    #             "message": message.body,
    #             "username": user.username,
    #             "file_url": message.file.url if message.file else None,
    #         },
    #     )

    def receive(self, text_data):
        data = json.loads(text_data)
        message_content = data.get("message", "").lower()
        file_data = data.get("file", None)
        hive = Hive.objects.get(id=self.hive_id)
        user = self.scope["user"]

        # Load spam words
        spam_words = load_spam_words()

        
        # Check for offensive content
        if any(spam_word in message_content for spam_word in spam_words):
            # Send a warning back to the user
            self.send(text_data=json.dumps({
                "type": "warning",
                "message": "Your message contains offensive words and cannot be sent."
            }))
            return  # Prevent further processing of the message
        
        action = data.get("action", "")

        if action == "kick":
            kicked_user_id = data.get("user_id")
            if self.scope["user"].id == kicked_user_id:
                self.close()
            return

        # Handle high score submission
        if action == "submit_score":
            score = data.get("score")
            if score is not None:
                # Check if there's an existing high score for the user in this hive
                highscore, created = Highscore.objects.get_or_create(hive=hive, user=user)

                # If the score is higher than the existing high score, update it
                if score > highscore.score:
                    highscore.score = score
                    highscore.save()

                    # Broadcast the updated high score to the Hive group
                    async_to_sync(self.channel_layer.group_send)(
                        self.hive_group_name,
                        {
                            "type": "update_highscore",
                            "username": user.username,
                            "score": highscore.score,
                        }
                    )
                else:
                    # Send a message if the score was not high enough to beat the current score
                    self.send(text_data=json.dumps({
                        "type": "info",
                        "message": "Your score is lower than the current high score."
                    }))

            return  # Prevent further processing for the score submission

        # Handle game over (when the game ends)
        if action == "game_over":
            # Send the game over message with the redirect URL
            self.send(text_data=json.dumps({
                "type": "game_over",
                "message": "The game has ended. Redirecting you back to the hive.",
                "redirect_to": f"/hive/{self.hive_id}/"  # Redirect to the hive page
            }))
            return

        file = None
        if file_data:
            # Handle Base64-encoded file
            try:
                format, file_str = file_data.split(";base64,")
                ext = format.split("/")[-1]
                file = ContentFile(base64.b64decode(file_str), name=f"{user.username}_upload.{ext}")
            except Exception as e:
                self.send(text_data=json.dumps({
                    "type": "error",
                    "message": f"Failed to process the file: {str(e)}"
                }))
                return

        # Save the message to the database
        message = Message.objects.create(
            user=user,
            hive=hive,
            body=message_content,
            file=file,
        )

        # Broadcast the message to the group
        async_to_sync(self.channel_layer.group_send)(
            self.hive_group_name,
            {
                "type": "hive_message",
                "message": message.body,
                "username": user.username,
                "file_url": message.file.url if message.file else None,
            },
        )
        
        
    def hive_message(self, event):
        self.send(text_data=json.dumps({
            "message": event["message"],
            "username": event["username"],
            "file_url": event["file_url"],
        }))

    # New method to broadcast updated high scores
    def update_highscore(self, event):
        self.send(text_data=json.dumps({
            "type": "highscore_update",
            "username": event["username"],
            "score": event["score"],
        }))
        


class SnakeGameConsumer(WebsocketConsumer):
    async def connect(self):
        # Handle WebSocket connection
        self.hive_id = self.scope['url_route']['kwargs']['hive_id']
        self.room_group_name = f'hive_{self.hive_id}_game'

        # Join the group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Handle messages (e.g., game over, score updates)
        data = json.loads(text_data)
        if data['type'] == 'game_over':
            # Broadcast the game over event with the redirect URL
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_over',
                    'redirect_to': f'/hive/{self.hive_id}/'
                }
            )
    
    # Method to handle game over message
    async def game_over(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_over',
            'message': 'Game Over!',
            'redirect_to': event['redirect_to']
        }))


# class HiveChatConsumer(WebsocketConsumer):
#     def connect(self):
#         self.hive_id = self.scope["url_route"]["kwargs"]["hive_id"]
#         self.hive_group_name = f"hive_{self.hive_id}"
#         async_to_sync(self.channel_layer.group_add)(
#             self.hive_group_name, self.channel_name
#         )
#         self.accept()

#     def disconnect(self, close_code):
#         async_to_sync(self.channel_layer.group_discard)(
#             self.hive_group_name, self.channel_name
#         )

#     def receive(self, text_data):
#         data = json.loads(text_data)
#         hive = Hive.objects.get(id=self.hive_id)
#         user = self.scope["user"]

#         # Add the user to the hive's members
#         if user not in hive.members.all():
#             hive.members.add(user)

#         # Handle file uploads
#         file = None
#         if "file" in data:
#             file_data = data["file"].split(";base64,")[1]
#             file_name = f"{user.username}_upload"
#             file = ContentFile(base64.b64decode(file_data), name=file_name)

#         # Save the message or file
#         message = Message.objects.create(
#             user=user,
#             hive=hive,
#             body=data.get("message", ""),
#             file=file
#         )

#         # Broadcast the message
#         async_to_sync(self.channel_layer.group_send)(
#             self.hive_group_name, {
#                 "type": "hive_message",
#                 "message": message.body,
#                 "file_url": message.file.url if message.file else None,
#                 "username": message.user.username,
#                 "timestamp": message.created_at.strftime("%Y-%m-%d %H:%M:%S"),
#             }
#         )

#     def hive_message(self, event):
#         self.send(text_data=json.dumps({
#             "message": event["message"],
#             "file_url": event["file_url"],
#             "username": event["username"],
#             "timestamp": event["timestamp"],
#         }))
# class HiveChatConsumer(WebsocketConsumer):
#     def connect(self):
#         self.hive_id = self.scope["url_route"]["kwargs"]["hive_id"]
#         self.hive_group_name = f"hive_{self.hive_id}"
#         self.notification_group_name = f"notifications_{self.hive_id}"

#         # Join the chat group
#         async_to_sync(self.channel_layer.group_add)(
#             self.hive_group_name, self.channel_name
#         )

#         # Join the notification group
#         async_to_sync(self.channel_layer.group_add)(
#             self.notification_group_name, self.channel_name
#         )

#         self.accept()

#     def disconnect(self, close_code):
#         # Leave the chat group
#         async_to_sync(self.channel_layer.group_discard)(
#             self.hive_group_name, self.channel_name
#         )

#         # Leave the notification group
#         async_to_sync(self.channel_layer.group_discard)(
#             self.notification_group_name, self.channel_name
#         )

#     def receive(self, text_data):
#         data = json.loads(text_data)
#         message_content = data["message"]

#         # Save the message to the database
#         hive = Hive.objects.get(id=self.hive_id)
#         message = Message.objects.create(
#             user=self.scope["user"], hive=hive, body=message_content
#         )

#         # Send message to the chat group
#         async_to_sync(self.channel_layer.group_send)(
#             self.hive_group_name,
#             {
#                 "type": "hive_message",
#                 "message": message.body,
#                 "username": message.user.username,
#                 "timestamp": message.created_at.strftime("%Y-%m-%d %H:%M:%S"),
#             },
#         )

#         # Send notification to the notification group
#         async_to_sync(self.channel_layer.group_send)(
#             self.notification_group_name,
#             {
#                 "type": "send_notification",
#                 "message": f"{message.user.username} sent a new message.",
#                 "username": message.user.username,
#             },
#         )

#     def hive_message(self, event):
#         # Send the message to WebSocket
#         self.send(text_data=json.dumps({
#             "message": event["message"],
#             "username": event["username"],
#             "timestamp": event["timestamp"],
#         }))

#     def send_notification(self, event):
#         # Send the notification to WebSocket
#         self.send(text_data=json.dumps({
#             "type": "notification",
#             "message": event["message"],
#             "username": event["username"],
#         }))



class HomepageConsumer(WebsocketConsumer):
    def connect(self):
        # You can add group add logic here if you want all homepage users to join a group
        self.accept()

    def disconnect(self, close_code):
        # Handle disconnection if necessary
        pass

    def receive(self, text_data):
        # This is just a placeholder for any data sent to the homepage WebSocket
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message', 'No message provided')

        # Echo message back to WebSocket client
        self.send(text_data=json.dumps({
            'message': f"Received on homepage: {message}"
        }))



# class NotificationConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         # Group name for notifications for the specific hive
#         self.hive_id = self.scope["url_route"]["kwargs"]["hive_id"]
#         self.notification_group_name = f"notifications_{self.hive_id}"
        
#         # Add to notification group
#         await self.channel_layer.group_add(
#             self.notification_group_name, 
#             self.channel_name
#         )
#         await self.accept()

#     async def disconnect(self, close_code):
#         # Remove from notification group
#         await self.channel_layer.group_discard(
#             self.notification_group_name, 
#             self.channel_name
#         )

#     # Called when a new notification is received
#     async def send_notification(self, event):
#         message = event["message"]
#         sender = event["sender"]
        
#         # Send notification to WebSocket
#         await self.send(text_data=json.dumps({
#             "type": "notification",
#             "message": message,
#             "sender": sender
#         }))
# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from channels.generic.websocket import WebsocketConsumer

# class Chat_Consumer(WebsocketConsumer):
#     def connect(self):
#         self.accept()
        
#         self.send(text_data=json.dumps(
#             {
#                 'type':'connection_established',
#                 'message':"Connected"
#             }
#         ))

# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.hive_id = self.scope['url_route']['kwargs']['hive_id']
#         self.hive_group_name = f'hive_{self.hive_id}'

#         await self.channel_layer.group_add(
#             self.hive_group_name,
#             self.channel_name
#         )

#         await self.accept()

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(
#             self.hive_group_name,
#             self.channel_name
#         )

#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         message = data['message']

#         await self.channel_layer.group_send(
#             self.hive_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message
#             }
#         )

#     async def chat_message(self, event):
#         message = event['message']

#         await self.send(text_data=json.dumps({
#             'message': message
#         }))


# class NotificationConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.hive_id = self.scope['url_route']['kwargs']['hive_id']
#         self.hive_group_name = f'hive_{self.hive_id}'

#         # Join the hive group
#         await self.channel_layer.group_add(
#             self.hive_group_name,
#             self.channel_name
#         )

#         await self.accept()

#     async def disconnect(self, close_code):
#         # Leave the hive group
#         await self.channel_layer.group_discard(
#             self.hive_group_name,
#             self.channel_name
#         )

#     # Receive message from WebSocket
#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         message = data['message']

#         # Send message to hive group
#         await self.channel_layer.group_send(
#             self.hive_group_name,
#             {
#                 'type': 'hive_message',
#                 'message': message
#             }
#         )

#     # Receive message from hive group
#     async def hive_message(self, event):
#         message = event['message']

#         # Send message to WebSocket
#         await self.send(text_data=json.dumps({
#             'message': message
#         }))

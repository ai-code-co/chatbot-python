import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = f"user_{self.user_id}"

        await self.channel_layer.group_add(
            self.room_group_name, 
            self.channel_name
        )
        await self.accept()

        await self.send(json.dumps({
            "type": "system",
            "message": "WebSocket connected"
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name, 
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        user_message = data.get("message")

        # TODO: integrate OpenAI streaming & memory here

        # For now echo back
        await self.send(json.dumps({
            "type": "echo",
            "message": user_message
        }))

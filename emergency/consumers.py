from channels.generic.websocket import AsyncWebsocketConsumer
import json

class AlertConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Allow authenticated users to join the WebSocket group
        if self.scope['user'].is_authenticated:
            self.group_name = 'alerts_group'
            
            # Ensure the channel layer is available
            if self.channel_layer is not None:
                await self.channel_layer.group_add(
                    self.group_name,
                    self.channel_name
                )
                await self.accept()
            else:
                await self.close()
        else:
            await self.close()

    async def disconnect(self, close_code):
        # Ensure the channel layer is available
        if self.channel_layer is not None:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Broadcast the message to all connected clients
        if self.channel_layer is not None:
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'send_alert',
                    'message': message
                }
            )

    async def send_alert(self, event):
        message = event['message']

        # Send the message to WebSocket client
        await self.send(text_data=json.dumps({
            'message': message
        }))

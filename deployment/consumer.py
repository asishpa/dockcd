from channels.generic.websocket import AsyncWebsocketConsumer
import json
class DeploymentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.deployment_id = self.scope['url_route']['kwargs']['deployment_id']
        self.group_name = f'deployment_{self.deployment_id}'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
    async def deployment_log(self,event):
        await self.send(
            text_data=json.dumps({
                "log": event["log"]
            })
        )
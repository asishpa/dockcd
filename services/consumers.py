from channels.generic.websocket import AsyncWebsocketConsumer
import json

from services.command_service import validate_command
from .docker_utils import get_service_container, execute_command
from asgiref.sync import sync_to_async
from common.exceptions import ContainerNotFound
from common.docker_client import docker_client
# from services.command_service import validate_command

class ServiceExecConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.service_id =self.scope['url_route']['kwargs']['service_id']
        user = self.scope['user']
        if not user.is_authenticated:
            await self.close()
            return
        await self.accept()
    async def receive(self,text_data):
        from services.models import Service

        data = json.loads(text_data)
        container_name = data.get("container_name")
        command = data.get("command")
        user = self.scope['user']

        service = await sync_to_async(Service.objects.get)(id=self.service_id)

        #check permissions and command validation
        await sync_to_async(validate_command)(user,command)

        containers =await sync_to_async(get_service_container)(service)
        if container_name not in containers:
            return ContainerNotFound(f"Container with name {container_name} not found in service {service.name}")
        container = docker_client.containers.get(container_name)

        stream = execute_command(container_name,command)
        for chunk in stream:
            await self.send(chunk.decode())





class ContainerLogsConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.container_name = self.scope['url_route']['kwargs']['container_name']
        try:
            self.container = await sync_to_async(docker_client.containers.get)(self.container_name)
        except Exception:
            await self.close()
            return
        await self.accept()

        for line in self.container.logs(stream=True,follow=True):
            await self.send(
                text_data=json.dumps({
                    "log": line.decode()
                })
            )
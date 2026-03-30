from channels.generic.websocket import AsyncWebsocketConsumer
import json
import asyncio
import threading

from services.command_service import ensure_allowed_command, validate_command
from .docker_utils import execute_command
from asgiref.sync import sync_to_async
from common.docker_client import docker_client
from common.exceptions import CommandNotAllowed
# from services.command_service import validate_command

# Track threads to make sure that only one thread per conntaner is running
container_streams = {}
class ServiceExecConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.container_name = self.scope['url_route']['kwargs']['container_name']
        await self.accept()
    
    async def receive(self,text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(json.dumps({"error": "invalid JSON payload"}))
            return

        if not isinstance(data, dict):
            await self.send(json.dumps({"error": "JSON object payload is required"}))
            return

        command = data.get("command")
        mode = data.get("mode", "auto")
        user = self.scope.get('user')

        if not command:
            await self.send(json.dumps({"error": "command is required"}))
            return

        allowed_modes = {"auto", "process", "django_shell"}
        if mode not in allowed_modes:
            await self.send(json.dumps({"error": "mode must be one of: auto, process, django_shell"}))
            return

        command_for_validation = command if mode != "django_shell" else "python"
        try:
            await sync_to_async(ensure_allowed_command)(command_for_validation)
            if user and getattr(user, "is_authenticated", False):
                await sync_to_async(validate_command)(user, command_for_validation)
        except CommandNotAllowed as exc:
            await self.send(json.dumps({"error": str(exc)}))
            return
        
        asyncio.create_task(self._execute_command(self.container_name, command, mode))
    
    async def _execute_command(self, container_name, command, mode):
        """Execute command and stream output without blocking event loop"""
        queue = asyncio.Queue()
        loop = asyncio.get_event_loop()
        
        def stream_in_thread():
            """Read from Docker stream in background thread"""
            try:
                stream = execute_command(container_name, command, mode=mode)
                for chunk in stream:
                    asyncio.run_coroutine_threadsafe(
                        queue.put(chunk.decode()), 
                        loop
                    )
                asyncio.run_coroutine_threadsafe(queue.put(None), loop)
            except Exception as e:
                asyncio.run_coroutine_threadsafe(
                    queue.put({"error": str(e)}), 
                    loop
                )
        
        thread = threading.Thread(target=stream_in_thread, daemon=True)
        thread.start()
        
        while True:
            chunk = await queue.get()
            if chunk is None:
                break
            if isinstance(chunk, dict) and "error" in chunk:
                await self.send(json.dumps(chunk))
                break
            else:
                await self.send(chunk)





class ContainerLogsConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.container_name = self.scope['url_route']['kwargs']['container_name']
        try:
            self.container = await sync_to_async(docker_client.containers.get)(self.container_name)
        except Exception:
            await self.close()
            return
        await self.accept()
        
        
        # Register subscriber
        if self.container_name not in container_streams:
            container_streams[self.container_name] = {
                "subscribers": set(),
                "stop_event": threading.Event(),
                "thread": None,
                "loop": asyncio.get_running_loop(),

            }
        stream = container_streams[self.container_name]
        stream["subscribers"].add(self)
        if stream["thread"] is None:
            stream["thread"] = threading.Thread(
                target = self.start_log_stream,
                args=(self.container_name,),
                daemon=True
            )
            stream["thread"].start()
    async def disconnect(self, close_code):
        stream = container_streams.get(self.container_name)
        if not stream:
            return
        stream["subscribers"].discard(self)

        if not stream["subscribers"]:
            stream["stop_event"].set()
            container_streams.pop(self.container_name, None)

    def start_log_stream(self, container_name):
        stream = container_streams[container_name]
        stop_event = stream["stop_event"]
        loop = stream["loop"]
        try:
            container = docker_client.containers.get(container_name)

            for line in container.logs(stream=True, follow=True):
                if stop_event.is_set():
                    break

                message = json.dumps({"log": line.decode()})
                for consumer in list(stream["subscribers"]):
                    asyncio.run_coroutine_threadsafe(
                        consumer.send(message),
                        loop
                    )
        except Exception as e:
            error_msg = json.dumps({"error": str(e)})
            for consumer in list(stream["subscribers"]):
                asyncio.run_coroutine_threadsafe(
                    consumer.send(error_msg),
                    loop
                )
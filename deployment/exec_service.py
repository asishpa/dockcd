from services.models import AllowedCommands
from common import docker_client
from common.exceptions import CommandNotAllowed, ContainerNotFound

def validate_command(user,command):
    if user.role == user.ROLE_ADMIN:
        return
    
    allowed = AllowedCommands.objects.filter(command=command).exists()
    if not allowed:
        raise CommandNotAllowed(f"Command '{command}' is not allowed for this user")
def execute_command(container_name,command):
    try:
        container = docker_client.containers.get(container_name)
    except docker_client.errors.NotFound:
        raise ContainerNotFound(f"Container {container_name} not found")
    exec_instance = container.exec_run(command, stdout=True, stderr=True)
    return exec_instance.output.decode()

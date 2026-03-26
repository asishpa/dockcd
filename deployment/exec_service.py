from common import docker_client
from common.exceptions import ContainerNotFound

def execute_command(user, container_name, command):
    from services.command_service import validate_command  # lazy import

    validate_command(user, command)

    try:
        container = docker_client.containers.get(container_name)
    except docker_client.errors.NotFound:
        raise ContainerNotFound(f"Container {container_name} not found")

    exec_instance = container.exec_run(command, stdout=True, stderr=True)
    return exec_instance.output.decode()
from common.docker_client import docker_client
from common.exceptions import ContainerNotFound
def get_service_container(service):

    containers = docker_client.containers.list(
        all=True,
        filters={
            "label":[f"com.docker.compose.service={service.name}"]}
        
    )
    if not containers:
        return None
    return containers

def execute_command(conatiner_name, command):
    try:
        container = docker_client.containers.get(conatiner_name)
    except docker_client.errors.NotFound:
        raise ContainerNotFound(f"Container with name {conatiner_name} not found.")
    parts = command.split()
    exec_result = container.exec_run(
        parts,
        stdout=True,
        stderr=True,
        stream=True
    )
    return exec_result.output
from common.docker_client import docker_client
from common.exceptions import ContainerNotFound, ContainerStartFailed, ContainerStopFailed

def stop_container(container_id):
    try:
        container = docker_client.containers.get(container_id)
        container.stop()
    except docker_client.errors.NotFound:
        raise ContainerNotFound(f"Container with ID {container_id} not found")
    except Exception as e:
        raise ContainerStopFailed(f"Failed to stop container {container_id}: {str(e)}")
    
def start_container(container_id):
    try:
        container = docker_client.containers.get(container_id)
        container.start()
    except docker_client.errors.NotFound:
        raise ContainerNotFound(f"Container with ID {container_id} not found")
    except Exception as e:
        raise ContainerStartFailed(f"Failed to start container {container_id}: {str(e)}")

def restart_container(container_id):
    try:
        container = docker_client.containers.get(container_id)
        container.restart()
    except docker_client.errors.NotFound:
        raise ContainerNotFound(f"Container with ID {container_id} not found")
    except Exception as e:
        raise ContainerStartFailed(f"Failed to restart container {container_id}: {str(e)}")
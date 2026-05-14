from common.runtime_client import get_container_runtime_client
from applications.models import Application
from common.exceptions import ContainerNotFound, ContainerStartFailed, ContainerStopFailed

def stop_container(container_id,application_id):
    try:
        application = Application.objects.get(id=application_id)
        runtime_client = get_container_runtime_client(application.deployment_type)
        container = runtime_client.containers.get(container_id)
        container.stop()
    except Exception as e:
        raise ContainerStopFailed(f"Failed to stop container {container_id}: {str(e)}")
    
def start_container(container_id,application_id):
    try:
        application = Application.objects.get(id=application_id)
        runtime_client = get_container_runtime_client(application.deployment_type)
        container = runtime_client.containers.get(container_id)
        container.start()
    except Exception as e:
        raise ContainerStartFailed(f"Failed to start container {container_id}: {str(e)}")

def restart_container(container_id,application_id):
    try:
        application = Application.objects.get(id=application_id)
        runtime_client = get_container_runtime_client(application.deployment_type)
        container = runtime_client.containers.get(container_id)
        container.restart()
    except Exception as e:
        raise ContainerStartFailed(f"Failed to restart container {container_id}: {str(e)}")
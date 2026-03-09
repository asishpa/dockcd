from common.docker_client import docker_client

def get_service_container(service):

    containers = docker_client.containers.list(
        all=True,
        filters={
            "label":[f"com.docker.compose.service={service.name}"]}
        
    )
    if not containers:
        return None
    return containers

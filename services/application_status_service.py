from common.docker_client import docker_client
import logging
logger = logging.getLogger(__name__)

def get_application_services_status(application):

    services = application.services.all()
    containers = docker_client.containers.list(all=True)

    service_conatiner_map = {}

    for container in containers:
        labels = container.labels

        service_name = labels.get("com.docker.compose.service")

        #logger.info(f"Container {container.name} has labels: {labels}")
        if not service_name:
            logger.warning(f"Container {container.name} does not have 'com.docker.compose.service' label. Skipping.")
            continue
        service_conatiner_map.setdefault(service_name, []).append(container)

    result = []

    for service in services:
        service_containers = service_conatiner_map.get(service.name, [] )
        logger.info(f"Service {service.name} has {len(service_containers)} containers.")

        container_info = []

        service_status = "stopped"

        if service_containers:
            service_status = "running"
        for container in service_containers:

            container.reload()

            health = None

            state = container.attrs["State"]

            if "Health" in state:
                health = state["Health"]["Status"]
            
            container_info.append({
                "id": container.id,
                "name": container.name,
                "status": state["Status"],
                "health": health,
                "image": container.image.tags,
                "started_at": state["StartedAt"],
            })

            if health == "unhealthy":
                service_status = "degraded"
        result.append({
            "service_id": str(service.id),
            "service_name": service.name,
            "status": service_status,
            "container_count": len(service_containers),
            "containers": container_info
        })
    return result



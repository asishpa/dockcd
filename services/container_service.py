from services.docker_utils import get_container_by_service

def get_service_container_status(service):
    containers = get_container_by_service(service)
    result = []

    for container in containers:
        container.reload()  # Refresh container data
        health  = None

        if "Health" in container.attrs["State"]:
            health = container.attrs["State"]["Health"]["Status"]

            result.append({
                "name": container.name,
                "image": container.image.tags,
                "status": container.status,
                "health": health,
                "created": container.attrs["Created"],
                "started_at": container.attrs["State"]["StartedAt"],
            })
        return result
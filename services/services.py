
from celery.beat import Service

from common import docker_client
from services.docker_utils import get_service_container
from django.db import transaction

def get_service_status(service):
    container = get_service_container(service)
    if not container:
        return {
            "status": "not found"
        }
    container.reload()
    return {
        "container_id": container.id,
        "name": container.name,
        "status": container.status,
        "image": container.image.tags,
    }

def restart_service(service):
    containers = get_service_container(service)
    restarted = []
    for container in containers:
        container.restart()
        restarted.append(container.name)
    return restarted

def stop_service(service):
    containers = get_service_container(service)
    stopped = []
    for container in containers:
        container.stop()
        stopped.append(container.name)
    return stopped

def start_service(service):
    containers = get_service_container(service)
    started = []
    for container in containers:
        container.start()
        started.append(container.name)
    return started
def update_service_deploy_order(application, services_data):

    with transaction.atomic():

        for item in services_data:

            service = Service.objects.get(
                id=item["service_id"],
                application=application
            )

            service.deploy_order = item["deploy_order"]

            service.save(update_fields=["deploy_order"])


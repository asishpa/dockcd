from common.runtime_client import get_container_runtime_client
from applications.models import Application
def get_application_containers(application_id):
    application = Application.objects.get(id=application_id)
    deploy_path = application.deploy_path.rstrip("/")

    runtime_client = get_container_runtime_client(application.deployment_type)
    containers = runtime_client.containers.list(all=True)

    container_data = []

    for c in containers:
        labels = c.labels
        working_dir = labels.get("com.docker.compose.project.working_dir", "")

        if working_dir and working_dir.startswith(deploy_path):
            container_data.append({
                "id": c.short_id.split(":")[-1],
                "name": c.name,
                "status": c.status
            })

    return container_data
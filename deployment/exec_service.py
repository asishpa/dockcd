from common.runtime_client import get_container_runtime_client
from common.exceptions import ContainerNotFound
from applications.models import Application

def execute_command(user, container_name, command, application_id):
    from services.command_service import validate_command  # lazy import

    validate_command(user, command)

    try:
        application = Application.objects.get(id=application_id)
        runtime_client = get_container_runtime_client(application.deployment_type)
        container = runtime_client.containers.get(container_name)
    except Exception as e:
        raise ContainerNotFound(f"Container with name {container_name} not found: {str(e)}")
    exec_instance = container.exec_run(command, stdout=True, stderr=True)
    return exec_instance.output.decode()
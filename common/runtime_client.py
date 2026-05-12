from common.docker_client import docker_client
from common.podman_client import podman_client


def get_container_runtime_client(deployment_type):
    deployment_type_normalized = (deployment_type or "").strip().lower()

    if deployment_type_normalized == "docker":
        return docker_client
    if deployment_type_normalized == "podman":
        return podman_client

    raise ValueError(f"Unsupported deployment type: {deployment_type}")
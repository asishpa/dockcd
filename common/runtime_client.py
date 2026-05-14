import os
import docker


DOCKER_SOCKET = os.getenv(
    "DOCKER_SOCKET",
    "unix:///var/run/docker.sock"
)

PODMAN_SOCKET = os.getenv(
    "PODMAN_SOCKET",
    "unix:///run/user/1000/podman/podman.sock"
)


def get_container_runtime_client(deployment_type):

    deployment_type_normalized = (
        (deployment_type or "")
        .strip()
        .lower()
    )

    socket_map = {
        "docker": DOCKER_SOCKET,
        "podman": PODMAN_SOCKET,
    }

    if deployment_type_normalized not in socket_map:

        raise ValueError(
            f"Unsupported deployment type: {deployment_type}"
        )

    return docker.DockerClient(
        base_url=socket_map[
            deployment_type_normalized
        ]
    )
import docker
import shlex

from common.docker_client import docker_client
from common.exceptions import ContainerNotFound
def get_service_container(service):

    containers = docker_client.containers.list(
        all=True,
        filters={
            "label":[f"com.docker.compose.service={service.name}"]}
        
    )
    if not containers:
        return None
    return containers

def _is_bash_unavailable_error(exc):
    message = str(exc).lower()
    return (
        "executable file not found" in message
        or "no such file or directory" in message
        or "not found in $path" in message
    )


def _is_bash_unavailable_output(chunk):
    if not chunk:
        return False
    message = chunk.decode(errors="ignore").lower()
    return (
        "exec: \"/bin/bash\"" in message
        and ("no such file or directory" in message or "executable file not found" in message)
    )


def _run_django_shell(container, command):
    exec_result = container.exec_run(
        ["python", "manage.py", "shell", "-c", command],
        stdout=True,
        stderr=True,
        stream=True,
    )
    return exec_result.output


def _run_process_command(container, command):
    parts = shlex.split(command)
    if not parts:
        raise ValueError("command is required")

    exec_result = container.exec_run(
        parts,
        stdout=True,
        stderr=True,
        stream=True,
    )
    return exec_result.output


def execute_command(conatiner_name, command, mode="auto"):
    try:
        container = docker_client.containers.get(conatiner_name)
    except docker_client.errors.NotFound:
        raise ContainerNotFound(f"Container with name {conatiner_name} not found.")

    if mode == "process":
        return _run_process_command(container, command)

    if mode == "django_shell":
        return _run_django_shell(container, command)

    # Primary strategy: execute command through bash for familiar shell behavior.
    try:
        exec_result = container.exec_run(
            ["/bin/bash", "-lc", command],
            stdout=True,
            stderr=True,
            stream=True,
        )
        stream = iter(exec_result.output)
        first_chunk = next(stream, None)
        if _is_bash_unavailable_output(first_chunk):
            return _run_django_shell(container, command)

        def combined_stream():
            if first_chunk is not None:
                yield first_chunk
            for chunk in stream:
                yield chunk

        return combined_stream()
    except docker.errors.APIError as exc:
        if not _is_bash_unavailable_error(exc):
            raise

    # Fallback for hardened images without bash: run command in Django shell context.
    return _run_django_shell(container, command)
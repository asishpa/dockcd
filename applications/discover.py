import os
import subprocess
import yaml
import logging
from services.helpers import get_repo_head_commit
from services.models import Service

logger = logging.getLogger(__name__)
BASE_DEPLOY_DIR = "/opt/dockcd"


def validate_deploy_path(path):
    abs_path = os.path.abspath(path)

    if not abs_path.startswith(BASE_DEPLOY_DIR):
        raise ValueError("Deploy path must be inside /opt/dockcd")

    return abs_path


def clone_repo(repo_url, branch, deploy_path):
    if os.path.exists(deploy_path):
        raise ValueError("Deploy path already exists")
    print(f"Cloning repository {repo_url} (branch: {branch}) into {deploy_path}")
    subprocess.run(
        ["git", "clone", repo_url, deploy_path],
        check=True
    )

    subprocess.run(
        ["git", "checkout", branch],
        cwd=deploy_path,
        check=True
    )


def discover_compose_files(repo_path):
    compose_files = []

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in [".git", "node_modules", "__pycache__"]]
        for file in files:
            if file.startswith("docker-compose") and file.endswith((".yml", ".yaml")):
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, repo_path)
                compose_files.append(relative_path)

    return compose_files

def discover_env_files(folder_path):
    for root, dirs, files in os.walk(folder_path):
        dirs[:] = [d for d in dirs if d not in [".git", "node_modules", "__pycache__"]]

        for file in files:
            if file.endswith(".env"):
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, folder_path)
                return relative_path

    return None


def extract_services_from_compose(compose_full_path):
    with open(compose_full_path, "r") as f:
        data = yaml.safe_load(f)

    services = list(data.get("services", {}).keys())
    result = []
    for svc in services:
        if "-svc-" in svc:
            base = svc.split("-svc-")[0] + "-svc"
            if base not in result:
                result.append(base)
        else:
            if svc not in result:
                result.append(svc)
    
    return result




def auto_create_services(application):
    repo_path = application.deploy_path
    created_services = []

    logger.info(f"Repo path at {repo_path}")
    compose_files = discover_compose_files(repo_path)
    current_commit = get_repo_head_commit(repo_path)

    for compose_file in compose_files:
        full_path = os.path.join(repo_path, compose_file)

        service_names = extract_services_from_compose(full_path)

        env_file = discover_env_files(os.path.dirname(full_path))

        for service_name in service_names:
            defaults = {
                "compose_file_path": compose_file,
                "deploy_path": repo_path,
                "auto_deploy": True,
                "desired_commit": current_commit,
                "last_deployed_commit": None,
            }

            if env_file:
                defaults["env_file_path"] = env_file

            service, created = Service.objects.get_or_create(
                application=application,
                name=service_name,
                defaults=defaults
            )

            created_services.append(service)

    return created_services
  
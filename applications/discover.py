import os
import subprocess
import yaml

from services.models import Service


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


def extract_services_from_compose(compose_full_path):
    with open(compose_full_path, "r") as f:
        data = yaml.safe_load(f)

    services = list(data.get("services", {}).keys())
    return services[0] if services else None




def auto_create_services(application):
    repo_path = application.deploy_path
    created_services= []
    compose_files = discover_compose_files(repo_path)

    for compose_file in compose_files:
        full_path = os.path.join(repo_path, compose_file)

        service_name = extract_services_from_compose(full_path)
        service, created = Service.objects.get_or_create(
        application=application,
        name=service_name,
            defaults={
                "compose_file_path": compose_file,
                "deploy_path": repo_path,
                "auto_deploy": True
            }
        )

        created_services.append(service)     
    return created_services
  
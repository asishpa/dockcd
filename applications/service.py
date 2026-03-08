from applications.models import Application
from deployment.executor import LocalDeploymentExecutor
from deployment.models import Deployment
import services
from .discover import clone_repo, auto_create_services
from common.exceptions import (
    DeployPathInvalid,
    DeployPathExists,
    GitCloneFailed
)
import os


def register_application_service(validated_data):
    name = validated_data["name"]
    repo_url = validated_data["repo_url"]
    branch = validated_data["branch"]
    deploy_path = validated_data["deploy_path"]
    already_cloned = validated_data.get("already_cloned", False)
    abs_path = os.path.abspath(deploy_path)


    if not deploy_path.startswith("/opt/dockcd"):
        raise DeployPathInvalid(
            "Deploy path must be inside /opt/dockcd"
        )
    path_exists = os.path.exists(abs_path)

    if already_cloned and not path_exists:
        raise DeployPathInvalid(
            "Repository marked as already_cloned but path does not exist"
    )
    if not already_cloned and path_exists:
        raise DeployPathExists(
            "Deploy path already exists. Set already_cloned to True if repo is already cloned"
        )
    
    if not already_cloned:
        try:
            clone_repo(repo_url, branch, deploy_path)
        except Exception:
            raise GitCloneFailed("Failed to clone repository")
    application = Application.objects.create(
        name=name,
        repo_url=repo_url,
        branch=branch,
        deploy_path=deploy_path
    )
    services = auto_create_services(application)
    # for service in services:
    
    #     deployment = Deployment.objects.create(service=service)
    #     LocalDeploymentExecutor(deployment).run()

    return application,services
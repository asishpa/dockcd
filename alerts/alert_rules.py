from applications.models import Application
from common.docker_client import docker_client
from alerts.helpers import fetch_alert_rule_for_application, create_alert_event
from alerts.services import should_trigger_alert, trigger_alert
def evaluate_container_down(application_id):
    application = Application.objects.get(id=application_id)
    deploy_path = application.deploy_path.rstrip("/")
    containers = docker_client.containers.list(all=True)
    alert_rules = fetch_alert_rule_for_application(application_id, "container_down")
    for c in containers:
        labels = c.labels
        working_dir = labels.get("com.docker.compose.project.working_dir", "")
        if working_dir and working_dir.startswith(deploy_path) and c.status != "running":
            container_name = c.name
            if alert_rules and should_trigger_alert(alert_rules):
                message = f"Container {container_name} is down for application {application.name}"
                create_alert_event(alert_rules, message)
                trigger_alert(alert_rules, message)

def evaluate_container_restarting(application_id):
    application = Application.objects.get(id=application_id)
    deploy_path = application.deploy_path.rstrip("/")
    containers = docker_client.containers.list(all=True)
    alert_rules = fetch_alert_rule_for_application(application_id, "container_restarting")
    for c in containers:
        labels = c.labels
        working_dir = labels.get("com.docker.compose.project.working_dir", "")
        if working_dir and working_dir.startswith(deploy_path) and c.status == "restarting":
            container_name = c.name
            if alert_rules and should_trigger_alert(alert_rules):
                message = f"Container {container_name} is restarting for application {application.name}"
                create_alert_event(alert_rules, message)
                trigger_alert(alert_rules, message)
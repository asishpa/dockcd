
from celery import shared_task

from applications.models import Application
from alerts.alert_rules import evaluate_container_down, evaluate_container_restarting
@shared_task
def monitor_container_status():
    applications = Application.objects.all()
    for app in applications:
        evaluate_container_down(app.id)
        evaluate_container_restarting(app.id)


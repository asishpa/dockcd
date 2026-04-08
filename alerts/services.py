from django.utils import timezone
import requests
import logging
from alerts.models import AlertRule, AlertEvent, AlertChannel
from django.core.mail import send_mail
logger = logging.getLogger(__name__)

def should_trigger_alert(rule):
    last_event = AlertEvent.objects.filter(rule=rule).order_by("-triggered_at").first()
    if not last_event:
        return True
    elapsed_time = timezone.now() - last_event.triggered_at
    if elapsed_time.total_seconds() >= rule.frequenecy_minutes * 60:
        return True
    return False

def trigger_alert(rule, message):
    for channel in rule.channel.filter(enabled=True):
        if channel.type == "email" and channel.email:
            send_mail(
                subject="Alert Triggered",
                message=message,
                from_email="noreply@yourapp.com",
                recipient_list=[channel.email]
            )
        elif channel.type == "webhook" and channel.webhook_enabled and channel.webhook_url:
            try:
                requests.post(channel.webhook_url, json={"message": message,"rule": rule.condition})    
            except requests.RequestException as e:
                logger.error(f"Failed to send webhook alert: {e}")

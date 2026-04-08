from alerts.models import AlertEvent,AlertRule
def create_alert_event(rule, message):
    AlertEvent.objects.create(rule=rule, message=message)
def fetch_alert_rule_for_application(application_id,condition):
    try:
        return AlertRule.objects.get(application_id=application_id, condition=condition, enabled=True)
    except AlertRule.DoesNotExist:
        return None

from django.db import models

# Create your models here.

class AlertChannel(models.Model):

    TYPE_EMAIL= "email"
    TYPE_WEBHOOK = "webhook"

    TYPE_CHOICES = [
        (TYPE_EMAIL, "Email"),
        (TYPE_WEBHOOK, "Webhook"),
    ]
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    application = models.ForeignKey("applications.Application", on_delete=models.CASCADE, related_name="alert_channels")
    email = models.EmailField(blank=True, null=True)
    webhook_url = models.URLField(blank=True, null=True)
    webhook_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class AlertRule(models.Model):
    CONDITION_CONTAINER_DOWN = "container_down"
    CONDITION_CONTAINER_RESTARTING = "container_restarting"
    CONDITION_CHOICES = [
        (CONDITION_CONTAINER_DOWN, "Container Down"),
        (CONDITION_CONTAINER_RESTARTING, "Container Restarting"),
    ]

    condition = models.CharField(max_length=50, choices=CONDITION_CHOICES)
    application = models.ForeignKey("applications.Application", on_delete=models.CASCADE, related_name="alert_rules")
    frequency_minutes = models.PositiveIntegerField(default=5)
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class AlertEvent(models.Model):
    rule = models.ForeignKey(AlertRule,on_delete=models.CASCADE, related_name="events")
    triggered_at = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    resolved = models.BooleanField(default=False)
    

    
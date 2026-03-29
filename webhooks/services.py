from webhooks.models import GitHubWebhook
from applications.models import Application


def create_github_webhook(application_id, secret):

    application = Application.objects.get(id=application_id)

    webhook = GitHubWebhook.objects.create(
        application=application,
        secret=secret,
        is_active=True
    )

    return webhook


def edit_github_webhook_secret(application_id, secret):
    webhook = GitHubWebhook.objects.get(application_id=application_id)
    webhook.secret = secret
    webhook.save(update_fields=["secret", "updated_at"])
    return webhook
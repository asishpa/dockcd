from .views import AlertChannelView, AlertRuleView
from django.urls import path
urlpatterns = [
    path("alert-channels/", AlertChannelView.as_view(), name="alert-channel-list"),
    path("alert-rules/", AlertRuleView.as_view(), name="alert-rule-list"),
]   
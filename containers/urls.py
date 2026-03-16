from containers.views import ContainerLogsView

from django.urls import path
urlpatterns = [
path("<str:container_id>/logs/", ContainerLogsView.as_view()),
]
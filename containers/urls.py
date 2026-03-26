from containers.views import ContainerListView, ContainerLogsView, ContainerRestartView, ContainerStartView, ContainerStopView

from django.urls import path
urlpatterns = [
path("<str:container_id>/logs/", ContainerLogsView.as_view()),
path("<str:container_id>/start/", ContainerStartView.as_view()),
path("<str:container_id>/stop/", ContainerStopView.as_view()),
path("<str:container_id>/restart/", ContainerRestartView.as_view()),
path("list/", ContainerListView.as_view()),     
]
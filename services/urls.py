from django.urls import path
from services.views import RestartServiceView, ServiceContainersView, ServiceStatusView, StartServiceView, StopServiceView

urlpatterns = [
    
    path(
        "<uuid:service_id>/status/",
        ServiceStatusView.as_view(),
        name="service-status"
    ),
    path(
        "<uuid:service_id>/restart/",
        RestartServiceView.as_view(),
        name="service-restart"
    ),
    path(
        "<uuid:service_id>/stop/",
        StopServiceView.as_view(),
        name="service-stop"
    ),
    path(
        "<uuid:service_id>/start/",
        StartServiceView.as_view(),
        name="service-start"
    ),
    path(
        "<uuid:service_id>/containers/",
        ServiceContainersView.as_view(),
        name="service-containers"
    )

]

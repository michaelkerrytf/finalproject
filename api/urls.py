
from django.urls import path

from . import views

urlpatterns = [
    path("view/logs/<str:tenant_prefix>", views.index, name="index"),
    path("health", views.health, name="health"),
    path("migrate/stage", views.stage, name="stage"),
    path("validate/stage", views.validate_stage, name="validate_stage"),
    path("migrate/prod", views.prod, name="prod"),
    path("validate/prod", views.validate_prod, name="validate_prod"),
    path("migrate/logs/<str:tenant_prefix>", views.logs, name="logs"),
    path("endpoints", views.endpoints, name="endpoints"),
    path("endpoints/<int:ep_id>", views.endpoint, name="endpoint")
]

from django.urls import path

from . import views

urlpatterns = [
    path("", views.bare_index, name="bare_index"),
    path("view/logs/<str:tenant_prefix>", views.index, name="index"),
    path("view/logs", views.bare_view_logs, name="bare_view_logs"),
    path("health", views.health, name="health"),
    path("migrate/stage", views.stage, name="stage"),
    path("validate/stage", views.validate_stage, name="validate_stage"),
    path("migrate/prod", views.prod, name="prod"),
    path("validate/prod", views.validate_prod, name="validate_prod"),
    path("migrate/logs/<str:tenant_prefix>", views.logs, name="logs")
]
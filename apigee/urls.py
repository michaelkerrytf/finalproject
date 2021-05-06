from django.urls import path

from . import views

urlpatterns = [
    path("health", views.health, name="health"),
    path("organizations/<str:org_name>/sharedflows/<str:sharedflow_name>", views.info, name="info"),
    path("organizations/<str:org_name>/sharedflows/<str:sharedflow_name>/revisions/<int:rev_no>", views.bundle, name="bundle"),
    path("organizations/<str:org_name>/sharedflows", views.post, name="post"),
    path("organizations/<str:org_name>/environments/<str:env_name>/sharedflows/<str:sharedflow_name>/revisions/<int:rev_no>/deployments", views.deploy, name="deploy"),
    path("organizations/<str:org_name>/userroles/<str:userrole_name>/users", views.userinfo, name="userroles"),
    path("organizations/<str:org_name>/userroles/<str:userrole_name>/resourcepermissions", views.assign, name="assign")
]

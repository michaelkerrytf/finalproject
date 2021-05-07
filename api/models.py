import json

from django.db import models

# Create your models here.

DATE_TIME_DISPLAY_FORMAT = "%b %d %Y, %I:%M %p"
DATE_TIME_SORT_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"


def cleanup(text):
    return text.replace('b\'{', '{').replace('\'"', '"').replace('\\"', '"')


class ApigeeMgmtLog(models.Model):
    """
    encapsulates relevant logging information for migration requests
    """
    tenant_prefix = models.CharField(max_length=10, blank=True, null=True)
    destination = models.CharField(max_length=10, blank=True, null=True)
    status = models.CharField(max_length=10, blank=True, null=True)
    request_text = models.TextField(blank=True, null=True)
    response_text = models.TextField(blank=True, null=True)
    ip_addr = models.CharField(max_length=32, blank=True, null=True)
    username = models.CharField(max_length=256, blank=True, null=True)
    created_by = models.CharField(max_length=256, blank=True, null=True)
    created_date = models.DateTimeField(blank=True, null=True, auto_now=True)
    user_roles = models.CharField(max_length=1024, blank=True, null=True)
    build_tags = models.CharField(max_length=1024, blank=True, null=True)
    build_comment = models.TextField(blank=True, null=True)

    def serialize(self):
        return {
            "id": self.id,
            "tenantPrefix": self.tenant_prefix,
            "destination": self.destination,
            "status": self.status,
            "requestText": json.dumps(json.loads(self.request_text), indent=2),
            "responseText": json.dumps(json.loads(self.response_text), indent=2),
            "ipAddr": self.ip_addr,
            "username": self.username,
            "userRoles": self.user_roles,
            "tags": self.build_tags,
            "comment": self.build_comment,
            "createdBy": self.created_by,
            "timestamp": self.created_date.strftime(DATE_TIME_DISPLAY_FORMAT),
            "createdDate": self.created_date.strftime(DATE_TIME_DISPLAY_FORMAT),
            "createdDateSort": self.created_date.strftime(DATE_TIME_SORT_FORMAT)
        }

from django.db import models
import uuid
# Create your models here.

class DKIMDefaultSelector(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True, db_index=True)
    service_provider = models.CharField(max_length=1000, db_index=True)
    domain = models.CharField(max_length=1000, db_index=True)
    selector = models.JSONField(default=list, null=True)
    status = models.BooleanField(default=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.domain if self.domain else f"{self.id}"


class EmailDomains(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True, db_index=True)
    domain = models.CharField(max_length=1000, unique=True, db_index=True, null=True)
    email = models.CharField(max_length=1000, db_index=True, null=True)
    # MX Record Management
    mx_status = models.BooleanField(default=False, null=True)
    mx_records = models.JSONField(default=list, null=True)
    smtp_status = models.BooleanField(default=False, null=True)
    smtp_response = models.JSONField(null=True)
    # SPF Record Management
    spf_status = models.BooleanField(default=False, null=True)
    spf_records = models.JSONField(null=True)
    # DMARC Record Management
    dmarc_status = models.BooleanField(default=False, null=True)
    dmarc_records = models.JSONField(null=True)
    # DKIM Record Management
    dkim_selector = models.JSONField(default=list, null=True)
    dkim_status = models.BooleanField(default=False, null=True)
    dkim_records = models.JSONField(null=True)

    status = models.BooleanField(default=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.domain if self.domain else f"{self.id}"

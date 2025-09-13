from django.contrib import admin
from email_service.models import EmailDomains, DKIMDefaultSelector

# Register your models here.

@admin.register(DKIMDefaultSelector)
class DKIMDefaultSelectorAdmin(admin.ModelAdmin):
    list_display = ['id', 'service_provider', 'domain', 'selector', 'status', 'created_at', 'updated_at']
    search_fields = ['id', 'service_provider', 'domain', 'selector']
    list_filter = ['status', 'created_at', 'updated_at']
    ordering = ['-created_at']

@admin.register(EmailDomains)
class EmailDomainsAdmin(admin.ModelAdmin):
    list_display = ["id", 'domain', 'mx_status', 'spf_status', 'dmarc_status', 'dkim_status', 'status', 'created_at', 'updated_at']
    search_fields = ["id", 'domain', 'mx_records', 'spf_records', 'dmarc_records', 'dkim_records', 'dkim_selector']
    list_filter = ['status', 'created_at', 'updated_at']
    ordering = ['-created_at']


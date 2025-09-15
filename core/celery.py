from __future__ import absolute_import, unicode_literals

import os

from celery import Celery, shared_task
from celery.schedules import crontab
from django.db import transaction, IntegrityError


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')

# app.conf.enable_utc = False

app.conf.update(timezone='Asia/Kathmandu')

app.autodiscover_tasks()


@app.on_after_configure.connect
def smtp_updater_task(sender, **kwargs):
    sender.add_periodic_task(crontab(minute="*/30"), smtp_auto_updater.s())

@shared_task()
def update_domain_records(record_id):
    from email_service.models import EmailDomains
    from email_service.utils import (
        get_mx_records, get_top_level_domain, get_dkim_selector, smtp_verification, check_spf, check_dmarc, check_dkim
    )
    email_domain_obj = EmailDomains.objects.get(id=record_id)
    try:
        domain = email_domain_obj.domain
        email = email_domain_obj.email

        mx_status, mx_records = get_mx_records(domain)
        mx_record = mx_records[0] if mx_records else []
        mx_top_level_domain = get_top_level_domain(mx_record) if mx_record else None

        dkim_selectors = get_dkim_selector(mx_top_level_domain) if mx_top_level_domain else []
        smtp_status, smtp_response = smtp_verification(mx_record, email) if mx_record else (False, None)
        spf_status, spf_records = check_spf(domain)
        dmarc_status, dmarc_records = check_dmarc(domain)
        dkim_status, dkim_records = check_dkim(domain, selectors=dkim_selectors) if dkim_selectors else (False, None)

        email_domain_obj.mx_status = mx_status
        email_domain_obj.mx_records = mx_records
        email_domain_obj.smtp_status = smtp_status
        email_domain_obj.smtp_response = smtp_response
        email_domain_obj.spf_status = spf_status
        email_domain_obj.spf_records = spf_records
        email_domain_obj.dmarc_status = dmarc_status
        email_domain_obj.dmarc_records = dmarc_records
        email_domain_obj.dkim_status = dkim_status
        email_domain_obj.dkim_records = dkim_records
        email_domain_obj.save()
    except Exception as e:
        print(f"Error updating {email_domain_obj.domain}: {e}")


@shared_task
def smtp_auto_updater():
    from email_service.models import EmailDomains
    domains_records = EmailDomains.objects.iterator()
    for record in domains_records:
        update_domain_records.apply_async(args=[record.id])


@app.task
def aggregate_results(results):
    return {"results": results}


@app.task
def get_smtp_records(email):
    from email_service.utils import get_smtp_records
    records = get_smtp_records(email)
    return records


@app.task
def create_domain_record(emails_domains):
    from email_service.models import EmailDomains
    from email_service.utils import (
        get_mx_records, get_top_level_domain, get_dkim_selector, smtp_verification, check_spf, check_dmarc, check_dkim
    )
    domain = emails_domains.get("domain")
    email = emails_domains.get("email")
    if not EmailDomains.objects.filter(domain=domain).exists():
        mx_status, mx_records = get_mx_records(domain)
        if not mx_status:
            return {"email": email, "message": "MX Record is missing"}
        mx_top_level_domain = get_top_level_domain(mx_records[0])
        dkim_selectors = get_dkim_selector(mx_top_level_domain)
        smtp_status, smtp_response = smtp_verification(mx_records[0], email)
        spf_status, spf_records = check_spf(domain)
        dmarc_status, dmarc_records = check_dmarc(domain)
        dkim_status, dkim_records = check_dkim(domain, selectors=dkim_selectors)
        try:
            with transaction.atomic():
                email_domain_obj, created = EmailDomains.objects.select_for_update().get_or_create(
                    domain=domain,
                    defaults={
                        "email": email,
                        "mx_status": mx_status,
                        "mx_records": mx_records,
                        "smtp_status": smtp_status,
                        "smtp_response": smtp_response,
                        "spf_status": spf_status,
                        "spf_records": spf_records,
                        "dmarc_status": dmarc_status,
                        "dmarc_records": dmarc_records,
                        "dkim_status": dkim_status,
                        "dkim_selector": dkim_selectors,
                        "dkim_records": dkim_records,
                    },
                )
        except IntegrityError:
            pass
    return {"status":True}

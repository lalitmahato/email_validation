import logging
import re
import smtplib

import tldextract
from django.db import transaction, IntegrityError
from dns import resolver

from email_service.models import EmailDomains, DKIMDefaultSelector
from email_service.serializers import EmailDomainSerializer

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")


def email_validator(email):
    if EMAIL_REGEX.match(email):
        return True
    return False


def get_unique_domain_from_email(emails):
    unique_domains = []
    unique_emails_domains = []
    for email in emails:
        domain = email.split("@")[1]
        if domain not in unique_domains:
            unique_domains.append(domain)
            if not EmailDomains.objects.filter(domain=domain).exists():
                unique_emails_domains.append({"email": email, "domain": domain})
    return unique_domains, unique_emails_domains


def get_mx_records(domain):
    try:
        mx_records = resolver.resolve(domain, "MX")
        mx_records_list = [str(r.exchange) for r in mx_records]
        if mx_records_list == ["."]:
            return False, []
        return True, mx_records_list
    except Exception as e:
        return False, []


def smtp_verification(mx_record, email, timeout=5):
    try:
        with smtplib.SMTP(mx_record, 25, timeout=timeout) as server:
            server.ehlo_or_helo_if_needed()
            server.mail(email)
            code, response = server.rcpt(email)
            if 200 <= code < 300:
                return True, {"code": code, "result": f"{str(response)}"}
            return False, {"code": code, "result": f"{str(response)}"}
    except Exception as e:
        print(e)
    return False, {"message": "Unable to connect to the smtp server."}


def check_spf(domain):
    try:
        answers = resolver.resolve(domain, "TXT")
        for r in answers:
            content = str(r.strings[0].decode())
            if "v=spf" in content:
                return True, {"result": content}
        return False, {"message": "SPF Record is missing"}
    except Exception as e:
        return False, {"message": f"{e}"}


def check_dmarc(domain):
    try:
        answers = resolver.resolve(f"_dmarc.{domain}", "TXT")
        for r in answers:
            content = str(r.strings[0].decode())
            if "v=DMARC" in content:
                return True, {"result": content}
        return False, {"message": "DMARC Record is missing"}
    except Exception as e:
        return False, {"message": f"{e}"}


def check_dkim(domain, selectors=["default"]):
    for selector in selectors:
        try:
            query = f"{selector}._domainkey.{domain}"
            answers = resolver.resolve(query, "TXT")
            for record in answers:
                content = b"".join(record.strings).decode()
                if "v=DKIM" in content:
                    return True, {"result": content}
        except Exception as e:
            logging.error(f"DKIM Error: {e}")
    return False, {"message": "DKIM record is missing or default selector is invalid"}


def get_top_level_domain(mx_record):
    ext = tldextract.extract(mx_record.rstrip('.'))
    main_domain = f"{ext.domain}.{ext.suffix}"
    return main_domain


def get_dkim_selector(top_level_domain):
    dkim_selector_objs = DKIMDefaultSelector.objects.filter(domain=top_level_domain)
    if not dkim_selector_objs:
        with transaction.atomic():
            DKIMDefaultSelector.objects.select_for_update()
            DKIMDefaultSelector.objects.create(
                service_provider=top_level_domain,
                domain=top_level_domain,
                selector=["default"]
            )
    dkim_selectors = []
    for obj in dkim_selector_objs:
        dkim_selectors += obj.selector
    return dkim_selectors


def get_smtp_records(email):
    email_validation_status = email_validator(email)
    if not email_validation_status:
        return {"message": "Invalid email address."}
    email_domain = email.split("@")[1]
    email_domain_obj = EmailDomains.objects.filter(domain=email_domain).first()
    if email_domain_obj:
        serializer = EmailDomainSerializer(email_domain_obj)
    else:
        mx_status, mx_records = get_mx_records(email_domain)
        if not mx_status:
            return {"email": email, "message": "MX Record is missing"}
        mx_top_level_domain = get_top_level_domain(mx_records[0])
        dkim_selectors = get_dkim_selector(mx_top_level_domain)
        smtp_status, smtp_response = smtp_verification(mx_records[0], email)
        spf_status, spf_records = check_spf(email_domain)
        dmarc_status, dmarc_records = check_dmarc(email_domain)
        dkim_status, dkim_records = check_dkim(email_domain, selectors=dkim_selectors)
        try:
            with transaction.atomic():
                email_domain_obj, created = EmailDomains.objects.select_for_update().get_or_create(
                    domain=email_domain,
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
            email_domain_obj = EmailDomains.objects.get(domain=email_domain)
        serializer = EmailDomainSerializer(email_domain_obj)
    data = serializer.data
    data["email"] = email
    return data


def get_live_smtp_records(email):
    domain = email.split("@")[1]
    mx_status, mx_records = get_mx_records(domain)
    if not mx_status:
        return {"email": email, "message": "MX Record is missing or email domain is not valid"}
    mx_top_level_domain = get_top_level_domain(mx_records[0])
    dkim_selectors = get_dkim_selector(mx_top_level_domain)
    smtp_status, smtp_response = smtp_verification(mx_records[0], email, timeout=10)
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
    return {
        "email": email,
        "result": {
            "domain": domain,
            "mx_records": mx_records,
            "smtp_status": smtp_status,
            "smtp_response": smtp_response,
            "spf_records": spf_records,
            "dmarc_records": dmarc_records,
            "dkim_records": dkim_records
        }
    }

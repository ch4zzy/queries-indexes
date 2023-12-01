from datetime import datetime

from django.db.models import QuerySet

from apps.queries.models import Order
import json


start_date = "2020-07-06 07:28:04"
end_date = "2023-08-06 07:28:04"


def filter_data() -> json:
    filter_dict = {
        "unpaid": start_date
    }
    return json.dumps([filter_dict])

def filter_data_diapason() -> json:
    filter_dict = {
        "unpaid":{
            "$gte": start_date,
            "$lte": end_date
        }
    }
    return json.dumps(filter_dict)


# email examples

def email_contains() -> QuerySet:
    return Order.objects.filter(email__contains="gmail", paid=True).explain(analyze=True)


def email_icontains() -> QuerySet:
    return Order.objects.filter(email__icontains="GMAIL", paid=True).explain(analyze=True)


def email_endswith() -> QuerySet:
    return Order.objects.filter(email__endswith="gmail.com", paid=True).explain(analyze=True)


def email_iendswith() -> QuerySet:
    return Order.objects.filter(email__iendswith="GMAIL.COM", paid=True).explain(analyze=True)


def email_exact() -> QuerySet:
    return Order.objects.filter(email__exact="hartmankristina@example.com", paid=True).explain(analyze=True)


def email_iexact() -> QuerySet:
    return Order.objects.filter(email__iexact="HARtmankristina@example.com", paid=True).explain(analyze=True)


def email_in() -> QuerySet:
    return Order.objects.filter(email__in=["hartmankristina@example.com"], paid=True).explain(analyze=True)


def email_isnull() -> QuerySet:
    return Order.objects.filter(email__isnull=True, paid=True).explain(analyze=True)


def email_regex() -> QuerySet:
    return Order.objects.filter(email__regex="^.*@.*\.Com$", paid=True).explain(analyze=True)


def email_iregex() -> QuerySet:
    return Order.objects.filter(email__iregex="^.*@.*\.cOm$", paid=True).explain(analyze=True)


def email_startswith() -> QuerySet:
    return Order.objects.filter(email__startswith="hartmankristina", paid=True).explain(analyze=True)


def email_istartswith() -> QuerySet:
    return Order.objects.filter(email__istartswith="HARTMANKRISTINA", paid=True).explain(analyze=True)


# date examples


def status_contains(filter_dict) -> QuerySet:
    return Order.objects.filter(status__contains=[filter_dict]).explain(analyze=True)


def date_search_json(filter_dict) -> QuerySet:
    return Order.objects.filter(status__contains=filter_dict).explain(analyze=True)


def date_search_gte(filter_dict) -> QuerySet:
    return Order.objects.filter(status__gte=[filter_dict]).explain(analyze=True)


def date_search_lte(filter_dict) -> QuerySet:
    return Order.objects.filter(status__lte=[filter_dict]).explain(analyze=True)




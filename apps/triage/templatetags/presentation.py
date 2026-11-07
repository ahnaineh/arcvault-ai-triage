"""Readable labels for persisted analysis; no policy or inference changes."""
from decimal import Decimal

from django import template

register = template.Library()

LABELS = {
    'low_confidence': 'The model score is below the automatic routing threshold.',
    'active_outage': 'A possible active outage needs attention.',
    'inconsistent_analysis': 'The category and outage signal disagree.',
    'outage_scope_unresolved': 'The outage scope could not be established.',
    'billing_comparison_unresolved': 'The billed and expected amounts cannot be safely compared.',
    'billing_overcharge': 'The apparent overcharge exceeds USD 500.',
    'insufficient_information': 'The message needs more information.',
    'conflicting_intents': 'The message contains competing requests.',
}


@register.filter
def readable(value):
    return LABELS.get(str(value), str(value).replace('_', ' ').capitalize())


@register.inclusion_tag('intake/value.html')
def readable_value(value):
    if isinstance(value, dict):
        return {'mapping': value}
    if isinstance(value, list):
        return {'sequence': value}
    return {'scalar': value}


@register.filter
def signal_label(value):
    return {
        'active_service_outage': 'Service outage',
        'conflicting_intents': 'Competing requests',
        'insufficient_information': 'Missing information',
    }.get(str(value), str(value).replace('_', ' ').capitalize())


@register.filter
def percent(value):
    number = format(Decimal(str(value)) * 100, 'f')
    return (number.rstrip('0').rstrip('.') if '.' in number else number) + '%'


@register.filter
def amount(value):
    return format(Decimal(str(value)), ',f') if value is not None else 'Unknown'

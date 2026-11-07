"""Pure policy: decide(validated_analysis); Decimal arithmetic never uses FX."""
import re
from decimal import Decimal, localcontext

from .schemas import Analysis, Comparison

QUEUES = {'Bug Report':'Engineering','Feature Request':'Product','Billing Issue':'Billing','Technical Question':'Technical Support','Incident/Outage':'Engineering'}

def _subtract_exact(a, b):
    with localcontext() as ctx:
        operands = [Decimal(a), Decimal(b)]
        ctx.prec = max(len(v.as_tuple().digits) + v.as_tuple().exponent for v in operands) + max(-v.as_tuple().exponent for v in operands) + 1
        difference = Decimal(a) - Decimal(b)
    return difference

def normalize_billing(comparison: Comparison | None, source: str | None = None):
    """Return status, signed difference and explicit synthetic-domain assumptions."""
    if comparison is None: return 'not_applicable', None, []
    a, b = comparison.billed, comparison.expected
    assumptions = []
    def currency(token):
        if token == '$' and 'Unqualified $ interpreted as USD in synthetic domain' not in assumptions:
            assumptions.append('Unqualified $ interpreted as USD in synthetic domain')
        return 'USD' if token in ('USD', 'US$', '$') else token
    ca, cb = currency(a.currency), currency(b.currency)
    if ca != 'USD' or cb != 'USD' or a.amount is None or b.amount is None:
        return 'unresolved', None, assumptions
    # Apply only to a complete direct comparison statement. Extra period,
    # component or currency clauses fail closed, even if omitted by extraction.
    direct = source and re.fullmatch(
        r'invoice\s+#[\w-]+\s+shows a charge of\s+(?:US\$|\$|USD\s*)[\d,.]+'
        r'\s+but\s+(?:our )?contract rate is\s+(?:US\$|\$|USD\s*)[\d,.]+/month'
        r'\.?(?:\s+(?:(?:Can|Could) (?:someone|you) (?:please )?look into this|(?:Can|Could) you (?:please )?(?:check this|investigate|help)|Please (?:check this|investigate))[?.]?)?',
        ' '.join(source.split()), re.IGNORECASE)
    if (direct and a.period in (None, 'invoice') and b.period == 'monthly'
            and a.components is None and b.components is None
            and all(excerpt in source for excerpt in a.evidence + b.evidence)):
        assumptions.append(
            'Apparent difference assumes one monthly charge and the same '
            'component for a direct invoice versus contract comparison')
        return 'comparable_usd', _subtract_exact(a.amount, b.amount), assumptions
    # Unknown bases are unsafe; extraction must preserve invoice/monthly wording.
    periods = (a.period, b.period)
    if any(p not in {'invoice', 'monthly', 'annual', 'one_time'} for p in periods):
        return 'unresolved', None, assumptions
    if any(c not in {'subscription', 'total', 'usage', 'tax'} for c in (a.components, b.components)):
        return 'unresolved', None, assumptions
    if set(periods) == {'invoice', 'monthly'} and a.components == b.components and a.components is not None:
        assumptions.append('Direct invoice/monthly contract comparison treated as one monthly charge')
    elif a.period is None or a.period != b.period:
        return 'unresolved', None, assumptions
    if a.components is None or a.components != b.components:
        return 'unresolved', None, assumptions
    return 'comparable_usd', _subtract_exact(a.amount, b.amount), assumptions

def decide_projection(*, category, confidence, active_service_outage, insufficient_information, conflicting_intents, billing_status, reported_overcharge):
    """Controlled policy projection for fixtures; application callers use decide."""
    outage = category == 'Incident/Outage'
    conditions = [confidence < .70, outage or active_service_outage is True,
                  (outage and active_service_outage is not True) or (not outage and active_service_outage is True),
                  active_service_outage is None, billing_status == 'unresolved',
                  billing_status == 'comparable_usd' and reported_overcharge is not None and Decimal(reported_overcharge) > 500,
                  insufficient_information, conflicting_intents]
    names = ['low_confidence','active_outage','inconsistent_analysis','outage_scope_unresolved','billing_comparison_unresolved','billing_overcharge','insufficient_information','conflicting_intents']
    reasons = [name for name, condition in zip(names, conditions) if condition]
    queue = QUEUES[category]
    return {'standard_destination': queue, 'final_destination': 'Human Review' if reasons else queue, 'human_escalation': bool(reasons), 'escalation_reasons': reasons}

def decide(analysis: Analysis):
    """Derive export-ready decision from context-validated analysis, without model calls."""
    source = analysis._source
    data = analysis.model_dump()
    if analysis._accepted is None or data != analysis._accepted:
        raise ValueError('analysis must be accepted by validate_analysis and unchanged')
    def excerpts(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key == 'evidence':
                    yield from ([item] if isinstance(item, str) else item)
                else:
                    yield from excerpts(item)
        elif isinstance(value, list):
            for item in value:
                yield from excerpts(item)
    analysis = Analysis.model_validate(data, context={'message': '\n'.join(excerpts(data))})
    status, difference, assumptions = normalize_billing(analysis.billing_comparison, source)
    signals = analysis.signals
    result = decide_projection(category=analysis.category, confidence=analysis.confidence,
        active_service_outage=signals.active_service_outage.value,
        insufficient_information=signals.insufficient_information.value,
        conflicting_intents=signals.conflicting_intents.value,
        billing_status=status, reported_overcharge=difference)
    return result | {'reported_overcharge': str(difference) if difference is not None else None, 'comparison_assumptions': assumptions}

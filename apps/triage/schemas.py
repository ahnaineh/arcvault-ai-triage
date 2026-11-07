"""Strict analysis contract. Integration must call validate_analysis(payload, message)."""
import re
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, ValidationInfo, PrivateAttr, model_validator

Text = Annotated[str, StringConstraints(min_length=1, pattern=r'\S')]
Category = Literal['Bug Report', 'Feature Request', 'Billing Issue', 'Technical Question', 'Incident/Outage']
class Strict(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True, allow_inf_nan=False, revalidate_instances='always')
class Entity(Strict):
    type: Literal['account_id','invoice_number','error_code','url','product_or_integration','time_expression','other']
    value: Text
    evidence: Text
class Urgency(Strict):
    level: Literal['Low','Medium','High','Unknown']
    evidence: list[Text]
class Signal(Strict):
    value: bool
    evidence: list[Text]
class Outage(Strict):
    value: bool | None
    evidence: list[Text]
class Signals(Strict):
    active_service_outage: Outage
    insufficient_information: Signal
    conflicting_intents: Signal
class Money(Strict):
    amount: Text | None
    currency: Text | None
    period: Text | None
    components: Text | None
    evidence: list[Text]
    @model_validator(mode='after')
    def monetary(self):
        if self.amount is not None and not re.fullmatch(r'[0-9]+(?:\.[0-9]+)?', self.amount):
            raise ValueError('money must be a nonnegative plain decimal')
        return self
class Comparison(Strict):
    billed: Money
    expected: Money
class Analysis(Strict):
    _accepted: dict | None = PrivateAttr(default=None)
    category: Category
    priority: Literal['Low','Medium','High']
    confidence: float = Field(ge=0, le=1)
    core_issue: Text
    entities: list[Entity]
    urgency: Urgency
    signals: Signals
    billing_comparison: Comparison | None
    summary_sentences: list[Text] = Field(min_length=2, max_length=3)
    @model_validator(mode='after')
    def evidence(self, info: ValidationInfo):
        message = (info.context or {}).get('message')
        if not isinstance(message, str):
            raise ValueError('raw message context is required')
        def walk(value):
            if isinstance(value, dict):
                for key, item in value.items():
                    if key == 'evidence':
                        for excerpt in ([item] if isinstance(item, str) else item):
                            if excerpt not in message:
                                raise ValueError('evidence must be an exact message excerpt')
                    else:
                        walk(item)
            elif isinstance(value, list):
                for item in value: walk(item)
        walk(self.model_dump())
        if self.billing_comparison:
            from decimal import Decimal
            for fact in (self.billing_comparison.billed, self.billing_comparison.expected):
                if any(v is not None for v in (fact.amount, fact.currency, fact.period, fact.components)) and not fact.evidence:
                    raise ValueError('populated money requires evidence')
                if fact.amount is not None:
                    tokens = re.findall(r'(?<![\w.])[0-9]+(?:,[0-9]{3})*(?:\.[0-9]+)?(?![\w.])', ' '.join(fact.evidence))
                    if not any(Decimal(t.replace(',', '')) == Decimal(fact.amount) for t in tokens):
                        raise ValueError('amount lacks numeric evidence')
        outage = self.signals.active_service_outage
        if outage.value is not False and not outage.evidence:
            raise ValueError('true/unknown outage requires evidence')
        return self

def validate_analysis(payload: dict, message: str) -> Analysis:
    """Validate structure and exact excerpts; does not establish semantic truth."""
    analysis = Analysis.model_validate(payload, context={'message': message})
    analysis._accepted = analysis.model_dump()
    return analysis

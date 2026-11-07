import uuid

from django.db import models


class Request(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    principal = models.CharField(max_length=150)
    idempotency_key = models.CharField(max_length=128, null=True)
    source = models.CharField(max_length=20)
    message = models.TextField()
    status = models.CharField(max_length=16, default='pending')
    received_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    next_attempt_at = models.DateTimeField(null=True)
    dispatch_reserved_until = models.DateTimeField(null=True)
    dispatch_error = models.CharField(max_length=50, null=True)
    error = models.CharField(max_length=50, null=True)

    lease_until = models.DateTimeField(null=True, db_index=True)
    owner = models.UUIDField(null=True)

    class Meta:
        constraints = (models.UniqueConstraint(fields=['principal', 'idempotency_key'], name='principal_intake_key'),)


class Attempt(models.Model):
    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name='attempts')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True)
    error = models.CharField(max_length=50, null=True)
    latency_ms = models.FloatField(null=True)
    usage = models.JSONField(null=True)


class Result(models.Model):
    request = models.OneToOneField(Request, on_delete=models.CASCADE, related_name='accepted_result')
    attempt = models.OneToOneField(Attempt, on_delete=models.PROTECT)
    record = models.JSONField()

"""Test-only entrypoint; never imported by production settings."""

import json
import os
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django

django.setup()
from django.db import connection

from apps.triage import tasks
from apps.triage.models import Request, Result
from apps.triage.schemas import validate_analysis


def analyze(message):
    assert not connection.in_atomic_block
    if message in ("transient", "permanent"):
        exc = RuntimeError("synthetic failure")
        exc.code = "provider_transient" if message == "transient" else "provider_auth"
        raise exc
    a = {
        "category": "Technical Question",
        "priority": "Low",
        "confidence": 0.9,
        "core_issue": "Usage question.",
        "entities": [],
        "urgency": {"level": "Unknown", "evidence": []},
        "signals": {
            k: {"value": False, "evidence": []}
            for k in (
                "active_service_outage",
                "insufficient_information",
                "conflicting_intents",
            )
        },
        "billing_comparison": None,
        "summary_sentences": [
            "Customer asks about usage.",
            "No further details supplied.",
        ],
    }
    return SimpleNamespace(
        analysis=validate_analysis(a, message),
        model="synthetic-infrastructure-only",
        prompt_version="test",
        schema_version="test",
        latency_ms=1,
        usage=None,
    )


tasks.get_provider = lambda: SimpleNamespace(analyze=analyze)
if sys.argv[1] == "worker":
    from config.celery import app

    app.worker_main(["worker", "--pool=solo", "--loglevel=WARNING"])
elif sys.argv[1] == "web":
    from django.core.management import execute_from_command_line

    execute_from_command_line(["manage.py", "runserver", "0.0.0.0:8000", "--noreload"])
else:

    def http(path, data=None):
        req = urllib.request.Request(
            "http://web:8000" + path,
            data=json.dumps(data).encode() if data else None,
            headers={
                "Authorization": "Bearer infrastructure-test",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req) as r:
            return r.status, json.load(r)

    def post(message, key):
        return http(
            "/api/v1/requests/",
            {"source": "Email", "message": message, "idempotency_key": key},
        )

    def wait(pk, status):
        for _ in range(160):
            row = Request.objects.get(pk=pk)
            if row.status == status:
                return row
            time.sleep(0.25)
        raise AssertionError((row.status, status))

    for _ in range(60):
        try:
            post("usage?", "ready")
            break
        except OSError:
            time.sleep(0.5)
    with ThreadPoolExecutor(max_workers=8) as pool:
        replies = list(pool.map(lambda _: post("usage?", "concurrent"), range(8)))
    assert sorted(s for s, _ in replies) == [200] * 7 + [202]
    pk = replies[0][1]["id"]
    wait(pk, "completed")
    for _ in range(5):
        tasks.process.delay(pk)
    time.sleep(2)
    assert Request.objects.get(pk=pk).attempts.count() == 1
    assert Result.objects.filter(request_id=pk).count() == 1
    status = http(f"/api/v1/requests/{pk}/")[1]
    assert (
        status["result"]
        == http(f"/api/v1/requests/{pk}/export/")[1]
        == Result.objects.get(request_id=pk).record
    )
    for message, count in [("transient", 3), ("permanent", 1)]:
        _, r = post(message, message)
        row = wait(r["id"], "failed")
        assert row.attempts.count() == count
    from unittest.mock import patch

    from apps.intake.service import accept, dispatch

    with patch.object(tasks.process, "apply_async", side_effect=OSError("private")):
        row, _ = accept(
            "service",
            {
                "source": "Email",
                "message": "usage?",
                "idempotency_key": "publish-failure",
            },
        )
    row.refresh_from_db()
    assert row.status == "pending" and row.dispatch_error == "dispatch_failed"
    dispatch(row.pk)
    wait(row.pk, "completed")
    from datetime import timedelta

    from django.utils import timezone

    early = Request.objects.create(
        principal="service",
        source="Email",
        message="usage?",
        status="retrying",
        next_attempt_at=timezone.now() + timedelta(seconds=3),
    )
    tasks.process.delay(str(early.pk))
    time.sleep(1)
    assert early.attempts.count() == 0
    wait(early.pk, "completed")
    assert early.attempts.count() == 1
    print("PASS early delivery republishes countdown without consuming an attempt")
    print(
        json.dumps(
            list(
                Request.objects.order_by("received_at").values(
                    "message", "status", "error", "dispatch_error"
                )
            )
        )
    )
    print(
        "PASS concurrent HTTP intake, duplicate broker deliveries, status/export DB parity, outside-transaction mock inference, real bounded retries, permanent failure, publication failure and republish"
    )

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET

from apps.triage.models import Request


@login_required
@require_GET
def inbox(request):
    rows = Request.objects.select_related('accepted_result').order_by('-received_at')
    review_count = rows.filter(accepted_result__record__decision__human_escalation=True).count()
    if request.GET.get('queue') == 'review':
        rows = rows.filter(accepted_result__record__decision__human_escalation=True)
    return render(request, 'intake/inbox.html', {'rows': rows[:100], 'review_count': review_count})


@login_required
@require_GET
def tester(request):
    return render(request, 'intake/tester.html')


@login_required
@require_GET
def detail(request, request_id):
    row = get_object_or_404(Request.objects.select_related('accepted_result'), pk=request_id)
    record = row.accepted_result.record if row.status == 'completed' else None
    return render(request, 'intake/detail.html', {'row': row, 'record': record})

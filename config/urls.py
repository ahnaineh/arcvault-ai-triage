from django.conf import settings
from django.contrib import admin
from django.db import DatabaseError, connection
from django.http import JsonResponse
from django.urls import path
from redis import Redis
from redis.exceptions import RedisError


def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        Redis.from_url(settings.CELERY_BROKER_URL, socket_connect_timeout=2,
                       socket_timeout=2).ping()
    except (DatabaseError, RedisError):
        return JsonResponse({"status": "unavailable"}, status=503)
    return JsonResponse({"status": "ok"})


urlpatterns = [path("admin/", admin.site.urls), path("health/", health)]

from apps.intake.views import endpoint

urlpatterns += [
    path('api/v1/requests/', endpoint),
    path('api/v1/requests/<uuid:request_id>/', endpoint),
    path('api/v1/requests/<uuid:request_id>/export/', endpoint, {'export': True}),
]

from django.urls import include

urlpatterns += [path('', include('apps.intake.ui_urls'))]

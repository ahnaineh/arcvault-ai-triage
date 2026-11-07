from unittest.mock import patch

import pytest
from django.test import Client
from redis.exceptions import RedisError


@pytest.mark.django_db
def test_health():
    with patch("config.urls.Redis") as redis:
        response = Client(HTTP_HOST="localhost").get("/health/")
    assert response.status_code == 200
    redis.from_url.return_value.ping.assert_called_once()


@pytest.mark.django_db
def test_health_dependency_failure():
    with patch("config.urls.Redis.from_url", side_effect=RedisError):
        assert Client(HTTP_HOST="localhost").get("/health/").status_code == 503

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings

pytestmark = pytest.mark.django_db


@override_settings(DEBUG=True)
def test_demo_login_is_repeatable_and_not_privileged(django_user_model):
    call_command('create_demo_user')
    user = django_user_model.objects.get(username='admin')
    assert user.check_password('admin') and user.is_active
    assert not user.is_staff and not user.is_superuser
    password_hash = user.password
    call_command('create_demo_user')
    user.refresh_from_db()
    assert user.password == password_hash


@override_settings(DEBUG=False)
def test_demo_login_disabled_outside_local_mode(django_user_model):
    with pytest.raises(CommandError, match='DJANGO_DEBUG'):
        call_command('create_demo_user')
    assert not django_user_model.objects.exists()


@override_settings(DEBUG=True)
def test_demo_setup_preserves_existing_account(django_user_model):
    user = django_user_model.objects.create_user('admin', password='existing-password')
    with pytest.raises(CommandError, match='left unchanged'):
        call_command('create_demo_user')
    user.refresh_from_db()
    assert user.check_password('existing-password')

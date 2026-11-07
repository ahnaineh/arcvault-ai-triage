"""Create the documented local-demo login without changing existing accounts."""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Create the local demo login: admin / admin (DEBUG mode only).'

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError('Demo login requires DJANGO_DEBUG=true.')
        User = get_user_model()
        user, created = User.objects.get_or_create(username='admin')
        if created:
            user.set_password('admin')
            user.save(update_fields=['password'])
        elif not user.is_active or not user.check_password('admin') or user.is_staff or user.is_superuser:
            raise CommandError('An existing admin account was left unchanged.')
        self.stdout.write('Local demo login ready: admin / admin')

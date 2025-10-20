"""
Management command to test infrastructure components (Redis and Celery).
"""

from django.core.management.base import BaseCommand
from django.core.cache import cache
from config.celery import app as celery_app


class Command(BaseCommand):
    """Test infrastructure components."""

    help = 'Test Redis cache and Celery connections'

    def handle(self, *args, **options):
        """Execute the command."""
        self.stdout.write(self.style.WARNING('Testing infrastructure components...'))

        # Test Redis cache
        self.test_redis()

        # Test Celery
        self.test_celery()

        self.stdout.write(self.style.SUCCESS('\nAll infrastructure tests completed!'))

    def test_redis(self):
        """Test Redis cache connection."""
        self.stdout.write('\n--- Testing Redis Cache ---')

        try:
            # Test SET operation
            test_key = 'healthcare:test:connection'
            test_value = 'Infrastructure test successful'
            cache.set(test_key, test_value, timeout=60)
            self.stdout.write(self.style.SUCCESS('  ✓ Redis SET operation successful'))

            # Test GET operation
            retrieved_value = cache.get(test_key)
            if retrieved_value == test_value:
                self.stdout.write(self.style.SUCCESS('  ✓ Redis GET operation successful'))
            else:
                self.stdout.write(self.style.ERROR('  ✗ Redis GET returned unexpected value'))

            # Test DELETE operation
            cache.delete(test_key)
            if cache.get(test_key) is None:
                self.stdout.write(self.style.SUCCESS('  ✓ Redis DELETE operation successful'))
            else:
                self.stdout.write(self.style.ERROR('  ✗ Redis DELETE failed'))

            # Test cache info
            from django_redis import get_redis_connection
            redis_conn = get_redis_connection("default")
            info = redis_conn.info()
            self.stdout.write(f'  ℹ Redis version: {info.get("redis_version", "unknown")}')
            self.stdout.write(f'  ℹ Connected clients: {info.get("connected_clients", "unknown")}')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ Redis connection failed: {str(e)}'))

    def test_celery(self):
        """Test Celery configuration."""
        self.stdout.write('\n--- Testing Celery Configuration ---')

        try:
            # Test Celery app configuration
            self.stdout.write(f'  ℹ Celery broker URL: {celery_app.conf.broker_url}')
            self.stdout.write(f'  ℹ Celery result backend: {celery_app.conf.result_backend}')
            self.stdout.write(f'  ℹ Celery task serializer: {celery_app.conf.task_serializer}')
            self.stdout.write(self.style.SUCCESS('  ✓ Celery configuration loaded'))

            # Check if Celery workers are running
            inspect = celery_app.control.inspect()
            active_workers = inspect.active()

            if active_workers:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Celery workers detected: {list(active_workers.keys())}'))
            else:
                self.stdout.write(self.style.WARNING('  ⚠ No active Celery workers detected'))
                self.stdout.write('    Run "celery -A config worker -l info" to start workers')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ Celery configuration check failed: {str(e)}'))

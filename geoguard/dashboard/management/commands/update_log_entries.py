# dashboard/management/commands/update_log_entries.py

from django.core.management.base import BaseCommand
from django.contrib.admin.models import LogEntry
from dashboard.models import CustomUser

class Command(BaseCommand):
    help = 'Update LogEntry user references to CustomUser'

    def handle(self, *args, **kwargs):
        log_entries = LogEntry.objects.all()
        for entry in log_entries:
            try:
                custom_user = CustomUser.objects.get(id=entry.user_id)
                entry.user = custom_user
                entry.save()
            except CustomUser.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'CustomUser with id {entry.user_id} does not exist'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error updating LogEntry with id {entry.id}: {e}'))

        self.stdout.write(self.style.SUCCESS('Successfully updated LogEntry user references'))

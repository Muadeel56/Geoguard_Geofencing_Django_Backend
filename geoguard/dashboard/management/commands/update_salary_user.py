from django.core.management.base import BaseCommand
from dashboard.models import Salary, CustomUser

class Command(BaseCommand):
    help = 'Update Salary records with associated users'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting salary update'))
        
        salaries_without_user = Salary.objects.filter(user__isnull=True)

        for salary in salaries_without_user:
            user = CustomUser.objects.filter(salary=salary).first()

            if user:
                salary.user = user
                salary.save()
                self.stdout.write(self.style.SUCCESS(f'Updated salary for user: {user.username}'))
            else:
                self.stdout.write(self.style.WARNING(f'No user found for salary ID: {salary.id}'))

        self.stdout.write(self.style.SUCCESS('Finished updating salary records.'))

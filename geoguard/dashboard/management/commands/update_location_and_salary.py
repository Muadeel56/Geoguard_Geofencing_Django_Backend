from django.core.management.base import BaseCommand
from django.utils import timezone
from dashboard.models import CustomUser, LocationHistory, UserSalary, Salary
from datetime import timedelta
from collections import defaultdict
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Update user location history and calculate salaries'

    def handle(self, *args, **kwargs):
        try:
            print("Command Called")
            self.stdout.write(self.style.SUCCESS('Starting update and salary calculation'))
            self.update_user_location_history()
            self.calculate_monthly_salaries()
            self.stdout.write(self.style.SUCCESS('Successfully completed command execution'))
        except Exception as e:
            logger.error(f"Error during command execution: {e}")
            self.stdout.write(self.style.ERROR(f"Error during command execution: {e}"))

    def update_user_location_history(self):
        now = timezone.now()
        users = CustomUser.objects.filter(role=CustomUser.MONITORED)
        if not users.exists():
            self.stdout.write(self.style.WARNING('No monitored users found'))
        
        location_histories = []
        for user in users:
            latitude = 0.0
            longitude = 0.0
            is_within_geofence = True
            location = LocationHistory(
                user=user,
                latitude=latitude,
                longitude=longitude,
                is_within_geofence=is_within_geofence,
                record_at=now
            )
            location_histories.append(location)
        
        LocationHistory.objects.bulk_create(location_histories)
        self.stdout.write(self.style.SUCCESS('Successfully updated user location history'))

    def calculate_monthly_salaries(self):
        now = timezone.now()
        first_day_of_current_month = now.replace(day=1)
        last_month_end = first_day_of_current_month - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)

        users = CustomUser.objects.filter(role=CustomUser.MONITORED)
        if not users.exists():
            self.stdout.write(self.style.WARNING('No monitored users found'))

        for user in users:
            daily_hours_outside = self.calculate_daily_hours_outside_geofence(user, last_month_start, last_month_end)
            self.stdout.write(self.style.SUCCESS(f'User: {user.username}'))
            self.stdout.write(self.style.SUCCESS(f'Daily Hours Outside Geofence: {daily_hours_outside}'))

            # Fetch salary from user
            if user.salary is None:
                self.stdout.write(self.style.WARNING(f'No salary record for user: {user.username}'))
                continue

            salary = user.salary
            total_deduction = Decimal('0.00')
            for date, hours in daily_hours_outside.items():
                if hours > 2:
                    daily_salary = Decimal(salary.basic_pay + salary.allowances) / Decimal('30')
                    hours_as_decimal = Decimal(hours)
                    deduction = daily_salary * (hours_as_decimal / Decimal('8'))
                    total_deduction += deduction

            remaining_salary = Decimal(salary.basic_pay) - total_deduction

            # Get or create the UserSalary record
            user_salary, created = UserSalary.objects.update_or_create(
                user=user,
                month=last_month_start.month,
                year=last_month_start.year,
                defaults={
                    'salary': salary,
                    'bonus': Decimal('0.00'),
                    'monthly_salary': max(Decimal('0.00'), remaining_salary),
                    'organization': user.organization  # Adjust this if needed
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f'Created UserSalary record for user: {user.username}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Updated UserSalary record for user: {user.username}'))

            self.stdout.write(self.style.SUCCESS(f'Remaining Salary = {remaining_salary:.2f}'))
            self.stdout.write(self.style.SUCCESS(f'Monthly Salary Set To = {user_salary.monthly_salary:.2f}'))

        self.stdout.write(self.style.SUCCESS('Successfully calculated and updated monthly salaries'))

    def calculate_daily_hours_outside_geofence(self, user, start_date, end_date):
        daily_hours = defaultdict(float)
        location_histories = LocationHistory.objects.filter(
            user=user,
            record_at__range=(start_date, end_date)
        )
        
        for history in location_histories:
            if not history.is_within_geofence:
                date = history.record_at.date()
                daily_hours[date] += 1  # Assuming 1 hour for each record outside geofence

        return daily_hours

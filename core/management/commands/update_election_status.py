# core/management/commands/update_election_status.py

from django.core.management.base import BaseCommand
from django.utils.timezone import now
from core.models import Election

class Command(BaseCommand):
    help = 'Updates election statuses automatically'

    def handle(self, *args, **kwargs):
        today = now().date()

        # Update 'Upcoming' to 'Ongoing'
        Election.objects.filter(start_date__lte=today, status='Upcoming').update(status='Ongoing')

        # Update 'Ongoing' to 'Completed'
        Election.objects.filter(end_date__lt=today, status='Ongoing').update(status='Completed')

        self.stdout.write(self.style.SUCCESS("Election statuses updated!"))

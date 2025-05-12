# core/tasks.py

from celery import shared_task
from django.utils.timezone import now
from .models import Election

@shared_task
def update_election_status():
    today = now().date()

    # Update elections from 'Upcoming' to 'Ongoing'
    Election.objects.filter(start_date__lte=today, status='Upcoming').update(status='Ongoing')

    # Update elections from 'Ongoing' to 'Completed'
    Election.objects.filter(end_date__lt=today, status='Ongoing').update(status='Completed')

    print("Election statuses updated successfully!")


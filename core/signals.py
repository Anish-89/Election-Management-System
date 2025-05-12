# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Election, Candidate
from .models import AuditLog

def record_audit_log(action_type, performed_by, details=""):
    AuditLog.objects.create(
        action_type=action_type,
        performed_by=performed_by,
        details=details
    )

@receiver(post_save, sender=Election)
def assign_election_to_candidates(sender, instance, created, **kwargs):
    if created:
        # Automatically add the new election to all verified candidates
        verified_candidates = Candidate.objects.filter(is_verified=True)
        for candidate in verified_candidates:
            candidate.eligible_elections.add(instance)


from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Election)
def update_candidate_eligibility(sender, instance, **kwargs):
    # Fetch candidates matching the election type
    candidates = Candidate.objects.filter(election_type=instance.election_type)
    for candidate in candidates:
        if instance.status == 'Upcoming':
            candidate.eligible_elections.add(instance)
        else:
            candidate.eligible_elections.remove(instance)


@receiver(post_save, sender=Candidate)
def update_elections_for_candidate(sender, instance, **kwargs):
    elections = Election.objects.filter(
        status='Upcoming',
        election_type=instance.election_type
    )
    instance.eligible_elections.set(elections)

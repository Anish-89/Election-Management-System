# models.py
from django.db import models
from django.utils.timezone import now, timedelta
from django.contrib.auth.models import User
import random


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} - {self.email}"


class Election(models.Model):
    name = models.CharField(max_length=200)
    start_date = models.DateField(default=now)
    end_date = models.DateField(default=now)
    region = models.CharField(max_length=200)
    election_type = models.CharField(
        max_length=20, 
        choices=[
            ('Rajya Sabha', 'Rajya Sabha'),
            ('Lok Sabha', 'Lok Sabha'),
            ('Others', 'Others'),
        ], 
        default='Others'
    )
    STATUS_CHOICES = [
        ('Ongoing', 'Ongoing'),
        ('Completed', 'Completed'),
        ('Upcoming', 'Upcoming'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Upcoming')
    description = models.TextField(blank=True)
    result_published = models.BooleanField(default=False)  # New field for result status
    winner = models.ForeignKey('Candidate', null=True, blank=True, on_delete=models.SET_NULL)  # Store winner

    def __str__(self):
        return self.name



class Candidate(models.Model):
    ELECTION_TYPES = [
        ('Rajya Sabha', 'Rajya Sabha'),
        ('Lok Sabha', 'Lok Sabha'),
        ('Others', 'Others'),
    ]

    # Existing fields
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField()
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    political_party = models.CharField(max_length=255, null=True, blank=True)
    id_proof = models.FileField(upload_to='documents/id_proofs/')
    profile_image = models.ImageField(upload_to='candidate_profile_images/', null=True, blank=True)
    verification_status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')],
        default='Pending'
    )
    verification_notes = models.TextField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    # New field for election type
    election_type = models.CharField(max_length=20, choices=ELECTION_TYPES, default='Others')

    # Relationships
    eligible_elections = models.ManyToManyField('Election', blank=True, related_name='candidates')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.political_party})"


class Voter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    date_of_birth = models.DateField()
    id_proof = models.FileField(upload_to='documents/id_proofs/')
    profile_image = models.ImageField(upload_to='voter_profile_images/', null=True, blank=True)
    election_type = models.CharField(
        max_length=20,
        choices=[
            ('Rajya Sabha', 'Rajya Sabha'),
            ('Lok Sabha', 'Lok Sabha'),
            ('Others', 'Others'),
        ],
        default='Others'
    )
    verification_status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Approved', 'Approved'),
            ('Rejected', 'Rejected')
        ],
        default='Pending'
    )
    verification_notes = models.TextField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True)  # Unique ID for students
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.name} ({self.student_id})"


class OTPVerification(models.Model):
    phone = models.CharField(max_length=15, unique=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        expiry_time = self.created_at + timedelta(minutes=5)  # OTP expires in 5 min
        return now() <= expiry_time  # Check if OTP is still valid


class Vote(models.Model):
    voter = models.ForeignKey('Voter', on_delete=models.CASCADE)
    election = models.ForeignKey('Election', on_delete=models.CASCADE)
    candidate = models.ForeignKey('Candidate', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('voter', 'election')  # Ensures one vote per election

    def __str__(self):
        return f"{self.voter.name} voted in {self.election.name}"


class Nomination(models.Model):
    
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='nominations')
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='nominations')  # Added field
    
    status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')],
        default='Pending'
    )
    remarks = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.candidate.name} - {self.election.name}"  # Updated field reference


class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    admin_user = models.ForeignKey(User, null=True, blank=True, related_name="admin_logs", on_delete=models.SET_NULL)
    candidate = models.ForeignKey('Candidate', null=True, blank=True, on_delete=models.SET_NULL)
    voter = models.ForeignKey('Voter', null=True, blank=True, on_delete=models.SET_NULL)
    action = models.TextField()
    details = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action}"

class Feedback(models.Model):
    ROLE_CHOICES = [
        ('Candidate', 'Candidate'),
        ('Voter', 'Voter'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    name = models.CharField(max_length=100)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.role}) - {self.submitted_at.strftime('%Y-%m-%d %H:%M')}"


class Report(models.Model):
    REPORT_TYPES = [
        ('Election Activity', 'Election Activity'),
        ('Voter Turnout', 'Voter Turnout'),
        ('Election Results', 'Election Results'),
        ('Custom', 'Custom')
    ]

    name = models.CharField(max_length=255)  # Report name
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)  # Admin user
    generated_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='reports/')  # Stores the generated PDF/Excel file

    def __str__(self):
        return f"{self.name} ({self.report_type}) - {self.generated_at}"

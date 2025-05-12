from django.contrib import messages
from .forms import ContactForm
from .models import ContactMessage
from core.utils import send_admin_notification
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login,logout
import datetime
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from .models import Election, Candidate, Nomination,AuditLog,Voter,Vote,Report,Feedback,Student
from .forms import  ElectionForm,CandidateRegistrationForm,CandidateProfileForm
from django.contrib.auth.models import User
from django.core.mail import send_mail
import logging
import os
from .utils import generate_random_password,send_email,send_sms_notification,send_otp, verify_otp
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .forms import LokSabhaNominationForm, RajyaSabhaNominationForm, OthersNominationForm,FeedbackForm
from .forms import CandidateUsernameChangeForm, VoterRegistrationForm,VoterUsernameChangeForm
from .forms import VoteForm,VoterProfileForm,VoterPasswordUpdateForm,FeedbackForm
from django.utils import timezone
from django.http import Http404,FileResponse, HttpResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db.models import Count
from django.db.models import Q
from django.utils.timezone import now
import pandas as pd
from django.utils.timezone import now
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
from django.core.files.base import File
from reportlab.lib import colors
from datetime import datetime
from itertools import groupby
from operator import attrgetter
import json
from django.http import JsonResponse
import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend for Matplotlib
import matplotlib.pyplot as plt
import numpy as np
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from django.core.files import File



# Homepage view
def home(request):
    return render(request, 'core/home.html')

# About page view
def about(request):
    return render(request, 'core/about.html')

# Contact page view
def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save the data to the database
            contact_message = ContactMessage.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                message=form.cleaned_data['message']
            )
            # Send email notification to Admin
            send_admin_notification(
                name=contact_message.name,
                email=contact_message.email,
                message=contact_message.message
            )
            # Display success message
            messages.success(request, "Your message has been sent successfully!")
            form = ContactForm()  # Clear the form
        else:
            messages.error(request, "There was an error in your submission. Please try again.")
    else:
        form = ContactForm()
    
    return render(request, 'core/contact.html', {'form': form})


def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            subject = "Login Notification"
            message = f"Dear {user.username},\n\nYou have successfully logged into the election portal."
            send_email(subject, message, user.email)
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid credentials or access denied.')
    return render(request, 'core/home.html')



def admin_dashboard(request):
    elections = Election.objects.all()

    for election in elections:
        if election.end_date < now().date():
            election.status = 'Completed'
        elif election.start_date <= now().date() <= election.end_date:
            election.status = 'Ongoing'
        else:
            election.status = 'Upcoming'

        if election.id:  # Ensure it has an ID before saving
            election.save()

    completed_elections = elections.filter(status='Completed')

    # Debugging election IDs before passing them
    for e in completed_elections:
        print(f"Passing to Template: Election ID={e.id}, Name={e.name}, Status={e.status}")

    context = {
        'total_elections': elections.count(),
        'total_voters': Voter.objects.count(),
        'total_candidates': Candidate.objects.count(),
        'completed_elections': completed_elections,
    }

    return render(request, 'core/admin_dashboard.html', context)


def logout_view(request):
    logout(request)
    return redirect('home')


def list_elections(request):
    elections = Election.objects.order_by('-start_date')
    return render(request, 'core/list_elections.html', {'elections': elections})

def create_election(request):
    if request.method == 'POST':
        form = ElectionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_elections')
    else:
        form = ElectionForm()
    return render(request, 'core/election_form.html', {'form': form})

def update_election(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    if request.method == 'POST':
        form = ElectionForm(request.POST, instance=election)
        if form.is_valid():
            form.save()
            return redirect('list_elections')
    else:
        form = ElectionForm(instance=election)
    return render(request, 'core/election_form.html', {'form': form})

def delete_election(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    election.delete()
    return redirect('list_elections')


@login_required
def eligible_elections(request, id):
    try:
        # Initialize variables
        voter = None
        candidate = None
        elections = None

        # Candidate logic
        if hasattr(request.user, 'candidate'):
            candidate = Candidate.objects.get(user=request.user)

            upcoming_elections = Election.objects.filter(
                status='Upcoming', election_type=candidate.election_type
            )
            ongoing_elections = Election.objects.filter(
                status='Ongoing', election_type=candidate.election_type
            )
            completed_elections = Election.objects.filter(
                status='Completed', election_type=candidate.election_type
            )

            template = 'candidate/eligible_elections.html'

        # Voter logic
        elif hasattr(request.user, 'voter'):
            voter = Voter.objects.get(user=request.user)

            # Ensure voter is verified
            if not voter.is_verified:
                messages.error(request, "Your profile is not verified yet.")
                return redirect('voter_dashboard')

            upcoming_elections = Election.objects.filter(
                status='Upcoming', election_type=voter.election_type
            )
            ongoing_elections = Election.objects.filter(
                status='Ongoing', election_type=voter.election_type
            )
            completed_elections = Election.objects.filter(
                status='Completed', election_type=voter.election_type
            )

            template = 'voter/voter_eligible_elections.html'

        else:
            messages.error(request, "Profile not found.")
            return redirect('home')

        # Render the appropriate template with categorized elections
        return render(request, template, {
            'upcoming_elections': upcoming_elections,
            'ongoing_elections': ongoing_elections,
            'completed_elections': completed_elections,
            'voter': voter,
            'candidate': candidate
        })

    except (Candidate.DoesNotExist, Voter.DoesNotExist):
        messages.error(request, "Profile not found.")
        return redirect('home')

@login_required
def submit_nomination(request, election_id):
    candidate = Candidate.objects.get(user=request.user)
    election = Election.objects.get(id=election_id)

    # Ensure the candidate is eligible for the election
    if election not in candidate.eligible_elections.filter(status='Upcoming'):
        return redirect('eligible_elections', id=candidate.id)  # Fixed

    # Prevent duplicate nominations
    if Nomination.objects.filter(candidate=candidate, election=election).exists():
        messages.error(request, "You have already submitted a nomination for this election.")
        return redirect('eligible_elections', id=candidate.id)  # Fixed

    # Choose the form based on election type
    if election.election_type == 'Lok Sabha':
        FormClass = LokSabhaNominationForm
    elif election.election_type == 'Rajya Sabha':
        FormClass = RajyaSabhaNominationForm
    else:
        FormClass = OthersNominationForm

    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES, candidate=candidate)
        if form.is_valid():
            nomination = form.save(commit=False)
            nomination.candidate = candidate
            nomination.election = election
            nomination.save()

            # Automatically register the candidate for the election
            candidate.eligible_elections.add(election)

            messages.success(request, "Your nomination has been successfully submitted!")
            return redirect('eligible_elections', id=candidate.id)  # Fixed
    else:
        form = FormClass(candidate=candidate)

    return render(request, 'candidate/submit_nomination.html', {'form': form, 'election': election, 'candidate': candidate})


@login_required
def view_results(request):
    voter = None
    candidate = None
    completed_elections = Election.objects.filter(status='Completed')

    new_results = []
    past_results = []

    for election in completed_elections:
        results = (
            Vote.objects.filter(election=election)
            .values('candidate__id', 'candidate__name')
            .annotate(total_votes=Count('candidate'))
            .order_by('-total_votes')
        )

        total_voters = Voter.objects.count()
        total_votes_cast = Vote.objects.filter(election=election).count()

        # Prepare Chart.js data
        labels = [result["candidate__name"] for result in results]
        vote_counts = [result["total_votes"] for result in results]

        election_data = {
            'id': election.id,
            'name': election.name,
            'election_type': election.election_type,
            'winner': election.winner,
            'results': results,
            'total_voters': total_voters,
            'total_votes_cast': total_votes_cast,
            'chart_labels': json.dumps(labels),
            'chart_data': json.dumps(vote_counts),
            'published_days_ago': (now().date() - election.end_date).days,
        }

        # Categorize as new or past result
        if election_data['published_days_ago'] <= 2:
            new_results.append(election_data)
        else:
            past_results.append(election_data)

    # Determine user role and template
    if request.user.is_superuser:
        template = 'core/results.html'
    elif hasattr(request.user, 'candidate'):
        candidate = Candidate.objects.get(user=request.user)
        template = 'candidate/results.html'
    elif hasattr(request.user, 'voter'):
        voter = Voter.objects.get(user=request.user)
        template = 'voter/results.html'
    else:
        messages.error(request, "Profile not found.")
        return redirect('home')

    return render(request, template, {
        'new_results': new_results,
        'past_results': past_results,
        'voter': voter,
        'candidate': candidate
    })


@login_required
def result_detail(request, election_id):
    """View for detailed election results."""
    election = get_object_or_404(Election, id=election_id, status='Completed')

    results = (
        Vote.objects.filter(election=election)
        .values('candidate__id', 'candidate__name')
        .annotate(total_votes=Count('candidate'))
        .order_by('-total_votes')
    )

    total_voters = Voter.objects.count()
    total_votes_cast = Vote.objects.filter(election=election).count()

    # Prepare Chart.js data
    labels = [result["candidate__name"] for result in results]
    vote_counts = [result["total_votes"] for result in results]

    election_data = {
        'id': election.id,
        'name': election.name,
        'election_type': election.election_type,
        'winner': election.winner,
        'results': results,
        'total_voters': total_voters,
        'total_votes_cast': total_votes_cast,
        'chart_labels': json.dumps(labels), 
        'chart_data': json.dumps(vote_counts),  
    }

    return render(request, 'core/result_detail.html', {'election': election_data})


@staff_member_required
def view_audit_logs(request):
    admin_logs = AuditLog.objects.filter(admin_user__isnull=False).order_by('-timestamp')
    candidate_logs = AuditLog.objects.filter(candidate__isnull=False).order_by('candidate', '-timestamp')
    voter_logs = AuditLog.objects.filter(voter__isnull=False).order_by('voter', '-timestamp')

    # Group logs by Candidate
    candidate_logs_grouped = {candidate: list(logs) for candidate, logs in groupby(candidate_logs, key=attrgetter('candidate'))}
    
    # Group logs by Voter
    voter_logs_grouped = {voter: list(logs) for voter, logs in groupby(voter_logs, key=attrgetter('voter'))}

    return render(request, 'core/audit_logs.html', {
        'admin_logs': admin_logs,
        'candidate_logs_grouped': candidate_logs_grouped,
        'voter_logs_grouped': voter_logs_grouped,
    })



def candidate_list(request):
    candidates = Candidate.objects.all()
    return render(request, 'core/candidate_list.html', {'candidates': candidates})

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def send_otp_request(request):
    """Handles OTP request during registration."""
    student_id = request.GET.get('student_id')

    try:
        student = Student.objects.get(student_id=student_id)
        if send_otp(student.phone):
            return JsonResponse({"success": True, "message": "OTP sent successfully"})
        else:
            return JsonResponse({"success": False, "message": "Failed to send OTP"})
    except Student.DoesNotExist:
        return JsonResponse({"success": False, "message": "Invalid Student ID"})


def candidate_registration(request):
    if request.method == 'POST':
        form = CandidateRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            student_id = form.cleaned_data['student_id']
            otp = form.cleaned_data['otp']
            try:
                student = Student.objects.get(student_id=student_id)
            except Student.DoesNotExist:
                messages.error(request, "Invalid Student ID")
                return redirect('candidate_registration')

            if not verify_otp(student.phone, otp):
                messages.error(request, "Invalid OTP")
                return redirect('candidate_registration')

            # Save the candidate details
            candidate = form.save()

            # Send email notification
            subject = "Candidate Registration Received"
            message = f"""
                Dear {candidate.name},

                Your registration for the election as a candidate has been received.
                Here are your details:
                
                Name: {candidate.name}
                Email: {candidate.email}
                Political Party: {candidate.political_party}
                Election Type: {candidate.election_type}

                Please wait for admin approval.

                Regards,
                Election Management Team
            """
            send_email(subject, message, candidate.email)

            messages.success(request, "Registration successful! Please wait for admin approval.")
            return redirect('candidate_registration')
    else:
        form = CandidateRegistrationForm()

    return render(request, 'core/candidate_registration.html', {'form': form})


def verify_candidate(request, id):
    candidate = get_object_or_404(Candidate, id=id)
    
    if request.method == 'POST':
        verification_status = request.POST.get('verification_status')
        verification_notes = request.POST.get('verification_notes')

        candidate.verification_status = verification_status
        candidate.verification_notes = verification_notes
        candidate.is_verified = (verification_status == 'Approved')
        candidate.save()

        if verification_status == 'Approved' and not candidate.user:
            username = f"candidate_{candidate.id}"
            password = generate_random_password()  # Use custom password generator
            user = User.objects.create_user(
                username=username,
                password=password,
                email=candidate.email,
                first_name=candidate.name.split()[0],
                last_name=" ".join(candidate.name.split()[1:]) if len(candidate.name.split()) > 1 else "",
            )
            candidate.user = user
            candidate.save()

            # Use the email utility function
            email_sent = send_email(
                'Your Candidate Login Credentials',
                f"Hello {candidate.name},\n\nYour account has been approved. "
                f"Here are your login details:\n\n"
                f"Username: {username}\nPassword: {password}\n\n"
                "Please log in and change your password as soon as possible.\n\nThank you!",
                candidate.email
            )
            if not email_sent:
                print("Failed to send approval email.")

        return redirect('candidate_list')

    return render(request, 'core/verify_candidate.html', {'candidate': candidate})


def candidate_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if hasattr(user, 'candidate'):
                login(request, user)

                subject = "Login Notification"
                message = f"Dear {user.username},\n\nYou have successfully logged into the election portal."
                send_email(subject, message, user.email)
                
                
                return redirect('candidate_dashboard')
            else:
                messages.error(request, 'You are not authorized as a candidate.')

        else:
            messages.error(request, 'Invalid username or password.')

            
    return render(request, 'core/home.html')


@login_required
def candidate_dashboard(request):
    candidate = Candidate.objects.get(user=request.user)
    upcoming_elections_count = Election.objects.filter(status='Upcoming').count()
    participated_elections_count = Nomination.objects.filter(candidate=candidate).count()
    campaign_status = "Active" if candidate.verification_status == "Approved" else "Inactive"

    context = {
        'candidate': candidate,
        'upcoming_elections_count': upcoming_elections_count,
        'participated_elections_count': participated_elections_count,
        'campaign_status': campaign_status,
    }
    return render(request, 'core/candidate_dashboard.html', context)


@login_required
def candidate_profile(request):
    candidate = Candidate.objects.get(user=request.user)
    
    if request.method == "POST":
        form = CandidateProfileForm(request.POST, request.FILES, instance=candidate)
        if form.is_valid():
            form.save()
            return redirect('candidate_profile')

    else:
        form = CandidateProfileForm(instance=candidate)

    return render(request, 'candidate/profile.html', {'candidate': candidate, 'form': form})  

@login_required
def update_candidate_profile(request):
    candidate = Candidate.objects.get(user=request.user)

    if request.method == 'POST':
        form = CandidateProfileForm(request.POST, request.FILES, instance=candidate)
        if form.is_valid():
            # Save changes
            updated_candidate = form.save(commit=False)

            # Audit changes
            changes = []
            for field, value in form.cleaned_data.items():
                old_value = getattr(candidate, field, None)
                if old_value != value:
                    changes.append(f"{field}: '{old_value}' -> '{value}'")

            updated_candidate.save()

        
            messages.success(request, "Profile updated successfully.")
            return redirect('candidate_profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CandidateProfileForm(instance=candidate)

    return render(request, 'candidate/update_profile.html', {'form': form , 'candidate': candidate} )



@login_required
def candidate_audit_logs(request):
    candidate = Candidate.objects.get(user=request.user)
    audit_logs = AuditLog.objects.filter(candidate=candidate).order_by('-timestamp')

    return render(request, 'candidate/audit_logs.html', {
        'audit_logs': audit_logs,
        'candidate': candidate,
    })


def candidate_create(request):
    if request.method == 'POST':
        form = CandidateRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Candidate added successfully.')
            return redirect('candidate_list')
    else:
        form = CandidateRegistrationForm()
    return render(request, 'core/candidate_form.html', {'form': form})

def candidate_update(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk)
    if request.method == 'POST':
        form = CandidateRegistrationForm(request.POST, instance=candidate)
        if form.is_valid():
            form.save()
            messages.success(request, 'Candidate updated successfully.')
            return redirect('candidate_list')
    else:
        form = CandidateRegistrationForm(instance=candidate)
    return render(request, 'core/candidate_form.html', {'form': form})

def candidate_delete(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk)
    candidate.delete()
    messages.success(request, 'Candidate deleted successfully.')
    return redirect('candidate_list')


@login_required
def update_credentials(request):
    user = request.user
    candidate = None

    if hasattr(user, 'candidate'):
        candidate = user.candidate  # Fetch candidate object

    if request.method == 'POST':
        password_form = PasswordChangeForm(user=user, data=request.POST)
        username_form = CandidateUsernameChangeForm(instance=user, data=request.POST)

        if password_form.is_valid() and username_form.is_valid():
            username_form.save()
            updated_user = password_form.save()
            update_session_auth_hash(request, updated_user)
            messages.success(request, "Your username and password were successfully updated!")
            return redirect('candidate_dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        password_form = PasswordChangeForm(user=user)
        username_form = CandidateUsernameChangeForm(instance=user)

    context = {
        'password_form': password_form,
        'username_form': username_form,
        'candidate': candidate,  # Ensure candidate is passed to the template
    }
    return render(request, 'core/update_credentials.html', context)


def voter_registration(request):
    if request.method == 'POST':
        form = VoterRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            student_id = form.cleaned_data['student_id']
            otp = form.cleaned_data['otp']
            student = Student.objects.get(student_id=student_id)

            if not verify_otp(student.phone, otp):
                messages.error(request, "Invalid OTP")
                return redirect('voter_registration')

            voter = form.save()
            # Send email confirmation
            subject = "Voter Registration Received"
            message = f"""
                Dear {voter.name},

                Your registration for the election as a voter has been received.
                Here are your details:
                
                Name: {voter.name}
                Email: {voter.email}
                
                Election Type: {voter.election_type}

                Please wait for admin approval.

                Regards,
                Election Management Team
            """
            send_email(subject, message, voter.email)

            messages.success(request, "Registration successful!")
            return redirect('voter_registration')
    else:
        form = VoterRegistrationForm()
    return render(request, 'voter/voter_registration.html', {'form': form})



def verify_voter(request, id):
    voter = get_object_or_404(Voter, id=id)

    if request.method == 'POST':
        verification_status = request.POST.get('verification_status')
        verification_notes = request.POST.get('verification_notes')

        voter.verification_status = verification_status
        voter.verification_notes = verification_notes
        voter.is_verified = (verification_status == 'Approved')
        voter.save()

        if verification_status == 'Approved' and not voter.user:
            username = f"voter_{voter.id}"
            password = generate_random_password()
            user = User.objects.create_user(
                username=username,
                password=password,
                email=voter.email,
                first_name=voter.name.split()[0],
                last_name=" ".join(voter.name.split()[1:]) if len(voter.name.split()) > 1 else "",
            )
            voter.user = user
            voter.save()

            # Send approval email
            email_sent = send_email(
                'Your Voter Login Credentials',
                f"Hello {voter.name},\n\nYour account has been approved. "
                f"Here are your login details:\n\n"
                f"Username: {username}\nPassword: {password}\n\n"
                "Please log in and change your password as soon as possible.\n\nThank you!",
                voter.email
            )
            if not email_sent:
                print("Failed to send approval email.")

        return redirect('voter_list')

    return render(request, 'core/verify_voter.html', {'voter': voter})



@login_required
def voter_list(request):
    voters = Voter.objects.all()
    return render(request, 'core/voter_list.html', {'voters': voters})


def voter_delete(request, id):
    voter = get_object_or_404(Voter, id=id)
    voter.delete()
    messages.success(request, 'Voter deleted successfully.')
    return redirect('voter_list')

def voter_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if hasattr(user, 'voter'):
                login(request, user)

                # Send login notification email
                subject = "Login Notification"
                message = f"Dear {user.username},\n\nYou have successfully logged into the election portal."
                send_email(subject, message, user.email)
                return redirect('voter_dashboard')
            else:
                messages.error(request, 'You are not authorized as a Voter.')

        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'core/home.html')


@login_required
def voter_dashboard(request):
    voter = get_object_or_404(Voter, user=request.user)

    if not voter.id:
        messages.error(request, "Voter profile not found.")
        return redirect('home')  # Redirect to a safe page

    total_elections = Election.objects.count()
    upcoming_elections = Election.objects.filter(start_date__gte=timezone.now())
    election_id = upcoming_elections.first().id if upcoming_elections.exists() else None
    cast_vote = Vote.objects.filter(voter=voter).count()
    
    context = {
        'user': request.user,
        'voter': voter,
        'voter_id': voter.id,  # Ensure voter_id exists
        'total_elections': total_elections,
        'upcoming_elections': upcoming_elections,
        'election_id': election_id,
        'votes_cast': cast_vote,
    }
    return render(request, 'voter/voter_dashboard.html', context)

@login_required
def voter_profile(request, id):
    voter = get_object_or_404(Voter, id=id)
    return render(request, 'voter/voter_profile.html', {'voter': voter })


@login_required
def update_voter_profile(request, id):
    voter = get_object_or_404(Voter, id=id)
    if request.method == 'POST':
        form = VoterProfileForm(request.POST, request.FILES, instance=voter)
        if form.is_valid():
            form.save()
            return redirect('voter_dashboard')  # Redirect to dashboard or profile page
    else:
        form = VoterProfileForm(instance=voter)

    return render(request, 'voter/update_voter_profile.html', {
        'form': form,
        'voter': voter  # Pass voter to the template
    })

@login_required
def update_voter_credentials(request, id):
    voter = get_object_or_404(Voter, id=id)
    user = voter.user  # Use the related user for authentication

    if request.method == 'POST':
        password_form = PasswordChangeForm(user=user, data=request.POST)
        username_form = VoterUsernameChangeForm(instance=user, data=request.POST)

        if password_form.is_valid() and username_form.is_valid():
            # Save the username and password changes
            username_form.save()
            updated_user = password_form.save()

            # Keep the user logged in after password change
            update_session_auth_hash(request, updated_user)

            messages.success(request, "Your username and password were successfully updated!")
            return redirect('voter_dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        password_form = PasswordChangeForm(user=user)
        username_form = VoterUsernameChangeForm(instance=user)

    context = {
        'password_form': password_form,
        'username_form': username_form,
        'voter': voter,
    }
    return render(request, 'voter/update_voter_credentials.html', context)

@login_required
def cast_vote(request, election_id):
    print(f"Requested Election ID: {election_id}")  # Debugging
    try:
        voter = get_object_or_404(Voter, user=request.user)
        election = get_object_or_404(Election, id=election_id)
        print(f"Election Found: {election.name}")  # Debugging

        # Check if voter is verified
        if not voter.is_verified:
            messages.error(request, "Your profile is not verified. You cannot vote.")
            return redirect('voter_dashboard')

        # Check if voter has already voted
        if Vote.objects.filter(voter=voter, election=election).exists():
            messages.warning(request, "You have already voted in this election.")
            return redirect('voter_dashboard')

        # FIXED: Use `nominations` instead of `nomination`
        nominated_candidates = Candidate.objects.filter(nominations__election=election)

        if request.method == 'POST':
            form = VoteForm(request.POST, election=election, voter=voter)
            if form.is_valid():
                vote = form.save(commit=False)
                vote.voter = voter
                vote.election = election
                vote.save()
                
                subject = "Vote Confirmation"
                message = f"Dear {voter.user.username},\n\nYour vote has been successfully cast for {election.name}."
                send_email(subject, message, voter.user.email)
                send_sms_notification(voter.phone, message)

                messages.success(request, "Your vote has been cast successfully!")
                return redirect('voter_dashboard')
        else:
            form = VoteForm(election=election, voter=voter)

        return render(request, 'voter/cast_vote.html', {
            'form': form,
            'election': election,
            'voter': voter,
            'nominated_candidates': nominated_candidates
        })
    except Election.DoesNotExist:
        print(f"Election with ID {election_id} not found!")  # Debugging
        raise Http404("Election does not exist.")

@login_required
def voter_audit_logs(request):
    voter = Voter.objects.get(user=request.user)
    audit_logs = AuditLog.objects.filter(voter=voter).order_by('-timestamp')

    return render(request, 'voter/audit_logs.html', {
        'audit_logs': audit_logs,
        'voter': voter,
    })


@login_required
def view_candidates(request, election_id):
    """
    Display a list of candidates who have submitted nomination forms for a specific election.
    """
    voter = get_object_or_404(Voter, user=request.user)
    election = get_object_or_404(Election, id=election_id)
    candidates = Candidate.objects.filter(nominations__election=election)
    return render(request, 'voter/candidate_list.html', {'candidates': candidates, 'election': election,'voter': voter,})


@login_required
def candidate_detail(request, candidate_id):
    """
    Display detailed profile information of a selected candidate.
    """
    voter = get_object_or_404(Voter, user=request.user)
    candidate = get_object_or_404(Candidate, id=candidate_id)
    
    # Fetch the candidate's nomination
    nomination = candidate.nominations.first()  # Get the first nomination (assuming one per election)
    
    return render(request, 'voter/candidate_profile.html', {
        'candidate': candidate,
        'nomination': nomination,  # Pass nomination data to template
        'voter': voter
    })


@login_required
def calculate_all_results(request):
    completed_elections = Election.objects.filter(status='Completed', result_published=False)  # Only process unfinished results

    if not completed_elections.exists():
        messages.warning(request, "No completed elections found or results already published.")
        return redirect('view_results')

    for election in completed_elections:
        results = (
            Vote.objects.filter(election=election)
            .values('candidate')
            .annotate(total_votes=Count('candidate'))
            .order_by('-total_votes')
        )

        if results:
            winner_id = results[0]['candidate']
            winner_candidate = Candidate.objects.get(id=winner_id)

            election.winner = winner_candidate
            election.result_published = True
            election.save()

    messages.success(request, "Results calculated for all completed elections.")
    return redirect('view_results')


def send_election_reminders():
    upcoming_elections = Election.objects.filter(status='Upcoming')
    voters = Voter.objects.filter(is_verified=True)
    candidates= Candidate.objects.filter(is_verified=True)

    for election in upcoming_elections:
        subject = f"Reminder: Upcoming Election - {election.name}"
        message = f"Dear Voter,\n\nRemember to cast your vote for {election.name} on {election.date}.\n\nElection Management System."

        for user in list(candidates) + list(voters):
            send_email(subject, message, user.user.email)
            send_sms_notification(user.phone, message)

    print("Election reminders sent successfully.")


def send_result_announcements():
    completed_elections = Election.objects.filter(status='Completed')

    for election in completed_elections:
        results = (
            Vote.objects.filter(election=election)
            .values('candidate__id', 'candidate__name')
            .annotate(total_votes=Count('candidate'))
            .order_by('-total_votes')
        )

        winner = results[0] if results else None
        subject = f"Election Results: {election.name}"
        message = f"The results for {election.name} are out!\nWinner: {winner['candidate__name']} with {winner['total_votes']} votes."

        candidates = Candidate.objects.filter(nominations__election=election)
        voters = Voter.objects.filter(is_verified=True)

        for user in list(candidates) + list(voters):
            send_email(subject, message, user.user.email)
            send_sms_notification(user.phone, message)

    print("Result announcements sent successfully.")


@login_required
def generate_report(request):
    if request.method == "POST":
        election_id = request.POST.get("election_id")
        report_type = request.POST.get("report_type")

        if not election_id or not report_type:
            return HttpResponse("Invalid selection", status=400)

        election = Election.objects.filter(id=election_id, status="Completed").first()
        if not election:
            return HttpResponse("Election not found or not completed.", status=400)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_name = f"{report_type.replace(' ', '_')}_{timestamp}"
        pdf_path = f"media/reports/{report_name}.pdf"
        excel_candidates_path = f"media/reports/{report_name}_candidates.xlsx"
        excel_voters_path = f"media/reports/{report_name}_voters.xlsx"
        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

        #  Fetch Data
        candidates = Candidate.objects.filter(nominations__election=election)
        total_candidates = Candidate.objects.count()
        candidates_registered = candidates.count()

        all_voters = Voter.objects.all()
        total_voters = all_voters.count()
        voters_who_voted = Vote.objects.filter(election=election).values_list('voter', flat=True).distinct()

        #  Graph 1: Candidate Votes Bar Chart
        candidate_names = [candidate.name for candidate in candidates]
        votes_received = [Vote.objects.filter(election=election, candidate=candidate).count() for candidate in candidates]
        bar_colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]

        plt.figure(figsize=(8, 5))
        y_positions = np.arange(len(candidate_names))
        plt.barh(y_positions, votes_received, color=bar_colors[:len(candidate_names)], align='center', edgecolor='black')
        plt.yticks(y_positions, candidate_names)
        plt.xlabel("Votes Received")
        plt.title("Votes Per Candidate")
        plt.gca().invert_yaxis()
        candidate_graph_path = f"media/reports/{report_name}_candidates.png"
        plt.savefig(candidate_graph_path, bbox_inches="tight")
        plt.close()

        #  Graph 2: Voter Turnout Donut Chart
        labels = ["Voted", "Did Not Vote"]
        sizes = [len(voters_who_voted), total_voters - len(voters_who_voted)]
        pcolors = ["#2ca02c", "#d62728"]

        plt.figure(figsize=(6, 6))
        plt.pie(sizes, labels=labels, autopct="%1.1f%%", colors=pcolors, startangle=140, wedgeprops={"edgecolor": "black"})
        centre_circle = plt.Circle((0, 0), 0.70, fc="white")
        plt.gcf().gca().add_artist(centre_circle)
        plt.title("Voter Turnout")
        voter_graph_path = f"media/reports/{report_name}_voter_turnout.png"
        plt.savefig(voter_graph_path)
        plt.close()

        # Graph 3: Line Chart (Vote Trends)
        plt.figure(figsize=(8, 5))
        plt.plot(candidate_names, votes_received, marker='o', linestyle='-', color='b', linewidth=2, markersize=8)
        plt.xlabel("Candidates")
        plt.ylabel("Votes Received")
        plt.title("Vote Trend Across Candidates")
        plt.grid(True)
        candidate_line_chart_path = f"media/reports/{report_name}_candidate_trend.png"
        plt.savefig(candidate_line_chart_path, bbox_inches="tight")
        plt.close()
        
        #  Generate PDF
        pdf = SimpleDocTemplate(pdf_path, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        #  Report Title
        title_style = styles['Heading1']
        title_style.alignment = 1
        elements.append(Paragraph(f"{report_type} - {election.name}", title_style))
        elements.append(Spacer(1, 20))

        #  Election Info Table
        election_info = [["Election ID", "Election Name", "Start Date", "End Date", "Status"],
                         [election.id, election.name, election.start_date.strftime("%Y-%m-%d"),
                          election.end_date.strftime("%Y-%m-%d"), election.status]]

        election_table = Table(election_info, colWidths=[1.5*inch, 2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        election_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold')
        ]))
        elements.append(election_table)
        elements.append(Spacer(1, 20))

        #  Candidate Statistics
        elements.append(Paragraph("Candidate Statistics", styles['Heading2']))
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(f"Total Candidates: {total_candidates}", styles['Normal']))
        elements.append(Paragraph(f"Candidates Registered for Election: {candidates_registered}", styles['Normal']))
        elements.append(Spacer(1, 20))
        elements.append(Image(candidate_graph_path, width=400, height=250))
        elements.append(Spacer(1, 20))
        elements.append(Image(candidate_line_chart_path, width=400, height=250))
        elements.append(Spacer(1, 20))

        # Candidate Table
        elements.append(Paragraph("Candidates Participated", styles['Heading2']))
        elements.append(Spacer(1, 12))
        candidate_table_data = [["Candidate ID", "Candidate Name", "Party", "Votes Received"]]
        for candidate in candidates:
            votes = Vote.objects.filter(election=election, candidate=candidate).count()
            candidate_table_data.append([candidate.id, candidate.name, candidate.political_party, votes])

        candidate_table = Table(candidate_table_data, colWidths=[1.5*inch, 2.5*inch, 2*inch, 1.5*inch])
        candidate_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold')
        ]))
        elements.append(candidate_table)
        elements.append(Spacer(1, 20))

        #  Voter Statistics
        elements.append(Paragraph("Voter Statistics", styles['Heading2']))
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(f"Total Voters: {total_voters}", styles['Normal']))
        elements.append(Paragraph(f"Voters Who Cast Their Vote: {len(voters_who_voted)}", styles['Normal']))
        elements.append(Spacer(1, 20))
        elements.append(Image(voter_graph_path, width=300, height=300))
        elements.append(Spacer(1, 20))

        #  Voter Table (With "Voted" Status Instead of Phone Number)
        elements.append(Paragraph("Voter List", styles['Heading2']))
        elements.append(Spacer(1, 12))
        voter_table_data = [["Voter ID", "Voter Name", "Email", "Voted"]]
        for voter in all_voters:
            voted_status = "Yes" if voter.id in voters_who_voted else "No"
            voter_table_data.append([voter.id, voter.name, voter.email, voted_status])

        voter_table = Table(voter_table_data, colWidths=[1.5*inch, 2.5*inch, 2*inch, 1.5*inch])
        voter_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold')
        ]))
        elements.append(voter_table)
        elements.append(Spacer(1, 20))

        #  Generate Final PDF
        pdf.build(elements)
        pd.DataFrame(candidate_table_data[1:], columns=candidate_table_data[0]).to_excel(excel_candidates_path, index=False)
        pd.DataFrame(voter_table_data[1:], columns=voter_table_data[0]).to_excel(excel_voters_path, index=False)

        #  Save Report to DB
        report = Report.objects.create(
            name=report_name,
            report_type=report_type,
            generated_by=request.user
        )
        with open(pdf_path, "rb") as f:
            report.file.save(f"{report_name}.pdf", File(f))

        return redirect("report_list")

    return HttpResponse("Invalid request", status=400)


@login_required
def report_list(request):
    reports = Report.objects.all().order_by('-generated_at')
    completed_elections = Election.objects.filter(status="Completed")
    return render(request, 'core/reports.html', {
        'reports': reports,
        'completed_elections': completed_elections
    })


@login_required
def download_report(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    return FileResponse(report.file, as_attachment=True)


def submit_feedback(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your feedback has been submitted successfully!")
            return redirect('submit_feedback')  
    else:
        form = FeedbackForm()
    
    return render(request, 'core/submit_feedback.html', {'form': form})


@staff_member_required
def view_feedback(request):
    feedbacks = Feedback.objects.all().order_by('-submitted_at')
    return render(request, 'core/view_feedback.html', {'feedbacks': feedbacks})

def live_results(request):
    active_elections = Election.objects.filter(status='Ongoing')

    return render(request, 'core/live_results.html', {'active_elections': active_elections})


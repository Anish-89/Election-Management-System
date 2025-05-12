from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from .models import Election,Candidate,Nomination,Voter,Vote,Student,Feedback
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import date, timedelta


def validate_age(value):
    """Ensure user is at least 18 years old."""
    today = date.today()
    try:
        age_limit = today.replace(year=today.year - 18)
    except ValueError:
        # Handle leap year birthdays
        age_limit = today.replace(month=2, day=28, year=today.year - 18)
    
    if value > age_limit:
        raise ValidationError("You must be at least 18 years old to register.")

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, required=True, label="Name")
    email = forms.EmailField(required=True, label="Email")
    message = forms.CharField(widget=forms.Textarea, required=True, label="Message")


class ElectionForm(forms.ModelForm):
    class Meta:
        model = Election
        fields = ['name', 'start_date', 'end_date', 'region', 'election_type', 'description']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'election_type': forms.Select(attrs={'class': 'form-control'}),
        }

class CandidateRegistrationForm(forms.ModelForm):
    student_id = forms.CharField(
    max_length=20, 
    required=True, 
    widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'student_id'})  # Added ID
    )

    otp = forms.CharField(
        max_length=6, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter OTP'})
    )

    class Meta:
        model = Candidate
        fields = ['student_id', 'name', 'date_of_birth', 'profile_image', 'address', 'email', 'phone',
                  'political_party', 'id_proof', 'election_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'profile_image': forms.FileInput(attrs={'class': 'file-input'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'political_party': forms.TextInput(attrs={'class': 'form-control'}),
            'election_type': forms.Select(attrs={'class': 'form-control'}),
            'id_proof': forms.FileInput(attrs={'class': 'file-input'}),
        }

    def clean_student_id(self):
        student_id = self.cleaned_data.get('student_id')
        if not Student.objects.filter(student_id=student_id).exists():
            raise forms.ValidationError("Invalid Student ID")
        return student_id
    # Add age validation
    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        validate_age(dob)  # Check if age is 18+
        return dob



class CandidateProfileForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['name',  'profile_image','address', 'phone', 'political_party', ]
        


class CandidatePasswordUpdateForm(PasswordChangeForm):
    class Meta:
        model = Candidate
        fields = ['old_password', 'new_password1', 'new_password2']



class CandidateUsernameChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username


class NominationFormBase(forms.ModelForm):
    class Meta:
        model = Nomination
        fields = ['election']

    def __init__(self, *args, **kwargs):
        candidate = kwargs.pop('candidate', None)
        super().__init__(*args, **kwargs)
        if candidate:
            # Filter elections for the candidate
            self.fields['election'].queryset = candidate.eligible_elections.filter(
                nominations__candidate=candidate
            )


class LokSabhaNominationForm(NominationFormBase):
    # Add additional fields specific to Lok Sabha
    special_loksabha_field = forms.CharField(required=True, label="Lok Sabha Special Requirement")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class RajyaSabhaNominationForm(NominationFormBase):
    # Add additional fields specific to Rajya Sabha
    special_rajyasabha_field = forms.CharField(required=True, label="Rajya Sabha Special Requirement")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

from django import forms
from .models import Nomination

class OthersNominationForm(forms.ModelForm):
    class Meta:
        model = Nomination
        fields = ['election']  # Base fields common to all nominations
        widgets = {
            'election': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
        }

    full_name = forms.CharField(
        max_length=255, 
        label="Full Name",
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_full_name', 'required': 'required'})
    )

    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'id': 'id_email', 'required': 'required'})
    )

    phone_number = forms.CharField(
        max_length=15,
        label="Phone Number",
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_phone', 'required': 'required'})
    )

    date_of_birth = forms.DateField(
        label="Date of Birth",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'id_dob'})
    )

    photo = forms.ImageField(
        label="Upload Photo",
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'})
    )

    position_applied_for = forms.CharField(
        max_length=255,
        label="Position Applied For",
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_position', 'required': 'required'})
    )

    department = forms.CharField(
        max_length=255,
        label="Department/Team/Batch Details",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_department'})
    )

    statement_of_purpose = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'id': 'id_statement', 'rows': 4}),
        label="Statement of Purpose (Optional)",
        required=False
    )

    eligibility_declaration = forms.BooleanField(
        label="I confirm that I meet the eligibility criteria for this election.",
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'checkbox-input', 'id': 'id_eligibility'})
    )

    code_of_conduct_agreement = forms.BooleanField(
        label="I agree to abide by the rules of the election.",
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'checkbox-input', 'id': 'id_rules'})
    )

    final_declaration = forms.BooleanField(
        label="I confirm that the information provided is accurate, and I accept the election process.",
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'checkbox-input', 'id': 'id_accurate'})
    )

    def __init__(self, *args, **kwargs):
        candidate = kwargs.pop('candidate', None)
        super().__init__(*args, **kwargs)
        
        if candidate:
            self.fields['election'].queryset = candidate.eligible_elections.filter(
                status='Upcoming', 
                election_type=candidate.election_type
            ).distinct()


class VoterRegistrationForm(forms.ModelForm):
    student_id = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'student_id'})
    )
    name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'id': 'email'})
    )
    phone = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'phone'})
    )
    address = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'id': 'address'})
    )
    date_of_birth = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'class': 'form-control', 'id': 'date_of_birth', 'type': 'date'})
    )
    profile_image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'file-input', 'id': 'profile_image'})
    )
    id_proof = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'file-input', 'id': 'id_proof', 'accept': 'image/*,.pdf'})
    )
    election_type = forms.ChoiceField(
        choices=[
            ('', 'Select Election Type'),
            ('Rajya Sabha', 'Rajya Sabha'),
            ('Lok Sabha', 'Lok Sabha'),
            ('Others', 'Others'),
        ],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'election_type'})
    )
    otp = forms.CharField(
        max_length=6,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control otp-input', 'id': 'otp', 'placeholder': 'Enter OTP'})
    )

    class Meta:
        model = Voter
        fields = ['student_id', 'name', 'email', 'phone', 'profile_image', 'address', 'date_of_birth', 'id_proof',
                  'election_type']

    
      # Add age validation
    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        validate_age(dob)  # Check if age is 18+
        return dob

    def clean_student_id(self):
        student_id = self.cleaned_data.get('student_id')
        if not Student.objects.filter(student_id=student_id).exists():
            raise forms.ValidationError("Invalid Student ID")
        return student_id


class VoterProfileForm(forms.ModelForm):
    class Meta:
        model = Voter
        fields = ['name', 'profile_image', 'phone', 'email', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your full name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter your address', 'rows': 3}),
        }

class VoterPasswordUpdateForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2']
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'placeholder': f'Enter {field.replace("_", " ").title()}'
            })

class VoterUsernameChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter new username'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(id=self.instance.id).exists():
            raise forms.ValidationError("This username is already taken.")
        return username


class VoteForm(forms.ModelForm):
    class Meta:
        model = Vote
        fields = ['candidate']

    def __init__(self, *args, **kwargs):
        election = kwargs.pop('election', None)
        voter = kwargs.pop('voter', None)
        super().__init__(*args, **kwargs)

        if election:
            # Get only candidates who have submitted nomination forms for the election
            self.fields['candidate'].queryset = Candidate.objects.filter(nominations__election=election)

        # Prevent already voted voters
        if voter and Vote.objects.filter(voter=voter, election=election).exists():
            self.fields['candidate'].disabled = True
            self.fields['candidate'].widget.attrs['readonly'] = True


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['role', 'name', 'message']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your name'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write your feedback here...', 'rows': 5}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name or not name.strip():
            raise forms.ValidationError("Name is required.")
        if len(name) > 100:
            raise forms.ValidationError("Name must be 100 characters or fewer.")
        return name

    def clean_message(self):
        message = self.cleaned_data.get('message')
        if not message or not message.strip():
            raise forms.ValidationError("Message is required.")
        if len(message) > 500:
            raise forms.ValidationError("Message must be 500 characters or fewer.")
        return message
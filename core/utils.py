from django.core.mail import send_mail
from .models import Election, Candidate,OTPVerification
from django.conf import settings
import requests  # type: ignore
import logging
from django.utils.timezone import now
import random
import string

logger = logging.getLogger(__name__)

def send_admin_notification(name, email, message):
    """
    Send an email notification to the Admin when a new contact message is submitted.
    """
    subject = f"New Contact Message from {name}"
    body = (
        f"You have received a new message through the Contact Us form.\n\n"
        f"Name: {name}\n"
        f"Email: {email}\n\n"
        f"Message:\n{message}\n\n"
        f"Please respond to the query as soon as possible."
    )
    admin_email = 'anishkjha7@gmail.com'  # Replace with the Admin's email
    send_mail(subject, body, email, [admin_email])


def generate_random_password(length=8):
    """
    Generate a random password with letters, digits, and special characters.

    Args:
        length (int): Length of the password (default: 8).

    Returns:
        str: Randomly generated password.
    """
    characters = string.ascii_letters + string.digits + "!@#$%^&*()"
    password = ''.join(random.choice(characters) for _ in range(length))
    return password



def send_email(subject, message, recipient_email):
    """Utility function to send emails."""
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            fail_silently=False
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
    

api_secret = settings.SMSCHEF_API_SECRET
device_id = settings.SMSCHEF_DEVICE_ID

def generate_otp():
    return str(random.randint(100000, 999999))  # 6-digit OTP

def send_otp(phone):
    otp = generate_otp()

    # Ensure phone number is in E.164 format (+91 for India)
    if not phone.startswith("+"):
        phone = "+91" + phone  

    # Store OTP in the database
    otp_record, created = OTPVerification.objects.update_or_create(
        phone=phone, defaults={"otp": otp, "created_at": now()}
    )

    url = "https://www.cloud.smschef.com/api/send/otp"
    data = {
        "secret": api_secret,
        "type": "sms",
        "message": f"Your OTP for Registering into Online Election Portal is {otp}",
        "phone": phone,   # Ensure correct format
        "expire": 300 ,   # OTP expires in 5 minutes
        "mode": "devices" ,
        "device": device_id,
        "sim": 1,
        "priority": 1, 
    }

    try:
        response = requests.post(url, data=data)
        result = response.json()

        if response.status_code == 200 and result.get("status") == 200:
            logger.info(f"OTP sent successfully to {phone}")
            return True
        else:
            logger.error(f"Failed to send OTP: {result}")
            return False
    except Exception as e:
        logger.error(f"Error sending OTP: {e}")
        return False



def verify_otp(phone, otp):
    try:
        # Ensure phone number is in E.164 format (+91 for India)
        if not phone.startswith("+"):
            phone = "+91" + phone  

        # Retrieve OTP record
        otp_record = OTPVerification.objects.filter(phone=phone, otp=otp).first()

        if otp_record and otp_record.is_valid():
            return True
        return False
    except Exception as e:
        logger.error(f"Error verifying OTP: {e}")
        return False



def send_sms_notification(phone, message):
    """Send SMS notification using SMSChef."""
    try:
        api_secret = settings.SMSCHEF_API_SECRET
        device_id = settings.SMSCHEF_DEVICE_ID

        if not phone.startswith("+"):
            phone = "+91" + phone

        payload = {
            "secret": api_secret,
            "mode": "devices",
            "device": device_id,
            "sim": 1,
            "priority": 1,
            "phone": phone,
            "message": message,
        }

        response = requests.post(
            url="https://www.cloud.smschef.com/api/send/sms",
            params=payload,
            timeout=10
        )

        result = response.json()
        if result.get("status") == 200:
            print(logger.info(f"SMS sent successfully to {phone}"))
            return True
        else:
            print(logger.error(f"Failed to send SMS: {result.get('message')}"))
            return False
    except Exception as e:
        logger.error(f"Error sending SMS: {e}")
        return False


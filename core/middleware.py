from core.models import AuditLog, Candidate, Voter
from django.utils.timezone import now

class UserActionLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            user = request.user
            candidate = Candidate.objects.filter(user=user).first()
            voter = Voter.objects.filter(user=user).first()
            is_admin = user.is_staff  # Check if the user is an admin

            # Only log important GET requests (like dashboard access)
            important_get_paths = ['/dashboard/', '/admin-dashboard/']
            if request.method in ['POST', 'PUT', 'DELETE'] or request.path in important_get_paths:
                action = f"{request.method} {request.path}"

                # Filter sensitive fields
                details = request.POST.dict() if request.method in ['POST', 'PUT', 'DELETE'] else {}
                sensitive_fields = ['password', 'new_password', 'confirm_password']
                for field in sensitive_fields:
                    if field in details:
                        details[field] = '******'  # Mask password fields

                # Improve success detection
                status_code = response.status_code
                if status_code in [200, 201, 204]:  # Standard success codes
                    status_message = "Success"
                elif status_code in [301, 302]:  # Redirects (e.g., login success)
                    status_message = "Success (Redirect)"
                else:
                    status_message = f"Failed (Status: {status_code})"

                # Create AuditLog and link it to the correct user type
                AuditLog.objects.create(
                    user=user,
                    admin_user=user if is_admin else None,
                    candidate=candidate if candidate else None,
                    voter=voter if voter else None,
                    action=action,
                    timestamp=now(),
                    details=f"{status_message} - {details}"
                )

        return response
